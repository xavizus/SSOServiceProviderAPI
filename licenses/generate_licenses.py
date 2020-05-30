import subprocess
import platform

command = [
    "pip-licenses",
    "--ignore-packages",
    "asgiref",
    "pip-licenses",
    "pipdeptree",
    "pyasn1-modules",
    "pylint-flask",
    "astroid",
    "lazy-object-proxy",
    "six",
    "wrapt",
    "colorama",
    "isort",
    "mccabe",
    "toml",
    "pylint-plugin-utils",
    "pylint",
    "setuptools",
    "sqlparse",
    "--with-license-file",
    "--no-license-path",
    "--format=plain-vertical"
]
shellEncoding = 'utf-8'
if platform.system() == 'Windows':
    shellEncoding = 'iso-8859-1'

with open("licenses.txt", "w", encoding='utf-8') as licenseFile:
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        encoding=shellEncoding
    ).stdout
    print(result)
    licenseFile.write(result)
