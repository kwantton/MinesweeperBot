# MinesweeperBot
Course _Aineopintojen harjoitustyö - algoritmit ja tekoäly_, University of Helsinki

## git cloning

see 'how_to_clone.md'

## Current state (13.10.2024)

Capable of solving all solvable situations, including those that need minecount. 
Capable of guessing, choosing the better alternative from near-front cells or from other cells ('unseen unclicked') based on probabilities acquired from minecount functionalities and from the number of remaining mines (remaining minecount) and remaining unseen unclicked cells.
I am now using separated sets also for minecount and guessing situations. I'm also using the \[0s, 1s\] compact counting in both non-minecount and minecount situation. I'm now also using `botGame.py`'s `simple_solver()` to get all the obvious solutions out of the way every time before utilizing `CSP_solver`, which reduces the (separated) sets' sizes significantly in many cases. Next: testing.

## Goal
The goal is to implement a bot that's capable of solving all solvable minesweeper situations (done) using coupled subsets CSP, referring to Becerra, David J. 2015. Algorithmic Approaches to Playing Minesweeper. Bachelor's thesis, Harvard College (permalink: http://nrs.harvard.edu/urn-3:HUL.InstRepos:14398552).

## Ideas
- subtraction of shorter equations from longer ones could be done before the rest of current `CSP_solver` to reduce the sizes of (separated) eq sets for `CSP_solver`. Overall, so far hybrid solutions and solution space reduction have proven to be the best tools apart from my strategy in `chain_link_equations` which connects one equation alt answers to compatible alt answers from another group, and repeats until all equations have been covered (on-the-go reduction of solutions is done that way)
