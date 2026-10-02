import os
import cv2
import numpy as np

from PIL import Image, ImageDraw, ImageFont

from config import (
    LANGUAGES,
    SIGN_TRANSLATIONS
)


class SignLanguageUI:

    def __init__(self):

        # ========================================================
        # LAYOUT
        # ========================================================

        self.panel_width = 360
        self.margin = 14

        # ========================================================
        # COLORS - OpenCV uses BGR
        # ========================================================

        self.background = (16, 15, 19)
        self.card = (43, 39, 43)

        self.white = (245, 245, 245)
        self.gray = (180, 180, 190)

        # Sky blue / cyan
        self.blue = (225, 205, 45)

        # ========================================================
        # FONTS
        # ========================================================

        self.font_paths = {
            "en": self.find_font("NotoSans-Regular"),
            "hi": self.find_font("NotoSansDevanagari-Regular"),
            "te": self.find_font("NotoSansTelugu-Regular"),
            "ta": self.find_font("NotoSansTamil-Regular"),
            "ml": self.find_font("NotoSansMalayalam-Regular"),
            "kn": self.find_font("NotoSansKannada-Regular"),
            "bn": self.find_font("NotoSansBengali-Regular")
        }

    # ============================================================
    # FIND FONT
    # ============================================================

    def find_font(self, font_name):

        directories = [
            r"C:\Windows\Fonts",
            os.path.expanduser(
                r"~\AppData\Local\Microsoft\Windows\Fonts"
            )
        ]

        for directory in directories:

            if not os.path.exists(directory):
                continue

            try:
                files = os.listdir(directory)
            except Exception:
                continue

            for file in files:

                if font_name.lower() in file.lower():
                    return os.path.join(
                        directory,
                        file
                    )

        return r"C:\Windows\Fonts\arial.ttf"

    # ============================================================
    # FONT
    # ============================================================

    def get_font(self, language, size):

        path = self.font_paths.get(
            language,
            r"C:\Windows\Fonts\arial.ttf"
        )

        try:

            return ImageFont.truetype(
                path,
                size
            )

        except Exception:

            return ImageFont.truetype(
                r"C:\Windows\Fonts\arial.ttf",
                size
            )

    # ============================================================
    # TEXT
    # ============================================================

    def draw_text(
        self,
        image,
        text,
        position,
        language="en",
        size=20,
        fill=None
    ):

        if fill is None:
            fill = self.white

        pil_image = Image.fromarray(
            cv2.cvtColor(
                image,
                cv2.COLOR_BGR2RGB
            )
        )

        draw = ImageDraw.Draw(
            pil_image
        )

        font = self.get_font(
            language,
            size
        )

        draw.text(
            position,
            text,
            font=font,
            fill=fill
        )

        return cv2.cvtColor(
            np.array(pil_image),
            cv2.COLOR_RGB2BGR
        )

    # ============================================================
    # ROUNDED CARD
    # ============================================================

    def draw_card(
        self,
        image,
        x1,
        y1,
        x2,
        y2,
        radius=16
    ):

        color = self.card

        cv2.rectangle(
            image,
            (x1 + radius, y1),
            (x2 - radius, y2),
            color,
            -1
        )

        cv2.rectangle(
            image,
            (x1, y1 + radius),
            (x2, y2 - radius),
            color,
            -1
        )

        cv2.circle(
            image,
            (x1 + radius, y1 + radius),
            radius,
            color,
            -1
        )

        cv2.circle(
            image,
            (x2 - radius, y1 + radius),
            radius,
            color,
            -1
        )

        cv2.circle(
            image,
            (x1 + radius, y2 - radius),
            radius,
            color,
            -1
        )

        cv2.circle(
            image,
            (x2 - radius, y2 - radius),
            radius,
            color,
            -1
        )

    # ============================================================
    # NORMAL CAMERA
    #
    # IMPORTANT:
    # We do NOT shrink the camera vertically.
    # We keep the original camera height.
    # We only crop the sides if necessary.
    # This keeps the person's face at normal size.
    # ============================================================

    def prepare_camera(
        self,
        frame,
        target_width,
        target_height
    ):

        frame_h, frame_w = frame.shape[:2]

        # --------------------------------------------------------
        # First make the HEIGHT exactly the target height.
        #
        # For a 1280x720 camera and 720 display height:
        # scale = 1
        #
        # So the face remains at normal camera size.
        # --------------------------------------------------------

        scale = target_height / frame_h

        new_width = int(
            frame_w * scale
        )

        new_height = int(
            frame_h * scale
        )

        resized = cv2.resize(
            frame,
            (new_width, new_height),
            interpolation=cv2.INTER_LINEAR
        )

        # --------------------------------------------------------
        # If camera is wider than available space,
        # crop ONLY the sides.
        # No zoom-out.
        # --------------------------------------------------------

        if new_width > target_width:

            start_x = (
                new_width - target_width
            ) // 2

            camera = resized[
                :,
                start_x:start_x + target_width
            ]

        # --------------------------------------------------------
        # If camera is smaller, don't enlarge excessively.
        # Put it in the center.
        # --------------------------------------------------------

        else:

            camera = np.zeros(
                (
                    target_height,
                    target_width,
                    3
                ),
                dtype=np.uint8
            )

            x = (
                target_width - new_width
            ) // 2

            camera[
                :,
                x:x + new_width
            ] = resized

        return camera

    # ============================================================
    # BLUE DOT
    # ============================================================

    def draw_dot(
        self,
        image,
        x,
        y
    ):

        cv2.circle(
            image,
            (x, y),
            6,
            self.blue,
            -1
        )

        return image

    # ============================================================
    # LANGUAGE LINE
    # ============================================================

    def draw_language_line(
        self,
        image,
        x,
        y,
        width,
        selected_language
    ):

        # Small horizontal language controls.
        #
        # 1 English / 2 Hindi / 3 Telugu / ...
        #

        languages = [
            ("1", "English", "en"),
            ("2", "Hindi", "hi"),
            ("3", "Telugu", "te"),
            ("4", "Tamil", "ta"),
            ("5", "Malayalam", "ml"),
            ("6", "Kannada", "kn"),
            ("7", "Bengali", "bn")
        ]

        # Background strip

        cv2.rectangle(
            image,
            (x, y),
            (x + width, y + 38),
            (20, 19, 23),
            -1
        )

        # Calculate positions dynamically

        available = width - 20

        item_width = (
            available // len(languages)
        )

        current_x = x + 10

        for number, name, code in languages:

            if code == selected_language:

                # Small blue indicator
                cv2.circle(
                    image,
                    (
                        current_x + 5,
                        y + 19
                    ),
                    4,
                    self.blue,
                    -1
                )

                text_color = self.blue

            else:

                text_color = self.gray

            output = self.draw_text(
                image,
                f"{number} {name}",
                (
                    current_x + 12,
                    y + 9
                ),
                code,
                11,
                text_color
            )

            image = output

            current_x += item_width

        return image

    # ============================================================
    # MAIN UI
    # ============================================================

    def render(
        self,
        frame,
        current_sign,
        selected_language,
        fps=0
    ):

        h, w = frame.shape[:2]

        # ========================================================
        # SIDEBAR WIDTH
        # ========================================================

        panel_width = min(
            self.panel_width,
            int(w * 0.30)
        )

        camera_width = w - panel_width

        # ========================================================
        # FINAL CANVAS
        # ========================================================

        output = np.zeros(
            (h, w, 3),
            dtype=np.uint8
        )

        # ========================================================
        # CAMERA
        # ========================================================

        camera_view = self.prepare_camera(
            frame,
            camera_width,
            h - 42
        )

        output[
            0:h - 42,
            0:camera_width
        ] = camera_view

        # ========================================================
        # CAMERA HEADER
        # ========================================================

        output = self.draw_text(
            output,
            "SIGN LANGUAGE TRANSLATOR",
            (22, 16),
            "en",
            24,
            self.white
        )

        output = self.draw_text(
            output,
            "10 GESTURES • 7 LANGUAGES",
            (24, 48),
            "en",
            15,
            self.blue
        )

        output = self.draw_text(
            output,
            f"FPS: {int(fps)}",
            (
                camera_width - 75,
                18
            ),
            "en",
            13,
            self.gray
        )

        # ========================================================
        # LANGUAGE LINE BELOW CAMERA
        # ========================================================

        output = self.draw_language_line(
            output,
            0,
            h - 42,
            camera_width,
            selected_language
        )

        # ========================================================
        # RIGHT SIDEBAR
        # ========================================================

        cv2.rectangle(
            output,
            (camera_width, 0),
            (w, h),
            self.background,
            -1
        )

        x = camera_width + 12
        right = w - 12

        # ========================================================
        # CURRENT GESTURE CARD
        # ========================================================

        self.draw_card(
            output,
            x,
            14,
            right,
            220
        )

        output = self.draw_text(
            output,
            "CURRENT GESTURE",
            (x + 18, 29),
            "en",
            15,
            self.gray
        )

        if current_sign:

            # Gesture name

            output = self.draw_text(
                output,
                current_sign,
                (x + 18, 65),
                "en",
                27,
                self.white
            )

            # Translation

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

            output = self.draw_text(
                output,
                translation,
                (x + 18, 110),
                selected_language,
                23,
                self.blue
            )

        else:

            output = self.draw_text(
                output,
                "Show a gesture...",
                (x + 18, 72),
                "en",
                21,
                self.white
            )

        # ========================================================
        # SELECTED LANGUAGE - SMALL
        # ========================================================

        output = self.draw_text(
            output,
            "Language: ",
            (x + 18, 166),
            "en",
            14,
            self.gray
        )

        output = self.draw_text(
            output,
            LANGUAGES.get(
                selected_language,
                "English"
            ),
            (x + 92, 163),
            selected_language,
            17,
            self.blue
        )

        # ========================================================
        # SUPPORTED GESTURES CARD
        # ========================================================

        self.draw_card(
            output,
            x,
            235,
            right,
            h - 14
        )

        output = self.draw_text(
            output,
            "SUPPORTED GESTURES",
            (x + 18, 250),
            "en",
            15,
            self.gray
        )

        # ========================================================
        # GESTURES
        # ========================================================

        left_gestures = [
            "HELLO",
            "THANK YOU",
            "NO",
            "FRIEND",
            "DRINK"
        ]

        right_gestures = [
            "STOP",
            "YES",
            "PLEASE",
            "EAT",
            "HELP"
        ]

        gesture_y = [
            290,
            340,
            390,
            440,
            490
        ]

        # LEFT

        for gesture, y in zip(
            left_gestures,
            gesture_y
        ):

            output = self.draw_dot(
                output,
                x + 20,
                y + 9
            )

            output = self.draw_text(
                output,
                gesture,
                (x + 38, y - 2),
                "en",
                14,
                self.white
            )

        # RIGHT

        for gesture, y in zip(
            right_gestures,
            gesture_y
        ):

            output = self.draw_dot(
                output,
                x + 180,
                y + 9
            )

            output = self.draw_text(
                output,
                gesture,
                (x + 198, y - 2),
                "en",
                14,
                self.white
            )

        return output