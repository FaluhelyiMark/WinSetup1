import tkinter as tk
import subprocess
import threading

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
        result = subprocess.run(f'reg query "{path}" /v {key}', shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if key in line and "REG_DWORD" in line:
                    return int(line.strip().split()[-1], 16)
    except:
        pass
    return None

def get_darkmode_state():
    val = reg_read_dword("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize", "AppsUseLightTheme")
    return val == 0

def get_telemetry_state():
    val = reg_read_dword("HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection", "AllowTelemetry")
    return val == 0

def get_extensions_state():
    val = reg_read_dword("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "HideFileExt")
    return val == 0

def get_gamemode_state():
    val = reg_read_dword("HKCU\\Software\\Microsoft\\GameBar", "AutoGameModeEnabled")
    return val == 1

def get_ads_state():
    try:
        with open(r"C:\Windows\System32\drivers\etc\hosts", "r") as f:
            return "WinSetup" in f.read()
    except:
        return False

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
        points = [x1+radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y2-radius, x2, y2, x2-radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y1+radius, x1, y1]
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
        self.geometry("660x600")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.toggles = {}
        self.build_ui()
        self.after(300, self.detect_states)

    def build_ui(self):
        header = tk.Frame(self, bg=SURFACE, height=56)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="⚡ WinSetup", font=("Consolas", 16, "bold"), bg=SURFACE, fg=ACCENT).pack(side="left", padx=20, pady=14)
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        log_frame = tk.Frame(self, bg=SURFACE2, height=70)
        log_frame.pack(fill="x")
        log_frame.pack_propagate(False)
        tk.Label(log_frame, text="Napló:", font=("Consolas", 9), bg=SURFACE2, fg=TEXT2).pack(anchor="w", padx=14, pady=(8,0))
        self.log_var = tk.StringVar(value="Állapotok beolvasása...")
        tk.Label(log_frame, textvariable=self.log_var, font=("Consolas", 10), bg=SURFACE2, fg=TEXT, wraplength=620, justify="left", anchor="w").pack(fill="x", padx=14)
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.btn_frame = tk.Frame(canvas, bg=BG)
        self.btn_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=self.btn_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.build_rows()

    def build_rows(self):
        sections = [
            ("📦  Alkalmazás telepítő", [
                {
                    "label": "🌐  Chrome",
                    "desc": "Google Chrome böngésző – BE: telepít, KI: eltávolít",
                    "id": "chrome",
                    "on_fn": lambda: self.choco_install("googlechrome", "Chrome telepítve!"),
                    "off_fn": lambda: self.choco_uninstall("googlechrome", "Chrome eltávolítva!"),
                    "detect": None,
                },
                {
                    "label": "🎮  Roblox",
                    "desc": "Roblox játékplatform – BE: telepít, KI: eltávolít",
                    "id": "roblox",
                    "on_fn": lambda: self.choco_install("roblox", "Roblox telepítve!"),
                    "off_fn": lambda: self.choco_uninstall("roblox", "Roblox eltávolítva!"),
                    "detect": None,
                },
                {
                    "label": "📱  Viber",
                    "desc": "Viber üzenetküldő – BE: telepít, KI: eltávolít",
                    "id": "viber",
                    "on_fn": lambda: self.choco_install("viber", "Viber telepítve!"),
                    "off_fn": lambda: self.choco_uninstall("viber", "Viber eltávolítva!"),
                    "detect": None,
                },
                {
                    "label": "💻  MobaXterm",
                    "desc": "MobaXterm SSH/terminál kliens – BE: telepít, KI: eltávolít",
                    "id": "mobaxterm",
                    "on_fn": lambda: self.choco_install("mobaxterm", "MobaXterm telepítve!"),
                    "off_fn": lambda: self.choco_uninstall("mobaxterm", "MobaXterm eltávolítva!"),
                    "detect": None,
                },
            ]),
            ("🛡️  Adatvédelem", [
                {
                    "label": "🚫  Reklámblokkolás",
                    "desc": "Hosts fájl módosítással blokkolja a hirdetési szervereket",
                    "id": "ads",
                    "detect": get_ads_state,
                    "on_fn": self.ads_on,
                    "off_fn": self.ads_off,
                },
                {
                    "label": "🖨️  Nyomkövetés letiltása",
                    "desc": "Windows telemetria és adatgyűjtés – BE: letiltva, KI: engedélyezve",
                    "id": "tracking",
                    "detect": get_telemetry_state,
                    "on_cmd": 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f && sc config DiagTrack start= disabled && sc stop DiagTrack',
                    "off_cmd": 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 1 /f && sc config DiagTrack start= auto && sc start DiagTrack',
                    "on_msg": "Nyomkövetés letiltva!",
                    "off_msg": "Nyomkövetés visszakapcsolva.",
                },
            ]),
            ("⚡  Teljesítmény & megjelenés", [
                {
                    "label": "🎯  Játék optimalizálás",
                    "desc": "Game Mode + nagy teljesítményű energiaséma – BE/KI",
                    "id": "gamemode",
                    "detect": get_gamemode_state,
                    "on_cmd": 'reg add "HKCU\\Software\\Microsoft\\GameBar" /v AutoGameModeEnabled /t REG_DWORD /d 1 /f && powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c',
                    "off_cmd": 'reg add "HKCU\\Software\\Microsoft\\GameBar" /v AutoGameModeEnabled /t REG_DWORD /d 0 /f && powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e',
                    "on_msg": "Játék optimalizálás bekapcsolva!",
                    "off_msg": "Játék optimalizálás kikapcsolva.",
                },
                {
                    "label": "🌙  Sötét mód",
                    "desc": "Windows rendszer és alkalmazások sötét témája – BE/KI",
                    "id": "darkmode",
                    "detect": get_darkmode_state,
                    "on_cmd": 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v AppsUseLightTheme /t REG_DWORD /d 0 /f && reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v SystemUsesLightTheme /t REG_DWORD /d 0 /f',
                    "off_cmd": 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v AppsUseLightTheme /t REG_DWORD /d 1 /f && reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v SystemUsesLightTheme /t REG_DWORD /d 1 /f',
                    "on_msg": "Sötét mód bekapcsolva!",
                    "off_msg": "Világos mód visszakapcsolva.",
                },
                {
                    "label": "📄  Fájlkiterjesztések",
                    "desc": "Megmutatja a fájlok kiterjesztését (.exe, .txt stb.) – BE/KI",
                    "id": "extensions",
                    "detect": get_extensions_state,
                    "on_cmd": 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v HideFileExt /t REG_DWORD /d 0 /f',
                    "off_cmd": 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v HideFileExt /t REG_DWORD /d 1 /f',
                    "on_msg": "Fájlkiterjesztések megjelenítve!",
                    "off_msg": "Fájlkiterjesztések elrejtve.",
                },
            ]),
        ]

        for section_title, items in sections:
            lbl_frame = tk.Frame(self.btn_frame, bg=BG)
            lbl_frame.pack(fill="x", padx=20, pady=(18, 6))
            tk.Label(lbl_frame, text=section_title, font=("Consolas", 11, "bold"), bg=BG, fg=ACCENT2).pack(anchor="w")
            tk.Frame(lbl_frame, bg=BORDER, height=1).pack(fill="x", pady=(4,0))
            for item in items:
                self.make_toggle_row(item)

        tk.Frame(self.btn_frame, bg=BG, height=20).pack()

    def make_toggle_row(self, item):
        row = tk.Frame(self.btn_frame, bg=SURFACE, highlightbackground=BORDER, highlightthickness=1)
        row.pack(fill="x", padx=20, pady=4)
        info = tk.Frame(row, bg=SURFACE)
        info.pack(side="left", fill="both", expand=True, padx=14, pady=12)
        tk.Label(info, text=item["label"], font=("Consolas", 12, "bold"), bg=SURFACE, fg=TEXT, anchor="w").pack(anchor="w")
        tk.Label(info, text=item["desc"], font=("Consolas", 9), bg=SURFACE, fg=TEXT2, anchor="w", wraplength=440).pack(anchor="w")
        tog = Toggle(row, state=False, command=lambda s, i=item: self.on_toggle(s, i))
        tog.pack(side="right", padx=18, pady=12)
        self.toggles[item["id"]] = tog

    def on_toggle(self, state, item):
        fn_key = "on_fn" if state else "off_fn"
        cmd_key = "on_cmd" if state else "off_cmd"
        msg_key = "on_msg" if state else "off_msg"
        if fn_key in item:
            threading.Thread(target=item[fn_key], daemon=True).start()
        elif cmd_key in item:
            self.run_cmd(item[cmd_key], item.get(msg_key, "Kész!"))

    def run_cmd(self, cmd, success_msg):
        self.log("⏳ Futtatás...")
        def task():
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    self.after(0, lambda: self.log(f"✅ {success_msg}"))
                else:
                    err = (result.stderr or result.stdout or "Ismeretlen hiba").strip()[:120]
                    self.after(0, lambda: self.log(f"❌ Hiba: {err}"))
            except Exception as e:
                self.after(0, lambda: self.log(f"❌ Kivétel: {str(e)[:120]}"))
        threading.Thread(target=task, daemon=True).start()

    def ensure_choco(self):
        """Telepíti a Chocolatey-t ha még nincs fenn."""
        result = subprocess.run("choco --version", shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            self.after(0, lambda: self.log("⏳ Chocolatey telepítése..."))
            install_cmd = 'powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString(\'https://community.chocolatey.org/install.ps1\'))"'
            r = subprocess.run(install_cmd, shell=True, capture_output=True, text=True)
            return r.returncode == 0
        return True

    def choco_install(self, package, success_msg):
        self.after(0, lambda: self.log(f"⏳ {package} telepítése..."))
        def task():
            if not self.ensure_choco():
                self.after(0, lambda: self.log("❌ Chocolatey telepítése sikertelen!"))
                return
            result = subprocess.run(f"choco install {package} -y", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.after(0, lambda: self.log(f"✅ {success_msg}"))
            else:
                err = (result.stderr or result.stdout or "Ismeretlen hiba").strip()[:120]
                self.after(0, lambda: self.log(f"❌ Hiba: {err}"))
        threading.Thread(target=task, daemon=True).start()

    def choco_uninstall(self, package, success_msg):
        self.after(0, lambda: self.log(f"⏳ {package} eltávolítása..."))
        def task():
            result = subprocess.run(f"choco uninstall {package} -y", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.after(0, lambda: self.log(f"✅ {success_msg}"))
            else:
                err = (result.stderr or result.stdout or "Ismeretlen hiba").strip()[:120]
                self.after(0, lambda: self.log(f"❌ Hiba: {err}"))
        threading.Thread(target=task, daemon=True).start()

    def detect_states(self):
        detectors = {
            "darkmode": get_darkmode_state,
            "tracking": get_telemetry_state,
            "extensions": get_extensions_state,
            "gamemode": get_gamemode_state,
            "ads": get_ads_state,
        }
        for tid, fn in detectors.items():
            try:
                state = fn()
                if tid in self.toggles:
                    self.toggles[tid].set_state(state)
            except:
                pass
        self.log("✅ Állapotok beolvasva – minden készen áll.")

    def ads_on(self):
        hosts_entry = "\n# WinSetup - reklámblokkolás\n127.0.0.1 ads.google.com\n127.0.0.1 doubleclick.net\n127.0.0.1 googleadservices.com\n127.0.0.1 googlesyndication.com\n127.0.0.1 adservice.google.com\n127.0.0.1 pagead2.googlesyndication.com\n"
        try:
            with open(r"C:\Windows\System32\drivers\etc\hosts", "r") as f:
                content = f.read()
            if "WinSetup" in content:
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
            new_lines = []
            skip = False
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
