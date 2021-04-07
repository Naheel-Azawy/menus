import sys
import os

import menus.start
import menus.face
import menus.power
import menus.hud
import menus.keys
from menus.utils import handle_terminal

def main():
    arg0 = sys.argv[0]
    args = sys.argv[1:]

    menus.face.interface = os.getenv("MENUS_INTERFACE", "dmenu")

    run_in_term = False
    if len(args) > 0 and args[0] == "--interm":
        menus.face.interface = "fzf"
        menus.face.interm = True
        args = args[1:]
    elif menus.face.interface == "fzf":
        run_in_term = True

    if os.getenv("TMUX") is not None:
        try:
            sh.tmux("rename-window", "menu")
        except:
            pass

    if len(args) > 0:
        if args[0] == "ls":
            menus.start.main(["ls"])
        elif args[0] == "power":
            if run_in_term:
                return handle_terminal(["python3", arg0, "--interm"] + args)
            return menus.power.main([arg0] + args[1:])
        elif args[0] == "hud":
            return menus.hud.main([arg0] + args[1:])
        elif args[0] == "keys":
            return menus.keys.main([arg0] + args[1:])
        elif args[0] == "face":
            return menus.face.main([arg0] + args[1:])
    elif len(args) == 0:
        if run_in_term:
            return handle_terminal(["python3", arg0, "--interm"] + args)
        menus.start.main([])
    else:
        print("usage: menus [ARGS]")
        return 1
    return 0

if __name__ == "__main__":
    exit(main())
