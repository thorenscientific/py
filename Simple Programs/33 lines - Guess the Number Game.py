#33 lines - Guess the Number Game
import random

guessesTaken = 0

print 'Hello! What is your name?'
myName = raw_input()

number = random.randint(1, 20)
print 'Well, ' + myName + ', I am thinking of a number between 1 and 20.'

while guessesTaken < 6:
    print 'Take a guess.'
    guess = input()
    #fyi: input() is for numbers.  raw_input() is for strings.

    guessesTaken = guessesTaken + 1

    if guess < number:
        print 'Your guess is too low.'

    if guess > number:
        print 'Your guess is too high.'

    if guess == number:
        break

if guess == number:
    guessesTaken = str(guessesTaken)
    print 'Good job, ' + myName + '! You guessed my number in ' + guessesTaken + ' guesses!'

if guess != number:
    print 'Nope. The number I was thinking of was ' + str(number)
