import os
import re
import glob
from tokenise import tokenise


class DependencyError(ValueError):
    pass


types = {"null": "None", "Integer": "int",
         "Float": "float", "String": "str", "Boolean": "bool"}


def resolve_dependencies(textLineArray,
                         i,
                         outputText,
                         currentIndentationLevel):

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
                            cIL = currentIndentationLevel
                            parsed = parse(tokenised,
                                           currentIndentationLevel=cIL)
                            outputText += parsed[0]
                            currentIndentationLevel = parsed[1]
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
                                cIL = currentIndentationLevel
                                parsed = parse(tokenised,
                                               currentIndentationLevel=cIL)
                                outputText += parsed[0]
                                currentIndentationLevel = parsed[1]
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

        return outputText, currentIndentationLevel


def parse_objects(textLineArray, outputText, currentIndentationLevel=0):
    for i in range(len(textLineArray)):
        if textLineArray[i] == "object":
            indentation = "    "*currentIndentationLevel
            outputText += f"{indentation}class {textLineArray[i+1]}"
        if textLineArray[i] == "{":
            outputText += ":"
            currentIndentationLevel += 1

    outputText += "\n"

    return outputText, currentIndentationLevel


def parse_procedures(textLineArray, outputText, currentIndentationLevel=0):
    parameters = {}
    returnTypes = textLineArray[0].split("|")
    for i in range(len(returnTypes)):
        returnTypes[i] = types[returnTypes[i]]
    name = textLineArray[2]
    for i in range(len(textLineArray)):
        if textLineArray[i] in types or "|" in textLineArray[i]:
            parameters[textLineArray[i+2]] = [types[type]
                                              for type in textLineArray[i].split("|")]

        indentation = "    "*currentIndentationLevel
        outputText += f"{indentation}def {name}("
        if len(parameters):
            for name in parameters.keys():
                if not parameters[name] == "['None']":
                    outputText += f"{name}: Union{parameters[name]}, "
            outputText = outputText[:-1]
        outputText += ")"
        outputText += f" -> Union{returnTypes}"

        if textLineArray[i] == "{":
            outputText += ":"
            currentIndentationLevel += 1

        outputText += "\n"

        print(outputText)

    return outputText, currentIndentationLevel


def parse(textLineArray, currentIndentationLevel=0):
    outputText = ""
    for i in range(len(textLineArray)):
        if textLineArray[i].startswith('#'):
            break

        if textLineArray[i] == "}":
            currentIndentationLevel -= 1
            continue

        if textLineArray[i] == "use":
            outputText, currentIndentationLevel = resolve_dependencies(
                textLineArray,
                i,
                outputText,
                currentIndentationLevel=currentIndentationLevel)
            break

        if textLineArray[i] == "object":
            outputText, currentIndentationLevel = parse_objects(
                textLineArray,
                outputText,
                currentIndentationLevel=currentIndentationLevel)

        if textLineArray[i] in types or "|" in textLineArray[i]:
            if textLineArray[i+1] == "procedure":
                outputText, currentIndentationLevel = parse_procedures(
                    textLineArray,
                    outputText,
                    currentIndentationLevel=currentIndentationLevel)
            # else:
            #     outputText = parse_variables(
            #         textLineArray,
            #         outputText,
            #         currentIndentationLevel=currentIndentationLevel)

    return outputText, currentIndentationLevel


parse(["use", "local", "example", ":", "Object"])[0]
