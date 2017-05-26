def greet(name):
    print 'hello', name
    return 'Returned name'


    
greet(greet('jack'))
greet('Jill')
greet('Bob')

#Sample output:
#hello jack
#hello None   #Note the "None", what type is this?
#hello Jill
#hello Bob
