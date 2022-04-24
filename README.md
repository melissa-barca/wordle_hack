# wordle_hack
A Python program I wrote to keep up with my family's Wordle addiction. My dad says this is cheating.
For each result, enter a period if the letter is not in the world, the lower case letter if it is in the word but in the wrong spot, or the capital letter if it's in the word in the wrong spot. 

The word list is from https://static.nytimes.com/newsgraphics/2022/01/25/wordle-solver/assets/solutions.txt

## Example
```
➜  python wordle_hack.py
Welcome to Wordle Hack!
Do you want to view the instructions? [Yes/No] N
Enter a five letter word to make your first guess or press Enter to be provided a random first guess.
>
Your guess: nabes
Enter your result: ...e.
Your guess: flype
Enter your result: ..ype
Your guess: pervy
Enter your result: pe..Y
Your guess: empty
Enter your result: E.p.Y
Final guess! This must be the winner: epoxy
```
