# wordlesolve
> wordlesolve solves Wordle!

*wordlesolve* will solve almost any Wordle puzzle within six guesses. Just follow the suggestions and type in the results.

## Installation

```sh
pip install wordlesolve
```

## Usage

### Solve mode

```sh
python3 -m wordlesolve
```
or
```sh
>>> from wordlesolve import Solver
>>> solver = Solver()
>>> solver.solve()
```

*wordlesolve* gives you up to five suggestions for each guess.
Type in the guess you use and the outcome Wordle gives for each letter: 0 for grey, 1 for yellow, 2 for green.

For example if you guess RATES and get

![Screenshot](img/rates.png)

enter:
* Your guess: RATES
* Outcome: 02100

*wordlesolve* will use that information to suggest some more guesses, getting you closer to the solution each time!

![Screenshot](img/solvemode.png)

### Play mode

*wordlesolve* also includes a play mode - a console-based Wordle clone. Not nearly as good as [the real thing](https://www.nytimes.com/games/wordle/index.html) but fun to practise!

```sh
python3 -m wordlesolve -p
```
or
```sh
>>> from wordlesolve import Solver
>>> solver = Solver()
>>> solver.play()
```

![Screenshot](img/playmode.png)

### Test mode

Also included is a test mode - this was originally intended to test the algorithm during development. Test mode runs the solve algorithm against any number of solutions, either provided or randomly selected from the built-in database, and provides information on how quickly each was solved.

```sh
python3 -m wordlesolve -t -c 10 -v
```
or
```sh
>>> from wordlesolve import Solver
>>> solver = Solver()
>>> solver.test(count=10, verbosity=1)
```

![Screenshot](img/testmode.png)

### Options
Each *wordlesolve* mode takes a number of configuration options, either as command line switches or keyword argments.

<table>
    <tr>
        <th>Command line</th>
        <th>Keyword</th>
        <th>Type</th>
        <th>Description</th>
        <th>Solve mode</th>
        <th>Play mode</th>
        <th>Test mode</th>
    </tr>
    <tr>
        <td>--hard</td>
        <td>hard</td>
        <td>bool</td>
        <td>Use hard mode</td>
        <td>yes</td>
        <td>yes</td>
        <td>yes</td>
    </tr>
    <tr>
        <td>-g --guessfreq</td>
        <td>guess_freq</td>
        <td>float</td>
        <td>Minimum word frequency allowed for guesses</td>
        <td>yes</td>
        <td>yes</td>
        <td>yes</td>
    </tr>
    <tr>
        <td>--solutionfreq</td>
        <td>solution_freq</td>
        <td>float</td>
        <td>Minimum word frequency allowed for solutions</td>
        <td>no</td>
        <td>yes</td>
        <td>yes</td>
    </tr>
    <tr>
        <td>-v --verbosity</td>
        <td>verbosity</td>
        <td>count (cl) int (kw)</td>
        <td>Verbosity level for test results</td>
        <td>no</td>
        <td>no</td>
        <td>yes</td>
    </tr>
    <tr>
        <td>--solutions</td>
        <td>solutions</td>
        <td>list[str]</td>
        <td>Solutions to test</td>
        <td>no</td>
        <td>no</td>
        <td>yes</td>
    </tr>
    <tr>
        <td>-f --file</td>
        <td>filename</td>
        <td>str</td>
        <td>Path to a text file containing solutions to test (one word per line)</td>
        <td>no</td>
        <td>no</td>
        <td>yes</td>
    </tr>
</table>

## Release History

* 0.0.1
    * Work in progress

## Meta

Neil Martin – neilmartin12@me.com

Distributed under the MIT license. See ``LICENSE`` for more information.

[https://github.com/neilmartin12/wordlesolve](https://github.com/neilmartin12/wordlesolve)

