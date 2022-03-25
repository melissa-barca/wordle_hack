import random
import sys

def intro():
    print("Welcome to Wordle Hack!")

    instructions = input("Do you want to view the instructions? [Yes/No] ")
    if instructions[0] == ['Y', 'y']:
        print("Either provide your own first guess or request one. After each guess, enter a five character result using dots if the letter is not in the word, lower case letters if the letter is in the word but the wrong spot, and capital letters if the letter is in the correct spot.")

    print("Enter a five letter word to make your first guess or press Enter to be provided a random first guess.")

def get_guess_and_result(guess, words):
    if len(guess) != 5:
        guess = random.choice(words)
    words.remove(guess)
    print(f"Your guess: {guess}")
    return guess, input("Enter your result: ")

if __name__ = "__main__":

    with open("words.txt") as f:
        words = f.read().strip().split()

    intro()
    guess, result = get_guess_and_result(input("> "), words)

    if len(result) != 5:
        result = input("Invalid result. Try again: ")

    while result.upper() != guess.upper():
        for (i, zipped) in enumerate(zip(guess, result)):
            if zipped[1] == '.':
                words = [w for w in words if zipped[0] not in w]
            elif zipped[1].upper() == zipped[0].upper():
                if zipped[1].isupper():
                    words = [w for w in words if w[i] == zipped[0].lower()]
                else:
                    words = [w for w in words if zipped[0] in w and w[i] != zipped[0].lower()]
            else:
                sys.exit(f"Unexpected input: {g} Exiting early")

        if len(words) == 1:
            sys.exit(f"Final guess! This must be the winner: {words[0]}")

        guess, result = get_guess_and_result("", words)
