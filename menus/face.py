from subprocess import Popen, PIPE, STDOUT
import sys

def dmenu_cmd(opts=""):
    cmd = "dmenu"
    if opts:
        cmd += " " + opts
    return cmd

# TODO: add more interfaces
# def dmenu_cmd(opts=""):
#     cmd = "rofi -width 50 -dmenu"
#     return cmd

# example:
# pipe = pipemenu("-i -r")
# pipe.stdin.write("hi\n")
# pipe.stdin.write("hello\n")
# pipe.stdin.close()
# for line in iter(pipe.stdout.readline, ""):
#     print(line, end="")
def pipemenu(opts=""):
    cmd = dmenu_cmd(opts)
    pipe = Popen(cmd, shell=True,
                 universal_newlines=True,
                 stdin=PIPE, stdout=PIPE)
    return pipe

# example:
# dictmenu({"yep": lambda: print("yay"), "nope": None})
def dictmenu(d, opts=""):
    pipe = pipemenu(opts)
    for i in d:
        pipe.stdin.write(i + "\n")
    pipe.stdin.close()
    res = pipe.stdout.readline().strip()
    if res in d and callable(d[res]):
        d[res]()

# example:
# confirm("Dude sure?!", lambda: print("yep"))
def confirm(msg, callback):
    dictmenu(
        {"Yes": callback, "No": None},
        f"-i -p '{msg}' " +
        "-sb red -sf black -nb black -nf red")

def main(args):
    opts = []
    for arg in args:
        opts.append(f"'{arg}'")
    opts = " ".join(opts)
    pipe = pipemenu(opts)
    for line in sys.stdin:
        pipe.stdin.write(line)
    pipe.stdin.close()
    for line in iter(pipe.stdout.readline, ""):
        print(line, end="")
