from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Set
from piece import Piece


class Board:
    """Represents the checkers board and handles board-specific operations"""

    BOARD_SIZE = 8

    def __init__(self):
        self.squares = [[None] * self.BOARD_SIZE for _ in range(self.BOARD_SIZE)]
        self._initialize_pieces()

    def _initialize_pieces(self):
        """Set up the initial board position"""
        # Place black pieces (top of board)
        self._place_initial_pieces('black', 0, 3)
        # Place red pieces (bottom of board)
        self._place_initial_pieces('red', 5, 8)

    def _place_initial_pieces(self, color: str, start_row: int, end_row: int):
        """Helper to place pieces for one side during initialization"""
        for row in range(start_row, end_row):
            for col in range(self.BOARD_SIZE):
                if self.is_dark_square(row, col):
                    self.squares[row][col] = Piece(color)

    @staticmethod
    def is_dark_square(row: int, col: int) -> bool:
        """Check if a square is a dark square (where pieces can move)"""
        return (row + col) % 2 == 1

    def is_valid_position(self, row: int, col: int) -> bool:
        """Check if a position is within the board boundaries"""
        return 0 <= row < self.BOARD_SIZE and 0 <= col < self.BOARD_SIZE

    def get_piece(self, row: int, col: int) -> Optional[Piece]:
        """Get the piece at a given position"""
        if self.is_valid_position(row, col):
            return self.squares[row][col]
        return None

    def move_piece(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """
        Move a piece from one position to another.
        Returns the position of any captured piece, or None if no capture occurred.
        """
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        if not (self.is_valid_position(from_row, from_col) and
                self.is_valid_position(to_row, to_col)):
            return None

        piece = self.squares[from_row][from_col]
        if not piece:
            return None

        # Move the piece
        self.squares[to_row][to_col] = piece
        self.squares[from_row][from_col] = None

        # Check for and handle capture
        if abs(to_row - from_row) == 2:
            captured_row = (to_row + from_row) // 2
            captured_col = (to_col + from_col) // 2
            self.squares[captured_row][captured_col] = None
            return (captured_row, captured_col)

        return None

    def get_valid_moves(self, row: int, col: int, capture_only: bool = False) -> Set[Tuple[int, int]]:
        """Get all valid moves for a piece at the given position"""
        piece = self.get_piece(row, col)
        if not piece:
            return set()

        moves = set()
        captures = set()

        # Get move directions based on piece type
        directions = piece.get_move_directions()

        # Check captures
        for d_row, d_col in directions:
            capture_pos = self._check_capture(row, col, d_row, d_col, piece.color)
            if capture_pos:
                captures.add(capture_pos)

        # If we have captures or only want captures, return captures
        if captures or capture_only:
            return captures

        # Check regular moves
        for d_row, d_col in directions:
            new_row, new_col = row + d_row, col + d_col
            if (self.is_valid_position(new_row, new_col) and
                    not self.get_piece(new_row, new_col)):
                moves.add((new_row, new_col))

        return moves

    def _check_capture(self, row: int, col: int, d_row: int, d_col: int,
                       piece_color: str) -> Optional[Tuple[int, int]]:
        """Check if a capture is possible in a given direction"""
        jump_row, jump_col = row + d_row * 2, col + d_col * 2
        mid_row, mid_col = row + d_row, col + d_col

        if not self.is_valid_position(jump_row, jump_col):
            return None

        mid_piece = self.get_piece(mid_row, mid_col)
        if (mid_piece and
                mid_piece.color != piece_color and
                not self.get_piece(jump_row, jump_col)):
            return (jump_row, jump_col)

        return None

    def has_captures_available(self, color: str) -> bool:
        """Check if any piece of given color has available captures"""
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                piece = self.get_piece(row, col)
                if piece and piece.color == color:
                    if self.get_valid_moves(row, col, capture_only=True):
                        return True
        return False

    def has_valid_moves(self, color: str) -> bool:
        """Check if any piece of given color has any valid moves"""
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                piece = self.get_piece(row, col)
                if piece and piece.color == color:
                    if self.get_valid_moves(row, col):
                        return True
        return False

    def count_pieces(self, color: str) -> int:
        """Count the number of pieces of a given color"""
        count = 0
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                piece = self.get_piece(row, col)
                if piece and piece.color == color:
                    count += 1
        return count

    def promote_if_eligible(self, row: int, col: int):
        """Promote a piece to king if it has reached the opposite end"""
        piece = self.get_piece(row, col)
        if not piece:
            return

        if ((piece.color == 'red' and row == 0) or
                (piece.color == 'black' and row == self.BOARD_SIZE - 1)):
            piece.king = True

    def serialize(self) -> List[List[Dict]]:
        """Convert board state to serializable format"""
        return [[piece.serialize() if piece else None
                 for piece in row]
                for row in self.squares]

    @classmethod
    def deserialize(cls, data: List[List[Dict]]) -> 'Board':
        """Create board instance from serialized data"""
        board = cls()
        board.squares = [[Piece.deserialize(piece_data) if piece_data else None
                          for piece_data in row]
                         for row in data]
        return board

    def clone(self) -> 'Board':
        """Create a deep copy of the board"""
        new_board = Board()
        new_board.squares = [[piece.clone() if piece else None
                              for piece in row]
                             for row in self.squares]
        return new_board