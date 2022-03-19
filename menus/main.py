import sys
import os
import sh

import menus.start
import menus.face
import menus.power
import menus.hud
import menus.keys

def main():
    arg0 = sys.argv[0]
    args = sys.argv[1:]

    menus.face.interface = os.getenv("MENUS_INTERFACE", "dmenu")

    if len(args) > 0:
        if args[0] == "ls":
            menus.start.StartMenu().ls()
        elif args[0] == "power":
            return menus.power.main([arg0] + args[1:])
        elif args[0] == "hud":
            return menus.hud.main([arg0] + args[1:])
        elif args[0] == "keys":
            return menus.keys.main([arg0] + args[1:])
        elif args[0] == "face":
            return menus.face.main([arg0] + args[1:])
    elif len(args) == 0:
        try:
            window_id = sh.xdotool("getactivewindow").strip()
        except:
            window_id = None
        menus.start.StartMenu(window_id).show()
    else:
        print("usage: menus [ARGS]")
        return 1
    return 0

if __name__ == "__main__":
    exit(main())
