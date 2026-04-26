"""
Hell Modulator — Main Application
A signal modulator with profile management and real-time preview.
"""

import importlib
import json
import math
import os
import sys
import subprocess
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
APP_NAME = "Hell Modulator"
APP_VERSION = "1.0"
PROCESS_MODULE = "process"
PROCESS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "process.py")
PROFILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "profiles")

WAVEFORMS = ("Sine", "Square", "Sawtooth", "Triangle")
MOD_TYPES = ("AM", "FM", "PM")

DARK_BG = "#1a1a2e"
DARK_PANEL = "#16213e"
DARK_ACCENT = "#e94560"
DARK_ACCENT2 = "#0f3460"
DARK_TEXT = "#eaeaea"
DARK_ENTRY = "#0d1b2a"
DARK_BORDER = "#e94560"

HELP_TEXT = """\
Hell Modulator — Quick Start

1. Waveform — select the shape of the modulating signal:
   Sine, Square, Sawtooth, Triangle.

2. Frequency (Hz) — frequency of the modulating signal.

3. Amplitude — signal amplitude from 0.0 to 1.0.

4. Modulation Type — AM / FM / PM.

5. Modulation Depth — strength of modulation (0.0–1.0 for AM/PM, any for FM).

6. Carrier Frequency (Hz) — frequency of the carrier wave.

7. Click "Modulate" to compute the signal and see the waveform preview.

8. Use "Save Profile" to save current settings for later.

9. Use the "Profiles" tab to load any saved profile.

10. The "Restart" button fully restarts the application without clearing profiles.
"""


# ---------------------------------------------------------------------------
# Process-file check
# ---------------------------------------------------------------------------
def check_process_file():
    """Check that process.py exists; ask the user to download it if missing."""
    if os.path.exists(PROCESS_FILE):
        return True

    answer = messagebox.askyesno(
        "Process file missing",
        f"The required process engine file was not found:\n\n  {PROCESS_FILE}\n\n"
        "Would you like to download it now?",
        icon="warning",
    )
    if answer:
        _download_process_file()
        if os.path.exists(PROCESS_FILE):
            return True
        messagebox.showerror(
            "Download failed",
            "Could not restore the process file. "
            "Please place process.py next to main.py and restart.",
        )
    return False


def _download_process_file():
    """
    Attempt to fetch process.py from the project's GitHub repository.
    Falls back to creating a minimal stub if the network is unavailable.
    """
    raw_url = (
        "https://raw.githubusercontent.com/zelobeseder/Pothead/main/process.py"
    )
    try:
        import urllib.request

        urllib.request.urlretrieve(raw_url, PROCESS_FILE)
        messagebox.showinfo("Download complete", "process.py downloaded successfully.")
        return
    except Exception:
        pass

    # Offline fallback: write a minimal stub so the app can still launch.
    stub = (
        '"""Hell Modulator process stub (auto-generated)."""\n'
        "import math, os, json\n\n"
        "WAVEFORMS = ('Sine', 'Square', 'Sawtooth', 'Triangle')\n"
        "MOD_TYPES = ('AM', 'FM', 'PM')\n\n"
        "def list_profiles(d): return []\n"
        "def load_profile_from_file(p): return {}\n"
        "def process_profile(profile, duration=1.0): return {'signal':[], 'peak':0.0, 'rms':0.0, 'profile':profile}\n"
    )
    with open(PROCESS_FILE, "w", encoding="utf-8") as fh:
        fh.write(stub)
    messagebox.showwarning(
        "Offline stub created",
        "Could not reach the internet.\n"
        "A minimal process.py stub was created so the app can start,\n"
        "but full modulation features will be unavailable until the real\n"
        "process.py is placed next to main.py.",
    )


# ---------------------------------------------------------------------------
# Help / About window
# ---------------------------------------------------------------------------
class HelpWindow(tk.Toplevel):
    def __init__(self, master, process_module):
        super().__init__(master)
        self.title("Help & Profiles")
        self.geometry("640x480")
        self.resizable(True, True)
        self.configure(bg=DARK_BG)
        self._process = process_module
        self._master_app = master

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=8, pady=8)

        # Tab 1 — How to use
        help_frame = tk.Frame(nb, bg=DARK_BG)
        nb.add(help_frame, text="  How to use  ")
        self._build_help_tab(help_frame)

        # Tab 2 — Profiles
        profiles_frame = tk.Frame(nb, bg=DARK_BG)
        nb.add(profiles_frame, text="  Profiles  ")
        self._build_profiles_tab(profiles_frame)

        close_btn = tk.Button(
            self, text="Close", command=self.destroy,
            bg=DARK_ACCENT2, fg=DARK_TEXT, activebackground=DARK_ACCENT,
            relief="flat", padx=16, pady=4,
        )
        close_btn.pack(pady=(0, 8))

    # ---- Help tab ----
    def _build_help_tab(self, parent):
        txt = tk.Text(
            parent, bg=DARK_ENTRY, fg=DARK_TEXT, insertbackground=DARK_TEXT,
            relief="flat", wrap="word", font=("Consolas", 10), padx=10, pady=10,
        )
        txt.insert("1.0", HELP_TEXT)
        txt.config(state="disabled")
        scroll = ttk.Scrollbar(parent, orient="vertical", command=txt.yview)
        txt.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        txt.pack(fill="both", expand=True, padx=(8, 0), pady=8)

    # ---- Profiles tab ----
    def _build_profiles_tab(self, parent):
        top = tk.Frame(parent, bg=DARK_BG)
        top.pack(fill="x", padx=8, pady=(8, 4))

        tk.Label(top, text="Available profiles:", bg=DARK_BG, fg=DARK_TEXT,
                 font=("Segoe UI", 10)).pack(side="left")

        refresh_btn = tk.Button(
            top, text="⟳ Refresh", command=self._refresh_profiles,
            bg=DARK_ACCENT2, fg=DARK_TEXT, activebackground=DARK_ACCENT,
            relief="flat", padx=8,
        )
        refresh_btn.pack(side="right")

        browse_btn = tk.Button(
            top, text="Browse…", command=self._browse_profile,
            bg=DARK_ACCENT2, fg=DARK_TEXT, activebackground=DARK_ACCENT,
            relief="flat", padx=8,
        )
        browse_btn.pack(side="right", padx=(0, 4))

        # Listbox + scrollbar
        list_frame = tk.Frame(parent, bg=DARK_BG)
        list_frame.pack(fill="both", expand=True, padx=8, pady=4)

        self._profile_listbox = tk.Listbox(
            list_frame, bg=DARK_ENTRY, fg=DARK_TEXT, selectbackground=DARK_ACCENT,
            selectforeground=DARK_TEXT, relief="flat", font=("Segoe UI", 10),
            activestyle="none",
        )
        lb_scroll = ttk.Scrollbar(list_frame, orient="vertical",
                                  command=self._profile_listbox.yview)
        self._profile_listbox.configure(yscrollcommand=lb_scroll.set)
        lb_scroll.pack(side="right", fill="y")
        self._profile_listbox.pack(fill="both", expand=True)
        self._profile_listbox.bind("<Double-Button-1>", lambda e: self._load_selected())

        # Preview area
        self._preview_var = tk.StringVar(value="Select a profile to preview its settings.")
        preview = tk.Label(
            parent, textvariable=self._preview_var,
            bg=DARK_PANEL, fg=DARK_TEXT, justify="left",
            font=("Consolas", 9), anchor="nw", relief="flat",
            padx=8, pady=6,
        )
        preview.pack(fill="x", padx=8, pady=(0, 4))

        # Load button
        load_btn = tk.Button(
            parent, text="Load Profile", command=self._load_selected,
            bg=DARK_ACCENT, fg=DARK_TEXT, activebackground="#c73652",
            relief="flat", padx=16, pady=4, font=("Segoe UI", 10, "bold"),
        )
        load_btn.pack(pady=(0, 4))

        self._profile_paths = []
        self._refresh_profiles()
        self._profile_listbox.bind("<<ListboxSelect>>", self._on_select)

    def _refresh_profiles(self):
        self._profile_listbox.delete(0, "end")
        self._profile_paths = []
        if self._process:
            paths = self._process.list_profiles(PROFILES_DIR)
        else:
            paths = []
            if os.path.isdir(PROFILES_DIR):
                paths = [
                    os.path.join(PROFILES_DIR, fn)
                    for fn in sorted(os.listdir(PROFILES_DIR))
                    if fn.lower().endswith(".json")
                ]
        for p in paths:
            name = _profile_display_name(p)
            self._profile_listbox.insert("end", name)
            self._profile_paths.append(p)
        self._preview_var.set("Select a profile to preview its settings.")

    def _browse_profile(self):
        path = filedialog.askopenfilename(
            title="Open profile",
            filetypes=[("JSON profiles", "*.json"), ("All files", "*.*")],
        )
        if path:
            self._load_profile_path(path)

    def _on_select(self, _event=None):
        idx = self._profile_listbox.curselection()
        if not idx:
            return
        path = self._profile_paths[idx[0]]
        try:
            if self._process:
                data = self._process.load_profile_from_file(path)
            else:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            self._preview_var.set(_format_profile_preview(data))
        except Exception as exc:
            self._preview_var.set(f"Error reading profile: {exc}")

    def _load_selected(self):
        idx = self._profile_listbox.curselection()
        if not idx:
            messagebox.showwarning("No selection", "Please select a profile first.",
                                   parent=self)
            return
        self._load_profile_path(self._profile_paths[idx[0]])

    def _load_profile_path(self, path: str):
        try:
            if self._process:
                data = self._process.load_profile_from_file(path)
            else:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            self._master_app.apply_profile(data)
            messagebox.showinfo("Profile loaded",
                                f"Profile \"{data.get('name', 'unknown')}\" loaded.",
                                parent=self)
            self.destroy()
        except Exception as exc:
            messagebox.showerror("Error", f"Could not load profile:\n{exc}", parent=self)


# ---------------------------------------------------------------------------
# Waveform canvas preview
# ---------------------------------------------------------------------------
class WaveformCanvas(tk.Canvas):
    """Simple canvas that draws a signal preview."""

    def __init__(self, master, **kwargs):
        kwargs.setdefault("bg", DARK_ENTRY)
        kwargs.setdefault("highlightthickness", 1)
        kwargs.setdefault("highlightbackground", DARK_BORDER)
        super().__init__(master, **kwargs)
        self._samples: list[float] = []

    def set_samples(self, samples: list[float]):
        self._samples = samples
        self._draw()

    def _draw(self):
        self.delete("all")
        w = self.winfo_width() or int(self["width"])
        h = self.winfo_height() or int(self["height"])
        mid = h // 2

        # Centre line
        self.create_line(0, mid, w, mid, fill="#2a2a4a", dash=(4, 4))

        if not self._samples:
            self.create_text(w // 2, mid, text="No signal", fill="#555577",
                             font=("Segoe UI", 9))
            return

        samples = self._samples
        step = max(1, len(samples) // w)
        points = []
        for i in range(min(w, len(samples) // step)):
            s = samples[i * step]
            x = i
            y = mid - int(s * (h * 0.45))
            points.extend([x, y])

        if len(points) >= 4:
            self.create_line(*points, fill=DARK_ACCENT, width=1, smooth=False)


# ---------------------------------------------------------------------------
# Main Application Window
# ---------------------------------------------------------------------------
class HellModulatorApp(tk.Tk):
    def __init__(self, process_module):
        super().__init__()
        self._process = process_module
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry("760x600")
        self.minsize(600, 480)
        self.configure(bg=DARK_BG)

        self._apply_theme()
        self._build_ui()

    # ------------------------------------------------------------------ theme
    def _apply_theme(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook", background=DARK_BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=DARK_PANEL, foreground=DARK_TEXT,
                        padding=[10, 4], font=("Segoe UI", 9))
        style.map("TNotebook.Tab",
                  background=[("selected", DARK_ACCENT2)],
                  foreground=[("selected", DARK_TEXT)])
        style.configure("TScrollbar", background=DARK_PANEL, troughcolor=DARK_BG,
                        arrowcolor=DARK_TEXT)
        style.configure("Horizontal.TScale", background=DARK_BG,
                        troughcolor=DARK_ENTRY)

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        # ---- Header ----
        hdr = tk.Frame(self, bg=DARK_ACCENT2, pady=6)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🔥 HELL MODULATOR", bg=DARK_ACCENT2, fg=DARK_ACCENT,
                 font=("Segoe UI", 16, "bold")).pack(side="left", padx=16)
        tk.Label(hdr, text=f"v{APP_VERSION}", bg=DARK_ACCENT2, fg=DARK_TEXT,
                 font=("Segoe UI", 9)).pack(side="left")

        # ---- Toolbar ----
        toolbar = tk.Frame(self, bg=DARK_PANEL, pady=4)
        toolbar.pack(fill="x")

        btn_cfg = dict(bg=DARK_ACCENT2, fg=DARK_TEXT, activebackground=DARK_ACCENT,
                       relief="flat", padx=10, pady=3, font=("Segoe UI", 9))

        tk.Button(toolbar, text="⟳ Restart", command=self._restart, **btn_cfg).pack(
            side="left", padx=(8, 4))
        tk.Button(toolbar, text="? Help", command=self._open_help, **btn_cfg).pack(
            side="left", padx=4)
        tk.Button(toolbar, text="💾 Save Profile", command=self._save_profile,
                  **btn_cfg).pack(side="right", padx=8)
        tk.Button(toolbar, text="📂 Load Profile", command=self._open_profiles_tab,
                  **btn_cfg).pack(side="right", padx=4)

        # ---- Main area ----
        main_frame = tk.Frame(self, bg=DARK_BG)
        main_frame.pack(fill="both", expand=True, padx=12, pady=8)

        left = tk.Frame(main_frame, bg=DARK_BG)
        left.pack(side="left", fill="y", padx=(0, 12))

        right = tk.Frame(main_frame, bg=DARK_BG)
        right.pack(side="left", fill="both", expand=True)

        self._build_controls(left)
        self._build_preview(right)

        # ---- Status bar ----
        self._status_var = tk.StringVar(value="Ready.")
        status = tk.Label(self, textvariable=self._status_var, bg=DARK_PANEL,
                          fg=DARK_TEXT, anchor="w", font=("Segoe UI", 8), pady=3)
        status.pack(fill="x", side="bottom")

    def _build_controls(self, parent):
        lbl_cfg = dict(bg=DARK_BG, fg=DARK_TEXT, anchor="w",
                       font=("Segoe UI", 9))
        entry_cfg = dict(bg=DARK_ENTRY, fg=DARK_TEXT, insertbackground=DARK_TEXT,
                         relief="flat", font=("Segoe UI", 10), width=14)

        # --- Waveform ---
        tk.Label(parent, text="Waveform", **lbl_cfg).grid(
            row=0, column=0, sticky="w", pady=(0, 2))
        self._waveform_var = tk.StringVar(value="Sine")
        cb = ttk.Combobox(parent, textvariable=self._waveform_var,
                          values=WAVEFORMS, state="readonly", width=12)
        cb.grid(row=0, column=1, sticky="w", padx=(6, 0), pady=(0, 6))

        # --- Frequency ---
        tk.Label(parent, text="Frequency (Hz)", **lbl_cfg).grid(
            row=1, column=0, sticky="w", pady=(0, 2))
        self._freq_var = tk.StringVar(value="440")
        tk.Entry(parent, textvariable=self._freq_var, **entry_cfg).grid(
            row=1, column=1, sticky="w", padx=(6, 0), pady=(0, 6))

        # --- Amplitude ---
        tk.Label(parent, text="Amplitude", **lbl_cfg).grid(
            row=2, column=0, sticky="w", pady=(0, 2))
        self._amp_var = tk.DoubleVar(value=0.8)
        amp_scale = ttk.Scale(parent, from_=0.0, to=1.0, variable=self._amp_var,
                              orient="horizontal", length=130)
        amp_scale.grid(row=2, column=1, sticky="w", padx=(6, 0), pady=(0, 6))
        self._amp_label = tk.Label(parent, text="0.80", **lbl_cfg)
        self._amp_label.grid(row=2, column=2, sticky="w", padx=(4, 0))
        self._amp_var.trace_add("write", self._update_amp_label)

        # --- Modulation type ---
        tk.Label(parent, text="Modulation", **lbl_cfg).grid(
            row=3, column=0, sticky="w", pady=(0, 2))
        self._mod_type_var = tk.StringVar(value="AM")
        mt_cb = ttk.Combobox(parent, textvariable=self._mod_type_var,
                             values=MOD_TYPES, state="readonly", width=12)
        mt_cb.grid(row=3, column=1, sticky="w", padx=(6, 0), pady=(0, 6))

        # --- Modulation depth ---
        tk.Label(parent, text="Depth", **lbl_cfg).grid(
            row=4, column=0, sticky="w", pady=(0, 2))
        self._depth_var = tk.DoubleVar(value=0.5)
        depth_scale = ttk.Scale(parent, from_=0.0, to=1.0, variable=self._depth_var,
                                orient="horizontal", length=130)
        depth_scale.grid(row=4, column=1, sticky="w", padx=(6, 0), pady=(0, 6))
        self._depth_label = tk.Label(parent, text="0.50", **lbl_cfg)
        self._depth_label.grid(row=4, column=2, sticky="w", padx=(4, 0))
        self._depth_var.trace_add("write", self._update_depth_label)

        # --- Carrier frequency ---
        tk.Label(parent, text="Carrier (Hz)", **lbl_cfg).grid(
            row=5, column=0, sticky="w", pady=(0, 2))
        self._carrier_var = tk.StringVar(value="1000")
        tk.Entry(parent, textvariable=self._carrier_var, **entry_cfg).grid(
            row=5, column=1, sticky="w", padx=(6, 0), pady=(0, 6))

        # --- Sample rate ---
        tk.Label(parent, text="Sample Rate", **lbl_cfg).grid(
            row=6, column=0, sticky="w", pady=(0, 2))
        self._sample_rate_var = tk.StringVar(value="44100")
        sr_cb = ttk.Combobox(parent, textvariable=self._sample_rate_var,
                             values=["8000", "22050", "44100", "48000"],
                             state="readonly", width=12)
        sr_cb.grid(row=6, column=1, sticky="w", padx=(6, 0), pady=(0, 12))

        # --- Modulate button ---
        mod_btn = tk.Button(
            parent, text="▶  Modulate", command=self._run_modulation,
            bg=DARK_ACCENT, fg=DARK_TEXT, activebackground="#c73652",
            relief="flat", padx=16, pady=6, font=("Segoe UI", 11, "bold"),
        )
        mod_btn.grid(row=7, column=0, columnspan=3, sticky="ew", pady=(4, 0))

    def _build_preview(self, parent):
        tk.Label(parent, text="Signal Preview", bg=DARK_BG, fg=DARK_TEXT,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")

        self._wave_canvas = WaveformCanvas(parent, width=440, height=200)
        self._wave_canvas.pack(fill="both", expand=True, pady=(4, 8))

        # Stats frame
        stats = tk.Frame(parent, bg=DARK_PANEL, pady=6, padx=10)
        stats.pack(fill="x")
        self._peak_var = tk.StringVar(value="Peak: —")
        self._rms_var = tk.StringVar(value="RMS:  —")
        self._samples_var = tk.StringVar(value="Samples: —")

        for var in (self._peak_var, self._rms_var, self._samples_var):
            tk.Label(stats, textvariable=var, bg=DARK_PANEL, fg=DARK_TEXT,
                     font=("Consolas", 10), anchor="w").pack(anchor="w")

    # ---------------------------------------------------------------- helpers
    def _update_amp_label(self, *_):
        self._amp_label.config(text=f"{self._amp_var.get():.2f}")

    def _update_depth_label(self, *_):
        self._depth_label.config(text=f"{self._depth_var.get():.2f}")

    def _current_profile(self) -> dict:
        return {
            "name": "Custom",
            "waveform": self._waveform_var.get(),
            "frequency": float(self._freq_var.get() or 440),
            "amplitude": round(self._amp_var.get(), 4),
            "modulation_type": self._mod_type_var.get(),
            "modulation_depth": round(self._depth_var.get(), 4),
            "carrier_frequency": float(self._carrier_var.get() or 1000),
            "sample_rate": int(self._sample_rate_var.get() or 44100),
        }

    def apply_profile(self, data: dict):
        """Apply a loaded profile to all control widgets."""
        if "waveform" in data and data["waveform"] in WAVEFORMS:
            self._waveform_var.set(data["waveform"])
        if "frequency" in data:
            self._freq_var.set(str(data["frequency"]))
        if "amplitude" in data:
            self._amp_var.set(float(data["amplitude"]))
        if "modulation_type" in data and data["modulation_type"] in MOD_TYPES:
            self._mod_type_var.set(data["modulation_type"])
        if "modulation_depth" in data:
            self._depth_var.set(float(data["modulation_depth"]))
        if "carrier_frequency" in data:
            self._carrier_var.set(str(data["carrier_frequency"]))
        if "sample_rate" in data:
            self._sample_rate_var.set(str(data["sample_rate"]))
        self._status_var.set(f"Profile loaded: {data.get('name', 'unknown')}")

    # ---------------------------------------------------------------- actions
    def _run_modulation(self):
        try:
            profile = self._current_profile()
        except ValueError as exc:
            messagebox.showerror("Input error", str(exc))
            return

        self._status_var.set("Computing…")
        self.update_idletasks()

        try:
            result = self._process.process_profile(profile, duration=0.05)
        except Exception as exc:
            messagebox.showerror("Modulation error", str(exc))
            self._status_var.set("Error during modulation.")
            return

        signal = result["signal"]
        self._wave_canvas.set_samples(signal)
        self._wave_canvas.update()

        self._peak_var.set(f"Peak:    {result['peak']:.4f}")
        self._rms_var.set(f"RMS:     {result['rms']:.4f}")
        self._samples_var.set(f"Samples: {len(signal)}")
        self._status_var.set("Modulation complete.")

    def _open_help(self):
        HelpWindow(self, self._process)

    def _open_profiles_tab(self):
        win = HelpWindow(self, self._process)
        # Switch directly to the Profiles tab (index 1)
        win.after(50, lambda: win.nametowidget(win.winfo_children()[0]).select(1))

    def _save_profile(self):
        profile = self._current_profile()
        name = _ask_profile_name(self)
        if name is None:
            return
        profile["name"] = name

        os.makedirs(PROFILES_DIR, exist_ok=True)
        safe_name = "".join(c if c.isalnum() or c in "-_ " else "_" for c in name)
        path = os.path.join(PROFILES_DIR, f"{safe_name}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=4)
        self._status_var.set(f"Profile saved: {path}")
        messagebox.showinfo("Saved", f"Profile \"{name}\" saved to:\n{path}")

    def _restart(self):
        """Restart the application without clearing any settings."""
        self.destroy()
        os.execv(sys.executable, [sys.executable] + sys.argv)


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------
def _profile_display_name(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("name", os.path.basename(path))
    except Exception:
        return os.path.basename(path)


def _format_profile_preview(data: dict) -> str:
    lines = [
        f"Name:       {data.get('name', '—')}",
        f"Waveform:   {data.get('waveform', '—')}",
        f"Frequency:  {data.get('frequency', '—')} Hz",
        f"Amplitude:  {data.get('amplitude', '—')}",
        f"Modulation: {data.get('modulation_type', '—')}  "
        f"depth={data.get('modulation_depth', '—')}",
        f"Carrier:    {data.get('carrier_frequency', '—')} Hz",
        f"Sample rate:{data.get('sample_rate', '—')} Hz",
    ]
    if "description" in data:
        lines.insert(1, f"Desc:       {data['description']}")
    return "\n".join(lines)


def _ask_profile_name(parent) -> str | None:
    dialog = tk.Toplevel(parent)
    dialog.title("Save profile")
    dialog.geometry("320x120")
    dialog.configure(bg=DARK_BG)
    dialog.grab_set()
    dialog.transient(parent)

    tk.Label(dialog, text="Profile name:", bg=DARK_BG, fg=DARK_TEXT,
             font=("Segoe UI", 10)).pack(pady=(16, 4))

    name_var = tk.StringVar(value="My Profile")
    entry = tk.Entry(dialog, textvariable=name_var, bg=DARK_ENTRY, fg=DARK_TEXT,
                     insertbackground=DARK_TEXT, relief="flat",
                     font=("Segoe UI", 10), width=28)
    entry.pack()
    entry.select_range(0, "end")
    entry.focus_set()

    result = [None]

    def _ok(_event=None):
        result[0] = name_var.get().strip() or None
        dialog.destroy()

    def _cancel():
        dialog.destroy()

    btn_frame = tk.Frame(dialog, bg=DARK_BG)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="Save", command=_ok, bg=DARK_ACCENT, fg=DARK_TEXT,
              relief="flat", padx=10).pack(side="left", padx=4)
    tk.Button(btn_frame, text="Cancel", command=_cancel, bg=DARK_ACCENT2,
              fg=DARK_TEXT, relief="flat", padx=10).pack(side="left", padx=4)
    entry.bind("<Return>", _ok)
    dialog.bind("<Escape>", lambda e: _cancel())
    dialog.wait_window()
    return result[0]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    # 1. Ensure the process file exists before doing anything else.
    root_check = tk.Tk()
    root_check.withdraw()
    if not check_process_file():
        root_check.destroy()
        sys.exit(1)
    root_check.destroy()

    # 2. Dynamically import the process module (may have just been downloaded).
    spec = importlib.util.spec_from_file_location(PROCESS_MODULE, PROCESS_FILE)
    process_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(process_mod)

    # 3. Launch the main application.
    app = HellModulatorApp(process_mod)
    app.mainloop()


if __name__ == "__main__":
    main()
