from numpy import choose
import starters

import collections

import random
import sys

MAX_GUESS = 6
WORD_LENGTH = 5
WORD_FILE = "words/words_small.txt"
LONG_WORD_FILE = "words/words.txt"
ALREADY_USED_FILE = "words/already_used.txt"

NO_MORE_GUESSES = "Uh oh! We ran out of guesses! 😿"
NOT_IN_WORD_CHAR = "."

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
    first_guess = input("> ")
    if len(first_guess) != WORD_LENGTH:
        first_guess = starters.get_starter()
    return first_guess

def get_guess(guess, words):
    if len(guess) != WORD_LENGTH:
        if len(words) == 0:
            sys.exit(NO_MORE_GUESSES)
        guess = random.choice(words)
    if guess in words:
        words.remove(guess)
    return guess.lower()

def get_wordle(guess, words):
    guess = get_guess(guess, words)
    print(f"Your guess: {guess}")

    result = input("Enter your result: ")
    while len(result) != WORD_LENGTH:
        result = input("Invalid result. Try again: ")

    return Wordle(guess, result)

# assumes letter and guess are in lower case
def apply_results_multiple(letter, wordle, words):
    positions = set()
    result = ""

    for pos, char in enumerate(wordle.guess):
        if char == letter:
            positions.add(pos)
            result += wordle.result[pos]
    
    # if the letter never appears in the word, remove all words with the letter
    if result.count(NOT_IN_WORD_CHAR) == len(result):
        words = [w for w in words if letter not in w]
        return words

    # analyze the number of occurrences
    if NOT_IN_WORD_CHAR in result:
        exact_count = len(result) - result.count(NOT_IN_WORD_CHAR)
        words = [w for w in words if w.count(letter) == exact_count]
    else:
        floor_count = len(positions)
        words = [w for w in words if w.count(letter) >= floor_count]
    
    # analyze the positions
    for pos in positions:
        if wordle.result[pos] != NOT_IN_WORD_CHAR:
            if wordle.result[pos].isupper():
                words = [w for w in words if w[pos] == letter]
            else:
                words = [w for w in words if w[pos] != letter]

    return words

# assumes guesses are in lower case
def apply_results(results, words):

    for wordle in results:
        multiples = set()

        for (i, zipped) in enumerate(zip(wordle.guess, wordle.result)):

            if (wordle.guess.count(zipped[0]) > 1):
                if zipped[0] not in multiples:
                    multiples.add(zipped[0])
                    words = apply_results_multiple(zipped[0], wordle, words)

            elif zipped[1] == NOT_IN_WORD_CHAR:
                words = [w for w in words if zipped[0] not in w]

            elif zipped[0] == zipped[1].lower():
                if zipped[1].isupper():
                    words = [w for w in words if w[i] == zipped[0].lower()]
                else:
                    words = [w for w in words if zipped[0] in w and w[i] != zipped[0].lower()]

            else:
                sys.exit(f"Unexpected input: {zipped[1]} Exiting early")

        if len(words) <= 1:
            return words

    return words

def retire_word(word, file_name = WORD_FILE):
    with open(ALREADY_USED_FILE, 'a') as f:
        f.write(word + '\n')
        print(f"{word} written to {ALREADY_USED_FILE}")
    with open(file_name, 'r') as f:
        lines = f.readlines()
    lines.remove(word + "\n")
    with open(file_name, 'w') as f:
        f.writelines(["%s" % line for line in lines ])
        print(f"{word} removed from {file_name}")
    
def prompt_for_retire(backup_files, backup_file_count, word):
    if len(backup_files) == 0:
        sys.exit(f"This is a repeat word - {word} is already in {ALREADY_USED_FILE}!")

    retire = input("Would you like to retire this word? [Yes/No] ") 
    if len(retire) > 0 and retire[0] in ['Y', 'y']:
        if len(backup_files) == backup_file_count:
            retire_word(word)
        else:
            retire_word(word, LONG_WORD_FILE)

def read_words_from_backup_file(file_name, results):
    with open(file_name) as f:
        words = f.read().strip().split()
    words = apply_results(results, words) 
    return words

def most_common_letter(words, exclude = []):
    long_word = ''.join(str(w) for w in words)
    for e in exclude:
        long_word = long_word.replace(e, "")
    if len(long_word) == 0:
        return None

    return collections.Counter(long_word).most_common(1)[0][0]
    #return collections.Counter(long_word).most_common(round(len(words) / 2))[0][0]

def most_common_letter_guess(words):
    excludes = []
    while len(words) != 1:
        letter = most_common_letter(words, excludes)

        if letter == None:
            return random.choice(words)
        excludes.append(letter)

        words = [w for w in words if letter in w]
    return words[0]

def get_next_guess(wordle, words, results, backup_files):
    return most_common_letter_guess(words)

if __name__ == "__main__":

    with open(WORD_FILE) as f:
        words = f.read().strip().split()

    backup_files = [LONG_WORD_FILE, ALREADY_USED_FILE]
    backup_file_count = len(backup_files)

    first_guess = intro()
    wordle = get_wordle(first_guess, words)
    results = {wordle}

    while wordle.result != wordle.guess.upper():

        if len(results) == MAX_GUESS:
            continue_play = input(f"I'm sorry! You lost the NY Times puzzle 🙀 Do you want to keep playing? [Yes/yes to continue]")
            if len(continue_play) == 0 or continue_play[0] not in ['Y', 'y']:
                sys.exit(f"Sorry! Thanks for playing! 😿")

        # apply results to word list
        words = apply_results([wordle], words)

        # when we run out of words, use back up files of less common and already used words
        while len(words) == 0 and len(backup_files) != 0:
            file_name = backup_files.pop(0)
            with open(file_name) as f:
                words = f.read().strip().split()
            words = apply_results(results, words) 

            if len(backup_files) == 0 and words == 0:
                sys.exit(NO_MORE_GUESSES)

        # exit the game when there is only one word left and we've used all backup files
        if len(words) == 1 and len(backup_files) == 0:
            print(f"Last guess! This must be the winner: {words[0]} 😸")
            prompt_for_retire(backup_files, backup_file_count, words[0])
            sys.exit()

        # retrieve next guess and result
        orig = len(words)
        guess = get_next_guess(wordle, words, results, backup_files)
        assert len(words) == orig
        wordle = get_wordle(guess, words)
        results.add(wordle)

    if wordle.result == wordle.guess.upper():
        print("Congrats! You're a winner! 😸")
        prompt_for_retire(backup_files, backup_file_count, wordle.guess)
    else:
        sys.exit("Oh no! Something bad happened! 😿")
