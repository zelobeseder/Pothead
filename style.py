def apply_style(root, ui, theme="minimal_light"):

    themes = {

        # --- 1. ЧИСТЫЙ СВЕТЛЫЙ ---
        "minimal_light": {
            "root_bg": "#f4f4f4",
            "panel": "#ffffff",
            "control": "#f0f0f0",
            "text": "#1f1f1f",
            "button": "#2c2c2c",
            "button_text": "#ffffff",
            "accent": "#e6e6e6",
            "about": "#3a7afe",
        },

        # --- 2. МЯГКИЙ ТЁМНЫЙ ---
        "soft_dark": {
            "root_bg": "#1c1c1c",
            "panel": "#252525",
            "control": "#202020",
            "text": "#eaeaea",
            "button": "#3a3a3a",
            "button_text": "#ffffff",
            "accent": "#2d2d2d",
            "about": "#4d7cff",
        },

        # --- 3. ЛАБОРАТОРИЯ ---
        "mono_lab": {
            "root_bg": "#e9e9e9",
            "panel": "#ededed",
            "control": "#e0e0e0",
            "text": "#111111",
            "button": "#000000",
            "button_text": "#ffffff",
            "accent": "#d5d5d5",
            "about": "#000000",
        }
    }

    c = themes.get(theme, themes["minimal_light"])

    # --- ROOT ---
    root.configure(bg=c["root_bg"])

    # --- TOP ---
    ui["top_frame"].configure(bg=c["root_bg"])
    ui["plot_frame"].configure(bg=c["panel"])

    # --- MIDDLE ---
    ui["info_frame"].configure(bg=c["panel"])
    ui["left_info"].configure(bg=c["panel"])
    ui["right_info"].configure(bg=c["panel"])

    ui["schedule_label"].configure(
        bg=c["panel"],
        fg=c["text"],
        font=("Arial", 16)
    )

    ui["capacity_label"].configure(
        bg=c["panel"],
        fg=c["text"],
        font=("Arial", 16)
    )

    ui["schedule_text"].configure(
        bg=c["panel"],
        fg=c["text"],
        relief="flat",
        borderwidth=0,
        highlightthickness=0,
        font=("Menlo", 11)
    )

    ui["capacity_text"].configure(
        bg=c["panel"],
        fg=c["text"],
        relief="flat",
        borderwidth=0,
        highlightthickness=0,
        font=("Menlo", 11)
    )

    # --- BOTTOM ---
    ui["control_frame"].configure(bg=c["control"])

    ui["calc_btn"].configure(
        bg=c["button"],
        fg="#000000",
        activebackground=c["accent"],
        activeforeground=c["button_text"],
        relief="flat",
        font=("Arial", 14),
        borderwidth=0
    )

    ui["footer_label"].configure(
        bg=c["control"],
        fg="#888888",
        font=("Arial", 11)
    )

    ui["about_btn"].configure(
        bg=c["about"],
        fg="#000000",
        activebackground=c["accent"],
        relief="flat",
        font=("Arial", 13, "bold"),
        borderwidth=0
    )