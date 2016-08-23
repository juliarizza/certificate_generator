import sys
from cx_Freeze import setup, Executable

build_exe_options = {"packages": ["PyPDF2", "pdfkit", "email"],
                     "excludes": ["tkinter"],
                     "include_files": ["images/background.png",
                                       "images/favicon.png",
                                       "images/favicon.ico",
                                       "certificate_back.html",
                                       "certificate_front.html",
                                       "certificate_resp.html"
                                      ],
#                     "include_msvcr": True,
                    }

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "Certifica!",
        version = "1.0.0",
        options = {"build_exe": build_exe_options},
        executables = [Executable("app.py",
                                  base=base,
			                      icon="images/favicon.ico",
                                  shortcutName="Certifica!",
			                      shortcutDir="DesktopFolder",)])
