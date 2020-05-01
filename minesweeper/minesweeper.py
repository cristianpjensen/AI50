import itertools
import random
import copy


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if self.count == len(self.cells):
            return self.cells

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # Optimization: list of checked subsets.
        self.checked_subsets = []

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.
        """
        # Mark the cell as a move that has been made.
        self.moves_made.add(cell)
        # Mark the cell as safe, updating any sentences that contain the
        # `cell` as well.
        self.mark_safe(cell)
        for sentence in self.knowledge:
            if cell in sentence.cells:
                sentence.cells.remove(cell)

        # Add a new sentence to the AI's knowledge base based on the value of
        # `cell` and `count`.
        cells = set()
        for i in [cell[0]-1, cell[0], cell[0]+1]:
            for j in [cell[1]-1, cell[1], cell[1]+1]:
                if 8 > i >= 0 and 8 > j >= 0:
                    if (i, j) not in self.safes and (i, j) not in self.mines and (i, j) != cell:
                        cells.add((i, j))
        self.knowledge.append(Sentence(cells, count))

        # Mark any additional cells as safe or as mines if it can be concluded
        # based on the AI's knowledge base.
        for sentence in self.knowledge:
            if sentence.known_safes() != None:
                for cell in sentence.known_safes().copy():
                    self.mark_safe(cell)
        
        # If 8 moves left, they must be the mines, since there are always 8 mines.
        moves = set()
        for i in range(self.width):
            for j in range(self.height):
                moves.add((i, j))
        
        moves_left = moves - self.moves_made

        if len(moves_left) == 8:
            for cell in moves_left:
                self.mark_mine(cell)

        knowledge_copy = copy.deepcopy(self.knowledge)
        
        for one in knowledge_copy:
            for two in knowledge_copy:
                if one.cells != two.cells:
                    if (one.cells, two.cells) not in self.checked_subsets:
                        self.checked_subsets.append((one.cells, two.cells))
                        if one.cells.issubset(two.cells) and len(one.cells) != 0 and len(two.cells) != 0:
                            cells_new = two.cells - one.cells
                            count_new = two.count - one.count
                            self.knowledge.append(Sentence(cells_new, count_new))

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for move in self.safes:
            if move not in self.moves_made:
                return move
        return None


    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # Make a list of all possible moves.
        all_moves = []
        for i in range(self.height):
            for j in range(self.width):
                all_moves.append((i, j))
        
        # Remove the moves that have already been made.
        for move in self.moves_made:
            if move in all_moves:
                all_moves.remove(move)
        
        # Remove the moves that are known to be mines.
        for move in self.mines:
            if move in all_moves:
                all_moves.remove(move)

        # If no moves are possible, return None.
        random.shuffle(all_moves)
        if len(all_moves) > 0:
            return all_moves[0]
        else:
            return None
       