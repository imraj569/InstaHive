import random
from time import sleep
from colorama import Fore,init,Style
init(autoreset=True)

def show_banner():
    banners = [
        f"""{Fore.MAGENTA}
╔══════════════════════════════════════════════╗
║     📸 InstaHive - Instagram Downloader     ║
╠══════════════════════════════════════════════╣
║ GitHub: https://github.com/imraj569          ║
╚══════════════════════════════════════════════╝
""",

        f"""{Fore.CYAN}
╔══════════════════════════════════════════════╗
║     📲 InstaHive - Grab Instagram Content   ║
╠══════════════════════════════════════════════╣
║ GitHub: https://github.com/imraj569          ║
╚══════════════════════════════════════════════╝
""",

        f"""{Fore.GREEN}
╔══════════════════════════════════════════════╗
║     🚀 InstaHive - Download Instagram Media  ║
╠══════════════════════════════════════════════╣
║ GitHub: https://github.com/imraj569          ║
╚══════════════════════════════════════════════╝
"""
    ]
    print(random.choice(banners))

