from typing import Union
# --- DISPLAY BEGIN


def display(value):
    print(value)
# --- DISPLAY END


# --- DISPLAY_INLINE BEGIN


def display_inline(value):
    print(value, end="\r")
# --- DISPLAY_INLINE END


# --- INPUT BEGIN


def user_input(value=""):
    return input(value)
# --- DISPLAY BEGIN


def display(value):
    print(value)
# --- DISPLAY END
class Object:
    def HelloWorld() -> Union[None]:
        string = str()
        display(string)
    def Add(number1:Union[int, float],number2:Union[int, float]) -> Union[int, float]:
        return number1 + number2
Object.HelloWorld()
number1 = int(user_input("Number 1:")
)
sum = Object.Add(number1,4)

if type(sum) == type(10):
    display(sum)
else:
    display("Sum is not an integer")
