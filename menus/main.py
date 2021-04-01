import sh
import os
import sys
import json
from shutil import which

import menus.face
import menus.keys
import menus.power
import menus.hud

HOME = os.getenv("HOME")

class StartMenu:
    def __init__(self):
        self.cache = f"{HOME}/.cache"
        self.cache_recent = f"{self.cache}/launcher_recent.json"
        self.cache_bins = f"{self.cache}/dmenu_run"

        # pinned items appear first
        self.pinned = {
            "terminal": "theterm",
            "editor":   "edit",
            "files":    "lf",
            "browser":  "browser"
        }

        if which("theterm") is None:
            e = os.getenv("TERMINAL")
            self.pinned["terminal"] = e if e is not None else "xterm"

        if which("edit") is None:
            e = os.getenv("EDITOR")
            self.pinned["editor"] = e if e is not None else "nano"

        if which("lf") is None:
            e = os.getenv("FILE_MANAGER")
            self.pinned["files"] = e if e is not None else "nautilus"

        if which("browser") is None:
            e = os.getenv("BROWSER")
            self.pinned["browser"] = e if e is not None else "firefox"

        # programs below run in a terminal window
        # TODO: move to some kind of config
        self.tui_apps = [
            "music-player", "lf", "vis", "corona",
            "alsamixer", "lyrics", "nano", "dice"
        ]

        # personal games script. not sure whether to
        # remove or not. will keep it for now
        try:
            self.games = sh.games("list").strip().split("\n")
        except:
            self.games = []

        # recent items are cached
        try:
            self.recent = json.load(open(self.cache_recent))
        except:
            self.recent = {}

        # load power items
        self.power = menus.power.items()

        # global access to the hud interface not to load
        # the interface twice
        self.hud_interface = None

    # increment the counter for an item
    def inc(self, b, kind="bins"):
        # to keep the order of the kinds
        ordered = {
            "menu": {}, "bins": {},
            "games": {}, "power": {}
        }

        # copy self.recent to ordered
        for k in self.recent:
            ordered[k] = self.recent[k]

        # increment
        if b not in ordered[kind]:
            ordered[kind][b] = 1
        else:
            ordered[kind][b] += 1

        # sort
        for k in ordered:
            ordered[k] = dict(sorted(ordered[k].items(),
                                     key=lambda item: item[1],
                                     reverse=True))

        # save
        if not os.path.isdir(self.cache):
            os.makedirs(self.cache, exist_ok=True)
        json.dump(ordered, open(self.cache_recent, 'w'))
        self.recent = ordered

    # run the item in the arg
    def run(self, arg):
        arg = arg.strip()
        sp  = arg.split(":")
        kind = sp[0]
        if len(sp) > 1:
            del sp[0]
            run = ":".join(sp)
        else:
            run = sp[0]
            kind = ""
        run  = run.strip()
        kind = kind.strip()

        if kind == "power":
            sel = run.title()
            if sel in self.power:
                self.power[sel]()
                self.inc(sel, kind)

        elif kind == "shortcuts":
            run = run.split(":")[0].strip()
            menus.keys.run(run)

        elif kind == "menu":
            if self.hud_interface is not None:
                item = run.split(":")[0].strip()
                self.hud_interface.run(item)
                self.inc(item, kind)

        elif kind == "games":
            sh.games(run)
            self.inc(run, kind)

        else:
            if kind == "pinned":
                exe = self.pinned[run]
            elif kind == "bins":
                exe = run.split()[0]
            else:
                return
            if not exe:
                return
            if which(exe):
                if kind != "pinned":
                    self.inc(exe)
                if exe in self.tui_apps:
                    try:
                        sh.theterm(f"exec {exe}")
                    except sh.ErrorReturnCode as e:
                        print(e)
                else:
                    sh.Command(exe)()
            else:
                raise ValueError("Couldn't run given command")

    # replicates what the command `dmenu_path` does
    def path_bins(self):
        PATH = os.getenv("PATH").split(":")
        try:
            sh.stest("-dqr", "-n", self.cache_bins, *PATH) # if that
            for b in sh.tee(sh.sort(
                    sh.stest("-flx", *PATH, _piped=True), _piped=True
            ), self.cache_bins, _iter=True):
                b = b.strip()
                yield b
        except sh.ErrorReturnCode: # else
            with open(self.cache_bins, "r") as f:
                for b in f.readlines():
                    b = b.strip()
                    yield b

    # list the items out to the `out` stream
    def ls(self, cmd="", out=sys.stdout):

        # identifier of the item
        def ident(i):
            return ("%9s: ") % i

        # print to `out`
        def printout(kind, item):
            out.write(ident(kind) + item + "\n")

        # print only if not printed before
        def printout_if_needed(kind, item):
            if kind not in self.recent or item not in self.recent[kind]:
                printout(kind, item)

        # print pinned items first
        for item in self.pinned:
            printout("pinned", item)

        # load hud menu items and print if needed
        self.hud_interface = menus.hud.hud_load()
        if self.hud_interface is not None:
            title = sh.xdotool("getactivewindow", "getwindowname").strip()
            menuitems, mainbar = self.hud_interface.list()
            # print title and main bar if any
            if title:
                printout("menu", title)
            if mainbar:
                printout("menu", mainbar)
            # print recent menu items
            for item in self.recent["menu"]:
                if item in menuitems:
                    printout("menu", item)
            # print other menu items
            for item in menuitems:
                printout_if_needed("menu", item)

        # print other recent items
        for kind in ["bins", "games", "power"]:
            if kind in self.recent:
                for item in self.recent[kind]:
                    printout(kind, item)

        # print power options
        for item in self.power:
            printout_if_needed("power", item)

        # print keyboard shortcuts
        for item in menus.keys.get_doc():
            printout("shortcuts", item)

        # print games
        for item in self.games:
            printout_if_needed("games", item)

        # print other bins
        for item in self.path_bins():
            printout_if_needed("bins", item)

    # use the dmenu incremental patche
    # https://tools.suckless.org/dmenu/patches/incremental
    def query(self, cmd):
        expr = cmd[1:].strip()
        if not expr:
            return []

        # math (with octave)
        try:
            expr = "format long;" + expr
            res = sh.octave("--eval", expr) \
                    .strip().replace("ans = ", "")
            if res:
                return [f"{cmd} = {res}"]
        except sh.ErrorReturnCode:
            pass

        # math (with bc)
        try:
            os.environ["BC_LINE_LENGTH"] = "0"
            res = sh.bc(sh.echo(expr), "-l").strip()
            if res:
                return [f"{cmd} = {res}"]
        except sh.ErrorReturnCode:
            pass

        # find. too slow, find an alternative
        # if cmd.startswith("=find "):
        #     cmd = cmd[5:].strip()
        #     if not cmd:
        #         return []
        #     try:
        #         res = sh.locate(cmd).strip()
        #         if res:
        #             files = []
        #             for f in res.split("\n"):
        #                 files.append(f"{cmd} {f}")
        #     except sh.ErrorReturnCode:
        #         pass

        return []

    def show(self):
        incremental = os.popen(
            "man dmenu | grep " +
            "'dmenu outputs text each time a key is pressed'").read().strip()
        opts = "-i -l 20"
        if incremental:
            opts += " -r"

        pipe = menus.face.pipemenu(opts)
        self.ls(out=pipe.stdin)
        line = ""
        for line in iter(pipe.stdout.readline, ""):
            line = line.strip()
            if line.startswith("="):
                for res in self.query(line):
                    pipe.stdin.write(res + "\n")
                    pipe.stdin.flush()
        # pipe.stdin.close() # broken pipe, why?
        if line:
            self.run(line)

def main():
    args = sys.argv[1:]
    if len(args) > 0:
        if args[0] == "ls":
            StartMenu().ls()
        elif args[0] == "power":
            return menus.power.main(args[1:])
        elif args[0] == "hud":
            return menus.hud.main(args[1:])
        elif args[0] == "keys":
            return menus.keys.main(args[1:])
        elif args[0] == "face":
            return menus.face.main(args[1:])
    elif len(args) == 0:
        StartMenu().show()
    else:
        print("usage: start [ls]")
        return 1
    return 0

if __name__ == "__main__":
    exit(main())
