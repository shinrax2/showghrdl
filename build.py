#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import PyInstaller.__main__

args = [
    "--name=showghrdl",
    "--clean",
    "--onefile",
    "showghrdl.py"
]
PyInstaller.__main__.run(args)
