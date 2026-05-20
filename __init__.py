import os
from lark import Lark, Transformer

import os
import sys

# Магия PyInstaller: определяем, запущена ли программа как скрипт или внутри .exe
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(__file__)

grammar_path = os.path.join(BASE_DIR, "grammar", "tinylang.lark")

with open(grammar_path, "r", encoding="utf-8") as f:
    grammar = f.read()

parser = Lark(grammar, parser="lalr")

class TinyLangToPythonCompiler(Transformer):
    def block(self, stmts):
        # Теперь просто собираем строки, ничего лишнего сюда не подмешиваем
        return "\n".join(stmts)

    # Функции и вызовы
    def func_def(self, args):
        name = args[0]
        params = args[1] if args[1] else ""
        body = args[2]
        # Делаем отступы для тела функции в Python
        indented_body = "\n".join(f"    {line}" for line in body.split("\n"))
        return f"def {name}({params}):\n{indented_body}"

    def param_list(self, args): return ", ".join(args)
    def return_stmt(self, args): return f"return {args[0]}"
    
    def func_call(self, args):
        name = args[0]
        # Перенаправляем вызовы на рантайм-функции
        if name == "input": name = "input_tl"
        if name == "close": name = "closeFile"
        params = args[1] if len(args) > 1 and args[1] else ""
        return f"{name}({params})"
        
    def arg_list(self, args): return ", ".join(args)

    # Присваивания и новые операторы (+=, -=, *=, /=, ++, --)
    def var_assign_op(self, args): return f"{args[0]} = {args[1]}"
    def var_add_assign(self, args): return f"{args[0]} += {args[1]}"
    def var_sub_assign(self, args): return f"{args[0]} -= {args[1]}"
    def var_mul_assign(self, args): return f"{args[0]} *= {args[1]}"
    def var_div_assign(self, args): return f"{args[0]} /= {args[1]}"
    def var_inc(self, args): return f"{args[0]} += 1"
    def var_dec(self, args): return f"{args[0]} -= 1"
    
    def var_call(self, args): return str(args[0])

    def STRING(self, token):
        # token — это объект Token из Lark. token.value — сама строка.
        raw_val = token.value
        
        # Срезаем кавычки по краям ("текст" -> текст или 'текст' -> текст)
        content = raw_val[1:-1]
        
        # Оборачиваем обратно в двойные кавычки для итогового Python-кода
        # (чтобы внутри Python всё склеилось стандартизировано)
        return f'"{content}"'

    # Директива импорта use
    def use_stmt(self, args):
        file_path = str(args[0]).strip('"')
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                sub_code = f.read()
            return f"# --- USE: {file_path} ---\n{compile_to_python(sub_code)}\n"
        except Exception as e:
            return f"print('Error importing {file_path}: {e}')"

    # Управляющие конструкции
    def if_stmt(self, args):
        cond = args[0]
        then_body = "\n".join(f"    {line}" for line in args[1].split("\n"))
        res = f"if {cond}:\n{then_body}"
        if len(args) > 2 and args[2]:
            else_body = "\n".join(f"    {line}" for line in args[2].split("\n"))
            res += f"\nelse:\n{else_body}"
        return res

    def while_stmt(self, args):
        cond = args[0]
        body = "\n".join(f"    {line}" for line in args[1].split("\n"))
        return f"while {cond}:\n{body}"

    def for_stmt(self, args):
        init = args[0]
        cond = args[1]
        step = args[2]
        body = args[3]
        # В Python нет for в стиле Си, поэтому разворачиваем его в структуру с while
        loop_content = f"{body}\n{step}"
        indented_body = "\n".join(f"    {line}" for line in loop_content.split("\n"))
        return f"{init}\nwhile {cond}:\n{indented_body}"

    def expr_stmt(self, args): return str(args[0])

    # Математика и операции
    def add(self, args): return f"({args[0]} + {args[1]})"
    def sub(self, args): return f"({args[0]} - {args[1]})"
    def mul(self, args): return f"({args[0]} * {args[1]})"
    def div(self, args): return f"({args[0]} // {args[1]})" # div теперь целочисленный!
    def mod(self, args): return f"({args[0]} % {args[1]})"  # mod теперь остаток!

    # Сравнения
    def eq(self, args): return f"{args[0]} == {args[1]}"
    def ne(self, args): return f"{args[0]} != {args[1]}"
    def ge(self, args): return f"{args[0]} >= {args[1]}"
    def le(self, args): return f"{args[0]} <= {args[1]}"
    def gt(self, args): return f"{args[0]} > {args[1]}"
    def lt(self, args): return f"{args[0]} < {args[1]}"

    # Атомы
    def num(self, args): return str(args[0])
    def str(self, args): return str(args[0])
    def true(self, args): return "True"
    def false(self, args): return "False"
    def null(self, args): return "None"
    def array(self, args): return f"[{', '.join(args)}]"

# Декомпилятор (собирает дерево обратно в TinyLang)
class ASTToTinyLangDecompiler(Transformer):
    def block(self, stmts): return "\n".join(stmts)
    def func_def(self, args): return f"function {args[0]}({args[1]}): {{\n{args[2]}\n}}"
    def param_list(self, args): return ", ".join(args)
    def return_stmt(self, args): return f"return {args[0]}"
    def var_assign_op(self, args): return f"{args[0]} = {args[1]}"
    def var_add_assign(self, args): return f"{args[0]} += {args[1]}"
    def var_sub_assign(self, args): return f"{args[0]} -= {args[1]}"
    def var_mul_assign(self, args): return f"{args[0]} *= {args[1]}"
    def var_div_assign(self, args): return f"{args[0]} /= {args[1]}"
    def var_inc(self, args): return f"{args[0]}++"
    def var_dec(self, args): return f"{args[0]}--"
    def var_call(self, args): return str(args[0])
    def use_stmt(self, args): return f"use {args[0]}"
    def if_stmt(self, args):
        res = f"if ({args[0]}): {{\n{args[1]}\n}}"
        if len(args) > 2 and args[2]: res += f" else: {{\n{args[2]}\n}}"
        return res
    def while_stmt(self, args): return f"while ({args[0]}): {{\n{args[1]}\n}}"
    def for_stmt(self, args): return f"for ({args[0]}; {args[1]}; {args[2]}): {{\n{args[3]}\n}}"
    def expr_stmt(self, args): return str(args[0])
    def add(self, args): return f"{args[0]} + {args[1]}"
    def sub(self, args): return f"{args[0]} - {args[1]}"
    def mul(self, args): return f"{args[0]} * {args[1]}"
    def div(self, args): return f"{args[0]} div {args[1]}"
    def mod(self, args): return f"{args[0]} mod {args[1]}"
    def num(self, args): return str(args[0])
    def str(self, args): return str(args[0])
    def true(self, args): return "true"
    def false(self, args): return "false"
    def null(self, args): return "null"
    def array(self, args): return f"[{', '.join(args)}]"
    def func_call(self, args): return f"{args[0]}(\n{args[1]} if len(args) > 1 else ''\n)"

def compile_to_python(code):
    tree = parser.parse(code)
    compiled_code = TinyLangToPythonCompiler().transform(tree)
    
    # Гарантированный рантайм, который приклеится к ЛЮБОМУ коду
    runtime = (
        "import sys\n"
        "def input_tl(*args):\n"
        "    res = input(*args)\n"
        "    return int(res) if res.isdigit() else res\n"
        "def openWrite(fp): return open(fp, 'w', encoding='utf-8')\n"
        "def openRead(fp): return open(fp, 'r', encoding='utf-8')\n"
        "def openAppend(fp): return open(fp, 'a', encoding='utf-8')\n"
        "def getText(fo): return fo.read()\n"
        "def writeText(fo, txt): fo.write(txt)\n"
        "def closeFile(fo): fo.close()\n"
    )
    
    return runtime + compiled_code

def decompile_to_tinylang(tree):
    return ASTToTinyLangDecompiler().transform(tree)