
# 💚 MATRIX HACKER MODE — ChaCha20 LIVE ANIMATION  
### 🔐 Real-time Visualization of the ChaCha20 Stream Cipher  
#### Built with Python, NumPy, Gradio & Custom Neon Matrix UI

---

## 🚀 Project Overview

This project is a **fully interactive, animated visualization** of the **ChaCha20 encryption algorithm**, designed with a **Matrix-style neon hacker theme**.

It converts difficult cryptographic operations into a **step-by-step live animation**, making it perfect for:

- 🔍 Learning cryptography  
- 🧑‍🏫 Classroom demonstrations  
- 🧪 Information Security mini-projects  
- 💡 Visual explanation of ChaCha20  
- 🎓 College/University submissions  
- 🖥️ Cybersecurity UI showcases  

---

## ✨ Features

### 🟩 **1. Live ChaCha20 Animation (20 Rounds)**
- Each round updates **in real time** using Gradio’s `yield`.
- See matrix values transform dynamically.
- Smooth neon glow on each matrix cell.

### 🌧 **2. Matrix Rain Background**
- Fullscreen animated Matrix rain canvas (JS-powered).
- Runs behind the Gradio interface.

### 🔊 **3. Sound Effects (Beep per Round)**
- Each ChaCha20 round triggers a soft beep.
- Enhances the hacker aesthetic.

### ⚡ **4. Neon Green Progress Bar**
- Shows algorithm progress from Round 1 → 20.
- Synchronizes with live updates.

### 📚 **5. Right-Side Cryptography Explanation Panel**
Contains:
- ChaCha20 overview  
- Round structure  
- Quarter-round operations  
- State matrix structure  
- How keystream XOR produces ciphertext  

Stays fixed on the right without overlapping.



---

## 🔐 What is ChaCha20?

**ChaCha20** is a modern, fast, and secure stream cipher:

- Designed by Daniel J. Bernstein  
- Widely used in **TLS 1.3**, **WireGuard VPN**, **OpenSSH**, **Google**, **Cloudflare**, etc.  
- Uses **20 rounds** of add–xor–rotate operations  
- Produces a 512-bit keystream block  
- Encryption = `ciphertext = plaintext XOR keystream`

The algorithm operates on a **4×4 matrix (16 × 32-bit words)** consisting of:

| Component  | Size |
|-----------|------|
| Constants | 128 bits |
| Key       | 256 bits |
| Counter   | 32 bits |
| Nonce     | 96 bits |

---

## 🧠 How the Animation Works

1. **Initial State Matrix**  
   - Shows constants, key, counter & nonce.

2. **20 Live Rounds (with glow animation)**  
   - Each round updates matrix values.  
   - Beep sound plays for each round.  
   - Neon progress bar increments.

3. **Final Keystream Matrix**  
   - After 20 rounds, final state is added to original state.

4. **XOR Encryption**  
   - Plaintext is XORed with keystream bytes.  
   - Output shown in hex.

---

## 🛠 Technologies Used

- **Python**
- **NumPy**
- **Gradio**
- **HTML + CSS + JavaScript**
- **Canvas-based Matrix Rain animation**

---

## 📦 Installation (Local Development)

```bash
pip install gradio numpy
python app.py
