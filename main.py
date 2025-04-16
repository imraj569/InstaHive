import re
import requests
import instaloader
import telebot
import sys
from time import sleep
from dotenv import load_dotenv
import shutil,os,sys,requests,zipfile
from colorama import Fore,init
init(autoreset=True)

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

# Load only the Telegram bot token
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# Setup Instaloader
SESSION_FILE = "ig_session"
L = instaloader.Instaloader(
    download_video_thumbnails=False,
    download_geotags=False,
    download_comments=False,
    save_metadata=False,
    post_metadata_txt_pattern="",
    filename_pattern="{shortcode}"
)

# Login or load existing session
def login_instagram():
    if os.path.exists(SESSION_FILE):
        try:
            L.load_session_from_file(username=None, filename=SESSION_FILE)
            print("✅ Logged in using existing session.")
            return
        except Exception as e:
            print(f"⚠️ Failed to load session. Reason: {e}")
    
    print("🔐 Instagram Login Required")
    try:
        ig_username = input("📥 Instagram Username: ").strip()
        ig_password = input("🔑 Instagram Password: ").strip()
        L.login(ig_username, ig_password)
        L.save_session_to_file(SESSION_FILE)
        print("✅ Logged in and session saved.")
    except Exception as e:
        print(f"❌ Login failed. Please check your credentials.\nError: {e}")
        exit(1)

# Extract shortcode
def extract_shortcode(url):
    match = re.search(r"instagram\.com/(?:reel|p|tv)/([^/?#&]+)", url)
    return match.group(1) if match else None

# Fetch post
def fetch_post(shortcode):
    return instaloader.Post.from_shortcode(L.context, shortcode)

# Send media
def send_media(chat_id, media_url, is_video):
    action = 'upload_video' if is_video else 'upload_photo'
    bot.send_chat_action(chat_id, action)

    r = requests.get(media_url, stream=True)
    if r.status_code == 200:
        media = r.content
        if is_video:
            bot.send_video(chat_id, media)
        else:
            bot.send_photo(chat_id, media)
    else:
        bot.send_message(chat_id, "⚠️ Failed to fetch media.")

# /start
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, """
👋 Welcome to the InstaHive Bot!

📥 Send me any public Instagram Reel, Post, or Video:
🔗 https://www.instagram.com/reel/shortcode/

I'll send:
✅ Cover image
✅ Post media (video/photo)
✅ Post details

🔧 Built by @imraj569  
🔗 GitHub: https://github.com/imraj569
""")

# Handle Instagram links
@bot.message_handler(func=lambda msg: True)
def handle_instagram_url(message):
    url = message.text.strip()
    shortcode = extract_shortcode(url)

    if not shortcode:
        bot.reply_to(message, "❌ Invalid Instagram URL. Please send a valid /p/, /reel/, or /tv/ link.")
        return

    bot.send_chat_action(message.chat.id, 'typing')

    try:
        post = fetch_post(shortcode)

        # Send cover
        bot.send_chat_action(message.chat.id, 'upload_photo')
        r = requests.get(post.url)
        if r.status_code == 200:
            bot.send_photo(message.chat.id, r.content, caption="🖼 Cover image")

        # Post details (removed inline caption preview)
        details = f"""📄 <b>Post Details</b>
👤 <b>User:</b> @{post.owner_username}
❤️ <b>Likes:</b> {post.likes}
🔗 <a href="{url}">View on Instagram</a>"""
        bot.send_message(message.chat.id, details, parse_mode="HTML", disable_web_page_preview=False)

        # ✨ Copyable caption
        caption = post.caption or "No caption"
        bot.send_message(message.chat.id, f"📝 <b>Full Caption:</b>\n<code>{caption.strip()}</code>", parse_mode="HTML")

       
        # Media
        if post.typename == "GraphSidecar":
            for node in post.get_sidecar_nodes():
                media_url = node.video_url if node.is_video else node.display_url
                send_media(message.chat.id, media_url, node.is_video)
        else:
            media_url = post.video_url if post.is_video else post.url
            send_media(message.chat.id, media_url, post.is_video)

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")


# Run bot
if __name__ == "__main__":
    check_and_update()
    login_instagram()
    print("🤖 Bot is running... by @imraj569")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"⚠️ Bot crashed: {e}")
        print("⏳ Restarting...")
        os.execl(sys.executable, sys.executable, *sys.argv)
