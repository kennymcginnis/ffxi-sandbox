"""
FFXI Contextual Translation Bridge (Community Edition)
Version: 2.0.0
"""

import sys
import os
import socket
import json
import time
import threading
from collections import deque
import re
from http.server import HTTPServer, BaseHTTPRequestHandler

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QTextEdit, QDialog, QLineEdit, QFormLayout, QComboBox
)
from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtGui import QFont

from google import genai
from google.genai import types

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "translator_config.json")

DEFAULT_CONFIG = {
    "PORT": 62660,
    "WEB_PORT": 8085,
    "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", ""),
    "MODEL_NAME": "gemini-3.5-flash-lite",
    "USER_LANG": "EN"  # "EN" for English speakers, "JA" for Japanese speakers
}

TRANSLATION_SYSTEM_INSTRUCTION = """You are an elite bilingual Japanese-English localization engine embedded inside Final Fantasy XI.
Your mission is to provide instantaneous, natural, context-aware translations between Japanese and English players.
CURRENT USER PRIMARY LANGUAGE: {user_lang}

GAME CONTEXT & GLOSSARY:
- Skillchains (連携): Light (光), Darkness (闇), Distortion (湾曲), Fusion (融合), Gravitation (重力), Fragmentation (分解), Liquefaction (溶解), Impaction (衝撃), Detonation (炸裂), Compression (硬化).
- Magic Burst (MB / マジックバースト)
- Roles: Tank/Shield (盾 / ナ / 剣), Healer (白), Puller (釣り), DPS (削り), Buffer/Support (支援 / 詩 / コ / 風).
- Tactics: Hate/Aggro (タゲ / ヘイト), Hate bounce (タゲ回し), Utsusemi (蝉 / 空蝉), AoE (範囲), Weakness (衰弱), Wipe (全滅), Reraise (リレイズ).
- Endgame Events: Sortie (ソーティ - Aminon, Objectives A-H), Odyssey (オデシー - Sheol A/B/C/Gaol, Bumba, Arebati), Dynamis-D (ダイナミスD).
- Net Slang: 'w' = lol, 'ノ' = hand raise / ready, '乙/おつ' = otsukaresama (good work), 'うす' = roger/got it.

KAOMOJI RULES:
- ONLY use standard ASCII and Shift-JIS characters: (^^;), (>_<), (*^-^*), (T_T), m(_ _)m, (^o^)/, (・ω・), (o^-')b, (´・ω・`), (*ﾉ▽ﾉ), ( ﾟдﾟ), (^-^)v
- NEVER use modern Unicode symbols like ✧, ◕, づ, ヮ, ﾉ, ⁄, ๑, ◡, ♥, ‿ as they CRASH FFXI!

TRANSLATION RULES:
1. If USER_LANG is 'EN':
   - Translate incoming Japanese to natural gaming English.
   - Translate outgoing English to polite Japanese gaming etiquette (丁寧語 / です・ます).
2. If USER_LANG is 'JA':
   - Translate incoming English to natural gaming Japanese.
   - Translate outgoing Japanese to natural, friendly English gaming terminology.
3. Preserve auto-translate brackets: Text inside 【 】 must remain matched to official terms.
4. Output clean JSON only matching the schema.

OUTPUT JSON SCHEMA:
{
    "translated_text": "Translation string",
    "tactical_alert": "Brief 2-4 word alert if urgent, else null"
}"""

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k, v in DEFAULT_CONFIG.items():
                    if k not in data:
                        data[k] = v
                return data
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()

def save_config(config_data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[-] Config Save Error: {e}")

CONFIG = load_config()
LOG_LOCK = threading.Lock()
raw_web_logs = deque(maxlen=30)
outbox_queue = deque(maxlen=50)

JP_REGEX = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF\u3000-\u303F]')

STATIC_TRANSLATION_CACHE = {
    # Japanese -> English
    "よろしくおねがいします": "Looking forward to working with you! (Greetings)",
    "よろしくお願いします": "Looking forward to working with you! (Greetings)",
    "よろしくです": "Greetings! (Polite)",
    "よろしく": "Greetings!",
    "よろ": "Greetings!",
    "よろー": "Greetings!",
    "お疲れ様でした": "Thank you for the party / Great job everyone!",
    "おつかれさまでした": "Thank you for the party / Great job everyone!",
    "おつでした": "Good work all / Thanks for party!",
    "おつー": "Good work all!",
    "おつ": "Good work!",
    "ありです": "Thank you! (Thanks for heal/buff)",
    "ありー": "Thanks!",
    "あり": "Thanks!",
    "ノ": "*Raises hand* (Ready / Invite me)",
    "ノシ": "*Waves goodbye*",
    "うす": "Understood / Roger that.",
    "すいません": "I'm sorry / My apologies.",
    "すみません": "I'm sorry / My apologies.",
    "ごめん": "Sorry!",
    "どんまい": "Don't mind / No worries!",
    "ドンマイ": "Don't mind / No worries!",
    
    # English -> Japanese
    "hello": "よろしくお願いします！",
    "hi": "よろしくです！",
    "thanks": "【ありがとう。】",
    "thank you": "ありがとうございました！",
    "sorry": "ごめんなさい！",
    "my bad": "すいませんでした！",
    "np": "どんまいです！",
    "no problem": "気にしないでください！",
    "good job": "お疲れ様でした！",
}

def clean_ffxi_bytes(raw_bytes: bytes) -> str:
    cleaned = raw_bytes.replace(b'\xfd', b'')
    try:
        return cleaned.decode('utf-8')
    except UnicodeDecodeError:
        pass
    try:
        return cleaned.decode('cp932')
    except UnicodeDecodeError:
        pass
    return cleaned.decode('utf-8', errors='replace')

def sanitize_ffxi_output(text: str) -> str:
    if not text:
        return ""
    text = text.replace('\r', ' ').replace('\n', ' ').strip()
    text = text.replace('\\', '/')
    text = text.replace('"', '”').replace("'", "’")
    
    safe_chars = []
    for char in text:
        try:
            char.encode('cp932')
            safe_chars.append(char)
        except UnicodeEncodeError:
            pass
    return "".join(safe_chars).strip()

def robust_json_decode(raw_text: str) -> dict:
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except Exception:
        pass
    match = re.search(r'"translated_text"\s*:\s*"([^"]+)"', cleaned)
    if match:
        alert_match = re.search(r'"tactical_alert"\s*:\s*"([^"]+)"', cleaned)
        return {
            "translated_text": match.group(1),
            "tactical_alert": alert_match.group(1) if alert_match else None
        }
    raise ValueError(f"Could not parse JSON from: {raw_text}")

# ==============================================================================
# WEB INSPECTOR
# ==============================================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>FFXI Translator Inspector</title>
    <style>
        body { background-color: #121212; color: #e0e0e0; font-family: 'Segoe UI', Consolas, sans-serif; margin: 20px; }
        h2 { color: #00e5ff; border-bottom: 2px solid #333; padding-bottom: 10px; }
        .card { background-color: #1e1e1e; border: 1px solid #333; border-radius: 8px; padding: 15px; margin-bottom: 15px; }
        .header { font-weight: bold; color: #00e5ff; margin-bottom: 8px; font-size: 1.1em; }
        .raw-box { background-color: #0d0d0d; color: #ffca28; padding: 10px; border-radius: 5px; font-family: Consolas, monospace; white-space: pre-wrap; word-break: break-all; }
    </style>
</head>
<body>
    <h2>🌐 FFXI Live Translation Inspector</h2>
    <p>Live stream from <code>translator_panel.py</code> on port 8085.</p>
    <div id="feed"></div>
    <script>
        async function fetchLogs() {
            try {
                let res = await fetch('/api/logs');
                let data = await res.json();
                let feed = document.getElementById('feed');
                feed.innerHTML = '';
                data.forEach(log => {
                    let card = document.createElement('div');
                    card.className = 'card';
                    card.innerHTML = `
                        <div class="header">[${log.timestamp}] ${log.character}</div>
                        <div class="raw-box">${log.raw}</div>
                    `;
                    feed.appendChild(card);
                });
            } catch(e) {}
        }
        setInterval(fetchLogs, 2000);
        fetchLogs();
    </script>
</body>
</html>
"""

class WebInspectorHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/logs":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            with LOG_LOCK:
                logs_snapshot = list(raw_web_logs)
            export_logs = [{"timestamp": item["timestamp"], "character": item["character"], "raw": item["raw"]} for item in reversed(logs_snapshot)]
            self.wfile.write(json.dumps(export_logs, ensure_ascii=False).encode('utf-8'))
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode('utf-8'))

    def log_message(self, format, *args):
        pass

def start_web_inspector():
    server = HTTPServer(("127.0.0.1", CONFIG["WEB_PORT"]), WebInspectorHandler)
    server.serve_forever()

# ==============================================================================
# SETTINGS MODAL
# ==============================================================================
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Translator Configuration")
        self.setFixedSize(500, 300)
        self.setStyleSheet("""
            QDialog { background-color: #1A1A22; color: #E0E0E0; font-family: Consolas; }
            QLabel { color: #00E5FF; font-weight: bold; font-size: 11px; }
            QLineEdit, QComboBox { 
                background-color: #0D0D12; 
                color: #FFCA28; 
                border: 1px solid #333344; 
                border-radius: 4px; 
                padding: 6px; 
            }
            QPushButton { background-color: #007ACC; color: white; border: none; border-radius: 4px; font-weight: bold; padding: 8px; }
            QPushButton:hover { background-color: #005A9E; }
        """)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English Speaker (EN -> JA)", "日本語話者 (JA -> EN)"])
        self.lang_combo.setCurrentIndex(0 if CONFIG.get("USER_LANG", "EN") == "EN" else 1)
        form.addRow(QLabel("User Primary Language:"), self.lang_combo)

        self.api_input = QLineEdit(CONFIG.get("GEMINI_API_KEY", ""))
        self.api_input.setEchoMode(QLineEdit.Password)
        form.addRow(QLabel("Gemini API Key:"), self.api_input)

        self.model_input = QLineEdit(CONFIG.get("MODEL_NAME", "gemini-2.5-flash"))
        form.addRow(QLabel("Model Name:"), self.model_input)

        self.port_input = QLineEdit(str(CONFIG.get("PORT", 62660)))
        form.addRow(QLabel("Socket Port:"), self.port_input)

        self.web_port_input = QLineEdit(str(CONFIG.get("WEB_PORT", 8085)))
        form.addRow(QLabel("Web Inspector Port:"), self.web_port_input)

        layout.addLayout(form)
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_and_close)
        layout.addWidget(save_btn)

    def save_and_close(self):
        try:
            CONFIG["USER_LANG"] = "EN" if self.lang_combo.currentIndex() == 0 else "JA"
            CONFIG["GEMINI_API_KEY"] = self.api_input.text().strip()
            CONFIG["MODEL_NAME"] = self.model_input.text().strip()
            CONFIG["PORT"] = int(self.port_input.text().strip())
            CONFIG["WEB_PORT"] = int(self.web_port_input.text().strip())
            save_config(CONFIG)
            self.accept()
        except Exception as e:
            print(f"[-] Config Error: {e}")

# ==============================================================================
# WORKER THREAD
# ==============================================================================
class TranslatorWorker(QThread):
    log_signal = Signal(str)
    lang_signal = Signal(str)

    def __init__(self):
        super().__init__()
        api_key = CONFIG.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY", "")
        self.client = genai.Client(api_key=api_key) if api_key else None

    def reload_client(self):
        api_key = CONFIG.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY", "")
        if api_key:
            self.client = genai.Client(api_key=api_key)

    def run(self):
        web_thread = threading.Thread(target=start_web_inspector, daemon=True)
        web_thread.start()
        self.log_signal.emit(f"[System] Web Inspector at http://localhost:{CONFIG['WEB_PORT']}")

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("127.0.0.1", CONFIG["PORT"]))
        server.listen(10)
        self.log_signal.emit(f"[System] Async Translator listening on Port {CONFIG['PORT']}")

        while True:
            try:
                conn, addr = server.accept()
                t = threading.Thread(target=self.handle_client, args=(conn,), daemon=True)
                t.start()
            except Exception as e:
                self.log_signal.emit(f"[-] Accept Error: {e}")

    def handle_client(self, conn):
        try:
            conn.settimeout(5.0)
            raw_bytes = conn.recv(16384)
            if not raw_bytes:
                return

            data_raw = clean_ffxi_bytes(raw_bytes).strip()
            payload = json.loads(data_raw)
            p_type = payload.get("type", "TRANSLATE_MESSAGE")

            # 1. Mode / Language Swap Sync from Lua
            if p_type == "LANG_SWAP":
                CONFIG["USER_LANG"] = payload.get("user_lang", "EN")
                save_config(CONFIG)
                self.lang_signal.emit(CONFIG["USER_LANG"])
                self.log_signal.emit(f"[Language Sync] Mode swapped to: {CONFIG['USER_LANG']}")
                conn.sendall(b'{"status":"OK"}\n')
                return

            # 2. Outbox Polling
            if p_type in ("POLL_OUTBOX", "UNIFIED_POLL"):
                ready_items = []
                with LOG_LOCK:
                    while outbox_queue:
                        ready_items.append(outbox_queue.popleft())

                response_key = "translations" if p_type == "UNIFIED_POLL" else "items"
                response = {
                    response_key: ready_items,
                    "user_lang": CONFIG.get("USER_LANG", "EN")
                }
                resp_bytes = json.dumps(response, ensure_ascii=False).encode('utf-8') + b"\n"
                conn.sendall(resp_bytes)
                return

            if p_type in ("TRUST_SYNC", "TRUST_FULL_STATUS", "LOCK_SCREEN"):
                conn.sendall(b'{"status":"IGNORED"}\n')
                return

            # 3. Translate Request
            direction = payload.get("direction", "INCOMING")
            raw_msg = payload.get("message", "").strip()
            sender = payload.get("sender", "Unknown")
            chan = payload.get("channel", "party")
            tell_target = payload.get("tell_target", "")
            user_lang = CONFIG.get("USER_LANG", "EN")

            # Static Cache Check
            cached = STATIC_TRANSLATION_CACHE.get(raw_msg) or STATIC_TRANSLATION_CACHE.get(raw_msg.lower())
            if cached:
                with LOG_LOCK:
                    outbox_queue.append({
                        "direction": direction,
                        "sender": sender,
                        "channel": chan,
                        "tell_target": tell_target,
                        "translated_text": cached,
                        "tactical_alert": None
                    })
                conn.sendall(b'{"status":"QUEUED_CACHED"}\n')
                self.log_signal.emit(f"[Cache Hit] '{raw_msg}' -> '{cached}'")
                return

            # Filter check:
            # If EN User: Ignore incoming English.
            # If JA User: Ignore incoming Japanese.
            has_jp = bool(JP_REGEX.search(raw_msg))
            if direction == "INCOMING":
                if user_lang == "EN" and not has_jp:
                    conn.sendall(b'{"status":"IGNORED"}\n')
                    return
                elif user_lang == "JA" and has_jp:
                    conn.sendall(b'{"status":"IGNORED"}\n')
                    return

            conn.sendall(b'{"status":"QUEUED_ASYNC"}\n')

            def async_gemini_task():
                if not self.client:
                    self.reload_client()
                if not self.client:
                    self.log_signal.emit("[-] API Key Missing.")
                    return

                system_instruction = TRANSLATION_SYSTEM_INSTRUCTION.replace("{user_lang}", user_lang)

                ctx_prompt = (
                    f"User Language: {user_lang}\n"
                    f"Direction: {direction}\n"
                    f"Zone: {payload.get('zone', 'Unknown')}\n"
                    f"Target Mob: {payload.get('target', 'None')}\n"
                    f"Party Comp: {', '.join(payload.get('party_jobs', []))}\n"
                    f"Channel: {chan}\n"
                    f"Original Message from [{sender}]: \"{raw_msg}\""
                )

                try:
                    response = self.client.models.generate_content(
                        model=CONFIG["MODEL_NAME"],
                        contents=ctx_prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            system_instruction=system_instruction,
                            temperature=0.1
                        )
                    )

                    ai_json = robust_json_decode(response.text)
                    trans_text = sanitize_ffxi_output(ai_json.get("translated_text", ""))

                    if trans_text:
                        with LOG_LOCK:
                            outbox_queue.append({
                                "direction": direction,
                                "sender": sender,
                                "channel": chan,
                                "tell_target": tell_target,
                                "translated_text": trans_text,
                                "tactical_alert": ai_json.get("tactical_alert", None)
                            })
                            raw_web_logs.append({
                                "timestamp": time.strftime("%H:%M:%S"),
                                "character": f"{direction} ({chan})",
                                "raw": f"Original: {raw_msg}\nTranslated: {trans_text}\nAlert: {ai_json.get('tactical_alert')}"
                            })
                        self.log_signal.emit(f"[AI Localizer] [{direction}] '{raw_msg}' -> '{trans_text}'")

                except Exception as ai_e:
                    self.log_signal.emit(f"[-] AI Error: {ai_e}")

            threading.Thread(target=async_gemini_task, daemon=True).start()

        except Exception as e:
            self.log_signal.emit(f"[-] Socket Error: {e}")
        finally:
            conn.close()

# ==============================================================================
# GUI
# ==============================================================================
class StandaloneGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FFXI Gemini Live Translator")
        self.setFixedSize(620, 380)
        self.setStyleSheet("""
            QMainWindow { background-color: #121212; }
            QLabel { color: #00E5FF; font-family: Consolas; font-weight: bold; }
            QTextEdit { background-color: #1A1A1A; color: #00E5FF; font-family: Consolas; font-size: 11px; border: 1px solid #333333; border-radius: 6px; }
            QPushButton { background-color: #2A2A2A; color: #FFFFFF; border: 1px solid #444444; border-radius: 4px; font-family: Consolas; font-weight: bold; padding: 6px 12px; }
            QPushButton:hover { background-color: #3A3A3A; }
        """)

        central = QWidget(self)
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        top_bar = QHBoxLayout()
        title = QLabel("🌐 FFXI ASYNC TRANSLATOR")
        title.setFont(QFont("Consolas", 11, QFont.Bold))
        top_bar.addWidget(title)
        top_bar.addStretch()

        self.lang_btn = QPushButton("Mode: EN -> JA")
        self.lang_btn.clicked.connect(self.toggle_language)
        top_bar.addWidget(self.lang_btn)

        settings_btn = QPushButton("⚙ Settings")
        settings_btn.clicked.connect(self.open_settings)
        top_bar.addWidget(settings_btn)
        layout.addLayout(top_bar)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box)

        self.worker = TranslatorWorker()
        self.worker.log_signal.connect(self.log)
        self.worker.lang_signal.connect(self.update_lang_btn)
        self.worker.start()

        self.update_lang_btn(CONFIG.get("USER_LANG", "EN"))

    def toggle_language(self):
        new_lang = "JA" if CONFIG.get("USER_LANG", "EN") == "EN" else "EN"
        CONFIG["USER_LANG"] = new_lang
        save_config(CONFIG)
        self.update_lang_btn(new_lang)
        self.log(f"[Mode] Language switched to: {new_lang}")

    def update_lang_btn(self, lang):
        if lang == "EN":
            self.lang_btn.setText("Mode: EN -> JA (English User)")
            self.lang_btn.setStyleSheet("background-color: #007ACC; color: white; border: 1px solid #005A9E;")
        else:
            self.lang_btn.setText("Mode: JA -> EN (日本語話者)")
            self.lang_btn.setStyleSheet("background-color: #28A745; color: white; border: 1px solid #1E7E34;")

    def open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec():
            self.worker.reload_client()
            self.update_lang_btn(CONFIG.get("USER_LANG", "EN"))
            self.log("[Settings] Settings saved.")

    @Slot(str)
    def log(self, text):
        timestamp = time.strftime("[%H:%M:%S]")
        self.log_box.append(f"{timestamp} {text}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = StandaloneGUI()
    gui.show()
    sys.exit(app.exec())