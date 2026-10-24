import os, sys, json, time, requests, re
import config

# Pre-crafted master curriculum for The Tesla Currents channel (Nikola Tesla scientific & philosophical masterworks)
TESLA_CURRICULUM = [
    {
        "id": "ep_1",
        "topic": "If You Only Knew the Magnificence of 3, 6, and 9: The Cosmic Geometry of Energy",
        "focus": "A deep contemplation on Nikola Tesla's most enigmatic revelation: the universal mathematics of vibration, frequency, vortex mathematics, and the sacred triadic geometry that governs cosmic reality.",
        "thumbnail_title_1": "THE 3 6 9 CODE",
        "thumbnail_title_2": "COSMIC ENERGY",
        "thumbnail_hook": "The Secret Key to the Universe",
        "acts": [
            ("Act 1: The Supreme Secret of the Universe", "Energy, frequency, and vibration as the true foundational currency of all existence."),
            ("Act 2: The Sacred Triad: The Mathematics of 3, 6, and 9", "Vortex mathematics, doubling patterns, and why 3, 6, and 9 govern the flux of universal energy."),
            ("Act 3: The Ocean of Primal Energy", "The luminous aether, radiant energy, and the inexhaustible cosmic engine sustaining all matter."),
            ("Act 4: Resonance: The Key to Infinite Power", "How aligning with the natural frequencies of the earth and cosmos unlocks boundless force."),
            ("Act 5: The Promethean Awakening: Aligning with Cosmic Law", "Transcending crude materialism to harmonize human consciousness with the cosmic transmitter.")
        ]
    },
    {
        "id": "ep_2",
        "topic": "The War of the Currents: Alternating Current and the Electrification of the Modern World",
        "focus": "The epic battle between Thomas Edison's direct current and Nikola Tesla's polyphase alternating current: corporate smear campaigns, the Niagara Falls triumph, and how Tesla gave light to civilization.",
        "thumbnail_title_1": "WAR OF CURRENTS",
        "thumbnail_title_2": "TESLA VS EDISON",
        "thumbnail_hook": "How Tesla Lit the World",
        "acts": [
            ("Act 1: The Dark World Before the Spark", "The limitations of direct current and the suffocating darkness of nineteenth-century cities."),
            ("Act 2: The Revelation in the Budapest Park", "Tesla's sudden visionary epiphany of the rotating magnetic field while reciting Goethe's Faust."),
            ("Act 3: The Smear Campaign: The Battle for the Future", "Edison's ruthless war against alternating current, fear-mongering, and the electrocution circus."),
            ("Act 4: The Triumph at Niagara Falls", "Harnessing the primordial power of the waterfall to electrify civilization across hundreds of miles."),
            ("Act 5: The Gift of Fire: Lighting the Century", "Why Tesla surrendered his billion-dollar royalties so that humanity could have light.")
        ]
    },
    {
        "id": "ep_3",
        "topic": "Wireless Power and Wardenclyffe: The Tragedy of Free Global Energy",
        "focus": "The supreme vision of Wardenclyffe Tower: terrestrial stationary waves, universal wireless power transmission, and the corporate betrayal that extinguished free global energy.",
        "thumbnail_title_1": "WIRELESS ENERGY",
        "thumbnail_title_2": "WARDENCLYFFE TOWER",
        "thumbnail_hook": "The Lost Free Power Dream",
        "acts": [
            ("Act 1: The Earth as a Resonating Conductor", "Discovering that our planet is charged with electricity and can be vibrated like a giant tuning fork."),
            ("Act 2: The Vision of the World Wireless System", "Transmitting power, news, voice, and pictures across the globe without a single wire."),
            ("Act 3: The Magnificent Tower of Long Island", "Constructing the architectural marvel of Wardenclyffe and its subterranean energetic roots."),
            ("Act 4: J.P. Morgan and the Question of the Meter", "The fatal corporate dilemma: 'If anyone can draw power, where do we put the meter?'"),
            ("Act 5: The Demolition of Prometheus: A Dream Deferred", "The destruction of the tower and the enduring prophecy of wireless universal connection.")
        ]
    },
    {
        "id": "ep_4",
        "topic": "The Mystery of the Luminous Aether: Beyond Einstein and Modern Physics",
        "focus": "Nikola Tesla's radical Dynamic Theory of Gravity: the luminous aether as the all-pervading carrier of light, force, and life, and why matter is merely condensed energy.",
        "thumbnail_title_1": "THE AETHER MYSTERY",
        "thumbnail_title_2": "BEYOND EINSTEIN",
        "thumbnail_hook": "The Hidden Medium of Space",
        "acts": [
            ("Act 1: The Ancient Conception of the Aether", "The fifth element: the continuous, invisible medium that connects all cosmic phenomena."),
            ("Act 2: Tesla's Dynamic Theory of Gravity", "Rejecting curved spacetime in favor of an electromagnetic field vibrating through the aether."),
            ("Act 3: Matter as Condensed Radiant Energy", "How primary substance creates atomic form through whirlpools of force and motion."),
            ("Act 4: Cosmic Rays and Celestial Transmissions", "Tapping the radiant energies streaming ceaselessly from the sun and distant stars."),
            ("Act 5: The Unified Fabric of Nature", "Why understanding the aether restores the spiritual unity of science and existence.")
        ]
    },
    {
        "id": "ep_5",
        "topic": "The Solitary Mind: Hyperphantasia, Celibacy, and the Burden of Prophetic Genius",
        "focus": "Inside the miraculous psychological mechanism of Nikola Tesla: building operating engines entirely in his imagination, ascetic solitude, and the loneliness of living decades ahead of time.",
        "thumbnail_title_1": "SOLITARY GENIUS",
        "thumbnail_title_2": "BURDEN OF VISION",
        "thumbnail_hook": "Inside the Mind of Tesla",
        "acts": [
            ("Act 1: The Inner Eye: The Gift of Hyperphantasia", "Constructing, running, and measuring machines in three-dimensional mental projection."),
            ("Act 2: The Ascetic Crucible: Celibacy and Discipline", "Sacrificing romantic love and domestic comfort on the altar of pure creative invention."),
            ("Act 3: The Hypersensitivity of the Senses", "Hearing the ticking of a pocket watch three rooms away; the agony of acute perception."),
            ("Act 4: The White Pigeon of Room 3327", "The mysterious, tender bond between a solitary titan and an injured white bird."),
            ("Act 5: The Solitude of Prometheus", "Why true visionaries must walk alone in the wilderness of their own minds.")
        ]
    },
    {
        "id": "ep_6",
        "topic": "Resonance and Vibration: The Power to Move the Earth",
        "focus": "Nikola Tesla's mechanical oscillators and telegeodynamics: tuning into the resonant frequency of buildings, bedrock, and the planet, and how micro-impulses compound into seismic force.",
        "thumbnail_title_1": "EARTH RESONANCE",
        "thumbnail_title_2": "VIBRATION & POWER",
        "thumbnail_hook": "Could a Pocket Device Shake a City?",
        "acts": [
            ("Act 1: The Rhythm of the Swing", "How tiny periodic impulses add together to create titanic, overwhelming power."),
            ("Act 2: The Manhattan Earthquake Experiment", "The day Tesla attached a pocket oscillator to an iron pillar and shook Lower Manhattan."),
            ("Act 3: Telegeodynamics: Communicating Through the Bedrock", "Sending seismic acoustic messages and energy through the core of the globe."),
            ("Act 4: Tuning to the Earth's Electromagnetic Pulse", "Discovering terrestrial stationary waves decades before the Schumann resonance."),
            ("Act 5: The Symphony of the Cosmos", "Why everything in existence is an instrument waiting to be tuned.")
        ]
    },
    {
        "id": "ep_7",
        "topic": "Signals from the Cosmos: The Colorado Springs Lightning Experiments",
        "focus": "The 1899 Colorado Springs high-voltage laboratory: artificial lightning bolts 130 feet long, the magnifying transmitter, and the interception of rhythmic extraterrestrial pulses.",
        "thumbnail_title_1": "SIGNALS FROM SPACE",
        "thumbnail_title_2": "COLORADO SPRINGS",
        "thumbnail_hook": "Who Was Tesla Contacting?",
        "acts": [
            ("Act 1: High Altitude Storms on the Colorado Plateau", "Building a cathedral of lightning beneath Pikes Peak to conquer electrical voltage."),
            ("Act 2: The Magnifying Transmitter", "Generating millions of volts and thunderclaps audible fifteen miles away."),
            ("Act 3: The Interception of the Unknown", "Hearing rhythmic mathematical clicks: one, two, three — a voice from deep space."),
            ("Act 4: The Ridicule of the Scientific Establishment", "How the world mocked Tesla's claim of extraterrestrial intelligent contact."),
            ("Act 5: The Cosmic Horizon of Humanity", "Why man is not alone in the vast electromagnetic ocean of the stars.")
        ]
    },
    {
        "id": "ep_8",
        "topic": "The Promethean Tragedy: Forgotten in Room 3327 and the Redemption of Time",
        "focus": "The final quiet chapter of Nikola Tesla at the Hotel New Yorker: the teleforce beam, the seizure of his trunks by the Alien Property Custodian, and his prophetic vindication across history.",
        "thumbnail_title_1": "THE FINAL SECRET",
        "thumbnail_title_2": "ROOM 3327",
        "thumbnail_hook": "The Future Was His",
        "acts": [
            ("Act 1: The Twilight of an Inventor", "Feeding pigeons in Bryant Park while living on warm milk and crackers in Room 3327."),
            ("Act 2: The Teleforce Weapon: A Shield Against War", "Inventing the macroscopic particle beam to render national borders impregnable."),
            ("Act 3: The Cold January Night of 1943", "The silent passing of an impoverished titan who gave humanity the electric age."),
            ("Act 4: The Seizure of the Trunks", "The FBI, the Alien Property Custodian, and the classified blueprints of a visionary."),
            ("Act 5: The Eternal Triumph of Nikola Tesla", "'The present is theirs; the future, for which I really worked, is mine.'")
        ]
    }
]

# Master pre-written script for Episode 1 (~20 minutes spoken duration, 42 turns, ~2,150 words)
EPISODE_1_SCRIPT = [
    # Act 1: The Supreme Secret of the Universe (Turns 1 - 8)
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "Welcome into the electric, luminous sanctuary of The Tesla Currents. Today, we stand upon the threshold of the greatest cosmic mystery ever contemplated by human intellect: the secret geometry of vibration, frequency, and the sacred numbers three, six, and nine."
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "Throughout human history, there have lived men who saw the world not merely as it appeared to the physical eye, but as it resonated in the invisible fabric of the cosmos. Foremost among these titans was Nikola Tesla — an inventor who did not merely invent machines, but tapped directly into the operating code of creation."
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "Tesla famously delivered an axiom that stands as the master key to all modern physics and ancient metaphysics alike: 'If you want to find the secrets of the universe, think in terms of energy, frequency and vibration.'"
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "Consider the profound simplicity of that revelation. We inhabit a culture blinded by the illusion of solid matter. We look upon stones, metal, human bodies, and distant planets as dense, disconnected objects separated by empty void."
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "Yet Tesla realized that what we call solid matter is nothing other than energy trapped in a perpetual state of rhythmic vibration. There is no empty space. The universe is a boundless ocean of radiant electromagnetic force, pulsing with infinite frequencies from the smallest subatomic vortex to the grandest galactic rotations."
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "When you strike a bell, it does not invent sound; it translates mechanical impact into acoustic vibrations that ripple through the air. In precisely the same manner, every atom in your physical body is an energetic bell, tuned to specific cosmic frequencies, vibrating in concert with the universal transmitter."
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "If our senses could perceive the full spectrum of electromagnetic radiation, the illusion of solid walls and isolated individuals would dissolve instantly into a radiant, interconnected web of shimmering light and harmonic frequencies."
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "And at the glowing heart of this cosmic symphony sits an enigmatic mathematical pattern — a numerical trinity so profound that Tesla once declared: 'If you only knew the magnificence of the three, six and nine, then you would have the key to the universe.'"
    },

    # Act 2: The Sacred Triad: The Mathematics of 3, 6, and 9 (Turns 9 - 16)
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "Why did Nikola Tesla possess such an overwhelming, almost mystical reverence for the numbers three, six, and nine? Why did he circle a building three times before entering? Why did he demand eighteen napkins to clean his dining table, a multiple of nine? Was this mere eccentric madness, or did he perceive a fundamental mathematical truth concealed from ordinary men?"
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "To comprehend Tesla's insight, we must examine the hidden mathematics of nature: the science of vortex mathematics and the universal doubling circuit that governs biological and physical growth."
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "Observe how life multiplies in the material world. When an embryo forms, one cell divides into two; two divide into four; four into eight; eight into sixteen; sixteen into thirty-two; thirty-two into sixty-four. This doubling pattern is the universal blueprint of cellular mitosis, computer binary, and geometric crystal formation."
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "Now, let us reduce these doubling numbers to their single-digit digital roots using ancient mathematical reduction: One doubles to two. Two doubles to four. Four doubles to eight. Eight doubles to sixteen, and one plus six equals seven. Sixteen doubles to thirty-two, and three plus two equals five. Thirty-two doubles to sixty-four, and six plus four equals ten, which reduces to one."
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "Examine the repeating sequence of this physical material cycle: one, two, four, eight, seven, five. And then it repeats infinitely: one, two, four, eight, seven, five. Notice the astonishing truth: in this entire perpetual cycle of material manifestation, the numbers three, six, and nine never appear! They are completely absent from the physical circuit."
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "Now observe what happens when we look at the numbers three and six. Three doubled is six. Six doubled is twelve, and one plus two equals three. Twelve doubled is twenty-four, and two plus four equals six. Twenty-four doubled is forty-eight, and four plus eight equals twelve, which reduces to three! Three and six form their own sacred, self-balancing oscillation, dancing back and forth like positive and negative poles."
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "And what of the number nine? Nine doubled is eighteen, and one plus eight equals nine. Eighteen doubled is thirty-six, and three plus six equals nine. Thirty-six doubled is seventy-two, and seven plus two equals nine! Nine never changes. Nine remains immutable, absolute, and centered at the axis of all geometric transformation."
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "Tesla realized that three and six represent the dual magnetic poles of manifestation, while nine represents the transcendent cosmic axis — the zero-point singularity through which all energy flows from the unseen realm into the physical world. Three, six, and nine are not in the material world; they are the governing architects of it."
    },

    # Act 3: The Ocean of Primal Energy (Turns 17 - 24)
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "Having uncovered the harmonic mathematics of the universe, Tesla turned his attention to the medium through which this divine energy travels: the luminous aether. Unlike twentieth-century physicists who came to deny the aether, Tesla insisted upon its existence until his final breath."
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "Tesla wrote: 'There is no energy in matter other than that received from the environment. All perceptible matter comes from a primary substance, or tenuity beyond conception, filling all space, the Akasha or luminous ether, which is acted upon by the life-giving Prana or creative force, calling into existence, in never-ending cycles, all things and phenomena.'"
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "Consider the immense philosophical majesty of that statement. Tesla drew directly upon ancient Vedic wisdom, recognizing that modern Western science was merely rediscovering what Eastern sages had known for millennia: that all atoms are whirlpools within an infinite cosmic sea."
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "When you burn coal or split an atom, you are merely tapping the primitive surface of energy. But Tesla envisioned tapping the cosmic reservoir directly. He demonstrated that the earth itself is an immense electrical conductor, charged to millions of volts, floating within an energized atmospheric envelope."
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "Why burn fossil fuels? Why poison the earth and enslave mankind to corporate monopolies of petroleum and copper wire, when free, inexhaustible cosmic power surrounds every square inch of our planet?"
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "This was the foundational vision behind his legendary laboratory at Colorado Springs and the majestic Wardenclyffe Tower on Long Island. Tesla did not seek to generate power through combustion; he sought to attune his instruments to the cosmic frequency of the earth itself."
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "He designed giant magnifying transmitters capable of pumping terrestrial stationary waves into the bedrock of the globe. A farmer in the Australian outback or an explorer in the Arctic could simply plunge an iron rod into the soil, connect an antenna, and draw clean, limitless electrical power directly from the resonance of the planet."
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "It was the ultimate Promethean gift — a vision of free global energy that would abolish poverty, eliminate the root causes of war, and unite humanity into a single flourishing community. But in a world ruled by financial profit, a gift of free energy was the ultimate heresy."
    },

    # Act 4: Resonance: The Key to Infinite Power (Turns 25 - 32)
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "How could a small device tap into such colossal universal forces? The answer lies in the most astonishing physical principle known to science: the law of resonance."
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "Consider the simple physics of a child on a playground swing. If you push the swing at random intervals, you expend enormous physical effort and achieve nothing but chaos. The swing halts and jolts."
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "But if you apply a tiny push — merely the touch of a single finger — timed precisely to the natural resonant frequency of the swing, your small effort compounds with every cycle. Within minutes, that gentle touch sends the swing soaring into the sky. That is the miracle of resonance: timing and frequency multiplying power to infinity."
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "Tesla applied this principle not merely to swings, but to the crystalline bedrock of the earth and the electromagnetic field of the atmosphere. In 1898, in his laboratory on Houston Street in Manhattan, he attached a small mechanical oscillator, no larger than an alarm clock, to a central steel supporting pillar of the building."
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "He adjusted the frequency millimeter by millimeter. When the oscillator matched the resonant vibration of the steel and the underlying bedrock of Manhattan, the entire building began to groan and shudder. Windows shattered, plaster rained down, and police officers rushed to the building as seismic tremors spread across several city blocks."
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "Tesla grabbed a sledgehammer and smashed the tiny oscillator just as the police broke through the door. He told them calmly: 'Gentlemen, I am sorry. You are just a trifle too late to witness my experiment. But had I continued for ten minutes longer, I could have brought down the Brooklyn Bridge into the East River.'"
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "This was not boastful arrogance; it was the absolute mathematical certainty of resonance. With resonance, a tiny vibration can split an empire. With resonance, a solitary human mind, properly attuned, can comprehend the architecture of the cosmos."
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "Every cell in your biological body possesses its own resonant frequency. When your thoughts and emotions are scattered in anxiety, fear, and resentment, your inner energy cancels itself out into chaotic interference. But when your consciousness aligns in coherence and clarity, you become an open conduit for the cosmic current."
    },

    # Act 5: The Promethean Awakening: Aligning with Cosmic Law (Turns 33 - 42)
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "What, then, is the ultimate philosophical invitation of Nikola Tesla for you, listening to these words across the digital waves of the modern world?"
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "Tesla did not live for the petty praise or the material wealth of his contemporaries. When J.P. Morgan withdrew funding from Wardenclyffe, when Thomas Edison launched smear campaigns against alternating current, and when his laboratory burned to ashes taking forty years of work with it, Tesla did not descend into bitterness."
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "He stood tall among the ruins because he knew that he worked not for his own century, but for eternity. He famously declared: 'The present is theirs; the future, for which I really worked, is mine.'"
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "We are living in the very future that Nikola Tesla dreamed into existence. The alternating current powering your home, the electric motors driving modern transportation, the radio frequencies transmitting voice and data, the neon lights illuminating our cities — all were born inside the luminous theater of Tesla's mind."
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "Yet his greatest gift to humanity remains unfulfilled: the realization that you are not a helpless, isolated biological accident. You are an energetic transmitter in a living, conscious universe."
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "Stop thinking in terms of limitation, scarcity, and matter. Begin to think in terms of energy, frequency, and vibration. What frequency are you broadcasting into the aether each day? Are you broadcasting the discordant static of worry, complaint, and smallness? Or are you broadcasting the harmonic clarity of purpose, vision, and courage?"
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "Tune your mind to the higher octave of the universe. Honor the sacred trinity of three, six, and nine: the balance of body, mind, and spirit; the harmony of thought, feeling, and action; the union of the observer, the observed, and the cosmic fabric that binds them."
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "Remember the words Tesla inscribed in his journal: 'My brain is only a receiver, in the Universe there is a core from which we obtain knowledge, strength and inspiration. I have not penetrated into the secrets of this core, but I know that it exists.'"
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "That core is waiting for you to tune your receiver. Dare to step beyond the herd. Dare to cultivate the solitary genius within your own soul. And dare to hold the electric spark of truth even when the darkness of the world attempts to extinguish it."
    },
    {
        "speaker": "male",
        "name": "The Visionary",
        "text": "Thank you for joining us in the current of The Tesla Currents. If this exploration of the three, six, nine code and the cosmic architecture of energy has illuminated your mind, subscribe to our channel, share these frequencies with those who seek visionary truth, and walk forward in resonance with the cosmos. Until our next transmission — let there be light."
    }
]

def load_history_topics() -> list:
    past = []
    for fname in ["published_videos.json", "history.json"]:
        fpath = os.path.join(config.BASE_DIR, fname)
        if os.path.exists(fpath):
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and item.get("topic"):
                                t = item["topic"].strip()
                                if t not in past:
                                    past.append(t)
            except Exception:
                pass
    return past

def generate_dynamic_story_ai(topic: str = None, ep_num: int = 1, past_topics: list = None) -> dict:
    """Uses Pollinations AI to dynamically generate an original Tesla episode."""
    if past_topics is None:
        past_topics = load_history_topics()

    print(f"[StoryGenerator] Invoking AI for dynamic visionary Tesla episode #{ep_num}...")
    headers = {"Content-Type": "application/json"}
    api_key = os.environ.get("POLLINATIONS_API_KEY")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    avoid_clause = f"AVOID repeating these already covered topics: {', '.join(past_topics)}" if past_topics else ""

    prompt = f"""You are Nikola Tesla's intellectual and spiritual successor, the lead visionary for 'The Tesla Currents' channel.
Generate a master 20-minute spoken scientific and philosophical video episode (Episode #{ep_num}).
{avoid_clause}
Topic override: {topic if topic else 'Choose a profound theme from Nikola Tesla (e.g. 3 6 9 Code, War of the Currents, Wardenclyffe Free Energy, The Luminous Aether, Resonance, Cosmic Signals)'}.

Return ONLY valid JSON matching this exact structure:
{{
  "topic": "Comprehensive Title of the Tesla Topic",
  "focus": "2-3 sentences explaining the core visionary and scientific inquiry.",
  "thumbnail_title_1": "2-4 WORDS HEADLINE 1 (e.g. THE 3 6 9 CODE)",
  "thumbnail_title_2": "2-4 WORDS HEADLINE 2 (e.g. COSMIC ENERGY)",
  "thumbnail_hook": "Short curiosity question (e.g. The Secret Key to the Universe)",
  "acts": [
    ["Act 1: Title", "Summary"],
    ["Act 2: Title", "Summary"],
    ["Act 3: Title", "Summary"],
    ["Act 4: Title", "Summary"],
    ["Act 5: Title", "Summary"]
  ],
  "dialogue": [
    {{"speaker": "male", "name": "The Visionary", "text": "Deep, poetic, aristocratic, prophetic narration in the cadence of Nikola Tesla..."}}
  ]
}}
Ensure the dialogue contains at least 35 to 40 rich turns (~2,200 words total) divided evenly across the 5 acts.
"""

    try:
        r = requests.post(
            "https://text.pollinations.ai/",
            json={"messages": [{"role": "user", "content": prompt}], "jsonMode": True},
            headers=headers,
            timeout=90
        )
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict) and data.get("dialogue") and len(data["dialogue"]) >= 15:
                print(f"[StoryGenerator] AI successfully generated {len(data['dialogue'])} turns for '{data.get('topic')}'.")
                return data
    except Exception as e:
        print(f"[StoryGenerator] AI generation encountered issue ({e}). Proceeding to curriculum...")

    return None

def generate_full_podcast_story(target_minutes: float = 20.0, topic: str = None, ep_num: int = 1) -> dict:
    """Generates the full story dialogue and chapter structure for the episode."""
    print(f"[StoryGenerator] Preparing script for Episode #{ep_num} (Target: {target_minutes:.1f} mins)...")
    past_topics = load_history_topics()

    catalog_item = None
    if topic:
        catalog_item = next((item for item in TESLA_CURRICULUM if item["topic"].lower() == topic.lower() or item["id"] == topic), None)

    if not catalog_item:
        ep_id = f"ep_{ep_num}"
        match_by_id = next((item for item in TESLA_CURRICULUM if item["id"] == ep_id), None)
        if match_by_id and match_by_id["topic"] not in past_topics:
            catalog_item = match_by_id

    if not catalog_item:
        for item in TESLA_CURRICULUM:
            if item["topic"] not in past_topics:
                catalog_item = item
                break

    if not catalog_item:
        curriculum_idx = (ep_num - 1) % len(TESLA_CURRICULUM)
        catalog_item = TESLA_CURRICULUM[curriculum_idx]

    dialogue = None
    if catalog_item["id"] == "ep_1":
        dialogue = EPISODE_1_SCRIPT
    else:
        ai_story = generate_dynamic_story_ai(topic=catalog_item["topic"], ep_num=ep_num, past_topics=past_topics)
        if ai_story and ai_story.get("dialogue"):
            catalog_item["thumbnail_title_1"] = ai_story.get("thumbnail_title_1", catalog_item["thumbnail_title_1"])
            catalog_item["thumbnail_title_2"] = ai_story.get("thumbnail_title_2", catalog_item["thumbnail_title_2"])
            catalog_item["thumbnail_hook"] = ai_story.get("thumbnail_hook", catalog_item["thumbnail_hook"])
            dialogue = ai_story["dialogue"]

    if not dialogue:
        dialogue = EPISODE_1_SCRIPT

    total_turns = len(dialogue)
    turns_per_act = max(1, total_turns // 5)
    chapters = []
    for act_idx, act_info in enumerate(catalog_item["acts"]):
        start_turn = min(act_idx * turns_per_act, total_turns - 1)
        chapters.append({
            "act": act_idx + 1,
            "title": act_info[0],
            "description": act_info[1],
            "start_turn": start_turn,
            "start_time": 0.0
        })

    total_words = sum(len(t["text"].split()) for t in dialogue)
    print(f"[StoryGenerator] Dialogue assembled: {len(dialogue)} turns, {total_words} words.")
    est_duration_mins = (total_words / 115.0) + (len(dialogue) * config.PAUSE_BETWEEN_TURNS / 60.0)
    print(f"[StoryGenerator] Estimated spoken duration: ~{est_duration_mins:.1f} minutes.")

    return {
        "episode": ep_num,
        "topic": catalog_item["topic"],
        "focus": catalog_item["focus"],
        "thumbnail_title_1": catalog_item["thumbnail_title_1"],
        "thumbnail_title_2": catalog_item["thumbnail_title_2"],
        "thumbnail_hook": catalog_item["thumbnail_hook"],
        "chapters": chapters,
        "dialogue": dialogue
    }

def generate_metadata(topic: str, total_duration_sec: float, chapters: list, ep_num: int = 1, story: dict = None) -> dict:
    """Formats dynamic YouTube title, timestamps description, tags, and metadata."""
    if story and story.get("focus"):
        focus_desc = story["focus"]
    else:
        focus_desc = f"Nikola Tesla's visionary scientific and philosophical inquiry into {topic}."

    clean_topic = topic.replace("Nikola Tesla on ", "").replace("Nikola Tesla: ", "")
    title = f"Nikola Tesla: {clean_topic} | The Secrets of Cosmic Energy (Ep. {ep_num:02d})"
    if len(title) > 98:
        title = f"Nikola Tesla: {clean_topic[:60]}... (Ep. {ep_num:02d})"

    desc_lines = [
        f"{focus_desc}",
        "",
        '"If you want to find the secrets of the universe, think in terms of energy, frequency and vibration."',
        " — Nikola Tesla",
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "TIMESTAMPS & CHAPTERS:",
    ]

    for ch in chapters:
        sec = int(ch.get("start_time", 0.0))
        mm = sec // 60
        ss = sec % 60
        desc_lines.append(f"{mm:02d}:{ss:02d} - {ch['title']}")

    desc_lines.extend([
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "ABOUT THE TESLA CURRENTS:",
        "The Tesla Currents is dedicated to exploring the profound discoveries, prophetic visions, and cosmic philosophy of Nikola Tesla. We explore the mysteries of electricity, the 3-6-9 universal resonance, wireless energy, and the radiant fabric of the universe.",
        "",
        "Subscribe to join our visionary circle: @TheTeslaCurrents",
        "",
        "RECOMMENDED TESLA WORKS:",
        "• My Inventions: The Autobiography of Nikola Tesla",
        "• Experiments with Alternate Currents of High Potential and High Frequency",
        "• The Problem of Increasing Human Energy (1900)",
        "• Colorado Springs Notes 1899-1900",
        "",
        f"#NikolaTesla #Tesla #Energy #Frequency #Vibration #369Code #Physics #CosmicEnergy #Wardenclyffe #Science #Philosophy"
    ])

    return {
        "title": title,
        "description": "\n".join(desc_lines),
        "tags": [
            "Nikola Tesla", "Tesla", clean_topic, "369 code", "Energy frequency vibration",
            "Wardenclyffe", "Free energy", "Wireless power", "Alternating current", "Physics",
            "Cosmic energy", "Tesla documentary", "Tesla Currents"
        ]
    }
