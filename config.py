import os, sys
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")

for d in [INPUT_DIR, OUTPUT_DIR, TEMP_DIR, ASSETS_DIR, IMAGES_DIR]:
    os.makedirs(d, exist_ok=True)

# Channel Identity & Branding
CHANNEL_NAME = "THE TESLA CURRENTS"
CHANNEL_HANDLE = "@TheTeslaCurrents"
TAGLINE = "Nikola Tesla, Cosmic Energy & The Secrets of the Universe"
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")
DEFAULT_IMAGE_PATH = os.path.join(IMAGES_DIR, "tesla_portrait_01.jpg")

# Video Dimensions & Frame Rate
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 30

IS_SOLO = True

# Subtitle Position & Typography (Large, bold, single-line in open right zone)
SUBTITLE_CENTER_X = 1360
SUBTITLE_Y = 470
MAX_SUBTITLE_WIDTH = 880
SUBTITLE_FONT_SIZE = 48

# Audio Spectrum Visualizer (Directly below single-line subtitle with generous breathing gap)
VIS_CENTER_X = 1360
VIS_BASE_Y = 675
VIS_NUM_BARS = 24
VIS_BAR_WIDTH = 10
VIS_BAR_SPACING = 8
VIS_MIN_HEIGHT = 4
VIS_MAX_HEIGHT = 50
VIS_COLOR = (245, 197, 66, 240)  # Luminous Antique Gold

# Voiceover Engine & Model Selection
TTS_ENGINE = "kokoro"
KOKORO_VOICE = "bm_lewis"
KOKORO_LANG = "en-gb"
KOKORO_SPEED = 0.85            # Slowed-down visionary philosophical & scientific cadence

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = "pNInz6obpgDQGcFmaJgB"

# Edge-TTS Fallback Settings
VOICE_HOST1 = "en-GB-RyanNeural"
VOICE_HOST2 = "en-GB-RyanNeural"
HOST1_NAME = "The Visionary"
HOST2_NAME = "The Visionary"
HOST1_SPEAKER = "male"
HOST2_SPEAKER = "male"
HOST1_PITCH = "+0Hz"
HOST2_PITCH = "+0Hz"
TTS_RATE = "+0%"
PAUSE_BETWEEN_TURNS = 0.45

# Subtitle Sentence Chunking
MAX_WORDS_PER_CHUNK = 14
MAX_CHARS_PER_LINE = 28

# AI Generation Settings
POLLINATIONS_API_KEY = os.environ.get("POLLINATIONS_API_KEY", "sk_B0I1QMA8hWP14sICrnx1S1pt8riQdpLZ")
POLLINATIONS_ENDPOINT = "https://gen.pollinations.ai/v1/chat/completions"
POLLINATIONS_MODEL = "gemini-fast"
NICHE_PROMPT = "Profound philosophical and scientific contemplation on Nikola Tesla's visionary theories of the cosmos, 3-6-9 universal resonance, wireless power, the luminous aether, the mysteries of electricity, and the eternal clash between solitary genius and modern commercial exploitation, narrated with cosmic wonder, deep intellectual authority, and dramatic gravitas."

# Typography Candidates
FONT_CANDIDATES = [
    r"C:\Windows\Fonts\arialbd.ttf",
    r"C:\Windows\Fonts\georgiab.ttf",
    r"C:\Windows\Fonts\segoeuib.ttf",
    r"C:\Windows\Fonts\timesbd.ttf",
    r"C:\Windows\Fonts\arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
]
FONT_PATH = next((p for p in FONT_CANDIDATES if os.path.exists(p)), "arial.ttf")
FALLBACK_FONT_PATH = FONT_PATH
