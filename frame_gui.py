import os
import tkinter as tk
import threading
import ttkbootstrap as ttkb
import frame_sevices

from ttkbootstrap.constants import *
from ttkbootstrap import Style
from tkinter import filedialog, messagebox
from tkinter.colorchooser import askcolor


# ---- Интерфейс ----


def browse_input():
    folder = filedialog.askdirectory()
    if folder:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, folder)


def browse_output():
    folder = filedialog.askdirectory()
    if folder:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, folder)


def choose_color():
    color = askcolor()[1]
    if color:
        color_entry.delete(0, tk.END)
        color_entry.insert(0, color)


def start_processing():
    input_folder = input_entry.get()
    output_folder = output_entry.get()
    aspect = aspect_var.get()
    color = color_entry.get()
    thickness = thickness_entry.get()
    quality = int(quality_entry.get())
    frame_mode = frame_entry.get()

    def task():
        try:
            if not os.path.exists(input_folder):
                os.makedirs(input_folder)
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            total_files = len(
                [
                    f
                    for f in os.listdir(input_folder)
                    if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
                ]
            )
            if total_files == 0:
                root.after(
                    0,
                    lambda: messagebox.showerror(
                        "Ошибка", "В папке нет изображений для обработки!"
                    ),
                )
                return

            root.after(0, lambda: progress_bar.config(maximum=total_files))

            processed = frame_sevices.process_folder(
                input_folder=input_folder,
                output_folder=output_folder,
                aspect_ratio=aspect,
                border_thickness=thickness,
                border_color=color,
                quality=quality,
                frame_mode=frame_mode,
                progress_callback=update_progress,
            )

            root.after(
                0,
                lambda: messagebox.showinfo(
                    "Готово!", f"Обработано {processed} изображений!"
                ),
            )

        except Exception as e:
            root.after(0, lambda: messagebox.showerror("Ошибка", str(e)))

    threading.Thread(target=task, daemon=True).start()


def update_progress(processed, total_files):
    root.after(
        0,
        lambda: (
            progress_bar.config(value=processed),
            progress_label.config(text=f"{processed}/{total_files}"),
        ),
    )


style = Style("cosmo")

BG = style.colors.bg
BTN = style.colors.primary

root = style.master

icon_path = "main.ico"
if os.path.exists(icon_path):
    try:
        root.iconbitmap(icon_path)
    except:
        pass  # Если что — оставляем стандартную иконку

root.title("Frame Utility")
root.geometry("440x530")
root.resizable(False, False)

font_label = ("Segoe UI", 11)
font_entry = ("Segoe UI", 11)


def label(text):
    return ttkb.Label(root, text=text, font=font_label)


def entry(default_text=""):
    e = ttkb.Entry(root, font=font_entry)
    if default_text:
        e.insert(0, default_text)
    return e


# Разделитель
ttkb.Separator(root, bootstyle="secondary").grid(
    row=0, column=0, columnspan=3, sticky="ew", padx=15, pady=10
)

# Папки
label("Папка с исходниками:").grid(row=1, column=0, sticky="w", padx=15, pady=10)
input_entry = entry("input")
input_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
ttkb.Button(root, text="...", command=browse_input, bootstyle="secondary").grid(
    row=1, column=2
)

label("Папка для сохранения:").grid(row=2, column=0, sticky="w", padx=15, pady=10)
output_entry = entry("output")
output_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
ttkb.Button(root, text="...", command=browse_output, bootstyle="secondary").grid(
    row=2, column=2
)

# Соотношение
label("Соотношение сторон:").grid(row=3, column=0, sticky="w", padx=15, pady=10)
aspect_var = ttkb.StringVar(value="4:5")
aspect_combo = ttkb.Combobox(
    root, textvariable=aspect_var, font=font_entry, bootstyle="success"
)
aspect_combo["values"] = [
    "1:1",
    "4:5",
    "9:16",
    "16:9",
]
aspect_combo.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

# Цвет рамки
label("Цвет рамки:").grid(row=4, column=0, sticky="w", padx=15, pady=10)
color_entry = entry("white")
color_entry.grid(row=4, column=1, padx=10, pady=10, sticky="ew")
ttkb.Button(root, text="...", command=choose_color, bootstyle="secondary").grid(
    row=4, column=2
)

# Толщина
label("Толщина рамки:").grid(row=5, column=0, sticky="w", padx=15, pady=10)
thickness_entry = entry("5%")
thickness_entry.grid(row=5, column=1, padx=10, pady=10, sticky="ew")

# Качество
label("Качество JPEG:").grid(row=6, column=0, sticky="w", padx=15, pady=10)
quality_entry = entry("95")
quality_entry.grid(row=6, column=1, padx=10, pady=10, sticky="ew")

# Метка
label("Метка в названии:").grid(row=7, column=0, sticky="w", padx=15, pady=10)
frame_entry = entry("frame")
frame_entry.grid(row=7, column=1, padx=10, pady=10, sticky="ew")

# Прогресс
progress_label = ttkb.Label(root, text="0/0", font=("Segoe UI", 10))
progress_label.grid(row=8, column=0, columnspan=3, pady=(10, 5))

progress_bar = ttkb.Progressbar(
    root, orient=HORIZONTAL, length=400, mode="determinate", bootstyle="success-striped"
)
progress_bar.grid(row=9, column=0, columnspan=3, padx=15, pady=5)

# Старт
ttkb.Style().configure(
    "Start.TButton", font=("Segoe UI", 10), padding=10  # Задаём шрифт
)  # Делаем кнопку побольше
ttkb.Button(
    root,
    text="Применить",
    command=start_processing,
    bootstyle="primary",
    width=14,
    style="Start.TButton",
    padding=(5, 5),
).grid(row=10, column=0, columnspan=3, padx=50, pady=25)

root.mainloop()
