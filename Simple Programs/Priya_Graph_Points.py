## {{{ http://code.activestate.com/recipes/577814/ (r1)
# Lorenz Attractor (projected onto XY-plane)
# http://en.wikipedia.org/wiki/Lorenz_attractor
# FB - 201107317
import random, sys
from PIL import Image, ImageDraw
imgx = 1000
imgy = 1000
image = Image.new("RGB", (imgx, imgy))

draw = ImageDraw.Draw(image)

color = (255,150,100)
scale = 10
points = ((250, 250), (250,750), (750,750),(750,250),(250,250))

#points = points * scale

draw = ImageDraw.Draw(image)
#draw.line((0, 0) + image.size, fill=(255,255,255), width=10)
#draw.line((0, image.size[1], image.size[0], 0), fill=128)
draw.line(points, fill=color, width=25)
del draw


#image.save(sys.stdout, "PNG")
image.save("Priya_Points.png", "PNG")
## end of http://code.activestate.com/recipes/577814/ }}}
