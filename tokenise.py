import sys

def tokenise(text):
    isString = False
    token = ""
    tokens = []
    for char in text:
        if char == '"':
            isString = not isString

        if char in [" ", "\n", "(", ")", "{", "}"] and isString == False:
            if not (token == " " or len(token) == 0):
                token = token.replace(' ', '')
                tokens.append(token)
            token = ""

        token += char

    return tokens

with open("example.txt", "r") as f:
    l = f.readline()
    while l:
        print(tokenise(l))
        l = f.readline()
