import argparse
import starters
import collections
import random
import sys
import math

MAX_GUESS = 6
WORD_LENGTH = 5
WORD_FILE = "words/wordle_words.txt"
ALREADY_USED_FILE = "words/already_used.txt"
MISSING_FILE = "words/missing_words.txt"

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

def setup_parse():
    parser = argparse.ArgumentParser(description="Wordle Hack")
    parser.add_argument("--debug", action='store_true', help="Run with debug logging")
    return parser.parse_args()

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

    log_debug(f"applying results on {len(words)} words")
    for wordle in results:
        multiples = set()

        log_debug(f"Applying guess '{wordle.guess}' and result '{wordle.result}'");
        for (i, zipped) in enumerate(zip(wordle.guess, wordle.result)):

            if (wordle.guess.count(zipped[0]) > 1):
                if zipped[0] not in multiples:
                    multiples.add(zipped[0])
                    words = apply_results_multiple(zipped[0], wordle, words)
                    log_debug(f"1 word count: {len(words)}");

            elif zipped[1] == NOT_IN_WORD_CHAR:
                words = [w for w in words if zipped[0] not in w]
                log_debug(f"2 word count: {len(words)}");

            elif zipped[0] == zipped[1].lower():
                if zipped[1].isupper():
                    words = [w for w in words if w[i] == zipped[0].lower()]
                    log_debug(f"3 word count: {len(words)}");
                else:
                    words = [w for w in words if zipped[0] in w and w[i] != zipped[0].lower()]
                    log_debug(f"4 word count: {len(words)}");

            else:
                sys.exit(f"Unexpected input: {zipped[1]} Exiting early")

        log_debug(f"Length of words after applying wordle: {len(words)}")
        if len(words) <= 1:
            return words

    return words

def retire_word(word, file_name = WORD_FILE):
    with open(ALREADY_USED_FILE, 'a') as f:
        f.write(word.upper() + '\n')
        log_debug(f"{word} written to {ALREADY_USED_FILE}")

    with open(file_name, 'r') as f:
        lines = f.readlines()
    if word + "\n" in lines:
        lines.remove(word + "\n")
    else:
        sys.exit(f"Word '{word}' not found in {file_name}, could not complete retirement.")

    with open(file_name, 'w') as f:
        f.writelines(["%s" % line for line in lines ])
        log_debug(f"{word} removed from {file_name}")
    
def prompt_for_retire(backup_files, backup_file_count, word):
    if len(backup_files) == 0:
        sys.exit(f"This is a repeat word - {word} is already in {ALREADY_USED_FILE}!")

    retire = input("Would you like to retire this word? [Yes/No] ") 
    if len(retire) > 0 and retire[0] in ['Y', 'y']:
        if len(backup_files) == backup_file_count:
            retire_word(word)
        else:
            retire_word(word, MISSING_FILE)

def read_words_from_backup_file(file_name, results):
    with open(file_name, encoding='utf-8') as f:
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
    if len(words) <= 3:
        # If very few words remain, just return the first one
        return words[0]
    
    # Score each word based on unique letter frequency
    word_scores = {}
    for word in words:
        # Only count each letter once per word to avoid duplicates
        unique_letters = set(word)
        score = 0
        for letter in unique_letters:
            # Count how many words contain this letter
            score += sum(1 for w in words if letter in w)
        word_scores[word] = score
    
    # Return the word with the highest score
    return max(word_scores, key=word_scores.get)

def calculate_entropy(word, word_list):
    """Calculate how much a guess reduces possible solutions"""
    patterns = {}
    
    # For each potential answer, determine what pattern we'd get
    for potential_answer in word_list:
        pattern = []
        for i, letter in enumerate(word):
            if letter == potential_answer[i]:
                pattern.append('G')  # Green
            elif letter in potential_answer:
                pattern.append('Y')  # Yellow
            else:
                pattern.append('.')  # Gray
        
        pattern_key = ''.join(pattern)
        patterns[pattern_key] = patterns.get(pattern_key, 0) + 1
    
    # Calculate entropy (information gain)
    total = len(word_list)
    entropy = 0
    for count in patterns.values():
        probability = count / total
        entropy -= probability * (math.log2(probability))
    
    return entropy

def get_next_guess(wordle, words, results, backup_files):
    if len(words) < 20:
        # For small word lists, calculate entropy for all words
        word_entropy = {word: calculate_entropy(word, words) for word in words}
        return max(word_entropy, key=word_entropy.get)
    
    # Existing logic for larger word lists
    # ...

def position_based_guess(words):
    # Create a scoring matrix for each position
    position_scores = [{} for _ in range(WORD_LENGTH)]
    
    # Count letter frequencies at each position
    for word in words:
        for pos, letter in enumerate(word):
            position_scores[pos][letter] = position_scores[pos].get(letter, 0) + 1
    
    # Score each word based on positional letter frequency
    word_scores = {}
    for word in words:
        score = 0
        for pos, letter in enumerate(word):
            score += position_scores[pos].get(letter, 0)
        word_scores[word] = score
    
    return max(word_scores, key=word_scores.get)

def log_debug(message):
    try:
        if args.debug:
            print(message)
    except NameError:
        pass

if __name__ == "__main__":
    args = setup_parse()

    log_debug(f"Debug mode is on")
    log_debug(f"Opening file {WORD_FILE}")

    with open(WORD_FILE) as f:
        words = f.read().strip().split()

    log_debug(f"...read {len(words)} words...")

    backup_files = [ MISSING_FILE, ALREADY_USED_FILE ]
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
            log_debug(f"Opening file {file_name}")
            with open(file_name, encoding='utf-8') as f:
                words = f.read().strip().split()
            log_debug(f"...read {len(words)} words...")
            words = apply_results(results, words) 

            if len(backup_files) == 0 and words == 0:
                sys.exit(NO_MORE_GUESSES)

        # exit the game when there is only one word left and we've used all backup files
        if len(words) == 1 and len(backup_files) == 0:
            print(f"Last guess! This must be the winner: {words[0]} 😸")
            prompt_for_retire(backup_files, backup_file_count, words[0])
            sys.exit()

        # retrieve next guess and result
        guess = get_next_guess(wordle, words, results, backup_files)
        wordle = get_wordle(guess, words)
        results.add(wordle)

    if wordle.result == wordle.guess.upper():
        print("Congrats! You're a winner! 😸")
        prompt_for_retire(backup_files, backup_file_count, wordle.guess)
    else:
        sys.exit("Oh no! Something bad happened! 😿")
