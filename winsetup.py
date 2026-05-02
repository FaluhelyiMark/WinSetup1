import tkinter as tk
import subprocess
import threading
import os

BG = "#1a0a0a"
SURFACE = "#2a1010"
SURFACE2 = "#200808"
BORDER = "#5a2020"
ACCENT = "#cc3333"
ACCENT2 = "#ff6666"
TEXT = "#f0e0e0"
TEXT2 = "#aa8888"
BTN_BG = "#3a1515"
BTN_ACTIVE = "#5a2020"
BTN_ON = "#cc3333"
BTN_OFF = "#2a1010"

def reg_read_dword(path, key):
    try:
        r = subprocess.run(f'reg query "{path}" /v {key}', shell=True, capture_output=True, text=True)
        if r.returncode == 0:
            for line in r.stdout.splitlines():
                if key in line and "REG_DWORD" in line:
                    return int(line.strip().split()[-1], 16)
    except: pass
    return None

def get_darkmode_state(): return reg_read_dword("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize", "AppsUseLightTheme") == 0
def get_extensions_state(): return reg_read_dword("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "HideFileExt") == 0
def get_ads_state():
    try:
        with open(r"C:\Windows\System32\drivers\etc\hosts", "r") as f: return "WinSetup" in f.read()
    except: return False
def get_telemetry_state(): return reg_read_dword("HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection", "AllowTelemetry") == 0
def get_explorer_state(): return reg_read_dword("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "LaunchTo") == 1
def get_cortana_state(): return reg_read_dword("HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search", "AllowCortana") == 0
def get_powerplan_state():
    try:
        r = subprocess.run("powercfg /getactivescheme", shell=True, capture_output=True, text=True)
        return "e9a42b02" in r.stdout.lower()
    except: return False


class WinSetup(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WinSetup")
        self.geometry("700x520")
        self.resizable(True, True)
        self.configure(bg=BG)
        self.toggle_states = {}
        self.toggle_btns = {}
        self.build_ui()
        self.after(400, self.detect_states)

    def build_ui(self):
        # Header
        header = tk.Frame(self, bg=SURFACE2, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="⚡ WinSetup", font=("Consolas", 17, "bold"), bg=SURFACE2, fg=ACCENT2).pack(side="left", padx=18, pady=10)
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        # Tab bar
        self.tabbar = tk.Frame(self, bg=SURFACE2, height=38)
        self.tabbar.pack(fill="x")
        self.tabbar.pack_propagate(False)
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        # Log bar
        log_frame = tk.Frame(self, bg=SURFACE2, height=32)
        log_frame.pack(fill="x", side="bottom")
        log_frame.pack_propagate(False)
        tk.Frame(self, bg=BORDER, height=1).pack(side="bottom", fill="x")
        self.log_var = tk.StringVar(value="Üdvözöl a WinSetup!")
        tk.Label(log_frame, textvariable=self.log_var, font=("Consolas", 9), bg=SURFACE2, fg=TEXT2, anchor="w").pack(fill="x", padx=14, pady=7)

        self.content = tk.Frame(self, bg=BG)
        self.content.pack(fill="both", expand=True)

        self.tab_frames = {}
        self.tab_buttons = {}

        tabs = [
            ("🏠 Kezdőlap", self.build_home),
            ("📦 Telepítő", self.build_installer),
        ]

        for name, builder in tabs:
            frame = tk.Frame(self.content, bg=BG)
            self.tab_frames[name] = frame
            builder(frame)
            btn = tk.Label(self.tabbar, text=name, font=("Consolas", 10, "bold"),
                           bg=SURFACE2, fg=TEXT2, cursor="hand2", padx=16, pady=8)
            btn.pack(side="left")
            btn.bind("<Button-1>", lambda e, n=name: self.show_tab(n))
            self.tab_buttons[name] = btn

        self.show_tab("🏠 Kezdőlap")

    def show_tab(self, name):
        for f in self.tab_frames.values(): f.pack_forget()
        self.tab_frames[name].pack(fill="both", expand=True)
        for n, b in self.tab_buttons.items():
            b.config(bg=ACCENT if n == name else SURFACE2, fg=TEXT if n == name else TEXT2)

    def build_home(self, parent):
        main = tk.Frame(parent, bg=BG)
        main.pack(fill="both", expand=True, padx=16, pady=14)

        # Adatvédelem sor
        self.make_section_row(main, "🛡️ Adatvédelem", [
            ("Reklámblokkolás", "ads", self.ads_on, self.ads_off),
            ("Telemetria letiltása", "telemetry",
             lambda: self.run_cmd('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f && sc config DiagTrack start= disabled && sc stop DiagTrack', "Telemetria letiltva!"),
             lambda: self.run_cmd('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 1 /f && sc config DiagTrack start= auto && sc start DiagTrack', "Telemetria visszakapcsolva.")),
            ("Cortana letiltása", "cortana",
             lambda: self.run_cmd('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search" /v AllowCortana /t REG_DWORD /d 0 /f && reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v ShowCortanaButton /t REG_DWORD /d 0 /f', "Cortana letiltva!"),
             lambda: self.run_cmd('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search" /v AllowCortana /t REG_DWORD /d 1 /f && reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v ShowCortanaButton /t REG_DWORD /d 1 /f', "Cortana visszakapcsolva.")),
        ])

        # Teljesítmény sor
        self.make_section_row(main, "⚡ Teljesítmény", [
            ("Ultimate Power Plan", "powerplan", self.enable_ultimate_power,
             lambda: self.run_cmd("powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e", "Normál energiaséma visszaállítva.")),
        ])

        # Megjelenés sor
        self.make_section_row(main, "🎨 Megjelenés", [
            ("Sötét mód", "darkmode",
             lambda: self.run_cmd('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v AppsUseLightTheme /t REG_DWORD /d 0 /f && reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v SystemUsesLightTheme /t REG_DWORD /d 0 /f', "Sötét mód bekapcsolva!"),
             lambda: self.run_cmd('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v AppsUseLightTheme /t REG_DWORD /d 1 /f && reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v SystemUsesLightTheme /t REG_DWORD /d 1 /f', "Világos mód visszakapcsolva.")),
            ("Fájlkiterjesztések", "extensions",
             lambda: self.run_cmd('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v HideFileExt /t REG_DWORD /d 0 /f', "Fájlkiterjesztések megjelenítve!"),
             lambda: self.run_cmd('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v HideFileExt /t REG_DWORD /d 1 /f', "Fájlkiterjesztések elrejtve.")),
            ("Fájlkezelő: Ez a gép", "explorer",
             lambda: self.run_cmd('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v LaunchTo /t REG_DWORD /d 1 /f', "Fájlkezelő: Ez a gép!"),
             lambda: self.run_cmd('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v LaunchTo /t REG_DWORD /d 2 /f', "Fájlkezelő: Gyorselérés.")),
        ])

        # Fájlok sor
        self.make_section_row(main, "🗂️ Fájlok", [
            ("Temp fájlok törlése", None, self.clean_temp, None),
        ])

        # Alsó gombok
        bottom = tk.Frame(parent, bg=BG)
        bottom.pack(side="bottom", fill="x", padx=16, pady=10)
        tk.Frame(bottom, bg=BORDER, height=1).pack(fill="x", pady=(0,10))
        btn_frame = tk.Frame(bottom, bg=BG)
        btn_frame.pack(anchor="e")
        for label, cmd in [("🔄 Újraindítás", "shutdown /r /t 5"), ("⏹️ Leállítás", "shutdown /s /t 5")]:
            tk.Button(btn_frame, text=label, font=("Consolas", 10), bg=ACCENT, fg=TEXT,
                      relief="flat", activebackground=BTN_ACTIVE, cursor="hand2",
                      bd=0, padx=16, pady=6,
                      command=lambda c=cmd: subprocess.Popen(c, shell=True)).pack(side="left", padx=4)

    def make_section_row(self, parent, title, buttons):
        row = tk.Frame(parent, bg=BG)
        row.pack(fill="x", pady=4)
        tk.Label(row, text=title, font=("Consolas", 10, "bold"), bg=BG, fg=TEXT2, width=18, anchor="w").pack(side="left")
        for label, tid, on_fn, off_fn in buttons:
            is_action = tid is None
            state = [False]
            btn = tk.Button(row, text=label, font=("Consolas", 9),
                            bg=BTN_BG, fg=TEXT, relief="flat",
                            activebackground=BTN_ACTIVE, cursor="hand2",
                            bd=0, padx=12, pady=5)
            btn.pack(side="left", padx=3)
            if is_action:
                btn.config(command=on_fn)
            else:
                def make_cmd(b, s, o, of, t):
                    def click():
                        s[0] = not s[0]
                        if s[0]:
                            b.config(bg=BTN_ON, fg="#ffffff")
                            threading.Thread(target=o, daemon=True).start()
                        else:
                            b.config(bg=BTN_BG, fg=TEXT)
                            threading.Thread(target=of, daemon=True).start()
                    return click
                btn.config(command=make_cmd(btn, state, on_fn, off_fn, tid))
                if tid:
                    self.toggle_btns[tid] = (btn, state)

    def build_installer(self, parent):
        main = tk.Frame(parent, bg=BG)
        main.pack(fill="both", expand=True, padx=16, pady=14)

        self.make_section_row(main, "🌐 Böngészők", [
            ("Chrome", None, lambda: self.choco_install("googlechrome", "Chrome telepítve!"), None),
        ])
        self.make_section_row(main, "🎮 Játék", [
            ("Roblox", None, lambda: self.choco_install("roblox", "Roblox telepítve!"), None),
        ])
        self.make_section_row(main, "💬 Kommunikáció", [
            ("Viber", None, lambda: self.choco_install("viber", "Viber telepítve!"), None),
        ])

    # ── LOGIKA ────────────────────────────────────────

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

    def ensure_choco(self):
        r = subprocess.run("choco --version", shell=True, capture_output=True, text=True)
        if r.returncode != 0:
            self.after(0, lambda: self.log("⏳ Chocolatey telepítése..."))
            cmd = 'powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString(\'https://community.chocolatey.org/install.ps1\'))"'
            r2 = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return r2.returncode == 0
        return True

    def choco_install(self, package, success_msg):
        self.after(0, lambda: self.log("⏳ Chocolatey ellenőrzése..."))
        def task():
            if not self.ensure_choco():
                self.after(0, lambda: self.log("❌ Chocolatey telepítése sikertelen!")); return
            self.after(0, lambda: self.log(f"⏳ {package} telepítése..."))
            r = subprocess.run(f"choco install {package} -y", shell=True, capture_output=True, text=True)
            if r.returncode == 0: self.after(0, lambda: self.log(f"✅ {success_msg}"))
            else:
                err = (r.stderr or r.stdout or "Ismeretlen hiba").strip()[:120]
                self.after(0, lambda: self.log(f"❌ Hiba: {err}"))
        threading.Thread(target=task, daemon=True).start()

    def enable_ultimate_power(self):
        self.after(0, lambda: self.log("⏳ Ultimate Power Plan bekapcsolása..."))
        def task():
            r = subprocess.run("powercfg /setactive e9a42b02-d5df-448d-aa00-03f14749eb61", shell=True, capture_output=True, text=True)
            if r.returncode != 0:
                subprocess.run("powercfg /duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61", shell=True, capture_output=True)
                subprocess.run("powercfg /setactive e9a42b02-d5df-448d-aa00-03f14749eb61", shell=True, capture_output=True)
            self.after(0, lambda: self.log("✅ Ultimate Power Plan bekapcsolva!"))
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

    def detect_states(self):
        detectors = {
            "darkmode": get_darkmode_state,
            "extensions": get_extensions_state,
            "ads": get_ads_state,
            "telemetry": get_telemetry_state,
            "explorer": get_explorer_state,
            "cortana": get_cortana_state,
            "powerplan": get_powerplan_state,
        }
        for tid, fn in detectors.items():
            try:
                state = fn()
                if tid in self.toggle_btns:
                    btn, s = self.toggle_btns[tid]
                    s[0] = state
                    btn.config(bg=BTN_ON if state else BTN_BG, fg="#ffffff" if state else TEXT)
            except: pass
        self.log("✅ Üdvözöl a WinSetup!")

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
