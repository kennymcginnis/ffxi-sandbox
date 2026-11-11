"""
FFXI Unified Tactical Switchboard & Contextual Translator
Version: 9.1 Universal
Authors: Gemini / Taylormade (Jim & I)
"""

import sys
import os
import socket
import json
import time
import threading
import subprocess
import re
import ctypes
from collections import deque
import win32gui
import win32con
import win32process
import win32api
from http.server import HTTPServer, BaseHTTPRequestHandler
import tkinter as tk
from ctypes import wintypes

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QTextEdit, QDialog, QTabWidget, QLineEdit, 
    QFormLayout, QFrame, QScrollArea, QGridLayout, QComboBox
)
from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtGui import QFont

from google import genai
from google.genai import types

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

STANDARD_MODES = {
    "AutoBuffMode": ["Off", "Auto"],
    "AutoHealMode": ["Off", "Auto", "Emergency"],
    "AutoSongMode": ["Off", "Auto", "Dummy"],
    "AutoStatusRemovalMode": ["Off", "Auto"],
    "AutoEngageMode": ["Off", "Always", "Mirror"],
    "AutoSkillchainMode": ["Off", "Auto", "Cleave", "Spam"],
    "AutoFollowMode": ["Off", "Always", "Path"],
    "AutoCampMode": ["Off", "Auto"],
    "AutoPullMode": ["Off", "Auto", "Aggroed", "All"],
    "CombatMode": ["Off", "Auto", "Mirror"],
    "FlankMode": ["Off", "Back", "Left", "Right"]
}

DEFAULT_CONFIG = {
    "PANEL_PORT": 62650,
    "WEB_PORT": 8080,
    "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", ""),
    "MODEL_NAME": "gemini-2.5-flash",
    "USER_LANG": "EN",
    "LOCK_PASSWORD": "password123",
    "LOCK_OPACITY": 0.20,
    "LEADER_NAME": "Taylormade",
    "CHARACTERS": ["Taylormade", "Socoxak"], # , "Oletole"
    "SE_PASSWORD": "",
    "POL_INITIAL_DELAY": 12.0,
    "POL_ACCOUNTS": {"Taylormade": 1, "Socoxak": 2}, # , "Oletole": 3
    "WINDOWER_PATH": r"C:\Program Files (x86)\Windower\Windower.exe",
    "WINDOWER_PROFILES": {"Taylormade": "Taylormade", "Socoxak": "Socoxak"}, # , "Oletole": "Oletole"
    "MAIN_TV_POS": {"x": -1920, "y": 0, "width": 1920, "height": 1080},
    "SLOTS": {
        "Taylormade": {"x": 1920, "y": 0, "width": 1920, "height": 1080},
        "Socoxak": {"x": 0, "y": 0, "width": 1920, "height": 1080},
        # "Oletole": {"x": 1720, "y": 960, "width": 840, "height": 470},
    },
    "TRUST_MODES": {
        "Taylormade": {"AutoBuffMode": "Off", "AutoHealMode": "Off", "AutoStatusRemovalMode": "Off", "AutoEngageMode": "Off", "AutoSkillchainMode": "Off", "AutoFollowMode": "Always", "AutoCampMode": "Off", "AutoPullMode": "Off", "CombatMode": "Off", "FlankMode": "Off"},
        "Socoxak": {"AutoBuffMode": "Auto", "AutoHealMode": "Auto", "AutoStatusRemovalMode": "Auto", "AutoEngageMode": "Always", "AutoSkillchainMode": "Off", "AutoFollowMode": "Always", "AutoCampMode": "Off", "AutoPullMode": "Off", "CombatMode": "Auto", "FlankMode": "Off"},
        # "Oletole": {"AutoBuffMode": "Auto", "AutoHealMode": "Off", "AutoStatusRemovalMode": "Off", "AutoEngageMode": "Always", "AutoSkillchainMode": "Auto", "AutoFollowMode": "Always", "AutoCampMode": "Off", "AutoPullMode": "Off", "CombatMode": "Auto", "FlankMode": "Off"}
    }
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

KAOMOJI & EMOJI RULES:
- NEVER use ASCII semicolons (;) in kaomoji. ALWAYS use full-width （；） to prevent command truncation.
- NEVER use modern Unicode symbols like ✧, ◕, づ, ヮ, ⁄, ๑, ◡, ♥, ‿, ╯, ︵, ┻, ━ as they CRASH FFXI!
- Select diverse, context-appropriate kaomoji matching the player's emotion from these CP932-safe sets:
  * Polite / Apology / Gratitude: m(_ _)m, m(__)m
  * Happy / Cheers / Celebrating: (^o^)/, (*'▽')/, (^-^)v
  * Chill / Relaxed / Agreement: (´ー｀), ヽ(´ー｀)ノ, (￣ー￣)
  * Thumbs up / Nice job: (o^-')b, d(^-^)b
  * Sweat / Oops / Embarrassed: (^^；), (；・∀・), (*ﾉ▽ﾉ)
  * Surprised / Shocked: Σ(゜д゜;), ( ﾟдﾟ), (゜Д゜)
  * Sad / Frustrated / Wipe: (T_T), (>_<), (ノДT)
  * Table Flip / Rage / Disbelief: (ノ｀Д´)ノ彡┴─┴, (ノ゜Д゜)ノ ┴─┴
  * Table Reset / Calming Down: ┬─┬ ノ( ゜-゜ノ), ┬─┬ ノ(・_・ノ)
  * Playful / Cute: (*^-^*), (・ω・), (=^・^=)
- Do NOT force a kaomoji into every single sentence; only use them when the tone is friendly, emotional, or playful.
- If an incoming message is translated and contains kaomoji, include it. If it doesn't have any kaomoji/emoji, don't add it.

EXPLICIT EMOJI SHORTCODES:
If the user types any of these shortcodes, place the exact corresponding CP932 kaomoji at that position in the translation:
- :flip:   -> (ノ｀Д´)ノ彡┴─┴
- :unflip: -> ┬─┬ ノ( ゜-゜ノ)
- :bow:    -> m(_ _)m
- :sweat:  -> (^^；)
- :shock:  -> Σ(゜д゜；)
- :cheer:  -> (^o^)/
- :thumbs: -> (o^-')b
- :wipe:   -> (T_T)

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

STATIC_TRANSLATION_CACHE = {
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

KAOMOJI_SHORTCODES = {
    ":flip:": "(ノ｀Д´)ノ彡┴─┴",
    ":unflip:": "┬─┬ ノ( ゜-゜ノ)",
    ":bow:": "m(_ _)m",
    ":sweat:": "(^^；)",
    ":shock:": "Σ(゜д゜;)",
    ":cheer:": "(^o^)/",
    ":thumbs:": "(o^-')b",
    ":wipe:": "(T_T)",
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k, v in DEFAULT_CONFIG.items():
                    if k not in data: data[k] = v
                return data
        except Exception: pass
    return DEFAULT_CONFIG.copy()

def save_config(config_data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[-] Config Save Error: {e}")

CONFIG = load_config()
CHARACTERS = CONFIG.get("CHARACTERS", ["Taylormade", "Socoxak"]) # , "Oletole"
current_active_index = 0

LOG_LOCK = threading.Lock()
raw_web_logs = deque(maxlen=50)

# Per-Character Outbox Queues (Eliminates the "Crap Shoot" Race Condition)
character_trans_outboxes = {c: deque(maxlen=30) for c in CHARACTERS}

JP_REGEX = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF\u3000-\u303F]')

def clean_ffxi_bytes(raw_bytes: bytes) -> str:
    cleaned = raw_bytes.replace(b'\xfd', b'')
    try: return cleaned.decode('utf-8')
    except UnicodeDecodeError: pass
    try: return cleaned.decode('cp932')
    except UnicodeDecodeError: pass
    return cleaned.decode('utf-8', errors='replace')

def sanitize_ffxi_output(text: str) -> str:
    if not text: return ""
    text = text.replace('\r', ' ').replace('\n', ' ').strip()
    text = text.replace('\\', '/')
    text = text.replace('"', '”').replace("'", "’")
    text = text.replace(';', '；')

    for code, kaomoji in KAOMOJI_SHORTCODES.items():
        text = text.replace(code, kaomoji)

    safe_chars = []
    for char in text:
        try:
            char.encode('cp932')
            safe_chars.append(char)
        except UnicodeEncodeError:
            pass
    return "".join(safe_chars).strip()

def fix_json_escapes(raw_text: str) -> str:
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = cleaned.replace(r"\'", "'")
    cleaned = cleaned.replace(r"\/", "/")
    cleaned = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', cleaned)
    return cleaned

def safe_json_loads(raw_bytes: bytes) -> dict:
    text = clean_ffxi_bytes(raw_bytes).strip()
    try:
        return json.loads(text)
    except Exception:
        fixed_text = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', text)
        return json.loads(fixed_text)

def robust_json_decode(raw_text: str) -> dict:
    cleaned = fix_json_escapes(raw_text)
    try: return json.loads(cleaned)
    except Exception: pass
    match = re.search(r'"translated_text"\s*:\s*"([^"]+)"', cleaned)
    if match:
        alert_match = re.search(r'"tactical_alert"\s*:\s*"([^"]+)"', cleaned)
        return {
            "translated_text": match.group(1),
            "tactical_alert": alert_match.group(1) if alert_match else None
        }
    raise ValueError(f"Could not parse JSON from: {raw_text}")

# ==============================================================================
# MULTI-MONITOR TRANSPARENT SCREEN LOCK (CRASH-PROOF)
# ==============================================================================
def get_all_monitors():
    try: ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try: ctypes.windll.user32.SetProcessDPIAware()
        except Exception: pass

    monitors = []
    def _callback(hMon, hDC, lprc, lData):
        r = lprc.contents
        monitors.append((r.left, r.top, r.right - r.left, r.bottom - r.top))
        return 1

    CALLBACK = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HMONITOR, wintypes.HDC, ctypes.POINTER(wintypes.RECT), wintypes.LPARAM)
    ctypes.windll.user32.EnumDisplayMonitors(None, None, CALLBACK(_callback), 0)

    if not monitors:
        u = ctypes.windll.user32
        monitors.append((u.GetSystemMetrics(76), u.GetSystemMetrics(77), u.GetSystemMetrics(78), u.GetSystemMetrics(79)))
    return monitors

class EasyScreenLock:
    def __init__(self, password=None, opacity=None):
        self.password = password or CONFIG.get("LOCK_PASSWORD", "password123")
        self.opacity = opacity or float(CONFIG.get("LOCK_OPACITY", 0.20))
        self.windows = []
        self.root = None
        self.entry = None
        self.last_esc_time = 0

    def start(self):
        monitors = get_all_monitors()
        self.root = tk.Tk()
        self.windows.append(self.root)

        mx, my, mw, mh = monitors[0]
        self._style_window(self.root, mx, my, mw, mh)
        self._build_center_box(self.root)

        for x, y, w, h in monitors[1:]:
            shield = tk.Toplevel(self.root)
            self.windows.append(shield)
            self._style_window(shield, x, y, w, h)

        self.root.lift()
        self.entry.focus_force()
        self.root.mainloop()

    def _style_window(self, win, x, y, w, h):
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.attributes("-alpha", self.opacity)
        win.config(bg="black")
        win.geometry(f"{w}x{h}+{x}+{y}")
        win.bind("<Button-1>", lambda e: self.entry.focus_force())

    def _build_center_box(self, parent):
        box = tk.Frame(parent, bg="#1a1a1a", bd=2, relief="ridge", padx=25, pady=20)
        box.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(box, text="🔒 SCREEN LOCKED", font=("Consolas", 12, "bold"), fg="#00FF66", bg="#1a1a1a").pack(pady=(0, 8))

        self.entry = tk.Entry(box, show="*", font=("Consolas", 12), justify="center", width=18)
        self.entry.pack(pady=5)
        self.entry.bind("<Return>", self._verify)
        self.entry.bind("<Escape>", self._on_escape)

        self.hint = tk.Label(box, text="Type password & press Enter", font=("Consolas", 8), fg="#999999", bg="#1a1a1a")
        self.hint.pack(pady=(5, 0))

    def _verify(self, event=None):
        if self.entry.get() == self.password:
            self.root.destroy()
        else:
            self.entry.delete(0, tk.END)
            self.hint.config(text="Wrong password! Try again.", fg="#ff5555")

    def _on_escape(self, event):
        now = time.time()
        if now - self.last_esc_time < 0.5:
            self.root.destroy()
        else:
            self.last_esc_time = now
            self.entry.delete(0, tk.END)

def launch_lock_screen():
    threading.Thread(target=lambda: EasyScreenLock().start(), daemon=True).start()

# ==============================================================================
# WINDOW POSITIONING & LAYOUT (GHOST-PROOF)
# ==============================================================================
character_hwnds = {}
last_known_slots = {}

def find_running_windows():
    global character_hwnds
    temp_hwnds = {}

    def _enum_cb(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if not title: return
            title_lower = title.lower()

            # Filter out browsers, IDEs, Explorer, and Discord to avoid false active states
            excluded_apps = ["notepad", "sublime", "code", "chrome", "firefox", "edge", "cmd", "python", "explorer", "powershell", "discord"]
            if any(app in title_lower for app in excluded_apps): return

            for char in CONFIG.get("CHARACTERS", CHARACTERS):
                if char.lower() in title_lower:
                    temp_hwnds[char] = hwnd

    win32gui.EnumWindows(_enum_cb, None)
    character_hwnds = temp_hwnds
    return character_hwnds

def force_foreground_window(hwnd):
    if not hwnd or not win32gui.IsWindow(hwnd): return
    if win32gui.IsIconic(hwnd): win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    fg_hwnd = win32gui.GetForegroundWindow()
    if fg_hwnd == hwnd: return

    fg_thread, _ = win32process.GetWindowThreadProcessId(fg_hwnd)
    target_thread, _ = win32process.GetWindowThreadProcessId(hwnd)
    curr_thread = win32api.GetCurrentThreadId()

    try:
        if fg_thread != curr_thread: win32process.AttachThreadInput(curr_thread, fg_thread, True)
        if target_thread != curr_thread: win32process.AttachThreadInput(curr_thread, target_thread, True)
        win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_EXTENDEDKEY | 0, 0)
        win32gui.SetForegroundWindow(hwnd)
        win32gui.BringWindowToTop(hwnd)
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
        win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_EXTENDEDKEY | win32con.KEYEVENTF_KEYUP, 0)
    except Exception:
        try: win32gui.SetForegroundWindow(hwnd)
        except Exception: pass
    finally:
        try:
            if fg_thread != curr_thread: win32process.AttachThreadInput(curr_thread, fg_thread, False)
            if target_thread != curr_thread: win32process.AttachThreadInput(curr_thread, target_thread, False)
        except Exception: pass

def make_window_borderless(hwnd):
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    frame_styles = win32con.WS_CAPTION | win32con.WS_THICKFRAME | win32con.WS_BORDER | win32con.WS_DLGFRAME
    if style & frame_styles:
        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style & ~frame_styles)
        win32gui.SetWindowPos(
            hwnd,
            0,
            0,
            0,
            0,
            0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOZORDER
            | win32con.SWP_NOACTIVATE | win32con.SWP_FRAMECHANGED,
        )

def apply_layout(active_char_name, gui_hwnd):
    global last_known_slots
    find_running_windows()
    main_pos = CONFIG.get("MAIN_TV_POS", {"x": 268, "y": -1080, "width": 1920, "height": 1080})
    slots = CONFIG.get("SLOTS", DEFAULT_CONFIG["SLOTS"])

    for char in CONFIG.get("CHARACTERS", CHARACTERS):
        if char.lower() != active_char_name.lower():
            hwnd = character_hwnds.get(char)
            if hwnd and win32gui.IsWindow(hwnd):
                pos = slots.get(char, {"x": 1720, "y": 0, "width": 840, "height": 470})
                current_state = (hwnd, pos["x"], pos["y"], pos["width"], pos["height"], "IDLE")
                make_window_borderless(hwnd)
                if last_known_slots.get(char) != current_state:
                    try:
                        win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, pos["x"], pos["y"], pos["width"], pos["height"], win32con.SWP_SHOWWINDOW | win32con.SWP_NOACTIVATE | win32con.SWP_NOZORDER | win32con.SWP_NOCOPYBITS)
                        last_known_slots[char] = current_state
                    except Exception: pass

    vacant_pos = slots.get(active_char_name, {"x": 1720, "y": 0, "width": 840, "height": 470})
    if gui_hwnd and win32gui.IsWindow(gui_hwnd):
        gui_state = (gui_hwnd, vacant_pos["x"], vacant_pos["y"], vacant_pos["width"], vacant_pos["height"])
        if last_known_slots.get("GUI") != gui_state:
            try:
                win32gui.SetWindowPos(gui_hwnd, win32con.HWND_NOTOPMOST, vacant_pos["x"], vacant_pos["y"], vacant_pos["width"], vacant_pos["height"], win32con.SWP_SHOWWINDOW | win32con.SWP_NOACTIVATE | win32con.SWP_NOZORDER)
                last_known_slots["GUI"] = gui_state
            except Exception: pass

    active_hwnd = character_hwnds.get(active_char_name)
    if active_hwnd and win32gui.IsWindow(active_hwnd):
        active_state = (active_hwnd, main_pos["x"], main_pos["y"], main_pos["width"], main_pos["height"], "ACTIVE")
        make_window_borderless(active_hwnd)
        if last_known_slots.get(active_char_name) != active_state:
            try:
                win32gui.SetWindowPos(active_hwnd, win32con.HWND_TOP, main_pos["x"], main_pos["y"], main_pos["width"], main_pos["height"], win32con.SWP_SHOWWINDOW)
                force_foreground_window(active_hwnd)
                last_known_slots[active_char_name] = active_state
            except Exception:
                win32gui.ShowWindow(active_hwnd, win32con.SW_RESTORE)

# ==============================================================================
# CALIBRATED POL AUTO-LOGIN ENGINE
# ==============================================================================
def set_hardware_input_blocked(block: bool):
    try: ctypes.windll.user32.BlockInput(block)
    except Exception: pass

def send_keypress(vk_code, delay=0.15):
    win32api.keybd_event(vk_code, 0, 0, 0)
    time.sleep(delay)
    win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(delay)

def type_text(text, per_char_delay=0.06):
    for char in text:
        vk = win32api.VkKeyScan(char)
        shift = (vk >> 8) & 1
        vk_code = vk & 0xFF
        if shift:
            win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
            time.sleep(0.03)
        win32api.keybd_event(vk_code, 0, 0, 0)
        time.sleep(per_char_delay)
        win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
        if shift:
            time.sleep(0.03)
            win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(per_char_delay)

def find_pol_window():
    found_hwnd = []
    def enum_pol(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "playonline" in title.lower() or "pol.exe" in title.lower():
                found_hwnd.append(hwnd)
    win32gui.EnumWindows(enum_pol, None)
    return found_hwnd[0] if found_hwnd else None

def click_and_park_cursor(hwnd, client_x, client_y):
    rect = win32gui.GetClientRect(hwnd)
    w = rect[2] - rect[0]
    h = rect[3] - rect[1]
    scaled_x = int(client_x * (w / 640.0)) if w > 0 else client_x
    scaled_y = int(client_y * (h / 480.0)) if h > 0 else client_y

    pt = win32gui.ClientToScreen(hwnd, (scaled_x, scaled_y))
    win32api.SetCursorPos(pt)
    time.sleep(0.12)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.12)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.20)

    neutral_pt = win32gui.ClientToScreen(hwnd, (0, 0))
    win32api.SetCursorPos(neutral_pt)
    time.sleep(0.10)

def click_pol_account_slot(pol_hwnd, slot_num=1):
    slot_idx = max(1, min(4, slot_num))
    target_x = 410
    target_y = 130 + (slot_idx - 1) * 60
    click_and_park_cursor(pol_hwnd, target_x, target_y)

def launch_character_process(char_name, auto_type_pwd=True, log_callback=None):
    windower_exe = CONFIG.get("WINDOWER_PATH", r"C:\Program Files (x86)\Windower\Windower.exe")
    profiles = CONFIG.get("WINDOWER_PROFILES", {})
    profile_name = profiles.get(char_name, char_name).strip()

    if not os.path.exists(windower_exe):
        if log_callback: log_callback(f"[-] Windower.exe not found at '{windower_exe}'")
        return False

    windower_dir = os.path.dirname(os.path.abspath(windower_exe))
    cmd = [windower_exe]
    if profile_name and profile_name.lower() not in ["", "none", "default"]:
        cmd.extend(["-p", profile_name])

    try:
        subprocess.Popen(cmd, cwd=windower_dir)
        if log_callback: log_callback(f"[Launcher] Launched Windower profile '{profile_name}'")
    except Exception as e:
        if log_callback: log_callback(f"[-] Launch Error for {char_name}: {e}")
        return False

    if auto_type_pwd:
        threading.Thread(target=auto_login_pol_sequence, args=(char_name, log_callback), daemon=True).start()
    return True

def auto_login_pol_sequence(char_name, log_callback=None):
    if log_callback: log_callback(f"[Auto-Login] Waiting for PlayOnline window for '{char_name}'...")
    
    pol_hwnd = None
    for _ in range(60):
        time.sleep(0.5)
        pol_hwnd = find_pol_window()
        if pol_hwnd: break

    if not pol_hwnd:
        if log_callback: log_callback("[-] POL window timeout. Skipping keystrokes.")
        return

    initial_delay = float(CONFIG.get("POL_INITIAL_DELAY", 12.0))
    if log_callback: log_callback(f"[Auto-Login] POL detected! Waiting {initial_delay:.1f}s for POL fade-in...")
    time.sleep(initial_delay)
    
    force_foreground_window(pol_hwnd)
    time.sleep(1.5)

    set_hardware_input_blocked(True)
    try:
        account_slot = CONFIG.get("POL_ACCOUNTS", {}).get(char_name, 1)
        click_pol_account_slot(pol_hwnd, account_slot)
        if log_callback: log_callback(f"[Auto-Login] Selected Account Slot #{account_slot} & parked mouse.")
        time.sleep(1.5)

        send_keypress(win32con.VK_RETURN)
        time.sleep(1.5)

        send_keypress(win32con.VK_RETURN)
        time.sleep(1.8)

        send_keypress(win32con.VK_RETURN)
        time.sleep(1.2)

        se_pwd = CONFIG.get("SE_PASSWORD", "").strip()
        if se_pwd:
            type_text(se_pwd)
            time.sleep(0.8)
            send_keypress(win32con.VK_RETURN)
            time.sleep(0.8)
            send_keypress(win32con.VK_TAB)
            time.sleep(0.4)
            send_keypress(win32con.VK_TAB)
            time.sleep(0.4)
            send_keypress(win32con.VK_RETURN)
            if log_callback: log_callback("[Auto-Login] Submitted SE password & executed login!")
        else:
            send_keypress(win32con.VK_RETURN)
            time.sleep(0.8)
            send_keypress(win32con.VK_TAB)
            time.sleep(0.4)
            send_keypress(win32con.VK_TAB)
            time.sleep(0.4)
            send_keypress(win32con.VK_RETURN)
    finally:
        set_hardware_input_blocked(False)

    if log_callback: log_callback("[Auto-Login] POL credentials passed. Waiting for Character Select...")

    # Wait up to 50s for character screen
    for _ in range(50):
        time.sleep(1.0)
        hwnds = find_running_windows()
        if char_name in hwnds:
            time.sleep(5.0)
            send_keypress(win32con.VK_RETURN)
            time.sleep(2.5)
            send_keypress(win32con.VK_RETURN)
            time.sleep(2.5)
            send_keypress(win32con.VK_RETURN)
            if log_callback: log_callback(f"[Auto-Login] Logged in '{char_name}'!")
            break

# ==============================================================================
# WEB INSPECTOR
# ==============================================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>FFXI Tactical & Translation Live Stream</title>
    <style>
        body { background-color: #121212; color: #e0e0e0; font-family: 'Segoe UI', Consolas, sans-serif; margin: 20px; }
        h2 { color: #00e5ff; border-bottom: 2px solid #333; padding-bottom: 10px; }
        .card { background-color: #1e1e1e; border: 1px solid #333; border-radius: 8px; padding: 15px; margin-bottom: 15px; }
        .header { font-weight: bold; color: #00e5ff; margin-bottom: 8px; font-size: 1.1em; }
        .raw-box { background-color: #0d0d0d; color: #ffca28; padding: 10px; border-radius: 5px; font-family: Consolas, monospace; white-space: pre-wrap; word-break: break-all; }
    </style>
</head>
<body>
    <h2>⚡ FFXI Unified Command & Translation Inspector</h2>
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
                    card.innerHTML = `<div class="header">[${log.timestamp}] ${log.tag}</div><div class="raw-box">${log.raw}</div>`;
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

class UnifiedWebHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/logs":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            with LOG_LOCK: logs_snapshot = list(raw_web_logs)
            export_logs = [{"timestamp": i["timestamp"], "tag": i["tag"], "raw": i["raw"]} for i in reversed(logs_snapshot)]
            self.wfile.write(json.dumps(export_logs, ensure_ascii=False).encode('utf-8'))
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode('utf-8'))
    def log_message(self, format, *args): pass

def start_unified_web_server():
    server = HTTPServer(("127.0.0.1", CONFIG.get("WEB_PORT", 8080)), UnifiedWebHandler)
    server.serve_forever()

# ==============================================================================
# UNIFIED WORKER: SINGLE PORT (62650)
# ==============================================================================
class UnifiedWorker(QThread):
    log_signal = Signal(str)
    mode_signal = Signal(str)
    cycle_signal = Signal(str)
    trust_sync_signal = Signal(str, str, str)
    assist_sync_signal = Signal(str, str)
    trans_lang_signal = Signal(str)

    def __init__(self):
        super().__init__()
        api_key = CONFIG.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY", "")
        self.gemini_client = genai.Client(api_key=api_key) if api_key else None
        self.command_queues = {c: [] for c in CONFIG.get("CHARACTERS", CHARACTERS)}
        self.force_query_flags = {c: False for c in CONFIG.get("CHARACTERS", CHARACTERS)}
        self.current_hud_mode = "Normal"

    def reload_gemini(self):
        api_key = CONFIG.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY", "")
        if api_key: self.gemini_client = genai.Client(api_key=api_key)

    def run(self):
        threading.Thread(target=start_unified_web_server, daemon=True).start()
        self.log_signal.emit(f"[System] Unified Web Inspector at http://localhost:{CONFIG.get('WEB_PORT', 8080)}")

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("127.0.0.1", CONFIG.get("PANEL_PORT", 62650)))
        server.listen(15)
        self.log_signal.emit(f"[System] Unified Bridge Engine listening on Port {CONFIG.get('PANEL_PORT', 62650)}")

        while True:
            try:
                conn, _ = server.accept()
                threading.Thread(target=self._handle_client, args=(conn,), daemon=True).start()
            except Exception as e:
                self.log_signal.emit(f"[-] Accept Error: {e}")

    def _handle_client(self, conn):
        try:
            conn.settimeout(3.0)
            raw_bytes = conn.recv(16384)
            if not raw_bytes: return

            payload = safe_json_loads(raw_bytes)
            p_type = payload.get("type", "")

            # 1. SCREEN LOCK TRIGGER
            if p_type == "LOCK_SCREEN":
                launch_lock_screen()
                conn.sendall(b'{"status":"LOCKED"}\n')
                return

            # 2. LANGUAGE SWAP
            if p_type == "LANG_SWAP":
                CONFIG["USER_LANG"] = payload.get("user_lang", "EN")
                save_config(CONFIG)
                self.trans_lang_signal.emit(CONFIG["USER_LANG"])
                self.log_signal.emit(f"[Translator] Mode swapped to: {CONFIG['USER_LANG']}")
                conn.sendall(b'{"status":"OK"}\n')
                return

            # 3. UNIFIED POLL
            if p_type == "UNIFIED_POLL":
                char_name = payload.get("my_name", "")
                do_query = self.force_query_flags.get(char_name, False)
                self.force_query_flags[char_name] = False

                cmds = []
                if char_name in self.command_queues and len(self.command_queues[char_name]) > 0:
                    bot_payload = self.command_queues[char_name].pop(0)
                    cmds = bot_payload.get("commands", [])
                    if cmds:
                        self.log_signal.emit(
                            f"[Bridge Debug] Sending to {char_name}: {' | '.join(cmds)}"
                        )

                trans_items = []
                with LOG_LOCK:
                    q = character_trans_outboxes.get(char_name)
                    if q:
                        while q: trans_items.append(q.popleft())

                resp_obj = {
                    "commands": cmds,
                    "translations": trans_items,
                    "sync_mode": self.current_hud_mode,
                    "user_lang": CONFIG.get("USER_LANG", "EN"),
                    "query_trust": do_query
                }
                conn.sendall(json.dumps(resp_obj, ensure_ascii=False).encode('utf-8') + b"\n")
                return

            # 4. CHAT TRANSLATION DISPATCH
            if p_type == "TRANSLATE_MESSAGE":
                direction = payload.get("direction", "INCOMING")
                raw_msg = payload.get("message", "").strip()
                sender = payload.get("sender", "Unknown")
                recipient = payload.get("recipient", sender)
                chan = payload.get("channel", "party")
                tell_target = payload.get("tell_target", "")
                user_lang = CONFIG.get("USER_LANG", "EN")

                # Static Cache Check
                cached = STATIC_TRANSLATION_CACHE.get(raw_msg) or STATIC_TRANSLATION_CACHE.get(raw_msg.lower())
                if cached:
                    with LOG_LOCK:
                        target_queue = character_trans_outboxes.get(recipient)
                        if target_queue is not None:
                            target_queue.append({
                                "direction": direction, "sender": sender, "channel": chan,
                                "tell_target": tell_target, "translated_text": cached, "tactical_alert": None
                            })
                    conn.sendall(b'{"status":"QUEUED_CACHED"}\n')
                    self.log_signal.emit(f"[Trans Hit] '{raw_msg}' -> '{cached}'")
                    return

                # Language Filter
                has_jp = bool(JP_REGEX.search(raw_msg))
                if direction == "INCOMING":
                    if (user_lang == "EN" and not has_jp) or (user_lang == "JA" and has_jp):
                        conn.sendall(b'{"status":"IGNORED"}\n')
                        return

                conn.sendall(b'{"status":"QUEUED_ASYNC"}\n')

                def async_gemini_translation():
                    if not self.gemini_client: self.reload_gemini()
                    if not self.gemini_client:
                        self.log_signal.emit("[-] Translator API Key Missing.")
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
                        response = self.gemini_client.models.generate_content(
                            model=CONFIG.get("MODEL_NAME", "gemini-2.5-flash"),
                            contents=ctx_prompt,
                            config=types.GenerateContentConfig(
                                response_mime_type="application/json",
                                system_instruction=system_instruction,
                                temperature=0.10
                            )
                        )

                        ai_json = robust_json_decode(response.text)
                        trans_text = sanitize_ffxi_output(ai_json.get("translated_text", ""))

                        if trans_text:
                            with LOG_LOCK:
                                target_queue = character_trans_outboxes.get(recipient)
                                if target_queue is not None:
                                    target_queue.append({
                                        "direction": direction,
                                        "sender": sender,
                                        "channel": chan,
                                        "tell_target": tell_target,
                                        "translated_text": trans_text,
                                        "tactical_alert": ai_json.get("tactical_alert", None)
                                    })
                                raw_web_logs.append({
                                    "timestamp": time.strftime("%H:%M:%S"),
                                    "tag": f"Translate [{direction}] {chan}",
                                    "raw": f"Original: {raw_msg}\nTranslated: {trans_text}\nAlert: {ai_json.get('tactical_alert')}"
                                })
                            self.log_signal.emit(f"[Trans] [{direction}] '{raw_msg}' -> '{trans_text}'")
                    except Exception as ai_e:
                        self.log_signal.emit(f"[-] AI Trans Error: {ai_e}")

                threading.Thread(target=async_gemini_translation, daemon=True).start()
                return

            # 5. CYCLE WINDOW
            if p_type == "CYCLE_WINDOW":
                self.cycle_signal.emit(payload.get("direction", "next"))
                conn.sendall(json.dumps({"commands":[], "reply":"", "sync_mode": self.current_hud_mode}).encode('utf-8') + b"\n")
                return

            # 6. TRUST FULL STATUS
            if p_type == "TRUST_FULL_STATUS":
                c_name = payload.get("character", "")
                raw_modes = payload.get("modes", {})
                assist_target = payload.get("assist_target", "")

                if c_name in CONFIG.get("TRUST_MODES", {}):
                    for real_mode, options in STANDARD_MODES.items():
                        if real_mode in raw_modes:
                            in_val = raw_modes[real_mode]
                            for opt in options:
                                if opt.lower() == in_val.lower():
                                    CONFIG["TRUST_MODES"][c_name][real_mode] = opt
                                    self.trust_sync_signal.emit(c_name, real_mode, opt)
                                    break
                    save_config(CONFIG)
                    if assist_target: self.assist_sync_signal.emit(c_name, assist_target)
                conn.sendall(json.dumps({"commands":[], "reply":"", "sync_mode": self.current_hud_mode}).encode('utf-8') + b"\n")
                return

            # 7. TRUST SINGLE SYNC
            if p_type == "TRUST_SYNC":
                c_name = payload.get("character", "")
                m_name = payload.get("mode_name", "")
                m_val = payload.get("mode_val", "")
                for real_mode in STANDARD_MODES.keys():
                    if real_mode.lower() == m_name.lower():
                        m_name = real_mode
                        break
                for opt in STANDARD_MODES.get(m_name, []):
                    if opt.lower() == m_val.lower():
                        m_val = opt
                        break
                if c_name in CONFIG.get("TRUST_MODES", {}) and m_name in STANDARD_MODES:
                    CONFIG["TRUST_MODES"][c_name][m_name] = m_val
                    save_config(CONFIG)
                    self.trust_sync_signal.emit(c_name, m_name, m_val)
                conn.sendall(json.dumps({"commands":[], "reply":"", "sync_mode": self.current_hud_mode}).encode('utf-8') + b"\n")
                return

            conn.sendall(json.dumps({"commands":[], "reply":"", "sync_mode": self.current_hud_mode}).encode('utf-8') + b"\n")
        except Exception as e:
            self.log_signal.emit(f"[-] Client Error: {e}")
        finally:
            conn.close()

# ==============================================================================
# SETTINGS CONFIGURATION MODAL
# ==============================================================================
class UnifiedSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("FFXI Companion Configuration")
        self.setFixedSize(760, 560)
        self.setStyleSheet("""
            QDialog { background-color: #16161E; color: #E0E0E0; font-family: Consolas; }
            QLabel { color: #00FF66; font-weight: bold; font-size: 11px; }
            QLineEdit, QTextEdit, QComboBox { background-color: #0A0A0E; color: #FFCA28; border: 1px solid #333344; border-radius: 4px; padding: 6px; }
            QPushButton { background-color: #007ACC; color: white; border: none; border-radius: 4px; font-weight: bold; padding: 8px; }
            QPushButton:hover { background-color: #005A9E; }
            QTabWidget::pane { border: 1px solid #333344; }
            QTabBar::tab { background: #22222E; color: #AAA; padding: 8px 16px; font-weight: bold; }
            QTabBar::tab:selected { background: #007ACC; color: white; }
            QScrollArea { border: none; background: transparent; }
        """)

        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        chars = CONFIG.get("CHARACTERS", CHARACTERS)
        self.inputs = {}

        # Tab 1: Layout Coordinates
        layout_tab = QWidget()
        tab1_vlayout = QVBoxLayout(layout_tab)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_grid = QGridLayout(scroll_content)

        tv_frame = QFrame()
        tv_frame.setStyleSheet("background-color: #1A1A24; border: 1px solid #282838; border-radius: 6px; padding: 4px;")
        tv_form = QFormLayout(tv_frame)
        tv_form.addRow(QLabel("=== MAIN TV MONITOR ==="), QLabel(""))
        for k in ["x", "y", "width", "height"]:
            key_name = f"TV_{k}"
            self.inputs[key_name] = QLineEdit(str(CONFIG.get("MAIN_TV_POS", {}).get(k, 0)))
            tv_form.addRow(QLabel(f"TV {k.upper()}:"), self.inputs[key_name])
        scroll_grid.addWidget(tv_frame, 0, 0)

        slots = CONFIG.get("SLOTS", {})
        col_idx, row_idx = 1, 0
        for char in chars:
            c_frame = QFrame()
            c_frame.setStyleSheet("background-color: #1A1A24; border: 1px solid #282838; border-radius: 6px; padding: 4px;")
            c_form = QFormLayout(c_frame)
            c_form.addRow(QLabel(f"=== {char.upper()} SLOT ==="), QLabel(""))
            char_slot_data = slots.get(char, {"x": 1720, "y": 0, "width": 840, "height": 470})
            for k in ["x", "y", "width", "height"]:
                key_name = f"{char}_{k}"
                self.inputs[key_name] = QLineEdit(str(char_slot_data.get(k, 0)))
                c_form.addRow(QLabel(f"{k.upper()}:"), self.inputs[key_name])
            scroll_grid.addWidget(c_frame, row_idx, col_idx)
            col_idx += 1
            if col_idx > 1:
                col_idx = 0
                row_idx += 1

        scroll.setWidget(scroll_content)
        tab1_vlayout.addWidget(scroll)
        self.tabs.addTab(layout_tab, "Coordinates")

        # Tab 2: Translation & Lock Screen Setup
        trans_tab = QWidget()
        t_form = QFormLayout(trans_tab)

        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English Speaker (EN -> JA)", "日本語話者 (JA -> EN)"])
        self.lang_combo.setCurrentIndex(0 if CONFIG.get("USER_LANG", "EN") == "EN" else 1)
        t_form.addRow(QLabel("User Primary Language:"), self.lang_combo)

        self.api_key_input = QLineEdit(CONFIG.get("GEMINI_API_KEY", ""))
        self.api_key_input.setEchoMode(QLineEdit.Password)
        t_form.addRow(QLabel("Gemini API Key:"), self.api_key_input)

        self.model_input = QLineEdit(CONFIG.get("MODEL_NAME", "gemini-2.5-flash"))
        t_form.addRow(QLabel("Model Name:"), self.model_input)

        self.lock_pwd_input = QLineEdit(CONFIG.get("LOCK_PASSWORD", "password123"))
        t_form.addRow(QLabel("Lock Screen Password:"), self.lock_pwd_input)

        self.lock_opacity_input = QLineEdit(str(CONFIG.get("LOCK_OPACITY", 0.20)))
        t_form.addRow(QLabel("Lock Screen Opacity (0.1 - 0.9):"), self.lock_opacity_input)

        self.tabs.addTab(trans_tab, "Translator & Lock Screen")

        # Tab 3: Launcher Timings
        launcher_tab = QWidget()
        l_form = QFormLayout(launcher_tab)

        self.windower_path_input = QLineEdit(CONFIG.get("WINDOWER_PATH", r"C:\Program Files (x86)\Windower\Windower.exe"))
        l_form.addRow(QLabel("Windower.exe Path:"), self.windower_path_input)

        self.se_pwd_input = QLineEdit(CONFIG.get("SE_PASSWORD", ""))
        self.se_pwd_input.setEchoMode(QLineEdit.Password)
        l_form.addRow(QLabel("SE Password:"), self.se_pwd_input)

        self.pol_delay_input = QLineEdit(str(CONFIG.get("POL_INITIAL_DELAY", 12.0)))
        l_form.addRow(QLabel("POL Initial Delay (sec):"), self.pol_delay_input)

        self.tabs.addTab(launcher_tab, "Launcher & Auto-Login")

        save_btn = QPushButton("★ Save All Settings")
        save_btn.clicked.connect(self.save_and_close)
        layout.addWidget(save_btn)

    def save_and_close(self):
        try:
            CONFIG["USER_LANG"] = "EN" if self.lang_combo.currentIndex() == 0 else "JA"
            CONFIG["GEMINI_API_KEY"] = self.api_key_input.text().strip()
            CONFIG["MODEL_NAME"] = self.model_input.text().strip()
            CONFIG["LOCK_PASSWORD"] = self.lock_pwd_input.text().strip()
            CONFIG["LOCK_OPACITY"] = float(self.lock_opacity_input.text().strip() or "0.20")
            CONFIG["WINDOWER_PATH"] = self.windower_path_input.text().strip()
            CONFIG["SE_PASSWORD"] = self.se_pwd_input.text().strip()
            CONFIG["POL_INITIAL_DELAY"] = float(self.pol_delay_input.text().strip() or "12.0")

            CONFIG["MAIN_TV_POS"] = {
                "x": int(self.inputs["TV_x"].text()),
                "y": int(self.inputs["TV_y"].text()),
                "width": int(self.inputs["TV_width"].text()),
                "height": int(self.inputs["TV_height"].text())
            }
            if "SLOTS" not in CONFIG: CONFIG["SLOTS"] = {}
            for char in CONFIG.get("CHARACTERS", CHARACTERS):
                if f"{char}_x" in self.inputs:
                    CONFIG["SLOTS"][char] = {
                        "x": int(self.inputs[f"{char}_x"].text()),
                        "y": int(self.inputs[f"{char}_y"].text()),
                        "width": int(self.inputs[f"{char}_width"].text()),
                        "height": int(self.inputs[f"{char}_height"].text())
                    }
            save_config(CONFIG)
            self.accept()
        except Exception as e:
            print(f"[-] Config Save Error: {e}")

# ==============================================================================
# MASTER DASHBOARD GUI (840x470)
# ==============================================================================
class MasterControlGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FFXI Tactical Command & Translation Bridge v9.1")
        self.setFixedSize(840, 470)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)

        self.worker = UnifiedWorker()
        self.worker.log_signal.connect(self.log)
        self.worker.cycle_signal.connect(self.cycle_active_character)
        self.worker.trust_sync_signal.connect(self.sync_trust_mode_ui)
        self.worker.assist_sync_signal.connect(self.sync_assist_target_ui)
        self.worker.trans_lang_signal.connect(self.update_lang_btn)
        self.worker.start()

        self.trust_toggle_buttons = {}
        self.assist_labels = {}
        self.char_buttons = {}

        self.setup_ui()
        self.apply_styles()

    def get_hwnd(self): return int(self.winId())

    def setup_ui(self):
        chars = CONFIG.get("CHARACTERS", CHARACTERS)
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 6, 10, 6)
        main_layout.setSpacing(4)

        # Header Bar
        header = QHBoxLayout()
        title = QLabel("⚡ FFXI TACTICAL COMMAND & TRANSLATOR")
        title.setFont(QFont("Consolas", 10, QFont.Bold))
        title.setStyleSheet("color: #00FF66;")
        header.addWidget(title)
        header.addStretch()

        boot_btn = QPushButton("🚀 Boot Party")
        boot_btn.setFixedHeight(22)
        boot_btn.setStyleSheet("background-color: #2E1B44; color: #E040FB; font-size: 10px; font-weight: bold; border: 1px solid #7B1FA2;")
        boot_btn.clicked.connect(self.boot_all_party_members)
        header.addWidget(boot_btn)

        lock_btn = QPushButton("🔒 Lock Screen")
        lock_btn.setFixedHeight(22)
        lock_btn.setStyleSheet("background-color: #332211; color: #FFAA00; font-size: 10px; font-weight: bold; border: 1px solid #774400;")
        lock_btn.clicked.connect(launch_lock_screen)
        header.addWidget(lock_btn)

        self.lang_btn = QPushButton("Mode: EN -> JA")
        self.lang_btn.setFixedHeight(22)
        self.lang_btn.clicked.connect(self.toggle_translator_mode)
        header.addWidget(self.lang_btn)

        reload_btn = QPushButton("⚡ Reload Bridge")
        reload_btn.setFixedHeight(22)
        reload_btn.setStyleSheet("background-color: #2A2A38; color: #00E5FF; font-size: 10px; font-weight: bold; border: 1px solid #3A3A4C;")
        reload_btn.clicked.connect(self.broadcast_reload_bridge)
        header.addWidget(reload_btn)

        settings_btn = QPushButton("⚙")
        settings_btn.setFixedSize(22, 22)
        settings_btn.clicked.connect(self.open_settings)
        header.addWidget(settings_btn)

        close_btn = QPushButton("❌")
        close_btn.setFixedSize(22, 22)
        close_btn.clicked.connect(self.close)
        header.addWidget(close_btn)
        main_layout.addLayout(header)

        # Column Dynamic Switchboard
        cols_layout = QHBoxLayout()
        cols_layout.setSpacing(6)

        for char in chars:
            box = QFrame()
            box.setStyleSheet("background-color: #16161E; border: 1px solid #282838; border-radius: 6px;")
            box_layout = QVBoxLayout(box)
            box_layout.setContentsMargins(4, 4, 4, 4)
            box_layout.setSpacing(2)

            c_btn = QPushButton(f"★ {char}")
            c_btn.setFixedHeight(24)
            c_btn.setFont(QFont("Consolas", 10, QFont.Bold))
            c_btn.clicked.connect(lambda checked, c=char: self.handle_character_focus(c))
            self.char_buttons[char] = c_btn
            box_layout.addWidget(c_btn)

            a_lbl = QLabel(f"Assist: {CONFIG.get('LEADER_NAME', 'Taylormade')}")
            a_lbl.setAlignment(Qt.AlignCenter)
            a_lbl.setFont(QFont("Consolas", 8))
            a_lbl.setStyleSheet("color: #00E5FF; padding-bottom: 2px;")
            self.assist_labels[char] = a_lbl
            box_layout.addWidget(a_lbl)

            for mode_name, options in STANDARD_MODES.items():
                row = QWidget()
                r_layout = QHBoxLayout(row)
                r_layout.setContentsMargins(1, 1, 1, 1)
                r_layout.setSpacing(2)

                clean_name = mode_name.replace("Mode", "").replace("Auto", "Auto ")
                lbl = QLabel(clean_name)
                lbl.setFont(QFont("Consolas", 8, QFont.Bold))
                lbl.setStyleSheet("color: #C0C0D0;")
                r_layout.addWidget(lbl)
                r_layout.addStretch()

                if "TRUST_MODES" not in CONFIG: CONFIG["TRUST_MODES"] = {}
                if char not in CONFIG["TRUST_MODES"]: CONFIG["TRUST_MODES"][char] = {}

                cur_val = CONFIG["TRUST_MODES"][char].get(mode_name, options[0])
                toggle = QPushButton(cur_val)
                toggle.setFixedSize(65, 20)
                toggle.setFont(QFont("Consolas", 8, QFont.Bold))
                toggle.clicked.connect(lambda checked, c=char, m=mode_name: self.cycle_trust_mode(c, m))
                self.trust_toggle_buttons[(char, mode_name)] = toggle
                self.update_trust_btn_style(toggle, cur_val)

                r_layout.addWidget(toggle)
                box_layout.addWidget(row)

            box_layout.addStretch()
            cols_layout.addWidget(box)

        main_layout.addLayout(cols_layout)

        # Monospace Live Log
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setFixedHeight(75)
        self.log_box.setFont(QFont("Consolas", 8))
        self.log_box.setStyleSheet("background-color: #0A0A0E; color: #00FF66; border: 1px solid #222230; border-radius: 4px;")
        main_layout.addWidget(self.log_box)

        self.update_character_ui(chars[0])
        self.update_lang_btn(CONFIG.get("USER_LANG", "EN"))

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #121216; }
            QLabel { color: #FFFFFF; font-family: Consolas; }
            QPushButton { background-color: #242430; color: #FFFFFF; border: 1px solid #3A3A4C; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #323244; }
        """)

    def boot_all_party_members(self):
        threading.Thread(target=self._boot_sequence, daemon=True).start()

    def _boot_sequence(self):
        chars = CONFIG.get("CHARACTERS", CHARACTERS)
        self.log("[Auto-Boot] Launching characters in sequence...")
        for char in chars:
            hwnds = find_running_windows()
            if char in hwnds:
                self.log(f"[Auto-Boot] '{char}' already active. Skipping.")
                continue

            self.log(f"[Auto-Boot] Launching '{char}' via Calibrated POL...")
            launch_character_process(char, auto_type_pwd=True, log_callback=self.log)
            
            # Allow up to 50 seconds for full login before launching next character
            for _ in range(50):
                time.sleep(1.0)
                if char in find_running_windows(): 
                    self.log(f"[Auto-Boot] '{char}' client detected!")
                    break

            apply_layout(chars[current_active_index], self.get_hwnd())
            time.sleep(5.0)

        apply_layout(chars[current_active_index], self.get_hwnd())
        self.log("[Auto-Boot] All party members processed!")

    def toggle_translator_mode(self):
        new_lang = "JA" if CONFIG.get("USER_LANG", "EN") == "EN" else "EN"
        CONFIG["USER_LANG"] = new_lang
        save_config(CONFIG)
        self.update_lang_btn(new_lang)
        self.log(f"[Translator] Mode set to: {new_lang}")

    def update_lang_btn(self, lang):
        if lang == "EN":
            self.lang_btn.setText("Mode: EN -> JA")
            self.lang_btn.setStyleSheet("background-color: #007ACC; color: white; border: 1px solid #005A9E; font-size: 10px; font-weight: bold;")
        else:
            self.lang_btn.setText("Mode: JA -> EN")
            self.lang_btn.setStyleSheet("background-color: #28A745; color: white; border: 1px solid #1E7E34; font-size: 10px; font-weight: bold;")

    def cycle_trust_mode(self, char_name, mode_name):
        options = STANDARD_MODES[mode_name]
        cur_val = CONFIG["TRUST_MODES"][char_name].get(mode_name, options[0])
        next_idx = (options.index(cur_val) + 1) % len(options)
        new_val = options[next_idx]

        CONFIG["TRUST_MODES"][char_name][mode_name] = new_val
        save_config(CONFIG)

        btn = self.trust_toggle_buttons.get((char_name, mode_name))
        if btn: self.update_trust_btn_style(btn, new_val)

        trust_cmd = f"//trust set {mode_name} {new_val}"
        self.worker.command_queues.setdefault(char_name, []).append({"commands": [trust_cmd], "reply": ""})
        self.log(f"[{char_name} Trust] {mode_name} -> {new_val}")

    @Slot(str, str, str)
    def sync_trust_mode_ui(self, char_name, mode_name, val):
        btn = self.trust_toggle_buttons.get((char_name, mode_name))
        if btn: self.update_trust_btn_style(btn, val)

    @Slot(str, str)
    def sync_assist_target_ui(self, char_name, target):
        lbl = self.assist_labels.get(char_name)
        if lbl: lbl.setText(f"Assist: {target}")

    def update_trust_btn_style(self, btn: QPushButton, val: str):
        btn.setText(val)
        if val in ["Always", "Auto"]:
            btn.setStyleSheet("background-color: #1B4420; color: #00FF66; border: 1px solid #2E7D32; border-radius: 3px;")
        elif val in ["Emergency", "Mirror", "Spam", "Path", "Back", "Left", "Right", "Aggroed"]:
            btn.setStyleSheet("background-color: #4A3A10; color: #FFD54F; border: 1px solid #F57F17; border-radius: 3px;")
        else:
            btn.setStyleSheet("background-color: #22222E; color: #888899; border: 1px solid #333344; border-radius: 3px;")

    def broadcast_reload_bridge(self):
        for c in CONFIG.get("CHARACTERS", CHARACTERS):
            self.worker.command_queues.setdefault(c, []).append({"commands": ["//lua r bridge"], "reply": ""})
        self.log("[Addon] Reloaded bridge addon on all clients!")

    def open_settings(self):
        dialog = UnifiedSettingsDialog(self)
        if dialog.exec():
            self.worker.reload_gemini()
            chars = CONFIG.get("CHARACTERS", CHARACTERS)
            apply_layout(chars[current_active_index % len(chars)], self.get_hwnd())
            self.update_lang_btn(CONFIG.get("USER_LANG", "EN"))
            self.log("[Settings] Settings updated!")

    @Slot(str)
    def log(self, text):
        self.log_box.append(f"{time.strftime('[%H:%M:%S]')} {text}")

    @Slot(str)
    def cycle_active_character(self, direction):
        global current_active_index
        chars = CONFIG.get("CHARACTERS", CHARACTERS)
        if direction == "next":
            current_active_index = (current_active_index + 1) % len(chars)
        else:
            current_active_index = (current_active_index - 1) % len(chars)
        char_name = chars[current_active_index]
        self.handle_character_focus(char_name)

    def handle_character_focus(self, char_name):
        hwnds = find_running_windows()
        if char_name not in hwnds:
            self.log(f"[Launcher] '{char_name}' not detected. Launching via POL...")
            launch_character_process(char_name, auto_type_pwd=True, log_callback=self.log)
        self.update_character_ui(char_name)
        apply_layout(char_name, self.get_hwnd())

    def update_character_ui(self, active_char):
        for char, btn in self.char_buttons.items():
            if char.lower() == active_char.lower():
                btn.setStyleSheet("background-color: #007ACC; color: #FFFFFF; border: 2px solid #005A9E;")
            else:
                btn.setStyleSheet("background-color: #20202A; color: #888899; border: 1px solid #333344;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = MasterControlGUI()
    gui.show()
    chars = CONFIG.get("CHARACTERS", CHARACTERS)
    apply_layout(chars[0], gui.get_hwnd())
    sys.exit(app.exec())