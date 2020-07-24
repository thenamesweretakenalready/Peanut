import os
import re

class DependencyError(ValueError):
    pass

def parse(textArray):
    outputText = ""
    for i in range(len(textArray)):
        if textArray[i] == "use":
            if textArray[i+1] == "module":
                if not os.path.isfile(f"builtins/{textArray[i+2]}.py"):
                    raise DependencyError(f"{textArray[i+2]} is not a builtin.")

                if len(textArray) == 3:
                    with open(f"builtins/{textArray[i+2]}.py") as f:
                        data = f.read()
                        outputText += data
                else:
                    
