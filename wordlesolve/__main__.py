"""Entry point for wordlesolve package

>>> python3 -m wordlesolve [options]

usage: wordlesolve [-h] [-p] [-s] [-t] [-g GUESSFREQ] [--solutionfreq SOLUTIONFREQ]
                   [-c TESTCOUNT] [--solutions [SOLUTIONS ...]] [-f FILE] [-v] [--hard]

wordlesolve solves Wordle!

optional arguments:
  -h, --help            show this help message and exit
  -p, --play            play Wordle
  -s, --solve           solve Wordle (the default)
  -t, --test            run test solves
  -g GUESSFREQ, --guessfreq GUESSFREQ
                        set minimum guess frequency
  --solutionfreq SOLUTIONFREQ
                        set minimum solution frequency (test mode only)
  -c TESTCOUNT, --testcount TESTCOUNT
                        number of tests to run (test mode only)
  --solutions [SOLUTIONS ...]
                        5-letter solutions to test (test mode only)
  -f FILE, --file FILE  text file with 5-letter solutions to test (one word per line)
  -v, --verbosity       increase test mode verbosity
  --hard                enable hard mode

"""

import argparse
import sys

from wordlesolve import Solver


def main(clargs: argparse.Namespace):
    """Run the Solver

    Converts command line arguments into kwargs,
    creates a Solver instance and calls the appropriate method:
        Solver.solve() / Solver.play() / Solver.test()
        with appropriate arguments

    Args:
        clargs: command line arguments as returned by argparse.parse_args()

    """

    solver = Solver()

    # kwargs from command line
    kwargs = {"hard": clargs.hard}

    # guess_freq is common to all modes
    if clargs.guessfreq is not None:
        kwargs["guess_freq"] = float(clargs.guessfreq)

    # Some args don't apply to solve mode
    if clargs.play or clargs.test:
        if clargs.solutionfreq is not None:
            kwargs["solution_freq"] = float(clargs.solutionfreq)

        # play mode
        if clargs.play:
            solver.play(**kwargs)

        # test mode - additional command line arguments
        else:

            # verbosity
            kwargs["verbosity"] = int(clargs.verbosity)

            # test coune
            if clargs.testcount is not None:
                kwargs["count"] = int(clargs.testcount)

            # solutions
            if clargs.solutions is not None:
                kwargs["solutions"] = [word.upper() for word in clargs.solutions]

            # solutions file
            if clargs.file is not None:
                kwargs["filename"] = clargs.file

            solver.test(**kwargs)

    # solve mode
    else:
        solver.solve(**kwargs)


def parse_args(args: list[str]) -> argparse.Namespace:
    """Parse command line arguments

    Args:
        args: sys.argv[1:]

    Returns:
        Namespace object containing parsed argument data
    """

    # Build command line options
    parser = argparse.ArgumentParser(
        prog="wordlesolve", description="wordlesolve solves Wordle!"
    )

    # play mode
    parser.add_argument("-p", "--play", help="play Wordle", action="store_true")

    # solve mode
    parser.add_argument(
        "-s",
        "--solve",
        help="solve Wordle (the default)",
        action="store_true",
        default=True,
    )

    # test mode
    parser.add_argument("-t", "--test", help="run test solves", action="store_true")

    # guess frequency
    parser.add_argument("-g", "--guessfreq", help="set minimum guess frequency")

    # solution frequency
    parser.add_argument(
        "--solutionfreq", help="set minimum solution frequency (test mode only)"
    )

    # test count
    parser.add_argument(
        "-c", "--testcount", help="number of tests to run (test mode only)"
    )

    # solutions
    parser.add_argument(
        "--solutions", help="5-letter solutions to test (test mode only)", nargs="*"
    )

    # solutions file
    parser.add_argument(
        "-f",
        "--file",
        help="text file with 5-letter solutions to test (one word per line)",
    )

    # verbosity
    parser.add_argument(
        "-v",
        "--verbosity",
        help="increase test mode verbosity",
        action="count",
        default=0,
    )

    # hard mode
    parser.add_argument("--hard", help="enable hard mode", action="store_true")

    return parser.parse_args(args)


if __name__ == "__main__":  # pragma: no cover
    main(parse_args(sys.argv[1:]))
