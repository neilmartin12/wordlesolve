"""Solver class

>>> solver = Solver()

Has 3 public methods:

    .solve(guess_freq=1.17, hard=False)
        Solve Wordle puzzle.
        Runs an interactive console session providing context-sensitive
        guess suggestions to solve a Wordle puzzle.

    .play(solution_freq=3.2, guess_freq=0.0, hard=False)
        Play Wordle game.
        Runs a console-based Wordle clone.

    .test(solutions=None, filename=None, count=1, solution_freq=4.0, guess_freq=1.17,
            hard=False, verbosity=0, retval=False)
        Test Solver algorithm.
        Runs an automated test session and displays its results.


"""
from concurrent.futures import ProcessPoolExecutor
import datetime as dt
from functools import partial
import random
import string
from typing import Optional

import colorama as cr  # type: ignore
from wordfreq import zipf_frequency  # type: ignore

from .console import (
    display_test_outcomes,
    get_guess_input,
    get_outcome_input,
    get_yn_input,
    GuessOutcome,
    print_alphabet,
    print_word,
    TestOutcome,
)
from .ruleset import RuleSet, WordScore
from .wordlist import WORDLIST


class Solver:
    """Main Wordle Solver class."""

    def __init__(self):
        """Initialize Solver class"""
        self.words = WORDLIST
        cr.init(autoreset=True)

    def solve(self, guess_freq: float = 1.17, hard: bool = False):
        """Run solve mode

        Solves a Wordle puzzle.
        The user takes guesses from a list of suggestions
        and enters the outcome of each guess until the puzzle is solved.

        Args:
            guess_freq: minimum word frequency any guesses may have (default 1.7)
            hard: True for hard mode, False (the default) for normal mode
        """

        # Get the master word list
        words = self._filter_words(guess_freq)

        while True:
            print("\n")
            print("Wordle Solver")
            print("-------------")
            print(
                cr.Style.DIM
                + "Original game at https://www.nytimes.com/games/wordle/index.html"
            )
            if hard:
                print("[Hard mode]")
            print()

            # Initial match list is full word list
            matches = words
            rule_set = RuleSet()

            for guess_number in range(1, 7):

                # Get the scored word list
                # In hard mode score only matches, otherwise score all words
                word_scores = rule_set.score_words(matches if hard else words, matches)

                print(f"Guess number {guess_number}")

                # If solver is beaten the word_scores list will be empty
                # This means there are no matches for the ruleset in the word list
                # presumably because the solution isn't in the list
                # (or the user entered an outcome incorrectly)
                if word_scores:
                    print(
                        "Suggestions: "
                        + ", ".join((score[0] for score in word_scores[:5]))
                    )
                else:
                    print("Sorry - I don't have any suggestions for you!")

                guess = get_guess_input(13)
                outcome = get_outcome_input(13)
                print()

                # Solved?
                if outcome == "22222":
                    print("Congratulations - you solved it!\n")
                    break

                # Add outcome to ruleset and filter matches
                rule_set.add_outcome(guess, outcome)
                matches = rule_set.filter_matches(matches)

            # Solution not found
            else:
                print("Sorry - I wasn't able to solve that one for you!")

            # Play again?
            if get_yn_input("Solve another? ") == "N":
                break

    def play(
        self, solution_freq: float = 3.2, guess_freq: float = 0.0, hard: bool = False
    ):
        """Run play mode.

        Will choose a solution at random from the word list
        and allow the user 6 guesses to find it.
        Once the game has finished the user will be asked if they wish to play again.

        Args:
            solution_freq: minimum word frequency the solution may have (default 4.0)
            guess_freq: minimum word frequency any guesses may have (default 0.0)
            hard: True for hard mode, False (the default) for normal mode

        """

        # Get the master word list
        words = self._filter_words(guess_freq)

        while True:

            # Get a solution to find
            solution = random.choice(self._filter_words(solution_freq))

            # Initialize RuleSet
            rule_set = RuleSet()

            # Print header
            print("\n")
            print("WORDLE")
            print("------")
            print(
                cr.Style.DIM
                + "Original game at https://www.nytimes.com/games/wordle/index.html"
            )
            if hard:
                print("[Hard mode]")
            print()

            # Up to six guesses
            for guess_number in range(1, 7):

                valid = False

                while not valid:

                    # Get a guess
                    print("Guess number " + str(guess_number))
                    guess = get_guess_input()

                    # Check it is a valid word
                    if guess not in words:
                        print("That is not a valid word. Please try again.\n")

                    else:
                        # In hard mode the guess must match all rules
                        if hard and not rule_set.is_match(guess):
                            print(
                                "In hard mode you have to use all revealed hints in each guess\n"
                            )

                        else:
                            valid = True

                # Show outcome
                outcome = _get_outcome(guess, solution)
                print()
                print_word(guess, outcome)
                print()

                # Solved?
                if outcome == "22222":
                    print("Congratulations - you solved it!\n")
                    break

                # Add outcome to ruleset
                rule_set.add_outcome(guess, outcome)

                # Print alphabet
                print_alphabet(rule_set.get_alphabet_status())
                print()

            # Solution not found
            else:
                print("The correct answer was: " + cr.Style.BRIGHT + solution)
                print("Better luck next time!\n")

            # Play again?
            if get_yn_input("Play again? ") == "N":
                break

    def test(
        self,
        solutions: list[str] = None,
        filename: str = None,
        count: int = 1,
        solution_freq: float = 3.2,
        guess_freq: float = 1.17,
        hard: bool = False,
        verbosity: int = 0,
        retval: bool = False,
    ) -> Optional[dict[str, TestOutcome]]:
        """Run test mode

        Args:
            solutions:
                list of solutions to test
                if None (the default) random words will be used

            filename:
                file of solutions to test
                must be a text file with one solution per line
                if solutions is not None this argument is ignored

            count:
                number of different solutions to test
                if solutions or filename is not None this argument is ignored
                if zero all words in the word list will be tested

            solution_freq:
                minimum word frequency the solution may have (default 4.0)
                if solutions or filename is not None this argument is ignored

            guess_freq:
                minimum word frequency any guesses may have (default 0.0)

            hard:
                whether to use hard mode (default is False)

            verbosity:
                0: only minimal output - a progress indicator and summary of results (default)
                1: list of words and guesses to solve (one line per word)
                2: shows scores and matches for each guess

            retval:
                if True the function will return a dict of test outcomes
                with data about each word guessed, number of matches, etc.
        """
        # pylint: disable=too-many-arguments

        print("\n")
        print("Wordle Solver Test Mode")
        print("-----------------------")
        print()

        # Get the master word list
        words = self._filter_words(freq=guess_freq)

        # Get the list of solutions
        if solutions:

            # Filter out any invalid solutions
            solutions = [
                word.upper()
                for word in solutions
                if len(word) == 5
                and all(letter in string.ascii_letters for letter in word)
            ]

        else:
            # Solutions from file
            if filename is not None:
                try:
                    with open(filename, encoding="utf-8") as file:

                        # Validate words and add to solutions list
                        solutions = [
                            word[:5].upper()
                            for word in file
                            if (
                                len(word) >= 5
                                and all(
                                    letter in string.ascii_letters
                                    for letter in word[:5]
                                )
                            )
                        ]

                # Manage file error
                except OSError:
                    print(
                        cr.Style.BRIGHT
                        + cr.Fore.RED
                        + "Unable to read solutions file\n"
                    )

                # Manage invalid or empty file
                else:
                    if not solutions:
                        print(
                            cr.Style.BRIGHT
                            + cr.Fore.RED
                            + "File has no valid solutions"
                        )

        # Generate solutions from word list
        if not solutions:
            solutions = self._filter_words(freq=solution_freq)
            if 0 < count < len(solutions):
                solutions = random.sample(solutions, count)

        # Start a timer
        start = dt.datetime.now()

        # Run tests
        outcomes = _run_tests(words, solutions, hard)

        # Stop timer
        end = dt.datetime.now()
        time = (end - start).total_seconds()

        display_test_outcomes(outcomes, time, hard, verbosity)

        if retval:
            return outcomes

        return None

    def _filter_words(self, freq: float) -> list[str]:
        """Filters the master word list to the given frequency

        Args:
            freq: minimum frequency to include

        Returns the new list of words.
        """
        return [
            word
            for word in self.words
            if (freq == 0.0 or zipf_frequency(word, "en") >= freq)
        ]


def _get_outcome(guess: str, solution: str) -> str:
    """Get outcome string for the given guess / solution combination

    Args:
        guess: the word guessed
        solution: puzzle solution

    Returns:
        5-character string of:
            '0' = letter not present
            '1' = letter present but not in correct position
            '2' = letter present and in correct position
    """

    # We use lists to have mutable objects to work with
    outcome = list("-----")
    guess_list = list(guess)
    solution_list = list(solution)

    # Get 0 and 2 first - this manages multiple occurrences of the same letter
    # whereby a letter in the correct position should take precedence
    # over one not in the correct position
    for position in range(5):

        # Letter not present = 0
        if guess_list[position] not in solution_list:
            outcome[position] = "0"
            guess_list[position] = "-"

        # Letter in correct position = 2
        elif guess_list[position] == solution_list[position]:
            outcome[position] = "2"
            solution_list[position] = "-"
            guess_list[position] = "-"

    # Now mop up remaining letters
    for position in range(5):
        if guess_list[position] != "-":
            if guess_list[position] not in solution_list:
                outcome[position] = "0"

            else:
                outcome[position] = "1"
                solution_list[solution_list.index(guess_list[position])] = "-"

    return "".join(outcome)


def _run_tests(
    words: list[str], solutions: list[str], hard: bool
) -> dict[str, TestOutcome]:
    """Run a set of test solves

    Args:
        words: master word list for guesses
        solutions: solutions to find
        hard: True for hard mode

    Returns:
        dict of test outcomes
    """

    # Set up outcomes dict and tally counter
    outcomes = {}
    count = 0

    # Get word scores for the first guess (this will be the same for every test)
    rule_set = RuleSet()
    init_scores = rule_set.score_words(words, words)

    # Set up function for Executor.map()
    testfunc = partial(_test_one, words, init_scores, hard=hard)

    # Hide cursor for running total
    print("\033[?25l", end="")

    # Tests are processor-intensive
    # So multi-processing is used to speed things up
    with ProcessPoolExecutor() as executor:

        for solution, outcome in zip(
            solutions,
            executor.map(testfunc, solutions),
        ):
            outcomes[solution] = outcome
            count += 1
            print(
                f"Test count:   {count}/{len(solutions)} [{int(count*100/len(solutions))}%]",
                end="\r",
            )

    # Restore cursor
    print("\033[?25h", end="")

    return outcomes


def _test_one(
    words: list[str], init_scores: list[WordScore], solution: str, hard: bool = False
) -> TestOutcome:
    """Runs a test solve for a single solution

    Args:
        words: word list to take guesses from
        init_scores: set of word scores for the first guess
        solution: word to find
        hard: True for hard mode, False otherwise (the default)

    Returns a list of dicts with information about each guess:
        "scores": the top 5 scored words as WordScore objects
        "score_count": the number of words in the full word list
        "guess": the word guessed
        "outcome": the outcome when matched against the solution
        "matches": the first 5 remaining matches (in alphabetical order)
        "match_count": the total number of remaining matches

    """

    # Initial match list is full word list
    matches = words

    rule_set = RuleSet()
    guesses = []

    # Cycle through guesses (max 6)
    for guess_number in range(1, 7):

        # For the first guess the word scores are always the same
        if guess_number == 1:
            word_scores = init_scores

        # For other guesses the scored word list needs to be built
        else:
            # Score only matches if (1) this is hard mode, or
            # (2) this is the last guess - this essentially means
            # the Solver has failed and will just guess the match
            # with the highest word frequemcy.
            # Otherwise score all words
            word_scores = rule_set.score_words(
                matches if (hard or guess_number == 6) else words, matches
            )

        # Guess the highest scoring word
        guess = word_scores[0][0]

        # Get outcome, add to ruleset and filter matches
        outcome = _get_outcome(guess, solution)
        rule_set.add_outcome(guess, outcome)
        matches = rule_set.filter_matches(matches)

        # Guess info
        guesses.append(
            GuessOutcome(
                scores=word_scores[:5],
                score_count=len(word_scores),
                guess=guess,
                outcome=outcome,
                matches=matches[:5],
                match_count=len(matches),
                alphabet=rule_set.get_alphabet_status(),
            )
        )

        if not matches or (len(matches) == 1 and guess == solution):
            break

    return guesses
