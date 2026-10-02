# --------------------------------------------------
# Multilingual TTS
# Uses gTTS + pygame in a background worker.
# --------------------------------------------------

import os
import time
import tempfile
import threading
import queue
from gtts import gTTS
import pygame


class SpeechEngine:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.queue = queue.Queue(maxsize=3)
        self.last_item = None
        self.running = True

        pygame.mixer.init()
        self.worker = threading.Thread(target=self._worker, daemon=True)
        self.worker.start()

    def speak(self, text: str, lang_code: str = "en"):
        if not text:
            return

        item = (text, lang_code)
        if item == self.last_item:
            return

        self.last_item = item
        try:
            self.queue.put_nowait(item)
        except queue.Full:
            try:
                self.queue.get_nowait()
                self.queue.task_done()
            except queue.Empty:
                pass
            try:
                self.queue.put_nowait(item)
            except queue.Full:
                pass

    def _worker(self):
        while self.running:
            try:
                text, lang_code = self.queue.get(timeout=0.2)
            except queue.Empty:
                continue

            temp_file = None
            try:
                fd, temp_file = tempfile.mkstemp(
                    prefix="sign_tts_", suffix=".mp3"
                )
                os.close(fd)

                gTTS(text=text, lang=lang_code, slow=False).save(temp_file)
                pygame.mixer.music.load(temp_file)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy() and self.running:
                    time.sleep(0.05)

                try:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.unload()
                except Exception:
                    pass

            except Exception as e:
                print(f"Speech Error: {e}")

            finally:
                if temp_file and os.path.exists(temp_file):
                    for _ in range(8):
                        try:
                            os.remove(temp_file)
                            break
                        except PermissionError:
                            time.sleep(0.1)
                        except OSError:
                            break
                self.queue.task_done()

    def reset(self):
        self.last_item = None

    def close(self):
        self.running = False
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            pygame.mixer.quit()
        except Exception:
            pass
