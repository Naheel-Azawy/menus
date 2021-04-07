import sys
import os
import sh

import menus.start
import menus.face
import menus.power
import menus.hud
import menus.keys
from menus.utils import handle_terminal, set_tmux_title

def main():
    arg0 = sys.argv[0]
    args = sys.argv[1:]

    menus.face.interface = os.getenv("MENUS_INTERFACE", "dmenu")
    window_id = None

    i = 0
    opts_count = 0
    while i < len(args):
        if args[i] == "--interm":
            menus.face.interface = "fzf"
            menus.face.interm = True
            opts_count += 1
        elif args[i] == "--winid":
            window_id = args[i + 1]
            i += 1
            opts_count += 2
        i += 1
    args = args[opts_count:]

    if window_id is None:
        try:
            window_id = sh.xdotool("getactivewindow").strip()
        except:
            window_id = None

    run_in_term = False
    if menus.face.interface == "fzf" and \
       not menus.face.interm:
        run_in_term = True

    if len(args) > 0:
        if args[0] == "ls":
            menus.start.StartMenu().ls()
        elif args[0] == "power":
            if run_in_term:
                return handle_terminal(["python3", arg0, "--interm"] + args)
            set_tmux_title()
            return menus.power.main([arg0] + args[1:])
        elif args[0] == "hud":
            return menus.hud.main([arg0] + args[1:])
        elif args[0] == "keys":
            return menus.keys.main([arg0] + args[1:])
        elif args[0] == "face":
            return menus.face.main([arg0] + args[1:])
    elif len(args) == 0:
        if run_in_term:
            t_args = ["python3", arg0, "--interm"]
            if window_id is not None:
                t_args += ["--winid", window_id]
            return handle_terminal(t_args + args)
        set_tmux_title()
        menus.start.StartMenu(window_id).show()
    else:
        print("usage: menus [ARGS]")
        return 1
    return 0

if __name__ == "__main__":
    exit(main())
