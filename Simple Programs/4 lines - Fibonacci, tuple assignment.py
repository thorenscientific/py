parents, babies = (1.0, 1.0)
while babies < 1000000000.0:
    print 'This generation has %d babies' % babies
    parents, babies = (babies, parents + babies)
# add calculation of golden ratio
    print "Golden ratio approximation: ",  (babies / parents)
