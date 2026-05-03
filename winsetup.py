import tkinter as tk
import subprocess
import threading
import os

BG = "#0d0d11"
SURFACE = "#13131a"
SURFACE2 = "#16161f"
BORDER = "#1e1e2a"
BORDER2 = "#2a2a3a"
ACCENT = "#7c6fff"
ACCENT_DIM = "#3d3680"
TEXT = "#d0cef0"
TEXT2 = "#444458"
TEXT3 = "#3a3a50"
TOGGLE_ON = "#5a4fff"
TOGGLE_OFF = "#222230"
BTN_BG = "#1e1c35"
BTN_BORDER = "#3a3570"
BTN_TEXT = "#9b96e8"
ACTIVE_BG = "#13122a"
ACTIVE_BORDER = "#3d3680"
ACTIVE_TEXT = "#b8b0ff"

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


class Toggle(tk.Canvas):
    def __init__(self, parent, state=False, command=None, **kwargs):
        super().__init__(parent, width=38, height=21, bg=SURFACE2, highlightthickness=0, cursor="hand2", **kwargs)
        self.state = state
        self.command = command
        self.draw()
        self.bind("<Button-1>", self.toggle)

    def draw(self):
        self.delete("all")
        color = TOGGLE_ON if self.state else TOGGLE_OFF
        self.create_rounded_rect(1, 1, 37, 20, radius=10, fill=color, outline="#2a2a3a")
        cx = 28 if self.state else 11
        dot_color = "#ffffff" if self.state else "#3a3a50"
        self.create_oval(cx-7, 3, cx+7, 17, fill=dot_color, outline="")

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
        self.geometry("680x700")
        self.resizable(True, True)
        self.configure(bg=BG)
        self.toggles = {}
        self.tab_frames = {}
        self.tab_buttons = {}
        self.build_ui()
        self.after(400, self.detect_states)

    def build_ui(self):
        # Header
        header = tk.Frame(self, bg=SURFACE, height=52)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="⚡ WinSetup", font=("Segoe UI", 15, "bold"), bg=SURFACE, fg="#e2e0ff").pack(side="left", padx=20, pady=14)
        tk.Label(header, text="WINDOWS 10", font=("Segoe UI", 8, "bold"), bg=SURFACE, fg="#2a2a40").pack(side="right", padx=20)
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        # Tabs
        self.tabbar = tk.Frame(self, bg=SURFACE, height=40)
        self.tabbar.pack(fill="x")
        self.tabbar.pack_propagate(False)
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        # Log bar
        log_frame = tk.Frame(self, bg=BG, height=30)
        log_frame.pack(fill="x", side="bottom")
        log_frame.pack_propagate(False)
        tk.Frame(self, bg=BORDER, height=1).pack(side="bottom", fill="x")
        self.log_var = tk.StringVar(value="● Minden készen áll.")
        tk.Label(log_frame, textvariable=self.log_var, font=("Segoe UI", 9), bg=BG, fg=TEXT3, anchor="w").pack(fill="x", padx=20, pady=6)

        # Content
        self.content = tk.Frame(self, bg=BG)
        self.content.pack(fill="both", expand=True)

        tabs = [
            ("Kezdőlap", self.build_home),
            ("Telepítő", self.build_installer),
        ]

        for name, builder in tabs:
            frame = tk.Frame(self.content, bg=BG)
            self.tab_frames[name] = frame
            builder(frame)
            btn = tk.Label(self.tabbar, text=name, font=("Segoe UI", 10, "bold"),
                           bg=SURFACE, fg="#555577", cursor="hand2", padx=18, pady=10)
            btn.pack(side="left")
            btn.bind("<Button-1>", lambda e, n=name: self.show_tab(n))
            self.tab_buttons[name] = btn

        self.show_tab("Kezdőlap")

    def show_tab(self, name):
        for f in self.tab_frames.values(): f.pack_forget()
        self.tab_frames[name].pack(fill="both", expand=True)
        for n, b in self.tab_buttons.items():
            b.config(fg=ACCENT if n == name else "#555577")

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

    def group_label(self, parent, text):
        f = tk.Frame(parent, bg=BG)
        f.pack(fill="x", padx=20, pady=(18,4))
        tk.Label(f, text=text.upper(), font=("Segoe UI", 8, "bold"), bg=BG, fg=TEXT3).pack(anchor="w")
        tk.Frame(f, bg="#1a1a24", height=1).pack(fill="x", pady=(4,0))

    def toggle_item(self, parent, label, desc, tid, on_fn=None, off_fn=None, on_cmd=None, off_cmd=None, on_msg="Kész!", off_msg="Visszaállítva."):
        row = tk.Frame(parent, bg=SURFACE2, highlightbackground=BORDER, highlightthickness=1)
        row.pack(fill="x", padx=20, pady=3)
        info = tk.Frame(row, bg=SURFACE2)
        info.pack(side="left", fill="both", expand=True, padx=16, pady=13)
        name_lbl = tk.Label(info, text=label, font=("Segoe UI", 11, "bold"), bg=SURFACE2, fg=TEXT, anchor="w")
        name_lbl.pack(anchor="w")
        tk.Label(info, text=desc, font=("Segoe UI", 9), bg=SURFACE2, fg=TEXT2, anchor="w").pack(anchor="w")
        item = {"on_fn": on_fn, "off_fn": off_fn, "on_cmd": on_cmd, "off_cmd": off_cmd,
                "on_msg": on_msg, "off_msg": off_msg, "row": row, "name_lbl": name_lbl}
        tog = Toggle(row, state=False, command=lambda s, i=item: self.on_toggle(s, i))
        tog.pack(side="right", padx=16, pady=13)
        self.toggles[tid] = (tog, row, name_lbl)

    def button_item(self, parent, label, desc, btn_text, command):
        row = tk.Frame(parent, bg=SURFACE2, highlightbackground=BORDER, highlightthickness=1)
        row.pack(fill="x", padx=20, pady=3)
        info = tk.Frame(row, bg=SURFACE2)
        info.pack(side="left", fill="both", expand=True, padx=16, pady=13)
        tk.Label(info, text=label, font=("Segoe UI", 11, "bold"), bg=SURFACE2, fg=TEXT, anchor="w").pack(anchor="w")
        tk.Label(info, text=desc, font=("Segoe UI", 9), bg=SURFACE2, fg=TEXT2, anchor="w").pack(anchor="w")
        btn = tk.Label(row, text=btn_text, font=("Segoe UI", 9, "bold"),
                       bg=BTN_BG, fg=BTN_TEXT, cursor="hand2", padx=14, pady=6,
                       relief="flat", highlightbackground=BTN_BORDER, highlightthickness=1)
        btn.pack(side="right", padx=16, pady=13)
        btn.bind("<Button-1>", lambda e: command())
        btn.bind("<Enter>", lambda e: btn.config(bg="#2a2550"))
        btn.bind("<Leave>", lambda e: btn.config(bg=BTN_BG))

    def build_home(self, parent):
        inner = self.make_scroll(parent)

        self.group_label(inner, "🛡️  Adatvédelem")
        self.toggle_item(inner, "Reklámblokkolás", "Hosts fájl módosítással blokkolja a hirdetési szervereket", "ads",
            on_fn=self.ads_on, off_fn=self.ads_off)
        self.toggle_item(inner, "Telemetria letiltása", "Windows diagnosztikai adatgyűjtés kikapcsolása", "telemetry",
            on_cmd='reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f && sc config DiagTrack start= disabled && sc stop DiagTrack',
            off_cmd='reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 1 /f && sc config DiagTrack start= auto && sc start DiagTrack',
            on_msg="Telemetria letiltva!", off_msg="Telemetria visszakapcsolva.")
        self.toggle_item(inner, "Cortana letiltása", "Cortana asszisztens és tálcagomb teljes letiltása", "cortana",
            on_cmd='reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search" /v AllowCortana /t REG_DWORD /d 0 /f && reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v ShowCortanaButton /t REG_DWORD /d 0 /f',
            off_cmd='reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search" /v AllowCortana /t REG_DWORD /d 1 /f && reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v ShowCortanaButton /t REG_DWORD /d 1 /f',
            on_msg="Cortana letiltva!", off_msg="Cortana visszakapcsolva.")

        self.group_label(inner, "⚡  Teljesítmény & megjelenés")
        self.toggle_item(inner, "Ultimate Power Plan", "Maximális teljesítmény energiaséma – játékra optimális", "powerplan",
            on_fn=self.enable_ultimate_power,
            off_fn=lambda: self.run_cmd("powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e", "Normál energiaséma visszaállítva."))
        self.toggle_item(inner, "Sötét mód", "Windows rendszer és alkalmazások sötét témája", "darkmode",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v AppsUseLightTheme /t REG_DWORD /d 0 /f && reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v SystemUsesLightTheme /t REG_DWORD /d 0 /f',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v AppsUseLightTheme /t REG_DWORD /d 1 /f && reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v SystemUsesLightTheme /t REG_DWORD /d 1 /f',
            on_msg="Sötét mód bekapcsolva!", off_msg="Világos mód visszakapcsolva.")
        self.toggle_item(inner, "Fájlkiterjesztések megjelenítése", "Megmutatja a fájlok kiterjesztését (.exe, .txt stb.)", "extensions",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v HideFileExt /t REG_DWORD /d 0 /f',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v HideFileExt /t REG_DWORD /d 1 /f',
            on_msg="Fájlkiterjesztések megjelenítve!", off_msg="Fájlkiterjesztések elrejtve.")
        self.toggle_item(inner, "Fájlkezelő: Ez a gép", "Fájlkezelő megnyitásakor az Ez a gép nézet jelenik meg", "explorer",
            on_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v LaunchTo /t REG_DWORD /d 1 /f',
            off_cmd='reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v LaunchTo /t REG_DWORD /d 2 /f',
            on_msg="Fájlkezelő: Ez a gép!", off_msg="Fájlkezelő: Gyorselérés visszaállítva.")
        self.button_item(inner, "Ideiglenes fájlok törlése", "Temp mappák kiürítése – felszabadít helyet a lemezen", "Törlés", self.clean_temp)

        tk.Frame(inner, bg=BG, height=20).pack()

    def build_installer(self, parent):
        inner = self.make_scroll(parent)

        self.group_label(inner, "📦  Alkalmazások")
        self.button_item(inner, "Chrome", "Google Chrome böngésző telepítése", "Telepítés",
            lambda: self.choco_install("googlechrome", "Chrome telepítve!"))
        self.button_item(inner, "Roblox", "Roblox játékplatform telepítése", "Telepítés",
            lambda: self.direct_install("https://www.roblox.com/download/client", "RobloxSetup.exe", "Roblox telepítve!"))
        self.button_item(inner, "Viber", "Viber üzenetküldő telepítése", "Telepítés",
            lambda: self.direct_install("https://download.viber.com/desktop/ViberSetup.exe", "ViberSetup.exe", "Viber telepítve!"))

        tk.Frame(inner, bg=BG, height=20).pack()

    # ── LOGIKA ────────────────────────────────────────

    def on_toggle(self, state, item):
        row = item.get("row")
        name_lbl = item.get("name_lbl")
        if row and name_lbl:
            if state:
                row.config(highlightbackground=ACCENT_DIM, bg=ACTIVE_BG)
                name_lbl.config(fg=ACTIVE_TEXT, bg=ACTIVE_BG)
                for w in row.winfo_children():
                    if isinstance(w, tk.Frame): w.config(bg=ACTIVE_BG)
            else:
                row.config(highlightbackground=BORDER, bg=SURFACE2)
                name_lbl.config(fg=TEXT, bg=SURFACE2)
                for w in row.winfo_children():
                    if isinstance(w, tk.Frame): w.config(bg=SURFACE2)

        fn_key = "on_fn" if state else "off_fn"
        cmd_key = "on_cmd" if state else "off_cmd"
        msg_key = "on_msg" if state else "off_msg"
        if item.get(fn_key): threading.Thread(target=item[fn_key], daemon=True).start()
        elif item.get(cmd_key): self.run_cmd(item[cmd_key], item.get(msg_key, "Kész!"))

    def run_cmd(self, cmd, success_msg):
        self.log("Futtatás...")
        def task():
            try:
                r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if r.returncode == 0: self.after(0, lambda: self.log(f"● {success_msg}"))
                else:
                    err = (r.stderr or r.stdout or "Ismeretlen hiba").strip()[:120]
                    self.after(0, lambda: self.log(f"✕ Hiba: {err}"))
            except Exception as e:
                self.after(0, lambda: self.log(f"✕ {str(e)[:120]}"))
        threading.Thread(target=task, daemon=True).start()

    def ensure_choco(self):
        r = subprocess.run("choco --version", shell=True, capture_output=True, text=True)
        if r.returncode != 0:
            self.after(0, lambda: self.log("Chocolatey telepítése..."))
            cmd = 'powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString(\'https://community.chocolatey.org/install.ps1\'))"'
            r2 = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return r2.returncode == 0
        return True

    def choco_install(self, package, success_msg):
        self.after(0, lambda: self.log("Chocolatey ellenőrzése..."))
        def task():
            if not self.ensure_choco():
                self.after(0, lambda: self.log("✕ Chocolatey telepítése sikertelen!")); return
            self.after(0, lambda: self.log(f"{package} telepítése..."))
            r = subprocess.run(f"choco install {package} -y", shell=True, capture_output=True, text=True)
            if r.returncode == 0: self.after(0, lambda: self.log(f"● {success_msg}"))
            else:
                err = (r.stderr or r.stdout or "Ismeretlen hiba").strip()[:120]
                self.after(0, lambda: self.log(f"✕ Hiba: {err}"))
        threading.Thread(target=task, daemon=True).start()

    def enable_ultimate_power(self):
        self.after(0, lambda: self.log("Ultimate Power Plan bekapcsolása..."))
        def task():
            r = subprocess.run("powercfg /setactive e9a42b02-d5df-448d-aa00-03f14749eb61", shell=True, capture_output=True, text=True)
            if r.returncode != 0:
                subprocess.run("powercfg /duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61", shell=True, capture_output=True)
                subprocess.run("powercfg /setactive e9a42b02-d5df-448d-aa00-03f14749eb61", shell=True, capture_output=True)
            self.after(0, lambda: self.log("● Ultimate Power Plan bekapcsolva!"))
        threading.Thread(target=task, daemon=True).start()

    def clean_temp(self):
        self.log("Ideiglenes fájlok törlése...")
        def task():
            count = 0
            for folder in [os.environ.get("TEMP",""), os.environ.get("TMP",""), r"C:\Windows\Temp"]:
                if not folder: continue
                for root, dirs, files in os.walk(folder):
                    for f in files:
                        try: os.remove(os.path.join(root, f)); count += 1
                        except: pass
            self.after(0, lambda: self.log(f"● {count} ideiglenes fájl törölve!"))
        threading.Thread(target=task, daemon=True).start()

    def direct_install(self, url, filename, success_msg):
        self.after(0, lambda: self.log(filename + " letoltese..."))
        def task():
            try:
                dest = os.path.join(os.environ.get("TEMP", "C:\\Temp"), filename)
                cmd = 'powershell -Command "Invoke-WebRequest -Uri \"' + url + '\" -OutFile \"' + dest + '\""'
                subprocess.run(cmd, shell=True, capture_output=True)
                subprocess.Popen(dest, shell=True)
                self.after(0, lambda: self.log("● " + success_msg + " (telepito elindítva)"))
            except Exception as e:
                self.after(0, lambda: self.log("✕ " + str(e)))
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
                if tid in self.toggles:
                    tog, row, name_lbl = self.toggles[tid]
                    tog.set_state(state)
                    if state:
                        row.config(highlightbackground=ACCENT_DIM, bg=ACTIVE_BG)
                        name_lbl.config(fg=ACTIVE_TEXT, bg=ACTIVE_BG)
                        for w in row.winfo_children():
                            if isinstance(w, tk.Frame): w.config(bg=ACTIVE_BG)
            except: pass
        self.log("● Minden készen áll.")

    def ads_on(self):
        hosts_entry = "\n# WinSetup - reklámblokkolás\n127.0.0.1 ads.google.com\n127.0.0.1 doubleclick.net\n127.0.0.1 googleadservices.com\n127.0.0.1 googlesyndication.com\n127.0.0.1 adservice.google.com\n127.0.0.1 pagead2.googlesyndication.com\n"
        try:
            with open(r"C:\Windows\System32\drivers\etc\hosts", "r") as f:
                if "WinSetup" in f.read(): self.after(0, lambda: self.log("● Már aktív.")); return
            with open(r"C:\Windows\System32\drivers\etc\hosts", "a") as f: f.write(hosts_entry)
            self.after(0, lambda: self.log("● Reklámok blokkolva!"))
        except Exception as e: self.after(0, lambda: self.log(f"✕ {e}"))

    def ads_off(self):
        try:
            with open(r"C:\Windows\System32\drivers\etc\hosts", "r") as f: lines = f.readlines()
            new_lines, skip = [], False
            for line in lines:
                if "WinSetup - reklámblokkolás" in line: skip = True
                if skip and line.strip() == "": skip = False; continue
                if not skip: new_lines.append(line)
            with open(r"C:\Windows\System32\drivers\etc\hosts", "w") as f: f.writelines(new_lines)
            self.after(0, lambda: self.log("● Reklámblokkolás kikapcsolva."))
        except Exception as e: self.after(0, lambda: self.log(f"✕ {e}"))

    def log(self, msg): self.log_var.set(msg)

if __name__ == "__main__":
    app = WinSetup()
    app.mainloop()
