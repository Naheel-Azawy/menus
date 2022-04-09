import sys
import sh
from shutil import which
from menus.face import confirm, dictmenu, n

dmenu_loc = "-L top-right -y 30"

def items():
    if n:
        conf_opts = {"dmenu": dmenu_loc}
    else:
        conf_opts = {}
    items = {
        "Suspend":
        lambda: sh.systemctl("suspend"),
        "Shutdown":
        lambda: confirm("Shutdown?",
                        sh.systemctl.bake("poweroff"),
                        opts=conf_opts),
        "Reboot":
        lambda: confirm("Reboot?",
                        sh.systemctl.bake("reboot"),
                        opts=conf_opts),
        "Logout":
        lambda: confirm("Logout?",
                        sh.wm_msg.bake("end"),
                        opts=conf_opts),
        "Lock":
        lambda: sh.lockscreen(),
        "Hibernate":
        lambda: confirm("Hibernate?",
                        sh.systemctl.bake("hibernate"),
                        opts=conf_opts)
    }
    if which("lockscreen") is None:
        del items["Lock"]
    return items

def main(args):
    i = items()
    if len(args) > 1:
        sel = args[1].title()
        if sel in i:
            i[sel]()
    else:
        if n:
            conf_opts = dmenu_loc + "-i -l 3 -c 2 "
        else:
            conf_opts = "-i"
        dictmenu(i, opts={
            "dmenu": conf_opts
        })
    return 0
