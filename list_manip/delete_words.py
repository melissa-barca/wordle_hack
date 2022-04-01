import sys


with open("already_used.txt") as f:
    delete_words = set(f.read().strip().split())

with open("words_small.txt") as f:
    words = set(f.read().strip().split())

new_words = words.difference(delete_words)
delete_words = delete_words.difference(words)

with open("words_small_edit.txt", 'w') as f:
    f.writelines(["%s\n" % w for w in new_words])

if len(delete_words) == 0:
    sys.exit("Delete words is empty")

print(f"Continuing to delete {len(delete_words)} from words.txt...")

with open("words.txt") as f:
    long_words = set(f.read().strip().split())

long_words = long_words.difference(words).difference(delete_words)
with open("words_edit.txt", 'w') as f:
    f.writelines(["%s\n" % w for w in long_words])



sys.exit(f"Delete words: {len(delete_words)}")
