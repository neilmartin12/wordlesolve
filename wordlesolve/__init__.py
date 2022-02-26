"""WordleSolver solves Wordle!

*wordlesolve* will solve almost any Wordle puzzle within six guesses.
Just follow the suggestions and type in the results.

Usage
=====

Solve mode
----------

>>> from wordlesolve import Solver
>>> solver = Solver()
>>> solver.solve()

*wordlesolve* gives you up to five suggestions for each guess.
Type in the guess you use and the outcome Wordle gives for each letter:
0 for grey, 1 for yellow, 2 for green.

For example if you guess RATES and get R/E/S in grey, T in yellow and A in green, enter:
Your guess:  RATES
Outcome:     02100

*wordlesolve* will use that information to suggest some more guesses,
getting you closer to the solution each time!


Play mode
---------

*wordlesolve* also includes a play mode - a console-based Wordle clone.
Not nearly as good as the real thing but fun to practise!

>>> from wordlesolve import Solver
>>> solver = Solver()
>>> solver.play()


Test mode
---------

Also included is a test mode - this was originally intended
to test the algorithm during development.
Test mode runs the solve algorithm against any number of solutions,
either provided or randomly selected from the built-in database,
and provides information on how quickly each was solved.

>>> from wordlesolve import Solver
>>> solver = Solver()
>>> solver.test()


Arguments
---------

Each *wordlesolve* mode takes a number of keyword arguments.

Keyword         Type        Description                                         Modes
hard            bool        Use hard mode                                       solve, play, test
guess_freq      float       Minimum word frequency allowed for guesses          solve, play, test
solution_freq   float       Minimum word frequency allowed for solutions        play, test
verbosity       int         Verbosity level for test results                    test
solutions       list[str]   Solutions to test                                   test
filename        str         Path to a text file containing solutions to test    test


How it works
============

*wordlesolve* takes the result of each guess and builds a set of rules, for example:

    Your guess:  RATES
    Outcome:     02100

will generate five rules:

- There is no R in the solution
- There is at least one A, including one in second position
- There is at least one T but not in third position
- There is no E
- There is no S

*wordlesolve* will then filter its database of five-letter words
to keep only those that match the rules.
In this case there are 113 matching words, including FAITH, FAULT, PAINT, HABIT and VAULT.

*wordlesolve* analyses all matching words and counts letter frequency,
i.e. in how many words each letter appears once, twice, etc.
So of the 113 matching words, 44 have at least one letter N,
but only 2 contain the letter X.

A similar analysis is run for the position of each letter,
so for example 52 of the 113 words begin with the letter T,
and 39 end with the letter T.

*wordlesolve* applies a mask to these counts,
to remove any letters or positions that are already defined by the rules.
For example there is no E in the letter, so all E scores will be set to zero.
Similarly, because we know there is an A in position 2,
no score will be given for an A in position 2.

In normal mode, *wordlesolve* returns to the full list of words
and scores each word according to these frequency and position scores.
If a word contains at least one letter N, it will score 44 points;
if it begins with a T it will score 52, etc.

(In hard mode only the list of matching words is analysed
rather than the full word list)

This produces a list of scored words, where the score indicates how
useful the word will be in confirming or eliminating the remaining matches.
The next guess is made and the process starts again.



"""

__version__ = "0.1.0"

from .solver import Solver
