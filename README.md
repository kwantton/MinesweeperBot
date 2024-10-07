# MinesweeperBot
Course _Aineopintojen harjoitustyö - algoritmit ja tekoäly_, University of Helsinki

## Current state (7.10.2024)

Capable of solving all solvable situation, including those that need minecount.

## Goal
The goal is to implement a bot that's capable of solving all solvable minesweeper situations (done) using coupled subsets CSP, referring to Becerra, David J. 2015. Algorithmic Approaches to Playing Minesweeper. Bachelor's thesis, Harvard College (permalink: http://nrs.harvard.edu/urn-3:HUL.InstRepos:14398552).

If possible, should be even more efficient (to-do). At the moment, capable of handling expert maps, but in wilder situations than what one usually encounters in expert, it could become unusably slow and RAM-exhaustive (e.g. several disconnected fronts in a minecount situation).

## NB!
Currently (7.10.24) every press of 'b' in the game gets all the possible answers for every front (highlighted in yellow if you press 'h' in the game). Of course, since the number of <em>possible</em> answers for the `self.front`('s all 1 or more separated components) in almost any situation in minesweeper is practically always multiple(s) of times higher than the total number of <em>impossible</em> answers, it would be much faster to look for impossible answers than for the possible ones: try a cell in `self.front`, place its value as 1, see if ANY possible answer is found, if so, place as 0, same thing, as long as an impossible 0 or 1 is found -> mark that as answer. Noteworthily, however, currently (7.10.2024) I do manage to get all the possible answers for (all the) front(s) decently fast by using an equation compatible alt answer coupling method in `CSP_solver`, and by reducing minecount situations to simple math exactly by ruling out the impossible situations.
