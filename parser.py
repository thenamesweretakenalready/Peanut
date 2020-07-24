import os
import re
import glob
from tokenise import tokenise


class DependencyError(ValueError):
    pass


def resolve_dependencies(textLineArray, i, outputText, currentIndentationLevel):
    if textLineArray[i+1] == "module":
        if not os.path.isfile(f"builtins/{textLineArray[i+2]}.py"):
            raise DependencyError(
                f"{textLineArray[i+2]} is not a builtin.")

        if len(textLineArray) == 3:
            with open(f"builtins/{textLineArray[i+2]}.py") as f:
                data = f.read()
                outputText += data
        else:
            with open(f"builtins/{textLineArray[i+2]}.py") as f:
                name = textLineArray[i+4].upper()
                data = f.readline()
                begin = False
                while data:
                    begin = bool(
                        re.search(
                            f"# --- {name} BEGIN", data)
                    )
                    outputText += bool(begin)*data
                    if not re.search(f"# --- {name} END", data):
                        data = f.readline()
                    else:
                        break
    elif textLineArray[i+1] == "local":
        found = False
        path = os.path.dirname(os.path.realpath(__file__))
        for filename in glob.iglob(f'{path}/*', recursive=True):
            found = filename == f"{path}/{textLineArray[i+2]}.pnut"
            if found:
                with open(f"{filename}", "r") as f:
                    if len(textLineArray) == 3:
                        line = f.readline()
                        while line:
                            tokenised = tokenise.tokenise(line)
                            outputText += parse(tokenised,
                                                currentIndentationLevel=currentIndentationLevel)
                            print(outputText)
                            line = f.readline()
                        break
                    else:
                        with open(f"{filename}") as f:
                            name = textLineArray[i+4].upper()
                            data = f.readline()
                            begin = False
                            while data:
                                begin = bool(int(bool(
                                    re.search(
                                        f"# --- {name} BEGIN", data)
                                )) + int(begin))
                                tokenised = tokenise(bool(begin)*data)
                                outputText += parse(tokenised,
                                                    currentIndentationLevel=currentIndentationLevel)
                                if not re.search(
                                        f"# --- {name} END", data):
                                    data = f.readline()
                                else:
                                    break
                        break
        if not found:
            raise DependencyError(f"""
            Could not find {textLineArray[i+2]}.pnut in the local path
            """)

        return outputText


def parse_objects(textLineArray, outputText):
    return outputText


def parse(textLineArray, currentIndentationLevel=0):
    outputText = ""
    for i in range(len(textLineArray)):
        if textLineArray[i].startswith('#'):
            break

        if textLineArray[i] == "use":
            outputText = resolve_dependencies(textLineArray, i, outputText)
            break

        if textLineArray[i] == "object":
            outputText = parse_objects(textLineArray, outputText)
    return outputText


print(parse(["use", "local", "example", ":", "Object"]))
