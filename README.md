# Sonic-Cipher-4.0
Hide secret text messages inside WAV audio files using binary tone encoding — Audio Steganography built with Java &amp; Python.


# 🔊 Sonic Cipher 4.0 — Audio Steganography System

> "Don't just encrypt your message. Hide the fact that it exists."

Sonic Cipher 4.0 is an Audio Steganography System that conceals 
secret text messages inside standard WAV audio files using binary 
tone encoding — no external libraries, no complex setup.

The encoded audio sounds like a sequence of beeps to any listener 
but carries a completely hidden message that can only be revealed 
by decoding it through the same platform.

---

## ⚙️ How It Works

| Step | Process |
|------|---------|
| 1 | User enters any text |
| 2 | Text → ASCII → 8-bit Binary |
| 3 | Each '0' = 200ms audio tone |
| 4 | Each '1' = 500ms audio tone |
| 5 | 50ms silence gap between every bit |
| 6 | All tones packaged into a .WAV file |
| 7 | Drag the file back → message decoded instantly |

---

## 🛠️ Tech Stack

- **Java** — Core encoding, decoding & audio signal generation
- **Python + Tkinter** — Drag-and-drop graphical interface
- **WAV Format** — 44,100 Hz | 16-bit PCM | Mono channel

---

## 🚀 How to Run

### 1. Compile Java files
javac src/*.java -d out/

### 2. Launch the GUI
python gui.py

### 3. Encode
Type your message → Click Encode → Download the .WAV file

### 4. Decode
Drag the .WAV file into the platform → Hidden text appears

---

## 📁 Project Structure

Sonic-Cipher-4.0/
├── src/
│   ├── Main.java        → Entry point & orchestration
│   ├── Encoder.java     → Text to audio encoding
│   ├── Decoder.java     → Audio to text decoding
│   └── AudioUtil.java   → Tone & WAV utilities
├── output/
│   └── encoded.wav      → Generated audio output
└── gui.py               → Python Tkinter GUI

---

## 👨‍💻 Author

**[Shourya Sinha]**
1st Year B.Tech | Semester 2
[Bennett University]

---

## ⭐ If you found this interesting, drop a star!
