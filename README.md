# Dog-Agility-Solver

Algorithm to solve the "gambler" game in dog agility (for points/seconds)

Includes a simple python version and a (currently unfinished) c++ version. 

NOTE: I may or may not get back to the c++ version in the future to finish it.

The python example data shows how the input data is formatted. You should be able to paste this into a python console and get it running right away.

The algorithm does a divide-and-conquer brute force search, and uses a heuristic Branch-and-Bound technique, where we only search the x% closest obstacles at any iteration (so 100% would be a pure BFS). 
