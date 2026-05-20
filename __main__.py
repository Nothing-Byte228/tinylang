import sys, __init__ as tl, subprocess

args = sys.argv

match args:
    case [_, "--help"]:
        print("=========================================")
        print("          TinyLang 1.0.0 Atom            ")
        print("=========================================")
        print("\nUsage:")
        print("  tinylang <file-path>     Run .tl file (or just double-click it)")
        print("  tinylang --code <code>   Execute raw code from a console")
        print("  tinylang --help          Show this help message")
        print("\nDeveloper: KTO-TO, 2026 - present")
        print("=========================================\n")
    case [_, target]:
        with open(target, "r", encoding="utf-8") as f:
            data = f.read()
            f.close()
        try:
            python_code = tl.compile_to_python(data)
            
            # Определяем, как запускать сгенерированный код
            # Если мы внутри скомпилированного .exe, sys.executable указывает на exe. 
            # В таком случае берем системный "python". Иначе — текущий sys.executable.
            python_interpreter = "python" if getattr(sys, 'frozen', False) else sys.executable

            # И теперь используем его в subprocess:
            subprocess.run([python_interpreter, "-c", python_code])
        except Exception as e:
            print("An error occurred while running this code:", e)
    case [_, "--code", code]: 
        data = code
        try:
            python_code = tl.compile_to_python(data)
            
            # Определяем, как запускать сгенерированный код
            # Если мы внутри скомпилированного .exe, sys.executable указывает на exe. 
            # В таком случае берем системный "python". Иначе — текущий sys.executable.
            python_interpreter = "python" if getattr(sys, 'frozen', False) else sys.executable

            # И теперь используем его в subprocess:
            subprocess.run([python_interpreter, "-c", python_code])
        except Exception as e:
            print("An error occurred while running this code:", e)
    case [_]:
        print("Write `tinylang --help` for help.")