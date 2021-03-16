import sys
import sh
from shutil import which
from menus.face import confirm, dictmenu

def items():
    items = {
        "Suspend":
        lambda: sh.systemctl("suspend"),
        "Shutdown":
        lambda: confirm("Shutdown? ",
                        sh.systemctl.bake("poweroff")),
        "Reboot":
        lambda: confirm("Reboot?",
                        sh.systemctl.bake("reboot")),
        "Logout":
        lambda: confirm("Logout?",
                        sh.wmctl.bake("kill")),
        "Lock":
        lambda: sh.lockscreen(),
        "Hibernate":
        lambda: confirm("Hibernate?",
                        sh.systemctl.bake("hibernate"))
    }

    if which("lockscreen") is None:
        del items["Lock"]

    if which("wmctl") is None:
        del items["Logout"]
    return items

def main(args):
    items = items()
    if len(args) > 0:
        sel = args[0].title()
        if sel in items:
            items[sel]()
    else:
        dictmenu(items, "-p 'Power options'")
    return 0
