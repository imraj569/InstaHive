import os,re,shutil,platform
import instaloader
from time import sleep
from DataBase.features import *

# Determine platform-specific download path
if platform.system() == "Windows":
    user = os.getlogin()
    download_path = f"C://Users//{user}//Downloads"
else:
    download_path = "/data/data/com.termux/files/home/storage/downloads"

session_file = "ig_session"
temp_dir = os.path.join(download_path, "temp_download")

# Clear screen
def clear_screen():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

# Extract shortcode
def extract_shortcode(url):
    match = re.search(r"instagram\.com/(?:reel|p|tv)/([^/?#&]+)", url)
    return match.group(1) if match else None

# Setup instaloader
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

    media_found = False
    for file in os.listdir(temp_dir):
        if (file.endswith((".mp4", ".jpg", ".jpeg", ".png")) and shortcode in file):
            old_path = os.path.join(temp_dir, file)
            new_filename = f"{post.owner_username}_{file}"
            new_path = os.path.join(download_path, new_filename)
            shutil.move(old_path, new_path)
            print(Fore.GREEN + f"[✓] Saved: {new_filename}")
            media_found = True

    if not media_found:
        print(Fore.RED + "[X] Media file not found.")
    shutil.rmtree(temp_dir)

# Start
clear_screen()
show_banner()

# Login
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
