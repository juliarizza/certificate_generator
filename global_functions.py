# -*- coding: utf-8 -*-
import os
import sys
import re
from shutil import copyfile

from PyQt4 import QtGui

# If the platform is Windows, we have to create the app folder in
# somewhere else than the place where it is installed
if "win" in sys.platform:
    # Creating app folders and copying files to them
    app_dir = "{0}\\Certifica\\".format(os.environ['APPDATA'])
    if getattr(sys, "frozen", False):
        root_dir = os.path.dirname(sys.path[0])
    elif __file__:
        root_dir = os.path.dirname(__file__)
    templates_dir = os.path.join(app_dir, "templates")
    images_dir = os.path.join(app_dir, "images")
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)
        os.makedirs(images_dir)
        os.makedirs(os.path.join(app_dir, "signatures"))
        os.makedirs(templates_dir)

    # Verifies if it's a normal execution or installed app
    try:
        copyfile(os.path.join(root_dir, "background.png"),
                 os.path.join(images_dir, "background.png"))
        copyfile(os.path.join(root_dir, "favicon.ico"),
                 os.path.join(images_dir, "favicon.ico"))
    except IOError:
        copyfile(os.path.join(root_dir, "images", "background.png"),
                 os.path.join(images_dir, "background.png"))
        copyfile(os.path.join(root_dir, "images", "favicon.ico"),
                 os.path.join(images_dir, "favicon.ico"))

    copyfile(os.path.join(root_dir, "certificate_back.html"),
             os.path.join(templates_dir, "certificate_back.html"))
    copyfile(os.path.join(root_dir, "certificate_resp.html"),
             os.path.join(templates_dir, "certificate_resp.html"))
    copyfile(os.path.join(root_dir, "certificate_front.html"),
             os.path.join(templates_dir, "certificate_front.html"))
else:
    app_dir = os.path.dirname(os.path.abspath(__file__))+"/"
    root_dir = app_dir
    templates_dir = app_dir
    images_dir = os.path.join(app_dir, "images")

# Font for titles
titleFont = QtGui.QFont()
titleFont.setBold(True)
titleFont.setPixelSize(20)


# CODE FROM: http://wiki.python.org.br/VerificadorDeCpfCnpjSimples
def validar_cpf(cpf):
    """
    Valida CPFs, retornando apenas a string de números válida.

    # CPFs errados
    >>> validar_cpf('abcdefghijk')
    False
    >>> validar_cpf('123')
    False
    >>> validar_cpf('')
    False
    >>> validar_cpf(None)
    False
    >>> validar_cpf('12345678900')
    False

    # CPFs corretos
    >>> validar_cpf('95524361503')
    '95524361503'
    >>> validar_cpf('955.243.615-03')
    '95524361503'
    >>> validar_cpf('  955 243 615 03  ')
    '95524361503'
    """
    cpf = ''.join(re.findall('\d', str(cpf)))

    if (not cpf) or (len(cpf) < 11):
        return False

    # Pega apenas os 9 primeiros dígitos do CPF e gera os 2 dígitos que faltam
    inteiros = map(int, cpf)
    novo = inteiros[:9]

    while len(novo) < 11:
        r = sum([(len(novo)+1-i)*v for i,v in enumerate(novo)]) % 11

        if r > 1:
            f = 11 - r
        else:
            f = 0
        novo.append(f)

    # Se o número gerado coincidir com o número original, é válido
    if novo == inteiros:
        return cpf
    return False


def validar_cnpj(cnpj):
    """
    Valida CNPJs, retornando apenas a string de números válida.

    # CNPJs errados
    >>> validar_cnpj('abcdefghijklmn')
    False
    >>> validar_cnpj('123')
    False
    >>> validar_cnpj('')
    False
    >>> validar_cnpj(None)
    False
    >>> validar_cnpj('12345678901234')
    False
    >>> validar_cnpj('11222333000100')
    False

    # CNPJs corretos
    >>> validar_cnpj('11222333000181')
    '11222333000181'
    >>> validar_cnpj('11.222.333/0001-81')
    '11222333000181'
    >>> validar_cnpj('  11 222 333 0001 81  ')
    '11222333000181'
    """
    cnpj = ''.join(re.findall('\d', str(cnpj)))

    if (not cnpj) or (len(cnpj) < 14):
        return False

    # Pega apenas os 12 primeiros dígitos do CNPJ e gera os 2 dígitos que faltam
    inteiros = map(int, cnpj)
    novo = inteiros[:12]

    prod = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    while len(novo) < 14:
        r = sum([x*y for (x, y) in zip(novo, prod)]) % 11
        if r > 1:
            f = 11 - r
        else:
            f = 0
        novo.append(f)
        prod.insert(0, 6)

    # Se o número gerado coincidir com o número original, é válido
    if novo == inteiros:
        return cnpj
    return False
