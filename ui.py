import gradio as gr
from brain import ask_jarvis
from voice import speak, listen
from memory import load_history, add_to_history, clear_history
from tools import execute_tool

conversation_history = load_history()

# ─────────────────────────────────────────────────────────────
# 🎨 FUTURISTIC CSS — Iron Man HUD Style
# ─────────────────────────────────────────────────────────────
JARVIS_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Rajdhani:wght@300;400;500;600&family=Share+Tech+Mono&display=swap');

:root {
    --cyan:        #00f5ff;
    --cyan-dim:    #00c8d4;
    --cyan-glow:   rgba(0, 245, 255, 0.15);
    --cyan-border: rgba(0, 245, 255, 0.35);
    --orange:      #ff6b00;
    --orange-glow: rgba(255, 107, 0, 0.2);
    --bg-void:     #000608;
    --bg-deep:     #020d12;
    --bg-panel:    #040f14;
    --bg-card:     #061520;
    --text-main:   #c8f4ff;
    --text-dim:    #4a8fa0;
    --text-mono:   #00f5ff;
    --danger:      #ff2244;
    --success:     #00ff88;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body, .gradio-container {
    background: var(--bg-void) !important;
    font-family: 'Rajdhani', sans-serif !important;
    color: var(--text-main) !important;
    min-height: 100vh;
    overflow-x: hidden;
}

.gradio-container::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0, 245, 255, 0.015) 2px,
        rgba(0, 245, 255, 0.015) 4px
    );
    pointer-events: none;
    z-index: 9999;
    animation: scanlines 8s linear infinite;
}

@keyframes scanlines {
    0%   { background-position: 0 0; }
    100% { background-position: 0 100px; }
}

.gradio-container::after {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image:
        linear-gradient(rgba(0, 245, 255, 0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 245, 255, 0.04) 1px, transparent 1px);
    background-size: 50px 50px;
    pointer-events: none;
    z-index: 0;
    animation: gridPulse 4s ease-in-out infinite alternate;
}

@keyframes gridPulse {
    0%   { opacity: 0.4; }
    100% { opacity: 1; }
}

.main, .contain, #component-0 {
    position: relative;
    z-index: 1;
}

#jarvis-header {
    text-align: center;
    padding: 28px 20px 20px;
    position: relative;
}

#jarvis-header::after {
    content: '';
    display: block;
    height: 1px;
    background: linear-gradient(90deg,
        transparent, var(--cyan), var(--orange), var(--cyan), transparent);
    margin-top: 20px;
    animation: headerLine 3s ease-in-out infinite alternate;
}

@keyframes headerLine {
    0%   { opacity: 0.4; }
    100% { opacity: 1; }
}

.jarvis-title {
    font-family: 'Orbitron', monospace !important;
    font-size: 3rem !important;
    font-weight: 900 !important;
    letter-spacing: 0.4em !important;
    color: transparent !important;
    background: linear-gradient(135deg, var(--cyan) 0%, #ffffff 50%, var(--orange) 100%) !important;
    -webkit-background-clip: text !important;
    background-clip: text !important;
    text-shadow: none !important;
    animation: titleGlow 2s ease-in-out infinite alternate;
    margin-bottom: 6px !important;
}

@keyframes titleGlow {
    0%   { filter: drop-shadow(0 0 8px rgba(0, 245, 255, 0.5)); }
    100% { filter: drop-shadow(0 0 20px rgba(0, 245, 255, 0.9)); }
}

.jarvis-subtitle {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.3em !important;
    color: var(--text-dim) !important;
    text-transform: uppercase;
}

#status-bar {
    display: flex;
    justify-content: center;
    gap: 30px;
    padding: 8px 20px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    color: var(--text-dim);
    letter-spacing: 0.15em;
}

.status-item { display: flex; align-items: center; gap: 6px; }

.status-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--success);
    box-shadow: 0 0 6px var(--success);
    animation: blink 1.5s ease-in-out infinite;
}

.status-dot.orange { background: var(--orange); box-shadow: 0 0 6px var(--orange); }
.status-dot.cyan   { background: var(--cyan);   box-shadow: 0 0 6px var(--cyan); }

@keyframes blink {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.3; }
}

#chatbox-wrap {
    background: var(--bg-panel) !important;
    border: 1px solid var(--cyan-border) !important;
    border-radius: 4px !important;
    position: relative;
    overflow: hidden;
    box-shadow:
        0 0 0 1px rgba(0, 245, 255, 0.05),
        0 0 30px rgba(0, 245, 255, 0.06),
        inset 0 0 60px rgba(0, 0, 0, 0.5);
}

#chatbox-wrap::before, #chatbox-wrap::after {
    content: '';
    position: absolute;
    width: 20px; height: 20px;
    border-color: var(--cyan);
    border-style: solid;
    z-index: 10;
}
#chatbox-wrap::before { top: -1px; left: -1px; border-width: 2px 0 0 2px; }
#chatbox-wrap::after  { bottom: -1px; right: -1px; border-width: 0 2px 2px 0; }

.gradio-container textarea,
.gradio-container input[type="text"] {
    background: rgba(0, 245, 255, 0.03) !important;
    border: 1px solid var(--cyan-border) !important;
    border-radius: 2px !important;
    color: var(--text-main) !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 500 !important;
    padding: 10px 14px !important;
    caret-color: var(--cyan) !important;
    transition: border-color 0.2s, box-shadow 0.2s;
    letter-spacing: 0.03em;
}

.gradio-container textarea:focus,
.gradio-container input[type="text"]:focus {
    border-color: var(--cyan) !important;
    box-shadow: 0 0 0 2px var(--cyan-glow), inset 0 0 20px rgba(0, 245, 255, 0.04) !important;
    outline: none !important;
}

.gradio-container textarea::placeholder,
.gradio-container input::placeholder {
    color: var(--text-dim) !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.8rem !important;
}

.gradio-container button {
    font-family: 'Orbitron', monospace !important;
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    border-radius: 2px !important;
    transition: all 0.2s ease !important;
    position: relative !important;
    overflow: hidden !important;
}

.gradio-container button.primary {
    background: transparent !important;
    border: 1px solid var(--cyan) !important;
    color: var(--cyan) !important;
    box-shadow: 0 0 10px var(--cyan-glow), inset 0 0 10px var(--cyan-glow) !important;
}

.gradio-container button.primary:hover {
    background: var(--cyan-glow) !important;
    box-shadow: 0 0 20px var(--cyan), inset 0 0 20px var(--cyan-glow) !important;
    transform: translateY(-1px) !important;
}

.gradio-container button.secondary,
.gradio-container button:not(.primary):not(.stop) {
    background: transparent !important;
    border: 1px solid var(--orange) !important;
    color: var(--orange) !important;
    box-shadow: 0 0 10px var(--orange-glow) !important;
}

.gradio-container button.secondary:hover,
.gradio-container button:not(.primary):not(.stop):hover {
    background: var(--orange-glow) !important;
    box-shadow: 0 0 20px var(--orange) !important;
    transform: translateY(-1px) !important;
}

.gradio-container button.stop {
    background: transparent !important;
    border: 1px solid var(--danger) !important;
    color: var(--danger) !important;
    box-shadow: 0 0 8px rgba(255, 34, 68, 0.2) !important;
}

.gradio-container button.stop:hover {
    background: rgba(255, 34, 68, 0.1) !important;
    box-shadow: 0 0 16px var(--danger) !important;
}

.gradio-container button::after {
    content: '';
    position: absolute;
    top: -50%; left: -60%;
    width: 40%; height: 200%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent);
    transform: skewX(-20deg);
    transition: left 0.5s;
}
.gradio-container button:hover::after { left: 120%; }

#side-panel {
    background: var(--bg-panel);
    border: 1px solid var(--cyan-border);
    border-radius: 4px;
    padding: 16px;
    position: relative;
    box-shadow: 0 0 20px rgba(0, 245, 255, 0.05);
}

#side-panel::before {
    content: '';
    position: absolute;
    top: -1px; left: -1px;
    width: 20px; height: 20px;
    border-top: 2px solid var(--cyan);
    border-left: 2px solid var(--cyan);
}

.gradio-container .prose p,
.gradio-container .prose li {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.72rem !important;
    color: var(--text-dim) !important;
    line-height: 1.8 !important;
    letter-spacing: 0.05em !important;
}

.gradio-container .prose code {
    background: rgba(0, 245, 255, 0.08) !important;
    color: var(--cyan) !important;
    border: 1px solid var(--cyan-border) !important;
    border-radius: 2px !important;
    padding: 1px 5px !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.7rem !important;
}

.gradio-container .prose h3 {
    font-family: 'Orbitron', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.2em !important;
    color: var(--cyan) !important;
    margin-bottom: 10px !important;
}

.gradio-container .block,
.gradio-container .form {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg-void); }
::-webkit-scrollbar-thumb { background: var(--cyan-border); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--cyan); }

.gradio-container footer { display: none !important; }
"""

# ─────────────────────────────────────────────────────────────
# 💬 CHAT RENDER
# ─────────────────────────────────────────────────────────────
def render_chat(history):
    if not history:
        return """
        <div style='height:460px; overflow-y:auto; padding:20px;
                    display:flex; align-items:center; justify-content:center;
                    flex-direction:column; gap:16px;'>
            <div style='width:80px; height:80px; border-radius:50%;
                        border:2px solid rgba(0,245,255,0.3);
                        box-shadow:0 0 30px rgba(0,245,255,0.15);
                        display:flex; align-items:center; justify-content:center;
                        animation:pulse 2s ease-in-out infinite; font-size:2rem;'>🤖</div>
            <div style='font-family:"Orbitron",monospace; font-size:0.65rem;
                        letter-spacing:0.3em; color:rgba(0,245,255,0.5);
                        text-transform:uppercase;'>Systems Online</div>
            <div style='font-family:"Share Tech Mono",monospace; font-size:0.7rem;
                        color:rgba(72,143,160,0.7); letter-spacing:0.1em;'>
                Awaiting your command, sir.</div>
            <style>
            @keyframes pulse {
                0%,100%{box-shadow:0 0 20px rgba(0,245,255,0.15);}
                50%{box-shadow:0 0 40px rgba(0,245,255,0.4);}
            }
            </style>
        </div>"""

    msgs_html = ""
    for i, (user_msg, bot_msg) in enumerate(history):
        ts = f"T+{i+1:03d}"
        msgs_html += f"""
        <div style='margin-bottom:20px; text-align:right; animation:fadeIn 0.3s ease;'>
            <div style='font-family:"Share Tech Mono",monospace; font-size:0.6rem;
                        color:rgba(0,245,255,0.35); letter-spacing:0.15em;
                        margin-bottom:5px;'>YOU · {ts}</div>
            <span style='background:linear-gradient(135deg,rgba(0,100,140,0.6),rgba(0,60,90,0.4));
                         color:#c8f4ff; padding:10px 16px; border-radius:2px 2px 2px 12px;
                         display:inline-block; max-width:78%; word-wrap:break-word;
                         font-size:0.95rem; font-family:"Rajdhani",sans-serif; font-weight:500;
                         line-height:1.5; letter-spacing:0.03em;
                         border:1px solid rgba(0,245,255,0.25);
                         box-shadow:0 0 15px rgba(0,245,255,0.08); text-align:left;'>
                {user_msg}
            </span>
        </div>"""

        safe_msg = bot_msg.replace('<', '&lt;').replace('>', '&gt;')
        msgs_html += f"""
        <div style='margin-bottom:24px; text-align:left; animation:fadeIn 0.3s ease 0.1s both;'>
            <div style='font-family:"Share Tech Mono",monospace; font-size:0.6rem;
                        color:rgba(255,107,0,0.5); letter-spacing:0.15em;
                        margin-bottom:5px;'>◈ J.A.R.V.I.S · {ts}</div>
            <span style='background:linear-gradient(135deg,rgba(4,15,20,0.9),rgba(6,21,32,0.8));
                         color:#c8f4ff; padding:12px 16px; border-radius:2px 12px 12px 2px;
                         display:inline-block; max-width:82%; word-wrap:break-word;
                         font-size:0.95rem; font-family:"Rajdhani",sans-serif; font-weight:400;
                         line-height:1.6; letter-spacing:0.03em;
                         border:1px solid rgba(255,107,0,0.2);
                         border-left:2px solid rgba(255,107,0,0.6);
                         box-shadow:0 0 15px rgba(255,107,0,0.05);
                         white-space:pre-wrap; text-align:left;'>
                {safe_msg}
            </span>
        </div>"""

    return (f"<div id='chatbox' style='height:460px; overflow-y:auto; padding:16px 20px;"
            f"scroll-behavior:smooth;"
            f"background:linear-gradient(180deg,rgba(0,6,8,0.6) 0%,rgba(2,13,18,0.4) 100%);'>"
            f"<style>"
            f"@keyframes fadeIn{{from{{opacity:0;transform:translateY(8px);}}"
            f"to{{opacity:1;transform:translateY(0);}}}}"
            f"#chatbox::-webkit-scrollbar{{width:3px;}}"
            f"#chatbox::-webkit-scrollbar-thumb{{background:rgba(0,245,255,0.2);}}"
            f"</style>"
            f"{msgs_html}"
            f"<script>var cb=document.getElementById('chatbox');"
            f"if(cb)cb.scrollTop=cb.scrollHeight;</script>"
            f"</div>")


# ─────────────────────────────────────────────────────────────
# 🧠 CHAT LOGIC
# ─────────────────────────────────────────────────────────────
def chat(user_message: str, history_display: list):
    global conversation_history

    if not user_message.strip():
        return "", history_display

    msg_lower = user_message.lower().strip()
    clean_msg = msg_lower
    if clean_msg.startswith("jarvis "):
        clean_msg = clean_msg[7:]

    known_sites = list({"youtube", "google", "github", "facebook", "instagram",
                        "twitter", "whatsapp", "gmail", "netflix", "amazon",
                        "flipkart", "stackoverflow", "chatgpt", "spotify"})
    known_apps  = list({"notepad", "calculator", "chrome", "firefox", "vlc",
                        "paint", "vs code", "explorer", "task manager", "word", "excel"})

    tool_prefixes = ["read:", "write:", "run:", "search:", "open:",
                     "sysinfo", "screenshot", "play:", "generate image"]

    is_play          = ("play" in clean_msg and any(x in clean_msg for x in
                        ["youtube", "song", "music", "video"])) or clean_msg.startswith("play ")
    is_open          = clean_msg.startswith("open ") or clean_msg.startswith("open:")
    is_search        = clean_msg.startswith("search ") or clean_msg.startswith("search:")
    is_run           = clean_msg.startswith("run ") or clean_msg.startswith("run:")
    is_read          = clean_msg.startswith("read ") or clean_msg.startswith("read:")

    # ✅ New: detect image generation command
    is_image         = (clean_msg.startswith("generate image") or
                        clean_msg.startswith("create image") or
                        clean_msg.startswith("make image") or
                        "generate image" in clean_msg)

    has_site         = any(site in clean_msg for site in known_sites)
    has_app          = any(app  in clean_msg for app  in known_apps)
    has_dotcom       = any(x    in clean_msg for x    in [".com", ".in", ".org", ".net"])

    is_tool = (
        any(msg_lower.startswith(p) for p in tool_prefixes)
        or clean_msg in ["sysinfo", "screenshot"]
        or is_play or is_open or is_search or is_run or is_read or is_image
        or (has_site and "open" in clean_msg)
        or (has_app  and "open" in clean_msg)
        or (has_dotcom and "open" in clean_msg)
    )

    try:
        if is_tool:
            # ── Image generation ──────────────────────────────
            if is_image:
                # Extract prompt after "generate image", "create image", etc.
                for trigger in ["generate image:", "generate image",
                                "create image:", "create image",
                                "make image:", "make image"]:
                    if clean_msg.startswith(trigger):
                        prompt = user_message[len(trigger):].strip()
                        clean_msg = f"generate image: {prompt}"
                        break

            elif is_play and not clean_msg.startswith("play:"):
                song = clean_msg
                for word in ["play", "on youtube", "in youtube",
                             "on music", "song", "video", "music"]:
                    song = song.replace(word, "").strip()
                clean_msg = "play:" + song

            elif is_open and not clean_msg.startswith("open:"):
                clean_msg = "open:" + clean_msg[5:]

            elif is_search and not clean_msg.startswith("search:"):
                clean_msg = "search:" + clean_msg.replace(
                    "search for ", "").replace("search ", "")

            elif is_run and not clean_msg.startswith("run:"):
                clean_msg = "run:" + clean_msg[4:]

            elif is_read and not clean_msg.startswith("read:"):
                clean_msg = "read:" + clean_msg[5:]

            elif "open" in clean_msg and (has_site or has_app or has_dotcom):
                after_open = clean_msg.split("open", 1)[1].strip()
                clean_msg  = "open:" + after_open

            tool_result = execute_tool(clean_msg)
            response    = tool_result
        else:
            response = ask_jarvis(user_message, conversation_history)

    except Exception as e:
        response = f"⚠ System error: {str(e)}"

    conversation_history = add_to_history(conversation_history, "user", user_message)
    conversation_history = add_to_history(conversation_history, "assistant", response)

    try:
        action_commands = ["open:", "open ", "run:", "screenshot",
                           "write:", "read:", "search:", "play:", "generate image"]
        is_action = (
            any(user_message.lower().strip().startswith(cmd) for cmd in action_commands)
            or is_play or is_open or is_image
        )
        if not is_action:
            speak(response[:250])
    except Exception as e:
        print(f"Voice error: {e}")

    history_display = history_display or []
    history_display.append((user_message, response))
    return "", history_display


def voice_input_fn(history_display):
    try:
        text = listen()
    except Exception:
        text = ""
    if text and text.strip():
        return chat(text, history_display)
    return "", history_display or []


def clear_chat():
    global conversation_history
    conversation_history = clear_history()
    return []


# ─────────────────────────────────────────────────────────────
# 🖥️  UI LAYOUT
# ─────────────────────────────────────────────────────────────
with gr.Blocks(
    title="J.A.R.V.I.S",
    css=JARVIS_CSS,
    theme=gr.themes.Base(
        primary_hue="cyan",
        neutral_hue="slate",
        font=gr.themes.GoogleFont("Rajdhani"),
    )
) as app:

    gr.HTML("""
    <div id='jarvis-header'>
        <div class='jarvis-title'>J.A.R.V.I.S</div>
        <div class='jarvis-subtitle'>
            Just A Rather Very Intelligent System · Personal AI Core
        </div>
    </div>
    <div id='status-bar'>
        <div class='status-item'><div class='status-dot'></div><span>NEURAL CORE ONLINE</span></div>
        <div class='status-item'><div class='status-dot cyan'></div><span>VOICE ACTIVE</span></div>
        <div class='status-item'><div class='status-dot orange'></div><span>GROQ ENGINE READY</span></div>
        <div class='status-item'><div class='status-dot'></div><span>IMAGE GEN READY</span></div>
    </div>
    """)

    with gr.Row(equal_height=True):
        with gr.Column(scale=4):
            gr.HTML("<div id='chatbox-wrap'>")
            chat_html  = gr.HTML(value=render_chat([]))
            gr.HTML("</div>")
            chat_state = gr.State([])

            with gr.Row(equal_height=True):
                msg_input = gr.Textbox(
                    value="",
                    placeholder="// ENTER COMMAND OR QUERY . . .",
                    show_label=False,
                    scale=5, lines=1, max_lines=3,
                    container=False,
                )
                send_btn  = gr.Button("SEND",  variant="primary", scale=1, min_width=80)
                voice_btn = gr.Button("⬤ MIC", scale=1, min_width=90)

        with gr.Column(scale=1, min_width=220):
            gr.HTML("<div id='side-panel'><div class='panel-title'>◈ Command Matrix</div></div>")

            gr.Markdown("""
### ◈ Command Matrix

- `play song on youtube`
- `search: query`
- `open: app or url`
- `read: filepath`
- `write: path | content`
- `run: terminal command`
- `sysinfo`
- `screenshot`
- `generate image: prompt` 🎨
""")
            gr.HTML("<div style='margin-top:20px;'></div>")
            clear_btn = gr.Button("⬛ CLEAR MEMORY", variant="stop", size="sm")

            gr.HTML("""
            <div style='margin-top:24px; padding:12px;
                        border:1px solid rgba(0,245,255,0.15); border-radius:2px;
                        font-family:"Share Tech Mono",monospace; font-size:0.62rem;
                        color:rgba(0,245,255,0.35); letter-spacing:0.08em; line-height:2;'>
                <div>SYS.VERSION · 3.1.0</div>
                <div>ENGINE · GROQ/LLAMA</div>
                <div>STT · GOOGLE+WHISPER</div>
                <div>TTS · PYTTSX3/ZIRA</div>
                <div>IMAGE · FLUX API</div>
                <div>STATUS · OPERATIONAL</div>
            </div>
            """)

    def handle_chat(user_message, history):
        new_input, new_history = chat(user_message, history)
        return new_input, new_history, render_chat(new_history)

    def handle_voice(history):
        new_input, new_history = voice_input_fn(history)
        return new_input, new_history, render_chat(new_history)

    def handle_clear():
        history = clear_chat()
        return history, render_chat(history)

    send_btn.click(fn=handle_chat, inputs=[msg_input, chat_state],
                   outputs=[msg_input, chat_state, chat_html])
    msg_input.submit(fn=handle_chat, inputs=[msg_input, chat_state],
                     outputs=[msg_input, chat_state, chat_html])
    voice_btn.click(fn=handle_voice, inputs=[chat_state],
                    outputs=[msg_input, chat_state, chat_html])
    clear_btn.click(fn=handle_clear, inputs=[], outputs=[chat_state, chat_html])


if __name__ == "__main__":
    print("\n" + "═" * 52)
    print("  J.A.R.V.I.S — Image Generation Edition")
    print("  Open: http://localhost:7860")
    print("═" * 52 + "\n")
    app.launch(server_name="0.0.0.0", server_port=7860, show_error=True)
