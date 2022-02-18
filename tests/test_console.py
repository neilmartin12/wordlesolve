"""Tests for ruleset module"""
# pylint: disable=no-self-use, redefined-outer-name

import string

import colorama as cr  # type: ignore
import pytest

from wordlesolve.console import (
    _letter_row,
    _print_word_row,
    _validate_input,
    COLORS,
    display_test_outcomes,
    get_guess_input,
    get_outcome_input,
    get_yn_input,
    GuessOutcome,
    print_alphabet,
    print_word,
)
from wordlesolve.ruleset import WordScore


class TestPrintWord:
    "Tests of play mode console word printing"

    def test_letter_row_content(self):
        "Letter row - test content"

        # Top row = "---"
        retval = _letter_row("A", 0, 0)
        assert "---" in retval
        assert "A" not in retval

        # Middle row = "| A |"
        retval = _letter_row("A", 0, 1)
        assert "| A |" in retval
        assert "---" not in retval

        # Bottom row = "---"
        retval = _letter_row("A", 0, 2)
        assert "---" in retval
        assert "A" not in retval

    def test_letter_row_colors(self):
        "Letter row - test colors"

        # 0 = red
        retval = _letter_row("A", 0, 1)
        assert cr.Fore.RED in retval
        assert all(color not in retval for color in [cr.Fore.YELLOW, cr.Fore.GREEN])

        # 1 = yellow
        retval = _letter_row("A", 1, 1)
        assert cr.Fore.YELLOW in retval
        assert all(color not in retval for color in [cr.Fore.RED, cr.Fore.GREEN])

        # 2 = green
        retval = _letter_row("A", 2, 1)
        assert cr.Fore.GREEN in retval
        assert all(color not in retval for color in [cr.Fore.RED, cr.Fore.YELLOW])

    def test_print_word_row(self, capsys):
        "print_word_row() function"

        # Middle row should contain all letters
        _print_word_row("ABCDE", "00000", 1)
        out = capsys.readouterr().out
        assert all(letter in out for letter in "ABCDE")
        assert all(letter not in out for letter in "FGHIJ")

        # Top / bottom row should contain no letters
        _print_word_row("ABCDE", "00000", 0)
        out = capsys.readouterr().out
        assert all(letter not in out for letter in "ABCDE")

    def test_print_word(self, capsys):
        "print_word() function"

        # Output should contain all letters
        print_word("ABCDE", "00000")
        out = capsys.readouterr().out
        assert all(letter in out for letter in "ABCDE")
        assert all(letter not in out for letter in "FGHIJ")


class TestPrintAlphabet:
    "print_alphabet() function"

    def test_print_alphabet(self, capsys):
        "print_alphabet() function"

        # Start with all unknown status
        status = {letter: -1 for letter in string.ascii_uppercase}
        print_alphabet(status)
        out = capsys.readouterr().out
        assert COLORS[-1] in out
        assert all(COLORS[n] not in out for n in (0, 1, 2))

        # Add an excluded letter
        status["A"] = 0
        print_alphabet(status)
        out = capsys.readouterr().out
        assert all(COLORS[n] in out for n in (-1, 0))
        assert all(COLORS[n] not in out for n in (1, 2))

        # Add a known letter with unknown position
        status["B"] = 1
        print_alphabet(status)
        out = capsys.readouterr().out
        assert all(COLORS[n] in out for n in (-1, 0, 1))
        assert COLORS[2] not in out

        # Add a known letter with known position
        status["C"] = 2
        print_alphabet(status)
        out = capsys.readouterr().out
        assert all(COLORS[n] in out for n in (-1, 0, 1, 2))

    def test_sep(self, capsys):
        "print_alphabet() sep argument"

        status = {letter: -1 for letter in string.ascii_uppercase}

        # Default separator is space character
        print_alphabet(status)
        out = capsys.readouterr().out
        assert " " in out
        assert "-" not in out

        # Change to dash
        print_alphabet(status, sep="-")
        out = capsys.readouterr().out
        assert "-" in out
        assert " " not in out

        # Remove separator
        print_alphabet(status, sep="")
        out = capsys.readouterr().out
        assert "-" not in out
        assert " " not in out


class TestTestOutcome:
    "Tests of test outcome console output"

    def test_display_test_outcomes(self, capsys, happy_test_outcome):
        "Display test outcome for solutions ['HAPPY', 'ABCDE']"

        display_test_outcomes(happy_test_outcome, 2.7, False, 0)
        out = capsys.readouterr().out
        assert "Words tested: 2" in out
        assert "Total time:   00:02" in out
        assert "Solved in 4:  1 [50%]" in out
        assert "Solved in 5:  0 [ 0%]" in out
        assert "Unsolved:     1" in out
        assert "Unsolved:     ABCDE" in out
        assert "solved in 4 guesses" not in out
        assert "not solved" not in out
        assert "hard mode" not in out

    def test_display_test_outcomes_verbosity_1(self, capsys, happy_test_outcome):
        "Test outcome with verbosity 1"

        display_test_outcomes(happy_test_outcome, 2.7, False, 1)
        out = capsys.readouterr().out

        # Includes info on guesses to solve
        assert "solved in 4 guesses" in out
        assert "not solved" in out
        assert "Outcome: 22222" not in out
        assert "Matches: 0" not in out

    def test_display_test_outcomes_verbosity_2(self, capsys, happy_test_outcome):
        "Test outcome with verbosity 2"

        display_test_outcomes(happy_test_outcome, 2.7, False, 2)
        out = capsys.readouterr().out

        # Includes info on guesses to solve
        assert "Matches: 0" in out
        assert "Outcome: 22222" in out


class TestValidateInput:
    "Tests of input validation functions"

    def test_validate_input(self):
        "_validate_input() function"

        # Valid
        assert _validate_input("HAPPY", 5, string.ascii_letters)

        # Wrong length
        assert not _validate_input("HAPP", 5, string.ascii_letters)

        # Invalid characters
        assert not _validate_input("01210", 5, string.ascii_letters)

    def test_get_outcome_input(self, monkeypatch, capsys):
        "get_outcome_input() function"

        # Valid input - should return original string
        monkeypatch.setattr("builtins.input", lambda _: "00112")

        assert get_outcome_input(11) == "00112"
        out = capsys.readouterr().out
        assert "2 = green" not in out

    def test_get_outcome_input_invalid(self, monkeypatch, capsys):
        "get_outcome_input() function with invalid input"

        # Invalid input - should return second (valid) string
        input_values = ["abcde", "00112"]
        input_iter = (v for v in input_values)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        assert get_outcome_input(11) == "00112"
        out = capsys.readouterr().out
        assert "2 = green" in out

    def test_get_guess_input(self, monkeypatch, capsys):
        "get_guess_input() function"

        # Valid input - should return original string
        monkeypatch.setattr("builtins.input", lambda _: "happy")

        assert get_guess_input() == "HAPPY"
        out = capsys.readouterr().out
        assert "Please enter a five-letter word" not in out

    def test_get_guess_input_invalid(self, monkeypatch, capsys):
        "get_guess_input() function with invalid input"

        # Invalid input - should return second (valid) string
        input_values = ["01210", "HAPPY"]
        input_iter = (v for v in input_values)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        assert get_guess_input() == "HAPPY"
        out = capsys.readouterr().out
        assert "Please enter a five-letter word" in out

    def test_get_yn_input(self, monkeypatch):
        "get_yn_input() function"

        # Valid input - should return original string
        monkeypatch.setattr("builtins.input", lambda _: "y")
        assert get_yn_input("Play again (Y/N)?") == "Y"

    def test_get_yn_input_invalid(self, monkeypatch):
        "get_yn_input() function with invalid input"

        # Invalid input - should return second (valid) string
        input_values = ["xxx", "Y"]
        input_iter = (v for v in input_values)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))
        assert get_yn_input("Play again (Y/N)?") == "Y"


@pytest.fixture
def happy_test_outcome():
    "Actual outcome of test to find solutions ['HAPPY', 'ABCDE']"

    return {
        "HAPPY": [
            GuessOutcome(
                scores=[
                    WordScore(word="TARES", score=34474, frequency=1.9),
                    WordScore(word="LARES", score=34317, frequency=0),
                    WordScore(word="RALES", score=34018, frequency=0),
                    WordScore(word="NARES", score=33738, frequency=0),
                    WordScore(word="RATES", score=33705, frequency=0),
                ],
                score_count=12972,
                guess="TARES",
                outcome="02000",
                matches=["AALII", "BABKA", "BABOO", "BABUL", "BACCA"],
                match_count=402,
                alphabet={
                    "A": 2,
                    "B": -1,
                    "C": -1,
                    "D": -1,
                    "E": 0,
                    "F": -1,
                    "G": -1,
                    "H": -1,
                    "I": -1,
                    "J": -1,
                    "K": -1,
                    "L": -1,
                    "M": -1,
                    "N": -1,
                    "O": -1,
                    "P": -1,
                    "Q": -1,
                    "R": 0,
                    "S": 0,
                    "T": 0,
                    "U": -1,
                    "V": -1,
                    "W": -1,
                    "X": -1,
                    "Y": -1,
                    "Z": -1,
                },
            ),
            GuessOutcome(
                scores=[
                    WordScore(word="LINDY", score=774, frequency=2.84),
                    WordScore(word="LINGY", score=760, frequency=0),
                    WordScore(word="MINCY", score=759, frequency=0),
                    WordScore(word="LINKY", score=758, frequency=0),
                    WordScore(word="MINGY", score=747, frequency=0),
                ],
                score_count=12972,
                guess="LINDY",
                outcome="00002",
                matches=["BACCY", "BAFFY", "BAGGY", "CABBY", "CACKY"],
                match_count=36,
                alphabet={
                    "A": 2,
                    "B": -1,
                    "C": -1,
                    "D": 0,
                    "E": 0,
                    "F": -1,
                    "G": -1,
                    "H": -1,
                    "I": 0,
                    "J": -1,
                    "K": -1,
                    "L": 0,
                    "M": -1,
                    "N": 0,
                    "O": -1,
                    "P": -1,
                    "Q": -1,
                    "R": 0,
                    "S": 0,
                    "T": 0,
                    "U": -1,
                    "V": -1,
                    "W": -1,
                    "X": -1,
                    "Y": 2,
                    "Z": -1,
                },
            ),
            GuessOutcome(
                scores=[
                    WordScore(word="GUMPS", score=63, frequency=1.37),
                    WordScore(word="GUMBO", score=59, frequency=0),
                    WordScore(word="GAMPS", score=58, frequency=0),
                    WordScore(word="GIMPS", score=58, frequency=0),
                    WordScore(word="GIMPY", score=58, frequency=0),
                ],
                score_count=12972,
                guess="GUMPS",
                outcome="00020",
                matches=["HAPPY", "PAPPY", "YAPPY", "ZAPPY"],
                match_count=4,
                alphabet={
                    "A": 2,
                    "B": -1,
                    "C": -1,
                    "D": 0,
                    "E": 0,
                    "F": -1,
                    "G": 0,
                    "H": -1,
                    "I": 0,
                    "J": -1,
                    "K": -1,
                    "L": 0,
                    "M": 0,
                    "N": 0,
                    "O": -1,
                    "P": 2,
                    "Q": -1,
                    "R": 0,
                    "S": 0,
                    "T": 0,
                    "U": 0,
                    "V": -1,
                    "W": -1,
                    "X": -1,
                    "Y": 2,
                    "Z": -1,
                },
            ),
            GuessOutcome(
                scores=[
                    WordScore(word="HAPPY", score=10, frequency=5.35),
                    WordScore(word="PUPPY", score=10, frequency=4.0),
                    WordScore(word="POPPY", score=10, frequency=3.59),
                    WordScore(word="HIPPO", score=10, frequency=3.13),
                    WordScore(word="HIPPY", score=10, frequency=3.0),
                ],
                score_count=12972,
                guess="HAPPY",
                outcome="22222",
                matches=["HAPPY"],
                match_count=1,
                alphabet={
                    "A": 2,
                    "B": -1,
                    "C": -1,
                    "D": 0,
                    "E": 0,
                    "F": -1,
                    "G": 0,
                    "H": 2,
                    "I": 0,
                    "J": -1,
                    "K": -1,
                    "L": 0,
                    "M": 0,
                    "N": 0,
                    "O": -1,
                    "P": 2,
                    "Q": -1,
                    "R": 0,
                    "S": 0,
                    "T": 0,
                    "U": 0,
                    "V": -1,
                    "W": -1,
                    "X": -1,
                    "Y": 2,
                    "Z": -1,
                },
            ),
        ],
        "ABCDE": [
            GuessOutcome(
                scores=[
                    WordScore(word="TARES", score=34474, frequency=1.9),
                    WordScore(word="LARES", score=34317, frequency=0),
                    WordScore(word="RALES", score=34018, frequency=0),
                    WordScore(word="NARES", score=33738, frequency=0),
                    WordScore(word="RATES", score=33705, frequency=0),
                ],
                score_count=12972,
                guess="TARES",
                outcome="01010",
                matches=["ABEAM", "ABELE", "ABIDE", "ABODE", "ABOVE"],
                match_count=271,
                alphabet={
                    "A": 1,
                    "B": -1,
                    "C": -1,
                    "D": -1,
                    "E": 1,
                    "F": -1,
                    "G": -1,
                    "H": -1,
                    "I": -1,
                    "J": -1,
                    "K": -1,
                    "L": -1,
                    "M": -1,
                    "N": -1,
                    "O": -1,
                    "P": -1,
                    "Q": -1,
                    "R": 0,
                    "S": 0,
                    "T": 0,
                    "U": -1,
                    "V": -1,
                    "W": -1,
                    "X": -1,
                    "Y": -1,
                    "Z": -1,
                },
            ),
            GuessOutcome(
                scores=[
                    WordScore(word="ALANE", score=577, frequency=1.41),
                    WordScore(word="LEONE", score=550, frequency=0),
                    WordScore(word="PLANE", score=546, frequency=0),
                    WordScore(word="VEALE", score=543, frequency=0),
                    WordScore(word="NEELE", score=542, frequency=0),
                ],
                score_count=12972,
                guess="ALANE",
                outcome="20002",
                matches=["ABIDE", "ABODE", "ABOVE", "ADOBE", "ADOZE"],
                match_count=16,
                alphabet={
                    "A": 2,
                    "B": -1,
                    "C": -1,
                    "D": -1,
                    "E": 2,
                    "F": -1,
                    "G": -1,
                    "H": -1,
                    "I": -1,
                    "J": -1,
                    "K": -1,
                    "L": 0,
                    "M": -1,
                    "N": 0,
                    "O": -1,
                    "P": -1,
                    "Q": -1,
                    "R": 0,
                    "S": 0,
                    "T": 0,
                    "U": -1,
                    "V": -1,
                    "W": -1,
                    "X": -1,
                    "Y": -1,
                    "Z": -1,
                },
            ),
            GuessOutcome(
                scores=[
                    WordScore(word="AMIDO", score=38, frequency=1.77),
                    WordScore(word="AZIDO", score=38, frequency=1.24),
                    WordScore(word="IMIDO", score=38, frequency=0.0),
                    WordScore(word="AVOID", score=36, frequency=0),
                    WordScore(word="MYOID", score=36, frequency=0),
                ],
                score_count=12972,
                guess="AMIDO",
                outcome="20020",
                matches=[],
                match_count=0,
                alphabet={
                    "A": 2,
                    "B": -1,
                    "C": -1,
                    "D": 2,
                    "E": 2,
                    "F": -1,
                    "G": -1,
                    "H": -1,
                    "I": 0,
                    "J": -1,
                    "K": -1,
                    "L": 0,
                    "M": 0,
                    "N": 0,
                    "O": 0,
                    "P": -1,
                    "Q": -1,
                    "R": 0,
                    "S": 0,
                    "T": 0,
                    "U": -1,
                    "V": -1,
                    "W": -1,
                    "X": -1,
                    "Y": -1,
                    "Z": -1,
                },
            ),
        ],
    }
