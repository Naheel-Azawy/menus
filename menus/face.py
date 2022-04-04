import sh
import os
import sys
import tempfile
from subprocess import Popen, PIPE, STDOUT

FONT = os.getenv("FONT", "monospace") + ":pixelsize=19"

interface = "dmenu"
n = "naheel" in sh.dmenu("-v") # personal dmenu fork

# opts:
# - prompt: str
# - color: red|normal
# - dmenu: dmenu specific args
def dmenu_cmd(opts={}):
    if interface == "dmenu":
        cmd = "dmenu"

        #cmd += f" -fn '{FONT}'"
        #cmd += " -nf '#fff' -nb '#000' -sf '#000' -sb '#fff'"

        if "dmenu" in opts:
            dopts = opts["dmenu"]
        else:
            dopts = ""

        if "prompt" in opts:
            dopts += f" -p '{opts['prompt']}'"
        if "color" in opts and opts["color"] == "red":
            dopts += " -sb red -sf black -nb black -nf red"

        cmd += " " + dopts
        return cmd
    else:
        return None

# example:
# pipe = pipemenu()
# pipe.stdin.write("hi\n")
# pipe.stdin.write("hello\n")
# pipe.stdin.close()
# for line in iter(pipe.stdout.readline, ""):
#     print(line, end="")
def pipemenu(opts={}):
    cmd = dmenu_cmd(opts)
    pipe = Popen(cmd, shell=True,
                 universal_newlines=True,
                 stdin=PIPE, stdout=PIPE)
    return pipe

# example:
# dictmenu({"yep": lambda: print("yay"), "nope": None})
def dictmenu(d, opts={}):
    pipe = pipemenu(opts)
    for i in d:
        pipe.stdin.write(i + "\n")
    pipe.stdin.close()
    res = pipe.stdout.readlines()
    if res:
        res = res[-1].strip()
        if res in d and callable(d[res]):
            d[res]()

# example:
# confirm("Dude sure?!", lambda: print("yep"))
def confirm(msg, callback, no_callback=None, opts={}):
    if not msg:
        msg = "Are you sure?"
    opts["prompt"] = msg
    opts["color"] = "red"
    if "dmenu" in opts:
        opts["dmenu"] = "-i " + opts["dmenu"]
    else:
        opts["dmenu"] = "-i"
    dictmenu(
        {"Yes": callback, "No": no_callback}, opts)

def main(args):
    opts = {}
    i = 1
    while i < len(args):
        if args[i] == "--confirm":
            opts["confirm"] = True
        if args[i] == "--prompt" or args[i] == "-p":
            opts["prompt"] = args[i + 1]
            i += 1
        elif args[i] == "--color":
            opts["color"] = args[i + 1]
            i += 1
        elif args[i] == "--dmenu":
            opts["dmenu"] = args[i + 1]
            i += 1
        else:
            if "dmenu" not in opts:
                opts["dmenu"] = ""
            opts["dmenu"] += f"'{args[i]}' "
        i += 1

    if "confirm" in opts:
        msg = opts["prompt"] if "prompt" in opts else None
        confirm(msg, lambda: print("yes"))
    else:
        pipe = pipemenu(opts)
        for line in sys.stdin:
            pipe.stdin.write(line)
        pipe.stdin.close()
        for line in iter(pipe.stdout.readline, ""):
            print(line, end="")
