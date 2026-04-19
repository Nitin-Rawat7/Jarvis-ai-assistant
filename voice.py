import speech_recognition as sr
import pyttsx3
import threading
import queue
import time
import logging
import os

# ─────────────────────────────────────────────────────────────
# 📋 LOGGER
# ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("Jarvis.Voice")


# ─────────────────────────────────────────────────────────────
# ⚙️  CONFIG  — Change values here to tune Jarvis
# ─────────────────────────────────────────────────────────────
class Cfg:
    # ── Mic ───────────────────────────────────────────────────
    MIC_INDEX               = None      # None = auto; set 0,1,2… to pin a mic

    # ── Energy / Sensitivity ──────────────────────────────────
    ENERGY_THRESHOLD        = 400       # Lower = more sensitive; Raise if noisy room
    DYNAMIC_ENERGY          = True      # Auto-adjusts threshold during session
    DYNAMIC_ENERGY_RATIO    = 1.2

    # ── Sentence Capture (MOST IMPORTANT) ─────────────────────
    PAUSE_THRESHOLD         = 1.5       # Seconds of silence = sentence finished
                                        # Raise to 3.5 if still cutting off early
    NON_SPEAKING_DURATION   = 1.0       # Silence before VAD resets
    PHRASE_TIME_LIMIT       = 25        # Max seconds per command (hard cap)
    LISTEN_TIMEOUT          = 5        # Seconds to wait for you to START speaking

    # ── Calibration ───────────────────────────────────────────
    CALIBRATION_DURATION    = 0.1         # Seconds to sample room noise at startup
    RECALIBRATE_EVERY       = 300       # Re-calibrate every 5 min (0 = never)

    # ── Recognition ───────────────────────────────────────────
    LANGUAGE                = "en-IN"   # en-US | en-IN | hi-IN etc.
    MAX_RETRIES             = 2         # Google retry attempts before Whisper kicks in
    RETRY_DELAY             = 0.4       # Seconds between retries

    # ── Whisper (offline fallback) ────────────────────────────
    USE_WHISPER_FALLBACK    = True      # ✅ ENABLED
    WHISPER_MODEL           = "small"   # tiny | base | small | medium
                                        # small = best for Indian English accent

    # ── TTS ───────────────────────────────────────────────────
    TTS_RATE                = 150       # Slightly slower — sounds better for Zira
    TTS_VOLUME              = 1.0

    # ✅ ZIRA VOICE — set by direct registry ID (100% reliable)
    # To switch back to David replace ZIRA → DAVID below
    VOICE_ID = (
        "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech"
        "\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0"
    )


# ─────────────────────────────────────────────────────────────
# 🎤  MICROPHONE HELPERS
# ─────────────────────────────────────────────────────────────
def list_microphones():
    """Call this to see all available mics and their index numbers."""
    mics = sr.Microphone.list_microphone_names()
    print("\n📋 Available microphones:")
    for i, name in enumerate(mics):
        print(f"  [{i}] {name}")
    print(f"\n  Tip: Set Cfg.MIC_INDEX = <number> to pin a specific mic\n")


def _get_mic() -> sr.Microphone:
    if Cfg.MIC_INDEX is not None:
        log.info(f"🎤 Using mic [{Cfg.MIC_INDEX}]")
        return sr.Microphone(device_index=Cfg.MIC_INDEX)
    return sr.Microphone()


# ─────────────────────────────────────────────────────────────
# 🧠  CALIBRATION MANAGER
#     Calibrates ONCE at startup — not on every listen() call
# ─────────────────────────────────────────────────────────────
class CalibrationManager:
    def __init__(self):
        self._recognizer      = self._build_recognizer()
        self._last_calibrated = 0.0
        self._calibrated      = False
        self._lock            = threading.Lock()

    def _build_recognizer(self) -> sr.Recognizer:
        r = sr.Recognizer()
        r.energy_threshold         = Cfg.ENERGY_THRESHOLD
        r.dynamic_energy_threshold = Cfg.DYNAMIC_ENERGY
        r.dynamic_energy_ratio     = Cfg.DYNAMIC_ENERGY_RATIO
        r.pause_threshold          = Cfg.PAUSE_THRESHOLD
        r.non_speaking_duration    = Cfg.NON_SPEAKING_DURATION
        r.operation_timeout        = None
        return r

    def calibrate(self, force: bool = False):
        now   = time.time()
        needs = (
            force
            or not self._calibrated
            or (Cfg.RECALIBRATE_EVERY > 0
                and (now - self._last_calibrated) > Cfg.RECALIBRATE_EVERY)
        )
        if not needs:
            return

        with self._lock:
            try:
                with _get_mic() as source:
                    log.info(f"🎙  Calibrating mic for {Cfg.CALIBRATION_DURATION}s "
                             f"— please stay quiet...")
                    self._recognizer.adjust_for_ambient_noise(
                        source, duration=Cfg.CALIBRATION_DURATION
                    )
                    self._last_calibrated = time.time()
                    self._calibrated      = True
                    log.info(f"✅ Calibration done. "
                             f"Energy threshold → {self._recognizer.energy_threshold:.1f}")
            except Exception as e:
                log.warning(f"Calibration failed: {e} — using default threshold")

    @property
    def recognizer(self) -> sr.Recognizer:
        return self._recognizer


_cal = CalibrationManager()


# ─────────────────────────────────────────────────────────────
# 🤫  WHISPER ENGINE  (offline, no internet needed)
# ─────────────────────────────────────────────────────────────
_whisper_model = None
_whisper_lock  = threading.Lock()


def _load_whisper():
    global _whisper_model
    with _whisper_lock:
        if _whisper_model is None:
            try:
                import whisper
                log.info(f"🔄 Loading Whisper '{Cfg.WHISPER_MODEL}' model...")
                _whisper_model = whisper.load_model(Cfg.WHISPER_MODEL)
                log.info("✅ Whisper model ready")
            except ImportError:
                log.error("❌ Whisper not installed! Run: pip install openai-whisper")
    return _whisper_model


def _recognize_whisper(audio: sr.AudioData) -> str:
    model = _load_whisper()
    if model is None:
        return ""

    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        tmp_path = f.name
        f.write(audio.get_wav_data())

    try:
        log.info("🤫 Whisper transcribing...")
        result = model.transcribe(
            tmp_path,
            language="en",
            fp16=False,
            condition_on_previous_text=False,
        )
        text = result.get("text", "").strip()
        log.info(f"✅ Whisper heard: '{text}'")
        return text
    except Exception as e:
        log.error(f"Whisper transcription error: {e}")
        return ""
    finally:
        os.unlink(tmp_path)


# ─────────────────────────────────────────────────────────────
# 🔤  TEXT CLEANER
# ─────────────────────────────────────────────────────────────
_REPLACEMENTS = {
    "vs code"       : "vscode",
    "open chrome"   : "open google chrome",
    "youtube"       : "YouTube",
    "jarvis"        : "Jarvis",
    "okay jarvis"   : "okay Jarvis",
    "hey jarvis"    : "hey Jarvis",
}

def clean_text(text: str) -> str:
    t = text.strip().lower()
    for src, dst in _REPLACEMENTS.items():
        t = t.replace(src, dst)
    return t


# ─────────────────────────────────────────────────────────────
# 🔊  TTS ENGINE — PERMANENT FIX
# ─────────────────────────────────────────────────────────────
# ROOT CAUSE OF THE BUG:
#   pyttsx3 on Windows uses SAPI5 via COM. After the first
#   runAndWait() call, the engine's internal event loop can
#   silently corrupt — subsequent say() calls do nothing.
#   No exception is raised, so it fails invisibly.
#
# THE FIX:
#   Create a BRAND NEW engine for every single speak call.
#   This is the only 100% reliable approach for pyttsx3 + SAPI5.
#   The overhead is ~50ms per call — completely unnoticeable.
#
# ─────────────────────────────────────────────────────────────
class TTSEngine:
    def __init__(self):
        self._queue  = queue.Queue()
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def _speak_once(self, text: str):
        """
        Create a fresh engine, speak the text, destroy it.
        Called inside the worker thread — never reuses an engine.
        This is the fix for pyttsx3 going silent after first response.
        """
        engine = None
        try:
            # COM must be initialized per-thread on Windows
            try:
                import pythoncom
                pythoncom.CoInitialize()
            except ImportError:
                pass

            engine = pyttsx3.init()
            engine.setProperty("rate",   Cfg.TTS_RATE)
            engine.setProperty("volume", Cfg.TTS_VOLUME)

            # Set Zira voice by direct registry ID
            try:
                engine.setProperty("voice", Cfg.VOICE_ID)
            except Exception as ve:
                log.warning(f"Voice ID set failed: {ve}")

            engine.say(text)
            engine.runAndWait()

        except Exception as e:
            log.error(f"🔊 TTS error: {e}")

        finally:
            # Always clean up — prevents engine state leaking
            try:
                if engine:
                    engine.stop()
            except Exception:
                pass
            try:
                import pythoncom
                pythoncom.CoUninitialize()
            except Exception:
                pass

    def _worker(self):
        """
        Worker thread — pulls text from queue, speaks it freshly each time.
        Runs forever as a daemon thread.
        """
        while True:
            text = self._queue.get()
            if text is None:
                break
            try:
                self._speak_once(text)
            finally:
                self._queue.task_done()

    def speak(self, text: str):
        """Queue text for speech. Flushes stale items so only latest speaks."""
        if not text or not text.strip():
            return

        # Drop any queued but unspoken items (prevents pile-up)
        flushed = 0
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
                self._queue.task_done()
                flushed += 1
            except queue.Empty:
                break
        if flushed:
            log.debug(f"Flushed {flushed} stale TTS item(s)")

        self._queue.put(text)
        log.info(f"🔊 {text[:90]}{'…' if len(text) > 90 else ''}")

    def shutdown(self):
        self._queue.put(None)
        self._thread.join(timeout=3)
        log.info("TTS engine shut down.")


# ─────────────────────────────────────────────────────────────
# 🎤  LISTEN  — Full sentence capture
# ─────────────────────────────────────────────────────────────
def listen(
    timeout: int | None      = None,
    phrase_limit: int | None = None,
    retries: int | None      = None,
    prompt: bool             = True,
) -> str:
    """
    Listen for a full voice command and return transcribed text.

    Flow:
      1. Calibrate mic (only on first call / every 5 min)
      2. Capture audio until silence > PAUSE_THRESHOLD
      3. Try Google Speech Recognition (with retries)
      4. If Google fails → try Whisper offline
      5. Return clean text or "" on total failure
    """
    timeout      = timeout      if timeout      is not None else Cfg.LISTEN_TIMEOUT
    phrase_limit = phrase_limit if phrase_limit is not None else Cfg.PHRASE_TIME_LIMIT
    retries      = retries      if retries      is not None else Cfg.MAX_RETRIES

    _cal.calibrate()
    recognizer = _cal.recognizer

    audio = None
    try:
        with _get_mic() as source:
            if prompt:
                log.info(f"🎤 Listening...  "
                         f"(stops after {Cfg.PAUSE_THRESHOLD}s silence, "
                         f"max {phrase_limit}s)")
            try:
                audio = recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_limit,
                )
                log.info("🔄 Audio captured — recognizing...")
            except sr.WaitTimeoutError:
                log.warning("⏱  No speech detected — timed out waiting")
                return ""

    except OSError as e:
        log.error(f"🎤 Microphone error: {e}")
        return ""
    except Exception as e:
        log.exception(f"Mic unexpected error: {e}")
        return ""

    for attempt in range(1, retries + 2):
        try:
            log.debug(f"   Google attempt {attempt}/{retries + 1}")

            result = recognizer.recognize_google(
                audio,
                language=Cfg.LANGUAGE,
                show_all=True,
            )

            if not result:
                raise sr.UnknownValueError()

            alternatives = result.get("alternative", [])
            if not alternatives:
                raise sr.UnknownValueError()

            if len(alternatives) > 1:
                log.debug(f"   Options: {[a['transcript'] for a in alternatives]}")

            text = clean_text(alternatives[0]["transcript"])
            log.info(f"✅ Google heard: '{text}'")
            return text

        except sr.UnknownValueError:
            log.warning(f"❓ Google attempt {attempt}: Could not understand")

            if attempt == retries + 1:
                if Cfg.USE_WHISPER_FALLBACK:
                    text = _recognize_whisper(audio)
                    if text:
                        return clean_text(text)
                log.error("❌ All recognition attempts failed")
                return ""

            time.sleep(Cfg.RETRY_DELAY)

        except sr.RequestError as e:
            log.error(f"🌐 Google API unavailable: {e}")
            if Cfg.USE_WHISPER_FALLBACK:
                log.info("🤫 No internet — switching to Whisper offline")
                text = _recognize_whisper(audio)
                if text:
                    return clean_text(text)
            return ""

    return ""


# ─────────────────────────────────────────────────────────────
# 🌍  MODULE-LEVEL API
# ─────────────────────────────────────────────────────────────
_tts = TTSEngine()


def speak(text: str):
    """Speak text asynchronously. Safe to call from any thread."""
    _tts.speak(text)


def shutdown():
    """Call this when Jarvis exits to cleanly stop the TTS thread."""
    _tts.shutdown()
    log.info("Jarvis voice engine shut down.")


# ─────────────────────────────────────────────────────────────
# 🧪  SELF-TEST
#     python voice.py
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "═" * 55)
    print("   JARVIS VOICE ENGINE v3 — Permanent TTS Fix")
    print("═" * 55)

    list_microphones()
    _cal.calibrate(force=True)

    if Cfg.USE_WHISPER_FALLBACK:
        _load_whisper()

    # Test: speak 3 times in a row to confirm the fix works
    speak("Jarvis is online. Testing response one.")
    time.sleep(3)
    speak("Response two. TTS still working.")
    time.sleep(3)
    speak("Response three. Fix confirmed, sir.")

    print("\n  If you heard all 3 responses — TTS fix is working!")
    print("  Say 'exit' to quit.\n")

    while True:
        command = listen()
        if command:
            print(f"\n  📝 Command: '{command}'\n")
            speak(f"You said: {command}")
            if any(w in command for w in ["exit", "shutdown", "stop"]):
                speak("Shutting down. Goodbye sir.")
                shutdown()
                break
        else:
            speak("I didn't catch that. Please try again sir.")