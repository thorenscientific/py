#Connect to Minecraft
from mcpi.minecraft import Minecraft
mc = Minecraft.create("10.26.148.195")

#Set x, y, and z variables to represent coordinates
x = 10
y = 110
z = 12

#Change the player's position
mc.player.setTilePos(x, y, z)
