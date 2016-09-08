# Dog-Agility-Solver

Algorithm to solve the "gambler" game in dog agility (for points/seconds)

Includes a simple python version and a (currently unfinished) c++ version.

NOTE: I may or may not get back to the c++ version in the future to finish it.

The python example data shows how the input data is formatted. You should be able to paste this into a python console and get it running right away.

The algorithm does a divide-and-conquer brute force search, and uses a heuristic Branch-and-Bound technique, where we only search the x% closest obstacles at any iteration (so 100% would be a pure BFS). I have found no good bound function that wasn't either extremely weak, or left the problem still NP-Hard (since this problem is a few NP-Hard problems "stacked on each other").

If you want to use this on 20 or more obstacles, I would recommend parallelizing, since the problem is close to embarassingly parallel (as a divide and conquer method).
