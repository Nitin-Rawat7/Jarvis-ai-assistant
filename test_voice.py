import traceback
try:
    import pyttsx3
    import pythoncom    
except Exception as e:
    print("Import error:", str(e))

def test_tts():
    try:
        print("Testing TTS INIT")
        try:
            # Need CoInitialize if comtypes is used in a background thread or sometimes even main thread
            pythoncom.CoInitialize()
        except:
            pass
        engine = pyttsx3.init()
        engine.say('test')
        engine.runAndWait()
        print("TTS SUCCESS")
    except Exception as e:
        print("TTS ERROR:", str(e))
        traceback.print_exc()

import threading
t = threading.Thread(target=test_tts)
t.start()
t.join()
