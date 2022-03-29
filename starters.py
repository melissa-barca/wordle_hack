# best starters according to https://www.oregonlive.com/trending/2022/02/best-wordle-strategy-for-first-guesses-based-on-expert-analysis.html

import random

STARTERS = [ 'slice', 'tried', 'crane']

def get_starter():
    return random.choice(STARTERS)
