from subprocess import Popen, PIPE, STDOUT
import sys

interface = "dmenu"

# opts:
# - prompt: str
# - color: red|normal
# - dmenu: dmenu specific args
def dmenu_cmd(opts={}):
    if interface == "dmenu":
        cmd = "dmenu"

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
    elif interface == "fzf":
        cmd = "fzf"
        cmd += " --reverse"
        cmd += " --no-sort"
        cmd += " --exact"
        cmd += " --info=hidden"
        cmd += " --pointer=' '"
        cmd += " --color=gutter:-1"
        cmd += " --color=hl:reverse,hl+:reverse"
        cmd += " --bind=change:first"
        cmd += " --print-query"

        if "prompt" in opts:
            if opts["prompt"]:
                cmd += f" --prompt='{opts['prompt']} '"
            else:
                cmd += " --prompt='> '"

        if "color" in opts and opts["color"] == "red":
            cmd += " --color='bg+:#ff0000,fg+:#000000,fg:#ff0000,prompt:#ff0000'"
        else:
            cmd += " --color='bg+:#ffffff,fg+:#000000,prompt:#ffffff'"

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
def confirm(msg, callback, no_callback=None):
    if not msg:
        msg = "Are you sure?"
    dictmenu(
        {"Yes": callback, "No": no_callback},
        opts={
            "prompt": msg,
            "color": "red",
            "dmenu": "-i"
        })

def main(args):
    opts = {}
    i = 0
    while i < len(args):
        if args[i] == "--confirm":
            opts["confirm"] = True
        if args[i] == "--prompt":
            opts["prompt"] = args[i + 1]
            i += 1
        elif args[i] == "--color":
            opts["color"] = args[i + 1]
            i += 1
        elif args[i] == "--dmenu":
            opts["dmenu"] = args[i + 1]
            i += 1
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
