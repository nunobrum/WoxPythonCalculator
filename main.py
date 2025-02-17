# -*- coding: utf-8 -*-
from math import *
import re
import os
import traceback

try:
    import pyperclip
except:
    pyperclip = None

try:
    import numpy as np
except:
    pass

try:
    from scipy.special import *
    c = binom
except:
    pass

from builtins import *  # Required for division scipy, also allows for pow to be used with modulus
import math_parser

sqr = lambda f: f ** 2
sqrt = sqr

x = None

if pyperclip is not None:
    try:
        x = float(pyperclip.paste())
    except ValueError:
        pass

xFilePath = os.environ['TMP'] + os.sep + "wox_pycalc_x.txt"

if x is None:
    if os.path.exists(xFilePath):
        try:
            with open(xFilePath, "r") as xFile:
                x = float(xFile.read())
        except:
            x = 0


def json_wox(title, subtitle, icon, action=None, action_params=None, action_keep=None):
    json = {
        'Title': title,
        'SubTitle': subtitle,
        'IcoPath': icon
    }
    if action and action_params and action_keep:
        json.update({
            'JsonRPCAction': {
                'method': action,
                'parameters': action_params,
                'dontHideAfterAction': action_keep
            }
        })
    return json


def copy_to_clipboard(text):
    if pyperclip is not None:
        pyperclip.copy(text)
    else:
        # Workaround
        cmd = 'echo ' + text.strip() + '| clip'
        os.system(cmd)


def write_to_x(result):
    x = result
    try:
        with open(xFilePath, "w") as xFile:
            xFile.write(result)
    except:
        pass


def to_eng(value):
    e = floor(log(abs(value), 1000))
    if -5 <= e < 0:
        suffix = "fpnum"[e]
    elif e == 0:
        suffix = ''
    elif e == 1:
        suffix = "k"
    elif e == 2:
        suffix = 'Meg'
    elif e == 3:
        suffix = 'Giga'
    else:
        return '{:E}'.format(value)
    return '{:g}{:}'.format(value * 1000**-e, suffix)


def format_result(result):
    if hasattr(result, '__call__'):
        # show docstring for other similar methods
        raise NameError
    if isinstance(result, str):
        return result
    if isinstance(result, int) or isinstance(result, float):
        if int(result) == float(result):
            return '{:,}'.format(int(result)).replace(',', ' ')
        else:
            return '{:,}'.format(round(float(result), 5)).replace(',', ' ')
    elif hasattr(result, '__iter__'):
        try:
            return '[' + ', '.join(list(map(format_result, list(result)))) + ']'
        except TypeError:
            # check if ndarray
            result = result.flatten()
            if len(result) > 1:
                return '[' + ', '.join(list(map(format_result, result.flatten()))) + ']'
            else:
                return format_result(np.asscalar(result))
    elif isinstance(result, bool):
        return 'True' if result else 'False'
    else:
        return str(result)

  
def handle_factorials(query):
    # Replace simple factorial
    query = re.sub(r'(\b\d+\.?\d*([eE][-+]?\d+)?\b)!',
                   lambda match: f'factorial({match.group(1)})', query)

    i = 2
    while i < len(query):
        if query[i] == "!" and query[i-1] == ")":
            j = i-1
            bracket_count = 1
            while bracket_count != 0 and j > 0:
                j -= 1
                if query[j] == ")":
                    bracket_count += 1
                elif query[j] == "(":
                    bracket_count -= 1
            query = query[:j] + f'factorial({query[j+1:i-1]})' +\
                    (query[i+1:] if i+1 < len(query) else "")
            i += 8  # 8 is the difference between factorial(...) and (...)!
        i += 1
    return query

def handle_pow_xor(query):
    return query.replace("^", "**").replace("xor", "^")

def handle_implied_multiplication(query):
    return re.sub(r'((?:\.\d+|\b\d+\.\d*|\b\d+)(?:[eE][-+]?\d+)?)\s*(x|pi)\b',
                  r'(\1*\2)', query)

def handle_engineering_notation(query):
    rgx = re.compile(r'\d([fpnumkMG])')
    E = {
        'f': 'e-15',
        'p': 'e-12',
        'n': 'e-9',
        'u': 'e-6',
        'm': 'e-3',
        'k': 'e+3',
        'M': 'e+6',
        'G': 'e+9',
    }
    aux = ''
    start = 0
    for m in rgx.finditer(query):
        try:  # This is needed to avoid that a number is after a unit qualifier
            skip = query[m.end(1)] in '0123456789'
        except IndexError:
            skip = False
        if not skip:
            aux += query[start:m.start(1)] + E[m.group(1)]
            start = m.end(1)
    aux += query[start:]
    return aux

    
def calculate(query):
    results = []
    try:
        result = math_parser.evaluate(query, {'x': x})
    except Exception as err:
        err_text = traceback.format_exc()
        results.append(json_wox(f"Error: {type(err)}",
                                "err_text",
                                'icons/app.png',
                                'change_query',
                                [err_text],
                                True))
    else:
        results.append(json_wox(to_eng(result),
                                '{} = {}'.format(query, to_eng(result)),
                                'icons/app.png',
                                'store_result',
                                [query, str(result)],
                                True))
    return results


from wox import Wox, WoxAPI


class Calculator(Wox):
    def query(self, query):
        return calculate(query)

    def context_menu(self, data):
        return ["Teste", 555]

    def change_query(self, query):
        # change query and copy to clipboard after pressing enter
        WoxAPI.change_query(query)
        write_to_x(query)
        copy_to_clipboard(query)

    def change_query_method(self, query):
        WoxAPI.change_query(query + '(')

    def store_result(self, query, result):
        WoxAPI.change_query(query)
        write_to_x(result)
        copy_to_clipboard(result)


if __name__ == '__main__':
    Calculator()
