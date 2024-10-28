# MinesweeperBot
Course _Aineopintojen harjoitustyö - algoritmit ja tekoäly_, University of Helsinki

Note: there are two general versions of Minesweeper: the 'classic' version where the first click is guaranteed to be a number cell with number 0...8, and the so-called 'modern' minesweeper where the first click is guaranteed to be a 0 (meaning, there's an opening guaranteed at the very start).

I had originally thought that these were the other way around, since minesweeper.online is a quite modern site, and I'm too young to have touched the original minesweeper. Hence, thus far (28.10.24), I had used win percentages for the modern version, thinking it was the classic version. Currently running games using the classic version (WIP).

## git cloning

see [how_to_clone.md](how_to_clone.md)

## results (as of 25.10.2024)
[Win_percentages_and_average_time_per_game](./Testing/Win_percentages_and_average_time_per_game.pdf)

Expert games: 
- classic: 33.91% won, average 67 ms/game, n = 68 357, 3.07 guesses/game
- modern: 39.81% won, average 83 ms/game, n = 102 317, 2.68 guesses/game

Intermediate games:
- modern: 83.20% won, average 12 ms/game, n=20 145, 0.73 guesses/game (new)

Beginner games:
- modern: 95.69% won, average 6 ms/game, n=23 474, 0.25 guesses/game (new)

Validity testing: 
[Logic validity testing](./Testing/Logic_validity_testing/Logic_validity_testing.pdf)

Results: no missing logic found after latest fixes (25.10.2024). I will run more tests still.

## Current state (25.10.2024)

Capable of solving all solvable situations, including those that need minecount. 
Capable of guessing, choosing the better alternative from near-front cells or from other cells ('unseen unclicked') based on probabilities from chained equation alt tree building (early) or minecount (worst-case-scenario where normal logic wasn't enough, and minecount is needed, and simple minecount wasn't enough, AND heavy minecount didn't yield new solutions either) and remaining unseen unclicked cells.
I am now using separated sets of equations also for minecount and guessing situations. I'm also using the \[0s, 1s\] compact counting in both non-minecount and minecount situation. I'm now also using `botGame.py`'s `simple_solver()` to get all the obvious solutions out of the way every time before utilizing `CSP_solver_old`, and if that wasn't enough, `CSP_solver` after that, as these two reduce the (separated) equation sets' sizes significantly in many cases. I'm also recognizing situations where minecount cannot possibly help (when both (1) max possible minecount in whole-front is less than the number of remaining mines in the map and not only max front n mines is viable, AND (2) `smallest_n_mines_in_front_alt_solutions + number_of_unclicked_unseen_cells >= n_mines_remaining` ), preventing minecount usage in those cases (if there are no alt solutions with too many mines AND there are no alt solutions with too few mines). In case of minecount, I'm using simple minecount -derived answers only whenever possible, preventing (possibly unneeded use of) heavier minecount in all situations where it is not needed. In cases where it's known that minecount would not help, guessing is done immediately (after not being able to solve variables definitely as 0 or 1 via `chain_link_equations()` and `join_comp_groups_into_solutions()`, which exist before minecount logic).

## Goal
The goal is to implement a bot that's capable of solving all solvable minesweeper situations (done as far as I know) using CSP, which includes handling of minecount situations. Note that my implementations of all code are designed by myself, and I didn't have a source material for the actual implementations (nor do I follow any solver design principles, as I have never read code regarding those). The source that I read partly through (regarding coupled subsets CSP) is Becerra, David J. 2015. Algorithmic Approaches to Playing Minesweeper. Bachelor's thesis, Harvard College (permalink: http://nrs.harvard.edu/urn-3:HUL.InstRepos:14398552).

## Ideas
- implemented in `CSP_solver_old`: subtraction of shorter equations from longer ones could be done before the rest of current `CSP_solver` to reduce the sizes of (separated) eq sets for `CSP_solver`. Overall, so far hybrid solutions and solution space reduction have proven to be the best tools apart from my strategy in `chain_link_equations` which connects one equation alt answers to compatible alt answers from another group, and repeats until all equations have been covered (on-the-go reduction of solutions is done that way)
- implemented: earlier recognition of minecount helpfulness; if the max number of mines near fronts + remaining cells is smaller than remaining minecount, do not even start minecount, as it's impossible in this situation that minecount could solve anything. For this, I needed the max possible number of mines in the front, before the 'minecount' activities would be started normally
- implemented using `sorted()`: try to maximize overlap in `chain_link_equations()` so that a maximum number of impossible alt answers is discarded as soon as possible and/or in total during the equation chain building (I have not verified how much difference the chaining order makes)
- implemented: grouping equations to separated sets; in each set, equations which directly or indirectly share variables with each other - each set has common variables with exactly 0 other sets
- implemented: for each alt solution per equation, discard if it's incompatible with all possible alt solutions from the next equation in the max-overlap equation chain
- implemented: chain link equations with (usually) high overlap regarding shared variables, discarding impossible alt solutions per equation based on this pairing. This builds a chain of equations, which eliminates the need to couple each equation directly to all other equations
- implemented: a timer (20 seconds per `CSP_solver` call) is be used to opt for performance in the worst cases of expert rather than absolute solving and accurate probability calculations
- implemented: in minecount, the moment that all variables have recorded value as both 0 and 1 at least once (i.e. in at least one viable alt solution), then you know that no absolutely solved var exists. This has  sped up the solving logic and the overall time from ~140 ms/expert game to ~77 ms/expert game!
- implemented: ensuring high overlap between each pair of equations in equation chaining in each disjoint subset of equations. This speeds up `join_comp_groups_into_solutions()` also in the slowest cases
