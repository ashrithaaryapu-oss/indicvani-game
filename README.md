# 🌌 IndicVani — The Indic Cinema Listening & Translation Game
> **An interactive audio guessing game featuring iconic movie dialogues across 10 Indian languages, powered by Sarvam AI.**

![IndicVani](https://img.shields.io/badge/Powered%20By-Sarvam%20AI-7c3aed?style=for-the-badge)
![Languages](https://img.shields.io/badge/Languages-10%20Indic%20Languages-38bdf8?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-emerald?style=for-the-badge)

---

## 🎮 Game Concept

**IndicVani** tests your ear for Indian cinema and languages:

1. **🔊 Listen to the Line**: The game plays a legendary dialogue spoken in one of 10 Indian languages using Sarvam AI's **Bulbul:v3** neural Text-to-Speech.
2. **🌐 Guess the Spoken Language (20 pts)**: Choose which Indian language was spoken from 10 regional cinemas.
3. **🗣️ Choose Response Language & Dictate (80 pts)**: Select your response language (English, Hindi, Tamil, Telugu, etc.), click the mic button, and dictate what you understood the sentence to mean. Sarvam's **Saaras:v3** Speech-to-Text transcribes your spoken voice.
4. **🏆 Semantic Scoring & Movie Reveal**: Sarvam's Indic reasoning LLM evaluates how close your translation is to the dialogue's true meaning (out of 80), displays your total score out of 100, and reveals the movie title, year, and character!

---

## 🎬 Equal Representation Across 10 Regional Cinemas

The game features exactly 3 iconic dialogues per language (30 iconic lines total) with zero discrimination:

* **Hindi (Bollywood)**: *Anand*, *Sholay*, *Mr. India*
* **Tamil (Kollywood)**: *Baashha*, *Nayakan*, *Kabali*
* **Telugu (Tollywood)**: *Pokiri*, *Baahubali 2*, *Pushpa: The Rise*
* **Bengali (Bangla Cinema)**: *Hirak Rajar Deshe*, *Chirodini Tumi Je Amar*, *Agantuk*
* **Malayalam (Mollywood)**: *Sandesham*, *Commissioner*, *Spadikam*
* **Kannada (Sandalwood)**: *Nagarahavu*, *K.G.F: Chapter 2*, *Kantara*
* **Marathi (Marathi Cinema)**: *Shantata! Court Chalu Aahe*, *Sairat*, *Pawankhind*
* **Gujarati (Dhollywood)**: *Hellaro*, *Chal Man Jeetva Jaiye*, *Chhello Show*
* **Punjabi (Pollywood)**: *Carry On Jatta*, *Jatt Jeona Morh*, *Angrej*
* **Odia (Ollywood)**: *Bhakta Salabega*, *I Love You*, *Daman*

---

## 🛠️ Tech Stack & Sarvam AI Integration

* **Text-to-Speech (TTS)**: `bulbul:v3` for expressive neural Indic voice synthesis with region-native speaker personas (`shreya`, `vijay`, `kavitha`, `roopa`, `ishita`, `pooja`, `aditya`, `priya`, `anand`, `shubh`).
* **Speech-to-Text (STT)**: `saaras:v3` for live audio transcription of the player's microphone dictation in their chosen response language.
* **Semantic Evaluation & Reasoning**: `sarvam-105b-conversations` for multilingual semantic closeness scoring (with a local fallback engine).
* **Backend**: Pure Python HTTP server (zero external web frameworks, lightweight and fast).
* **Frontend**: Space-themed dark celestial UI (deep midnight blues, interstellar violet, glassmorphism, animated sound waves, and slowly drifting cosmic constellation side art).

---

## 🚀 Quickstart

### 1. Clone the repository
```bash
git clone https://github.com/your-username/indicvani-sarvam-game.git
cd indicvani-sarvam-game
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Key
Create a `.env` file in the project root:
```env
SARVAM_API_KEY=your_sarvam_api_key_here
```
*(Get your key from [dashboard.sarvam.ai](https://dashboard.sarvam.ai/))*

### 4. Run the Game
```bash
python server.py
```
Open your browser to:
```
http://localhost:8080/
```

---

## 📁 Repository Structure
```
├── server.py          # Python HTTP server + space-themed single-page frontend
├── game_engine.py     # Game mechanics, Sarvam API client & semantic grading
├── sentences.py       # Curated bank of 30 iconic dialogues across 10 Indian languages
├── main.py            # Minimal starter script for Sarvam AI chat completion
├── requirements.txt   # Project dependencies (sarvamai)
├── .gitignore         # Ignores secret .env and cache files
└── README.md          # Project documentation
```

---

## 📜 License
MIT License. Crafted with ❤️ for Indic languages.
