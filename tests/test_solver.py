"""Tests for Solver class"""
# pylint: disable=no-self-use, protected-access, too-few-public-methods

from wordlesolve.ruleset import RuleSet
from wordlesolve.solver import Solver, _get_outcome, _test_one, _run_tests
from wordlesolve.wordlist import WORDLIST


class TestSolver:
    "Tests of Solver class"

    def test_init(self):
        "__init__() method"

        solver = Solver()
        assert solver.words

    def test_filter_words(self):
        "_filter_words() method"

        solver = Solver()
        filtered = solver._filter_words(4.0)
        assert len(filtered) < len(solver.words)


class TestSolve:
    "Test of solve mode"

    def test_solve(self, monkeypatch, capsys):
        "solve() success"

        # mock input
        input_values = ["RATES", "11000", "BRAIN", "02100", "AROMA", "22222", "N"]
        input_iter = (v for v in input_values)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        # solve mode
        solver = Solver()
        solver.solve()
        out = capsys.readouterr().out

        assert "Congratulations - you solved it!" in out
        assert "Hard mode" not in out
        assert "I don't have any suggestions" not in out
        assert "I wasn't able to solve that one" not in out

    def test_hard_mode(self, monkeypatch, capsys):
        "solve() success - hard mode"

        # mock input
        input_values = ["RATES", "22222", "N"]
        input_iter = (v for v in input_values)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        # solve mode
        solver = Solver()
        solver.solve(hard=True)
        out = capsys.readouterr().out

        assert "Hard mode" in out

    def test_no_suggestions(self, monkeypatch, capsys):
        "solve() - no suggestions"

        # mock input - 'QZPTQ' will generate 0 suggestions
        input_values = ["QZPTG", "11111", "GTZPQ", "22222", "N"]
        input_iter = (v for v in input_values)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        # solve mode
        solver = Solver()
        solver.solve()
        out = capsys.readouterr().out

        assert "I don't have any suggestions" in out

    def test_no_solve(self, monkeypatch, capsys):
        "solve() - no solution"

        # mock input - six guesses without success
        input_values = [
            "BRAIN",
            "02100",
            "BRAIN",
            "02100",
            "BRAIN",
            "02100",
            "BRAIN",
            "02100",
            "BRAIN",
            "02100",
            "BRAIN",
            "02100",
            "N",
        ]
        input_iter = (v for v in input_values)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        # solve mode
        solver = Solver()
        solver.solve()
        out = capsys.readouterr().out

        assert "I wasn't able to solve that one" in out


class TestPlay:
    "Tests of play mode"

    def test_play(self, monkeypatch, capsys):
        "play() guessed correctly"

        # mock random word
        monkeypatch.setattr("random.choice", lambda _: "HAPPY")

        # mock input
        input_values = ["HIPPY", "TULIP", "HAPPY", "N"]
        input_iter = (v for v in input_values)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        # play mode
        solver = Solver()
        solver.play()
        out = capsys.readouterr().out
        assert "Congratulations - you solved it!" in out
        assert "Better luck next time!" not in out
        assert "use all revealed hints" not in out
        assert "Hard mode" not in out
        assert "That is not a valid word" not in out

    def test_hard_mode(self, monkeypatch, capsys):
        "Hard mode"

        # mock random word
        monkeypatch.setattr("random.choice", lambda _: "HAPPY")

        # mock input
        input_values = ["HIPPY", "TULIP", "HAPPY", "N"]
        input_iter = (v for v in input_values)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        # play mode
        solver = Solver()
        solver.play(hard=True)
        out = capsys.readouterr().out
        assert "use all revealed hints" in out
        assert "Hard mode" in out

    def test_invalid_word(self, monkeypatch, capsys):
        "Enter invalid word"

        # mock random word
        monkeypatch.setattr("random.choice", lambda _: "HAPPY")

        # mock input
        input_values = ["HIPPY", "XCFPT", "HAPPY", "N"]
        input_iter = (v for v in input_values)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        # play mode
        solver = Solver()
        solver.play()
        out = capsys.readouterr().out
        assert "That is not a valid word" in out

    def test_solution_not_found(self, monkeypatch, capsys):
        "Solution not found"

        # mock random word
        monkeypatch.setattr("random.choice", lambda _: "HAPPY")

        # mock input - 6 incorrect guesses
        input_values = ["HIPPY", "GREAT", "BRING", "BRAKE", "BLING", "ALERT", "N"]
        input_iter = (v for v in input_values)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        # play mode
        solver = Solver()
        solver.play()
        out = capsys.readouterr().out
        assert "Congratulations - you solved it!" not in out
        assert "Better luck next time!" in out


class TestTest:
    "Solver.test() and related functions"

    def test_test_one(self):
        "_test_one() function"

        # Run a single test solve
        guesses = _test_one(
            WORDLIST, RuleSet().score_words(WORDLIST, WORDLIST), "SHAKE"
        )

        # Returned list has one element per guess
        assert len(guesses) < 7
        final = guesses[-1]
        assert final.guess == "SHAKE"
        assert final.outcome == "22222"

    def test_test_one_hard(self):
        "hard mode"

        # Run a single test solve
        guesses = _test_one(
            WORDLIST, RuleSet().score_words(WORDLIST, WORDLIST), "SHAKE", hard=True
        )

        # Returned list has one element per guess
        assert len(guesses) < 7
        final = guesses[-1]
        assert final.guess == "SHAKE"
        assert final.outcome == "22222"

    def test_run_tests(self, capsys):
        "_run_tests() function"

        # Run 3 tests
        solutions = ["SHAKE", "CYNIC", "CAULK"]
        outcomes = _run_tests(WORDLIST, solutions, False)

        # Outcomes dict is returned
        assert len(outcomes) == 3
        assert all(key in outcomes for key in solutions)
        assert all(len(value) < 7 for value in outcomes.values())

        # Console output
        out = capsys.readouterr().out
        assert "3/3 [100%]" in out

    def test_solver_test(self):
        "Solver.test() method"

        solver = Solver()

        # No return value
        assert solver.test() is None

        # With return value = outcomes dict
        outcomes = solver.test(count=3, retval=True)
        assert len(outcomes) == 3

    def test_solutions(self):
        "solutions argument"

        solver = Solver()
        outcomes = solver.test(solutions=["SHAKE", "CYNIC", "CAULK"], retval=True)
        assert len(outcomes) == 3

        # Invalid words are filtered out
        outcomes = solver.test(solutions=["SHAKE", "CYNIC", "CAULK", "X"], retval=True)
        assert len(outcomes) == 3

    def test_solutions_file(self):
        "filename argument"

        solver = Solver()
        outcomes = solver.test(filename="tests/test_solutions.txt", retval=True)
        assert len(outcomes) == 10

    def test_file_error(self, capsys):
        "filename argument supplies invalid filename"

        solver = Solver()
        solver.test(filename="nosuchfile.txt")

        out = capsys.readouterr().out
        assert "Unable to read solutions file" in out

    def test_empty_file(self, capsys):
        "filename argument supplies empty file"

        solver = Solver()
        solver.test(filename="tests/test_empty.txt")

        out = capsys.readouterr().out
        assert "File has no valid solutions" in out


class TestGetOutcome:
    "_get_outcome() function"

    def test_get_outcome(self):
        "get_outcome() function"

        assert _get_outcome("DARES", "CYNIC") == "00000"
        assert _get_outcome("COLIN", "CYNIC") == "20021"
        assert _get_outcome("CACKE", "CYNIC") == "20100"
        assert _get_outcome("CCCKE", "CYNIC") == "21000"
        assert _get_outcome("CCCCC", "CYNIC") == "20002"
        assert _get_outcome("CYNIC", "CYNIC") == "22222"
