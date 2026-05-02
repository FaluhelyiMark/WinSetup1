import tkinter as tk
import subprocess
import threading
import os

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
WARNING = "#ffa94d"
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

def get_defender_state():
    return reg_read_dword("HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows Defender", "DisableAntiSpyware") == 1

def get_updates_state():
    return reg_read_dword("HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU", "NoAutoUpdate") == 1

def get_hibernate_state():
    try:
        r = subprocess.run("powercfg /a", shell=True, capture_output=True, text=True)
        return "Hibernálás" in r.stdout or "Hibernate" in r.stdout
    except: return False

def get_taskbar_left_state():
    return reg_read_dword("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "TaskbarAl") == 0

def get_searchbar_state():
    return reg_read_dword("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Search", "SearchboxTaskbarMode") == 0

def get_widgets_state():
    return reg_read_dword("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "TaskbarDa") == 0

class Toggle(tk.Canvas):
    def __init__(self, parent, state=False, command=None, **kwargs):
        super().__init__(parent, width=48, height=26, bg=SURFACE, highlightthickness=0, cursor="hand2", **kwargs)
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
        self.geometry("720x620")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.toggles = {}
        self.tab_frames = {}
        self.active_tab = None
        self.build_ui()
        self.after(300, self.detect_states)

    def build_ui(self):
        # Header
        header = tk.Frame(self, bg=SURFACE, height=52)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="⚡ WinSetup", font=("Consolas", 15, "bold"), bg=SURFACE, fg=ACCENT).pack(side="left", padx=20, pady=12)
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        # Tab bar
        self.tabbar = tk.Frame(self, bg=SURFACE2, height=42)
        self.tabbar.pack(fill="x")
        self.tabbar.pack_propagate(False)
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        # Log
        log_frame = tk.Frame(self, bg=SURFACE2, height=36)
        log_frame.pack(fill="x", side="bottom")
        log_frame.pack_propagate(False)
        self.log_var = tk.StringVar(value="Állapotok beolvasása...")
        tk.Label(log_frame, textvariable=self.log_var, font=("Consolas", 9), bg=SURFACE2, fg=TEXT2, anchor="w").pack(fill="x", padx=14, pady=8)
        tk.Frame(self, bg=BORDER, height=1).pack(side="bottom", fill="x")

        # Content area
        self.content = tk.Frame(self, bg=BG)
        self.content.pack(fill="both", expand=True)

        tabs = [
            ("📦 Telepítő", self.build_installer),
            ("🛡️ Adatvédelem", self.build_privacy),
            ("⚡ Teljesítmény", self.build_performance),
            ("🎨 Megjelenés", self.build_appearance),
        ]

        self.tab_buttons = {}
        for name, builder in tabs:
            frame = tk.Frame(self.content, bg=BG)
            self.tab_frames[name] = frame
            builder(frame)

            btn = tk.Label(self.tabbar, text=name, font=("Consolas", 10),
                          bg=SURFACE2, fg=TEXT2, cursor="hand2", padx=16, pady=10)
            btn.pack(side="left")
            btn.bind("<Button-1>", lambda e, n=name: self.show_tab(n))
            self.tab_buttons[name] = btn

        self.show_tab("📦 Telepítő")

    def show_tab(self, name):
        for n, f in self.tab_frames.items():
            f.pack_forget()
        self.tab_frames[name].pack(fill="both", expand=True)

        for n, b in self.tab_buttons.items():
            if n == name:
                b.config(bg=BG, fg=ACCENT)
            else:
                b.config(bg=SURFACE2, fg=TEXT2)
        self.active_tab = name

    def make_scroll_frame(self, parent):
        canvas = tk.Canvas(parent, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=BG)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
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
        tk.Label(info, text=desc, font=("Consolas", 9), bg=SURFACE, fg=TEXT2, anchor="w", wraplength=480).pack(anchor="w")

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
        tk.Label(info, text=desc, font=("Consolas", 9), bg=SURFACE, fg=TEXT2, anchor="w", wraplength=480).pack(anchor="w")
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
        self.make_toggle_row(inner, "🖨️  Nyomkövetés letiltása", "Windows telemetria és adatgyűjtés kikapcsolása", "tracking",
            on_cmd='reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f && sc config DiagTrack start= disabled && sc stop DiagTrack',
            off_cmd='reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 1 /f && sc config DiagTrack start= auto && sc start DiagTrack',
            on_msg="Nyomkövetés letiltva!", off_msg="Nyomkövetés visszakapcsolva.")
        self.make_toggle_row(inner, "🛡️  Windows Defender", "Valós idejű védelem ki/bekapcsolása (játéknál gyorsabb kikapcsolva)", "defender",
            on_cmd='reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows Defender" /v DisableAntiSpyware /t REG_DWORD /d 0 /f',
            off_cmd='reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows Defender" /v DisableAntiSpyware /t REG_DWORD /d 1 /f',
            on_msg="Windows Defender bekapcsolva!", off_msg="Windows Defender kikapcsolva.")
        self.make_toggle_row(inner, "🔄  Automatikus frissítések", "Windows Update automatikus letöltés ki/bekapcsolása", "updates",
            on_cmd='reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" /v NoAutoUpdate /t REG_DWORD /d 0 /f',
            off_cmd='reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" /v NoAutoUpdate /t REG_DWORD /d 1 /f',
            on_msg="Automatikus frissítések bekapcsolva!", off_msg="Automatikus frissítések kikapcsolva.")
        tk.Frame(inner, bg=BG, height=16).pack()

    def build_performance(self, parent):
        inner = self.make_scroll_frame(parent)
        self.section_label(inner, "⚡  Teljesítmény")
        self.make_toggle_row(inner, "🎯  Játék optimalizálás", "Game Mode + nagy teljesítményű energiaséma", "gamemode",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\GameBar" /v AutoGameModeEnabled /t REG_DWORD /d 1 /f && powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\GameBar" /v AutoGameModeEnabled /t REG_DWORD /d 0 /f && powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e',
            on_msg="Játék optimalizálás bekapcsolva!", off_msg="Játék optimalizálás kikapcsolva.")
        self.make_toggle_row(inner, "💤  Hibernálás", "Hibernálás engedélyezése/tiltása", "hibernate",
            on_cmd="powercfg /hibernate on",
            off_cmd="powercfg /hibernate off",
            on_msg="Hibernálás bekapcsolva!", off_msg="Hibernálás kikapcsolva.")
        self.section_label(inner, "🧹  Karbantartás")
        self.make_button_row(inner, "🗑️  Ideiglenes fájlok törlése", "Temp mappák kiürítése – felszabadít helyet a lemezen", self.clean_temp)
        self.make_button_row(inner, "💾  RAM felszabadítás", "Felesleges háttérfolyamatok memóriájának felszabadítása", self.free_ram)
        tk.Frame(inner, bg=BG, height=16).pack()

    def build_appearance(self, parent):
        inner = self.make_scroll_frame(parent)
        self.section_label(inner, "🎨  Megjelenés")
        self.make_toggle_row(inner, "🌙  Sötét mód", "Windows rendszer és alkalmazások sötét témája", "darkmode",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v AppsUseLightTheme /t REG_DWORD /d 0 /f && reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v SystemUsesLightTheme /t REG_DWORD /d 0 /f',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v AppsUseLightTheme /t REG_DWORD /d 1 /f && reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v SystemUsesLightTheme /t REG_DWORD /d 1 /f',
            on_msg="Sötét mód bekapcsolva!", off_msg="Világos mód visszakapcsolva.")
        self.make_toggle_row(inner, "📄  Fájlkiterjesztések", "Megmutatja a fájlok kiterjesztését (.exe, .txt stb.)", "extensions",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v HideFileExt /t REG_DWORD /d 0 /f',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v HideFileExt /t REG_DWORD /d 1 /f',
            on_msg="Fájlkiterjesztések megjelenítve!", off_msg="Fájlkiterjesztések elrejtve.")
        self.make_toggle_row(inner, "◀  Tálca balra igazítása", "Windows 11-en a tálca ikonokat balra igazítja (alapból középen van)", "taskbar_left",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v TaskbarAl /t REG_DWORD /d 0 /f',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v TaskbarAl /t REG_DWORD /d 1 /f',
            on_msg="Tálca balra igazítva!", off_msg="Tálca középre visszaállítva.")
        self.make_toggle_row(inner, "🔍  Keresősáv elrejtése", "Keresősáv eltüntetése a tálcáról", "searchbar",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Search" /v SearchboxTaskbarMode /t REG_DWORD /d 0 /f',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Search" /v SearchboxTaskbarMode /t REG_DWORD /d 2 /f',
            on_msg="Keresősáv elrejtve!", off_msg="Keresősáv visszakapcsolva.")
        self.make_toggle_row(inner, "📰  Widgets kikapcsolása", "Időjárás/hírek widget eltüntetése a tálcáról", "widgets",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v TaskbarDa /t REG_DWORD /d 0 /f',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v TaskbarDa /t REG_DWORD /d 1 /f',
            on_msg="Widgets kikapcsolva!", off_msg="Widgets visszakapcsolva.")
        tk.Frame(inner, bg=BG, height=16).pack()

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

    def clean_temp(self):
        self.log("⏳ Ideiglenes fájlok törlése...")
        def task():
            temp = os.environ.get("TEMP", "")
            count = 0
            for root, dirs, files in os.walk(temp):
                for f in files:
                    try:
                        os.remove(os.path.join(root, f))
                        count += 1
                    except: pass
            self.after(0, lambda: self.log(f"✅ {count} ideiglenes fájl törölve!"))
        threading.Thread(target=task, daemon=True).start()

    def free_ram(self):
        self.log("⏳ RAM felszabadítás...")
        def task():
            subprocess.run("powershell -Command \"Get-Process | Where-Object {$_.WorkingSet -gt 50MB} | ForEach-Object { $_.MinWorkingSet = 1MB }\"", shell=True, capture_output=True)
            self.after(0, lambda: self.log("✅ RAM felszabadítva!"))
        threading.Thread(target=task, daemon=True).start()

    def detect_states(self):
        detectors = {
            "darkmode": get_darkmode_state,
            "tracking": get_telemetry_state,
            "extensions": get_extensions_state,
            "gamemode": get_gamemode_state,
            "ads": get_ads_state,
            "taskbar_left": get_taskbar_left_state,
            "searchbar": get_searchbar_state,
            "widgets": get_widgets_state,
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
                    self.after(0, lambda: self.log("ℹ️ Reklámblokkolás már aktív."))
                    return
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
                if "WinSetup - reklámblokkolás" in line:
                    skip = True
                if skip and line.strip() == "":
                    skip = False
                    continue
                if not skip:
                    new_lines.append(line)
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
