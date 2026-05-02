import tkinter as tk
import subprocess
import threading
import os
import platform
import socket
import shutil
import glob

BG = "#0f0f13"
SURFACE = "#18181f"
SURFACE2 = "#202028"
BORDER = "#2a2a35"
ACCENT = "#6c63ff"
ACCENT2 = "#4ecca3"
TEXT = "#e8e8f0"
TEXT2 = "#888899"
SUCCESS = "#4ecca3"
ERROR = "#ff6b6b"
TOGGLE_ON = "#6c63ff"
TOGGLE_OFF = "#2a2a35"

def reg_read_dword(path, key):
    try:
        r = subprocess.run(f'reg query "{path}" /v {key}', shell=True, capture_output=True, text=True)
        if r.returncode == 0:
            for line in r.stdout.splitlines():
                if key in line and "REG_DWORD" in line:
                    return int(line.strip().split()[-1], 16)
    except: pass
    return None

def reg_read_sz(path, key):
    try:
        r = subprocess.run(f'reg query "{path}" /v {key}', shell=True, capture_output=True, text=True)
        if r.returncode == 0:
            for line in r.stdout.splitlines():
                if key in line and "REG_SZ" in line:
                    return line.strip().split("REG_SZ")[-1].strip()
    except: pass
    return None

def get_darkmode_state(): return reg_read_dword("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize", "AppsUseLightTheme") == 0
def get_telemetry_state(): return reg_read_dword("HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection", "AllowTelemetry") == 0
def get_extensions_state(): return reg_read_dword("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "HideFileExt") == 0
def get_gamemode_state(): return reg_read_dword("HKCU\\Software\\Microsoft\\GameBar", "AutoGameModeEnabled") == 1
def get_ads_state():
    try:
        with open(r"C:\Windows\System32\drivers\etc\hosts", "r") as f: return "WinSetup" in f.read()
    except: return False
def get_updates_state(): return reg_read_dword("HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU", "NoAutoUpdate") == 1
def get_searchbar_state(): return reg_read_dword("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Search", "SearchboxTaskbarMode") == 0
def get_cortana_state(): return reg_read_dword("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "ShowCortanaButton") == 0
def get_taskview_state(): return reg_read_dword("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "ShowTaskViewButton") == 0
def get_notifications_state(): return reg_read_dword("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\PushNotifications", "ToastEnabled") == 0
def get_transparency_state(): return reg_read_dword("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize", "EnableTransparency") == 0
def get_firewall_state():
    try:
        r = subprocess.run('netsh advfirewall show allprofiles state', shell=True, capture_output=True, text=True)
        return "ON" in r.stdout.upper()
    except: return True
def get_rdp_state(): return reg_read_dword("HKLM\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server", "fDenyTSConnections") == 0
def get_bgapps_state(): return reg_read_dword("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\BackgroundAccessApplications", "GlobalUserDisabled") == 1
def get_hibernate_state():
    try:
        r = subprocess.run("powercfg /a", shell=True, capture_output=True, text=True)
        return "Hibernation" in r.stdout or "Hibernálás" in r.stdout
    except: return False
def get_superfetch_state():
    try:
        r = subprocess.run('sc query SysMain', shell=True, capture_output=True, text=True)
        return "STOPPED" in r.stdout
    except: return False
def get_wap_state(): return reg_read_dword("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager", "SystemPaneSuggestionsEnabled") == 0
def get_lockscreen_state(): return reg_read_dword("HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Personalization", "NoLockScreen") == 1
def get_uac_state(): return reg_read_dword("HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System", "EnableLUA") == 1
def get_numlock_state(): return reg_read_dword("HKCU\\Control Panel\\Keyboard", "InitialKeyboardIndicators") == 2
def get_hidden_files_state(): return reg_read_dword("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "Hidden") == 1
def get_snap_state(): return reg_read_dword("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "EnableSnapAssistFlyout") == 0
def get_sticky_keys_state(): return reg_read_dword("HKCU\\Control Panel\\Accessibility\\StickyKeys", "Flags") == 506
def get_location_state(): return reg_read_dword("HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\location", "Value") is None
def get_ipv6_state(): return reg_read_dword("HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip6\\Parameters", "DisabledComponents") == 255
def get_autoplay_state(): return reg_read_dword("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\AutoplayHandlers", "DisableAutoplay") == 1
def get_error_reporting_state(): return reg_read_dword("HKLM\\SOFTWARE\\Microsoft\\Windows\\Windows Error Reporting", "Disabled") == 1
def get_print_spooler_state():
    try:
        r = subprocess.run('sc query Spooler', shell=True, capture_output=True, text=True)
        return "RUNNING" in r.stdout
    except: return False
def get_wlan_state():
    try:
        r = subprocess.run('sc query WlanSvc', shell=True, capture_output=True, text=True)
        return "RUNNING" in r.stdout
    except: return False
def get_bluetooth_state():
    try:
        r = subprocess.run('sc query bthserv', shell=True, capture_output=True, text=True)
        return "RUNNING" in r.stdout
    except: return False

class Toggle(tk.Canvas):
    def __init__(self, parent, state=False, command=None, bg_color=SURFACE, **kwargs):
        super().__init__(parent, width=48, height=26, bg=bg_color, highlightthickness=0, cursor="hand2", **kwargs)
        self.state = state
        self.command = command
        self.draw()
        self.bind("<Button-1>", self.toggle)

    def draw(self):
        self.delete("all")
        color = TOGGLE_ON if self.state else TOGGLE_OFF
        self.create_rounded_rect(2, 2, 46, 24, radius=11, fill=color, outline="")
        cx = 35 if self.state else 13
        self.create_oval(cx-9, 4, cx+9, 22, fill="#ffffff", outline="")

    def create_rounded_rect(self, x1, y1, x2, y2, radius=10, **kwargs):
        points = [x1+radius,y1, x2-radius,y1, x2,y1, x2,y1+radius, x2,y2-radius, x2,y2, x2-radius,y2, x1+radius,y2, x1,y2, x1,y2-radius, x1,y1+radius, x1,y1]
        return self.create_polygon(points, smooth=True, **kwargs)

    def toggle(self, event=None):
        self.state = not self.state
        self.draw()
        if self.command: self.command(self.state)

    def set_state(self, state):
        self.state = state
        self.draw()


class WinSetup(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WinSetup")
        self.geometry("1000x700")
        self.resizable(True, True)
        self.configure(bg=BG)
        self.toggles = {}
        self.tab_frames = {}
        self.tab_buttons = {}
        self.build_ui()
        self.after(400, self.detect_states)

    def build_ui(self):
        header = tk.Frame(self, bg=SURFACE, height=52)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="⚡ WinSetup", font=("Consolas", 15, "bold"), bg=SURFACE, fg=ACCENT).pack(side="left", padx=20, pady=12)
        tk.Label(header, text="Windows 10", font=("Consolas", 9), bg=SURFACE, fg=TEXT2).pack(side="right", padx=20)
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        self.tabbar = tk.Frame(self, bg=SURFACE2, height=42)
        self.tabbar.pack(fill="x")
        self.tabbar.pack_propagate(False)
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        log_frame = tk.Frame(self, bg=SURFACE2, height=36)
        log_frame.pack(fill="x", side="bottom")
        log_frame.pack_propagate(False)
        tk.Frame(self, bg=BORDER, height=1).pack(side="bottom", fill="x")
        self.log_var = tk.StringVar(value="Állapotok beolvasása...")
        tk.Label(log_frame, textvariable=self.log_var, font=("Consolas", 9), bg=SURFACE2, fg=TEXT2, anchor="w").pack(fill="x", padx=14, pady=8)

        self.content = tk.Frame(self, bg=BG)
        self.content.pack(fill="both", expand=True)

        tabs = [
            ("📦 Telepítő", self.build_installer),
            ("🛡️ Adatvédelem", self.build_privacy),
            ("⚡ Teljesítmény", self.build_performance),
            ("🎨 Megjelenés", self.build_appearance),
            ("🔒 Biztonság", self.build_security),
            ("🌐 Hálózat", self.build_network),
            ("🛠️ Rendszer", self.build_system),
            ("⚙️ Szolgáltatások", self.build_services),
        ]

        for name, builder in tabs:
            frame = tk.Frame(self.content, bg=BG)
            self.tab_frames[name] = frame
            builder(frame)
            btn = tk.Label(self.tabbar, text=name, font=("Consolas", 9),
                           bg=SURFACE2, fg=TEXT2, cursor="hand2", padx=10, pady=10)
            btn.pack(side="left")
            btn.bind("<Button-1>", lambda e, n=name: self.show_tab(n))
            self.tab_buttons[name] = btn

        self.show_tab("📦 Telepítő")

    def show_tab(self, name):
        for f in self.tab_frames.values(): f.pack_forget()
        self.tab_frames[name].pack(fill="both", expand=True)
        for n, b in self.tab_buttons.items():
            b.config(bg=BG if n == name else SURFACE2, fg=ACCENT if n == name else TEXT2)

    def make_scroll_frame(self, parent):
        container = tk.Frame(parent, bg=BG)
        container.pack(fill="both", expand=True)
        canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
        sb = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=BG)
        def on_inner_configure(e): canvas.configure(scrollregion=canvas.bbox("all"))
        def on_canvas_configure(e): canvas.itemconfig(win_id, width=e.width)
        inner.bind("<Configure>", on_inner_configure)
        win_id = canvas.create_window((0,0), window=inner, anchor="nw")
        canvas.bind("<Configure>", on_canvas_configure)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        return inner

    def section_label(self, parent, text):
        f = tk.Frame(parent, bg=BG)
        f.pack(fill="x", padx=20, pady=(16,4))
        tk.Label(f, text=text, font=("Consolas", 11, "bold"), bg=BG, fg=ACCENT2).pack(anchor="w")
        tk.Frame(f, bg=BORDER, height=1).pack(fill="x", pady=(3,0))

    def make_toggle_row(self, parent, label, desc, tid, on_fn=None, off_fn=None, on_cmd=None, off_cmd=None, on_msg="Kész!", off_msg="Visszaállítva."):
        row = tk.Frame(parent, bg=SURFACE, highlightbackground=BORDER, highlightthickness=1)
        row.pack(fill="x", padx=20, pady=3)
        info = tk.Frame(row, bg=SURFACE)
        info.pack(side="left", fill="both", expand=True, padx=14, pady=10)
        tk.Label(info, text=label, font=("Consolas", 11, "bold"), bg=SURFACE, fg=TEXT, anchor="w").pack(anchor="w")
        tk.Label(info, text=desc, font=("Consolas", 9), bg=SURFACE, fg=TEXT2, anchor="w", wraplength=530).pack(anchor="w")
        item = {"on_fn": on_fn, "off_fn": off_fn, "on_cmd": on_cmd, "off_cmd": off_cmd, "on_msg": on_msg, "off_msg": off_msg}
        tog = Toggle(row, state=False, command=lambda s, i=item: self.on_toggle(s, i))
        tog.pack(side="right", padx=16, pady=10)
        self.toggles[tid] = tog

    def make_button_row(self, parent, label, desc, command):
        row = tk.Frame(parent, bg=SURFACE, highlightbackground=BORDER, highlightthickness=1)
        row.pack(fill="x", padx=20, pady=3)
        info = tk.Frame(row, bg=SURFACE)
        info.pack(side="left", fill="both", expand=True, padx=14, pady=10)
        tk.Label(info, text=label, font=("Consolas", 11, "bold"), bg=SURFACE, fg=TEXT, anchor="w").pack(anchor="w")
        tk.Label(info, text=desc, font=("Consolas", 9), bg=SURFACE, fg=TEXT2, anchor="w", wraplength=530).pack(anchor="w")
        btn = tk.Button(row, text="▶ Futtatás", font=("Consolas", 10), bg=ACCENT, fg="#fff",
                        relief="flat", activebackground="#8a83ff", cursor="hand2",
                        bd=0, padx=12, pady=6, command=command)
        btn.pack(side="right", padx=16, pady=10)

    # ══════════════════════════════════════════════════
    # TABS
    # ══════════════════════════════════════════════════

    def build_installer(self, parent):
        inner = self.make_scroll_frame(parent)
        self.section_label(inner, "🌐  Böngészők")
        browsers = [
            ("🌐  Chrome", "Google Chrome böngésző", "chrome", "googlechrome"),
            ("🦊  Firefox", "Mozilla Firefox böngésző", "firefox", "firefox"),
            ("🦁  Brave", "Brave – beépített reklámblokkolóval", "brave", "brave"),
            ("🔵  Opera GX", "Opera GX – játékosoknak szánt böngésző", "operagx", "opera"),
        ]
        for label, desc, tid, pkg in browsers:
            self.make_toggle_row(inner, label, desc, tid,
                on_fn=lambda p=pkg, n=label: self.choco_install(p, f"{n} telepítve!"),
                off_fn=lambda p=pkg, n=label: self.choco_uninstall(p, f"{n} eltávolítva!"))

        self.section_label(inner, "💬  Kommunikáció")
        comms = [
            ("📱  Viber", "Viber üzenetküldő", "viber", "viber"),
            ("💬  Discord", "Discord chat és közösségi platform", "discord", "discord"),
            ("📞  Zoom", "Zoom videókonferencia", "zoom", "zoom"),
            ("💙  Teams", "Microsoft Teams", "teams", "microsoft-teams"),
            ("✈️  Telegram", "Telegram üzenetküldő", "telegram", "telegram"),
        ]
        for label, desc, tid, pkg in comms:
            self.make_toggle_row(inner, label, desc, tid,
                on_fn=lambda p=pkg, n=label: self.choco_install(p, f"{n} telepítve!"),
                off_fn=lambda p=pkg, n=label: self.choco_uninstall(p, f"{n} eltávolítva!"))

        self.section_label(inner, "🎮  Játék")
        games = [
            ("🎮  Roblox", "Roblox játékplatform", "roblox", "roblox"),
            ("🎮  Steam", "Steam PC játékplatform", "steam", "steam"),
            ("🎮  Epic Games", "Epic Games Launcher", "epicgames", "epicgameslauncher"),
            ("🎮  GOG Galaxy", "GOG Galaxy játékplatform", "goggalaxy", "goggalaxy"),
        ]
        for label, desc, tid, pkg in games:
            self.make_toggle_row(inner, label, desc, tid,
                on_fn=lambda p=pkg, n=label: self.choco_install(p, f"{n} telepítve!"),
                off_fn=lambda p=pkg, n=label: self.choco_uninstall(p, f"{n} eltávolítva!"))

        self.section_label(inner, "🎵  Média")
        media = [
            ("🎬  VLC", "VLC médialejátszó", "vlc", "vlc"),
            ("🎵  Spotify", "Spotify zenei streaming", "spotify", "spotify"),
            ("🎬  MPC-HC", "Media Player Classic", "mpchc", "mpc-hc"),
            ("🎨  GIMP", "GIMP képszerkesztő", "gimp", "gimp"),
            ("🎬  HandBrake", "HandBrake videókonvertáló", "handbrake", "handbrake"),
            ("📸  Greenshot", "Képernyőkép készítő", "greenshot", "greenshot"),
            ("🎥  OBS Studio", "OBS képernyőrögzítő és streamer", "obs", "obs-studio"),
        ]
        for label, desc, tid, pkg in media:
            self.make_toggle_row(inner, label, desc, tid,
                on_fn=lambda p=pkg, n=label: self.choco_install(p, f"{n} telepítve!"),
                off_fn=lambda p=pkg, n=label: self.choco_uninstall(p, f"{n} eltávolítva!"))

        self.section_label(inner, "🛠️  Eszközök")
        tools = [
            ("🗜️  7-Zip", "7-Zip tömörítő", "7zip", "7zip"),
            ("📝  Notepad++", "Notepad++ szövegszerkesztő", "notepadpp", "notepadplusplus"),
            ("💻  MobaXterm", "MobaXterm SSH/terminál kliens", "mobaxterm", "mobaxterm"),
            ("📂  WinSCP", "WinSCP FTP/SFTP kliens", "winscp", "winscp"),
            ("🔍  Everything", "Everything – villámgyors fájlkereső", "everything", "everything"),
            ("🖥️  CPU-Z", "CPU-Z – rendszer információk", "cpuz", "cpu-z"),
            ("🖥️  GPU-Z", "GPU-Z – videókártya információk", "gpuz", "gpu-z"),
            ("🌡️  HWMonitor", "HWMonitor – hőmérséklet figyelő", "hwmonitor", "hwmonitor"),
            ("💾  CrystalDiskInfo", "CrystalDiskInfo – lemez állapot", "crystaldiskinfo", "crystaldiskinfo"),
            ("🔧  Autoruns", "Autoruns – indítóprogramok kezelője", "autoruns", "autoruns"),
            ("🔬  Process Hacker", "Process Hacker – folyamatkezelő", "processhacker", "processhacker"),
            ("📦  WinRAR", "WinRAR tömörítő", "winrar", "winrar"),
        ]
        for label, desc, tid, pkg in tools:
            self.make_toggle_row(inner, label, desc, tid,
                on_fn=lambda p=pkg, n=label: self.choco_install(p, f"{n} telepítve!"),
                off_fn=lambda p=pkg, n=label: self.choco_uninstall(p, f"{n} eltávolítva!"))

        self.section_label(inner, "👨‍💻  Fejlesztés")
        dev = [
            ("🐍  Python", "Python programozási nyelv", "python", "python"),
            ("🟢  Node.js", "Node.js JavaScript futtatókörnyezet", "nodejs", "nodejs"),
            ("🔧  Git", "Git verziókezelő", "git", "git"),
            ("💙  VS Code", "Visual Studio Code szerkesztő", "vscode", "vscode"),
            ("🐋  Docker", "Docker konténerplatform", "docker", "docker-desktop"),
            ("☕  Java", "Java fejlesztői csomag (JDK)", "java", "openjdk"),
        ]
        for label, desc, tid, pkg in dev:
            self.make_toggle_row(inner, label, desc, tid,
                on_fn=lambda p=pkg, n=label: self.choco_install(p, f"{n} telepítve!"),
                off_fn=lambda p=pkg, n=label: self.choco_uninstall(p, f"{n} eltávolítva!"))

        tk.Frame(inner, bg=BG, height=16).pack()

    def build_privacy(self, parent):
        inner = self.make_scroll_frame(parent)
        self.section_label(inner, "🛡️  Adatvédelem")
        self.make_toggle_row(inner, "🚫  Reklámblokkolás", "Hosts fájl módosítással blokkolja a hirdetési szervereket", "ads", on_fn=self.ads_on, off_fn=self.ads_off)
        self.make_toggle_row(inner, "🖨️  Telemetria letiltása", "Windows diagnosztikai adatgyűjtés kikapcsolása", "tracking",
            on_cmd='reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f && sc config DiagTrack start= disabled && sc stop DiagTrack',
            off_cmd='reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 1 /f && sc config DiagTrack start= auto && sc start DiagTrack',
            on_msg="Telemetria letiltva!", off_msg="Telemetria visszakapcsolva.")
        self.make_toggle_row(inner, "🔔  Értesítések kikapcsolása", "Toast értesítések letiltása", "notifications",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\PushNotifications" /v ToastEnabled /t REG_DWORD /d 0 /f',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\PushNotifications" /v ToastEnabled /t REG_DWORD /d 1 /f',
            on_msg="Értesítések kikapcsolva!", off_msg="Értesítések visszakapcsolva.")
        self.make_toggle_row(inner, "🔄  Automatikus frissítések", "Windows Update automatikus letöltés kikapcsolása", "updates",
            on_cmd='reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" /v NoAutoUpdate /t REG_DWORD /d 0 /f',
            off_cmd='reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" /v NoAutoUpdate /t REG_DWORD /d 1 /f',
            on_msg="Automatikus frissítések kikapcsolva!", off_msg="Automatikus frissítések visszakapcsolva.")
        self.make_toggle_row(inner, "💡  Tippek és javaslatok", "Windows tippek, trükkök és hirdetések letiltása", "wap",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager" /v SystemPaneSuggestionsEnabled /t REG_DWORD /d 0 /f && reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager" /v SoftLandingEnabled /t REG_DWORD /d 0 /f',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager" /v SystemPaneSuggestionsEnabled /t REG_DWORD /d 1 /f',
            on_msg="Tippek letiltva!", off_msg="Tippek visszakapcsolva.")
        self.make_toggle_row(inner, "📍  Helymeghatározás letiltása", "Windows helymeghatározás kikapcsolása", "location",
            on_cmd='reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\location" /v Value /t REG_SZ /d Deny /f',
            off_cmd='reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\location" /v Value /t REG_SZ /d Allow /f',
            on_msg="Helymeghatározás letiltva!", off_msg="Helymeghatározás visszakapcsolva.")
        self.make_toggle_row(inner, "🚗  AutoPlay letiltása", "Automatikus lejátszás/megnyitás letiltása USB eszközöknél", "autoplay",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\AutoplayHandlers" /v DisableAutoplay /t REG_DWORD /d 1 /f',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\AutoplayHandlers" /v DisableAutoplay /t REG_DWORD /d 0 /f',
            on_msg="AutoPlay letiltva!", off_msg="AutoPlay visszakapcsolva.")
        self.make_toggle_row(inner, "💥  Hibajelentés letiltása", "Windows Error Reporting kikapcsolása", "errorreporting",
            on_cmd='reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\Windows Error Reporting" /v Disabled /t REG_DWORD /d 1 /f',
            off_cmd='reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\Windows Error Reporting" /v Disabled /t REG_DWORD /d 0 /f',
            on_msg="Hibajelentés letiltva!", off_msg="Hibajelentés visszakapcsolva.")
        self.make_toggle_row(inner, "🔒  Zárolási képernyő letiltása", "Bejelentkezési képernyő előtti zárolás eltávolítása", "lockscreen",
            on_cmd='reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Personalization" /v NoLockScreen /t REG_DWORD /d 1 /f',
            off_cmd='reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Personalization" /v NoLockScreen /t REG_DWORD /d 0 /f',
            on_msg="Zárolási képernyő letiltva!", off_msg="Zárolási képernyő visszakapcsolva.")
        self.make_toggle_row(inner, "🎯  Hirdetési azonosító letiltása", "Személyre szabott reklámok azonosítójának törlése", "adid",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo" /v Enabled /t REG_DWORD /d 0 /f',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo" /v Enabled /t REG_DWORD /d 1 /f',
            on_msg="Hirdetési azonosító letiltva!", off_msg="Hirdetési azonosító visszakapcsolva.")
        self.make_toggle_row(inner, "🗣️  Hangfelismerés letiltása", "Online hangfelismerés kikapcsolása", "speech",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\Speech_OneCore\\Settings\\OnlineSpeechPrivacy" /v HasAccepted /t REG_DWORD /d 0 /f',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\Speech_OneCore\\Settings\\OnlineSpeechPrivacy" /v HasAccepted /t REG_DWORD /d 1 /f',
            on_msg="Hangfelismerés letiltva!", off_msg="Hangfelismerés visszakapcsolva.")
        self.section_label(inner, "🗑️  Bloatware")
        self.make_button_row(inner, "🗑️  Bloatware eltávolítása", "Bing, Weather, Office Hub, Solitaire, People, Teams és más felesleges appok törlése", self.remove_bloatware)
        self.make_button_row(inner, "🧹  Böngészési előzmények törlése", "Edge, Chrome, Firefox gyorsítótár és előzmények törlése", self.clear_browser_history)
        tk.Frame(inner, bg=BG, height=16).pack()

    def build_performance(self, parent):
        inner = self.make_scroll_frame(parent)
        self.section_label(inner, "⚡  Teljesítmény")
        self.make_toggle_row(inner, "🎯  Játék optimalizálás", "Game Mode + nagy teljesítményű energiaséma", "gamemode",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\GameBar" /v AutoGameModeEnabled /t REG_DWORD /d 1 /f && powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\GameBar" /v AutoGameModeEnabled /t REG_DWORD /d 0 /f && powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e',
            on_msg="Játék optimalizálás bekapcsolva!", off_msg="Játék optimalizálás kikapcsolva.")
        self.make_toggle_row(inner, "💤  Hibernálás", "Hibernálás engedélyezése/tiltása", "hibernate",
            on_cmd="powercfg /hibernate on", off_cmd="powercfg /hibernate off",
            on_msg="Hibernálás bekapcsolva!", off_msg="Hibernálás kikapcsolva.")
        self.make_toggle_row(inner, "🖼️  Vizuális effektek kikapcsolása", "Animációk, árnyékok letiltása – gyorsabb rendszer", "visualfx",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" /v VisualFXSetting /t REG_DWORD /d 2 /f',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" /v VisualFXSetting /t REG_DWORD /d 0 /f',
            on_msg="Vizuális effektek kikapcsolva!", off_msg="Vizuális effektek visszakapcsolva.")
        self.make_toggle_row(inner, "📱  Háttér appok letiltása", "Háttérben futó alkalmazások letiltása", "bgapps",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\BackgroundAccessApplications" /v GlobalUserDisabled /t REG_DWORD /d 1 /f',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\BackgroundAccessApplications" /v GlobalUserDisabled /t REG_DWORD /d 0 /f',
            on_msg="Háttér appok letiltva!", off_msg="Háttér appok visszakapcsolva.")
        self.make_toggle_row(inner, "🚀  Superfetch letiltása", "SysMain (Superfetch) szolgáltatás kikapcsolása – SSD-nél ajánlott", "superfetch",
            on_cmd="sc stop SysMain && sc config SysMain start= disabled",
            off_cmd="sc config SysMain start= auto && sc start SysMain",
            on_msg="Superfetch letiltva!", off_msg="Superfetch visszakapcsolva.")
        self.make_toggle_row(inner, "📄  Lapozófájl optimalizálás", "Rendszer kezeli a lapozófájlt automatikusan", "pagefile",
            on_cmd='wmic computersystem where name="%computername%" set AutomaticManagedPagefile=True',
            off_cmd='wmic computersystem where name="%computername%" set AutomaticManagedPagefile=False',
            on_msg="Lapozófájl automatikus!", off_msg="Lapozófájl manuális.")
        self.make_toggle_row(inner, "🔍  Keresési indexelés letiltása", "Windows Search indexelés kikapcsolása – gyorsabb HDD/SSD", "search_index",
            on_cmd="sc stop WSearch && sc config WSearch start= disabled",
            off_cmd="sc config WSearch start= auto && sc start WSearch",
            on_msg="Indexelés letiltva!", off_msg="Indexelés visszakapcsolva.")
        self.make_toggle_row(inner, "📅  Ütemezett defrag letiltása", "Automatikus lemez töredezettség-mentesítés kikapcsolása", "defrag",
            on_cmd='schtasks /Change /TN "\\Microsoft\\Windows\\Defrag\\ScheduledDefrag" /Disable',
            off_cmd='schtasks /Change /TN "\\Microsoft\\Windows\\Defrag\\ScheduledDefrag" /Enable',
            on_msg="Ütemezett defrag letiltva!", off_msg="Ütemezett defrag visszakapcsolva.")
        self.section_label(inner, "🧹  Karbantartás")
        self.make_button_row(inner, "🗑️  Ideiglenes fájlok törlése", "Temp mappák kiürítése", self.clean_temp)
        self.make_button_row(inner, "💾  RAM felszabadítás", "Felesleges folyamatok memóriájának felszabadítása", self.free_ram)
        self.make_button_row(inner, "🗑️  Szemetes kiürítése", "Lomtár tartalmának törlése", self.empty_recycle)
        self.make_button_row(inner, "🧹  DNS gyorsítótár törlése", "DNS cache ürítése", lambda: self.run_cmd("ipconfig /flushdns", "DNS cache törölve!"))
        self.make_button_row(inner, "📦  Windows Update cache törlése", "Windows Update letöltési cache törlése", self.clear_wu_cache)
        self.make_button_row(inner, "🔍  Lemezterület elemzése", "C: meghajtó szabad és foglalt helyének megjelenítése", self.show_disk_usage)
        tk.Frame(inner, bg=BG, height=16).pack()

    def build_appearance(self, parent):
        inner = self.make_scroll_frame(parent)
        self.section_label(inner, "🎨  Téma")
        self.make_toggle_row(inner, "🌙  Sötét mód", "Windows 10 sötét téma", "darkmode",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v AppsUseLightTheme /t REG_DWORD /d 0 /f && reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v SystemUsesLightTheme /t REG_DWORD /d 0 /f',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v AppsUseLightTheme /t REG_DWORD /d 1 /f && reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v SystemUsesLightTheme /t REG_DWORD /d 1 /f',
            on_msg="Sötét mód bekapcsolva!", off_msg="Világos mód visszakapcsolva.")
        self.make_toggle_row(inner, "💎  Átlátszóság kikapcsolása", "Tálca és ablakok átlátszóság effekt letiltása", "transparency",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v EnableTransparency /t REG_DWORD /d 0 /f',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v EnableTransparency /t REG_DWORD /d 1 /f',
            on_msg="Átlátszóság kikapcsolva!", off_msg="Átlátszóság visszakapcsolva.")
        self.make_toggle_row(inner, "✨  Animációk kikapcsolása", "Ablakok animációinak letiltása", "animations",
            on_cmd='reg add "HKCU\\Control Panel\\Desktop\\WindowMetrics" /v MinAnimate /t REG_SZ /d 0 /f',
            off_cmd='reg add "HKCU\\Control Panel\\Desktop\\WindowMetrics" /v MinAnimate /t REG_SZ /d 1 /f',
            on_msg="Animációk kikapcsolva!", off_msg="Animációk visszakapcsolva.")
        self.section_label(inner, "🗂️  Fájlkezelő")
        self.make_toggle_row(inner, "📄  Fájlkiterjesztések megjelenítése", "Megmutatja a fájlok kiterjesztését (.exe, .txt stb.)", "extensions",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v HideFileExt /t REG_DWORD /d 0 /f',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v HideFileExt /t REG_DWORD /d 1 /f',
            on_msg="Fájlkiterjesztések megjelenítve!", off_msg="Fájlkiterjesztések elrejtve.")
        self.make_toggle_row(inner, "👁️  Rejtett fájlok megjelenítése", "Rejtett fájlok és mappák megjelenítése", "hiddenfiles",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v Hidden /t REG_DWORD /d 1 /f',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v Hidden /t REG_DWORD /d 2 /f',
            on_msg="Rejtett fájlok megjelenítve!", off_msg="Rejtett fájlok elrejtve.")
        self.make_toggle_row(inner, "🖥️  Ez a gép megjelenítése asztalon", "Számítógép ikon megjelenítése az asztalon", "mypc",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\HideDesktopIcons\\NewStartPanel" /v {20D04FE0-3AEA-1069-A2D8-08002B30309D} /t REG_DWORD /d 0 /f',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\HideDesktopIcons\\NewStartPanel" /v {20D04FE0-3AEA-1069-A2D8-08002B30309D} /t REG_DWORD /d 1 /f',
            on_msg="Ez a gép ikon megjelent!", off_msg="Ez a gép ikon elrejtve.")
        self.section_label(inner, "📌  Tálca")
        self.make_toggle_row(inner, "🔍  Keresősáv elrejtése", "Keresősáv eltüntetése a tálcáról", "searchbar",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Search" /v SearchboxTaskbarMode /t REG_DWORD /d 0 /f',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Search" /v SearchboxTaskbarMode /t REG_DWORD /d 2 /f',
            on_msg="Keresősáv elrejtve!", off_msg="Keresősáv visszakapcsolva.")
        self.make_toggle_row(inner, "🤖  Cortana gomb elrejtése", "Cortana gomb eltüntetése a tálcáról", "cortana",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v ShowCortanaButton /t REG_DWORD /d 0 /f',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v ShowCortanaButton /t REG_DWORD /d 1 /f',
            on_msg="Cortana gomb elrejtve!", off_msg="Cortana gomb visszakapcsolva.")
        self.make_toggle_row(inner, "🗂️  Feladatnézet elrejtése", "Feladatnézet gomb eltüntetése a tálcáról", "taskview",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v ShowTaskViewButton /t REG_DWORD /d 0 /f',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v ShowTaskViewButton /t REG_DWORD /d 1 /f',
            on_msg="Feladatnézet elrejtve!", off_msg="Feladatnézet visszakapcsolva.")
        self.make_toggle_row(inner, "⌨️  Snap Assist kikapcsolása", "Ablakok illesztési segéd letiltása", "snap",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v EnableSnapAssistFlyout /t REG_DWORD /d 0 /f',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v EnableSnapAssistFlyout /t REG_DWORD /d 1 /f',
            on_msg="Snap Assist kikapcsolva!", off_msg="Snap Assist visszakapcsolva.")
        self.make_toggle_row(inner, "🔢  NumLock bekapcsolva induláskor", "Numpad automatikus bekapcsolása indításkor", "numlock",
            on_cmd='reg add "HKCU\\Control Panel\\Keyboard" /v InitialKeyboardIndicators /t REG_SZ /d 2 /f',
            off_cmd='reg add "HKCU\\Control Panel\\Keyboard" /v InitialKeyboardIndicators /t REG_SZ /d 0 /f',
            on_msg="NumLock bekapcsolva induláskor!", off_msg="NumLock kikapcsolva induláskor.")
        self.make_toggle_row(inner, "🔑  Sticky Keys letiltása", "Véletlenszerű Sticky Keys ablak letiltása", "stickykeys",
            on_cmd='reg add "HKCU\\Control Panel\\Accessibility\\StickyKeys" /v Flags /t REG_SZ /d 506 /f',
            off_cmd='reg add "HKCU\\Control Panel\\Accessibility\\StickyKeys" /v Flags /t REG_SZ /d 510 /f',
            on_msg="Sticky Keys letiltva!", off_msg="Sticky Keys visszakapcsolva.")
        self.make_button_row(inner, "🔄  Explorer újraindítása", "Tálca változások azonnal érvénybe lépnek", self.restart_explorer)
        tk.Frame(inner, bg=BG, height=16).pack()

    def build_security(self, parent):
        inner = self.make_scroll_frame(parent)
        self.section_label(inner, "🔒  Biztonság")
        self.make_toggle_row(inner, "🔥  Tűzfal", "Windows tűzfal be/kikapcsolása minden profilon", "firewall",
            on_cmd="netsh advfirewall set allprofiles state on",
            off_cmd="netsh advfirewall set allprofiles state off",
            on_msg="Tűzfal bekapcsolva!", off_msg="Tűzfal kikapcsolva!")
        self.make_toggle_row(inner, "🖥️  Távoli asztal (RDP)", "Remote Desktop Protocol engedélyezése/tiltása", "rdp",
            on_cmd='reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f && netsh advfirewall firewall set rule group="remote desktop" new enable=Yes',
            off_cmd='reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 1 /f',
            on_msg="Távoli asztal engedélyezve!", off_msg="Távoli asztal letiltva.")
        self.make_toggle_row(inner, "🛡️  UAC (felhasználói fiók felügyelet)", "User Account Control be/kikapcsolása", "uac",
            on_cmd='reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v EnableLUA /t REG_DWORD /d 1 /f',
            off_cmd='reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v EnableLUA /t REG_DWORD /d 0 /f',
            on_msg="UAC bekapcsolva!", off_msg="UAC kikapcsolva! (újraindítás szükséges)")
        self.make_toggle_row(inner, "👥  Vendég fiók letiltása", "Vendég felhasználói fiók letiltása", "guest",
            on_cmd='net user Guest /active:no',
            off_cmd='net user Guest /active:yes',
            on_msg="Vendég fiók letiltva!", off_msg="Vendég fiók engedélyezve.")
        self.make_toggle_row(inner, "🖨️  Nyomtató spooler", "Print Spooler szolgáltatás – ha nincs nyomtatód, kikapcsolható", "spooler",
            on_cmd="sc start Spooler && sc config Spooler start= auto",
            off_cmd="sc stop Spooler && sc config Spooler start= disabled",
            on_msg="Nyomtató spooler bekapcsolva!", off_msg="Nyomtató spooler kikapcsolva.")
        self.section_label(inner, "🔑  Bejelentkezés")
        self.make_button_row(inner, "🔑  Automatikus bejelentkezés beállítása", "Jelszó nélküli automatikus bejelentkezés", self.setup_autologin)
        self.make_button_row(inner, "🔒  Automatikus bejelentkezés törlése", "Automatikus bejelentkezés kikapcsolása", self.remove_autologin)
        self.make_button_row(inner, "🔐  Jelszó megváltoztatása", "Aktuális felhasználó jelszavának megváltoztatása", self.change_password)
        tk.Frame(inner, bg=BG, height=16).pack()

    def build_network(self, parent):
        inner = self.make_scroll_frame(parent)
        self.section_label(inner, "🌐  DNS beállítás")
        self.make_button_row(inner, "☁️  Google DNS (8.8.8.8)", "Gyors és megbízható Google DNS beállítása", self.set_google_dns)
        self.make_button_row(inner, "⚡  Cloudflare DNS (1.1.1.1)", "Leggyorsabb DNS – Cloudflare beállítása", self.set_cloudflare_dns)
        self.make_button_row(inner, "🔵  OpenDNS (208.67.222.222)", "OpenDNS – szűréssel és védelemmel", self.set_opendns)
        self.make_button_row(inner, "🔄  Automatikus DNS visszaállítása", "DNS visszaállítása DHCP automatikusra", self.reset_dns)
        self.section_label(inner, "🔧  Hálózat")
        self.make_button_row(inner, "🔄  Hálózati adapter reset", "TCP/IP, Winsock és DNS cache teljes reset", self.reset_network)
        self.make_button_row(inner, "📊  Hálózati információk", "IP cím, DNS, átjáró megjelenítése", self.show_network_info)
        self.make_button_row(inner, "🔍  Hálózati sebesség teszt", "Megnyitja a speedtest.net oldalt", lambda: subprocess.Popen("start https://speedtest.net", shell=True))
        self.make_toggle_row(inner, "🌍  IPv6 kikapcsolása", "IPv6 protokoll letiltása minden adapteren", "ipv6",
            on_cmd='reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip6\\Parameters" /v DisabledComponents /t REG_DWORD /d 255 /f',
            off_cmd='reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip6\\Parameters" /v DisabledComponents /t REG_DWORD /d 0 /f',
            on_msg="IPv6 kikapcsolva! (újraindítás után)", off_msg="IPv6 visszakapcsolva!")
        self.make_toggle_row(inner, "📶  WiFi letiltása", "Wireless hálózati adapter letiltása", "wifi",
            on_cmd='netsh interface set interface "Wi-Fi" disable',
            off_cmd='netsh interface set interface "Wi-Fi" enable',
            on_msg="WiFi letiltva!", off_msg="WiFi visszakapcsolva.")
        self.make_toggle_row(inner, "🦷  Bluetooth letiltása", "Bluetooth szolgáltatás kikapcsolása", "bluetooth",
            on_cmd="sc stop bthserv && sc config bthserv start= disabled",
            off_cmd="sc config bthserv start= auto && sc start bthserv",
            on_msg="Bluetooth letiltva!", off_msg="Bluetooth visszakapcsolva.")
        self.section_label(inner, "🔒  Megosztás")
        self.make_button_row(inner, "📂  Megosztott mappák listája", "Jelenleg megosztott mappák megjelenítése", lambda: self.run_cmd_output("net share", "Megosztott mappák:"))
        self.make_button_row(inner, "🔌  Aktív kapcsolatok", "Jelenleg aktív hálózati kapcsolatok listája", lambda: self.run_cmd_output("netstat -an | findstr ESTABLISHED", "Aktív kapcsolatok:"))
        tk.Frame(inner, bg=BG, height=16).pack()

    def build_system(self, parent):
        inner = self.make_scroll_frame(parent)
        self.section_label(inner, "ℹ️  Rendszerinformációk")
        info_frame = tk.Frame(inner, bg=SURFACE, highlightbackground=BORDER, highlightthickness=1)
        info_frame.pack(fill="x", padx=20, pady=3)
        self.info_text = tk.Label(info_frame, text="Betöltés...", font=("Consolas", 9), bg=SURFACE, fg=TEXT2, justify="left", anchor="w")
        self.info_text.pack(fill="x", padx=14, pady=12)
        tk.Button(info_frame, text="🔄 Frissítés", font=("Consolas", 9), bg=ACCENT, fg="#fff",
                  relief="flat", cursor="hand2", bd=0, padx=10, pady=4,
                  command=self.refresh_sysinfo).pack(anchor="e", padx=14, pady=(0,10))

        self.section_label(inner, "🖥️  Számítógép neve")
        name_frame = tk.Frame(inner, bg=SURFACE, highlightbackground=BORDER, highlightthickness=1)
        name_frame.pack(fill="x", padx=20, pady=3)
        tk.Label(name_frame, text="Új számítógépnév:", font=("Consolas", 10), bg=SURFACE, fg=TEXT).pack(anchor="w", padx=14, pady=(10,4))
        self.pc_name_var = tk.StringVar()
        tk.Entry(name_frame, textvariable=self.pc_name_var, font=("Consolas", 11), bg=SURFACE2, fg=TEXT, insertbackground=TEXT, relief="flat").pack(fill="x", padx=14, pady=(0,6))
        tk.Button(name_frame, text="▶ Átnevezés", font=("Consolas", 10), bg=ACCENT, fg="#fff",
                  relief="flat", cursor="hand2", bd=0, padx=12, pady=6, command=self.rename_pc).pack(anchor="e", padx=14, pady=(0,10))

        self.section_label(inner, "⚡  Gyors műveletek")
        self.make_button_row(inner, "🔄  Újraindítás", "Számítógép azonnali újraindítása (5mp)", self.do_restart)
        self.make_button_row(inner, "⏹️  Leállítás", "Számítógép azonnali leállítása (5mp)", self.do_shutdown)
        self.make_button_row(inner, "😴  Alvó állapot", "Számítógép alvó módba helyezése", self.do_sleep)
        self.make_button_row(inner, "🔒  Zárolás", "Képernyő zárolása", lambda: subprocess.Popen("rundll32.exe user32.dll,LockWorkStation", shell=True))
        self.make_button_row(inner, "🚪  Kijelentkezés", "Felhasználó kijelentkezése", lambda: subprocess.Popen("shutdown /l", shell=True))

        self.section_label(inner, "🛠️  Rendszereszközök")
        self.make_button_row(inner, "⚙️  Feladatkezelő megnyitása", "Windows Feladatkezelő megnyitása", lambda: subprocess.Popen("taskmgr", shell=True))
        self.make_button_row(inner, "🖥️  Eszközkezelő megnyitása", "Windows Eszközkezelő megnyitása", lambda: subprocess.Popen("devmgmt.msc", shell=True))
        self.make_button_row(inner, "💾  Lemezkezelő megnyitása", "Windows Lemezkezelő megnyitása", lambda: subprocess.Popen("diskmgmt.msc", shell=True))
        self.make_button_row(inner, "🔧  Rendszerkonfiguráció (msconfig)", "msconfig megnyitása", lambda: subprocess.Popen("msconfig", shell=True))
        self.make_button_row(inner, "📋  Eseménynapló megnyitása", "Windows Event Viewer megnyitása", lambda: subprocess.Popen("eventvwr.msc", shell=True))
        self.make_button_row(inner, "🔍  Rendszer információk", "Részletes rendszer információk (msinfo32)", lambda: subprocess.Popen("msinfo32", shell=True))
        self.make_button_row(inner, "🛡️  Windows Defender megnyitása", "Windows Security Center megnyitása", lambda: subprocess.Popen("start windowsdefender:", shell=True))
        self.make_button_row(inner, "🔄  Windows Update megnyitása", "Windows Update beállítások megnyitása", lambda: subprocess.Popen("start ms-settings:windowsupdate", shell=True))
        self.make_button_row(inner, "🖥️  Képernyőfelbontás beállítása", "Megjelenítési beállítások megnyitása", lambda: subprocess.Popen("start ms-settings:display", shell=True))
        self.make_button_row(inner, "🔊  Hangbeállítások megnyitása", "Hang és mikrofon beállítások", lambda: subprocess.Popen("start ms-settings:sound", shell=True))

        self.section_label(inner, "🩺  Rendszerkarbantartás")
        self.make_button_row(inner, "🔍  SFC vizsgálat futtatása", "System File Checker – sérült rendszerfájlok javítása", lambda: self.run_cmd("sfc /scannow", "SFC vizsgálat kész!"))
        self.make_button_row(inner, "🔧  DISM javítás futtatása", "DISM – Windows képfájl javítása", lambda: self.run_cmd("DISM /Online /Cleanup-Image /RestoreHealth", "DISM javítás kész!"))
        self.make_button_row(inner, "💾  CHKDSK futtatása (C:)", "Lemezhibák ellenőrzése és javítása következő indításkor", lambda: self.run_cmd("chkdsk C: /f /r /x", "CHKDSK ütemezve! Indítsd újra a gépet."))
        tk.Frame(inner, bg=BG, height=16).pack()
        self.after(500, self.refresh_sysinfo)

    def build_services(self, parent):
        inner = self.make_scroll_frame(parent)
        self.section_label(inner, "⚙️  Windows Szolgáltatások")
        services = [
            ("🖨️  Nyomtató spooler", "Print Spooler – ha nincs nyomtatód, kikapcsolható", "svc_spooler", "Spooler"),
            ("📶  WLAN AutoConfig", "WiFi kezelő szolgáltatás", "svc_wlan", "WlanSvc"),
            ("🦷  Bluetooth", "Bluetooth támogatás", "svc_bt", "bthserv"),
            ("🔍  Windows Search", "Fájl indexelés és keresés", "svc_search", "WSearch"),
            ("📊  Telemetria (DiagTrack)", "Diagnosztikai adatgyűjtés", "svc_diagtrack", "DiagTrack"),
            ("🗺️  Geolocation", "Helymeghatározás szolgáltatás", "svc_geo", "lfsvc"),
            ("📱  Push értesítések (WpnService)", "Windows Push Notifications", "svc_wpn", "WpnService"),
            ("🔄  Windows Update", "Windows automatikus frissítés", "svc_wupdate", "wuauserv"),
            ("🎮  Xbox Live", "Xbox Live hálózati szolgáltatás", "svc_xbox", "XblNetApi"),
            ("☁️  OneDrive szinkronizálás", "OneDrive felhő szinkronizálás letiltása", "svc_onedrive", "OneSyncSvc"),
            ("🖥️  Remote Registry", "Távoli registry elérés – biztonsági kockázat", "svc_remotereg", "RemoteRegistry"),
            ("🔊  Windows Audio", "Hang szolgáltatás – ne kapcsold ki ha hangot használsz!", "svc_audio", "AudioSrv"),
        ]
        for label, desc, tid, svc in services:
            self.make_toggle_row(inner, label, desc, tid,
                on_fn=lambda s=svc, n=label: self.service_start(s, n),
                off_fn=lambda s=svc, n=label: self.service_stop(s, n))
        self.section_label(inner, "📋  Indítóprogramok")
        self.make_button_row(inner, "📋  Indítóprogramok kezelője", "Megnyitja a Feladatkezelő Indítás fülét", lambda: subprocess.Popen("taskmgr /0 /startup", shell=True))
        self.make_button_row(inner, "🔍  Indítóprogramok listája", "Megjeleníti az összes induló programot", self.list_startup_programs)
        tk.Frame(inner, bg=BG, height=16).pack()

    # ══════════════════════════════════════════════════
    # LOGIKA
    # ══════════════════════════════════════════════════

    def on_toggle(self, state, item):
        fn_key = "on_fn" if state else "off_fn"
        cmd_key = "on_cmd" if state else "off_cmd"
        msg_key = "on_msg" if state else "off_msg"
        if item.get(fn_key): threading.Thread(target=item[fn_key], daemon=True).start()
        elif item.get(cmd_key): self.run_cmd(item[cmd_key], item.get(msg_key, "Kész!"))

    def run_cmd(self, cmd, success_msg):
        self.log("⏳ Futtatás...")
        def task():
            try:
                r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if r.returncode == 0: self.after(0, lambda: self.log(f"✅ {success_msg}"))
                else:
                    err = (r.stderr or r.stdout or "Ismeretlen hiba").strip()[:120]
                    self.after(0, lambda: self.log(f"❌ Hiba: {err}"))
            except Exception as e:
                self.after(0, lambda: self.log(f"❌ {str(e)[:120]}"))
        threading.Thread(target=task, daemon=True).start()

    def run_cmd_output(self, cmd, title):
        self.log(f"⏳ {title}")
        def task():
            try:
                r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                out = r.stdout.strip()[:500] or "Nincs találat"
                win = tk.Toplevel(self)
                win.title(title)
                win.configure(bg=SURFACE)
                win.geometry("600x400")
                txt = tk.Text(win, font=("Consolas", 9), bg=SURFACE2, fg=TEXT, relief="flat")
                txt.pack(fill="both", expand=True, padx=10, pady=10)
                txt.insert("end", out)
                txt.config(state="disabled")
            except Exception as e:
                self.after(0, lambda: self.log(f"❌ {e}"))
        threading.Thread(target=task, daemon=True).start()

    def ensure_choco(self):
        r = subprocess.run("choco --version", shell=True, capture_output=True, text=True)
        if r.returncode != 0:
            self.after(0, lambda: self.log("⏳ Chocolatey telepítése..."))
            cmd = 'powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString(\'https://community.chocolatey.org/install.ps1\'))"'
            return subprocess.run(cmd, shell=True, capture_output=True, text=True).returncode == 0
        return True

    def choco_install(self, package, success_msg):
        self.after(0, lambda: self.log(f"⏳ {package} telepítése..."))
        def task():
            if not self.ensure_choco():
                self.after(0, lambda: self.log("❌ Chocolatey telepítése sikertelen!"))
                return
            r = subprocess.run(f"choco install {package} -y", shell=True, capture_output=True, text=True)
            if r.returncode == 0: self.after(0, lambda: self.log(f"✅ {success_msg}"))
            else:
                err = (r.stderr or r.stdout or "Ismeretlen hiba").strip()[:120]
                self.after(0, lambda: self.log(f"❌ Hiba: {err}"))
        threading.Thread(target=task, daemon=True).start()

    def choco_uninstall(self, package, success_msg):
        self.after(0, lambda: self.log(f"⏳ {package} eltávolítása..."))
        def task():
            r = subprocess.run(f"choco uninstall {package} -y", shell=True, capture_output=True, text=True)
            if r.returncode == 0: self.after(0, lambda: self.log(f"✅ {success_msg}"))
            else:
                err = (r.stderr or r.stdout or "Ismeretlen hiba").strip()[:120]
                self.after(0, lambda: self.log(f"❌ Hiba: {err}"))
        threading.Thread(target=task, daemon=True).start()

    def service_start(self, svc, name):
        self.after(0, lambda: self.log(f"⏳ {name} elindítása..."))
        def task():
            r = subprocess.run(f"sc config {svc} start= auto && sc start {svc}", shell=True, capture_output=True, text=True)
            self.after(0, lambda: self.log(f"✅ {name} elindítva!" if r.returncode == 0 else f"❌ Hiba: {name}"))
        threading.Thread(target=task, daemon=True).start()

    def service_stop(self, svc, name):
        self.after(0, lambda: self.log(f"⏳ {name} leállítása..."))
        def task():
            r = subprocess.run(f"sc stop {svc} && sc config {svc} start= disabled", shell=True, capture_output=True, text=True)
            self.after(0, lambda: self.log(f"✅ {name} leállítva!" if r.returncode == 0 else f"❌ Hiba: {name}"))
        threading.Thread(target=task, daemon=True).start()

    def remove_bloatware(self):
        self.log("⏳ Bloatware eltávolítása...")
        apps = ["Microsoft.BingNews","Microsoft.BingWeather","Microsoft.GetHelp","Microsoft.Getstarted",
                "Microsoft.MicrosoftOfficeHub","Microsoft.MicrosoftSolitaireCollection","Microsoft.PowerAutomateDesktop",
                "Microsoft.SecHealthUI","Microsoft.People","Microsoft.Todos","Microsoft.WindowsAlarms",
                "Microsoft.WindowsCamera","microsoft.windowscommunicationsapps","Microsoft.WindowsFeedbackHub",
                "Microsoft.WindowsMaps","Microsoft.WindowsSoundRecorder","Microsoft.YourPhone",
                "Microsoft.ZuneMusic","Microsoft.ZuneVideo","MicrosoftTeams"]
        def task():
            removed = 0
            for app in apps:
                r = subprocess.run(f'powershell -Command "Get-AppxPackage *{app}* | Remove-AppxPackage"', shell=True, capture_output=True, text=True)
                if r.returncode == 0: removed += 1
            self.after(0, lambda: self.log(f"✅ Bloatware eltávolítva! ({removed} app)"))
        threading.Thread(target=task, daemon=True).start()

    def clear_browser_history(self):
        self.log("⏳ Böngésző cache törlése...")
        def task():
            paths = [
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache"),
                os.path.expandvars(r"%LOCALAPPDATA%\Mozilla\Firefox\Profiles"),
                os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache"),
            ]
            count = 0
            for p in paths:
                if os.path.exists(p):
                    for root, dirs, files in os.walk(p):
                        for f in files:
                            try: os.remove(os.path.join(root, f)); count += 1
                            except: pass
            self.after(0, lambda: self.log(f"✅ {count} cache fájl törölve!"))
        threading.Thread(target=task, daemon=True).start()

    def clean_temp(self):
        self.log("⏳ Ideiglenes fájlok törlése...")
        def task():
            count = 0
            for folder in [os.environ.get("TEMP",""), os.environ.get("TMP",""), r"C:\Windows\Temp"]:
                if not folder: continue
                for root, dirs, files in os.walk(folder):
                    for f in files:
                        try: os.remove(os.path.join(root, f)); count += 1
                        except: pass
            self.after(0, lambda: self.log(f"✅ {count} ideiglenes fájl törölve!"))
        threading.Thread(target=task, daemon=True).start()

    def free_ram(self):
        self.log("⏳ RAM felszabadítás...")
        def task():
            subprocess.run('powershell -Command "Get-Process | ForEach-Object { $_.MinWorkingSet = 1MB }"', shell=True, capture_output=True)
            self.after(0, lambda: self.log("✅ RAM felszabadítva!"))
        threading.Thread(target=task, daemon=True).start()

    def empty_recycle(self):
        self.log("⏳ Szemetes kiürítése...")
        def task():
            subprocess.run('powershell -Command "Clear-RecycleBin -Force"', shell=True, capture_output=True)
            self.after(0, lambda: self.log("✅ Szemetes kiürítve!"))
        threading.Thread(target=task, daemon=True).start()

    def clear_wu_cache(self):
        cmds = "net stop wuauserv && net stop cryptSvc && net stop bits && net stop msiserver && rmdir /s /q C:\\Windows\\SoftwareDistribution && net start wuauserv && net start cryptSvc && net start bits && net start msiserver"
        self.run_cmd(cmds, "Windows Update cache törölve!")

    def show_disk_usage(self):
        def task():
            info = ""
            for drive in ["C:", "D:", "E:", "F:"]:
                try:
                    usage = shutil.disk_usage(drive + "\\")
                    total = round(usage.total / (1024**3), 1)
                    used = round(usage.used / (1024**3), 1)
                    free = round(usage.free / (1024**3), 1)
                    pct = round(usage.used / usage.total * 100)
                    info += f"{drive}  {used}GB / {total}GB  ({free}GB szabad, {pct}% teli)\n"
                except: pass
            self.after(0, lambda: self.log(f"💾 {info.strip()[:200]}"))
        threading.Thread(target=task, daemon=True).start()

    def restart_explorer(self):
        self.log("⏳ Explorer újraindítása...")
        def task():
            subprocess.run("taskkill /f /im explorer.exe && start explorer.exe", shell=True, capture_output=True)
            self.after(0, lambda: self.log("✅ Explorer újraindítva!"))
        threading.Thread(target=task, daemon=True).start()

    def setup_autologin(self):
        win = tk.Toplevel(self)
        win.title("Automatikus bejelentkezés")
        win.configure(bg=SURFACE)
        win.geometry("380x200")
        win.resizable(False, False)
        tk.Label(win, text="Felhasználónév:", font=("Consolas", 10), bg=SURFACE, fg=TEXT).pack(anchor="w", padx=20, pady=(16,2))
        user_var = tk.StringVar()
        tk.Entry(win, textvariable=user_var, font=("Consolas", 11), bg=SURFACE2, fg=TEXT, insertbackground=TEXT, relief="flat").pack(fill="x", padx=20)
        tk.Label(win, text="Jelszó:", font=("Consolas", 10), bg=SURFACE, fg=TEXT).pack(anchor="w", padx=20, pady=(10,2))
        pass_var = tk.StringVar()
        tk.Entry(win, textvariable=pass_var, show="*", font=("Consolas", 11), bg=SURFACE2, fg=TEXT, insertbackground=TEXT, relief="flat").pack(fill="x", padx=20)
        def do_autologin():
            u, p = user_var.get(), pass_var.get()
            if not u: return
            for c in [f'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon" /v AutoAdminLogon /t REG_SZ /d 1 /f',
                      f'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon" /v DefaultUserName /t REG_SZ /d "{u}" /f',
                      f'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon" /v DefaultPassword /t REG_SZ /d "{p}" /f']:
                subprocess.run(c, shell=True, capture_output=True)
            self.log("✅ Automatikus bejelentkezés beállítva!")
            win.destroy()
        tk.Button(win, text="✅ Mentés", font=("Consolas", 10), bg=ACCENT, fg="#fff", relief="flat", cursor="hand2", bd=0, padx=14, pady=6, command=do_autologin).pack(pady=14)

    def remove_autologin(self):
        for c in ['reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon" /v AutoAdminLogon /t REG_SZ /d 0 /f',
                  'reg delete "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon" /v DefaultPassword /f']:
            subprocess.run(c, shell=True, capture_output=True)
        self.log("✅ Automatikus bejelentkezés törölve!")

    def change_password(self):
        win = tk.Toplevel(self)
        win.title("Jelszó megváltoztatása")
        win.configure(bg=SURFACE)
        win.geometry("380x160")
        win.resizable(False, False)
        tk.Label(win, text="Új jelszó:", font=("Consolas", 10), bg=SURFACE, fg=TEXT).pack(anchor="w", padx=20, pady=(16,2))
        pass_var = tk.StringVar()
        tk.Entry(win, textvariable=pass_var, show="*", font=("Consolas", 11), bg=SURFACE2, fg=TEXT, insertbackground=TEXT, relief="flat").pack(fill="x", padx=20)
        def do_change():
            p = pass_var.get()
            r = subprocess.run(f'net user %USERNAME% "{p}"', shell=True, capture_output=True, text=True)
            self.log("✅ Jelszó megváltoztatva!" if r.returncode == 0 else "❌ Hiba a jelszó változtatásnál!")
            win.destroy()
        tk.Button(win, text="✅ Mentés", font=("Consolas", 10), bg=ACCENT, fg="#fff", relief="flat", cursor="hand2", bd=0, padx=14, pady=6, command=do_change).pack(pady=14)

    def set_google_dns(self): self.run_cmd('powershell -Command "Get-NetAdapter | Where-Object {$_.Status -eq \'Up\'} | ForEach-Object { Set-DnsClientServerAddress -InterfaceIndex $_.InterfaceIndex -ServerAddresses (\'8.8.8.8\',\'8.8.4.4\') }"', "Google DNS beállítva!")
    def set_cloudflare_dns(self): self.run_cmd('powershell -Command "Get-NetAdapter | Where-Object {$_.Status -eq \'Up\'} | ForEach-Object { Set-DnsClientServerAddress -InterfaceIndex $_.InterfaceIndex -ServerAddresses (\'1.1.1.1\',\'1.0.0.1\') }"', "Cloudflare DNS beállítva!")
    def set_opendns(self): self.run_cmd('powershell -Command "Get-NetAdapter | Where-Object {$_.Status -eq \'Up\'} | ForEach-Object { Set-DnsClientServerAddress -InterfaceIndex $_.InterfaceIndex -ServerAddresses (\'208.67.222.222\',\'208.67.220.220\') }"', "OpenDNS beállítva!")
    def reset_dns(self): self.run_cmd('powershell -Command "Get-NetAdapter | Where-Object {$_.Status -eq \'Up\'} | ForEach-Object { Set-DnsClientServerAddress -InterfaceIndex $_.InterfaceIndex -ResetServerAddresses }"', "DNS visszaállítva automatikusra!")
    def reset_network(self): self.run_cmd("netsh int ip reset && netsh winsock reset && ipconfig /flushdns", "Hálózat resetelve! Újraindítás ajánlott.")

    def show_network_info(self):
        def task():
            try:
                hostname = socket.gethostname()
                ip = socket.gethostbyname(hostname)
                r = subprocess.run("ipconfig /all", shell=True, capture_output=True, text=True)
                dns = ""
                for line in r.stdout.splitlines():
                    if "DNS Servers" in line or "DNS-kiszolgálók" in line:
                        dns = line.split(":")[-1].strip()
                        break
                self.after(0, lambda: self.log(f"🌐 IP: {ip} | DNS: {dns} | Gép: {hostname}"))
            except Exception as e:
                self.after(0, lambda: self.log(f"❌ {e}"))
        threading.Thread(target=task, daemon=True).start()

    def refresh_sysinfo(self):
        def task():
            try:
                cpu = subprocess.run('wmic cpu get Name /value', shell=True, capture_output=True, text=True).stdout.strip().split("=")[-1].strip()
                ram_bytes = subprocess.run('wmic computersystem get TotalPhysicalMemory /value', shell=True, capture_output=True, text=True).stdout.strip().split("=")[-1].strip()
                ram_gb = round(int(ram_bytes) / (1024**3), 1) if ram_bytes.isdigit() else "?"
                disk = subprocess.run('wmic logicaldisk where "DeviceID=\'C:\'" get Size,FreeSpace /value', shell=True, capture_output=True, text=True).stdout
                free = size = 0
                for line in disk.splitlines():
                    if "FreeSpace=" in line: free = int(line.split("=")[-1].strip() or 0)
                    if "Size=" in line and "Free" not in line: size = int(line.split("=")[-1].strip() or 0)
                gpu = subprocess.run('wmic path win32_VideoController get Name /value', shell=True, capture_output=True, text=True).stdout.strip().split("=")[-1].strip()
                hostname = socket.gethostname()
                os_ver = platform.version()
                info = (f"💻  Gép neve:   {hostname}\n"
                        f"🖥️  CPU:        {cpu[:55]}\n"
                        f"🎮  GPU:        {gpu[:55]}\n"
                        f"🧠  RAM:        {ram_gb} GB\n"
                        f"💾  Lemez C:    {round(free/(1024**3),1)} GB szabad / {round(size/(1024**3),1)} GB\n"
                        f"🪟  Windows:    {os_ver[:45]}")
                self.after(0, lambda: self.info_text.config(text=info))
            except Exception as e:
                self.after(0, lambda: self.info_text.config(text=f"Hiba: {e}"))
        threading.Thread(target=task, daemon=True).start()

    def rename_pc(self):
        name = self.pc_name_var.get().strip()
        if not name: self.log("❌ Add meg az új nevet!"); return
        self.run_cmd(f'wmic computersystem where name="%computername%" call rename name="{name}"', f"Átnevezve: {name} (újraindítás után)")

    def list_startup_programs(self):
        self.run_cmd_output('reg query "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"', "Indítóprogramok listája")

    def do_restart(self): subprocess.Popen("shutdown /r /t 5", shell=True); self.log("🔄 Újraindítás 5mp múlva...")
    def do_shutdown(self): subprocess.Popen("shutdown /s /t 5", shell=True); self.log("⏹️ Leállítás 5mp múlva...")
    def do_sleep(self): subprocess.Popen("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True); self.log("😴 Alvó állapot...")

    def detect_states(self):
        detectors = {
            "darkmode": get_darkmode_state, "tracking": get_telemetry_state,
            "extensions": get_extensions_state, "gamemode": get_gamemode_state,
            "ads": get_ads_state, "updates": get_updates_state,
            "searchbar": get_searchbar_state, "cortana": get_cortana_state,
            "taskview": get_taskview_state, "notifications": get_notifications_state,
            "firewall": get_firewall_state, "rdp": get_rdp_state,
            "bgapps": get_bgapps_state, "hibernate": get_hibernate_state,
            "superfetch": get_superfetch_state, "wap": get_wap_state,
            "lockscreen": get_lockscreen_state, "uac": get_uac_state,
            "numlock": get_numlock_state, "hiddenfiles": get_hidden_files_state,
            "autoplay": get_autoplay_state, "errorreporting": get_error_reporting_state,
            "ipv6": get_ipv6_state,
        }
        for tid, fn in detectors.items():
            try:
                state = fn()
                if tid in self.toggles: self.toggles[tid].set_state(state)
            except: pass
        self.log("✅ Minden készen áll.")

    def ads_on(self):
        hosts_entry = "\n# WinSetup - reklámblokkolás\n127.0.0.1 ads.google.com\n127.0.0.1 doubleclick.net\n127.0.0.1 googleadservices.com\n127.0.0.1 googlesyndication.com\n127.0.0.1 adservice.google.com\n127.0.0.1 pagead2.googlesyndication.com\n"
        try:
            with open(r"C:\Windows\System32\drivers\etc\hosts", "r") as f:
                if "WinSetup" in f.read(): self.after(0, lambda: self.log("ℹ️ Már aktív.")); return
            with open(r"C:\Windows\System32\drivers\etc\hosts", "a") as f: f.write(hosts_entry)
            self.after(0, lambda: self.log("✅ Reklámok blokkolva!"))
        except Exception as e: self.after(0, lambda: self.log(f"❌ {e}"))

    def ads_off(self):
        try:
            with open(r"C:\Windows\System32\drivers\etc\hosts", "r") as f: lines = f.readlines()
            new_lines, skip = [], False
            for line in lines:
                if "WinSetup - reklámblokkolás" in line: skip = True
                if skip and line.strip() == "": skip = False; continue
                if not skip: new_lines.append(line)
            with open(r"C:\Windows\System32\drivers\etc\hosts", "w") as f: f.writelines(new_lines)
            self.after(0, lambda: self.log("✅ Reklámblokkolás kikapcsolva."))
        except Exception as e: self.after(0, lambda: self.log(f"❌ {e}"))

    def log(self, msg): self.log_var.set(msg)

if __name__ == "__main__":
    app = WinSetup()
    app.mainloop()
