# Escritorio Rápido 🖥️

Utilidad para Linux que permite enviar aplicaciones y archivos al escritorio de forma rápida.

## Requisitos
- Python 3
- Tkinter (`sudo apt install python3-tk`)
- zenity (`sudo apt install zenity`)

## Instalación
```bash
cp desk-launcher.py ~/.local/bin/desk-launcher.py
cp desk-launcher.svg ~/.local/share/icons/desk-launcher.svg
cp desk-launcher.desktop ~/.local/share/applications/
gio set ~/.local/share/applications/desk-launcher.desktop metadata::trusted true
```

## Uso
Abre la app desde el menú de aplicaciones o el escritorio.
