# Dog-Agility-Solver

Algorithm to solve the "gambler" game in dog agility (for points/seconds)

Includes a simple python version

NOTE: I may or may not get back to the unfinished parallel c++ version in the future to include it.

The python example data shows how the input data is formatted. You should be able to paste this into a python console and get it running right away.

The algorithm does a divide-and-conquer brute force search, and uses a heuristic "pseudo branch-and-bound" to reduce state space. We only search the x% closest obstacles at any iteration (so 100% would be a pure BFS). 

I have found no good classical bound function for B&B that wasn't either extremely weak, or left the problem still NP-Hard (since this problem is a few NP-Hard problems "stacked on each other"). So convergence past 17 or 18 obstacle courses becomes impossible without the heuristic bound method.

If you want to use this on 20 or more obstacles, I would recommend parallelizing using joblib, since the problem is close to embarassingly parallel (as a divide and conquer method).
