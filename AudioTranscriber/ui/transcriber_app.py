import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import sys
from functions.helpers import *

 
class TranscriberApp(tk.Tk):
    MODELS  = ["tiny", "base", "small", "medium", "large"]
    FORMATS = [".srt", ".vtt", ".txt", ".json (Premiere Pro)"]
 
    def __init__(self):
        super().__init__()
        self.title("Video Transcript Generator")
        self.resizable(False, False)
        self.configure(bg="#1a1a2e")
        self._build_ui()
 
    # ── UI ────────────────────────────────────────────────────────────────────
 
    def _build_ui(self):
        PAD = dict(padx=16, pady=6)
 
        style = ttk.Style(self)
        style.theme_use("clam")
 
        BG, FG     = "#1a1a2e", "#e0e0f0"
        ACCENT     = "#7b5ea7"
        ENTRY_BG   = "#16213e"
        BTN_ACTIVE = "#9b7ec8"
        DIM        = "#555577"
 
        style.configure("TFrame",         background=BG)
        style.configure("TLabel",         background=BG, foreground=FG,
                        font=("Segoe UI", 10))
        style.configure("Header.TLabel",  background=BG, foreground="#c8b1e4",
                        font=("Segoe UI", 18, "bold"))
        style.configure("Sub.TLabel",     background=BG, foreground="#888aaa",
                        font=("Segoe UI", 9))
        style.configure("Section.TLabel", background=BG, foreground="#a090cc",
                        font=("Segoe UI", 9, "bold"))
        style.configure("TEntry",         fieldbackground=ENTRY_BG, foreground=FG,
                        insertcolor=FG, borderwidth=0)
        style.configure("TCombobox",      fieldbackground=ENTRY_BG, foreground=FG,
                        selectbackground=ACCENT, borderwidth=0)
        style.configure("TSpinbox",       fieldbackground=ENTRY_BG, foreground=FG,
                        insertcolor=FG, borderwidth=0, arrowcolor=FG)
        style.configure("Accent.TButton", background=ACCENT, foreground="#ffffff",
                        font=("Segoe UI", 10, "bold"), borderwidth=0, relief="flat")
        style.map("Accent.TButton",
                  background=[("active", BTN_ACTIVE), ("disabled", "#444466")],
                  foreground=[("disabled", "#888888")])
        style.configure("TCheckbutton",   background=BG, foreground=FG,
                        font=("Segoe UI", 10))
        style.map("TCheckbutton",         background=[("active", BG)])
        style.configure("TProgressbar",   troughcolor=ENTRY_BG, background=ACCENT,
                        borderwidth=0, thickness=6)
 
        # ── header ────────────────────────────────────────────────────────────
        hdr = ttk.Frame(self)
        hdr.pack(fill="x", padx=24, pady=(24, 8))
        ttk.Label(hdr, text="🎬  Video Transcriber",
                  style="Header.TLabel").pack(anchor="w")
        ttk.Label(hdr, text="Generate SRT / VTT / TXT / Premiere Pro JSON caption files",
                  style="Sub.TLabel").pack(anchor="w")
 
        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=24, pady=4)
 
        body = ttk.Frame(self)
        body.pack(fill="both", padx=24, pady=8)
 
        # row 0 – video file
        ttk.Label(body, text="Video File").grid(row=0, column=0, sticky="w", **PAD)
        self.video_var = tk.StringVar()
        ttk.Entry(body, textvariable=self.video_var, width=48).grid(row=0, column=1, **PAD)
        ttk.Button(body, text="Browse…", style="Accent.TButton",
                   command=self._browse_video).grid(row=0, column=2, **PAD)
 
        # row 1 – export folder
        ttk.Label(body, text="Export Folder").grid(row=1, column=0, sticky="w", **PAD)
        self.export_var = tk.StringVar()
        ttk.Entry(body, textvariable=self.export_var, width=48).grid(row=1, column=1, **PAD)
        ttk.Button(body, text="Browse…", style="Accent.TButton",
                   command=self._browse_export).grid(row=1, column=2, **PAD)
 
        # row 2 – output filename
        ttk.Label(body, text="Output Filename").grid(row=2, column=0, sticky="w", **PAD)
        self.filename_var = tk.StringVar(value="transcript")
        ttk.Entry(body, textvariable=self.filename_var, width=30).grid(
            row=2, column=1, sticky="w", **PAD)
 
        # row 3 – caption format
        ttk.Label(body, text="Caption Format").grid(row=3, column=0, sticky="w", **PAD)
        self.format_var = tk.StringVar(value=".srt")
        ttk.Combobox(body, textvariable=self.format_var, values=self.FORMATS,
                     state="readonly", width=22).grid(row=3, column=1, sticky="w", **PAD)
 
        # row 4 – whisper model
        ttk.Label(body, text="Whisper Model").grid(row=4, column=0, sticky="w", **PAD)
        self.model_var = tk.StringVar(value="base")
        ttk.Combobox(body, textvariable=self.model_var, values=self.MODELS,
                     state="readonly", width=10).grid(row=4, column=1, sticky="w", **PAD)
        ttk.Label(body, text="tiny = fastest  |  large = most accurate",
                  style="Sub.TLabel").grid(row=4, column=1, sticky="e", **PAD)
 
        # row 5 – language
        ttk.Label(body, text="Language (optional)").grid(row=5, column=0, sticky="w", **PAD)
        self.lang_var = tk.StringVar(value="")
        ttk.Entry(body, textvariable=self.lang_var, width=14).grid(
            row=5, column=1, sticky="w", **PAD)
        ttk.Label(body, text='e.g. "en", "fr", "es" — leave blank for auto-detect',
                  style="Sub.TLabel").grid(row=5, column=1, sticky="e", **PAD)
 
        # ── section: caption splitting ────────────────────────────────────────
        ttk.Separator(body, orient="horizontal").grid(
            row=6, column=0, columnspan=3, sticky="ew", padx=0, pady=10)
        ttk.Label(body, text="CAPTION SPLITTING",
                  style="Section.TLabel").grid(row=7, column=0, sticky="w",
                                               padx=16, pady=(0, 4))
 
        # row 8 – max chars checkbox
        self.maxchars_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            body,
            text="Limit characters per caption  (soft guide — words are never cut)",
            variable=self.maxchars_enabled,
            style="TCheckbutton",
            command=self._toggle_maxchars,
        ).grid(row=8, column=0, columnspan=3, sticky="w", padx=16, pady=4)
 
        # row 9 – max chars spinbox
        ttk.Label(body, text="Max Characters").grid(row=9, column=0, sticky="w", **PAD)
        sf = ttk.Frame(body); sf.grid(row=9, column=1, sticky="w", **PAD)
        self.maxchars_var  = tk.IntVar(value=42)
        self.maxchars_spin = ttk.Spinbox(sf, from_=10, to=500, increment=1,
                                         textvariable=self.maxchars_var,
                                         width=6, state="disabled")
        self.maxchars_spin.pack(side="left")
        self.maxchars_hint = ttk.Label(sf,
                                       text="  splits at nearest word boundary around this limit",
                                       style="Sub.TLabel", foreground=DIM)
        self.maxchars_hint.pack(side="left")
 
        # row 10 – max duration checkbox
        self.maxdur_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            body,
            text="Limit duration per caption  (soft guide — words are never cut)",
            variable=self.maxdur_enabled,
            style="TCheckbutton",
            command=self._toggle_maxdur,
        ).grid(row=10, column=0, columnspan=3, sticky="w", padx=16, pady=4)
 
        # row 11 – max duration spinbox
        ttk.Label(body, text="Max Duration (sec)").grid(row=11, column=0, sticky="w", **PAD)
        df = ttk.Frame(body); df.grid(row=11, column=1, sticky="w", **PAD)
        self.maxdur_var  = tk.DoubleVar(value=3.0)
        self.maxdur_spin = ttk.Spinbox(df, from_=0.5, to=60.0, increment=0.5,
                                       textvariable=self.maxdur_var,
                                       format="%.1f", width=6, state="disabled")
        self.maxdur_spin.pack(side="left")
        self.maxdur_hint = ttk.Label(df,
                                     text="  splits long captions by distributing words evenly",
                                     style="Sub.TLabel", foreground=DIM)
        self.maxdur_hint.pack(side="left")
 
        # ── bottom separator + progress ───────────────────────────────────────
        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=24, pady=8)
        prog_frame = ttk.Frame(self)
        prog_frame.pack(fill="x", padx=24, pady=(0, 4))
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(prog_frame, textvariable=self.status_var,
                  style="Sub.TLabel").pack(anchor="w", pady=(0, 4))
        self.progress = ttk.Progressbar(prog_frame, mode="indeterminate",
                                        style="TProgressbar", length=500)
        self.progress.pack(fill="x")
 
        # ── buttons ───────────────────────────────────────────────────────────
        btn_row = ttk.Frame(self)
        btn_row.pack(fill="x", padx=24, pady=(8, 24))
        self.run_btn = ttk.Button(btn_row, text="▶  Generate Transcript",
                                  style="Accent.TButton",
                                  command=self._start_transcription)
        self.run_btn.pack(side="right")
        ttk.Button(btn_row, text="Clear",
                   command=self._clear).pack(side="right", padx=(0, 8))
 
    # ── toggle helpers ────────────────────────────────────────────────────────
 
    def _toggle_maxchars(self):
        on = self.maxchars_enabled.get()
        self.maxchars_spin.configure(state="normal" if on else "disabled")
        self.maxchars_hint.configure(foreground="#888aaa" if on else "#555577")
 
    def _toggle_maxdur(self):
        on = self.maxdur_enabled.get()
        self.maxdur_spin.configure(state="normal" if on else "disabled")
        self.maxdur_hint.configure(foreground="#888aaa" if on else "#555577")
 
    # ── callbacks ─────────────────────────────────────────────────────────────
 
    def _browse_video(self):
        path = filedialog.askopenfilename(
            title="Select a video file",
            filetypes=[
                ("Video files", "*.mp4 *.mkv *.avi *.mov *.webm *.flv *.wmv *.m4v"),
                ("All files", "*.*"),
            ],
        )
        if path:
            self.video_var.set(path)
            if not self.export_var.get():
                self.export_var.set(os.path.dirname(path))
            if not self.filename_var.get() or self.filename_var.get() == "transcript":
                self.filename_var.set(os.path.splitext(os.path.basename(path))[0])
 
    def _browse_export(self):
        path = filedialog.askdirectory(title="Select export folder")
        if path:
            self.export_var.set(path)
 
    def _clear(self):
        self.video_var.set("")
        self.export_var.set("")
        self.filename_var.set("transcript")
        self.format_var.set(".srt")
        self.model_var.set("base")
        self.lang_var.set("")
        self.maxchars_enabled.set(False)
        self.maxchars_var.set(42)
        self._toggle_maxchars()
        self.maxdur_enabled.set(False)
        self.maxdur_var.set(3.0)
        self._toggle_maxdur()
        self.status_var.set("Ready")
 
    # ── transcription ─────────────────────────────────────────────────────────
 
    def _start_transcription(self):
        video  = self.video_var.get().strip()
        folder = self.export_var.get().strip()
        name   = self.filename_var.get().strip() or "transcript"
        fmt    = self.format_var.get()
        model  = self.model_var.get()
        lang   = self.lang_var.get().strip() or None
        max_ch = 0
        max_du = 0.0
 
        if self.maxchars_enabled.get():
            try:
                max_ch = int(self.maxchars_var.get())
                if max_ch < 10:
                    raise ValueError
            except (ValueError, tk.TclError):
                messagebox.showwarning("Invalid value",
                                       "Max characters must be a whole number ≥ 10.")
                return
 
        if self.maxdur_enabled.get():
            try:
                max_du = float(self.maxdur_var.get())
                if max_du < 0.5:
                    raise ValueError
            except (ValueError, tk.TclError):
                messagebox.showwarning("Invalid value",
                                       "Max duration must be a number ≥ 0.5 seconds.")
                return
 
        if not video:
            messagebox.showwarning("Missing input", "Please select a video file.")
            return
        if not os.path.isfile(video):
            messagebox.showerror("File not found", f"Cannot find:\n{video}")
            return
        if not folder:
            messagebox.showwarning("Missing output", "Please select an export folder.")
            return
 
        # Determine real file extension
        if fmt.startswith(".json"):
            ext = ".json"
        else:
            ext = fmt
 
        os.makedirs(folder, exist_ok=True)
        out_path = os.path.join(folder, name + ext)
 
        self.run_btn.configure(state="disabled")
        self.progress.start(12)
        self.status_var.set("Loading Whisper model…")
 
        threading.Thread(
            target=self._transcribe,
            args=(video, out_path, model, lang, fmt, max_ch, max_du),
            daemon=True,
        ).start()
 
    def _transcribe(self, video_path, out_path, model_name, language,
                    fmt, max_chars, max_dur):
        try:
            import whisper
        except ImportError:
            self._done_error(
                "openai-whisper is not installed.\n\n"
                "Run:  pip install openai-whisper"
            )
            return
 
        try:
            self._set_status("Loading Whisper model…")
            model = whisper.load_model(model_name)
 
            self._set_status("Transcribing — this may take a few minutes…")
            kwargs = {"verbose": False}
            if language:
                kwargs["language"] = language
 
            result   = model.transcribe(video_path, **kwargs)
            segments = result.get("segments", [])
 
            # Apply splitting in order: duration first, then chars
            # (duration splits keep word groups intact; chars refines further)
            if max_dur > 0:
                self._set_status("Splitting captions by duration limit…")
                segments = apply_max_duration(segments, max_dur)
 
            if max_chars > 0:
                self._set_status("Splitting captions by character limit…")
                segments = apply_max_chars(segments, max_chars)
 
            self._set_status("Writing caption file…")
            if fmt == ".srt":
                content = segments_to_srt(segments)
            elif fmt == ".vtt":
                content = segments_to_vtt(segments)
            elif fmt.startswith(".json"):
                content = segments_to_premiere_json(segments, video_path)
            else:
                content = segments_to_txt(segments)
 
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(content)
 
            self._done_ok(out_path)
 
        except Exception as exc:
            self._done_error(str(exc))
 
    # ── thread-safe UI helpers ────────────────────────────────────────────────
 
    def _set_status(self, msg: str):
        self.after(0, lambda: self.status_var.set(msg))
 
    def _done_ok(self, out_path: str):
        def _inner():
            self.progress.stop()
            self.status_var.set(f"✅  Saved: {out_path}")
            self.run_btn.configure(state="normal")
            if messagebox.askyesno("Done!",
                                   f"Transcript saved to:\n{out_path}\n\nOpen the folder?"):
                self._open_folder(os.path.dirname(out_path))
        self.after(0, _inner)
 
    def _done_error(self, msg: str):
        def _inner():
            self.progress.stop()
            self.status_var.set("❌  Error — see dialog")
            self.run_btn.configure(state="normal")
            messagebox.showerror("Transcription failed", msg)
        self.after(0, _inner)
 
    @staticmethod
    def _open_folder(path: str):
        import subprocess
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
 