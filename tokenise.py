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

        if char in [" ", "\n"] and not isString:
            if not (token == " " or len(token) == 0):
                if not token.count('"'):
                    token = token.replace(' ', '')
                tokens.append(token)
            token = ""
            continue

        if char in ["(", ")", "{", "}", ":", ","] and not isString:
            if len(token.replace(' ', '')) > 0:
                tokens.append(token)
                token = ""
            tokens.append(char)
            continue

        token += char

    return tokens


# with open("example.pnut", "r") as f:
#     line = f.readline()
#     while line:
#         print(tokenise(line))
#         line = f.readline()
