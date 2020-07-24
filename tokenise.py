import sys

def tokenise(text):
    isString = False
    isComment = False
    token = ""
    tokens = []
    for char in text:
        if char == '"':
            isString = not isString

        if char == "#":
            isComment = True

        if isComment:
            if not char == "\n":
                token += char
                continue
            else:
                isComment = False
                tokens.append(token)
                token = ""
                continue

        if char in [" ", "\n"] and isString == False:
            if not (token == " " or len(token) == 0):
                if not token.count('"'):
                    token = token.replace(' ', '')
                tokens.append(token)
            token = ""
            continue

        if char in ["(", ")", "{", "}", ":", ","] and isString == False:
            if len(token.replace(' ', '')) > 0:
                tokens.append(token)
                token = ""
            tokens.append(char)
            continue

        token += char

    return tokens

with open("example.txt", "r") as f:
    l = f.readline()
    while l:
        print(tokenise(l))
        l = f.readline()
