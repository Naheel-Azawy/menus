import sys
import sh
from shutil import which
from menus.face import confirm, dictmenu

def items():
    items = {
        "Suspend":
        lambda: sh.systemctl("suspend"),
        "Shutdown":
        lambda: confirm("Shutdown?",
                        sh.systemctl.bake("poweroff")),
        "Reboot":
        lambda: confirm("Reboot?",
                        sh.systemctl.bake("reboot")),
        "Logout":
        lambda: confirm("Logout?",
                        sh.wm_msg.bake("end")),
        "Lock":
        lambda: sh.lockscreen(),
        "Hibernate":
        lambda: confirm("Hibernate?",
                        sh.systemctl.bake("hibernate"))
    }

    if which("lockscreen") is None:
        del items["Lock"]

    #if which("wmctl") is None: # TODO
    #    del items["Logout"]
    return items

def main(args):
    i = items()
    if len(args) > 1:
        sel = args[1].title()
        if sel in i:
            i[sel]()
    else:
        dictmenu(i, opts={
            "prompt": "Power options",
            "dmenu": "-i"
        })
    return 0
