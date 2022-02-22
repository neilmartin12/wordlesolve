"""Tests for __main__.py"""
# pylint: disable=no-self-use

from argparse import Namespace

from wordlesolve.__main__ import main, parse_args


class TestMain:
    "Tests of main() function - checking correct arguments are sent to correct method"

    def test_solve(self, monkeypatch, capsys):
        "default values should run solve mode"

        # monkeypatch will print kwargs to stdout
        monkeypatch.setattr(
            "wordlesolve.solver.Solver.solve", lambda _, **kwargs: print(kwargs)
        )

        # Run main() function with default args
        args = Namespace(hard=False, guessfreq=None, play=False, test=False)
        main(args)
        out = capsys.readouterr().out
        assert "'hard': False" in out
        assert "guess_freq" not in out

        # test different args
        args = Namespace(hard=True, guessfreq=1.5, play=False, test=False)
        main(args)
        out = capsys.readouterr().out
        assert "'hard': True" in out
        assert "'guess_freq': 1.5" in out

    def test_play(self, monkeypatch, capsys):
        "test args sent to play mode"

        # monkeypatch will print kwargs to stdout
        monkeypatch.setattr(
            "wordlesolve.solver.Solver.play", lambda _, **kwargs: print(kwargs)
        )

        # Run main() function calling Solver.play()
        args = Namespace(
            hard=False, guessfreq=None, play=True, test=False, solutionfreq=None
        )
        main(args)
        out = capsys.readouterr().out
        assert "'solution_freq'" not in out

        # add solutionfreq argument
        args = Namespace(
            hard=False, guessfreq=None, play=True, test=False, solutionfreq=4.0
        )
        main(args)
        out = capsys.readouterr().out
        assert "'solution_freq': 4.0" in out

    def test_test(self, monkeypatch, capsys):
        "test args sent to test mode"

        # monkeypatch will print kwargs to stdout
        monkeypatch.setattr(
            "wordlesolve.solver.Solver.test", lambda _, **kwargs: print(kwargs)
        )

        # Run main() function calling Solver.test()
        args = Namespace(
            hard=False,
            guessfreq=None,
            play=False,
            test=True,
            solutionfreq=None,
            verbosity="1",
            testcount=None,
            solutions=["HAPPY"],
            file=None,
        )
        main(args)
        out = capsys.readouterr().out
        assert "'verbosity': 1" in out
        assert "'solutions': ['HAPPY']" in out

        # with testcount arg
        args = Namespace(
            hard=False,
            guessfreq=None,
            play=False,
            test=True,
            solutionfreq=None,
            verbosity="1",
            testcount="10",
            solutions=None,
            file=None,
        )
        main(args)
        out = capsys.readouterr().out
        assert "'count': '10'" in out

    def test_file(self, monkeypatch, capsys):
        "test solutions file"

        # monkeypatch will print kwargs to stdout
        monkeypatch.setattr(
            "wordlesolve.solver.Solver.test", lambda _, **kwargs: print(kwargs)
        )

        # Run main() function calling Solver.test() with file argument
        args = Namespace(
            hard=False,
            guessfreq=None,
            play=False,
            test=True,
            solutionfreq=None,
            verbosity="1",
            testcount=None,
            solutions=None,
            file="tests/test_solutions.txt",
        )
        main(args)
        out = capsys.readouterr().out
        assert "'filename': 'tests/test_solutions.txt'" in out


class TestParseArgs:
    "Test parse_args() function"

    def test_default(self):
        "Test default (no arguments)"

        args = parse_args([])
        assert args.solve
        assert not args.play
        assert not args.test
        assert args.verbosity == 0
        assert not args.hard

    def test_hard(self):
        "hard mode"

        args = parse_args(["--hard"])
        assert args.solve
        assert args.hard

    def test_play(self):
        "play mode"

        args = parse_args(["-p", "-g", "1.5", "--solutionfreq", "2.5"])
        assert args.play
        assert args.guessfreq == "1.5"
        assert args.solutionfreq == "2.5"

    def test_test(self):
        "test mode"

        args = parse_args(["-t", "-c", "10", "-vv"])
        assert args.test
        assert args.testcount == "10"
        assert args.verbosity == 2

    def test_solutions(self):
        "test solutions list"

        args = parse_args(["-t", "--solutions", "HAPPY", "BREAK", "AARGH"])
        assert args.solutions == ["HAPPY", "BREAK", "AARGH"]

    def test_file(self):
        "test solutions filename"

        args = parse_args(["-t", "-f", "solutions.txt"])
        assert args.file == "solutions.txt"
