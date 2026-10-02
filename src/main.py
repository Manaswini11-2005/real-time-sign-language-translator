import cv2
import mediapipe as mp
import time

from config import (
    CAMERA_INDEX,
    MIN_DETECTION_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
    MAX_NUM_HANDS,
    LANGUAGES,
    DEFAULT_LANGUAGE,
    SIGN_TRANSLATIONS
)

from detector import GestureDetector
from speech_engine import SpeechEngine
from ui import SignLanguageUI


WINDOW_NAME = "Sign Language Translator | 10 Gestures"


def main():

    print("=" * 60)
    print("       SIGN LANGUAGE TRANSLATOR")
    print("=" * 60)

    print("\nGestures:")

    for i, gesture in enumerate(
        SIGN_TRANSLATIONS.keys(),
        1
    ):
        print(f"{i:2}. {gesture}")

    print("\nLanguages:")

    for key, language in LANGUAGES.items():
        print(f"{key} - {language}")

    print("\nControls:")
    print("1 - English")
    print("2 - Hindi")
    print("3 - Telugu")
    print("4 - Tamil")
    print("5 - Malayalam")
    print("6 - Kannada")
    print("7 - Bengali")
    print("Q - Quit")

    print("\nStarting camera...")
    print("=" * 60)

    # ============================================================
    # CAMERA
    # ============================================================

    camera = cv2.VideoCapture(
        CAMERA_INDEX,
        cv2.CAP_DSHOW
    )

    # Normal webcam resolution
    camera.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        1280
    )

    camera.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        720
    )

    # Default / normal zoom
    try:
        camera.set(
            cv2.CAP_PROP_ZOOM,
            0
        )
    except Exception:
        pass

    # Autofocus
    try:
        camera.set(
            cv2.CAP_PROP_AUTOFOCUS,
            1
        )
    except Exception:
        pass

    # Reduce camera buffering
    camera.set(
        cv2.CAP_PROP_BUFFERSIZE,
        1
    )

    if not camera.isOpened():

        print("ERROR: Could not open camera.")
        return

    # ============================================================
    # MEDIAPIPE
    # ============================================================

    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils

    hands_detector = mp_hands.Hands(

        static_image_mode=False,

        max_num_hands=MAX_NUM_HANDS,

        model_complexity=0,

        min_detection_confidence=
        MIN_DETECTION_CONFIDENCE,

        min_tracking_confidence=
        MIN_TRACKING_CONFIDENCE
    )

    # ============================================================
    # COMPONENTS
    # ============================================================

    detector = GestureDetector()
    speech = SpeechEngine()
    ui = SignLanguageUI()

    selected_language = DEFAULT_LANGUAGE
    current_sign = None

    previous_time = time.time()

    # ============================================================
    # NORMAL WINDOW
    # ============================================================

    cv2.namedWindow(
        WINDOW_NAME,
        cv2.WINDOW_NORMAL
    )

    cv2.resizeWindow(
        WINDOW_NAME,
        1280,
        720
    )

    cv2.moveWindow(
        WINDOW_NAME,
        50,
        30
    )

    # ============================================================
    # MAIN LOOP
    # ============================================================

    try:

        while True:

            success, frame = camera.read()

            if not success:
                continue

            # Mirror camera
            frame = cv2.flip(
                frame,
                1
            )

            # ----------------------------------------------------
            # FPS
            # ----------------------------------------------------

            current_time = time.time()

            fps = 1.0 / max(
                current_time - previous_time,
                0.001
            )

            previous_time = current_time

            # ----------------------------------------------------
            # MEDIAPIPE
            # ----------------------------------------------------

            rgb_frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            rgb_frame.flags.writeable = False

            results = hands_detector.process(
                rgb_frame
            )

            rgb_frame.flags.writeable = True

            # ----------------------------------------------------
            # HANDS
            # ----------------------------------------------------

            detected_hands = []

            if results.multi_hand_landmarks:

                for hand_landmarks in (
                    results.multi_hand_landmarks
                ):

                    detected_hands.append(
                        hand_landmarks.landmark
                    )

                    mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS
                    )

            # ----------------------------------------------------
            # GESTURE
            # ----------------------------------------------------

            detected_sign = detector.detect(
                detected_hands
            )

            if detected_sign:

                if detected_sign != current_sign:

                    current_sign = detected_sign

                    translation = (
                        SIGN_TRANSLATIONS
                        .get(
                            current_sign,
                            {}
                        )
                        .get(
                            selected_language,
                            current_sign
                        )
                    )

                    print(
                        f"Gesture: {current_sign} | "
                        f"{LANGUAGES[selected_language]}: "
                        f"{translation}"
                    )

                    speech.reset()

                    speech.speak(
                        translation,
                        selected_language
                    )

            else:

                current_sign = None
                speech.reset()

            # ----------------------------------------------------
            # UI
            # ----------------------------------------------------

            frame = ui.render(
                frame,
                current_sign,
                selected_language,
                fps
            )

            cv2.imshow(
                WINDOW_NAME,
                frame
            )

            # ----------------------------------------------------
            # KEYS
            # ----------------------------------------------------

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

            elif key == ord("1"):
                selected_language = "en"

            elif key == ord("2"):
                selected_language = "hi"

            elif key == ord("3"):
                selected_language = "te"

            elif key == ord("4"):
                selected_language = "ta"

            elif key == ord("5"):
                selected_language = "ml"

            elif key == ord("6"):
                selected_language = "kn"

            elif key == ord("7"):
                selected_language = "bn"

    finally:

        print("\nStopping translator...")

        camera.release()

        hands_detector.close()

        speech.close()

        cv2.destroyAllWindows()

        print("Translator stopped.")


if __name__ == "__main__":
    main()