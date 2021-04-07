import os
import sh
import menus.face

def nohup(cmd):
    return f"nohup {cmd} </dev/null >/dev/null 2>&1 &"

def handle_terminal(args):
    try:
        dim = "95x20"
        TERMINAL = os.getenv("TERMINAL")
        if TERMINAL == "theterm":
            sh.theterm("-a", f"-c __floatme__|__blurme__ -g {dim}", "--nocd", *args)
        elif TERMINAL == "st":
            sh.st("-c", "__floatme__|__blurme__", "-g", dim, "-e", *args)
        else:
            sh.Command(TERMINAL, "-e", *args)
    except sh.ErrorReturnCode as e:
        pass
    return 0

def set_tmux_title():
    if menus.face.interface == "fzf" and \
       os.getenv("TMUX") is not None:
        try:
            sh.tmux("rename-window", "menu")
        except:
            pass
