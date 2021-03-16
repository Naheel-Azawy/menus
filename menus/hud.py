# bring back the only one thing I miss from unity,
# the Head-Up Display (HUD) menu
# appmenu stuff based on:
# - https://github.com/RafaelBocquet/i3-hud-menu
# - https://github.com/tetzank/qmenu_hud
#
# don't forget to add:
# eval "$(hud env)"
#
# start the daemon with `hud daemon` and run `hud` to show the menu
# load in python as:
# from menus.hud import hud_env, hud_daemon, hud_load

import dbus # to be removed later. check the todo below.

import sys
import os
import re
import sh
import pkg_resources
from pydbus import SessionBus
from menus.face import pipemenu

# 'export GTK_MODULES="$GTK_MODULES:appmenu-gtk-module"'
# some gtk programs go crazy with this sometimes.
# GIMP crashes sometimes and libreoffice only hides the bars but the menu
# items are not functional, when they appear.
hud_env = """
PLOTINUS=$(whereis -b libplotinus | cut -d " " -f 2)'
[ -f "$PLOTINUS" ] && export GTK_MODULES="$GTK_MODULES:$PLOTINUS"
export UBUNTU_MENUPROXY=1
"""

def hud_daemon():
    from gi.repository import GLib
    loop = GLib.MainLoop()

    class AppMenuService:
        """
        <node>
          <interface name="com.canonical.AppMenu.Registrar">
            <method name="RegisterWindow">
              <arg name="windowId" type="u" direction="in"/>
              <arg name="menuObjectPath" type="o" direction="in"/>
            </method>
            <method name="UnregisterWindow">
              <arg name="windowId" type="u" direction="in"/>
            </method>
            <method name="GetMenuForWindow">
              <arg name="windowId" type="u" direction="in"/>
              <arg name="service" type="s" direction="out"/>
              <arg name="menuObjectPath" type="o" direction="out"/>
            </method>
          </interface>
        </node>
        """
        def __init__(self):
            self.window_dict = {}

        def RegisterWindow(self, windowId, menuObjectPath, dbus_context):
            self.window_dict[windowId] = (dbus_context.sender, menuObjectPath)

        def UnregisterWindow(self, windowId):
            del self.window_dict[windowId]

        def GetMenuForWindow(self, windowId):
            if windowId in self.window_dict:
                sender, menuObjectPath = self.window_dict[windowId]
                return [sender, menuObjectPath]

        def Q(self):
            loop.quit()

    # start plotinus service
    os.system("gsettings set com.worldwidemann.plotinus:/com/worldwidemann/plotinus/default/ dbus-enabled true")
    os.system("pgrep plotinus >/dev/null || plotinus &")

    # start dbus main service
    bus = SessionBus()
    bus.publish("com.canonical.AppMenu.Registrar", AppMenuService())
    loop.run()

def xprop(window_id, notype):
    res = sh.xprop("-id", window_id, "-notype", notype).strip()
    try:
        return re.search('.+ = "(.+)"', res)[1]
    except:
        return None

def format_label_list(label_list):
    return "| " + " → ".join(label_list).replace("_", "")

def format_main_bar(main_bar=[]):
    # main_bar = set(main_bar)
    # like a set, but keeps order
    main_bar_tmp = {}
    for item in main_bar:
        main_bar_tmp[item] = 1
    main_bar = list(main_bar_tmp.keys())
    if len(main_bar) > 0:
        return " | ".join(main_bar)
    else:
        return None

class HUDInterface:
    def __init__(self, window_id): pass
    def usuable(self): pass
    def list(self): pass
    def run(self, item): pass

class PlotinusHUD(HUDInterface):
    def __init__(self, window_id):
        self.window_id = window_id
        self.gtk_path = xprop(window_id, "_GTK_WINDOW_OBJECT_PATH")
        self.bus = SessionBus()
        try:
            self.plotinus = self.bus.get("com.worldwidemann.plotinus")
        except:
            self.plotinus = None

    def usuable(self):
        return None not in [self.gtk_path, self.plotinus]

    def list(self):
        bus_name, command_paths = self.plotinus.GetCommands(self.gtk_path)
        commands = [self.bus.get(bus_name, command_path)
                    for command_path in command_paths]

        self.actions = {}
        for i, command in enumerate(commands):
            path = command.Path + [command.Label]
            path.pop(0)
            l = format_label_list(path)
            self.actions[l] = command

        return self.actions, None

    def run(self, item):
        if item in self.actions:
            self.actions[item].Execute()

# FIXME: inactive items are shown normally

class GTKHUD(HUDInterface):
    def __init__(self, window_id):
        self.window_id = window_id
        self.gtk_bus_name = xprop(window_id, "_GTK_UNIQUE_BUS_NAME")
        self.gtk_object_path = xprop(window_id, "_GTK_MENUBAR_OBJECT_PATH")

    def usuable(self):
        return None not in [self.gtk_bus_name, self.gtk_object_path]

    def list(self):
        bus = SessionBus()
        self.menubar = bus.get(self.gtk_bus_name, self.gtk_object_path)

        gtk_menubar_results = self.menubar.Start(
            [x for x in range(1024)])

        gtk_menubar_menus = {}
        for gtk_menubar_result in gtk_menubar_results:
            gtk_menubar_menus[(gtk_menubar_result[0],
                               gtk_menubar_result[1])] = gtk_menubar_result[2]

        main_bar = []
        self.actions = {}
        targets = {}

        def explore_menu(menu_id, label_list=[]):
            if menu_id not in gtk_menubar_menus:
                return
            for menu in gtk_menubar_menus[menu_id]:
                if "label" in menu:
                    menu_label = menu["label"]
                else:
                    menu_label = "?"

                new_label_list = label_list + [menu_label]
                formatted_label = format_label_list(new_label_list)

                if len(new_label_list) == 1 and menu_label != "?":
                    main_bar.append(new_label_list[0].replace("_", ""))

                if "accel" in menu and menu["accel"]:
                    formatted_label += f" ({menu['accel']})"

                if ":section" in menu:
                    menu_section = menu[":section"]
                    section_menu_id = (menu_section[0], menu_section[1])
                    explore_menu(section_menu_id, label_list)

                if ":submenu" in menu:
                    menu_submenu = menu[":submenu"]
                    submenu_menu_id = (menu_submenu[0], menu_submenu[1])
                    explore_menu(submenu_menu_id, new_label_list)

                if ":section" not in menu and \
                   ":submenu" not in menu and \
                   "action" in menu:
                    menu_action = menu["action"]
                    self.actions[formatted_label] = menu_action
                    if "target" in menu:
                        menu_target = menu["target"]
                        targets[formatted_label] = menu_target

        explore_menu((0, 0))
        return self.actions, format_main_bar(main_bar)

    def run(self, item):
        if item in self.actions:
            action = self.actions[item].replace("unity.", "")
            self.menubar.Activate(action, [], {})

class AppMenuHUD(HUDInterface):
    def __init__(self, window_id):
        self.window_id = window_id
        try:
            bus = SessionBus()
            registrar = bus.get("com.canonical.AppMenu.Registrar")
            dbusmenu_bus, dbusmenu_object_path = \
                registrar.GetMenuForWindow(int(window_id))

            # TODO: remove dbus-python
            session_bus = dbus.SessionBus()
            dbusmenu_object = session_bus.get_object(
                dbusmenu_bus, dbusmenu_object_path)
            self.menubar = dbus.Interface(
                dbusmenu_object, "com.canonical.dbusmenu")

            # this should do the job, but it doesn't.
            # no idea why not. pydbus is no longer apparently maintained
            # so I'm not gonna complain there.
            # self.menubar = bus.get(dbusmenu_bus, dbusmenu_object_path)
        except Exception as e:
            # raise e
            self.menubar = None

    def usuable(self):
        return self.menubar is not None

    def list(self):
        dbusmenu_items = self.menubar.GetLayout(0, -1, ["label"])

        main_bar = []
        self.actions = {}

        def explore_dbusmenu_item(item, label_list=[]):
            item_id = item[0]
            item_props = item[1]
            item_children = item[2]

            if 'label' in item_props:
                new_label_list = label_list + [item_props["label"]]
            else:
                new_label_list = label_list

            if len(new_label_list) == 1:
                main_bar.append(new_label_list[0].replace("_", ""))

            if len(item_children) == 0:
                if "label" in item_props:
                    self.actions[format_label_list(new_label_list)] = item_id
            else:
                for child in item_children:
                    explore_dbusmenu_item(child, new_label_list)

        explore_dbusmenu_item(dbusmenu_items[1])
        return self.actions, format_main_bar(main_bar)

    def run(self, item):
        if item in self.actions:
            action = self.actions[item]
            self.menubar.Event(action, "clicked", 0, 0)

class EmacsHUD(HUDInterface):
    def __init__(self, window_id):
        self.window_id = window_id
        self.win_class = xprop(window_id, "WM_CLASS")
        self.win_name = xprop(window_id, "WM_NAME")

    def usuable(self):
        return None not in [self.win_class, self.win_name] and \
            (self.win_class.startswith("emacs") or \
             self.win_name.startswith("emacs"))

    def list(self):
        lisp = """(string-join
          (let (l)
            (mapatoms
             #'(lambda (f) (and
                            (commandp f)
                            (setq l (cons (symbol-name f) l)))))
            (when (called-interactively-p 'any)
              (with-current-buffer (get-buffer-create "*Major Modes*")
                (clear-buffer-delete)
                (let ((standard-output (current-buffer)))
                  (display-completion-list l)
                  (display-buffer (current-buffer)))))
            l) " ")"""

        out = sh.emacsclient("-e", lisp).strip()
        # remove starting and ending quotes
        out = out[1:-1]

        self.actions = {}
        for cmd in out.split(" "):
            self.actions[format_label_list([cmd])] = cmd
        return self.actions, None

    def run(self, item):
        if item in self.actions:
            cmd = self.actions[item]
            os.system(f"emacsclient -e '({cmd})' &")

def hud_load():
    try:
        window_id = sh.xdotool("getactivewindow").strip()
    except:
        return None
    interfaces = [EmacsHUD, PlotinusHUD,
                  GTKHUD, AppMenuHUD]
    for interface in interfaces:
        i = interface(window_id)
        if not i.usuable():
            continue
        return i
    return None

def run_now():
    i = hud_load()
    if i:
        pipe = pipemenu("-i -l 20")
        items, main_bar = i.list()
        if main_bar:
            pipe.stdin.write(main_bar + "\n")
        for item in items:
            pipe.stdin.write(item + "\n")
        pipe.stdin.close()
        res = pipe.stdout.readline().strip()
        i.run(res)
        return True
    return False

def main(args):
    if len(args) > 0:
        if args[0] == "daemon":
            hud_daemon()
        elif args[0] == "env":
            print(hud_env)
    else:
        if not run_now():
            print("Could not find a menu interface")
            return 1
    return 0
