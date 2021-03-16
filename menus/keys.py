import sh
import os
import sys
import re

argv = sys.argv
HOME = os.getenv("HOME")
sxhkdrc = f"{HOME}/.config/sxhkd/sxhkdrc"

class Binding:
    def __init__(self, t):
        if len(t) == 3:
            self.doc  = t[0]
            self.keys = t[1]
            self.cmd  = t[2]
        elif len(t) == 2:
            self.doc  = None
            self.keys = t[0]
            self.cmd  = t[1]

# because it used to be the other way around,
# I used to keep bindings in a seperate script that is used
# to generate the actual config file. might remove this later
# if not needed at all
def gen_sxhkdrc(src):
    if not os.path.exists(sxhkdrc):
        return
    with open(sxhkdrc, "w") as outfile:
        outfile.write("# DO NOT EDIT!\n")
        outfile.write(f"# Generated by %s at %s\n" % (__file__, sh.date().strip()))
        for b in src:
            b = Binding(b)
            if b.doc is not None:
                outfile.write("# %s\n" % b.doc)
            outfile.write("%s\n\t%s\n\n" % (b.keys, b.cmd))
    try:
        sh.pkill("-USR1", "-x", "sxhkd")
    except:
        pass

def parse_sxhkdrc():
    if not os.path.exists(sxhkdrc):
        return
    with open(sxhkdrc, "r") as f:
        text = f.read()
        # not the bet choice, but.. whatever...
        # replace later if you pass by here
        items = text.split("\n\n")
        for item in items:
            m = re.search("# (.+)\n(.+)\n\t(.+)", item)
            if m:
                yield (m[1], m[2], m[3])

def get_doc_from(src):
    for b in src:
        b = Binding(b)
        if b.doc is not None:
            yield ('%-40s: %s' % (b.keys, b.doc))

def run_from(src, keys):
    for b in src:
        b = Binding(b)
        if b.keys == keys:
            return os.system(b.cmd)
    return None

def get_doc():
    return get_doc_from(parse_sxhkdrc())

def run(keys):
    return run_from(parse_sxhkdrc(), keys)

def main(args):
    if len(args) > 0:
        if args[0] == "-d":
            for d in get_doc():
                print(d)
            return 0
        elif args[0] == "-r":
            run(args[1])
            return 0
    return 1
