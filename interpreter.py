from parser import parse
from tokenise import tokenise
import sys
import subprocess


def main(filename):
    with open(filename, "r") as f:
        output = ""
        data = f.readline()
        imports = []
        cIL = 0
        while data:
            parsed = parse(tokenise(data), imports=imports,
                           currentIndentationLevel=cIL)
            output += parsed[0]
            cIL = parsed[1]
            imports = parsed[2]

            data = f.readline()
    output = "from typing import Union\n" + output

    subprocess.run(["python3", "-c", output])


if __name__ == "__main__":
    main(sys.argv[1])
