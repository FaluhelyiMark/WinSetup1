import tkinter as tk
import subprocess
import threading
import os
import platform
import socket

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

def get_darkmode_state():
    return reg_read_dword("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize", "AppsUseLightTheme") == 0
def get_telemetry_state():
    return reg_read_dword("HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection", "AllowTelemetry") == 0
def get_extensions_state():
    return reg_read_dword("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "HideFileExt") == 0
def get_gamemode_state():
    return reg_read_dword("HKCU\\Software\\Microsoft\\GameBar", "AutoGameModeEnabled") == 1
def get_ads_state():
    try:
        with open(r"C:\Windows\System32\drivers\etc\hosts", "r") as f:
            return "WinSetup" in f.read()
    except: return False
def get_updates_state():
    return reg_read_dword("HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU", "NoAutoUpdate") == 1
def get_searchbar_state():
    return reg_read_dword("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Search", "SearchboxTaskbarMode") == 0
def get_cortana_state():
    return reg_read_dword("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "ShowCortanaButton") == 0
def get_taskview_state():
    return reg_read_dword("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "ShowTaskViewButton") == 0
def get_notifications_state():
    return reg_read_dword("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\PushNotifications", "ToastEnabled") == 0
def get_transparency_state():
    return reg_read_dword("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize", "EnableTransparency") == 0
def get_animations_state():
    return reg_read_dword("HKCU\\Control Panel\\Desktop\\WindowMetrics", "MinAnimate") == 0
def get_firewall_state():
    try:
        r = subprocess.run('netsh advfirewall show allprofiles state', shell=True, capture_output=True, text=True)
        return "ON" in r.stdout.upper()
    except: return True
def get_rdp_state():
    return reg_read_dword("HKLM\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server", "fDenyTSConnections") == 0
def get_ipv6_state():
    try:
        r = subprocess.run('netsh interface ipv6 show global', shell=True, capture_output=True, text=True)
        return r.returncode == 0
    except: return True
def get_bgapps_state():
    return reg_read_dword("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\BackgroundAccessApplications", "GlobalUserDisabled") == 1
def get_hibernate_state():
    try:
        r = subprocess.run("powercfg /a", shell=True, capture_output=True, text=True)
        return "Hibernation" in r.stdout or "Hibernálás" in r.stdout
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
        if self.command:
            self.command(self.state)

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
        for f in self.tab_frames.values():
            f.pack_forget()
        self.tab_frames[name].pack(fill="both", expand=True)
        for n, b in self.tab_buttons.items():
            b.config(bg=BG if n == name else SURFACE2, fg=ACCENT if n == name else TEXT2)

    def make_scroll_frame(self, parent):
        canvas = tk.Canvas(parent, bg=BG, highlightthickness=0)
        sb = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=BG)
        def on_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
        def on_canvas_resize(e):
            canvas.itemconfig(win_id, width=e.width)
        inner.bind("<Configure>", on_configure)
        win_id = canvas.create_window((0,0), window=inner, anchor="nw")
        canvas.bind("<Configure>", on_canvas_resize)
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
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

    # ── TABS ──────────────────────────────────────────

    def build_installer(self, parent):
        inner = self.make_scroll_frame(parent)
        self.section_label(inner, "📦  Alkalmazások")
        apps = [
            ("🌐  Chrome", "Google Chrome böngésző", "chrome", "googlechrome"),
            ("🎮  Roblox", "Roblox játékplatform", "roblox", "roblox"),
            ("📱  Viber", "Viber üzenetküldő", "viber", "viber"),
            ("💻  MobaXterm", "SSH/terminál kliens", "mobaxterm", "mobaxterm"),
            ("🗜️  7-Zip", "Legjobb tömörítő program", "7zip", "7zip"),
            ("🎬  VLC", "Videó- és médialejátszó", "vlc", "vlc"),
            ("💬  Discord", "Chat és közösségi platform", "discord", "discord"),
            ("🎮  Steam", "PC játékplatform", "steam", "steam"),
            ("🎵  Spotify", "Zenei streaming", "spotify", "spotify"),
        ]
        for label, desc, tid, pkg in apps:
            self.make_toggle_row(inner, label, desc, tid,
                on_fn=lambda p=pkg, n=label: self.choco_install(p, f"{n} telepítve!"),
                off_fn=lambda p=pkg, n=label: self.choco_uninstall(p, f"{n} eltávolítva!"))
        tk.Frame(inner, bg=BG, height=16).pack()

    def build_privacy(self, parent):
        inner = self.make_scroll_frame(parent)
        self.section_label(inner, "🛡️  Adatvédelem")
        self.make_toggle_row(inner, "🚫  Reklámblokkolás", "Hosts fájl módosítással blokkolja a hirdetési szervereket", "ads",
            on_fn=self.ads_on, off_fn=self.ads_off)
        self.make_toggle_row(inner, "🖨️  Nyomkövetés letiltása", "Windows telemetria és diagnosztikai adatgyűjtés kikapcsolása", "tracking",
            on_cmd='reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f && sc config DiagTrack start= disabled && sc stop DiagTrack',
            off_cmd='reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 1 /f && sc config DiagTrack start= auto && sc start DiagTrack',
            on_msg="Nyomkövetés letiltva!", off_msg="Nyomkövetés visszakapcsolva.")
        self.make_toggle_row(inner, "🔔  Értesítések kikapcsolása", "Toast értesítések letiltása Windows 10-en", "notifications",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\PushNotifications" /v ToastEnabled /t REG_DWORD /d 0 /f',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\PushNotifications" /v ToastEnabled /t REG_DWORD /d 1 /f',
            on_msg="Értesítések kikapcsolva!", off_msg="Értesítések visszakapcsolva.")
        self.make_toggle_row(inner, "🔄  Automatikus frissítések", "Windows Update automatikus letöltés kikapcsolása", "updates",
            on_cmd='reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" /v NoAutoUpdate /t REG_DWORD /d 0 /f',
            off_cmd='reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" /v NoAutoUpdate /t REG_DWORD /d 1 /f',
            on_msg="Automatikus frissítések kikapcsolva!", off_msg="Automatikus frissítések visszakapcsolva.")
        self.section_label(inner, "🗑️  Bloatware")
        self.make_button_row(inner, "🗑️  Bloatware eltávolítása", "Bing, Weather, Office Hub, Solitaire, People, Teams és más felesleges appok törlése", self.remove_bloatware)
        tk.Frame(inner, bg=BG, height=16).pack()

    def build_performance(self, parent):
        inner = self.make_scroll_frame(parent)
        self.section_label(inner, "⚡  Teljesítmény")
        self.make_toggle_row(inner, "🎯  Játék optimalizálás", "Game Mode + nagy teljesítményű energiaséma bekapcsolása", "gamemode",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\GameBar" /v AutoGameModeEnabled /t REG_DWORD /d 1 /f && powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\GameBar" /v AutoGameModeEnabled /t REG_DWORD /d 0 /f && powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e',
            on_msg="Játék optimalizálás bekapcsolva!", off_msg="Játék optimalizálás kikapcsolva.")
        self.make_toggle_row(inner, "💤  Hibernálás", "Hibernálás engedélyezése/tiltása", "hibernate",
            on_cmd="powercfg /hibernate on",
            off_cmd="powercfg /hibernate off",
            on_msg="Hibernálás bekapcsolva!", off_msg="Hibernálás kikapcsolva.")
        self.make_toggle_row(inner, "🖼️  Vizuális effektek kikapcsolása", "Animációk, árnyékok, átmenetek letiltása – gyorsabb rendszer", "visualfx",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" /v VisualFXSetting /t REG_DWORD /d 2 /f && reg add "HKCU\\Control Panel\\Desktop" /v UserPreferencesMask /t REG_BINARY /d 9012038010000000 /f',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" /v VisualFXSetting /t REG_DWORD /d 0 /f',
            on_msg="Vizuális effektek kikapcsolva!", off_msg="Vizuális effektek visszakapcsolva.")
        self.make_toggle_row(inner, "📱  Háttér appok letiltása", "Háttérben futó alkalmazások globális letiltása", "bgapps",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\BackgroundAccessApplications" /v GlobalUserDisabled /t REG_DWORD /d 1 /f',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\BackgroundAccessApplications" /v GlobalUserDisabled /t REG_DWORD /d 0 /f',
            on_msg="Háttér appok letiltva!", off_msg="Háttér appok visszakapcsolva.")
        self.section_label(inner, "🧹  Karbantartás")
        self.make_button_row(inner, "🗑️  Ideiglenes fájlok törlése", "Temp mappák kiürítése – felszabadít helyet a lemezen", self.clean_temp)
        self.make_button_row(inner, "💾  RAM felszabadítás", "Felesleges háttérfolyamatok memóriájának felszabadítása", self.free_ram)
        tk.Frame(inner, bg=BG, height=16).pack()

    def build_appearance(self, parent):
        inner = self.make_scroll_frame(parent)
        self.section_label(inner, "🎨  Megjelenés")
        self.make_toggle_row(inner, "🌙  Sötét mód", "Windows 10 rendszer és alkalmazások sötét témája", "darkmode",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v AppsUseLightTheme /t REG_DWORD /d 0 /f && reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v SystemUsesLightTheme /t REG_DWORD /d 0 /f',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v AppsUseLightTheme /t REG_DWORD /d 1 /f && reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v SystemUsesLightTheme /t REG_DWORD /d 1 /f',
            on_msg="Sötét mód bekapcsolva!", off_msg="Világos mód visszakapcsolva.")
        self.make_toggle_row(inner, "💎  Átlátszóság kikapcsolása", "Ablakok és tálca átlátszóság effektjének letiltása", "transparency",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v EnableTransparency /t REG_DWORD /d 0 /f',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v EnableTransparency /t REG_DWORD /d 1 /f',
            on_msg="Átlátszóság kikapcsolva!", off_msg="Átlátszóság visszakapcsolva.")
        self.make_toggle_row(inner, "✨  Animációk kikapcsolása", "Ablakok nyitási/zárási animációinak letiltása", "animations",
            on_cmd='reg add "HKCU\\Control Panel\\Desktop\\WindowMetrics" /v MinAnimate /t REG_SZ /d 0 /f',
            off_cmd='reg add "HKCU\\Control Panel\\Desktop\\WindowMetrics" /v MinAnimate /t REG_SZ /d 1 /f',
            on_msg="Animációk kikapcsolva!", off_msg="Animációk visszakapcsolva.")
        self.make_toggle_row(inner, "📄  Fájlkiterjesztések", "Megmutatja a fájlok kiterjesztését (.exe, .txt stb.)", "extensions",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v HideFileExt /t REG_DWORD /d 0 /f',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v HideFileExt /t REG_DWORD /d 1 /f',
            on_msg="Fájlkiterjesztések megjelenítve!", off_msg="Fájlkiterjesztések elrejtve.")
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
            off_cmd='reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 1 /f && netsh advfirewall firewall set rule group="remote desktop" new enable=No',
            on_msg="Távoli asztal engedélyezve!", off_msg="Távoli asztal letiltva.")
        self.section_label(inner, "🔑  Bejelentkezés")
        self.make_button_row(inner, "🔑  Automatikus bejelentkezés", "Jelszó nélküli automatikus bejelentkezés beállítása", self.setup_autologin)
        self.make_button_row(inner, "🔒  Automatikus bejelentkezés törlése", "Automatikus bejelentkezés kikapcsolása", self.remove_autologin)
        tk.Frame(inner, bg=BG, height=16).pack()

    def build_network(self, parent):
        inner = self.make_scroll_frame(parent)
        self.section_label(inner, "🌐  DNS beállítás")
        self.make_button_row(inner, "☁️  Google DNS", "DNS szerver beállítása Google-re (8.8.8.8 / 8.8.4.4)", self.set_google_dns)
        self.make_button_row(inner, "⚡  Cloudflare DNS", "DNS szerver beállítása Cloudflare-re (1.1.1.1 / 1.0.0.1) – gyorsabb", self.set_cloudflare_dns)
        self.make_button_row(inner, "🔄  Automatikus DNS visszaállítása", "DNS visszaállítása automatikusra (DHCP)", self.reset_dns)
        self.section_label(inner, "🔧  Hálózat")
        self.make_button_row(inner, "🔄  Hálózati adapter reset", "TCP/IP és DNS cache törlése, hálózat újraindítása", self.reset_network)
        self.make_toggle_row(inner, "🌍  IPv6 kikapcsolása", "IPv6 protokoll letiltása minden hálózati adapteren", "ipv6",
            on_cmd='reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip6\\Parameters" /v DisabledComponents /t REG_DWORD /d 255 /f',
            off_cmd='reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip6\\Parameters" /v DisabledComponents /t REG_DWORD /d 0 /f',
            on_msg="IPv6 kikapcsolva! (újraindítás után)", off_msg="IPv6 visszakapcsolva! (újraindítás után)")
        tk.Frame(inner, bg=BG, height=16).pack()

    def build_system(self, parent):
        inner = self.make_scroll_frame(parent)
        self.section_label(inner, "ℹ️  Rendszerinformációk")

        info_frame = tk.Frame(inner, bg=SURFACE, highlightbackground=BORDER, highlightthickness=1)
        info_frame.pack(fill="x", padx=20, pady=3)
        self.info_text = tk.Label(info_frame, text="Betöltés...", font=("Consolas", 9),
                                   bg=SURFACE, fg=TEXT2, justify="left", anchor="w")
        self.info_text.pack(fill="x", padx=14, pady=12)
        tk.Button(info_frame, text="🔄 Frissítés", font=("Consolas", 9), bg=ACCENT, fg="#fff",
                  relief="flat", cursor="hand2", bd=0, padx=10, pady=4,
                  command=self.refresh_sysinfo).pack(anchor="e", padx=14, pady=(0,10))

        self.section_label(inner, "🖥️  Számítógép neve")
        name_frame = tk.Frame(inner, bg=SURFACE, highlightbackground=BORDER, highlightthickness=1)
        name_frame.pack(fill="x", padx=20, pady=3)
        tk.Label(name_frame, text="Új számítógépnév:", font=("Consolas", 10), bg=SURFACE, fg=TEXT).pack(anchor="w", padx=14, pady=(10,4))
        self.pc_name_var = tk.StringVar()
        entry = tk.Entry(name_frame, textvariable=self.pc_name_var, font=("Consolas", 11),
                         bg=SURFACE2, fg=TEXT, insertbackground=TEXT, relief="flat",
                         highlightbackground=BORDER, highlightthickness=1)
        entry.pack(fill="x", padx=14, pady=(0,6))
        tk.Button(name_frame, text="▶ Átnevezés", font=("Consolas", 10), bg=ACCENT, fg="#fff",
                  relief="flat", cursor="hand2", bd=0, padx=12, pady=6,
                  command=self.rename_pc).pack(anchor="e", padx=14, pady=(0,10))

        self.section_label(inner, "⚡  Gyors műveletek")
        self.make_button_row(inner, "🔄  Újraindítás", "Számítógép azonnali újraindítása", self.do_restart)
        self.make_button_row(inner, "⏹️  Leállítás", "Számítógép azonnali leállítása", self.do_shutdown)
        self.make_button_row(inner, "😴  Alvó állapot", "Számítógép alvó módba helyezése", self.do_sleep)
        tk.Frame(inner, bg=BG, height=16).pack()

        self.after(500, self.refresh_sysinfo)

    # ── LOGIKA ────────────────────────────────────────

    def on_toggle(self, state, item):
        fn_key = "on_fn" if state else "off_fn"
        cmd_key = "on_cmd" if state else "off_cmd"
        msg_key = "on_msg" if state else "off_msg"
        if item.get(fn_key):
            threading.Thread(target=item[fn_key], daemon=True).start()
        elif item.get(cmd_key):
            self.run_cmd(item[cmd_key], item.get(msg_key, "Kész!"))

    def run_cmd(self, cmd, success_msg):
        self.log("⏳ Futtatás...")
        def task():
            try:
                r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if r.returncode == 0:
                    self.after(0, lambda: self.log(f"✅ {success_msg}"))
                else:
                    err = (r.stderr or r.stdout or "Ismeretlen hiba").strip()[:120]
                    self.after(0, lambda: self.log(f"❌ Hiba: {err}"))
            except Exception as e:
                self.after(0, lambda: self.log(f"❌ {str(e)[:120]}"))
        threading.Thread(target=task, daemon=True).start()

    def ensure_choco(self):
        r = subprocess.run("choco --version", shell=True, capture_output=True, text=True)
        if r.returncode != 0:
            self.after(0, lambda: self.log("⏳ Chocolatey telepítése..."))
            cmd = 'powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString(\'https://community.chocolatey.org/install.ps1\'))"'
            r2 = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return r2.returncode == 0
        return True

    def choco_install(self, package, success_msg):
        self.after(0, lambda: self.log(f"⏳ {package} telepítése..."))
        def task():
            if not self.ensure_choco():
                self.after(0, lambda: self.log("❌ Chocolatey telepítése sikertelen!"))
                return
            r = subprocess.run(f"choco install {package} -y", shell=True, capture_output=True, text=True)
            if r.returncode == 0:
                self.after(0, lambda: self.log(f"✅ {success_msg}"))
            else:
                err = (r.stderr or r.stdout or "Ismeretlen hiba").strip()[:120]
                self.after(0, lambda: self.log(f"❌ Hiba: {err}"))
        threading.Thread(target=task, daemon=True).start()

    def choco_uninstall(self, package, success_msg):
        self.after(0, lambda: self.log(f"⏳ {package} eltávolítása..."))
        def task():
            r = subprocess.run(f"choco uninstall {package} -y", shell=True, capture_output=True, text=True)
            if r.returncode == 0:
                self.after(0, lambda: self.log(f"✅ {success_msg}"))
            else:
                err = (r.stderr or r.stdout or "Ismeretlen hiba").strip()[:120]
                self.after(0, lambda: self.log(f"❌ Hiba: {err}"))
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
            self.after(0, lambda: self.log(f"✅ Bloatware eltávolítva! ({removed} app törölve)"))
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
        win.geometry("360x200")
        win.resizable(False, False)
        tk.Label(win, text="Felhasználónév:", font=("Consolas", 10), bg=SURFACE, fg=TEXT).pack(anchor="w", padx=20, pady=(16,2))
        user_var = tk.StringVar()
        tk.Entry(win, textvariable=user_var, font=("Consolas", 11), bg=SURFACE2, fg=TEXT, insertbackground=TEXT, relief="flat").pack(fill="x", padx=20)
        tk.Label(win, text="Jelszó:", font=("Consolas", 10), bg=SURFACE, fg=TEXT).pack(anchor="w", padx=20, pady=(10,2))
        pass_var = tk.StringVar()
        tk.Entry(win, textvariable=pass_var, show="*", font=("Consolas", 11), bg=SURFACE2, fg=TEXT, insertbackground=TEXT, relief="flat").pack(fill="x", padx=20)
        def do_autologin():
            u = user_var.get()
            p = pass_var.get()
            if not u: return
            cmds = [
                f'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon" /v AutoAdminLogon /t REG_SZ /d 1 /f',
                f'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon" /v DefaultUserName /t REG_SZ /d "{u}" /f',
                f'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon" /v DefaultPassword /t REG_SZ /d "{p}" /f',
            ]
            for c in cmds:
                subprocess.run(c, shell=True, capture_output=True)
            self.log("✅ Automatikus bejelentkezés beállítva!")
            win.destroy()
        tk.Button(win, text="✅ Mentés", font=("Consolas", 10), bg=ACCENT, fg="#fff",
                  relief="flat", cursor="hand2", bd=0, padx=14, pady=6,
                  command=do_autologin).pack(pady=14)

    def remove_autologin(self):
        cmds = [
            'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon" /v AutoAdminLogon /t REG_SZ /d 0 /f',
            'reg delete "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon" /v DefaultPassword /f',
        ]
        for c in cmds:
            subprocess.run(c, shell=True, capture_output=True)
        self.log("✅ Automatikus bejelentkezés törölve!")

    def set_google_dns(self):
        self.run_cmd(
            'powershell -Command "Get-NetAdapter | Where-Object {$_.Status -eq \'Up\'} | ForEach-Object { Set-DnsClientServerAddress -InterfaceIndex $_.InterfaceIndex -ServerAddresses (\'8.8.8.8\',\'8.8.4.4\') }"',
            "Google DNS beállítva! (8.8.8.8 / 8.8.4.4)")

    def set_cloudflare_dns(self):
        self.run_cmd(
            'powershell -Command "Get-NetAdapter | Where-Object {$_.Status -eq \'Up\'} | ForEach-Object { Set-DnsClientServerAddress -InterfaceIndex $_.InterfaceIndex -ServerAddresses (\'1.1.1.1\',\'1.0.0.1\') }"',
            "Cloudflare DNS beállítva! (1.1.1.1 / 1.0.0.1)")

    def reset_dns(self):
        self.run_cmd(
            'powershell -Command "Get-NetAdapter | Where-Object {$_.Status -eq \'Up\'} | ForEach-Object { Set-DnsClientServerAddress -InterfaceIndex $_.InterfaceIndex -ResetServerAddresses }"',
            "DNS visszaállítva automatikusra!")

    def reset_network(self):
        cmds = "netsh int ip reset && netsh winsock reset && ipconfig /flushdns && ipconfig /release && ipconfig /renew"
        self.run_cmd(cmds, "Hálózat resetelve! Újraindítás ajánlott.")

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
                free_gb = round(free / (1024**3), 1)
                size_gb = round(size / (1024**3), 1)
                hostname = socket.gethostname()
                os_ver = platform.version()
                info = f"💻  Gép neve:  {hostname}\n🖥️  CPU:       {cpu[:50]}\n🧠  RAM:       {ram_gb} GB\n💾  Lemez C:   {free_gb} GB szabad / {size_gb} GB\n🪟  Windows:   {os_ver[:40]}"
                self.after(0, lambda: self.info_text.config(text=info))
            except Exception as e:
                self.after(0, lambda: self.info_text.config(text=f"Hiba: {e}"))
        threading.Thread(target=task, daemon=True).start()

    def rename_pc(self):
        name = self.pc_name_var.get().strip()
        if not name:
            self.log("❌ Add meg az új nevet!")
            return
        self.run_cmd(f'wmic computersystem where name="%computername%" call rename name="{name}"',
                     f"Számítógép átnevezve: {name} (újraindítás után lép életbe)")

    def do_restart(self):
        subprocess.Popen("shutdown /r /t 5", shell=True)
        self.log("🔄 Újraindítás 5 másodperc múlva...")

    def do_shutdown(self):
        subprocess.Popen("shutdown /s /t 5", shell=True)
        self.log("⏹️ Leállítás 5 másodperc múlva...")

    def do_sleep(self):
        subprocess.Popen("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
        self.log("😴 Alvó állapot...")

    def detect_states(self):
        detectors = {
            "darkmode": get_darkmode_state,
            "tracking": get_telemetry_state,
            "extensions": get_extensions_state,
            "gamemode": get_gamemode_state,
            "ads": get_ads_state,
            "updates": get_updates_state,
            "searchbar": get_searchbar_state,
            "cortana": get_cortana_state,
            "taskview": get_taskview_state,
            "notifications": get_notifications_state,
            "firewall": get_firewall_state,
            "rdp": get_rdp_state,
            "bgapps": get_bgapps_state,
            "hibernate": get_hibernate_state,
        }
        for tid, fn in detectors.items():
            try:
                state = fn()
                if tid in self.toggles:
                    self.toggles[tid].set_state(state)
            except: pass
        self.log("✅ Minden készen áll.")

    def ads_on(self):
        hosts_entry = "\n# WinSetup - reklámblokkolás\n127.0.0.1 ads.google.com\n127.0.0.1 doubleclick.net\n127.0.0.1 googleadservices.com\n127.0.0.1 googlesyndication.com\n127.0.0.1 adservice.google.com\n127.0.0.1 pagead2.googlesyndication.com\n"
        try:
            with open(r"C:\Windows\System32\drivers\etc\hosts", "r") as f:
                if "WinSetup" in f.read():
                    self.after(0, lambda: self.log("ℹ️ Reklámblokkolás már aktív.")); return
            with open(r"C:\Windows\System32\drivers\etc\hosts", "a") as f:
                f.write(hosts_entry)
            self.after(0, lambda: self.log("✅ Reklámok blokkolva!"))
        except Exception as e:
            self.after(0, lambda: self.log(f"❌ Hiba: {e}"))

    def ads_off(self):
        try:
            with open(r"C:\Windows\System32\drivers\etc\hosts", "r") as f:
                lines = f.readlines()
            new_lines, skip = [], False
            for line in lines:
                if "WinSetup - reklámblokkolás" in line: skip = True
                if skip and line.strip() == "": skip = False; continue
                if not skip: new_lines.append(line)
            with open(r"C:\Windows\System32\drivers\etc\hosts", "w") as f:
                f.writelines(new_lines)
            self.after(0, lambda: self.log("✅ Reklámblokkolás kikapcsolva."))
        except Exception as e:
            self.after(0, lambda: self.log(f"❌ Hiba: {e}"))

    def log(self, msg):
        self.log_var.set(msg)

if __name__ == "__main__":
    app = WinSetup()
    app.mainloop()
