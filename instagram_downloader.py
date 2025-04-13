import os
import re
import instaloader
import shutil
from pathlib import Path
from colorama import init, Fore, Style
import platform

# Initialize colorama
init(autoreset=True)

# Set download directory
download_path = "/data/data/com.termux/files/home/storage/downloads"
session_file = "ig_session"
temp_dir = os.path.join(download_path, "temp_download")

# Clear screen function
def clear_screen():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

# Extract shortcode from IG URL
def extract_shortcode(url):
    match = re.search(r"instagram\.com/(?:reel|p|tv)/([^/?#&]+)", url)
    return match.group(1) if match else None

# Setup instaloader instance
L = instaloader.Instaloader(
    download_video_thumbnails=False,
    download_geotags=False,
    download_comments=False,
    save_metadata=False,
    post_metadata_txt_pattern="",
    filename_pattern="{shortcode}"
)

# Start of script
clear_screen()
print(Fore.CYAN + "=== Instagram Reel/Post Downloader ===")

# Ask once for username
username = input(Fore.YELLOW + "Enter your Instagram username: ")

# Try loading session or login
try:
    L.load_session_from_file(username, session_file)
    print(Fore.GREEN + "[+] Logged in with saved session.")
except FileNotFoundError:
    print(Fore.MAGENTA + "[!] No session found. Logging in...")
    password = input("Enter your Instagram password: ")
    try:
        L.login(username, password)
        L.save_session_to_file(session_file)
        print(Fore.GREEN + "[+] Login successful. Session saved.")
    except Exception as e:
        print(Fore.RED + f"[X] Login failed: {e}")
        exit()

# Main loop
while True:
    print()
    url = input(Fore.CYAN + "Enter Instagram reel/post URL (or type 'exit' to quit): ")

    if url.strip().lower() == "exit":
        print(Fore.YELLOW + "Exiting. Have a great day!")
        break

    shortcode = extract_shortcode(url)
    if not shortcode:
        print(Fore.RED + "[X] Invalid Instagram URL.")
        continue

    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)

        # Create and clean temp dir
        os.makedirs(temp_dir, exist_ok=True)
        L.dirname_pattern = temp_dir
        L.download_post(post, target="")

        # Move the video
        for file in os.listdir(temp_dir):
            if file.endswith(".mp4") and shortcode in file:
                old_path = os.path.join(temp_dir, file)
                new_filename = f"{post.owner_username}_{shortcode}.mp4"
                new_path = os.path.join(download_path, new_filename)
                shutil.move(old_path, new_path)
                print(Fore.GREEN + f"[✓] Video saved as: {new_filename}")
                break
        else:
            print(Fore.RED + "[X] No video file found.")
        
        shutil.rmtree(temp_dir)

    except Exception as e:
        print(Fore.RED + f"[X] Error downloading: {e}")
