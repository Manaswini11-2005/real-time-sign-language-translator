# 🤟 Real-Time Sign Language Translator

A real-time computer vision application that recognizes hand gestures through a webcam and translates them into meaningful text and speech.

The project uses **MediaPipe hand landmark detection** and **OpenCV** to identify predefined hand gestures in real time, with support for **10 gestures and 7 languages**.

---

## ✨ Features

- 🎥 Real-time webcam-based gesture recognition
- ✋ Hand landmark detection using MediaPipe
- 🤟 Recognition of 10 predefined gestures
- 🌐 Translation support for 7 languages
- 🔊 Text-to-speech output
- 🖥️ Real-time interactive dashboard
- ⚡ Stable gesture detection to reduce false predictions
- 📊 Live gesture and translation display
- 🔤 Unicode font support for Indian languages

---

## ✋ Supported Gestures

| Gesture | Meaning |
|---|---|
| 🖐️ Open Palm | HELLO |
| ✊ Closed Palm | STOP |
| 🙏 Two Palms Together | THANK YOU |
| 👍 Thumbs Up | YES |
| 👎 Thumbs Down | NO |
| 🤌 Pinched Fingers | PLEASE |
| ✌️ V Sign | FRIEND |
| 🖐️ Three Fingers | EAT |
| 🤏 Index + Thumb | DRINK |
| 🖐️🖐️ Two Open Hands | HELP |

---

## 🌐 Supported Languages

The application supports translation into:

1. English
2. Hindi
3. Telugu
4. Tamil
5. Malayalam
6. Kannada
7. Bengali

---

## 🛠️ Technologies Used

- Python
- OpenCV
- MediaPipe
- NumPy
- Pillow
- gTTS
- Pygame

---

## 🧠 How It Works

```text
Webcam
   ↓
Video Frame
   ↓
MediaPipe Hand Detection
   ↓
Hand Landmark Extraction
   ↓
Finger / Hand Gesture Analysis
   ↓
Gesture Classification
   ↓
Text Translation
   ↓
Selected Language
   ↓
Text-to-Speech Output




![alt text](<Sign Language Translator Project Overview.png>)