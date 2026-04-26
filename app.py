import tkinter as tk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import os

CORE = os.getenv("CORE_MODULE", "scheduler_core")
if CORE == "beta":
    import scheduler_core_beta as core
else:
    import scheduler_core as core

config = core.DEFAULT_CONFIG.copy()
BG = config["bg_color"]

visual_profile = "exponential"

APP_TITLE = f"Process manager&scheduler\n{core.CORE_NAME} v{core.CORE_VERSION}\n\nKitchen scheduler prototype."

run_scheduler = core.run_scheduler
plot_schedule = core.plot_schedule

from style import apply_style
from processes import ALL_PROCESSES

canvas_widget = None
last_data = None
process_vars = {}
dropdown_open = False


def show_about():
    messagebox.showinfo(
        "About",
        APP_TITLE
    )


def toggle_dropdown():
    global dropdown_open

    if dropdown_open:
        dropdown_frame.place_forget()
        dropdown_open = False
        return

    root.update_idletasks()

    # координаты кнопки относительно root
    root_x = root.winfo_rootx()
    root_y = root.winfo_rooty()

    btn_x = process_btn.winfo_rootx() - root_x
    btn_y = process_btn.winfo_rooty() - root_y

    # реальная высота dropdown после наполнения чекбоксами
    dropdown_h = dropdown_frame.winfo_reqheight()
    dropdown_w = dropdown_frame.winfo_reqwidth()

    # ставим над кнопкой
    x = btn_x
    y = btn_y - dropdown_h - 6

    # страховка: если ушло слишком высоко, прижимаем к верхнему краю окна
    if y < 8:
        y = 8

    dropdown_frame.place(x=x, y=y, width=dropdown_w, height=dropdown_h)
    dropdown_frame.lift()
    dropdown_open = True


def on_calculate():
    global last_data

    selected_processes = [
        p for p in ALL_PROCESSES
        if process_vars[p["name"]].get()
    ]

    if not selected_processes:
        messagebox.showwarning("Warning", "Select at least one process.")
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

dropdown_frame = tk.Frame(root, bg=BG, bd=1, relief="solid")
dropdown_frame.place_forget()

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
    command=show_about,
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