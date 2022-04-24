# script writes all words in 'READ_WORD_FILE' but not in 'ALREADY_USED_WORD_FILE' to 'NEW_WORD_FILE'

import sys

ALREADY_USED_WORD_FILE  = '../words/already_used.txt'
READ_WORD_FILE = './wordle_words.txt'
NEW_WORD_FILE = '../words/wordle_words.txt'

with open(ALREADY_USED_WORD_FILE) as f:
    delete_words = set(f.read().strip().split())

with open(READ_WORD_FILE) as f:
    words = set(f.read().strip().split())

new_words = list(words.difference(delete_words))
new_words.sort()
with open(NEW_WORD_FILE, 'w') as f:
    f.writelines(["%s\n" % w for w in new_words])

print(f'New file "{NEW_WORD_FILE}" contains {len(words) - len(new_words)} fewer words than "{ALREADY_USED_WORD_FILE}"')

#print(f"Continuing to delete {len(delete_words)} from words.txt...")
#with open("words.txt") as f:
#    long_words = set(f.read().strip().split())

#long_words = long_words.difference(words).difference(delete_words)
#with open("words_edit.txt", 'w') as f:
#    f.writelines(["%s\n" % w for w in long_words])

