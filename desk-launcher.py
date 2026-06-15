#!/usr/bin/env python3
import tkinter as tk

from tkinter import ttk, filedialog
import os
import glob
import shutil
import subprocess

DESKTOP_DIR = os.path.expanduser("~/Escritorio")
os.makedirs(DESKTOP_DIR, exist_ok=True)

def get_apps():
    apps = []
    dirs = [
        "/usr/share/applications",
        os.path.expanduser("~/.local/share/applications"),
        "/var/lib/snapd/desktop/applications"
    ]
    for d in dirs:
        for f in glob.glob(f"{d}/*.desktop"):
            try:
                name = ""
                nodisplay = False
                with open(f, encoding="utf-8", errors="ignore") as fp:
                    for line in fp:
                        if line.startswith("Name=") and not name:
                            name = line.strip().split("=",1)[1]
                        if line.startswith("NoDisplay=true"):
                            nodisplay = True
                if name and not nodisplay:
                    apps.append({"name": name, "file": f, "type": "app"})
            except:
                pass
    seen = set()
    unique = []
    for a in apps:
        if a["name"] not in seen:
            seen.add(a["name"])
            unique.append(a)
    return sorted(unique, key=lambda x: x["name"].lower())

def send_app_to_desktop(name, file):
    dest = os.path.join(DESKTOP_DIR, os.path.basename(file))
    shutil.copy2(file, dest)
    os.chmod(dest, 0o755)
    subprocess.run(["gio", "set", dest, "metadata::trusted", "true"], capture_output=True)
    status_var.set(f'✓ "{name}" enviado al escritorio')

def send_file_to_desktop():
    result = subprocess.run(["zenity", "--file-selection", "--title=Selecciona un archivo"], capture_output=True, text=True)
    file = result.stdout.strip()
    if not file:
        return
    name = os.path.basename(file)
    dest = os.path.join(DESKTOP_DIR, name)
    desktop_content = f"""[Desktop Entry]
Type=Link
Name={name}
URL=file://{file}
Icon=text-x-generic
"""
    with open(dest, "w") as f:
        f.write(desktop_content)
    os.chmod(dest, 0o755)
    subprocess.run(["gio", "set", dest, "metadata::trusted", "true"], capture_output=True)
    status_var.set(f'✓ "{name}" enviado al escritorio')

def filter_apps(*args):
    query = search_var.get().lower()
    listbox.delete(0, tk.END)
    for a in all_apps:
        if query in a["name"].lower():
            listbox.insert(tk.END, "  " + a["name"])

def on_select(event=None):
    sel = listbox.curselection()
    if not sel:
        return
    name = listbox.get(sel[0]).strip()
    for a in all_apps:
        if a["name"] == name:
            send_app_to_desktop(a["name"], a["file"])
            break

root = tk.Tk()
root.tk.call("tk", "appname", "desk-launcher")
root.tk.call("wm", "iconname", ".", "Escritorio Rápido")
root.wm_title("Escritorio Rápido")
root.title("Escritorio Rápido")
root.geometry("400x580")
root.configure(bg="#1e1e2e")
root.resizable(False, False)
try:
    icon_img = tk.PhotoImage(file=os.path.expanduser("~/.local/share/icons/desk-launcher.png"))
    root.iconphoto(True, icon_img)
except Exception:
    pass

# Header
header = tk.Frame(root, bg="#2a2a3e", pady=14)
header.pack(fill="x")

tk.Label(header, text="🖥  Escritorio Rápido",
         bg="#2a2a3e", fg="white",
         font=("Sans", 14, "bold")).pack()
tk.Label(header, text="Envía apps o archivos al escritorio",
         bg="#2a2a3e", fg="#888",
         font=("Sans", 9)).pack(pady=(2,0))

# Tabs
tab_frame = tk.Frame(root, bg="#1e1e2e")
tab_frame.pack(fill="x", padx=16, pady=(12,0))

def set_tab(t):
    if t == "apps":
        tab_apps.configure(bg="#5865f2", fg="white")
        tab_files.configure(bg="#2a2a3e", fg="#888")
        file_btn_frame.pack_forget()
        list_frame.pack(fill="both", expand=True, padx=16, pady=4)
        btn.pack(fill="x", padx=16, pady=(4,4))
    else:
        tab_apps.configure(bg="#2a2a3e", fg="#888")
        tab_files.configure(bg="#5865f2", fg="white")
        list_frame.pack_forget()
        btn.pack_forget()
        file_btn_frame.pack(fill="both", expand=True, padx=16, pady=16)

tab_apps = tk.Button(tab_frame, text="Aplicaciones",
                     bg="#5865f2", fg="white",
                     font=("Sans", 10, "bold"),
                     relief="flat", bd=0, padx=16, pady=8,
                     cursor="hand2",
                     command=lambda: set_tab("apps"))
tab_apps.pack(side="left", padx=(0,4))

tab_files = tk.Button(tab_frame, text="Archivos",
                      bg="#2a2a3e", fg="#888",
                      font=("Sans", 10, "bold"),
                      relief="flat", bd=0, padx=16, pady=8,
                      cursor="hand2",
                      command=lambda: set_tab("files"))
tab_files.pack(side="left")

# Search
search_frame = tk.Frame(root, bg="#2a2a3e", bd=0)
search_frame.pack(fill="x", padx=16, pady=(10,4))

tk.Label(search_frame, text="🔍", bg="#2a2a3e", fg="#888").pack(side="left", padx=(8,4), pady=8)
search_var = tk.StringVar()
search_var.trace("w", filter_apps)
search_entry = tk.Entry(search_frame, textvariable=search_var,
                        bg="#2a2a3e", fg="white",
                        insertbackground="white",
                        relief="flat", font=("Sans", 11), bd=0)
search_entry.pack(side="left", fill="x", expand=True, pady=8, padx=(0,8))
search_entry.focus()

# List
list_frame = tk.Frame(root, bg="#1e1e2e")
list_frame.pack(fill="both", expand=True, padx=16, pady=4)

scrollbar = tk.Scrollbar(list_frame, bg="#2a2a3e")
scrollbar.pack(side="right", fill="y")

listbox = tk.Listbox(list_frame,
                     bg="#2a2a3e", fg="white",
                     selectbackground="#5865f2",
                     selectforeground="white",
                     font=("Sans", 11),
                     relief="flat", bd=0,
                     activestyle="none",
                     yscrollcommand=scrollbar.set)
listbox.pack(fill="both", expand=True)
scrollbar.config(command=listbox.yview)
listbox.bind("<Double-Button-1>", on_select)
listbox.bind("<Return>", on_select)

# File button frame
file_btn_frame = tk.Frame(root, bg="#1e1e2e")
tk.Label(file_btn_frame,
         text="Selecciona cualquier archivo\ny lo enviamos al escritorio",
         bg="#1e1e2e", fg="#888",
         font=("Sans", 11),
         justify="center").pack(pady=(60,20))
tk.Button(file_btn_frame,
          text="📂  Seleccionar archivo",
          bg="#5865f2", fg="white",
          font=("Sans", 12, "bold"),
          relief="flat", bd=0,
          padx=24, pady=14,
          cursor="hand2",
          command=send_file_to_desktop).pack()

# Send button
btn = tk.Button(root, text="Enviar al escritorio",
                bg="#5865f2", fg="white",
                font=("Sans", 11, "bold"),
                relief="flat", bd=0,
                padx=20, pady=10,
                cursor="hand2",
                command=on_select)
btn.pack(fill="x", padx=16, pady=(4,4))

status_var = tk.StringVar(value="")
tk.Label(root, textvariable=status_var,
         bg="#1e1e2e", fg="#43b581",
         font=("Sans", 9)).pack(pady=(0,10))

all_apps = get_apps()
for a in all_apps:
    listbox.insert(tk.END, "  " + a["name"])

root.mainloop()
