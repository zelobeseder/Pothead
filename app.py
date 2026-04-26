import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import os
import importlib.util

CORE = os.getenv("CORE_MODULE", "scheduler_core")
if CORE == "beta":
    import scheduler_core_beta as core
else:
    import Scheduler_core as core

config = core.DEFAULT_CONFIG.copy()
BG = config["bg_color"]

visual_profile = "exponential"

APP_TITLE = f"Process manager&scheduler\n{core.CORE_NAME} v{core.CORE_VERSION}\n\nKitchen scheduler prototype."

run_scheduler = core.run_scheduler
plot_schedule = core.plot_schedule

from style import apply_style
from profiles import PROFILES


def _load_processes_from_file(filepath):
    try:
        spec = importlib.util.spec_from_file_location("_user_processes", filepath)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if not hasattr(mod, "ALL_PROCESSES"):
            raise AttributeError(f"No ALL_PROCESSES found in {filepath}")
        return mod.ALL_PROCESSES
    except (SyntaxError, AttributeError, Exception) as e:
        messagebox.showerror("Error loading processes", str(e))
        raise


PROCESSES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "processes.py")

ALL_PROCESSES = None  # resolved in _resolve_processes() after root is created

canvas_widget = None
last_data = None
process_vars = {}
dropdown_open = False


def show_help():
    win = tk.Toplevel(root)
    win.title("Help")
    win.resizable(False, False)
    win.configure(bg=BG)

    notebook = ttk.Notebook(win)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # --- Tab 1: Profiles ---
    profiles_tab = tk.Frame(notebook, bg=BG)
    notebook.add(profiles_tab, text="Profiles")

    tk.Label(
        profiles_tab,
        text="Visual profile:",
        bg=BG, fg="#ffffff",
        font=("Arial", 13)
    ).pack(anchor="w", padx=12, pady=(12, 4))

    profile_var = tk.StringVar(value=visual_profile)
    for name in PROFILES:
        rb = tk.Radiobutton(
            profiles_tab,
            text=name,
            variable=profile_var,
            value=name,
            bg=BG, fg="#ffffff",
            selectcolor=BG,
            activebackground=BG,
            font=("Arial", 12)
        )
        rb.pack(anchor="w", padx=24, pady=2)

    def apply_profile():
        global visual_profile
        visual_profile = profile_var.get()
        redraw_plot()
        win.destroy()

    tk.Button(
        profiles_tab,
        text="Apply",
        command=apply_profile,
        width=12
    ).pack(pady=(10, 14))

    # --- Tab 2: Service (hidden behind subtle label) ---
    service_tab = tk.Frame(notebook, bg=BG)
    notebook.add(service_tab, text="· · ·")

    tk.Label(
        service_tab,
        text="Service functions",
        bg=BG, fg="#888888",
        font=("Arial", 12, "italic")
    ).pack(pady=(16, 8))

    def restart_app():
        import sys
        win.destroy()
        root.destroy()
        os.execv(sys.executable, [sys.executable] + sys.argv)

    def clear_list():
        for var in process_vars.values():
            var.set(False)
        win.destroy()

    tk.Button(
        service_tab,
        text="Restart",
        command=restart_app,
        width=14
    ).pack(pady=6)

    tk.Button(
        service_tab,
        text="Clear list",
        command=clear_list,
        width=14
    ).pack(pady=6)


def toggle_dropdown():
    global dropdown_open

    if dropdown_open:
        dropdown_outer.place_forget()
        dropdown_open = False
        return

    root.update_idletasks()

    # координаты кнопки относительно root
    root_x = root.winfo_rootx()
    root_y = root.winfo_rooty()

    btn_x = process_btn.winfo_rootx() - root_x
    btn_y = process_btn.winfo_rooty() - root_y

    content_h = dropdown_frame.winfo_reqheight()
    content_w = dropdown_frame.winfo_reqwidth() + 2  # +2 for border

    need_scroll = content_h > DROPDOWN_MAX_H
    panel_h = DROPDOWN_MAX_H if need_scroll else content_h

    if need_scroll:
        dropdown_scrollbar.pack(side="right", fill="y")
    else:
        dropdown_scrollbar.pack_forget()

    dropdown_canvas.pack(side="left", fill="both", expand=True)
    dropdown_canvas.configure(width=content_w, height=panel_h)

    # ставим над кнопкой
    x = btn_x
    y = btn_y - panel_h - 6

    # страховка: если ушло слишком высоко, прижимаем к верхнему краю окна
    if y < 8:
        y = 8

    dropdown_outer.place(x=x, y=y, width=content_w + (16 if need_scroll else 0), height=panel_h)
    dropdown_outer.lift()
    dropdown_open = True


MAX_PROCESSES = 7


def _on_var_changed(name, *_):
    """Block checking a box when MAX_PROCESSES are already selected."""
    var = process_vars[name]
    if var.get():
        selected = sum(1 for v in process_vars.values() if v.get())
        if selected > MAX_PROCESSES:
            var.set(False)
            messagebox.showwarning(
                "Limit reached",
                f"Maximum {MAX_PROCESSES} processes allowed simultaneously.\n"
                "Deselect one before adding another."
            )


def on_calculate():
    global last_data

    selected_processes = [
        p for p in ALL_PROCESSES
        if process_vars[p["name"]].get()
    ]

    if not selected_processes:
        messagebox.showwarning("Warning", "Select at least one process.")
        return

    if len(selected_processes) > MAX_PROCESSES:
        messagebox.showwarning(
            "Too many processes",
            f"Maximum {MAX_PROCESSES} processes allowed. Please deselect some."
        )
        return

    try:
        scheduled, report_lines, report, config = run_scheduler(selected_processes)

        last_data = (scheduled, config)

        schedule_text.delete("1.0", tk.END)
        capacity_text.delete("1.0", tk.END)

        for line in report_lines:
            schedule_text.insert(tk.END, line + "\n")

        capacity_text.insert(
            tk.END,
            f"max simultaneously active: {report['max_active']}\n"
        )
        capacity_text.insert(
            tk.END,
            f"peak total load: {report['peak_total_load']}\n"
        )
        capacity_text.insert(
            tk.END,
            f"base_operator_mass: {report['base_operator_mass']}\n"
        )
        capacity_text.insert(
            tk.END,
            f"boost_power: {report['boost_power']}\n"
        )
        capacity_text.insert(
            tk.END,
            f"environment_load: {report['environment_load']}\n"
        )

        if report["overloads"]:
            capacity_text.insert(tk.END, "\nOverloads\n")
            for item in report["overloads"][:25]:
                capacity_text.insert(
                    tk.END,
                    f"t={item[0]} | active={item[1]} | load={item[2]} | capacity={item[3]}\n"
                )
        else:
            capacity_text.insert(tk.END, "\nNo overloads found.\n")

        redraw_plot()

    except Exception as e:
        messagebox.showerror("Ошибка", str(e))


def redraw_plot():
    global canvas_widget, last_data

    if not last_data:
        return

    scheduled, config = last_data
    fig = plot_schedule(scheduled, config, visual_profile=visual_profile)

    if canvas_widget is not None:
        canvas_widget.get_tk_widget().destroy()

    canvas_widget = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas_widget.draw()
    canvas_widget.get_tk_widget().configure(bg=BG)
    canvas_widget.get_tk_widget().pack()

# --- ROOT ---
root = tk.Tk()
root.title("POT HEAD")
root.geometry("920x660")
root.configure(bg=BG)
root.resizable(False, False)

# --- STARTUP: resolve processes file ---
def _resolve_processes():
    global ALL_PROCESSES
    if os.path.isfile(PROCESSES_FILE):
        ALL_PROCESSES = _load_processes_from_file(PROCESSES_FILE)
        return
    messagebox.showinfo(
        "Processes file not found",
        f"File not found:\n{PROCESSES_FILE}\n\nPlease select your processes.py file."
    )
    path = filedialog.askopenfilename(
        title="Select processes.py",
        filetypes=[("Python files", "*.py"), ("All files", "*.*")]
    )
    if path:
        ALL_PROCESSES = _load_processes_from_file(path)
    else:
        try:
            from processes import ALL_PROCESSES as _builtin
            ALL_PROCESSES = _builtin
        except ImportError:
            messagebox.showerror(
                "No processes file",
                "No processes file was selected and no built-in processes.py was found.\n"
                "The application will start with an empty process list."
            )
            ALL_PROCESSES = []

_resolve_processes()

# --- TOP: graph ---
top_frame = tk.Frame(root, bg=BG, height=360)
top_frame.pack(fill="both", expand=True, padx=14, pady=(14, 0))
top_frame.pack_propagate(False)

plot_frame = tk.Frame(top_frame, bg=BG)
plot_frame.pack(fill="both", expand=True)

# --- MIDDLE: info ---
info_frame = tk.Frame(root, bg=BG, height=210)
info_frame.pack(fill="x", padx=14)
info_frame.pack_propagate(False)

left_info = tk.Frame(info_frame, bg=BG)
left_info.pack(side="left", fill="both", expand=True, padx=(12, 18), pady=12)

right_info = tk.Frame(info_frame, bg=BG, width=360)
right_info.pack(side="right", fill="both", padx=(0, 12), pady=12)
right_info.pack_propagate(False)

schedule_label = tk.Label(left_info, text="Schedule")
schedule_label.pack(anchor="w", pady=(0, 6))

schedule_text = tk.Text(left_info, height=8, wrap="word")
schedule_text.pack(fill="both", expand=True)

capacity_label = tk.Label(right_info, text="Capacity")
capacity_label.pack(anchor="w", pady=(0, 6))

capacity_text = tk.Text(right_info, height=8, wrap="word")
capacity_text.pack(fill="both", expand=True)

# --- BOTTOM: controls ---
control_frame = tk.Frame(root, bg=BG, height=56)
control_frame.pack(fill="x", padx=14, pady=(0, 14))
control_frame.pack_propagate(False)

dropdown_outer = tk.Frame(root, bg=BG, bd=1, relief="solid")
dropdown_outer.place_forget()

DROPDOWN_MAX_H = 300
DROPDOWN_ITEM_H = 28  # approx per checkbox row

dropdown_canvas = tk.Canvas(dropdown_outer, bg=BG, highlightthickness=0)
dropdown_scrollbar = tk.Scrollbar(
    dropdown_outer, orient="vertical", command=dropdown_canvas.yview
)
dropdown_frame = tk.Frame(dropdown_canvas, bg=BG)

dropdown_frame_id = dropdown_canvas.create_window((0, 0), window=dropdown_frame, anchor="nw")

dropdown_canvas.configure(yscrollcommand=dropdown_scrollbar.set)

def _on_dropdown_frame_configure(event):
    dropdown_canvas.configure(scrollregion=dropdown_canvas.bbox("all"))
    w = dropdown_frame.winfo_reqwidth()
    dropdown_canvas.itemconfig(dropdown_frame_id, width=w)

dropdown_frame.bind("<Configure>", _on_dropdown_frame_configure)

def _on_mousewheel(event):
    dropdown_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

dropdown_canvas.bind_all("<MouseWheel>", _on_mousewheel)

process_btn = tk.Button(
    control_frame,
    text="Processes ▾",
    command=toggle_dropdown,
    width=14
)
process_btn.pack(side="left", padx=(0, 8), pady=8)

for proc in ALL_PROCESSES:
    var = tk.BooleanVar(value=False)
    process_vars[proc["name"]] = var
    var.trace_add("write", lambda *_, n=proc["name"]: _on_var_changed(n))

    chk = tk.Checkbutton(
        dropdown_frame,
        text=proc["name"],
        variable=var,
        anchor="w"
    )
    chk.pack(fill="x", padx=8, pady=2)

calc_btn = tk.Button(
    control_frame,
    text="Calculate",
    command=on_calculate,
    width=16
)
calc_btn.pack(side="left", padx=(0, 12), pady=8)

footer_text = f"{core.CORE_NAME} v{core.CORE_VERSION}"
footer_label = tk.Label(control_frame, text=footer_text, fg="white", bg=BG)
footer_label.pack(side="left", expand=True)

about_btn = tk.Button(
    control_frame,
    text="?",
    command=show_help,
    width=2
)
about_btn.pack(side="right", padx=10, pady=8)

apply_style(
    root,
    {
        "top_frame": top_frame,
        "plot_frame": plot_frame,
        "info_frame": info_frame,
        "left_info": left_info,
        "right_info": right_info,
        "schedule_label": schedule_label,
        "capacity_label": capacity_label,
        "schedule_text": schedule_text,
        "capacity_text": capacity_text,
        "control_frame": control_frame,
        "calc_btn": calc_btn,
        "footer_label": footer_label,
        "about_btn": about_btn,
    },
    theme="soft_dark"
)

root.mainloop()