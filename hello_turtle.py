#another priya program

import turtle
import random

print("Hello World")

t = turtle.Pen()
turtle.speed(10)
for i in range(360/5):
    t.forward(100 + 50*random.random())
    t.left(85)

raw_input("Hit enter to close")