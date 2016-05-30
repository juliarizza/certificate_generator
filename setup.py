from cx_Freeze import setup, Executable

setup(
    name = "Certifica!",
    version = "1.0.0",
    options = {"build_exe": {
        "packages":["PyPDF2","pdfkit","email"],
        "include_files": ["images/background.png",
                          "images/favicon.png",
                          "certificate_back.html",
                          "certificate_front.html",
                          "certificate_resp.html"
                         ],
        "include_msvcr": True,
    }},
    executables = [Executable("app.py",
                            base="Win32GUI",
			    icon="images/favicon.ico",
			    shortcutName="Certifica!",
			    shortcutDir="DesktopFolder",
                  )]
    )