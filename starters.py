import random

# best starters according to https://www.oregonlive.com/trending/2022/02/best-wordle-strategy-for-first-guesses-based-on-expert-analysis.html
#STARTERS = [ 'slice', 'tried', 'crane']

# vowel heavy starters
#STARTERS = [ 'adieu', 'audio', 'canoe']

# ny times wordle-bot starters 
STARTERS = [ 'slant', 'trace', 'crane', 'crate']


def get_starter():
    return random.choice(STARTERS)
