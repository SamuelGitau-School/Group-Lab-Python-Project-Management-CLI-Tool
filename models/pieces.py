from abc import ABC, abstractmethod

class Piece(ABC):
    """Base class for all chess pieces."""

    symbol = "?"

    def __init__(self, color, row, col):
        # Check that the color is either white or black
        if color != "white" and color != "black":
            raise ValueError("Color must be white or black")

        self.color = color
        self.row = row
        self.col = col

    @property
    def position(self):
        """Return the position of the piece."""
        return (self.row, self.col)

    def move_to(self, row, col):
        """Change the position of the piece."""
        self.row = row
        self.col = col

    @abstractmethod
    def get_legal_moves(self, board):
        """Return all legal moves for this piece."""
        pass

    def __repr__(self):
        """Show information about the piece."""
        return f"{self.__class__.__name__}({self.color} {self.position})"


class Bishop(Piece):
    """Bishop."""

    symbol = "B"

    def get_legal_moves(self, board):
        moves = []
        # Bishop moves diagonally in four directions.
        directions = [
            (-1, -1),  # up and left
            (-1, 1),   # up and right
            (1, -1),   # down and left
            (1, 1)     # down and right
        ]
        # Check each direction for Bishop.
        for dr, dc in directions:
            row = self.row + dr
            col = self.col + dc

            while board.in_bounds(row, col):
                piece = board.piece_at(row, col)
                if piece is None:
                    moves.append((row, col))
                # If an enemy piece is found Bishop captures it. Stops moving further.
                elif piece.color != self.color:
                    moves.append((row, col))
                    break
                # If a friendly piece is found Bishop cannot move further.
                else:
                    break
                # Move to the next square in same direction.
                row += dr
                col += dc

        return moves


class Queen(Piece):
    """Queen."""

    symbol = "Q"

    def get_legal_moves(self, board):
        moves = []
        # Queen can move diagonally and straight.
        directions = [
            (-1, -1),  # up and left
            (-1, 1),   # up and right
            (1, -1),   # down and left
            (1, 1),    # down and right
            (-1, 0),   # up
            (1, 0),    # down
            (0, -1),   # left
            (0, 1)     # right
        ]
        # Check each possible direction for Queen.
        for dr, dc in directions:
            row = self.row + dr
            col = self.col + dc

            while board.in_bounds(row, col):
                piece = board.piece_at(row, col)
                if piece is None:
                    moves.append((row, col))
                # If an enemy piece is found Queen captures it. Stops moving in that direction.
                elif piece.color != self.color:
                    moves.append((row, col))
                    break
                # If a friendly piece is found Queen stops moving.
                else:
                    break
                # Move to the next square.
                row += dr
                col += dc

        return moves


class Knight(Piece):
    """Knight."""

    symbol = "K"

    def get_legal_moves(self, board):
        moves = []
        # Knight can move in eight ways.
        offsets = [
            (-2, -1),
            (-2, 1),
            (2, -1),
            (2, 1),
            (-1, -2),
            (-1, 2),
            (1, -2),
            (1, 2)
        ]
        # Check each Knight move.
        for dr, dc in offsets:
            row = self.row + dr
            col = self.col + dc
            if not board.in_bounds(row, col):
                continue
            piece = board.piece_at(row, col)
            # Knight moves to an empty square or captures an enemy piece.
            if piece is None or piece.color != self.color:
                moves.append((row, col))

        return moves