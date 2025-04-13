import os
import re
import shutil
import platform
import requests
import sys
import logging
import zipfile
from time import sleep
from tqdm import tqdm
import instaloader
from DataBase.features import *
from colorama import Fore

logging.basicConfig(level=logging.CRITICAL)

def get_latest_version():
    version_url = "https://raw.githubusercontent.com/imraj569/InstaHive/main/version.txt"
    try:
        response = requests.get(version_url, timeout=5)
        if response.status_code == 200:
            return response.text.strip()
        else:
            print(Fore.RED + "[X] Failed to fetch version from GitHub.")
    except Exception as e:
        print(Fore.RED + f"[X] Error fetching version: {e}")
    return None

# Check and update the script if a new version is found
def check_and_update():
    # Fetch the latest version from GitHub
    remote_version = get_latest_version()
    
    # Check if the remote version exists and is different from the current version
    if remote_version:
        if remote_version != get_current_version():  # Compare with current version in the script
            print(Fore.MAGENTA + f"[!] New version available: {remote_version}. Updating...")
            update_script(remote_version)  # If update is needed, update the script
        else:
            print(Fore.GREEN + "[✓] You’re already using the latest version.")

# Update the script with the new code from GitHub
def update_script(remote_version):
    repo_url = "https://github.com/imraj569/InstaHive/archive/refs/heads/main.zip"
    download_path = "InstaHive-main.zip"

    # Download the entire repository as a zip
    try:
        print(Fore.YELLOW + "[*] Downloading the latest version of the repository...")
        response = requests.get(repo_url, stream=True)
        if response.status_code == 200:
            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            print(Fore.GREEN + "[✓] Repository downloaded successfully.")
        else:
            print(Fore.RED + "[X] Failed to download the repository.")
            return
    except Exception as e:
        print(Fore.RED + f"[X] Error downloading repository: {e}")
        return

    # Extract the downloaded ZIP file
    try:
        print(Fore.YELLOW + "[*] Extracting the repository...")
        with zipfile.ZipFile(download_path, 'r') as zip_ref:
            zip_ref.extractall()
        print(Fore.GREEN + "[✓] Repository extracted successfully.")
    except Exception as e:
        print(Fore.RED + f"[X] Error extracting repository: {e}")
        return

    # Replace the old files with the new ones
    extracted_folder = "InstaHive-main"
    for root, dirs, files in os.walk(extracted_folder):
        for file in files:
            # Skip the downloaded ZIP file itself
            if file == download_path:
                continue
            src_file = os.path.join(root, file)
            dst_file = os.path.join(os.getcwd(), file)

            try:
                # Replace old files with new ones
                if os.path.exists(dst_file):
                    os.remove(dst_file)
                shutil.copy(src_file, dst_file)
                print(Fore.GREEN + f"[✓] Replaced: {file}")
            except Exception as e:
                print(Fore.RED + f"[X] Error replacing {file}: {e}")

    # Clean up: Delete the downloaded ZIP and extracted folder
    os.remove(download_path)
    shutil.rmtree(extracted_folder)
    print(Fore.GREEN + "[✓] Update complete. Restarting...")
    sleep(2)
    os.execv(sys.executable, ['python'] + sys.argv)  # Restart the script to apply updates

# Function to get the current version of the script (use version.txt as the source)
def get_current_version():
    try:
        with open("version.txt", "r") as file:
            return file.read().strip()  # Get current version from the version.txt file
    except FileNotFoundError:
        print(Fore.RED + "[X] version.txt not found.")
    return "unknown"  # Default fallback version if version.txt isn't found

# Determine platform-specific download path
if platform.system() == "Windows":
    user = os.getlogin()
    download_path = f"C://Users//{user}//Downloads"
else:
    download_path = "/data/data/com.termux/files/home/storage/downloads"

session_file = "ig_session"
temp_dir = os.path.join(download_path, "temp_download")

# Clear screen function
def clear_screen():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

# Extract shortcode from URL
def extract_shortcode(url):
    match = re.search(r"instagram\.com/(?:reel|p|tv)/([^/?#&]+)", url)
    return match.group(1) if match else None

# Setup Instaloader
L = instaloader.Instaloader(
    download_video_thumbnails=False,
    download_geotags=False,
    download_comments=False,
    save_metadata=False,
    post_metadata_txt_pattern="",
    filename_pattern="{shortcode}"
)

# Download a single post (photo/video/album)
def download_post(shortcode):
    post = instaloader.Post.from_shortcode(L.context, shortcode)
    os.makedirs(temp_dir, exist_ok=True)
    L.dirname_pattern = temp_dir
    L.download_post(post, target="")

    files = [file for file in os.listdir(temp_dir) if (file.endswith((".mp4", ".jpg", ".jpeg", ".png")) and shortcode in file)]
    if not files:
        print(Fore.RED + "[X] Media file not found.")
        shutil.rmtree(temp_dir)
        return

    # Show progress bar during download
    for file in tqdm(files, desc="Downloading", colour="green"):
        old_path = os.path.join(temp_dir, file)
        new_filename = f"{post.owner_username}_{file}"
        new_path = os.path.join(download_path, new_filename)
        shutil.move(old_path, new_path)
        sleep(0.2)  # for progress bar effect

    print(Fore.GREEN + f"[✓] Saved {len(files)} file(s) successfully.")
    shutil.rmtree(temp_dir)
    sleep(2)
    clear_screen()
    show_banner()

# Start the script
clear_screen()
show_banner()

# Check for updates at the beginning
check_and_update()

# Login to Instagram
username = input(Fore.YELLOW + "Enter your Instagram username: ")
try:
    L.load_session_from_file(username, session_file)
    print(Fore.GREEN + "[✓] Logged in with saved session.")
    sleep(1)
    clear_screen()
    show_banner()
except FileNotFoundError:
    print(Fore.MAGENTA + "[!] No session found. Logging in...")
    password = input("Enter your Instagram password: ")
    try:
        L.login(username, password)
        L.save_session_to_file(session_file)
        print(Fore.GREEN + "[✓] Login successful. Session saved.")
        sleep(1)
        clear_screen()
        show_banner()
    except Exception as e:
        print(Fore.RED + f"[X] Login failed: {e}")
        exit()

# Main loop for downloading posts
while True:
    print()
    url = input(Fore.CYAN + "Paste Instagram URL (or type 'exit' to quit): ").strip()
    
    if url.lower() == "exit":
        print(Fore.YELLOW + "Goodbye! 👋")
        break

    shortcode = extract_shortcode(url)
    if not shortcode:
        print(Fore.RED + "[X] Unsupported or invalid URL.")
        continue
    try:
        download_post(shortcode)
    except Exception as e:
        print(Fore.RED + f"[X] Download failed: {e}")
