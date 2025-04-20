import os
import re
import sys
import requests
import instaloader
import telebot
import tempfile
import psutil
from dotenv import load_dotenv

class InstaHiveBot:
    def __init__(self):
        self.session_file = "ig_session"
        self._setup_bot()
        self._setup_instaloader()
        self._ensure_single_instance()

    def _setup_bot(self):
        load_dotenv()
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.bot = telebot.TeleBot(bot_token)

        # Handlers
        self.bot.message_handler(commands=['start'])(self._start_command)
        self.bot.message_handler(func=lambda msg: True)(self._handle_instagram_url)

    def _setup_instaloader(self):
        self.loader = instaloader.Instaloader(
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            post_metadata_txt_pattern="",
            filename_pattern="{shortcode}"
        )

    def _ensure_single_instance(self):
        lock_file = os.path.join(tempfile.gettempdir(), "instahive.lock")
        if os.path.exists(lock_file):
            try:
                with open(lock_file, "r") as f:
                    old_pid = int(f.read())
                    if psutil.pid_exists(old_pid):
                        print(f"⚠️ Terminating existing instance with PID {old_pid}")
                        os.kill(old_pid, 9)
            except Exception as e:
                print(f"⚠️ Error handling existing lock: {e}")
        with open(lock_file, "w") as f:
            f.write(str(os.getpid()))
        import atexit
        atexit.register(lambda: os.remove(lock_file) if os.path.exists(lock_file) else None)

    def login_instagram(self):
        if os.path.exists(self.session_file):
            try:
                self.loader.load_session_from_file(username=None, filename=self.session_file)
                print("✅ Logged in using existing session.")
                return
            except Exception as e:
                print(f"⚠️ Failed to load session. Reason: {e}")

        print("🔐 Instagram Login Required")
        try:
            username = input("📥 Instagram Username: ").strip()
            password = input("🔑 Instagram Password: ").strip()
            self.loader.login(username, password)
            self.loader.save_session_to_file(self.session_file)
            print("✅ Logged in and session saved.")
        except Exception as e:
            print(f"❌ Login failed. Please check your credentials.\nError: {e}")
            exit(1)

    def _start_command(self, message):
        self.bot.send_message(message.chat.id, """
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

    def _handle_instagram_url(self, message):
        url = message.text.strip()
        shortcode = self._extract_shortcode(url)

        if not shortcode:
            self.bot.reply_to(message, "❌ Invalid Instagram URL. Please send a valid /p/, /reel/, or /tv/ link.")
            return

        self.bot.send_chat_action(message.chat.id, 'typing')

        try:
            post = instaloader.Post.from_shortcode(self.loader.context, shortcode)

            # Cover
            self._send_image(message.chat.id, post.url, "🖼 Cover image")

            # Details
            details = f"""📄 <b>Post Details</b>
👤 <b>User:</b> @{post.owner_username}
❤️ <b>Likes:</b> {post.likes}
🔗 <a href="{url}">View on Instagram</a>"""
            self.bot.send_message(message.chat.id, details, parse_mode="HTML")

            # Caption
            caption = post.caption or "No caption"
            self.bot.send_message(message.chat.id, f"📝 <b>Full Caption:</b>\n<code>{caption.strip()}</code>", parse_mode="HTML")

            # Media
            if post.typename == "GraphSidecar":
                for node in post.get_sidecar_nodes():
                    media_url = node.video_url if node.is_video else node.display_url
                    self._send_media(message.chat.id, media_url, node.is_video)
            else:
                media_url = post.video_url if post.is_video else post.url
                self._send_media(message.chat.id, media_url, post.is_video)

        except Exception as e:
            self.bot.reply_to(message, f"❌ Error: {str(e)}")

    def _extract_shortcode(self, url):
        match = re.search(r"instagram\.com/(?:reel|p|tv)/([^/?#&]+)", url)
        return match.group(1) if match else None

    def _send_image(self, chat_id, img_url, caption=""):
        try:
            r = requests.get(img_url, timeout=10)
            if r.status_code == 200:
                self.bot.send_photo(chat_id, r.content, caption=caption)
        except Exception as e:
            self.bot.send_message(chat_id, f"⚠️ Failed to send image: {str(e)}")

    def _send_media(self, chat_id, media_url, is_video):
        action = 'upload_video' if is_video else 'upload_photo'
        self.bot.send_chat_action(chat_id, action)

        try:
            with requests.get(media_url, stream=True, timeout=(5, 30)) as r:
                if r.status_code != 200:
                    self.bot.send_message(chat_id, "⚠️ Failed to fetch media.")
                    return

                suffix = '.mp4' if is_video else '.jpg'
                with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
                    for chunk in r.iter_content(8192):
                        f.write(chunk)
                    temp_path = f.name

            with open(temp_path, 'rb') as file:
                if is_video:
                    self.bot.send_video(chat_id, file, timeout=60)
                else:
                    self.bot.send_photo(chat_id, file, timeout=60)

            os.unlink(temp_path)

        except requests.exceptions.Timeout:
            self.bot.send_message(chat_id, "⌛ Media download timed out. Please try again.")
        except Exception as e:
            self.bot.send_message(chat_id, f"⚠️ Error: {str(e)}")

    def run(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.login_instagram()
        print("🤖 Bot is running... by @imraj569")
        try:
            self.bot.polling(none_stop=True)
        except Exception as e:
            print(f"⚠️ Bot crashed: {e}")
            print("⏳ Restarting...")
            os.execl(sys.executable, sys.executable, *sys.argv)


if __name__ == "__main__":
    bot = InstaHiveBot()
    bot.run()
