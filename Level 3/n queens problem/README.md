# N-Queens Problem

This Python project solves the N-Queens puzzle: place `N` queens on an `N x N`
chessboard so that no two queens share a row, column, or diagonal.

## Approach

The board is represented by a two-dimensional list. A `1` contains a queen and
a `0` is an empty square. The solver uses backtracking to place exactly one
queen in each column. Before a placement, it checks the row and both diagonals
for an existing queen. If a later column cannot be filled, that placement is
removed and the solver tries the next candidate position.

## Run

From this directory, run a size of your choice (for example, 8):

```powershell
python "n-queen problem.py" 8
```

Because the filename contains a space, keep the quotation marks in the command.
To enter the board size interactively, run:

```powershell
python "n-queen problem.py"
```

The program prints one valid solution as a chessboard and as a 2D array. `1`
marks a queen and `0` marks an empty square. `N = 2` and `N = 3` correctly
report that no solution exists.
