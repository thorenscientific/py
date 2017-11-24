from mcpi.minecraft import Minecraft
mc = Minecraft.create()

import time

hits = mc.events.pollBlockHits()
print("Polling!!")
time.sleep(10)
print("Melonizing!!")

block = 103

for hit in hits:
    x,y,z = hit.pos.x, hit.pos.y, hit.pos.z
    mc.setBlock(x,y,x,block)

