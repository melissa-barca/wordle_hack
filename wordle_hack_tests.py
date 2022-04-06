import unittest
import wordle_hack
import random

FIRST_GUESS = 'kebab'
FIRST_RESULT = '.eBab'
TEST_WORDS = ['abbas', 'bubby', 'zebub', 'barbs', 'opens', 'karma', 'kebab', 'babes', 'abyss', 'abbey']

class TestWordleHack(unittest.TestCase):

    def test_apply_results_multiple(self):
        wordle = wordle_hack.Wordle(FIRST_GUESS, FIRST_RESULT)
        words = wordle_hack.apply_results_multiple('b', wordle, TEST_WORDS)
        self.assertEqual(set(words), {'abbas', 'bubby', 'babes', 'abbey'})

    def test_apply_results(self):
        wordle = wordle_hack.Wordle(FIRST_GUESS, FIRST_RESULT)
        words = wordle_hack.apply_results([wordle], TEST_WORDS)
        self.assertSetEqual(set(words), {'babes', 'abbey'})

    def test_apply_results_multiple_karma(self):
        wordle = wordle_hack.Wordle('karma', '.a..a')
        words = wordle_hack.apply_results_multiple('a', wordle, TEST_WORDS)
        self.assertEqual(set(words), {'abbas'})

    def test_apply_results_karma(self):
        wordle = wordle_hack.Wordle('karma', '.a..a')
        words = wordle_hack.apply_results([wordle], TEST_WORDS)
        self.assertEqual(set(words), {'abbas'})

    def play_game(self, winner, guess, in_words = TEST_WORDS):
        words = in_words.copy()
        words.remove(guess)

        guess_num = 1

        while guess != winner:
            #print(f"Guess: {guess}")
            self.assertNotIn(guess, words)
            result = ""
            for pos, g in enumerate(guess):
                if g not in winner:
                    result += wordle_hack.NOT_IN_WORD_CHAR
                elif g == winner[pos]:
                    result += g.upper()
                else:
                    guess_count = guess.count(g)
                    winner_count = winner.count(g)
                    if guess.count(g) == 1 or guess_count <= winner_count:
                        result += g.lower()
                    else:
                        correct_count = 0
                        for c, w in zip(guess, winner):
                            if g == c == w:
                                correct_count += 1
                        difference = winner_count - correct_count
                        if result.count(g.lower()) != difference:
                            result += g.lower()
                        else:
                            result += wordle_hack.NOT_IN_WORD_CHAR

            words = wordle_hack.apply_results([wordle_hack.Wordle(guess, result)], words)
            #print(f"Result: {result}")
            #print(f"Words: {words}")
            #guess = wordle_hack.get_guess("", words)
            guess = wordle_hack.get_guess(wordle_hack.most_common_letter_guess(words), words)
            guess_num += 1

        return guess, guess_num

    # play a round where each word is the winner once and the first guess is never correct
    def play_with_words(self, words):
        guess_sum = 0
        for winner in words:
            guess = random.choice([w for w in words if w != winner])
            guess, guess_num = self.play_game(winner, guess, words)
            self.assertEqual(guess, winner)
            guess_sum +=  guess_num
        print(f"Average win: {guess_sum / len(words)}")

    def test_fast(self):
        self.play_with_words(TEST_WORDS)

    def test_small_words(self):
        with open(wordle_hack.WORD_FILE) as f:
            words = f.read().strip().split()
        self.play_with_words(words)

    # play a round where the first guess is the winner
    def test_first_win(self):
        winner = random.choice(TEST_WORDS)
        self.assertEqual(self.play_game(winner, winner)[0], winner)

if __name__ == '__main__':
    unittest.main()
