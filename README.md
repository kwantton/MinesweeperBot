# MinesweeperBot
Course _Aineopintojen harjoitustyö - algoritmit ja tekoäly_, University of Helsinki

## git cloning
see 'How_to_install.md'

## Current state (7.10.2024)

Capable of solving all solvable situations, including those that need minecount. Next: improve minecount time complexity, then move on to implementing guessing (which should be very easy to implement given the current functionalities of `CSP_solver`)

## Goal
The goal is to implement a bot that's capable of solving all solvable minesweeper situations (done) using coupled subsets CSP, referring to Becerra, David J. 2015. Algorithmic Approaches to Playing Minesweeper. Bachelor's thesis, Harvard College (permalink: http://nrs.harvard.edu/urn-3:HUL.InstRepos:14398552).

If possible, should be even more efficient (to-do). At the moment, capable of handling expert maps, but in wilder situations than what one usually encounters in expert, it could become unusably slow and RAM-exhaustive (e.g. several disconnected fronts in a minecount situation).

## Ideas
- Currently (7.10.24) every press of 'b' in the game gets all the possible answers for every front (highlighted in yellow if you press 'h' in the game). Since the number of <em>possible</em> answers for the `self.front`('s all 1 or more separated components) in almost any situation in minesweeper is usually (?) multiple(s) of times higher than the total number of <em>impossible</em> answers, it could be much faster to look for impossible answers than for the possible ones: try a cell in `self.front`, place its value as 1, see if ANY possible answer is found, if so, place as 0, same thing, as long as an impossible 0 or 1 is found -> mark that as answer. Noteworthily, however, currently (7.10.2024) I do manage to get all the possible answers for (all the) front(s) decently fast by using an equation compatible alt answer coupling method in `CSP_solver`, and by reducing minecount situations to simple math exactly by ruling out the impossible situations.
- Important: in minecount needed -situations, I'm unnecessarily combining the separated sets for getting the alt minecount per entire-front alt answer. I could just use the minecounts per alt in the separated sets instead of combining first (no need to do that!), summing them up, this way virtually "combining" the alt answers per set for minecount inspection without actual combinations, the making of which takes a lot of computation and time -> some minecount situations would be dozens..thousands...more times faster. I'll do this once I have time from LaMa and todari-IIa
