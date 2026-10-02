import math


class GestureDetector:

    def __init__(self):

        # Stability
        self.current_candidate = None
        self.candidate_frames = 0
        self.stable_gesture = None

        # Number of consecutive frames required
        self.required_frames = 6

    # ============================================================
    # DISTANCE
    # ============================================================

    def distance(self, p1, p2):

        return math.sqrt(
            (p1.x - p2.x) ** 2 +
            (p1.y - p2.y) ** 2 +
            (p1.z - p2.z) ** 2
        )

    # ============================================================
    # FINGER DETECTION
    # ============================================================

    def finger_is_open(
        self,
        landmarks,
        tip,
        pip
    ):

        wrist = landmarks[0]

        tip_distance = self.distance(
            landmarks[tip],
            wrist
        )

        pip_distance = self.distance(
            landmarks[pip],
            wrist
        )

        return tip_distance > pip_distance * 1.12

    # ============================================================
    # GET FINGERS
    # ============================================================

    def get_fingers(self, landmarks):

        thumb = self.finger_is_open(
            landmarks,
            4,
            3
        )

        index = self.finger_is_open(
            landmarks,
            8,
            6
        )

        middle = self.finger_is_open(
            landmarks,
            12,
            10
        )

        ring = self.finger_is_open(
            landmarks,
            16,
            14
        )

        pinky = self.finger_is_open(
            landmarks,
            20,
            18
        )

        return [
            thumb,
            index,
            middle,
            ring,
            pinky
        ]

    # ============================================================
    # COUNT OPEN FINGERS
    # ============================================================

    def open_finger_count(self, landmarks):

        return sum(
            self.get_fingers(landmarks)
        )

    # ============================================================
    # THUMB DIRECTION
    # ============================================================

    def thumb_direction(self, landmarks):

        wrist = landmarks[0]
        thumb_tip = landmarks[4]

        if thumb_tip.y < wrist.y - 0.08:
            return "UP"

        if thumb_tip.y > wrist.y + 0.08:
            return "DOWN"

        return "CENTER"

    # ============================================================
    # PINCH
    # ============================================================

    def is_pinched(self, landmarks):

        distance = self.distance(
            landmarks[4],
            landmarks[8]
        )

        return distance < 0.075

    # ============================================================
    # PALM CENTER
    # ============================================================

    def palm_center(self, landmarks):

        points = [
            landmarks[0],
            landmarks[5],
            landmarks[9],
            landmarks[13],
            landmarks[17]
        ]

        x = sum(
            p.x for p in points
        ) / len(points)

        y = sum(
            p.y for p in points
        ) / len(points)

        z = sum(
            p.z for p in points
        ) / len(points)

        return x, y, z

    # ============================================================
    # PALM DISTANCE
    # ============================================================

    def palm_distance(
        self,
        hand1,
        hand2
    ):

        p1 = self.palm_center(hand1)
        p2 = self.palm_center(hand2)

        return math.sqrt(
            (p1[0] - p2[0]) ** 2 +
            (p1[1] - p2[1]) ** 2 +
            (p1[2] - p2[2]) ** 2
        )

    # ============================================================
    # SINGLE HAND
    # ============================================================

    def detect_single_hand(self, landmarks):

        fingers = self.get_fingers(
            landmarks
        )

        thumb, index, middle, ring, pinky = fingers

        # --------------------------------------------------------
        # HELLO
        # All fingers open
        # --------------------------------------------------------

        if sum(fingers) >= 5:
            return "HELLO"

        # --------------------------------------------------------
        # STOP
        # Closed fist
        # --------------------------------------------------------

        if sum(fingers) == 0:
            return "STOP"

        # --------------------------------------------------------
        # YES
        # Thumb only + pointing upward
        # --------------------------------------------------------

        if (
            thumb
            and not index
            and not middle
            and not ring
            and not pinky
            and self.thumb_direction(landmarks) == "UP"
        ):
            return "YES"

        # --------------------------------------------------------
        # NO
        # Thumb only + pointing downward
        # --------------------------------------------------------

        if (
            thumb
            and not index
            and not middle
            and not ring
            and not pinky
            and self.thumb_direction(landmarks) == "DOWN"
        ):
            return "NO"

        # --------------------------------------------------------
        # FRIEND
        # Index + middle
        # --------------------------------------------------------

        if (
            not thumb
            and index
            and middle
            and not ring
            and not pinky
        ):
            return "FRIEND"

        # --------------------------------------------------------
        # EAT
        # Index + middle + ring
        # --------------------------------------------------------

        if (
            not thumb
            and index
            and middle
            and ring
            and not pinky
        ):
            return "EAT"

        # --------------------------------------------------------
        # DRINK
        # Thumb + index
        # --------------------------------------------------------

        if (
            thumb
            and index
            and not middle
            and not ring
            and not pinky
        ):
            return "DRINK"

        # --------------------------------------------------------
        # PLEASE
        # Pinched fingers
        # --------------------------------------------------------

        if self.is_pinched(landmarks):

            if not middle and not ring and not pinky:
                return "DRINK"

            return "PLEASE"

        return None

    # ============================================================
    # TWO HAND GESTURES
    # ============================================================

    def detect_two_hands(
        self,
        hand1,
        hand2
    ):

        count1 = self.open_finger_count(
            hand1
        )

        count2 = self.open_finger_count(
            hand2
        )

        distance = self.palm_distance(
            hand1,
            hand2
        )

        # --------------------------------------------------------
        # THANK YOU
        #
        # Both hands mostly open + palms close together
        #
        # We allow 4/5 fingers because fingers can be hidden
        # when the palms are brought together.
        # --------------------------------------------------------

        if (
            count1 >= 4
            and count2 >= 4
            and distance < 0.30
        ):
            return "THANK YOU"

        # --------------------------------------------------------
        # HELP
        #
        # Both hands mostly open + clearly separated
        # --------------------------------------------------------

        if (
            count1 >= 4
            and count2 >= 4
            and distance > 0.34
        ):
            return "HELP"

        return None

    # ============================================================
    # RAW DETECTION
    # ============================================================

    def detect_raw(self, hands):

        if not hands:
            return None

        # --------------------------------------------------------
        # TWO HANDS
        # --------------------------------------------------------

        if len(hands) >= 2:

            gesture = self.detect_two_hands(
                hands[0],
                hands[1]
            )

            if gesture:
                return gesture

        # --------------------------------------------------------
        # SINGLE HAND
        # --------------------------------------------------------

        return self.detect_single_hand(
            hands[0]
        )

    # ============================================================
    # STABILITY
    # ============================================================

    def stabilize(self, gesture):

        # No proper gesture
        if gesture is None:

            self.current_candidate = None
            self.candidate_frames = 0
            self.stable_gesture = None

            return None

        # Same gesture
        if gesture == self.current_candidate:

            self.candidate_frames += 1

        else:

            self.current_candidate = gesture
            self.candidate_frames = 1
            self.stable_gesture = None

        # Stable
        if self.candidate_frames >= self.required_frames:

            self.stable_gesture = gesture

            return gesture

        return None

    # ============================================================
    # MAIN
    # ============================================================

    def detect(self, hands):

        gesture = self.detect_raw(
            hands
        )

        return self.stabilize(
            gesture
        )