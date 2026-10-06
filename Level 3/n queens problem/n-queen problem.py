"""Solve the N-Queens problem using backtracking.

Run this file directly and enter a board size, or provide the size as a
command-line argument: ``python "n-queen problem.py" 8``.
"""

from __future__ import annotations

import sys
from typing import Optional


Board = list[list[int]]


def is_safe(board: Board, row: int, col: int) -> bool:
    """Return whether a queen can be placed at ``(row, col)``.

    Queens are placed one column at a time from left to right, so only the
    current row and the two diagonals to the left need to be inspected.
    """
    size = len(board)

    for previous_col in range(col):
        if board[row][previous_col] == 1:
            return False

    check_row, check_col = row - 1, col - 1
    while check_row >= 0 and check_col >= 0:
        if board[check_row][check_col] == 1:
            return False
        check_row -= 1
        check_col -= 1

    check_row, check_col = row + 1, col - 1
    while check_row < size and check_col >= 0:
        if board[check_row][check_col] == 1:
            return False
        check_row += 1
        check_col -= 1

    return True


def solve_n_queens(size: int) -> Optional[Board]:
    """Return one N-Queens solution as a 2D array, or ``None`` if absent."""
    if size < 1:
        raise ValueError("Board size must be a positive integer.")

    board: Board = [[0 for _ in range(size)] for _ in range(size)]

    def place_queen(col: int) -> bool:
        if col == size:
            return True

        for row in range(size):
            if is_safe(board, row, col):
                board[row][col] = 1
                if place_queen(col + 1):
                    return True
                board[row][col] = 0  # Backtrack.

        return False

    return board if place_queen(0) else None


def display_board(board: Board) -> None:
    """Print a readable chessboard, using Q for a queen and . for empty."""
    for row in board:
        print(" ".join("Q" if square else "." for square in row))


def get_board_size(arguments: list[str]) -> int:
    """Read the board size from the command line or interactively."""
    if len(arguments) > 1:
        raise ValueError("Provide only one board size.")

    try:
        raw_size = arguments[0] if arguments else input("Enter the number of queens: ")
    except EOFError as error:
        raise ValueError("No board size was provided.") from error

    try:
        size = int(raw_size)
    except ValueError as error:
        raise ValueError("Please enter a whole number.") from error

    if size < 1:
        raise ValueError("Board size must be a positive integer.")
    return size


def main() -> None:
    """Run the command-line application."""
    try:
        size = get_board_size(sys.argv[1:])
        solution = solve_n_queens(size)
    except ValueError as error:
        print(f"Error: {error}")
        raise SystemExit(1) from error

    if solution is None:
        print(f"No solution exists for {size} queens.")
        return

    print(f"One solution for {size} queens:\n")
    display_board(solution)
    print("\n2D array representation:")
    for row in solution:
        print(row)


if __name__ == "__main__":
    main()
