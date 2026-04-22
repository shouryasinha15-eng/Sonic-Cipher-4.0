"""
SonicCipher 4.0 - Hacker GUI (Split Encoder/Decoder)
"""

import tkinter as tk
from tkinter import filedialog
import subprocess, threading, os, random, time, platform, shutil
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    TkinterDnD = None

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


JAVA_SRC_DIR = os.path.join(PROJECT_ROOT, "src")
JAVA_OUT_DIR = os.path.join(PROJECT_ROOT, "out")
OUTPUT_WAV   = os.path.join(PROJECT_ROOT, "output", "encoded.wav")

BG        = "#0a0a0a"
PANEL     = "#0f0f0f"
GREEN     = "#00ff41"
DIM_GREEN = "#004d14"
CYAN      = "#00e5ff"
RED       = "#ff0040"
AMBER     = "#ffb300"
FONT_MONO = ("Courier New", 10)
FONT_BIG  = ("Courier New", 12, "bold")
FONT_SM   = ("Courier New", 8)


# here we are doing the java bridge 
def compile_java():
    os.makedirs(JAVA_OUT_DIR, exist_ok=True)
    java_files = []
    for root, _, files in os.walk(JAVA_SRC_DIR):
        for f in files:
            if f.endswith(".java"):
                java_files.append(os.path.join(root, f))
    if not java_files:
        return False, "No .java files found in src/"
    r = subprocess.run(["javac", "-d", JAVA_OUT_DIR] + java_files,
                       capture_output=True, text=True)
    return (r.returncode == 0), (r.stderr if r.returncode != 0 else "Compiled OK")


def run_java(text: str, mode: str = "BOTH", filepath: str = OUTPUT_WAV):
    """
    Pipe `text` to Main stdin.
    Main prints: Binary, Audio file generated, Decoded Binary, Decoded Text.
    Returns (ok, lines, stderr).
    """
    cmd = ["java", "-cp", JAVA_OUT_DIR, "Main"]
    if mode != "BOTH":
        cmd.extend([mode, filepath])

    r = subprocess.run(
        cmd,
        input=(text + "\n") if text else "",
        capture_output=True, text=True, timeout=60
    )
    return r.returncode == 0, r.stdout.strip().splitlines(), r.stderr


def parse_decoded(lines):
    """Extract decoded text from Java stdout lines."""
    for line in reversed(lines):          # take the last occurrence
        if line.startswith("Decoded Text:"):
            return line[len("Decoded Text:"):].strip()
    return None


#these are cutom weights 

class MatrixRain(tk.Canvas):
    CHARS = "01アイウエオカキクケコタチツテトナニヌ█▓▒░"

    def __init__(self, master, **kw):
        super().__init__(master, bg=BG, highlightthickness=0, **kw)
        self._cols = []; self._after = None
        self.bind("<Configure>", self._reset)

    def _reset(self, _=None):
        if self._after: self.after_cancel(self._after)
        w, h = self.winfo_width(), self.winfo_height()
        if w < 2 or h < 2: return
        n = max(1, w // 14)
        self._cols = [random.randint(0, h // 16) for _ in range(n)]
        self._h = h
        self._tick()

    def _tick(self):
        self.delete("all")
        for i, y in enumerate(self._cols):
            x = i * 14 + 6
            self.create_text(x, y*16, text=random.choice(self.CHARS),
                             fill=GREEN, font=("Courier New", 9, "bold"), anchor="n")
            shades = ["#001500","#002200","#003300","#005500","#007700"]
            for t in range(1, min(7, y)):
                self.create_text(x, (y-t)*16, text=random.choice(self.CHARS),
                                 fill=shades[min(t-1,4)],
                                 font=("Courier New", 9), anchor="n")
            self._cols[i] = (y + 1) % (self._h // 16 + 10)
        self._after = self.after(80, self._tick)


class GlitchLabel(tk.Label):
    def __init__(self, master, text="", **kw):
        self._base = text
        super().__init__(master, text=text, **kw)

    def glitch(self, ms=1200):
        self._end = time.time() + ms/1000
        self._tick()

    def _tick(self):
        if time.time() > self._end:
            self.config(text=self._base, fg=GREEN); return
        chars = list(self._base)
        for i in random.sample(range(len(chars)), k=min(4, len(chars))):
            chars[i] = random.choice("!@#$%01█▓アイ")
        self.config(text="".join(chars),
                    fg=random.choice([GREEN, CYAN, RED, AMBER]))
        self.after(random.randint(40, 110), self._tick)


class TermLog(tk.Frame):
    def __init__(self, master, **kw):
        super().__init__(master, bg=PANEL, **kw)
        self._t = tk.Text(self, bg=PANEL, fg=GREEN, font=FONT_MONO,
                          insertbackground=GREEN, relief="flat",
                          wrap="word", state="disabled",
                          selectbackground=DIM_GREEN, height=8)
        sb = tk.Scrollbar(self, command=self._t.yview, bg="#111",
                          troughcolor=BG, width=8)
        self._t.config(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._t.pack(fill="both", expand=True)
        for tag, col in [("ok",GREEN),("err",RED),("info",CYAN),
                         ("warn",AMBER),("dim",DIM_GREEN)]:
            self._t.tag_config(tag, foreground=col)

    def log(self, msg, tag="ok"):
        ts = time.strftime("%H:%M:%S")
        self._t.config(state="normal")
        self._t.insert("end", f"[{ts}] {msg}\n", tag)
        self._t.see("end")
        self._t.config(state="disabled")

    def clear(self):
        self._t.config(state="normal")
        self._t.delete("1.0", "end")
        self._t.config(state="disabled")


class BinaryViz(tk.Canvas):
    def __init__(self, master, **kw):
        super().__init__(master, bg=BG, highlightthickness=0, height=55, **kw)
        self._bits = []; self._job = None

    def feed(self, s):
        self._bits = list(s[:300])
        self._anim(0)

    def _anim(self, idx):
        self.delete("all")
        w = self.winfo_width() or 600
        n = len(self._bits)
        if not n: return
        bw = max(3, w // n)
        for i, b in enumerate(self._bits):
            h  = 44 if b == "1" else 14
            y0 = 52 - h
            col = CYAN if i == idx % n else (GREEN if b == "1" else DIM_GREEN)
            self.create_rectangle(i*bw, y0, i*bw+bw-1, 52, fill=col, outline="")
        if self._job: self.after_cancel(self._job)
        self._job = self.after(35, self._anim, idx+1)

    def clear(self):
        if self._job: self.after_cancel(self._job)
        self.delete("all")


class HackerBar(tk.Canvas):
    def __init__(self, master, **kw):
        super().__init__(master, bg=BG, highlightthickness=0, height=18, **kw)
        self._pct = 0
        self.bind("<Configure>", lambda _: self._draw())

    def set(self, pct):
        self._pct = max(0, min(100, pct)); self._draw()

    def _draw(self):
        self.delete("all")
        w = self.winfo_width() or 400
        f = int(w * self._pct / 100)
        self.create_rectangle(0, 0, w-1, 17, outline=GREEN, fill=BG)
        if f > 2:
            self.create_rectangle(1, 1, f-1, 16, fill=GREEN, outline="")
            for y in range(1, 17, 3):
                self.create_line(1, y, f-1, y, fill=DIM_GREEN)
        self.create_text(w//2, 9, text=f"{self._pct:.0f}%",
                         fill=(BG if self._pct > 50 else GREEN), font=FONT_SM)


#app
BaseApp = TkinterDnD.Tk if TkinterDnD else tk.Tk

class App(BaseApp):
    def __init__(self):
        super().__init__()
        self.title("SONICCIPHER 4.0  //  STEGANOGRAPHIC AUDIO ENCODER")
        self.geometry("980x780"); self.minsize(820, 650)
        self.configure(bg=BG)
        self._last_text = ""
        self._decode_file = ""
        self._build()
        self._boot()

    # layout 
    def _sec(self, p, t):
        tk.Label(p, text=t, bg=BG, fg=DIM_GREEN, font=FONT_SM).pack(
            anchor="w", pady=(4,2))

    def _build(self):
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=12, pady=(8,0))
        self._title = GlitchLabel(hdr, "SONICCIPHER 4.0",
                                  bg=BG, fg=GREEN,
                                  font=("Courier New", 22, "bold"))
        self._title.pack(side="left")
        tk.Label(hdr, text="// AUDIO STEGANOGRAPHY ENGINE",
                 bg=BG, fg=DIM_GREEN, font=("Courier New",9)).pack(
                     side="left", padx=8, pady=6)
                     
        tk.Button(hdr, text="✕ CLEAR SYSTEM", bg=BG, fg=RED, font=FONT_SM, relief="flat", cursor="hand2", command=self._clear).pack(side="right", padx=(8,0))
        self._status = tk.Label(hdr, text="● IDLE", bg=BG, fg=AMBER,
                                font=FONT_MONO)
        self._status.pack(side="right")

        tk.Frame(self, bg=GREEN, height=1).pack(fill="x", padx=12)
        MatrixRain(self, height=65).pack(fill="x", padx=12)
        tk.Frame(self, bg=DIM_GREEN, height=1).pack(fill="x", padx=12)

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=12, pady=6)
        
        top_body = tk.Frame(body, bg=BG)
        top_body.pack(fill="x", side="top", pady=(0, 6))

        left = tk.Frame(top_body, bg=BG)
        left.pack(side="left", fill="both", expand=True, padx=(0,6))
        right = tk.Frame(top_body, bg=BG)
        right.pack(side="right", fill="both", expand=True, padx=(6,0))

        bottom_body = tk.Frame(body, bg=BG)
        bottom_body.pack(fill="both", expand=True, side="bottom")

        self._left(left)
        self._right(right)
        self._bottom(bottom_body)

    def _left(self, p):
        self._sec(p, "/// SECTION 1: ENCODER ///")
        
        self._sec(p, "[ PLAINTEXT INPUT ]")
        self._inp = tk.Text(p, bg=PANEL, fg=GREEN, font=FONT_MONO,
                            insertbackground=GREEN, relief="flat",
                            height=4, selectbackground=DIM_GREEN)
        self._inp.pack(fill="x", pady=(0,4))
        self._inp.bind("<KeyRelease>", self._on_key)

        row = tk.Frame(p, bg=BG); row.pack(fill="x", pady=(0,4))
        self._clbl = tk.Label(row, text="CHARS: 0",   bg=BG, fg=DIM_GREEN, font=FONT_SM)
        self._clbl.pack(side="left")
        self._blbl = tk.Label(row, text="BITS: 0",    bg=BG, fg=DIM_GREEN, font=FONT_SM)
        self._blbl.pack(side="left", padx=10)
        self._dlbl = tk.Label(row, text="EST: 0.00s", bg=BG, fg=DIM_GREEN, font=FONT_SM)
        self._dlbl.pack(side="left")

        self._sec(p, "[ BINARY WAVEFORM PREVIEW ]")
        self._bviz = BinaryViz(p)
        self._bviz.pack(fill="x", pady=(0,4))

        self._sec(p, "[ PROGRESS ]")
        self._bar = HackerBar(p)
        self._bar.pack(fill="x", pady=(0,8))

        br = tk.Frame(p, bg=BG); br.pack(fill="x")
        self._ebtn = tk.Button(
            br, text="▶  ENCODE → AUDIO", bg=BG, fg=GREEN,
            font=FONT_BIG, relief="flat", cursor="hand2", pady=8,
            highlightbackground=GREEN, highlightthickness=1,
            activebackground=DIM_GREEN, activeforeground=GREEN,
            command=self._do_encode)
        self._ebtn.pack(side="left", fill="x", expand=True, padx=(0,4))

        self._dlbtn = tk.Button(
            br, text="↓  DOWNLOAD AUDIO", bg=BG, fg=AMBER,
            font=FONT_BIG, relief="flat", cursor="hand2", pady=8,
            highlightbackground=AMBER, highlightthickness=1,
            activebackground="#1a1200", activeforeground=AMBER,
            command=self._download_audio)
        self._dlbtn.pack(side="right", fill="x", expand=True, padx=(4,0))

        tk.Button(p, text="🔊  PLAY ENCODED AUDIO",
                  bg=BG, fg=CYAN, font=FONT_MONO, relief="flat",
                  cursor="hand2", pady=5,
                  highlightbackground=CYAN, highlightthickness=1,
                  activebackground="#002233", activeforeground=CYAN,
                  command=self._play).pack(fill="x", pady=(6,2))

    def _right(self, p):
        self._sec(p, "/// SECTION 2: DECODER ///")
        
        self._sec(p, "[ AUDIO FILE INPUT ]")
        
        self._drop_area = tk.Frame(p, bg=PANEL, highlightbackground=DIM_GREEN, highlightthickness=1)
        self._drop_area.pack(fill="x", pady=(0,4), ipady=20)
        
        self._drop_lbl = tk.Label(self._drop_area, text="DRAG & DROP WAV FILE HERE\n\nOR", bg=PANEL, fg=DIM_GREEN, font=FONT_MONO, justify="center")
        self._drop_lbl.pack(pady=(10,5))
        
        tk.Button(self._drop_area, text="BROWSE FILES", bg=PANEL, fg=CYAN, font=FONT_SM, relief="flat", cursor="hand2", command=self._browse_decode).pack()

        self._decode_file_lbl = tk.Label(p, text="NO FILE SELECTED", bg=BG, fg=AMBER, font=FONT_SM)
        self._decode_file_lbl.pack(anchor="w", pady=(0,8))

        if TkinterDnD:
            self._drop_area.drop_target_register(DND_FILES)
            self._drop_area.dnd_bind('<<Drop>>', self._on_drop)
            self._drop_lbl.drop_target_register(DND_FILES)
            self._drop_lbl.dnd_bind('<<Drop>>', self._on_drop)

        self._dbtn = tk.Button(
            p, text="◀  DECODE → TEXT", bg=BG, fg=CYAN,
            font=FONT_BIG, relief="flat", cursor="hand2", pady=8,
            highlightbackground=CYAN, highlightthickness=1,
            activebackground=DIM_GREEN, activeforeground=CYAN,
            command=self._do_decode)
        self._dbtn.pack(fill="x", pady=(0,8))

        self._sec(p, "[ DECODED TEXT OUTPUT ]")
        self._out = tk.Text(p, bg=PANEL, fg=CYAN, font=FONT_MONO,
                            insertbackground=CYAN, relief="flat",
                            height=4, state="disabled",
                            selectbackground=DIM_GREEN)
        self._out.pack(fill="x", pady=(0,4))

        tk.Button(p, text="⎘  COPY DECODED TEXT",
                  bg=BG, fg=AMBER, font=FONT_SM, relief="flat",
                  cursor="hand2", command=self._copy).pack(fill="x")

    def _bottom(self, p):
        self._sec(p, "[ SYSTEM TERMINAL ]")
        self._log = TermLog(p)
        self._log.pack(fill="both", expand=True)

    # helpers 
    def _on_key(self, _=None):
        txt = self._inp.get("1.0", "end-1c")
        nc = len(txt); bits = nc*8
        self._clbl.config(text=f"CHARS: {nc}")
        self._blbl.config(text=f"BITS: {bits}")
        self._dlbl.config(text=f"EST: {bits*0.40:.2f}s")
        if txt:
            self._bviz.feed("".join(f"{ord(c):08b}" for c in txt))
        else:
            self._bviz.clear()

    def _on_drop(self, event):
        filepath = event.data
        if filepath.startswith('{') and filepath.endswith('}'):
            filepath = filepath[1:-1]
        self._set_decode_file(filepath)

    def _browse_decode(self):
        p = filedialog.askopenfilename(filetypes=[("WAV","*.wav"),("All","*.*")])
        if p: self._set_decode_file(p)

    def _set_decode_file(self, filepath):
        self._decode_file = filepath
        display_name = os.path.basename(filepath)
        self._decode_file_lbl.config(text=f"SELECTED: {display_name}", fg=GREEN)
        self._log.log(f"Loaded file for decoding: {filepath}", "info")

    def _download_audio(self):
        if not os.path.exists(OUTPUT_WAV):
            self._log.log("No audio generated yet. ENCODE first.", "err")
            return
        p = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV","*.wav")])
        if p:
            try:
                shutil.copy2(OUTPUT_WAV, p)
                self._log.log(f"Audio downloaded to: {p}", "ok")
            except Exception as e:
                self._log.log(f"Download failed: {e}", "err")

    def _setstatus(self, txt, col):
        self.after(0, lambda: self._status.config(text=f"● {txt}", fg=col))

    def _setprog(self, pct):
        self.after(0, self._bar.set, pct)

    def _setout(self, txt):
        def _do():
            self._out.config(state="normal")
            self._out.delete("1.0","end")
            self._out.insert("end", txt)
            self._out.config(state="disabled")
        self.after(0, _do)

    def _lock(self, v):
        s = "disabled" if v else "normal"
        self.after(0, lambda: self._ebtn.config(state=s))
        self.after(0, lambda: self._dbtn.config(state=s))
        self.after(0, lambda: self._dlbtn.config(state=s))

    # ── ENCODE 
    def _do_encode(self):
        text = self._inp.get("1.0","end-1c").strip()
        if not text:
            self._log.log("ERROR: Input is empty.", "err"); return
        self._last_text = text
        self._lock(True)
        # Always output to the internal OUTPUT_WAV
        threading.Thread(target=self._enc_w, args=(text, OUTPUT_WAV), daemon=True).start()

    def _enc_w(self, text, filepath):
        self._setstatus("COMPILING", AMBER)
        self._log.log("Compiling Java sources…", "dim")
        self._setprog(5)

        ok, msg = compile_java()
        if not ok:
            self._log.log(f"Compile FAILED:\n{msg}", "err")
            self._setstatus("ERROR", RED); self._lock(False); return
        self._log.log(msg, "ok"); self._setprog(25)

        binary = "".join(f"{ord(c):08b}" for c in text)
        self._log.log(f"Binary preview: {binary[:64]}{'…' if len(binary)>64 else ''}", "dim")
        self._setprog(35)

        self._setstatus("ENCODING", GREEN)
        self._log.log("Sending text to Java encoder…", "info")
        ok, lines, stderr = run_java(text, mode="ENCODE", filepath=filepath)
        self._setprog(90)

        if not ok:
            self._log.log(f"Java runtime error:\n{stderr}", "err")
            self._setstatus("ERROR", RED); self._lock(False); return

        self._setprog(100)
        self._log.log("✔ Audio generated. Ready for download.", "ok")
        self._setstatus("READY", GREEN)
        self._title.glitch(1200)
        self._lock(False)

    # ── DECODE (re-run with cached input) 
    def _do_decode(self):
        filepath = self._decode_file
        if not os.path.exists(filepath):
            self._log.log("No file selected for decoding. Drag and drop a WAV file or click BROWSE.", "err")
            return
        self._lock(True)
        threading.Thread(target=self._dec_w, args=(filepath,), daemon=True).start()

    def _dec_w(self, filepath):
        self._setstatus("DECODING", CYAN)
        self._log.log("Compiling…", "dim"); self._setprog(10)
        ok, msg = compile_java()
        if not ok:
            self._log.log(f"Compile FAILED:\n{msg}", "err")
            self._setstatus("ERROR", RED); self._lock(False); return
        self._setprog(30)

        self._log.log(f"Decoding from {filepath}…", "info")
        ok, lines, stderr = run_java("", mode="DECODE", filepath=filepath)
        self._setprog(85)

        if not ok:
            self._log.log(f"Java error:\n{stderr}", "err")
            self._setstatus("ERROR", RED); self._lock(False); return

        decoded = None
        for line in lines:
            if line.startswith("Enter text:"): continue
            tag = "dim" if "Binary:" in line else "ok"
            self._log.log(line, tag)
            if line.startswith("Decoded Text:"):
                decoded = line[len("Decoded Text:"):].strip()

        self._setprog(100)
        if decoded:
            self._setout(decoded)
            self._log.log(f"✔ Decoded: {decoded}", "ok")
        else:
            self._log.log("⚠ Decoded text not found. Is the WAV valid?", "warn")

        self._setstatus("READY", GREEN)
        self._lock(False)

    # ── PLAY AUDIO 
    def _play(self):
        wav = OUTPUT_WAV
        if not os.path.exists(wav):
            self._log.log(f"File not found: {wav}", "err")
            self._log.log("Run ENCODE first to generate the WAV.", "warn")
            return
        self._log.log(f"Opening: {wav}", "info")
        try:
            sys_name = platform.system()
            if sys_name == "Windows":
                os.startfile(wav)                    # uses default app (Media Player)
            elif sys_name == "Darwin":
                subprocess.Popen(["open", wav])
            else:
                subprocess.Popen(["xdg-open", wav])
        except Exception as e:
            self._log.log(f"Auto-open failed: {e}", "err")
            self._log.log(f"Open manually: {wav}", "warn")

    # ── CLEAR 
    def _clear(self):
        self._inp.delete("1.0","end")
        self._setout("")
        self._log.clear(); self._bviz.clear(); self._bar.set(0)
        self._clbl.config(text="CHARS: 0")
        self._blbl.config(text="BITS: 0")
        self._dlbl.config(text="EST: 0.00s")
        self._setstatus("IDLE", AMBER)
        self._last_text = ""
        self._decode_file = ""
        self._decode_file_lbl.config(text="NO FILE SELECTED", fg=AMBER)
        self._log.log("System cleared.", "dim")

    def _copy(self):
        txt = self._out.get("1.0","end-1c")
        if txt:
            self.clipboard_clear(); self.clipboard_append(txt)
            self._log.log("Copied to clipboard.", "info")

    # ── BOOT 
    def _boot(self):
        msgs = [
            ("SONICCIPHER 4.0 — STEGANOGRAPHIC AUDIO ENGINE", "info"),
            (f"Root : {PROJECT_ROOT}", "dim"),
            (f"Src  : {JAVA_SRC_DIR}", "dim"),
            (f"WAV  : {OUTPUT_WAV}", "dim"),
            ("Scheme: 0→200ms  1→500ms  gap→50ms  @44100Hz/16-bit", "dim"),
            ("─"*52, "dim"),
            ("READY. Drag & Drop supported.", "ok") if TkinterDnD else ("READY. (Drag & Drop disabled - missing tkinterdnd2)", "warn"),
        ]
        def feed(i=0):
            if i < len(msgs):
                self._log.log(*msgs[i])
                self.after(160, feed, i+1)
        self.after(300, feed)


if __name__ == "__main__":
    App().mainloop()