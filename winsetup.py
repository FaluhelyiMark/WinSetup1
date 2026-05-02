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
def get_extensions_state():
    return reg_read_dword("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "HideFileExt") == 0
def get_ads_state():
    try:
        with open(r"C:\Windows\System32\drivers\etc\hosts", "r") as f: return "WinSetup" in f.read()
    except: return False
def get_telemetry_state():
    return reg_read_dword("HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection", "AllowTelemetry") == 0
def get_explorer_state():
    return reg_read_dword("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "LaunchTo") == 1
def get_cortana_state():
    return reg_read_dword("HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search", "AllowCortana") == 0
def get_powerplan_state():
    try:
        r = subprocess.run("powercfg /getactivescheme", shell=True, capture_output=True, text=True)
        return "e9a42b02" in r.stdout.lower()
    except: return False

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
        if self.command: self.command(self.state)

    def set_state(self, state):
        self.state = state
        self.draw()


class WinSetup(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WinSetup")
        self.geometry("720x660")
        self.resizable(True, True)
        self.configure(bg=BG)
        self.toggles = {}
        self.tab_frames = {}
        self.tab_buttons = {}
        self.build_ui()
        self.after(400, self.detect_states)

    def build_ui(self):
        header = tk.Frame(self, bg=SURFACE, height=56)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="⚡ WinSetup", font=("Consolas", 16, "bold"), bg=SURFACE, fg=ACCENT).pack(side="left", padx=20, pady=14)
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
            ("🛡️ Rendszer", self.build_system),
        ]

        for name, builder in tabs:
            frame = tk.Frame(self.content, bg=BG)
            self.tab_frames[name] = frame
            builder(frame)
            btn = tk.Label(self.tabbar, text=name, font=("Consolas", 11),
                           bg=SURFACE2, fg=TEXT2, cursor="hand2", padx=20, pady=10)
            btn.pack(side="left")
            btn.bind("<Button-1>", lambda e, n=name: self.show_tab(n))
            self.tab_buttons[name] = btn

        self.show_tab("📦 Telepítő")

    def show_tab(self, name):
        for f in self.tab_frames.values(): f.pack_forget()
        self.tab_frames[name].pack(fill="both", expand=True)
        for n, b in self.tab_buttons.items():
            b.config(bg=BG if n == name else SURFACE2, fg=ACCENT if n == name else TEXT2)

    def make_scroll(self, parent):
        container = tk.Frame(parent, bg=BG)
        container.pack(fill="both", expand=True)
        canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
        sb = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=BG)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        win_id = canvas.create_window((0,0), window=inner, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        return inner

    def section(self, parent, text):
        f = tk.Frame(parent, bg=BG)
        f.pack(fill="x", padx=20, pady=(18,4))
        tk.Label(f, text=text, font=("Consolas", 11, "bold"), bg=BG, fg=ACCENT2).pack(anchor="w")
        tk.Frame(f, bg=BORDER, height=1).pack(fill="x", pady=(3,0))

    def button_row(self, parent, label, desc, command):
        row = tk.Frame(parent, bg=SURFACE, highlightbackground=BORDER, highlightthickness=1)
        row.pack(fill="x", padx=20, pady=4)
        info = tk.Frame(row, bg=SURFACE)
        info.pack(side="left", fill="both", expand=True, padx=14, pady=12)
        tk.Label(info, text=label, font=("Consolas", 12, "bold"), bg=SURFACE, fg=TEXT, anchor="w").pack(anchor="w")
        tk.Label(info, text=desc, font=("Consolas", 9), bg=SURFACE, fg=TEXT2, anchor="w", wraplength=480).pack(anchor="w")
        tk.Button(row, text="▶ Telepítés", font=("Consolas", 10), bg=ACCENT, fg="#fff",
                  relief="flat", activebackground="#8a83ff", cursor="hand2",
                  bd=0, padx=14, pady=8, command=command).pack(side="right", padx=16, pady=12)

    def toggle_row(self, parent, label, desc, tid, on_fn=None, off_fn=None, on_cmd=None, off_cmd=None, on_msg="Kész!", off_msg="Visszaállítva."):
        row = tk.Frame(parent, bg=SURFACE, highlightbackground=BORDER, highlightthickness=1)
        row.pack(fill="x", padx=20, pady=4)
        info = tk.Frame(row, bg=SURFACE)
        info.pack(side="left", fill="both", expand=True, padx=14, pady=12)
        tk.Label(info, text=label, font=("Consolas", 12, "bold"), bg=SURFACE, fg=TEXT, anchor="w").pack(anchor="w")
        tk.Label(info, text=desc, font=("Consolas", 9), bg=SURFACE, fg=TEXT2, anchor="w", wraplength=480).pack(anchor="w")
        item = {"on_fn": on_fn, "off_fn": off_fn, "on_cmd": on_cmd, "off_cmd": off_cmd, "on_msg": on_msg, "off_msg": off_msg}
        tog = Toggle(row, state=False, command=lambda s, i=item: self.on_toggle(s, i))
        tog.pack(side="right", padx=16, pady=12)
        self.toggles[tid] = tog

    def action_row(self, parent, label, desc, command):
        row = tk.Frame(parent, bg=SURFACE, highlightbackground=BORDER, highlightthickness=1)
        row.pack(fill="x", padx=20, pady=4)
        info = tk.Frame(row, bg=SURFACE)
        info.pack(side="left", fill="both", expand=True, padx=14, pady=12)
        tk.Label(info, text=label, font=("Consolas", 12, "bold"), bg=SURFACE, fg=TEXT, anchor="w").pack(anchor="w")
        tk.Label(info, text=desc, font=("Consolas", 9), bg=SURFACE, fg=TEXT2, anchor="w", wraplength=480).pack(anchor="w")
        tk.Button(row, text="▶ Futtatás", font=("Consolas", 10), bg="#2a2560", fg="#afa9ec",
                  relief="flat", activebackground="#3a3570", cursor="hand2",
                  bd=0, padx=14, pady=8, command=command).pack(side="right", padx=16, pady=12)

    # ── TABS ──────────────────────────────────────────

    def build_installer(self, parent):
        inner = self.make_scroll(parent)
        self.section(inner, "📦  Alkalmazások")
        self.button_row(inner, "🌐  Chrome", "Google Chrome böngésző telepítése",
            lambda: self.choco_install("googlechrome", "Chrome telepítve!"))
        self.button_row(inner, "🎮  Roblox", "Roblox játékplatform telepítése",
            lambda: self.choco_install("roblox", "Roblox telepítve!"))
        self.button_row(inner, "📱  Viber", "Viber üzenetküldő telepítése",
            lambda: self.choco_install("viber", "Viber telepítve!"))
        tk.Frame(inner, bg=BG, height=20).pack()

    def build_system(self, parent):
        inner = self.make_scroll(parent)
        self.section(inner, "🛡️  Adatvédelem")
        self.toggle_row(inner, "🚫  Reklámblokkolás", "Hosts fájl módosítással blokkolja a hirdetési szervereket", "ads",
            on_fn=self.ads_on, off_fn=self.ads_off)
        self.toggle_row(inner, "🖨️  Telemetria letiltása", "Windows adatgyűjtés és diagnosztika kikapcsolása", "telemetry",
            on_cmd='reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f && sc config DiagTrack start= disabled && sc stop DiagTrack',
            off_cmd='reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 1 /f && sc config DiagTrack start= auto && sc start DiagTrack',
            on_msg="Telemetria letiltva!", off_msg="Telemetria visszakapcsolva.")
        self.toggle_row(inner, "🤖  Cortana letiltása", "Cortana asszisztens teljes letiltása", "cortana",
            on_cmd='reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search" /v AllowCortana /t REG_DWORD /d 0 /f && reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v ShowCortanaButton /t REG_DWORD /d 0 /f',
            off_cmd='reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search" /v AllowCortana /t REG_DWORD /d 1 /f && reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v ShowCortanaButton /t REG_DWORD /d 1 /f',
            on_msg="Cortana letiltva!", off_msg="Cortana visszakapcsolva.")

        self.section(inner, "⚡  Teljesítmény & megjelenés")
        self.toggle_row(inner, "🎯  Ultimate Power Plan", "Maximális teljesítmény energiaséma – játékra optimális", "powerplan",
            on_fn=self.enable_ultimate_power,
            off_fn=lambda: self.run_cmd("powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e", "Normál energiaséma visszaállítva."))
        self.toggle_row(inner, "🌙  Sötét mód", "Windows sötét téma be/kikapcsolása", "darkmode",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v AppsUseLightTheme /t REG_DWORD /d 0 /f && reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v SystemUsesLightTheme /t REG_DWORD /d 0 /f',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v AppsUseLightTheme /t REG_DWORD /d 1 /f && reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v SystemUsesLightTheme /t REG_DWORD /d 1 /f',
            on_msg="Sötét mód bekapcsolva!", off_msg="Világos mód visszakapcsolva.")
        self.toggle_row(inner, "📄  Fájlkiterjesztések megjelenítése", "Megmutatja a fájlok kiterjesztését (.exe, .txt stb.)", "extensions",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v HideFileExt /t REG_DWORD /d 0 /f',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v HideFileExt /t REG_DWORD /d 1 /f',
            on_msg="Fájlkiterjesztések megjelenítve!", off_msg="Fájlkiterjesztések elrejtve.")
        self.toggle_row(inner, "🖥️  Fájlkezelő: Ez a gép", "Fájlkezelő megnyitásakor az \"Ez a gép\" jelenjen meg", "explorer",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v LaunchTo /t REG_DWORD /d 1 /f',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v LaunchTo /t REG_DWORD /d 2 /f',
            on_msg="Fájlkezelő: Ez a gép!", off_msg="Fájlkezelő: Gyorselérés visszaállítva.")
        self.action_row(inner, "🗑️  Ideiglenes fájlok törlése", "Temp mappák kiürítése – felszabadít helyet a lemezen", self.clean_temp)
        tk.Frame(inner, bg=BG, height=20).pack()

    # ── LOGIKA ────────────────────────────────────────

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
