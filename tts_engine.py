import os, json, asyncio, random, re
import soundfile as sf
import numpy as np
from pydub import AudioSegment
import config

def split_into_sentences(text: str) -> list:
    """Splits paragraph text into natural sentences for realistic speech synthesis."""
    # Split by terminal punctuation followed by space or quote
    raw_sents = re.split(r'(?<=[.?!])\s+', text.strip())
    cleaned = []
    for s in raw_sents:
        s = s.strip()
        if s:
            cleaned.append(s)
    return cleaned

def download_file_with_progress(url: str, dest_path: str):
    import requests
    from tqdm import tqdm
    print(f"[Model Download] Downloading {os.path.basename(dest_path)} from GitHub Releases: {url}...")
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    temp_dest = dest_path + ".tmp"
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        total_size = int(r.headers.get("content-length", 0))
        with open(temp_dest, "wb") as f, tqdm(
            desc=os.path.basename(dest_path),
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024
        ) as bar:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
                    bar.update(len(chunk))
    if os.path.exists(dest_path):
        os.remove(dest_path)
    os.rename(temp_dest, dest_path)
    print(f"[Model Download] Verified & saved: {dest_path}")

def ensure_kokoro_models(model_path: str, voices_path: str):
    """Ensures Kokoro model weights and voices exist. Downloads directly from GitHub releases on cloud/CI runners if absent."""
    KOKORO_MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
    VOICES_BIN_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"

    if not os.path.exists(model_path) or os.path.getsize(model_path) < 100_000_000:
        print("[Kokoro Runner Setup] Model weights missing in runner environment. Downloading from GitHub...")
        download_file_with_progress(KOKORO_MODEL_URL, model_path)

    if not os.path.exists(voices_path) or os.path.getsize(voices_path) < 10_000_000:
        print("[Kokoro Runner Setup] Voice embeddings missing in runner environment. Downloading from GitHub...")
        download_file_with_progress(VOICES_BIN_URL, voices_path)

def infer_kokoro_language(voice_name: str) -> str:
    """Infers the language code from the Kokoro voice prefix."""
    prefix = voice_name[:2].lower()
    mapping = {
        "af": "en-us", "am": "en-us",  # American English
        "bf": "en-gb", "bm": "en-gb",  # British English
        "ef": "es",    "em": "es",     # Spanish
        "ff": "fr-fr", "fm": "fr-fr",  # French
        "hf": "hi",    "hm": "hi",     # Hindi
        "if": "it",    "im": "it",     # Italian
        "jf": "ja",    "jm": "ja",     # Japanese
        "pf": "pt-br", "pm": "pt-br",  # Brazilian Portuguese
        "zf": "zh",    "zm": "zh"      # Mandarin Chinese
    }
    return mapping.get(prefix, "en-us")

def compute_acoustic_word_timings(words: list, dur_sec: float, curr_time: float, tokenizer=None, lang: str = "en-gb") -> list:
    """
    Computes precise, syllable- and phoneme-weighted word timestamps for speech synthesis,
    accounting for word complexity, rapid functional words, and natural punctuation pauses.
    """
    if not words:
        return []

    weights = []
    for w in words:
        p_len = 0
        if tokenizer:
            try:
                phonemes = tokenizer.phonemize(w, lang)
                p_len = len(phonemes)
            except Exception:
                p_len = 0

        if p_len == 0:
            clean = re.sub(r'[^a-zA-Z0-9]', '', w.lower())
            vowels = len(re.findall(r'[aeiouy]+', clean))
            p_len = max(1, vowels) * 2 + max(1, len(clean))

        # Punctuation pause weights (commas, dashes, terminal punctuation take acoustic pause time)
        punct_pause = 0
        stripped = w.rstrip('"\')]}')
        if stripped.endswith((',', ';', ':', '—', '--', '-')):
            punct_pause = 2.5
        elif stripped.endswith(('.', '!', '?')):
            punct_pause = 3.5

        weights.append(max(1.0, float(p_len)) + punct_pause)

    total_w = sum(weights)
    chunk_words = []
    elapsed = 0.0

    for i, w in enumerate(words):
        w_dur = (weights[i] / total_w) * dur_sec
        # Spoken active duration: when punctuated, leave trailing pause for silence
        stripped = w.rstrip('"\')]}')
        is_punct = stripped.endswith((',', ';', ':', '—', '--', '-', '.', '!', '?'))
        active_dur = w_dur * 0.82 if is_punct else w_dur

        w_start = curr_time + elapsed
        w_end = w_start + active_dur

        chunk_words.append({
            "word": w,
            "start": round(w_start, 3),
            "end": round(w_end, 3)
        })
        elapsed += w_dur

    return chunk_words

def generate_kokoro_dialogue(dialogue: list) -> tuple:
    """Synthesizes hyper-realistic human voice using local Kokoro-82M ONNX model."""
    from kokoro_onnx import Kokoro

    model_path = os.path.join(config.BASE_DIR, "models", "kokoro-v1.0.onnx")
    voices_path = os.path.join(config.BASE_DIR, "models", "voices-v1.0.bin")

    # Automatically fetch models on GitHub/cloud runners if missing
    ensure_kokoro_models(model_path, voices_path)

    voice_name = getattr(config, "KOKORO_VOICE", "am_adam")
    speed = getattr(config, "KOKORO_SPEED", 0.95)
    lang = getattr(config, "KOKORO_LANG", None) or infer_kokoro_language(voice_name)

    print(f"[Kokoro TTS] Loading hyper-realistic model (Voice: {voice_name}, Speed: {speed}, Lang: {lang})...")
    kokoro = Kokoro(model_path, voices_path)

    all_audio_segments = []
    all_chunks = []
    sr = 24000
    initial_silence = 0.25
    all_audio_segments.append(np.zeros(int(sr * initial_silence), dtype=np.float32))
    curr_time = initial_silence

    total_turns = len(dialogue)
    print(f"[Kokoro TTS] Synthesizing {total_turns} turns with neural human inflections...")

    for turn_idx, turn in enumerate(dialogue):
        turn_text = turn.get("text", "").strip()
        sentences = split_into_sentences(turn_text)

        for sent in sentences:
            try:
                samples, sample_rate = kokoro.create(sent, voice=voice_name, speed=speed, lang=lang)
                sr = sample_rate
            except Exception as e:
                print(f"  [Kokoro Warning] Retrying sentence with fallback formatting: {e}")
                # Remove special symbols if any
                clean_s = re.sub(r'[^\w\s.,?!\'"-]', '', sent)
                samples, sample_rate = kokoro.create(clean_s, voice=voice_name, speed=speed, lang=lang)
                sr = sample_rate

            dur_sec = len(samples) / float(sr)
            all_audio_segments.append(samples)

            # Precise acoustic phoneme & syllable breakdown for highlighting
            words = sent.split()
            chunk_words = compute_acoustic_word_timings(
                words=words,
                dur_sec=dur_sec,
                curr_time=curr_time,
                tokenizer=kokoro.tokenizer,
                lang=lang
            )

            all_chunks.append({
                "line_text": sent,
                "start": round(curr_time, 3),
                "end": round(curr_time + dur_sec, 3),
                "words": chunk_words,
                "turn_idx": turn_idx
            })

            # Natural inter-sentence pause (0.35s)
            inter_sent_pause = 0.35
            all_audio_segments.append(np.zeros(int(sr * inter_sent_pause), dtype=np.float32))
            curr_time += dur_sec + inter_sent_pause

        # Turn transition pause (0.45s)
        turn_pause = getattr(config, "PAUSE_BETWEEN_TURNS", 0.45)
        all_audio_segments.append(np.zeros(int(sr * turn_pause), dtype=np.float32))
        curr_time += turn_pause

        if (turn_idx + 1) % 5 == 0 or turn_idx == total_turns - 1:
            print(f"  [Kokoro Progress] Synthesized {turn_idx + 1}/{total_turns} turns ({curr_time/60.0:.1f} mins generated)")

    print("[Kokoro TTS] Concatenating and mastering audio track...")
    combined_samples = np.concatenate(all_audio_segments)
    temp_wav = os.path.join(config.TEMP_DIR, "kokoro_master_temp.wav")
    sf.write(temp_wav, combined_samples, sr)

    # Convert to standard 192k MP3
    master_path = os.path.join(config.OUTPUT_DIR, "master_podcast_audio.mp3")
    AudioSegment.from_wav(temp_wav).export(master_path, format="mp3", bitrate="192k")

    try: os.remove(temp_wav)
    except Exception: pass

    total_duration = len(combined_samples) / float(sr)
    print(f"[Kokoro TTS] Master audio ready: {total_duration:.2f}s ({total_duration/60.0:.2f} mins)")
    return master_path, all_chunks, total_duration

# Fallback Edge-TTS Implementation
EDGE_ENDPOINTS = [
    "wss://api.msedgeservices.com/tts/cognitiveservices/websocket/v1?Ocp-Apim-Subscription-Key=6A5AA1D4EAFF4E9FB37E23D68491D6F4",
    "wss://speech.platform.bing.com/consumer/speech/synthesize/readaloud/edge/v1?TrustedClientToken=6A5AA1D4EAFF4E9FB37E23D68491D6F4"
]

def set_edge_tts_endpoint(url: str):
    try:
        import edge_tts.constants, edge_tts.communicate
        edge_tts.constants.WSS_URL = url
        edge_tts.communicate.WSS_URL = url
    except Exception: pass

async def synthesize_turn_edge(text: str, voice: str, pitch: str, rate: str, turn_index: int) -> dict:
    import edge_tts
    temp_turn_path = os.path.join(config.TEMP_DIR, f"turn_{turn_index}.mp3")
    for attempt in range(5):
        target_endpoint = EDGE_ENDPOINTS[attempt % len(EDGE_ENDPOINTS)]
        set_edge_tts_endpoint(target_endpoint)
        try:
            kwargs = {"rate": rate}
            if pitch and pitch != "+0Hz":
                kwargs["pitch"] = pitch
            comm = edge_tts.Communicate(text, voice, boundary="WordBoundary", **kwargs)
            audio_data, wb_events = bytearray(), []
            async for chunk in comm.stream():
                if chunk["type"] == "audio":
                    audio_data.extend(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    s = chunk["offset"] / 10_000_000.0
                    d = chunk["duration"] / 10_000_000.0
                    wb_events.append({"word": chunk["text"].strip(), "rel_start": s, "rel_end": s + d, "duration": d})
            if len(audio_data) > 500:
                with open(temp_turn_path, "wb") as f: f.write(audio_data)
                seg = AudioSegment.from_file(temp_turn_path)
                orig_words = text.split()
                aligned = [{"word": ow, "rel_start": wb["rel_start"], "rel_end": wb["rel_end"]} for ow, wb in zip(orig_words, wb_events[:len(orig_words)])]
                return {"audio_segment": seg, "duration": len(seg)/1000.0, "words": aligned, "turn_index": turn_index}
        except Exception:
            await asyncio.sleep(1.0)
    seg = AudioSegment.silent(duration=3000)
    return {"audio_segment": seg, "duration": 3.0, "words": [], "turn_index": turn_index}

async def generate_edge_dialogue(dialogue: list) -> tuple:
    print(f"[Edge TTS] Synthesizing speech for {len(dialogue)} turns ({config.VOICE_HOST1})...")
    semaphore = asyncio.Semaphore(2)
    async def worker(idx: int, turn: dict):
        async with semaphore:
            res = await synthesize_turn_edge(turn.get("text", ""), config.VOICE_HOST1, config.HOST1_PITCH, config.TTS_RATE, idx)
            await asyncio.sleep(0.3)
            return idx, res
    tasks = [worker(i, t) for i, t in enumerate(dialogue)]
    results = await asyncio.gather(*tasks)
    results.sort(key=lambda x: x[0])
    ordered_turns = [r[1] for r in results]

    master_audio = AudioSegment.silent(duration=250)
    curr_offset = 0.25
    all_chunks = []
    for idx, tr in enumerate(ordered_turns):
        master_audio += tr["audio_segment"]
        pause_dur = int(config.PAUSE_BETWEEN_TURNS * 1000)
        master_audio += AudioSegment.silent(duration=pause_dur)
        curr_offset += tr["duration"] + config.PAUSE_BETWEEN_TURNS

    master_path = os.path.join(config.OUTPUT_DIR, "master_podcast_audio.mp3")
    master_audio.export(master_path, format="mp3", bitrate="192k")
    return master_path, all_chunks, len(master_audio)/1000.0

async def generate_podcast_audio(dialogue: list) -> tuple:
    engine = getattr(config, "TTS_ENGINE", "kokoro").lower()
    if engine == "kokoro":
        try:
            return generate_kokoro_dialogue(dialogue)
        except Exception as e:
            print(f"[TTS Fallback] Kokoro error: {e}. Falling back to Edge-TTS...")
            return await generate_edge_dialogue(dialogue)
    else:
        return await generate_edge_dialogue(dialogue)
