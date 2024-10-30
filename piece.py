from dataclasses import dataclass
from typing import List, Tuple, Dict


@dataclass
class Piece:
    """Represents a checker piece with its color and king status"""
    color: str  # 'red' or 'black'
    king: bool = False

    def get_move_directions(self) -> List[Tuple[int, int]]:
        """
        Get valid move directions for the piece.
        Returns list of (row_delta, col_delta) tuples.
        Red moves up (negative row) by default.
        Black moves down (positive row) by default.
        Kings can move both directions.
        """
        directions = []

        # Regular pieces can only move in one direction
        if self.color == 'red' or self.king:
            # Up-left and up-right
            directions.extend([(-1, -1), (-1, 1)])

        if self.color == 'black' or self.king:
            # Down-left and down-right
            directions.extend([(1, -1), (1, 1)])

        return directions

    def can_move_direction(self, row_delta: int, col_delta: int) -> bool:
        """Check if piece can legally move in given direction"""
        # Must be diagonal movement
        if abs(row_delta) != abs(col_delta):
            return False

        # Kings can move any diagonal direction
        if self.king:
            return True

        # Red pieces can only move up (negative row delta)
        if self.color == 'red':
            return row_delta < 0

        # Black pieces can only move down (positive row delta)
        return row_delta > 0

    def serialize(self) -> Dict:
        """Convert piece to serializable dictionary"""
        return {
            'color': self.color,
            'king': self.king
        }

    @classmethod
    def deserialize(cls, data: Dict) -> 'Piece':
        """Create piece instance from serialized data"""
        if data is None:
            return None
        return cls(
            color=data['color'],
            king=data['king']
        )

    def clone(self) -> 'Piece':
        """Create a deep copy of the piece"""
        return Piece(
            color=self.color,
            king=self.king
        )