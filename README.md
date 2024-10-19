# MinesweeperBot
Course _Aineopintojen harjoitustyö - algoritmit ja tekoäly_, University of Helsinki

## git cloning

see 'how_to_clone.md'

## results (as of 19.10.2024)
Out of the 15407 expert games so far, 38,40 % have been solved.
The algorithm only stalls in the worst situations (0.04% of all games after the improvements so far). This could be circumvented by a timer, utilizing last round's probabilities, random guessing or alike - or replacing `chain_link_equations()` with something better, of course. Plug-and-play propositional logic solver or the like, for example, however that would require Massive rework.
After the latest improvements, the average time per game is 0.68 seconds (including the slowest finished games, excluding games that were killed automatically), n=10092.

## Current state (19.10.2024)

Capable of solving all solvable situations, including those that need minecount. 
Capable of guessing, choosing the better alternative from near-front cells or from other cells ('unseen unclicked') based on probabilities acquired from minecount functionalities and from the number of remaining mines (remaining minecount) and remaining unseen unclicked cells.
I am now using separated sets also for minecount and guessing situations. I'm also using the \[0s, 1s\] compact counting in both non-minecount and minecount situation. I'm now also using `botGame.py`'s `simple_solver()` to get all the obvious solutions out of the way every time before utilizing `CSP_solver`, which reduces the (separated) sets' sizes significantly in many cases. I'm also recognizing minecount situations from those, where minecount cannot possibly help (if whole-front max mine number is less than remaining number of mines in the whole map), and if minecount would not help, instead guessing is done immediately after not being able to solve variables definitely as 0 or 1 via `chain_link_equations()` and `join_comp_groups_into_solutions()`.
Next: testing.

## Goal
The goal is to implement a bot that's capable of solving all solvable minesweeper situations (done as far as I know) using coupled subsets CSP, referring to Becerra, David J. 2015. Algorithmic Approaches to Playing Minesweeper. Bachelor's thesis, Harvard College (permalink: http://nrs.harvard.edu/urn-3:HUL.InstRepos:14398552).

## Ideas
- not done at the moment: subtraction of shorter equations from longer ones could be done before the rest of current `CSP_solver` to reduce the sizes of (separated) eq sets for `CSP_solver`. Overall, so far hybrid solutions and solution space reduction have proven to be the best tools apart from my strategy in `chain_link_equations` which connects one equation alt answers to compatible alt answers from another group, and repeats until all equations have been covered (on-the-go reduction of solutions is done that way)
- implemented: earlier recognition of minecount helpfulness; if the max number of mines near fronts + remaining cells is smaller than remaining minecount, do not even start minecount, as it's impossible in this situation that minecount could solve anything. For this, I needed the max possible number of mines in the front, before the 'minecount' activities would be started normally
- implemented using `sorted()`: try to maximize overlap in `chain_link_equations()` so that a maximum number of impossible alt answers is discarded as soon as possible and/or in total during the equation chain building (I have not verified how much difference the chaining order makes)
- implemented: grouping equations to separated sets; in each set, equations which directly or indirectly share variables with each other
- implemented: for each alt solution per equation, discard if it's incompatible with all possible alt solutions from one or more other equations
- implemented: chain link equations with (usually) maximum overlap regarding shared variables, discarding impossible alt solutions per equation based on this pairing. This builds a chain of equations, which eliminates the need to couple each equation directly to all other equations
- in the worst cases, a timer could be used to opt for performance in the rare cases rather than absolute solving and accurate probability calculations
