from setuptools import setup

setup(
    name="menus",
    version="1.0.0",
    description="Handy menus",
    author="Naheel Azawy",
    author_email="naheelazawy@gmail.com",
    url="https://github.com/Naheel-Azawy/menus",
    packages=["menus"],
    install_requires=["sh", "PyGObject", "pydbus",
                      "dbus-python"],
    # yep, weird why 2 dbus requirments. check hud.py.
    # also, xprop, xdotool, and systemctl
    entry_points={
        "console_scripts": [
            "menus = menus.main:main"
        ]
    },
    scripts=["bin/menus-face"]
)
