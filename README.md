# MinesweeperBot
Course _Aineopintojen harjoitustyö - algoritmit ja tekoäly_, University of Helsinki

## Current state (7.10.2024)

Capable of solving all solvable situation, including those that need minecount.

## Goal
The goal is to implement a bot that's capable of solving all solvable minesweeper situations (done) using coupled subsets CSP, referring to Becerra, David J. 2015. Algorithmic Approaches to Playing Minesweeper. Bachelor's thesis, Harvard College (permalink: http://nrs.harvard.edu/urn-3:HUL.InstRepos:14398552).

If possible, should be even more efficient (to-do). At the moment, capable of handling expert maps, but in wilder situations than what one usually encounters in expert, it could become unusably slow and RAM-exhaustive (e.g. several disconnected fronts in a minecount situation).