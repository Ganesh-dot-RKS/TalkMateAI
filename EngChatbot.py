
import re
import time
from typing import Tuple, List, Optional

# Voice input
import speech_recognition as sr

# Text-to-speech output
import pyttsx3

# Grammar checking (offline)
import language_tool_python

# NLP for synonyms
from textblob import TextBlob


class SpokenEnglishChatbot:
    """
    A voice‑interactive chatbot to help users practice spoken English.
    """

    def __init__(self):
        # ---------- Text-to-Speech Engine (offline) ----------
        print("Initializing TTS engine...")
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)   # words per minute
        self.tts_engine.setProperty('volume', 0.9) # 0.0 to 1.0

        # ---------- Speech Recognizer (uses Google API by default) ----------
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        # Adjust for ambient noise once
        with self.microphone as source:
            print("Adjusting for ambient noise... please wait")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

        # ---------- Grammar Checker (offline LanguageTool) ----------
        print("Loading grammar checker (first time downloads model)...")
        self.grammar_tool = language_tool_python.LanguageTool('en-US')

        # Conversation memory
        self.conversation_history = []

    def speak(self, text: str) -> None:
        """Convert text to speech and print it."""
        print(f"Bot: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def listen(self) -> Optional[str]:
        """
        Capture microphone input and convert to text.
        Returns: transcribed text or None on failure.
        """
        with self.microphone as source:
            print("\n🎤 Listening... (speak now)")
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                print("Processing speech...")
                # Using Google Web Speech API (requires internet)
                text = self.recognizer.recognize_google(audio)
                print(f"You said: {text}")
                return text
            except sr.WaitTimeoutError:
                print("No speech detected. Please try again.")
                return None
            except sr.UnknownValueError:
                print("Sorry, I could not understand that.")
                return None
            except sr.RequestError as e:
                print(f"Speech recognition service error: {e}")
                self.speak("I'm having trouble with speech recognition. Please check your internet connection.")
                return None

    def check_grammar(self, text: str) -> Tuple[str, List[str]]:
        """
        Check grammar and return corrected version + list of error messages.
        """
        matches = self.grammar_tool.check(text)
        corrected = language_tool_python.utils.correct(text, matches)
        errors = [match.message for match in matches]
        return corrected, errors

    def suggest_synonyms(self, word: str) -> List[str]:
        """
        Return a list of synonyms for a given word (max 3).
        """
        blob = TextBlob(word)
        # Get first synset for the word
        synsets = blob.words[0].synsets if blob.words else []
        if synsets:
            lemmas = [lemma.name() for syn in synsets[:2] for lemma in syn.lemmas()]
            # Remove duplicates and original word
            unique = list(set(lemmas))
            if word.lower() in unique:
                unique.remove(word.lower())
            return unique[:3]
        return []

    def generate_response(self, user_input: str) -> str:
        """
        Generate a simple conversational reply.
        """
        lower_input = user_input.lower().strip()

        # Exit condition
        if re.search(r'\b(bye|goodbye|exit|quit)\b', lower_input):
            return "Goodbye! Keep practicing your English every day."

        # Greetings
        if re.search(r'\b(hi|hello|hey)\b', lower_input):
            return "Hello! Let's practice English. Tell me something about your day."

        # How are you
        if re.search(r'how are you', lower_input):
            return "I'm doing well, thank you! How about you? Can you describe your mood in one sentence?"

        # Name
        if re.search(r'my name is|i am|i\'m', lower_input):
            name_match = re.search(r'(?:my name is|i am|i\'m) (\w+)', lower_input)
            if name_match:
                name = name_match.group(1)
                return f"Nice to meet you, {name}! What would you like to talk about today?"
            else:
                return "What's your name? I'd like to know you better."

        # Hobbies / likes
        if re.search(r'\b(like|love|enjoy|hobby|play|read|watch)\b', lower_input):
            return "That's interesting! Why do you enjoy that? Try to explain using full sentences."

        # Default – encourage elaboration
        return "Can you tell me more? Try to use a new adjective or adverb."

    def run(self) -> None:
        """
        Main interaction loop (voice in, voice out).
        """
        self.speak("Hello! I am your spoken English learning assistant. I will listen and help you improve.")
        self.speak("You can speak freely. Say 'goodbye' to stop.")

        while True:
            user_text = self.listen()
            if not user_text:
                continue

            # ---- Exit condition ----
            if re.search(r'\b(bye|goodbye|exit|quit)\b', user_text.lower()):
                self.speak("Thanks for practicing! See you next time.")
                break

            # ---- Grammar feedback ----
            corrected, errors = self.check_grammar(user_text)
            if errors:
                self.speak("I found some grammar points to improve.")
                for err in errors[:2]:  # limit to 2 per utterance
                    self.speak(err)
                self.speak(f"You could say: {corrected}")
            else:
                self.speak("Great grammar! That sentence was correct.")

            # ---- Vocabulary tip (optional) ----
            words = re.findall(r'\b[a-z]{4,}\b', user_text.lower())
            for word in words:
                syns = self.suggest_synonyms(word)
                if syns:
                    tip = f"Vocabulary tip: Instead of '{word}', you could use {', '.join(syns)}."
                    print(f"💡 {tip}")
                    self.speak(tip)
                    break  # only one tip per user turn

            # ---- Conversational reply ----
            reply = self.generate_response(user_text)
            self.speak(reply)

            # Store history
            self.conversation_history.append((user_text, reply))

        # Cleanup
        self.grammar_tool.close()


if __name__ == "__main__":
    chatbot = SpokenEnglishChatbot()
    try:
        chatbot.run()
    except KeyboardInterrupt:
        print("\nChatbot stopped by user.")
    finally:
        chatbot.speak("Shutting down. Keep practicing!")