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
                         imports=[],
                         currentIndentationLevel=0):
    if textLineArray[i+1] == "module":
        if textLineArray[i+2] not in imports:
            print(f"Resolving dependency {textLineArray[i+2]}...")
        if not os.path.isfile(f"builtins/{textLineArray[i+2]}.py"):
            raise DependencyError(
                f"{textLineArray[i+2]} is not a builtin.")

        if len(textLineArray) == 3:
            with open(f"builtins/{textLineArray[i+2]}.py") as f:
                data = f.read()
                outputText += data
                imports.append(textLineArray[i+2])
        else:
            with open(f"builtins/{textLineArray[i+2]}.py") as f:
                imports.append(textLineArray[i+4])
                name = textLineArray[i+4].upper()
                data = f.readline()
                begin = False
                while data:
                    begin = bool(int(bool(
                        re.match(
                            f"# --- {name} BEGIN", data)
                    )) + int(begin))
                    outputText += bool(begin)*data
                    if not re.match(f"# --- {name} END", data):
                        data = f.readline()
                    else:
                        break
    elif textLineArray[i+1] == "local":
        if textLineArray[i+2] not in imports:
            print(f"Resolving dependency {textLineArray[i+2]}...")
        found = False
        path = os.path.dirname(os.path.realpath(__file__))
        for filename in glob.iglob(f'{path}/*', recursive=True):
            found = filename == f"{path}/{textLineArray[i+2]}.pnut"
            if found:
                with open(f"{filename}", "r") as f:
                    if len(textLineArray) == 3:
                        imports.append(textLineArray[i+2])
                        line = f.readline()
                        while line:
                            tokenised = tokenise(line)
                            cIL = currentIndentationLevel
                            parsed = parse(tokenised,
                                           currentIndentationLevel=cIL)
                            outputText += parsed[0]
                            currentIndentationLevel = parsed[1]
                            line = f.readline()
                        break
                    else:
                        with open(f"{filename}") as f:
                            imports.append(textLineArray[i+4])
                            name = textLineArray[i+4].upper()
                            data = f.readline()
                            begin = False
                            while data:
                                if len(data.replace('\n', '')):
                                    if data.split()[0] == "use":
                                        cIL = currentIndentationLevel
                                        outputText, _ = resolve_dependencies(
                                            tokenise(data),
                                            0,
                                            outputText,
                                            currentIndentationLevel=cIL
                                        )
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

    return outputText, currentIndentationLevel, imports


def parse_objects(textLineArray, outputText, objects=[], currentIndentationLevel=0):
    for i in range(len(textLineArray)):
        if textLineArray[i] == "object":
            indentation = "    "*currentIndentationLevel
            outputText += f"{indentation}class {textLineArray[i+1]}"
            objects.append(textLineArray[i+1])
        if textLineArray[i] == "{":
            outputText += ":"
            currentIndentationLevel += 1

    outputText += "\n"

    return outputText, currentIndentationLevel, objects


def parse_procedures(textLineArray, outputText, procedures=[], currentIndentationLevel=0):
    parameters = {}
    returnTypes = textLineArray[0].split("|")
    for i in range(len(returnTypes)):
        returnTypes[i] = types[returnTypes[i]]
    name = textLineArray[2]
    procedures.append(name)
    try:
        for i in range(len(textLineArray[4:])):
            if textLineArray[4:][i] not in [",", "{", "}", "(", ")"]:
                if "|" in textLineArray[4:][i]:
                    parameterName = textLineArray[4:][i+1]
                else:
                    parameterName = textLineArray[4:][i]
                if parameterName == ")":
                    parameterName = textLineArray[4:][i-1]
                parameters[parameterName] = [types[type] for type in
                                             textLineArray[4:][
                                             textLineArray[4:].
                                             index(parameterName)-1].split("|")]
    except IndexError:
        pass

    indentation = "    "*currentIndentationLevel
    outputText += f"{indentation}def {name}("
    if len(parameters):
        for paramname in parameters.keys():
            if not parameters[paramname] == "[None]":
                outputText += f"""{paramname}:Union[{', '.join(parameters[
                                                    paramname
                                                    ]).replace("'", '')}],"""
        outputText = outputText[:-1]
    outputText += ")"
    outputText += f""" -> Union[{', '.join(returnTypes).replace("'", '')}]"""

    for i in range(len(textLineArray)):
        if textLineArray[i] == "{":
            outputText += ":"
            currentIndentationLevel += 1

    outputText += "\n"

    return outputText, currentIndentationLevel, procedures


def parse_variables(textLineArray, outputText, variables=[], currentIndentationLevel=0):
    type = None
    indentation = "    "*currentIndentationLevel
    if textLineArray[0].split('|')[0] in types:
        type = textLineArray[0]
        name = textLineArray[1]
        value = textLineArray[3:]
    elif textLineArray[1] != "=":
        name = textLineArray[1]
        value = textLineArray[3:]
    else:
        name = textLineArray[0]
        value = textLineArray[2:]

    variables.append(name)
    if type:
        outputText += f"""{indentation}{name} = {types[type.split('|')[0]]
                                               }({parse(value)[0]})"""
        outputText += "\n"
        return outputText, variables
    outputText += f"{indentation}{name} = {parse(value)[0]}"
    outputText += "\n"
    return outputText, variables


def parse_returns(textLineArray, outputText, currentIndentationLevel=0):
    indentation = "    "*currentIndentationLevel
    if textLineArray[0] == "return":
        outputText += f"{indentation}return {' '.join(textLineArray[1:])}"
        outputText += "\n"
    return outputText


def parse_conditionals(textLineArray, outputText, currentIndentationLevel=0):
    indentation = "    "*currentIndentationLevel
    conditions = textLineArray[2:-2]

    if len(conditions):
        if conditions[1] == "===":
            outputText += f"{indentation}if type({conditions[0]}) == type({conditions[2]})"
        else:
            outputText += f"{indentation}if {''.join(conditions)}"
    else:
        outputText += f"{indentation}else"

    if textLineArray[-1] == "{":
        outputText += ":"
        currentIndentationLevel += 1
    outputText += "\n"

    return outputText, currentIndentationLevel


def parse(textLineArray, imports=[], objects=[], procedures=[], variables=[], currentIndentationLevel=0):
    try:
        outputText = ""
        indentation = "    "*currentIndentationLevel
        for i in range(len(textLineArray)):
            if textLineArray[i].startswith('#'):
                break

            if textLineArray[i] == "}":
                currentIndentationLevel -= 1
                break

            if textLineArray[i] == "use":
                outputText, currentIndentationLevel, imports = resolve_dependencies(
                    textLineArray,
                    i,
                    outputText,
                    imports,
                    currentIndentationLevel=currentIndentationLevel)
                break

            if textLineArray[i] == "object":
                outputText, currentIndentationLevel, objects = parse_objects(
                    textLineArray,
                    outputText,
                    objects,
                    currentIndentationLevel=currentIndentationLevel)
                break

            if textLineArray[i] in types or "|" in textLineArray[i]:
                if textLineArray[i+1] == "procedure":
                    outputText, currentIndentationLevel, procedures = parse_procedures(
                        textLineArray,
                        outputText,
                        procedures,
                        currentIndentationLevel=currentIndentationLevel)
                    break
            if "=" in textLineArray:
                outputText, variables = parse_variables(
                    textLineArray,
                    outputText,
                    variables,
                    currentIndentationLevel=currentIndentationLevel)
                break

            if textLineArray[i] == "return":
                outputText = parse_returns(
                    textLineArray,
                    outputText,
                    currentIndentationLevel=currentIndentationLevel)

            # if textLineArray[i] in outputText:
            #     if outputText[outputText.find(textLineArray[i])+1] == "(":
            #         outputText += f"{textLineArray[i]}({textLineArray[i+1]})"

            if textLineArray[i] in ["if", "else"]:
                outputText, currentIndentationLevel = parse_conditionals(textLineArray,
                                                                         outputText,
                                                                         currentIndentationLevel=currentIndentationLevel)

            if textLineArray[i] in imports:
                if ":" in textLineArray:
                    if textLineArray[i+2] in objects:
                        outputText += f"{indentation}{textLineArray[i+2]}.{textLineArray[i+4]}({''.join(textLineArray[i+5:])})\n"
                    elif textLineArray[i+2] in procedures:
                        outputText += f"{indentation}{textLineArray[i+2]}({''.join(textLineArray[i+3:])})\n"
                    else:
                        outputText += f"{indentation}{textLineArray[i+2]}({''.join(textLineArray[i+3:])})\n"
                else:
                    outputText += f"{indentation}{textLineArray[i]}({''.join(textLineArray[i+1:])})\n"
                break
        return outputText, currentIndentationLevel, imports, objects
    except Exception as e:
        print(textLineArray)
        raise


with open("example2.py", "w") as f:
    compiled = "from typing import Union\n" + \
        parse(["use", "local", "example2"])[0]
    f.write(compiled)
