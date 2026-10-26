import os
import json
import uuid
import random
import difflib
import re
from pathlib import Path
from sentences import SENTENCE_BANK, INDIAN_LANGUAGES, RESPONSE_LANGUAGES

# Load .env file
env_path = Path(__file__).parent / ".env"
if env_path.is_file():
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip("'\"")
            if val:
                os.environ[key] = val

from sarvamai import SarvamAI

class GameEngine:
    def __init__(self):
        self.api_key = os.environ.get("SARVAM_API_KEY", "")
        self.client = SarvamAI(api_subscription_key=self.api_key) if self.api_key else None
        self.active_rounds = {}  # round_id -> sentence dict

    def start_round(self):
        """Picks a random sentence, generates TTS dictation audio using Sarvam Bulbul."""
        sentence = random.choice(SENTENCE_BANK)
        round_id = str(uuid.uuid4())
        self.active_rounds[round_id] = sentence

        audio_base64 = None
        error_msg = None

        if self.client:
            try:
                lang_info = INDIAN_LANGUAGES.get(sentence["language_code"], {})
                speaker = lang_info.get("speaker", "shreya")

                # Sarvam Text-to-Speech API
                try:
                    response = self.client.text_to_speech.convert(
                        text=sentence["text"],
                        language_code=sentence["language_code"],
                        speaker=speaker,
                        model="bulbul:v3",
                    )
                except Exception:
                    response = self.client.text_to_speech.convert(
                        text=sentence["text"],
                        language_code=sentence["language_code"],
                        speaker="shreya",
                        model="bulbul:v3",
                    )
                if response and response.audios:
                    audio_base64 = response.audios[0]
            except Exception as e:
                err_str = str(e)
                if "402" in err_str or "insufficient_quota_error" in err_str:
                    error_msg = "Sarvam AI: Account has 0 credits. (Add credits in dashboard.sarvam.ai for live neural TTS)."
                else:
                    error_msg = f"Sarvam TTS Note: {err_str[:120]}"

        return {
            "round_id": round_id,
            "has_audio": audio_base64 is not None,
            "audio_base64": audio_base64,
            "error_msg": error_msg,
            # We also send hint audio text in fallback mode so the player can still hear it via browser TTS
            "fallback_text": sentence["text"] if not audio_base64 else None,
            "fallback_lang": sentence["language_code"] if not audio_base64 else None,
            "languages": [
                {"code": code, "name": info["name"], "native": info["native"]}
                for code, info in sorted(INDIAN_LANGUAGES.items(), key=lambda x: x[1]["name"])
            ],
            "response_languages": [
                {"code": code, "name": info["name"], "native": info["native"]}
                for code, info in RESPONSE_LANGUAGES.items()
            ],
        }

    def transcribe_dictation(self, audio_bytes, mime_type="audio/webm", language_code="en-IN"):
        """Transcribes the user's spoken answer using Sarvam Saaras Speech-to-Text in their chosen response language."""
        if not self.client:
            return {"error": "Sarvam API key is not configured."}

        try:
            # Convert or pass audio to Sarvam STT
            file_tuple = ("recording.webm", audio_bytes, mime_type)
            # Pass language_code if it's supported by Sarvam STT
            stt_lang = language_code if language_code in INDIAN_LANGUAGES or language_code == "en-IN" else "en-IN"
            response = self.client.speech_to_text.transcribe(
                file=file_tuple,
                model="saaras:v3",
                language_code=stt_lang,
            )
            transcript = getattr(response, "transcript", "") or ""
            return {"transcript": transcript.strip()}
        except Exception as e:
            err_str = str(e)
            if "402" in err_str or "insufficient_quota" in err_str:
                return {
                    "error": "Sarvam STT: No credits available on account. Please use microphone dictation with browser speech recognition or type your answer.",
                    "is_quota_error": True,
                }
            return {"error": f"STT failed: {err_str[:140]}"}

    def evaluate(self, round_id, guessed_lang_code, guessed_meaning, response_lang_code="en-IN"):
        """Scores user's answer: 20 pts for language + 80 pts for sentence meaning in their chosen response language."""
        sentence = self.active_rounds.get(round_id)
        if not sentence:
            return {"error": "Invalid or expired round. Please start a new round."}

        # 1. Score Language Guess (20 points)
        correct_lang = sentence["language_code"]
        lang_correct = (guessed_lang_code == correct_lang)
        lang_score = 20 if lang_correct else 0

        # 2. Score Translation / Meaning Closeness (80 points)
        meaning_score, feedback, engine_used = self._score_meaning(
            guessed_meaning=guessed_meaning,
            original_text=sentence["text"],
            roman_text=sentence.get("roman", ""),
            true_meaning=sentence["meaning"],
            keywords=sentence.get("keywords", []),
            target_lang_code=correct_lang,
            target_lang_name=INDIAN_LANGUAGES.get(correct_lang, {}).get("name", "Indian Language"),
            response_lang_code=response_lang_code,
        )

        total_score = lang_score + meaning_score

        return {
            "round_id": round_id,
            "total_score": total_score,
            "max_score": 100,
            "breakdown": {
                "language_score": lang_score,
                "language_max": 20,
                "language_correct": lang_correct,
                "meaning_score": meaning_score,
                "meaning_max": 80,
                "response_language": RESPONSE_LANGUAGES.get(response_lang_code, {}).get("name", "English"),
            },
            "ground_truth": {
                "language_code": correct_lang,
                "language_name": INDIAN_LANGUAGES.get(correct_lang, {}).get("name", "Unknown"),
                "language_native": INDIAN_LANGUAGES.get(correct_lang, {}).get("native", ""),
                "movie": sentence.get("movie", "Iconic Film"),
                "character": sentence.get("character", ""),
                "original_text": sentence["text"],
                "roman": sentence.get("roman", ""),
                "true_meaning": sentence["meaning"],
            },
            "feedback": feedback,
            "engine": engine_used,
        }

    def _score_meaning(self, guessed_meaning, original_text, roman_text, true_meaning, keywords, target_lang_code, target_lang_name, response_lang_code):
        """Evaluates how close the guess in response_lang is to the actual meaning out of 80."""
        cleaned_guess = (guessed_meaning or "").strip()
        if not cleaned_guess:
            return 0, "No meaning guessed.", "Rules Engine"

        resp_lang_name = RESPONSE_LANGUAGES.get(response_lang_code, {}).get("name", "English")

        # Attempt to use Sarvam LLM for semantic grading if available
        if self.client:
            try:
                prompt = (
                    f"You are an expert multilingual evaluator in an Indian language listening and translation game.\n"
                    f"Target Language: {target_lang_name}\n"
                    f"Original Sentence spoken: \"{original_text}\"\n"
                    f"Romanized Pronunciation: \"{roman_text}\"\n"
                    f"Official English Meaning: \"{true_meaning}\"\n"
                    f"Player's Chosen Response Language: {resp_lang_name}\n"
                    f"Player's Guessed Translation (in {resp_lang_name}): \"{cleaned_guess}\"\n\n"
                    f"Rate how accurately the player's guess in {resp_lang_name} captures the meaning of the original {target_lang_name} sentence on a scale of 0 to 80 points:\n"
                    f"- 70-80: Perfect or nearly exact translation / essence captured in {resp_lang_name}.\n"
                    f"- 50-69: Captured main idea, key actions, and major concepts in {resp_lang_name}.\n"
                    f"- 30-49: Partial understanding; caught some concepts or context.\n"
                    f"- 10-29: Barely relevant; got one or two isolated words.\n"
                    f"- 0: Completely incorrect, unrelated, or gibberish.\n\n"
                    f"Output strictly a JSON object with keys 'score' (integer 0-80) and 'feedback' (1-2 encouraging sentences noting their {resp_lang_name} response)."
                )
                resp = self.client.chat.completions(
                    model="sarvam-105b-conversations",
                    messages=[{"role": "user", "content": prompt}],
                )
                content = resp.choices[0].message.content
                # Extract json
                match = re.search(r"\{.*\}", content, re.DOTALL)
                if match:
                    data = json.loads(match.group(0))
                    score = max(0, min(80, int(data.get("score", 0))))
                    feedback = data.get("feedback", f"Evaluated by Sarvam 105B in {resp_lang_name}.")
                    return score, feedback, "Sarvam AI (sarvam-105b-conversations)"
            except Exception:
                pass  # Fall through to deterministic local semantic matcher

        # If user responded in the target language itself:
        if response_lang_code == target_lang_code:
            sim_native = difflib.SequenceMatcher(None, cleaned_guess, original_text).ratio()
            sim_roman = difflib.SequenceMatcher(None, cleaned_guess.lower(), roman_text.lower()).ratio()
            best_sim = max(sim_native, sim_roman)
            if best_sim >= 0.85:
                return 80, f"Incredible! You repeated and transcribed the sentence in {target_lang_name} almost perfectly!", "Indic Semantic Engine"
            pts = int(round(best_sim * 80))
            return max(0, min(80, pts)), f"Matched against native {target_lang_name} sentence with {round(best_sim*100)}% similarity.", "Indic Semantic Engine"

        # Attempt to translate guess to English if non-English using Sarvam translation
        effective_guess = cleaned_guess
        if response_lang_code != "en-IN" and self.client:
            try:
                trans_resp = self.client.text.translate(
                    input=cleaned_guess,
                    source_language_code=response_lang_code,
                    target_language_code="en-IN",
                    model="mayura:v1",
                )
                if trans_resp and getattr(trans_resp, "translated_text", None):
                    effective_guess = trans_resp.translated_text
            except Exception:
                pass

        # Smart Local Semantic Matcher (Fallback when 402 quota or offline)
        score, feedback = self._local_semantic_match(effective_guess, true_meaning, keywords)
        return score, feedback, f"Indic Semantic Engine ({resp_lang_name})"

    def _local_semantic_match(self, guess, truth, keywords):
        guess_lower = guess.lower().strip()
        truth_lower = truth.lower().strip()

        # Exact or near-exact match
        sim_ratio = difflib.SequenceMatcher(None, guess_lower, truth_lower).ratio()
        if sim_ratio >= 0.90:
            return 80, "Exceptional translation! You captured the full meaning and key details effortlessly."

        # Token overlap
        guess_tokens = set(re.findall(r"\w+", guess_lower))
        truth_tokens = set(re.findall(r"\w+", truth_lower))
        stopwords = {"a", "an", "the", "in", "on", "at", "for", "to", "of", "and", "is", "was", "are", "were", "it", "this", "that", "all", "our", "us", "we", "be", "have", "has", "had", "will"}
        meaningful_truth = truth_tokens - stopwords
        meaningful_guess = guess_tokens - stopwords
        overlap = len(meaningful_guess & meaningful_truth) / max(1, len(meaningful_truth))

        # Keyword matching
        kw_hits = 0
        for kw in keywords:
            kw_l = kw.lower()
            if kw_l in guess_lower:
                kw_hits += 1
            else:
                words = [w for w in kw_l.split() if w not in stopwords]
                if any(w in guess_tokens for w in words):
                    kw_hits += 0.7
        kw_ratio = (kw_hits / max(1, len(keywords))) if keywords else 0

        # Composite score
        composite = (sim_ratio * 0.40) + (overlap * 0.35) + (kw_ratio * 0.25)
        total_meaning_score = int(round(composite * 80))
        total_meaning_score = max(0, min(80, total_meaning_score))

        if total_meaning_score >= 65:
            feedback = "Brilliant translation! You captured the core meaning and key details effortlessly."
        elif total_meaning_score >= 40:
            feedback = "Great effort! You caught the central theme and several key ideas."
        elif total_meaning_score >= 15:
            feedback = "You picked up a few words, but missed the main action or context."
        else:
            feedback = "The meaning was quite different from the actual sentence, but great attempt!"

        return total_meaning_score, feedback
