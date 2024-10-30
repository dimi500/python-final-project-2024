from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
import json


@dataclass
class Piece:
    color: str  # 'red' or 'black'
    king: bool = False

    def serialize(self) -> Dict:
        return {'color': self.color, 'king': self.king}

    @classmethod
    def deserialize(cls, data: Dict) -> 'Piece':
        return cls(**data) if data else None


class CheckersGame:
    def __init__(self):
        self.initialize_board()
        self.current_player = 'red'
        self.selected_piece = None
        self.valid_moves = []
        self.must_capture = False
        self.winner = None
        self._check_for_captures()

    def initialize_board(self):
        """Create starting board position"""
        self.board = [[None] * 8 for _ in range(8)]
        # Place black pieces (top of board)
        for row in range(3):
            for col in range(8):
                if (row + col) % 2 == 1:
                    self.board[row][col] = Piece('black')
        # Place red pieces (bottom of board)
        for row in range(5, 8):
            for col in range(8):
                if (row + col) % 2 == 1:
                    self.board[row][col] = Piece('red')

    def _get_piece_moves(self, row: int, col: int, capture_only: bool = False) -> List[Tuple[int, int]]:
        """Get all valid moves for a piece, optionally only capture moves"""
        piece = self.board[row][col]
        if not piece or piece.color != self.current_player:
            return []
        moves = []
        directions = []

        # Determine valid directions based on piece type
        if piece.color == 'red' or piece.king:
            directions.extend([(-1, -1), (-1, 1)])  # Up-left and up-right
        if piece.color == 'black' or piece.king:
            directions.extend([(1, -1), (1, 1)])  # Down-left and down-right
        # Check captures first
        captures = []
        for d_row, d_col in directions:
            new_row, new_col = row + d_row * 2, col + d_col * 2
            mid_row, mid_col = row + d_row, col + d_col

            if (0 <= new_row < 8 and 0 <= new_col < 8 and
                    self.board[mid_row][mid_col] and
                    self.board[mid_row][mid_col].color != piece.color and
                    not self.board[new_row][new_col]):
                captures.append((new_row, new_col))
        # If captures exist or we only want captures, return them
        if captures or capture_only:
            return captures
        # Check regular moves
        for d_row, d_col in directions:
            new_row, new_col = row + d_row, col + d_col
            if 0 <= new_row < 8 and 0 <= new_col < 8 and not self.board[new_row][new_col]:
                moves.append((new_row, new_col))
        return moves

    def _check_for_captures(self) -> bool:
        """Check if current player has any capture moves available"""
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == self.current_player:
                    if self._get_piece_moves(row, col, capture_only=True):
                        self.must_capture = True
                        return True
        self.must_capture = False
        return False

    def _can_continue_capture(self, row: int, col: int) -> bool:
        """Check if a piece can make another capture after a capture move"""
        return bool(self._get_piece_moves(row, col, capture_only=True))

    def select_piece(self, row: int, col: int):
        """Select a piece and calculate its valid moves"""
        piece = self.board[row][col]

        # Can only select own pieces
        if not piece or piece.color != self.current_player:
            return False
        # If captures are available, can only select pieces with captures
        if self.must_capture:
            moves = self._get_piece_moves(row, col, capture_only=True)
            if not moves:
                return False
        else:
            moves = self._get_piece_moves(row, col)
        self.selected_piece = (row, col)
        self.valid_moves = moves
        return True

    def make_move(self, new_row: int, new_col: int) -> bool:
        """Attempt to make a move to the given position"""
        if not self.selected_piece or (new_row, new_col) not in self.valid_moves:
            return False
        old_row, old_col = self.selected_piece
        piece = self.board[old_row][old_col]

        # Make the move
        self.board[new_row][new_col] = piece
        self.board[old_row][old_col] = None
        # Handle capture
        is_capture = abs(new_row - old_row) == 2
        if is_capture:
            mid_row = (new_row + old_row) // 2
            mid_col = (new_col + old_col) // 2
            self.board[mid_row][mid_col] = None
        # Handle king promotion
        if ((piece.color == 'red' and new_row == 0) or
                (piece.color == 'black' and new_row == 7)):
            piece.king = True
        # Check for continued captures
        if is_capture and self._can_continue_capture(new_row, new_col):
            self.selected_piece = (new_row, new_col)
            self.valid_moves = self._get_piece_moves(new_row, new_col, capture_only=True)
            return True
        # End turn
        self._end_turn()
        return True

    def _end_turn(self):
        """End the current turn and prepare for next player"""
        self.current_player = 'black' if self.current_player == 'red' else 'red'
        self.selected_piece = None
        self.valid_moves = []
        self._check_for_captures()

        # Check for game over
        if self.is_game_over():
            self.winner = 'black' if self.current_player == 'red' else 'red'

    def is_game_over(self) -> bool:
        """Check if the game is over (current player has no valid moves)"""
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == self.current_player:
                    if self._get_piece_moves(row, col):
                        return False
        return True

    def serialize(self) -> Dict:
        """Convert game state to serializable dictionary"""
        return {
            'board': [[piece.serialize() if piece else None for piece in row]
                      for row in self.board],
            'current_player': self.current_player,
            'selected_piece': self.selected_piece,
            'valid_moves': self.valid_moves,
            'must_capture': self.must_capture,
            'winner': self.winner
        }

    @classmethod
    def deserialize(cls, data: Dict) -> 'CheckersGame':
        """Create game instance from serialized data"""
        game = cls()
        game.board = [[Piece.deserialize(piece_data) if piece_data else None
                       for piece_data in row] for row in data['board']]
        game.current_player = data['current_player']
        game.selected_piece = data['selected_piece']
        game.valid_moves = data['valid_moves']
        game.must_capture = data['must_capture']
        game.winner = data['winner']
        return game