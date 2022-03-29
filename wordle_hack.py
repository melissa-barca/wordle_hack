import starters

import random
import sys

MAX_GUESS = 6
WORD_FILE = "words/words_small.txt"
LONG_WORD_FILE = "words/words.txt"
ALREADY_USED_FILE = "words/already_used.txt"

NO_MORE_GUESSES = "Uh oh! We ran out of guesses! 😿"

class Wordle:
    def __init__(self, guess, result):
        self.guess = guess
        self.result = result

def intro():
    print("Welcome to Wordle Hack!")

    instructions = input("Do you want to view the instructions? [Yes/No] ")
    if len(instructions) > 0 and instructions[0] in ['Y', 'y']:
        print("Either provide your own first guess or request one. After each guess, enter a five character result using dots if the letter is not in the word, lower case letters if the letter is in the word but the wrong spot, and capital letters if the letter is in the correct spot.")

    print("Enter a five letter word to make your first guess or press Enter to be provided a random first guess.")

def get_wordle(guess, words):
    if len(guess) != 5:
        if len(words) == 0:
            print(f"get_wordle guess: {guess}")
            sys.exit(NO_MORE_GUESSES)
        guess = random.choice(words)

    if guess in words:
        words.remove(guess)
  
    print(f"Your guess: {guess}")

    result = input("Enter your result: ")
    while len(result) != 5:
        result = input("Invalid result. Try again: ")

    return Wordle(guess, result)

def apply_results(results, words):
    for wordle in results:
        for (i, zipped) in enumerate(zip(wordle.guess, wordle.result)):
            if zipped[1] == '.':
                words = [w for w in words if zipped[0] not in w]
            elif zipped[1].upper() == zipped[0].upper():
                if zipped[1].isupper():
                    words = [w for w in words if w[i] == zipped[0].lower()]
                else:
                    words = [w for w in words if zipped[0] in w and w[i] != zipped[0].lower()]
            else:
                sys.exit(f"Unexpected input: {g} Exiting early")
        if len(words) <= 1:
            return words
    return words

def retire_word(word, file_name = WORD_FILE):
    with open(ALREADY_USED_FILE, 'a') as f:
        f.write(word + '\n')
    with open(file_name, 'r') as f:
        lines = f.readlines()
    lines.remove(word + "\n")
    with open(file_name, 'w') as f:
        f.writelines(["%s" % line for line in lines ])
    
def make_educated_guess(result, words):
    index = result.index('.')
    possibilities = set()
    second_possibilities = set()
    for w in words:
        if w[index].upper() in result:
            second_possibilities.add(w[index])
        else:
            possibilities.add(w[index])

    guess = ""
    for p in possibilities:
        guess = guess + p

    if len(guess) >= 5:
        return guess[0:5]

    for p in second_possibilities:
        guess = guess + p
        if len(guess) >= 5:
            return guess[0:5]

    return guess.rjust(5, end='.')


if __name__ == "__main__":

    with open(WORD_FILE) as f:
        words = f.read().strip().split()

    backup_files = [LONG_WORD_FILE, ALREADY_USED_FILE]

    intro()
    first_guess = input("> ")
    if len(first_guess) != 5:
        first_guess = starters.get_starter()

    wordle = get_wordle(first_guess, words)
    results = {wordle}

    while wordle.result != wordle.guess.upper():

        words = apply_results([wordle], words)

        while len(words) == 0 and len(backup_files) != 0:
            file_name = backup_files.pop(0)
            with open(file_name) as f:
                words = f.read().strip().split()
            words = apply_results(results, words) 

            if len(backup_files) == 0 and words == 0:
                sys.exit(NO_MORE_GUESSES)

        if len(words) == 1 and len(backup_files) == 0:
            sys.exit(f"Last guess! This must be the winner: {words[0]}")

        if wordle.result.isupper() and wordle.result.count('.') == 1 and len(results) < (MAX_GUESS - 2) and len(words) > 2:
            edu_guess = make_educated_guess(wordle.result, words)
            wordle = get_wordle(edu_guess, words)
        else:
            wordle = get_wordle("", words)
        results.add(wordle)

    if wordle.result == wordle.guess.upper():
        print("Congrats! You're a winner! 😸")
        retire = input("Would you like to retire this word? [Yes/No] ") 
        if len(retire) > 0 and retire[0] in ['Y', 'y']:
            retire_word(wordle.guess)
    else:
        sys.exit("Oh no! Something bad happened! 😿")
