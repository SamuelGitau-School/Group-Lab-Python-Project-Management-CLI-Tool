import random

class Board:
    """A 8x8 board."""

    def __init__(self, size=8):
        self.size = size
        self._grid = [[None] * size for _ in range(size)]

    def in_bounds(self, row, col):
        if row < 0 or row >= self.size: return False
        if col < 0 or col >= self.size: return False
        return True

    def piece_at(self, row, col):
        """Return the piece at a position."""
        if not self.in_bounds(row, col): return None
        return self._grid[row][col]

    def place(self, piece, row=None, col=None):
        """Put a piece on the board."""
        # If no row or column was given use position
        if row is None: row = piece.row
        if col is None: col = piece.col

        if not self.in_bounds(row, col): raise ValueError("Position is outside the board")
        if self._grid[row][col] is not None: raise ValueError("That square is already occupied")

        # Update the pieces position.
        piece.row = row
        piece.col = col

        # Put the piece on the board.
        self._grid[row][col] = piece

        return piece

    def remove(self, row, col):
        piece = self._grid[row][col]
        self._grid[row][col] = None
        return piece

    def pieces(self):
        """Return all pieces on the board."""
        all_pieces = []
        for row in self._grid:
            for piece in row:
                if piece is not None: all_pieces.append(piece)
        return all_pieces

    def move(self, piece, row, col):
        """Move a piece if the move is legal."""
        legal_moves = piece.get_legal_moves(self)

        # Check if the requested position is legal.
        if (row, col) not in legal_moves:
            raise ValueError(
                f"Illegal move: {piece} -> ({row}, {col})"
            )

        self._grid[piece.row][piece.col] = None

        # Check if another piece is at the position
        captured = self._grid[row][col]

        # Put the moving piece in the new position.
        self._grid[row][col] = piece

        # Update the pieces position.
        piece.move_to(row, col)

        # Return captured piece.
        return captured

    def play_random_moves(self, pieces=None, n=1, seed=None):
        """Make legal moves."""
        random_generator = random.Random(seed)
        log = []

        # Repeat for the requested number of rounds.
        for round_number in range(n):
            # Use provided pieces.
            if pieces is not None: active_pieces = list(pieces)
            else: active_pieces = self.pieces()

            # Randomize the order.
            random_generator.shuffle(active_pieces)

            for piece in active_pieces:
                if self._grid[piece.row][piece.col] is not piece:
                    continue

                # Find moves.
                legal_moves = piece.get_legal_moves(self)
                if len(legal_moves) == 0:
                    continue

                target = random_generator.choice(legal_moves)
                old_position = piece.position
                self.move(piece, target[0], target[1])

                # Save the move.
                log.append(
                    (piece, old_position, piece.position)
                )

        return log

    def render(self):
        """Return the board as text."""
        lines = []
        for row in range(self.size - 1, -1, -1):
            cells = []
            for col in range(self.size):
                piece = self._grid[row][col]
                # square
                if piece is None: cells.append(".")
                else:
                    # Get the piece symbol.
                    symbol = piece.symbol
                    # White = uppercase
                    # Black = lowercase
                    if piece.color == "white": cells.append(symbol)
                    else: cells.append(symbol.lower())

            # Add the row number.
            row_text = str(row + 1) + " "

            for cell in cells:
                row_text += cell + " "

            lines.append(row_text.rstrip())

        # Add the column letters.
        lines.append("a b c d e f g h")

        return "\n".join(lines)

    def __str__(self):
        return self.render()