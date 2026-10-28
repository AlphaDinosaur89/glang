import colorama

colorama.init()

yellow_f = colorama.Fore.LIGHTYELLOW_EX
red_f = colorama.Fore.LIGHTRED_EX
green_f = colorama.Fore.LIGHTGREEN_EX
reset_f = colorama.Fore.RESET

def log(msg):
    print(f"{green_f}INFO:{reset_f} {msg}")

def warning(msg):
    print(f"{yellow_f}WARNING:{reset_f} {msg}")

def error(msg):
    print(f"{red_f}ERROR:{reset_f} {msg}")

def errorp(msg):
    """only prints the error without clog.error"""
    print(msg)

def fail(code=0):
    print("Compilation terminated due to previous error(s).")
    exit(code)