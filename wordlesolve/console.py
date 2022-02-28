"""Functions to manage console input and output

Classes:
    GuessOutcome: outcome of a single guess

Types:
    TestOutcome: list[GuessOutcomes]

Output functions:
    display_test_outcome(outcomes, time, hard, verbosity): display the outcome of a test solve
    get_printable_alphabet(status, sep=" "): returns the alphabet color-coded by status
    print_alphabet(status, sep=" "): prints the alphabet color-coded by status
    print_word(word, outcome): play mode - print word to terminal

Input functions:
    get_guess_input(width=0): obtains valid guess from the user
    get_outcome_input(width): obtains valid outcome from the user
    get_yn_input(prompt): obtains y/n input from the user

"""

import string
from typing import NamedTuple

import colorama as cr  # type: ignore

from .ruleset import WordScore

COLORS = {
    -1: cr.Fore.WHITE,
    0: cr.Style.BRIGHT + cr.Fore.RED,
    1: cr.Style.BRIGHT + cr.Fore.YELLOW,
    2: cr.Style.BRIGHT + cr.Fore.GREEN,
}


class GuessOutcome(NamedTuple):
    """Outcome of a single guess"""

    scores: list[WordScore]  # Top 5 scoring words
    score_count: int  # Total number of words scored
    guess: str  # Word guessed
    outcome: str  # Outcome string ('01100' etc.)
    matches: list[str]  # First five matches after this guess
    match_count: int  # Total number of matches remaining
    alphabet: dict[str, int]  # Alphabet status


TestOutcome = list[GuessOutcome]


def print_word(word: str, outcome: str):
    """Play mode: print word to terminal

    Letters are printed across three rows,
    boxed in by | and - characters.

    Letters are color coded as per the outcome:
        RED if not present in the solution
        YELLOW if present but not in the correct position
        GREEN if present and in the correct position

    Args:
        word: word to print
        outcome: 5-character outcome string e.g. '01210'

    """
    for row in range(3):
        _print_word_row(word, outcome, row)


def _print_word_row(word: str, outcome: str, row: int):
    """Play mode: print single row for this word

    Args:
        word: word to print
        outcome: 5-character outcome string e.g. '01210'
        row index to print (0-2)
    """
    print(
        "  ".join(
            (
                _letter_row(letter, int(status), row)
                for letter, status in zip(word, outcome)
            )
        )
    )


def _letter_row(letter: str, status: int, row: int) -> str:
    """Play mode: returns single row for a single letter

    Args:
        letter: letter to print
        status: outcome status (0/1/2)
        row: row index to print (0-2)

    """
    return COLORS[status] + (f"| {letter} |" if row == 1 else " --- ")


def print_alphabet(status: dict[str, int], sep: str = " "):
    """Prints the alphabet color-coded by status

    Args:
        status:
            dict with one key per letter, the value is one of:
                -1: letter status unknown
                 0: letter is known not to be in the solution
                 1: letter is known to be in the solution but its position is not known
                 2: letter is known to be in the solution and its position is also known

        sep:
            string to place between letters (default is ASCII space)
    """

    print(get_printable_alphabet(status, sep))


def get_printable_alphabet(status: dict[str, int], sep: str = " ") -> str:
    """Returns the alphabet color-coded by status

    Args:
        status:
            dict with one key per letter, the value is one of:
                -1: letter status unknown
                 0: letter is known not to be in the solution
                 1: letter is known to be in the solution but its position is not known
                 2: letter is known to be in the solution and its position is also known

        sep:
            string to place between letters (default is ASCII space)
    """

    return sep.join(
        ((COLORS[status[letter]] + letter) for letter in string.ascii_uppercase)
    )


def display_test_outcomes(
    outcomes: dict[str, TestOutcome], time: float, hard: bool, verbosity: int
):
    """Display the outcome of a test run

    Args:
        outcomes: test outcomes dict
        time: time taken to run tests
        hard: True for hard mode
        verbosity: level of output (0-2)
    """

    # Get the tally of guesses taken
    guess_counter = {value: 0 for value in range(1, 7)}
    unsolved = []
    for word, guesses in outcomes.items():
        if guesses[-1].guess == word:
            guess_counter[len(guesses)] += 1
        else:
            unsolved.append(word)

    # Print test output
    print()
    print(f"Words tested: {len(outcomes)}{' (hard mode)' if hard else ''}")
    print(f"Total time:   {int(time/60):02d}:{int(time % 60):02d}")
    print()

    # Print tally of number of guesses required to solve
    # Right-align values and percentages
    maxval = max(guess_counter.values())
    maxlenv = len(str(maxval))
    maxlenp = len(str(int(maxval * 100 / len(outcomes))))

    # Print guess tally
    for key, value in guess_counter.items():
        percent = f"[{str(int(value*100/len(outcomes))).rjust(maxlenp)}%]"
        print(f"Solved in {key}:  {str(value).rjust(maxlenv)} {percent}")

    # Print unsolved total and words
    percent = f"[{str(int(len(unsolved)*100/len(outcomes))).rjust(maxlenp)}%]"
    print(f"Unsolved:     {str(len(unsolved)).rjust(maxlenv)} {percent}")
    if unsolved and verbosity == 0:
        print(f"Unsolved:     {', '.join(sorted(unsolved))}")

    # More detailed output as required
    if verbosity:
        _verbose_test_outcomes(outcomes, unsolved, verbosity)

    print("\n")


def _verbose_test_outcomes(
    outcomes: dict[str, TestOutcome], unsolved: list[str], verbosity: int
):
    """Display verbose test outcome

    Args:
        outcomes: test outcomes data
        unsolved: list of unsolved words
        verbosity: level of output (1 or 2)
    """

    print()

    # Verbosity >= 1: show guesses for each word
    for word in sorted(outcomes.keys()):
        guesses = outcomes[word]
        outcome_str = (
            "not solved" if word in unsolved else f"solved in {len(guesses)} guesses"
        )
        guess_list = ", ".join(guess.guess for guess in guesses)
        print(
            f"{cr.Fore.GREEN}{word}{cr.Style.RESET_ALL}: {outcome_str} ({guess_list})"
        )

        # Verbosity == 2: list out matches and scores
        if verbosity > 1:
            for guess_number, guess in enumerate(guesses):
                print()

                # Guess number
                print(f"Guess {guess_number+1}")
                score_str = ", ".join(
                    [
                        score[0]
                        + " ("
                        + str(score[1])
                        + ("/" + str(score[2]) if score[2] else "")
                        + ")"
                        for score in guess.scores
                    ]
                )

                # Word scores
                print(
                    "Scores:  "
                    + score_str
                    + (", ..." if guess.score_count > len(guess.scores) else "")
                )

                # Guess and outcome
                print("Guess:   " + guess.guess)
                print("Outcome: " + guess.outcome)

                # If not correctly guessed show remaining matches and alphabet status
                if guess.outcome != "22222":

                    # Matches
                    print(
                        "Matches: "
                        + str(guess.match_count)
                        + " ("
                        + ", ".join((match for match in guess.matches))
                        + (", ..." if guess.match_count > len(guess.matches) else "")
                        + ")"
                    )

                    # Alphabet
                    print("Letters: " + get_printable_alphabet(guess.alphabet))

            print("\n")


def get_yn_input(prompt: str) -> str:
    """Obtains y/n input from the user via builtins.input() function

    Only accepts input with one character Y/y/N/n
    Redisplays prompt until valid input is received.

    Args:
        prompt: input prompt

    Returns the validated response in upper case (Y or N)
    """

    # Loop until valid input
    while True:

        # Get input
        response = input(prompt)

        # Return if valid
        if _validate_input(response, 1, "YyNn"):
            return response.upper()


def get_guess_input(width: int = 0) -> str:
    """Obtains valid guess from the user via builtins.input() function

    Only accepts input with five characters a-z/A-Z.
    Displays a help message if invalid input is received.

    Args:
        width: input prompt will be left justified in this width

    Returns the validated guess string
    """

    # Loop until valid input
    while True:

        # Get input
        guess = input(("Your guess: ").ljust(width))

        # Return if valid
        if _validate_input(guess, 5, string.ascii_letters):
            return guess.upper()

        # Help text if invalid
        print("Please enter a five-letter word.")


def get_outcome_input(width: int) -> str:
    """Obtains valid outcome from the user via builtins.input() function

    Only accepts input with five characters 0-2.
    Displays a help message if invalid input is received.

    Args:
        width: input prompt will be left justified in this width

    Returns the validated outcome string
    """

    # Loop until valid input
    while True:

        # Get input
        outcome = input(("Outcome:").ljust(width))

        # Return if valid
        if _validate_input(outcome, 5, "012"):
            return outcome

        # Help text if invalid
        print("2 = green | 1 = yellow | 0 = grey")


def _validate_input(user_input: str, length: int, valid_chars: str) -> bool:
    """Validates user input

    Args:
        user_input: input string to validate
        length: acceptable length
        valid_chars: acceptable characters

    Returns True if user_input is valid, False otherwise.
    """
    return len(user_input) == length and all(
        letter in valid_chars for letter in user_input
    )
