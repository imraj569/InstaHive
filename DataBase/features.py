import random
from colorama import Fore,init,Style
init(autoreset=True)

# Banner display
def show_banner():
    banners = [
        f"""{Fore.MAGENTA}
     ╭━━╮╱╱╱╱╱╭╮╱╱╱╭╮╱╭╮
     ╰┫┣╯╱╱╱╱╭╯╰╮╱╱┃┃╱┃┃
     ╱┃┃╭━╮╭━┻╮╭╋━━┫╰━╯┣┳╮╭┳━━╮
     ╱┃┃┃╭╮┫━━┫┃┃╭╮┃╭━╮┣┫╰╯┃┃━┫
     ╭┫┣┫┃┃┣━━┃╰┫╭╮┃┃╱┃┃┣╮╭┫┃━┫
     ╰━━┻╯╰┻━━┻━┻╯╰┻╯╱╰┻╯╰╯╰━━╯
     {Style.BRIGHT + Fore.YELLOW}Download Reels, Posts, & videos
     {Fore.CYAN}GitHub: https://github.com/imraj569
""",

        f"""{Fore.CYAN}
     ██╗███╗░░██╗░██████╗████████╗░█████╗░  ██╗░░██╗██╗██╗░░░██╗███████╗
     ██║████╗░██║██╔════╝╚══██╔══╝██╔══██╗  ██║░░██║██║██║░░░██║██╔════╝
     ██║██╔██╗██║╚█████╗░░░░██║░░░███████║  ███████║██║╚██╗░██╔╝█████╗░░
     ██║██║╚████║░╚═══██╗░░░██║░░░██╔══██║  ██╔══██║██║░╚████╔╝░██╔══╝░░
     ██║██║░╚███║██████╔╝░░░██║░░░██║░░██║  ██║░░██║██║░░╚██╔╝░░███████╗
     ╚═╝╚═╝░░╚══╝╚═════╝░░░░╚═╝░░░╚═╝░░╚═╝  ╚═╝░░╚═╝╚═╝░░░╚═╝░░░╚══════╝
     {Style.BRIGHT + Fore.YELLOW}Download from Instagram like a boss 💪
     {Fore.CYAN}GitHub: https://github.com/imraj569
""",

        f"""{Fore.GREEN}
     ▀█▀ █▀▀▄ █▀▀ ▀▀█▀▀ █▀▀█ 　 ▒█░▒█ ░▀░ ▀█░█▀ █▀▀ 
     ▒█░ █░░█ ▀▀█ ░░█░░ █▄▄█ 　 ▒█▀▀█ ▀█▀ ░█▄█░ █▀▀ 
     ▄█▄ ▀░░▀ ▀▀▀ ░░▀░░ ▀░░▀ 　 ▒█░▒█ ▀▀▀ ░░▀░░ ▀▀▀
     {Style.BRIGHT + Fore.YELLOW}InstaHive - Grab reels, posts & more
     {Fore.CYAN}GitHub: https://github.com/imraj569
"""
    ]
    print(random.choice(banners))