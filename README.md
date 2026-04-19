# 🤖 JARVIS — Personal AI Assistant

A fully functional **voice-controlled AI assistant** inspired by JARVIS, built using modern **GenAI + automation tools**.
This assistant can understand natural language commands and execute real-world actions like playing music, controlling system apps, performing web searches, and more.

---

## 🚀 Key Highlights

* 🎤 **Voice-Controlled AI** — Real-time command execution using speech input
* 🧠 **LLM-Powered Intelligence** — Integrated with Groq LLM for fast responses
* 🔊 **Dual Speech Engine**

  * Google Speech-to-Text (online)
  * Whisper fallback (offline support)
* ⚡ **Agentic Tool Execution Pipeline**

  * YouTube auto-play with ad skip
  * AI image generation (Flux API)
  * Web search & information retrieval
  * File operations (read/write/list)
  * System control (open apps, run commands)
* 🖥️ **Futuristic UI**

  * Built with Gradio
  * Iron Man–inspired HUD design
  * Real-time chat + command visualization

---

## 🛠️ Tech Stack

* **Language:** Python
* **AI/LLM:** Groq API
* **Voice:** SpeechRecognition, Whisper
* **Automation:** Selenium
* **UI:** Gradio (custom CSS animations)
* **APIs:** Flux (Image Generation), Web APIs

---

## 🧠 Architecture Overview

```
User Input (Voice/Text)
        ↓
Speech Recognition Layer
        ↓
LLM (Intent Understanding)
        ↓
Command Router
        ↓
Tool Execution Layer
        ↓
Real-world Actions (Browser, Files, System, etc.)
```

---

## ⚙️ Installation & Setup

```bash
git clone https://github.com/YOUR_USERNAME/jarvis-ai-assistant.git
cd jarvis-ai-assistant

pip install -r requirements.txt
python main.py
```

---

## 🔐 Environment Variables

Create a `.env` file in the root directory:

```
GROQ_API_KEY=your_api_key_here
```

---

## 🎯 Features in Action

* 🎵 *"Play Shape of You on YouTube"* → Auto opens and plays video
* 🌐 *"Open GitHub"* → Launches website
* 📂 *"Read file notes.txt"* → Reads file content
* 🧠 *"Explain machine learning"* → AI-generated response
* 🎨 *"Generate an image of cyberpunk city"* → AI image output

---

## ⚠️ Limitations

* Requires local system access (not fully cloud-deployable yet)
* Selenium-based automation may break if YouTube UI changes
* Some features depend on OS-specific commands

---

## 🚀 Future Improvements

* Cloud deployment (Hugging Face / FastAPI backend)
* Better intent classification (agent routing)
* Memory system for contextual conversations
* Multi-modal capabilities (vision + voice)

---

## 👨‍💻 Author

**Nitin Rawat**
Aspiring AI Engineer | GenAI Developer

---

## ⭐ Project Vision

This project is a step toward building a **true agentic AI system** capable of:

* Understanding user intent
* Making decisions
* Executing real-world actions autonomously

Inspired by the concept of intelligent assistants like JARVIS.
