"""Rule-based recommendation engine for crop-residue reuse.

The engine is deliberately simple and transparent (no trained ML model):

    score = base suitability of the option for that residue
            + adjustment for moisture level
            + adjustment for residue quality
            + adjustment for quantity

Every option has a base score (0-10) per residue type, and small
positive/negative adjustments depending on moisture, quality and quantity.
Options scoring 5 or more are recommended (best four, at least two).

All farmer-facing text is stored in English ("en") and Tamil ("ta").
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Catalog: crops, residues, moisture, quality, units
# ---------------------------------------------------------------------------

CROPS = {
    "paddy": {
        "label": {"en": "Paddy (Rice)", "ta": "நெல்"},
        "icon": "🌾",
        "keywords": ["நெல்", "அரிசி", "paddy", "rice"],
        "residues": ["paddy_straw", "rice_husk"],
    },
    "sugarcane": {
        "label": {"en": "Sugarcane", "ta": "கரும்பு"},
        "icon": "🎋",
        "keywords": ["கரும்பு", "sugarcane", "sugar cane", "cane"],
        "residues": ["sugarcane_trash", "sugarcane_tops", "bagasse"],
    },
    "maize": {
        "label": {"en": "Maize", "ta": "மக்காச்சோளம்"},
        "icon": "🌽",
        "keywords": ["மக்காச்சோளம்", "மக்காசோளம்", "மக்கா", "maize", "corn"],
        "residues": ["maize_stover"],
    },
    "groundnut": {
        "label": {"en": "Groundnut", "ta": "நிலக்கடலை"},
        "icon": "🥜",
        "keywords": ["நிலக்கடலை", "கடலை", "groundnut", "ground nut", "peanut"],
        "residues": ["groundnut_haulms", "groundnut_shell"],
    },
    "cotton": {
        "label": {"en": "Cotton", "ta": "பருத்தி"},
        "icon": "☁️",
        "keywords": ["பருத்தி", "பஞ்சு", "cotton"],
        "residues": ["cotton_stalk"],
    },
    "millets": {
        "label": {"en": "Millets (Ragi, Cholam, Kambu)", "ta": "சிறுதானியங்கள் (கேழ்வரகு, சோளம், கம்பு)"},
        "icon": "🌿",
        "keywords": ["சிறுதானிய", "கேழ்வரகு", "ராகி", "கம்பு", "சோளம்", "millet", "ragi", "cholam", "kambu", "sorghum"],
        "residues": ["millet_stalk"],
    },
    "banana": {
        "label": {"en": "Banana", "ta": "வாழை"},
        "icon": "🍌",
        "keywords": ["வாழை", "banana", "plantain"],
        "residues": ["banana_waste"],
    },
    "coconut": {
        "label": {"en": "Coconut", "ta": "தென்னை"},
        "icon": "🥥",
        "keywords": ["தென்னை", "தேங்காய்", "coconut"],
        "residues": ["coconut_waste"],
    },
    "pulses": {
        "label": {"en": "Pulses (Black gram, Green gram)", "ta": "பயறு வகைகள் (உளுந்து, பாசிப்பயறு)"},
        "icon": "🌱",
        "keywords": ["பயறு", "உளுந்து", "பாசி", "துவரை", "pulse", "pulses", "gram", "dal", "lentil"],
        "residues": ["pulses_straw"],
    },
    "other": {
        "label": {"en": "Other crop", "ta": "மற்ற பயிர்"},
        "icon": "➕",
        "keywords": ["மற்ற", "வேறு", "other", "else"],
        "residues": ["other"],
    },
}

RESIDUES = {
    "paddy_straw": {
        "label": {"en": "Paddy straw", "ta": "நெல் வைக்கோல்"},
        "keywords": ["வைக்கோல்", "straw"],
    },
    "rice_husk": {
        "label": {"en": "Rice husk", "ta": "நெல் உமி"},
        "keywords": ["உமி", "husk"],
    },
    "sugarcane_trash": {
        "label": {"en": "Sugarcane trash (dry leaves)", "ta": "கரும்புத் தோகை"},
        "keywords": ["தோகை", "trash", "leaves", "leaf"],
    },
    "sugarcane_tops": {
        "label": {"en": "Sugarcane tops", "ta": "கரும்பு நுனி"},
        "keywords": ["நுனி", "tops", "top"],
    },
    "bagasse": {
        "label": {"en": "Bagasse (crushed cane)", "ta": "கரும்புச் சக்கை"},
        "keywords": ["சக்கை", "bagasse", "crushed"],
    },
    "maize_stover": {
        "label": {"en": "Maize stalks and leaves", "ta": "மக்காச்சோளத் தட்டை"},
        "keywords": ["தட்டை", "தண்டு", "stover", "stalk"],
    },
    "groundnut_haulms": {
        "label": {"en": "Groundnut haulms (vines)", "ta": "நிலக்கடலைக் கொடி"},
        "keywords": ["கொடி", "haulm", "vine"],
    },
    "groundnut_shell": {
        "label": {"en": "Groundnut shells", "ta": "நிலக்கடலை ஓடு"},
        "keywords": ["ஓடு", "shell"],
    },
    "cotton_stalk": {
        "label": {"en": "Cotton stalks", "ta": "பருத்திச் செடித் தண்டு"},
        "keywords": ["தண்டு", "stalk"],
    },
    "millet_stalk": {
        "label": {"en": "Millet stalks (straw)", "ta": "சிறுதானியத் தட்டை"},
        "keywords": ["தட்டை", "தாள்", "straw", "stalk"],
    },
    "banana_waste": {
        "label": {"en": "Banana stem and leaves", "ta": "வாழைத்தண்டு மற்றும் இலை"},
        "keywords": ["தண்டு", "இலை", "stem", "leaves"],
    },
    "coconut_waste": {
        "label": {"en": "Coconut husk, fronds, shells", "ta": "தேங்காய் மட்டை, ஓலை, சிரட்டை"},
        "keywords": ["மட்டை", "ஓலை", "சிரட்டை", "husk", "fronds", "shell"],
    },
    "pulses_straw": {
        "label": {"en": "Pulses straw (haulms)", "ta": "பயறு செடித் தண்டு"},
        "keywords": ["தண்டு", "straw", "haulm"],
    },
    "other": {
        "label": {"en": "Other residue", "ta": "மற்ற கழிவு"},
        "keywords": ["மற்ற", "other"],
    },
}

MOISTURE = {
    "low": {
        "label": {"en": "Dry", "ta": "உலர்ந்தது"},
        "short": {"en": "dry", "ta": "உலர்ந்த"},
        "hint": {"en": "Crackles or snaps when bent", "ta": "வளைத்தால் சடசடவென முறியும்"},
        "icon": "☀️",
        "keywords": ["உலர்", "காய்ந்த", "காய்", "dry", "low"],
    },
    "medium": {
        "label": {"en": "Slightly damp", "ta": "சிறிது ஈரம்"},
        "short": {"en": "slightly damp", "ta": "சிறிது ஈரமான"},
        "hint": {"en": "Feels cool and a little soft", "ta": "குளிர்ச்சியாகவும் சற்று மென்மையாகவும் இருக்கும்"},
        "icon": "🌦️",
        "keywords": ["சிறிது", "நடுத்தர", "மிதமான", "medium", "slightly", "damp", "moderate"],
    },
    "high": {
        "label": {"en": "Wet or green", "ta": "ஈரமானது / பசுமையானது"},
        "short": {"en": "wet", "ta": "ஈரமான"},
        "hint": {"en": "Feels wet; squeezing gives water or sap", "ta": "ஈரமாக இருக்கும்; பிழிந்தால் நீர் அல்லது சாறு வரும்"},
        "icon": "💧",
        "keywords": ["ஈர", "பசுமை", "பச்சை", "wet", "green", "high", "moist"],
    },
}

QUALITY = {
    "good": {
        "label": {"en": "Good", "ta": "நல்லது"},
        "short": {"en": "good quality", "ta": "நல்ல தரம்"},
        "hint": {"en": "Clean, no mold or disease", "ta": "சுத்தமானது; பூஞ்சை, நோய் இல்லை"},
        "icon": "😊",
        "keywords": ["நல்ல", "நன்று", "சுத்த", "good", "clean", "fresh"],
    },
    "fair": {
        "label": {"en": "Average", "ta": "சராசரி"},
        "short": {"en": "average quality", "ta": "சராசரி தரம்"},
        "hint": {"en": "Some dirt, damage or old spots", "ta": "சிறிது அழுக்கு அல்லது சேதம்"},
        "icon": "😐",
        "keywords": ["சராசரி", "பரவாயில்லை", "average", "fair", "okay", "so-so"],
    },
    "poor": {
        "label": {"en": "Poor", "ta": "மோசம்"},
        "short": {"en": "poor quality", "ta": "மோசமான தரம்"},
        "hint": {"en": "Moldy, diseased or rotting", "ta": "பூஞ்சை, நோய் அல்லது அழுகல் உள்ளது"},
        "icon": "⚠️",
        "keywords": ["மோசம்", "கெட்ட", "பூஞ்சை", "அழுகிய", "அழுகல்", "நோய்", "poor", "bad", "moldy", "mouldy", "rotten", "diseased"],
    },
}

UNITS = {
    "kg": {"label": {"en": "kg", "ta": "கிலோ"}, "to_kg": 1,
           "keywords": ["கிலோ", "கிகி", "kg", "kilo", "kilogram"]},
    "quintal": {"label": {"en": "quintal", "ta": "குவிண்டால்"}, "to_kg": 100,
                "keywords": ["குவிண்டால்", "குவின்டால்", "குயின்டால்", "quintal"]},
    "tonne": {"label": {"en": "tonne", "ta": "டன்"}, "to_kg": 1000,
              "keywords": ["டன்", "ton", "tonne"]},
}

TN_DISTRICTS = [
    "Ariyalur", "Chengalpattu", "Chennai", "Coimbatore", "Cuddalore", "Dharmapuri",
    "Dindigul", "Erode", "Kallakurichi", "Kancheepuram", "Kanniyakumari", "Karur",
    "Krishnagiri", "Madurai", "Mayiladuthurai", "Nagapattinam", "Namakkal", "Nilgiris",
    "Perambalur", "Pudukkottai", "Ramanathapuram", "Ranipet", "Salem", "Sivaganga",
    "Tenkasi", "Thanjavur", "Theni", "Thoothukudi", "Tiruchirappalli", "Tirunelveli",
    "Tirupathur", "Tiruppur", "Tiruvallur", "Tiruvannamalai", "Tiruvarur", "Vellore",
    "Viluppuram", "Virudhunagar",
]

# Residues that are naturally wet/green when fresh: moisture penalties are halved.
NATURALLY_WET = {"banana_waste", "sugarcane_tops"}

SMALL_LIMIT_KG = 500
LARGE_LIMIT_KG = 5000
MAX_QUANTITY_KG = 10_000_000

# ---------------------------------------------------------------------------
# Reuse options (bilingual content)
# ---------------------------------------------------------------------------

OPTIONS = {
    "compost": {
        "icon": "🌱",
        "title": {"en": "Compost preparation", "ta": "உரமாக்கல் (கம்போஸ்ட்)"},
        "description": {
            "en": "Convert the residue into nutrient-rich organic manure by piling it with cow dung and a microbial decomposer.",
            "ta": "மாட்டுச் சாணம் மற்றும் நுண்ணுயிர் கலவையுடன் அடுக்கி, கழிவை சத்து நிறைந்த இயற்கை உரமாக மாற்றலாம்.",
        },
        "steps": {
            "en": [
                "Chop or shred the residue into small pieces.",
                "Layer it with cow dung and a decomposer culture in a heap or pit.",
                "Keep it moist and turn it every 15-20 days until it turns dark and crumbly.",
            ],
            "ta": [
                "கழிவை சிறு துண்டுகளாக நறுக்கவும் அல்லது அரைக்கவும்.",
                "குவியல் அல்லது குழியில் மாட்டுச் சாணம் மற்றும் நுண்ணுயிர் கலவையுடன் அடுக்குகளாக இடவும்.",
                "ஈரப்பதத்தை பராமரித்து, 15-20 நாட்களுக்கு ஒருமுறை புரட்டி, கருமையாகவும் உதிரியாகவும் மாறும் வரை விடவும்.",
            ],
        },
        "precautions": {
            "en": [
                "Keep the heap moist but not waterlogged.",
                "Use diseased residue only after full, hot composting and complete maturing.",
            ],
            "ta": [
                "குவியலை ஈரமாக வைக்கவும்; ஆனால் தண்ணீர் தேங்க விடாதீர்கள்.",
                "நோய் பாதித்த கழிவை நன்கு சூடேறி முழுமையாக மக்கிய பின்னரே பயன்படுத்தவும்.",
            ],
        },
    },
    "mulching": {
        "icon": "🍂",
        "title": {"en": "Mulching", "ta": "மூடாக்கு (மல்ச்சிங்)"},
        "description": {
            "en": "Spread dry residue around crops to hold soil moisture, suppress weeds and protect the soil.",
            "ta": "உலர்ந்த கழிவை பயிர்களைச் சுற்றி பரப்பினால் மண் ஈரம் காக்கப்படும், களைகள் குறையும், மண் பாதுகாக்கப்படும்.",
        },
        "steps": {
            "en": [
                "Use dry, clean residue cut into manageable lengths.",
                "Spread a layer of about 5-10 cm between rows or around plants.",
                "Top up the layer as it decomposes.",
            ],
            "ta": [
                "உலர்ந்த, சுத்தமான கழிவை பொருத்தமான நீளத்தில் வெட்டிக்கொள்ளவும்.",
                "வரிசைகளுக்கு இடையே அல்லது செடிகளைச் சுற்றி சுமார் 5-10 செ.மீ. தடிமனில் பரப்பவும்.",
                "மக்கும்போது தேவைக்கேற்ப மீண்டும் இடவும்.",
            ],
        },
        "precautions": {
            "en": [
                "Keep mulch a little away from plant stems to avoid rot and termites.",
                "Do not mulch with diseased or pest-infested residue.",
            ],
            "ta": [
                "அழுகல் மற்றும் கரையான் தாக்குதலைத் தவிர்க்க, தண்டுகளிலிருந்து சற்று இடைவெளி விடவும்.",
                "நோய் அல்லது பூச்சி பாதித்த கழிவை மூடாக்காகப் பயன்படுத்த வேண்டாம்.",
            ],
        },
    },
    "animal_feed": {
        "icon": "🐄",
        "title": {"en": "Animal feed (fodder)", "ta": "கால்நடை தீவனம்"},
        "description": {
            "en": "Clean, dry, mold-free residue can be fed to cattle and goats, ideally after chopping or urea treatment.",
            "ta": "சுத்தமான, உலர்ந்த, பூஞ்சை இல்லாத கழிவை நறுக்கி அல்லது யூரியா சிகிச்சை செய்து மாடு, ஆடுகளுக்கு தீவனமாக அளிக்கலாம்.",
        },
        "steps": {
            "en": [
                "Check that the residue is clean, dry and free of mold.",
                "Chop it and mix with green fodder or concentrate for better nutrition.",
                "Store in a dry, covered place away from rain.",
            ],
            "ta": [
                "கழிவு சுத்தமாகவும், உலர்ந்ததாகவும், பூஞ்சை இல்லாததாகவும் உள்ளதா என சரிபார்க்கவும்.",
                "ஊட்டச்சத்து அதிகரிக்க நறுக்கி, பசுந்தீவனம் அல்லது அடர் தீவனத்துடன் கலந்து கொடுக்கவும்.",
                "மழை படாத உலர்ந்த, மூடிய இடத்தில் சேமிக்கவும்.",
            ],
        },
        "precautions": {
            "en": [
                "Never feed moldy or rotten residue; it can make animals sick.",
                "Ask a veterinary officer before starting urea treatment or changing the diet.",
            ],
            "ta": [
                "பூஞ்சை பிடித்த அல்லது அழுகிய கழிவை ஒருபோதும் கொடுக்க வேண்டாம்; கால்நடைகள் நோய்வாய்ப்படலாம்.",
                "யூரியா சிகிச்சை அல்லது தீவன மாற்றத்தைத் தொடங்கும் முன் கால்நடை மருத்துவரிடம் கேளுங்கள்.",
            ],
        },
    },
    "mushroom": {
        "icon": "🍄",
        "title": {"en": "Mushroom cultivation", "ta": "காளான் வளர்ப்பு"},
        "description": {
            "en": "Straw and similar residues can serve as the growing bed for oyster or paddy-straw mushrooms, giving extra income.",
            "ta": "வைக்கோல் போன்ற கழிவுகளை சிப்பிக் காளான் அல்லது வைக்கோல் காளான் வளர்ப்புக்கான படுக்கையாகப் பயன்படுத்தி கூடுதல் வருமானம் பெறலாம்.",
        },
        "steps": {
            "en": [
                "Cut the dry straw into small pieces, soak it, then pasteurise it.",
                "Mix with spawn and fill into bags or beds.",
                "Keep a clean, shaded, humid room until mushrooms appear.",
            ],
            "ta": [
                "உலர்ந்த வைக்கோலை சிறு துண்டுகளாக வெட்டி ஊறவைத்து, கொதிநீர் அல்லது நீராவியில் கிருமி நீக்கம் செய்யவும்.",
                "காளான் விதையுடன் கலந்து பைகள் அல்லது படுக்கைகளில் நிரப்பவும்.",
                "காளான் வரும் வரை சுத்தமான, நிழலான, ஈரப்பதம் உள்ள அறையில் வைக்கவும்.",
            ],
        },
        "precautions": {
            "en": [
                "Use only fresh, clean, mold-free straw; contamination ruins the crop.",
                "Get quality spawn and training from a KVK or agricultural university.",
            ],
            "ta": [
                "புதிய, சுத்தமான, பூஞ்சை இல்லாத வைக்கோலை மட்டும் பயன்படுத்தவும்; மாசு பட்டால் மகசூல் பாதிக்கும்.",
                "தரமான காளான் விதை மற்றும் பயிற்சியை வேளாண் அறிவியல் நிலையம் (KVK) அல்லது வேளாண் பல்கலைக்கழகத்தில் பெறவும்.",
            ],
        },
    },
    "incorporation": {
        "icon": "🚜",
        "title": {"en": "Field incorporation with decomposer", "ta": "நிலத்திலேயே மக்கச் செய்தல்"},
        "description": {
            "en": "Chop and mix the residue into the soil with a decomposer so it enriches soil organic matter instead of being burned.",
            "ta": "கழிவை நறுக்கி, மக்கச்செய்யும் நுண்ணுயிர் கலவையுடன் மண்ணில் கலந்தால், எரிக்காமலேயே மண்ணின் அங்கக சத்து உயரும்.",
        },
        "steps": {
            "en": [
                "Spread the chopped residue evenly across the field.",
                "Apply a decomposer culture and a little nitrogen fertiliser or cow-dung slurry.",
                "Plough it in, irrigate lightly and wait a few weeks before sowing the next crop.",
            ],
            "ta": [
                "நறுக்கிய கழிவை வயல் முழுவதும் சமமாகப் பரப்பவும்.",
                "மக்கச்செய்யும் நுண்ணுயிர் கலவையுடன் சிறிதளவு தழைச்சத்து உரம் அல்லது சாணக் கரைசல் இடவும்.",
                "உழுது மண்ணில் கலந்து, லேசாக நீர் பாய்ச்சி, அடுத்த பயிர் விதைக்கும் முன் சில வாரங்கள் காத்திருக்கவும்.",
            ],
        },
        "precautions": {
            "en": [
                "Do not plough in diseased residue; it can carry the problem into the next crop.",
                "Fresh residue can temporarily lock up soil nitrogen, so allow time to decompose.",
            ],
            "ta": [
                "நோய் பாதித்த கழிவை மண்ணில் கலக்க வேண்டாம்; அடுத்த பயிரைப் பாதிக்கலாம்.",
                "புதிய கழிவு தற்காலிகமாக மண்ணின் தழைச்சத்தை எடுத்துக்கொள்ளும்; எனவே மக்க நேரம் அளிக்கவும்.",
            ],
        },
    },
    "vermicompost": {
        "icon": "🐛",
        "title": {"en": "Vermicompost", "ta": "மண்புழு உரம்"},
        "description": {
            "en": "Earthworms turn partly decomposed residue and cow dung into a fine, high-quality manure.",
            "ta": "மண்புழுக்கள் பகுதியளவு மக்கிய கழிவையும் மாட்டுச் சாணத்தையும் தரமான நுண்ணிய உரமாக மாற்றும்.",
        },
        "steps": {
            "en": [
                "Pre-decompose the residue with cow dung for 2-3 weeks.",
                "Spread it in shaded beds or tanks and release earthworms.",
                "Keep it moist and harvest the vermicompost in about 45-60 days.",
            ],
            "ta": [
                "கழிவை மாட்டுச் சாணத்துடன் 2-3 வாரம் முன்கூட்டியே மக்க விடவும்.",
                "நிழலான படுக்கைகள் அல்லது தொட்டிகளில் பரப்பி மண்புழுக்களை விடவும்.",
                "ஈரத்தை பராமரித்து, சுமார் 45-60 நாட்களில் உரத்தை அறுவடை செய்யவும்.",
            ],
        },
        "precautions": {
            "en": [
                "Keep beds shaded and moist, and protect them from ants, rats and birds.",
                "Do not add fresh, hot or moldy material directly to the worms.",
            ],
            "ta": [
                "படுக்கைகளை நிழலில் ஈரமாக வைத்து, எறும்பு, எலி, பறவைகளிடமிருந்து பாதுகாக்கவும்.",
                "புதிய, சூடான அல்லது பூஞ்சை பிடித்த கழிவை நேரடியாக புழுக்களுக்கு இட வேண்டாம்.",
            ],
        },
    },
    "biogas": {
        "icon": "🔥",
        "title": {"en": "Biogas (with cow dung)", "ta": "உயிர்வாயு (சாணத்துடன்)"},
        "description": {
            "en": "Soft, wet residue mixed with cow dung can feed a biogas digester for cooking gas and slurry manure.",
            "ta": "மென்மையான ஈரக் கழிவை மாட்டுச் சாணத்துடன் கலந்து உயிர்வாயு அமைப்பில் இட்டால் சமையல் வாயுவும் உரக்கரைசலும் கிடைக்கும்.",
        },
        "steps": {
            "en": [
                "Chop the residue finely and remove stones or hard material.",
                "Mix with cow dung and water in the recommended ratio for your digester.",
                "Use the gas for cooking and the leftover slurry as manure.",
            ],
            "ta": [
                "கழிவை மிக நுண்ணியதாக நறுக்கி, கற்கள் மற்றும் கடினப் பொருட்களை நீக்கவும்.",
                "உங்கள் அமைப்புக்கு பரிந்துரைக்கப்பட்ட விகிதத்தில் சாணம் மற்றும் நீருடன் கலக்கவும்.",
                "வாயுவை சமையலுக்கும், மீதமுள்ள கரைசலை உரமாகவும் பயன்படுத்தவும்.",
            ],
        },
        "precautions": {
            "en": [
                "Needs a properly built digester and steady feeding; seek technical help.",
                "Follow gas-safety rules: check for leaks and keep flames away from the plant.",
            ],
            "ta": [
                "சரியாக அமைக்கப்பட்ட உயிர்வாயு அமைப்பும் தொடர்ந்த உணவளிப்பும் தேவை; தொழில்நுட்ப உதவி பெறவும்.",
                "வாயுக் கசிவு உள்ளதா எனப் பார்த்து, நெருப்பை அமைப்பிலிருந்து தள்ளி வைக்கவும்.",
            ],
        },
    },
    "biochar": {
        "icon": "♨️",
        "title": {"en": "Biochar (controlled charring)", "ta": "உயிர்க்கரி (கட்டுப்படுத்திய கரியாக்கல்)"},
        "description": {
            "en": "Hard, dry residue can be converted to charcoal-like biochar in a closed kiln and added to soil to improve it.",
            "ta": "கடினமான உலர்ந்த கழிவை மூடிய உலையில் கரியாக மாற்றி, மண்ணின் தரத்தை உயர்த்த இடலாம்.",
        },
        "steps": {
            "en": [
                "Dry the residue fully.",
                "Char it with limited air in a drum or pit kiln, never in the open.",
                "Quench the char, crush it and mix with compost before adding to soil.",
            ],
            "ta": [
                "கழிவை நன்கு உலர்த்தவும்.",
                "திறந்த வெளியில் அல்லாமல், குறைந்த காற்றோட்டத்துடன் டிரம் அல்லது குழி உலையில் கரியாக்கவும்.",
                "கரியை நீர் தெளித்து அணைத்து, தூளாக்கி, உரத்துடன் கலந்து மண்ணில் இடவும்.",
            ],
        },
        "precautions": {
            "en": [
                "Never burn in the open; use a kiln and keep water ready for fire safety.",
                "Wear gloves and a mask, and avoid breathing the smoke.",
            ],
            "ta": [
                "திறந்த வெளியில் எரிக்க வேண்டாம்; உலையைப் பயன்படுத்தி, தீ பாதுகாப்புக்கு நீர் தயாராக வைக்கவும்.",
                "கையுறை, முகக்கவசம் அணிந்து புகையைச் சுவாசிப்பதைத் தவிர்க்கவும்.",
            ],
        },
    },
    "briquette": {
        "icon": "🧱",
        "title": {"en": "Biomass briquettes / pellets", "ta": "உயிர்மக் எரிகட்டிகள்"},
        "description": {
            "en": "Dry residue can be compressed into fuel briquettes for boilers, kilns and cooking stoves.",
            "ta": "உலர்ந்த கழிவை அழுத்தி, கொதிகலன்கள், சூளைகள், அடுப்புகளுக்கான எரிகட்டிகளாக மாற்றலாம்.",
        },
        "steps": {
            "en": [
                "Dry the residue to low moisture and shred it.",
                "Press it in a briquetting machine, or supply it to a nearby unit that has one.",
                "Sell or use the briquettes as fuel.",
            ],
            "ta": [
                "கழிவை ஈரம் குறையும் வரை உலர்த்தி, அரைக்கவும்.",
                "எரிகட்டி இயந்திரத்தில் அழுத்தவும், அல்லது அருகிலுள்ள தயாரிப்பு நிலையத்திற்கு வழங்கவும்.",
                "எரிகட்டிகளை எரிபொருளாக விற்கவும் அல்லது பயன்படுத்தவும்.",
            ],
        },
        "precautions": {
            "en": [
                "Moisture must be low (roughly under 15%) for good briquettes.",
                "Store dry and covered; dry biomass is a fire risk.",
            ],
            "ta": [
                "நல்ல எரிகட்டிகளுக்கு ஈரப்பதம் குறைவாக (சுமார் 15%-க்கு கீழ்) இருக்க வேண்டும்.",
                "உலர்ந்த, மூடிய இடத்தில் சேமிக்கவும்; உலர்ந்த கழிவில் தீ பிடிக்கும் அபாயம் உண்டு.",
            ],
        },
    },
    "sell_biomass": {
        "icon": "💰",
        "title": {"en": "Sell to biomass buyers", "ta": "உயிர்மக் கழிவு வாங்குவோருக்கு விற்பனை"},
        "description": {
            "en": "Large quantities of dry residue can be sold to biomass power plants, boilers, paper or board units and fodder traders.",
            "ta": "அதிக அளவு உலர்ந்த கழிவை உயிர்மக் மின் நிலையங்கள், கொதிகலன்கள், காகித/அட்டை ஆலைகள், தீவன வியாபாரிகளுக்கு விற்கலாம்.",
        },
        "steps": {
            "en": [
                "Bale or bundle the dry residue to ease transport.",
                "Pool the quantity with neighbours or through a farmer group (FPO/SHG).",
                "Contact local buyers and compare prices before selling.",
            ],
            "ta": [
                "போக்குவரத்து எளிதாக உலர்ந்த கழிவை கட்டுகளாகக் கட்டவும்.",
                "அண்டை விவசாயிகள் அல்லது விவசாய உற்பத்தியாளர் குழு/சுய உதவிக் குழு மூலம் அளவைச் சேர்க்கவும்.",
                "உள்ளூர் வாங்குவோரைத் தொடர்புகொண்டு விலைகளை ஒப்பிட்ட பின் விற்கவும்.",
            ],
        },
        "precautions": {
            "en": [
                "Check the buyer, price and transport cost first; small lots may not pay.",
                "Keep stacks dry and away from fire sources.",
            ],
            "ta": [
                "முதலில் வாங்குவோர், விலை, போக்குவரத்துச் செலவு ஆகியவற்றைச் சரிபார்க்கவும்; சிறிய அளவு கட்டுபடியாகாது.",
                "கட்டுகளை உலர்ந்த நிலையில், தீ மூலங்களிலிருந்து தள்ளி வைக்கவும்.",
            ],
        },
    },
    "fibre": {
        "icon": "🧵",
        "title": {"en": "Fibre and craft products", "ta": "நார் மற்றும் கைவினைப் பொருட்கள்"},
        "description": {
            "en": "Fibrous residue such as banana stem or coconut husk can be turned into fibre, ropes, mats and other products.",
            "ta": "வாழைத்தண்டு, தேங்காய் மட்டை போன்ற நார்க் கழிவுகளை நார், கயிறு, விரிப்புகள் போன்ற பொருட்களாக மாற்றலாம்.",
        },
        "steps": {
            "en": [
                "Collect fresh stems or husks and separate the fibre with a decorticator or by retting.",
                "Dry and clean the fibre.",
                "Sell it to coir/fibre units or make products with a self-help group.",
            ],
            "ta": [
                "புதிய தண்டு அல்லது மட்டையைச் சேகரித்து, நார் பிரிப்பு இயந்திரம் அல்லது ஊறவைத்தல் மூலம் நாரைப் பிரிக்கவும்.",
                "நாரை உலர்த்தி சுத்தம் செய்யவும்.",
                "நார்த் தொழிற்சாலைகளுக்கு விற்கவும் அல்லது சுய உதவிக் குழு மூலம் பொருட்கள் செய்யவும்.",
            ],
        },
        "precautions": {
            "en": [
                "Needs a simple machine or a nearby fibre unit.",
                "Manage retting water properly so it does not pollute ponds or wells.",
            ],
            "ta": [
                "எளிய இயந்திரம் அல்லது அருகில் நார்த் தொழிற்சாலை தேவை.",
                "ஊறவைத்த நீர் குளம், கிணற்றில் கலந்து மாசுபடாதவாறு சரியாகக் கையாளவும்.",
            ],
        },
    },
}

OPTION_ORDER = [
    "compost", "mulching", "animal_feed", "mushroom", "incorporation", "vermicompost",
    "biogas", "biochar", "briquette", "sell_biomass", "fibre",
]

# ---------------------------------------------------------------------------
# Rule tables
# ---------------------------------------------------------------------------

# Base suitability (0-10) of each reuse option for each residue type.
#            compost mulch feed mush incorp vermi biogas biochar briq sell fibre
_BASE_ROWS = {
    "paddy_straw":      (8, 8, 6, 7, 8, 5, 4, 5, 5, 6, 0),
    "rice_husk":        (3, 5, 0, 1, 2, 2, 0, 9, 8, 8, 0),
    "sugarcane_trash":  (9, 10, 3, 4, 7, 6, 5, 6, 5, 5, 0),
    "sugarcane_tops":   (5, 5, 10, 2, 4, 5, 5, 3, 2, 3, 0),
    "bagasse":          (7, 6, 1, 6, 3, 6, 6, 6, 9, 9, 2),
    "maize_stover":     (7, 7, 9, 4, 6, 5, 6, 5, 6, 5, 0),
    "groundnut_haulms": (6, 5, 10, 2, 6, 5, 5, 3, 3, 4, 0),
    "groundnut_shell":  (5, 5, 1, 1, 3, 2, 1, 8, 9, 8, 0),
    "cotton_stalk":     (6, 5, 0, 4, 4, 3, 3, 8, 9, 8, 0),
    "millet_stalk":     (6, 7, 10, 3, 6, 4, 5, 4, 5, 5, 0),
    "banana_waste":     (8, 7, 4, 3, 5, 9, 7, 4, 2, 2, 9),
    "coconut_waste":    (7, 8, 0, 2, 3, 7, 3, 7, 6, 6, 10),
    "pulses_straw":     (8, 7, 8, 4, 8, 6, 5, 4, 4, 4, 0),
    "other":            (8, 6, 3, 3, 6, 6, 4, 6, 5, 4, 1),
}
BASE_SCORES = {
    residue: dict(zip(OPTION_ORDER, row)) for residue, row in _BASE_ROWS.items()
}

# Adjustments by moisture (low/medium/high), quality (good/fair/poor)
# and quantity (small/medium/large).
MODIFIERS = {
    "compost": {
        "moisture": {"low": 0, "medium": 1, "high": 1},
        "quality": {"good": 0, "fair": 0, "poor": 1},
        "quantity": {"small": 0, "medium": 0, "large": 1},
    },
    "mulching": {
        "moisture": {"low": 1, "medium": 0, "high": -3},
        "quality": {"good": 0, "fair": -1, "poor": -4},
        "quantity": {"small": 1, "medium": 0, "large": -1},
    },
    "animal_feed": {
        "moisture": {"low": 1, "medium": 0, "high": -4},
        "quality": {"good": 1, "fair": -2, "poor": -10},
        "quantity": {"small": 1, "medium": 0, "large": -1},
    },
    "mushroom": {
        "moisture": {"low": 0, "medium": 0, "high": -3},
        "quality": {"good": 1, "fair": -1, "poor": -8},
        "quantity": {"small": 1, "medium": -1, "large": -3},
    },
    "incorporation": {
        "moisture": {"low": 0, "medium": 0, "high": 1},
        "quality": {"good": 0, "fair": -1, "poor": -4},
        "quantity": {"small": 0, "medium": 0, "large": 1},
    },
    "vermicompost": {
        "moisture": {"low": -1, "medium": 1, "high": 2},
        "quality": {"good": 0, "fair": 0, "poor": -2},
        "quantity": {"small": 1, "medium": 1, "large": -2},
    },
    "biogas": {
        "moisture": {"low": -2, "medium": 1, "high": 2},
        "quality": {"good": 0, "fair": 0, "poor": 0},
        "quantity": {"small": -2, "medium": 1, "large": 1},
    },
    "biochar": {
        "moisture": {"low": 2, "medium": 0, "high": -3},
        "quality": {"good": 0, "fair": 0, "poor": 2},
        "quantity": {"small": 0, "medium": 1, "large": 1},
    },
    "briquette": {
        "moisture": {"low": 2, "medium": 0, "high": -5},
        "quality": {"good": 1, "fair": 0, "poor": -2},
        "quantity": {"small": -4, "medium": 0, "large": 2},
    },
    "sell_biomass": {
        "moisture": {"low": 2, "medium": 0, "high": -4},
        "quality": {"good": 1, "fair": 0, "poor": -3},
        "quantity": {"small": -6, "medium": -1, "large": 2},
    },
    "fibre": {
        "moisture": {"low": 0, "medium": 0, "high": 0},
        "quality": {"good": 0, "fair": -1, "poor": -3},
        "quantity": {"small": -1, "medium": 0, "large": 1},
    },
}

# Situation-specific notes shown on a recommendation when the condition matches:
# (option, factor, level, English, Tamil)
NOTES = [
    ("mulching", "moisture", "high",
     "Your residue is wet: spread it in the sun for a few days first, otherwise it may rot and attract pests.",
     "உங்கள் கழிவு ஈரமாக உள்ளது: முதலில் சில நாட்கள் வெயிலில் உலர்த்தவும்; இல்லையெனில் அழுகி பூச்சிகளை ஈர்க்கலாம்."),
    ("mulching", "quality", "poor",
     "Poor-quality or diseased residue can spread problems to your crop, so mulching is not advised.",
     "தரம் குறைந்த அல்லது நோய் பாதித்த கழிவு பயிருக்கு நோயைப் பரப்பலாம்; எனவே மூடாக்கு பரிந்துரைக்கப்படாது."),
    ("mulching", "residue", "sugarcane_trash",
     "Trash mulching in sugarcane fields is a well-known practice that saves irrigation water and controls weeds.",
     "கரும்புத் தோகை மூடாக்கு நீர்ப்பாசனத்தைச் சேமிக்கவும் களைகளைக் கட்டுப்படுத்தவும் உதவும் நன்கு அறியப்பட்ட முறை."),
    ("animal_feed", "moisture", "high",
     "Wet residue spoils quickly; dry it in the sun or make silage before feeding.",
     "ஈரக் கழிவு விரைவில் கெட்டுவிடும்; வெயிலில் உலர்த்தவும் அல்லது ஊறுகாய்ப்புல் (சைலேஜ்) செய்து கொடுக்கவும்."),
    ("animal_feed", "quality", "poor",
     "Moldy or poor-quality residue is unsafe as feed, so this option is not recommended.",
     "பூஞ்சை பிடித்த அல்லது தரம் குறைந்த கழிவு தீவனமாக பாதுகாப்பற்றது; எனவே இது பரிந்துரைக்கப்படவில்லை."),
    ("animal_feed", "residue", "paddy_straw",
     "Paddy straw is low in protein; mix it with green fodder or concentrate.",
     "நெல் வைக்கோலில் புரதம் குறைவு; பசுந்தீவனம் அல்லது அடர் தீவனத்துடன் கலந்து கொடுக்கவும்."),
    ("animal_feed", "residue", "sugarcane_tops",
     "Fresh cane tops make good green fodder; feed within a day or two, or dry or ensile them.",
     "புதிய கரும்பு நுனிகள் நல்ல பசுந்தீவனம்; ஓரிரு நாளில் கொடுக்கவும் அல்லது உலர்த்தவும்/சைலேஜ் செய்யவும்."),
    ("animal_feed", "residue", "groundnut_haulms",
     "Dry groundnut haulms quickly in the sun; moldy haulms can carry aflatoxin, which is harmful to animals.",
     "நிலக்கடலைக் கொடியை விரைவாக வெயிலில் உலர்த்தவும்; பூஞ்சை பிடித்த கொடியில் அஃப்ளாடாக்சின் நச்சு இருக்கலாம், இது கால்நடைகளுக்குத் தீங்கு."),
    ("mushroom", "moisture", "high",
     "Very wet straw is easily contaminated; drain it and use it fresh.",
     "மிகவும் ஈரமான வைக்கோலில் எளிதாக மாசு சேரும்; நீர் வடித்து புதிதாகப் பயன்படுத்தவும்."),
    ("mushroom", "quality", "poor",
     "Moldy or poor-quality straw ruins mushroom beds, so this option is not recommended.",
     "பூஞ்சை பிடித்த அல்லது தரம் குறைந்த வைக்கோல் காளான் படுக்கையைக் கெடுக்கும்; எனவே இது பரிந்துரைக்கப்படவில்லை."),
    ("mushroom", "quantity", "large",
     "Mushroom growing uses only a small part of a large heap; combine it with another option.",
     "காளான் வளர்ப்பில் பெரிய குவியலின் ஒரு சிறு பகுதியே பயன்படும்; மற்றொரு வழியுடன் இணைத்துச் செய்யவும்."),
    ("compost", "moisture", "low",
     "Your residue is dry: sprinkle water while layering so it decomposes well.",
     "உங்கள் கழிவு உலர்ந்துள்ளது: அடுக்கும்போது நீர் தெளித்தால் நன்றாக மக்கும்."),
    ("compost", "moisture", "high",
     "Your residue is wet: mix it with dry material to avoid a soggy, smelly heap.",
     "உங்கள் கழிவு ஈரமாக உள்ளது: உலர்ந்த பொருளுடன் கலந்தால் நாற்றமுள்ள, தண்ணீர் தேங்கிய குவியலைத் தவிர்க்கலாம்."),
    ("compost", "quality", "poor",
     "Hot composting is a safe way to make diseased or poor-quality residue usable.",
     "நோய் பாதித்த அல்லது தரம் குறைந்த கழிவை நன்கு சூடேறும்படி மக்க வைத்தால் பாதுகாப்பாகப் பயன்படுத்தலாம்."),
    ("compost", "residue", "cotton_stalk",
     "Shred cotton stalks first; they are woody and decompose slowly.",
     "பருத்தித் தண்டுகள் கடினமானவை, மெதுவாக மக்கும்; முதலில் துண்டாக்கவும்."),
    ("compost", "residue", "rice_husk",
     "Rice husk decomposes very slowly; mix it with other residue and dung, or char it instead.",
     "நெல் உமி மிக மெதுவாக மக்கும்; பிற கழிவு, சாணத்துடன் கலக்கவும் அல்லது கரியாக்கவும்."),
    ("incorporation", "quality", "poor",
     "Diseased residue should not be ploughed back; prefer hot composting or charring.",
     "நோய் பாதித்த கழிவை மண்ணில் கலக்கக் கூடாது; சூடேறி மக்க வைத்தல் அல்லது கரியாக்கலை விரும்பவும்."),
    ("vermicompost", "moisture", "low",
     "Wet dry residue and pre-decompose it before giving it to worms.",
     "உலர்ந்த கழிவை நனைத்து, முன்கூட்டியே மக்க வைத்த பிறகே புழுக்களுக்கு இடவும்."),
    ("vermicompost", "quantity", "large",
     "Large quantities need many beds and space; use this for a part and compost the rest.",
     "அதிக அளவுக்கு பல படுக்கைகளும் இடமும் தேவை; ஒரு பகுதிக்கு இதைப் பயன்படுத்தி மீதத்தை உரமாக்கலாம்."),
    ("biogas", "moisture", "low",
     "Dry residue needs soaking and mixing with dung slurry before it goes into the digester.",
     "உலர்ந்த கழிவை ஊறவைத்து சாணக் கரைசலுடன் கலந்த பிறகே உயிர்வாயு அமைப்பில் இடவும்."),
    ("biogas", "quantity", "small",
     "A small quantity is hard to use steadily; combine with regular dung feed.",
     "குறைந்த அளவை தொடர்ந்து பயன்படுத்துவது கடினம்; வழக்கமான சாண உணவுடன் சேர்க்கவும்."),
    ("biochar", "moisture", "high",
     "Too wet for charring; dry the residue fully first.",
     "கரியாக்க மிகவும் ஈரமாக உள்ளது; முதலில் முழுமையாக உலர்த்தவும்."),
    ("biochar", "quality", "poor",
     "Controlled charring destroys disease organisms, so it is a safe use for poor-quality residue.",
     "கட்டுப்படுத்திய கரியாக்கல் நோய்க்கிருமிகளை அழிக்கும்; எனவே தரம் குறைந்த கழிவுக்கு இது பாதுகாப்பான பயன்பாடு."),
    ("briquette", "moisture", "high",
     "Too wet for briquettes; dry the residue first.",
     "எரிகட்டிகளுக்கு மிகவும் ஈரமாக உள்ளது; முதலில் உலர்த்தவும்."),
    ("briquette", "quantity", "small",
     "The quantity is small; deliver it to a nearby briquette unit or pool it with other farmers.",
     "அளவு குறைவு; அருகிலுள்ள எரிகட்டி நிலையத்தில் கொடுக்கவும் அல்லது பிற விவசாயிகளுடன் சேர்க்கவும்."),
    ("sell_biomass", "moisture", "high",
     "Buyers pay for dry material; dry the residue before selling.",
     "வாங்குவோர் உலர்ந்த கழிவுக்கே விலை தருவர்; விற்கும் முன் உலர்த்தவும்."),
    ("sell_biomass", "quantity", "small",
     "The quantity is small; selling may not pay unless pooled with other farmers.",
     "அளவு குறைவு; பிற விவசாயிகளுடன் சேர்க்காவிட்டால் விற்பனை கட்டுபடியாகாது."),
    ("fibre", "quantity", "small",
     "For a small quantity, join a self-help group or a nearby fibre unit instead of buying a machine.",
     "குறைந்த அளவுக்கு இயந்திரம் வாங்குவதை விட சுய உதவிக் குழு அல்லது அருகிலுள்ள நார்த் தொழிற்சாலையில் சேரவும்."),
]

GENERAL_PRECAUTIONS = {
    "en": [
        "Do not burn crop residue in the open. It pollutes the air, harms soil life and wastes nutrients.",
        "These are general guidelines. Check with your local Krishi Vigyan Kendra (KVK) or agricultural extension office before large-scale use.",
    ],
    "ta": [
        "பயிர்க் கழிவுகளை திறந்தவெளியில் எரிக்க வேண்டாம். காற்று மாசு ஏற்படும், மண் நுண்ணுயிர்கள் அழியும், சத்துகள் வீணாகும்.",
        "இவை பொதுவான வழிகாட்டுதல்கள். பெரிய அளவில் செயல்படுத்தும் முன் உங்கள் பகுதி வேளாண் அறிவியல் நிலையம் (KVK) அல்லது வேளாண் விரிவாக்க மையத்தில் ஆலோசிக்கவும்.",
    ],
}

# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


def catalog() -> dict:
    """Everything the web page needs to build its form and voice matching."""
    return {
        "crops": [
            {"value": k, "label": v["label"], "icon": v["icon"],
             "keywords": v["keywords"], "residues": v["residues"]}
            for k, v in CROPS.items()
        ],
        "residues": [
            {"value": k, "label": v["label"], "keywords": v["keywords"]}
            for k, v in RESIDUES.items()
        ],
        "moisture": [
            {"value": k, "label": v["label"], "hint": v["hint"], "icon": v["icon"],
             "keywords": v["keywords"]}
            for k, v in MOISTURE.items()
        ],
        "quality": [
            {"value": k, "label": v["label"], "hint": v["hint"], "icon": v["icon"],
             "keywords": v["keywords"]}
            for k, v in QUALITY.items()
        ],
        "units": [
            {"value": k, "label": v["label"], "keywords": v["keywords"]}
            for k, v in UNITS.items()
        ],
        "districts": TN_DISTRICTS,
    }


def _msg(en: str, ta: str) -> dict:
    return {"en": en, "ta": ta}


def validate_input(payload) -> tuple[dict | None, dict | None]:
    """Validate a submission. Returns (clean_data, None) or (None, error_message)."""
    if not isinstance(payload, dict):
        return None, _msg("Invalid request.", "தவறான கோரிக்கை.")

    crop = payload.get("crop")
    if crop not in CROPS:
        return None, _msg("Please choose a crop.", "பயிரைத் தேர்ந்தெடுக்கவும்.")

    residue = payload.get("residue") or None
    allowed = CROPS[crop]["residues"]
    if residue is None and len(allowed) == 1:
        residue = allowed[0]
    if residue not in RESIDUES:
        return None, _msg("Please choose the residue type.", "கழிவு வகையைத் தேர்ந்தெடுக்கவும்.")
    if residue not in allowed:
        return None, _msg("This residue does not belong to the chosen crop.",
                          "இந்தக் கழிவு தேர்ந்தெடுத்த பயிருக்குரியது அல்ல.")

    unit = payload.get("unit") or "kg"
    if unit not in UNITS:
        return None, _msg("Please choose a valid unit.", "சரியான அலகைத் தேர்ந்தெடுக்கவும்.")
    try:
        quantity = float(payload.get("quantity"))
    except (TypeError, ValueError):
        return None, _msg("Please enter the quantity as a number.", "அளவை எண்ணாக உள்ளிடவும்.")
    if quantity != quantity or quantity <= 0:  # NaN or non-positive
        return None, _msg("Quantity must be greater than zero.", "அளவு பூஜ்யத்தை விட அதிகமாக இருக்க வேண்டும்.")
    quantity_kg = quantity * UNITS[unit]["to_kg"]
    if quantity_kg > MAX_QUANTITY_KG:
        return None, _msg("That quantity looks too large. Please check it.",
                          "அளவு மிக அதிகமாகத் தெரிகிறது. சரிபார்க்கவும்.")

    moisture = payload.get("moisture")
    if moisture not in MOISTURE:
        return None, _msg("Please choose the moisture level.", "ஈரப்பத அளவைத் தேர்ந்தெடுக்கவும்.")
    quality = payload.get("quality")
    if quality not in QUALITY:
        return None, _msg("Please choose the residue quality.", "கழிவின் தரத்தைத் தேர்ந்தெடுக்கவும்.")

    location = payload.get("location") or ""
    if not isinstance(location, str):
        return None, _msg("Invalid location.", "தவறான இடம்.")
    location = "".join(ch for ch in location if ch.isprintable()).strip()
    if len(location) > 100:
        return None, _msg("Location is too long (maximum 100 characters).",
                          "இடத்தின் பெயர் மிக நீளமானது (அதிகபட்சம் 100 எழுத்துகள்).")

    method = payload.get("input_method")
    method = method if method in ("voice", "manual") else "manual"
    language = payload.get("language")
    language = language if language in ("ta", "en") else "ta"

    return {
        "crop": crop, "residue": residue,
        "quantity": quantity, "unit": unit, "quantity_kg": quantity_kg,
        "moisture": moisture, "quality": quality,
        "location": location, "input_method": method, "language": language,
    }, None


def size_class(quantity_kg: float) -> str:
    if quantity_kg < SMALL_LIMIT_KG:
        return "small"
    if quantity_kg <= LARGE_LIMIT_KG:
        return "medium"
    return "large"


def score_option(option_id: str, residue: str, moisture: str, quality: str, size: str) -> int:
    base = BASE_SCORES.get(residue, BASE_SCORES["other"]).get(option_id, 0)
    if base == 0:
        return 0  # not applicable to this residue; adjustments cannot revive it
    mods = MODIFIERS[option_id]
    m = mods["moisture"][moisture]
    if residue in NATURALLY_WET and m < 0:
        m = -((-m) // 2)  # halve the penalty, rounding toward zero
    total = base + m + mods["quality"][quality] + mods["quantity"][size]
    return max(0, min(10, total))


def _level(score: int) -> str:
    if score >= 8:
        return "high"
    if score >= 6:
        return "medium"
    return "fair"


def _notes_for(option_id: str, residue: str, moisture: str, quality: str, size: str) -> dict:
    levels = {"moisture": moisture, "quality": quality, "quantity": size, "residue": residue}
    en, ta = [], []
    for opt, factor, level, text_en, text_ta in NOTES:
        if opt == option_id and levels[factor] == level:
            en.append(text_en)
            ta.append(text_ta)
    return {"en": en, "ta": ta}


def _fmt_number(x: float) -> str:
    return str(int(x)) if float(x).is_integer() else f"{x:g}"


def recommend(clean: dict) -> dict:
    """Apply the rules to validated input and build the bilingual result."""
    residue, moisture, quality = clean["residue"], clean["moisture"], clean["quality"]
    size = size_class(clean["quantity_kg"])

    scored = []
    for idx, option_id in enumerate(OPTION_ORDER):
        scored.append((score_option(option_id, residue, moisture, quality, size), idx, option_id))
    scored.sort(key=lambda s: (-s[0], s[1]))

    chosen = [s for s in scored if s[0] >= 5][:4]
    if len(chosen) < 2:
        chosen = [s for s in scored if s[0] > 0][:2]

    recommendations = []
    for rank, (score, _idx, option_id) in enumerate(chosen, start=1):
        opt = OPTIONS[option_id]
        recommendations.append({
            "id": option_id,
            "rank": rank,
            "score": score,
            "level": _level(score),
            "icon": opt["icon"],
            "title": opt["title"],
            "description": opt["description"],
            "steps": opt["steps"],
            "precautions": opt["precautions"],
            "notes": _notes_for(option_id, residue, moisture, quality, size),
        })

    unit = UNITS[clean["unit"]]["label"]
    qty = _fmt_number(clean["quantity"])
    res_label = RESIDUES[residue]["label"]
    mo = MOISTURE[moisture]["short"]
    qu = QUALITY[quality]["short"]
    unit_en = unit["en"] + ("s" if unit["en"] in ("tonne", "quintal") and clean["quantity"] != 1 else "")
    summary = {
        "en": (f"You have about {qty} {unit_en} of {res_label['en']} "
               f"({mo['en']}, {qu['en']}). These are the best ways to reuse it."),
        "ta": (f"உங்களிடம் சுமார் {qty} {unit['ta']} {res_label['ta']} "
               f"({mo['ta']}, {qu['ta']}) உள்ளது. இதை மீண்டும் பயன்படுத்த சிறந்த வழிகள் இவை."),
    }

    loc = clean["location"]
    if loc:
        location_tip = {
            "en": f"For hands-on help in {loc}, contact your nearest Krishi Vigyan Kendra (KVK) or Block Agricultural Extension Centre.",
            "ta": f"{loc} பகுதியில் நேரடி உதவிக்கு, அருகிலுள்ள வேளாண் அறிவியல் நிலையம் (KVK) அல்லது வட்டார வேளாண்மை விரிவாக்க மையத்தை அணுகவும்.",
        }
    else:
        location_tip = {
            "en": "For hands-on help, contact your nearest Krishi Vigyan Kendra (KVK) or Block Agricultural Extension Centre.",
            "ta": "நேரடி உதவிக்கு, அருகிலுள்ள வேளாண் அறிவியல் நிலையம் (KVK) அல்லது வட்டார வேளாண்மை விரிவாக்க மையத்தை அணுகவும்.",
        }

    return {
        "summary": summary,
        "size_class": size,
        "recommendations": recommendations,
        "general_precautions": GENERAL_PRECAUTIONS,
        "location_tip": location_tip,
    }
