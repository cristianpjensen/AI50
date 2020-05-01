import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # Check that the length of the words in the domains matches the desired
        # length of the variable (unary constraint).
        for v in self.domains:
            for x in self.domains[v].copy():
                if v.length != len(x):
                    self.domains[v].remove(x)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # If the ith letter of word in x and the jth letter of word in y
        # aren't the same remove the word from x (binary constraint).
        revised = False
        i, j = self.crossword.overlaps[x, y]
        for x_word in self.domains[x].copy():
            if not any(x_word[i] == y_word[j] for y_word in self.domains[y]):
                self.domains[x].remove(x_word)
                revised = True
            if len(self.domains[y]) == 1 and \
               next(iter(self.domains[y])) in self.domains[x]: ####
                self.domains[x].remove(next(iter(self.domains[y])))
                revised = True
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            # Add all arcs to the queue. An arc is two neighbors.
            queue = []
            for x in self.domains:
                for y in self.crossword.neighbors(x):
                    queue.append((x, y))
        else:
            queue = arcs

        while len(queue) != 0:
            x, y = queue.pop()
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for z in self.crossword.neighbors(x):
                    if x != y:
                        queue.append((z, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # Return true if all the domains are in the assignment.
        if all(variable in assignment for variable in self.domains.keys()):
            return True
        else:
            return False

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        distinct_words = set()

        for v1, w1 in assignment.items():
            # All words are distinct.
            if w1 not in distinct_words:
                distinct_words.add(w1)
            else:
                return False

            # Every word is the correct length.
            if v1.length != len(w1):
                return False

            # No conflicts between neighboring variables.
            for v2 in self.crossword.neighbors(v1):
                if v2 not in assignment:
                    continue

                i, j = self.crossword.overlaps[v1, v2]
                if w1[i] != assignment[v2][j]:
                    return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        heuristics = {}
        
        # Assign n to each word, based on how many values it rules out for
        # neighboring variables.
        for var_word in self.domains[var]:
            n = 0
            
            for neighbor in self.crossword.neighbors(var):
                i, j = self.crossword.overlaps[var, neighbor]
                for neighbor_word in self.domains[neighbor]:
                    if (var_word[i] != neighbor_word[j] or
                        var_word == neighbor_word):
                        n += 1

            heuristics[var_word] = n

        # Sort the words by the value of n, in ascending order.
        h_sorted = sorted(heuristics, 
                          key=lambda x: x[1])

        return h_sorted

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        heuristics = {}

        # If the variable is not yet assigned, add it to the heuristics and
        # give it the value of the length of the amount of words it has in
        # it's domain.
        for variable in self.domains:
            if variable in assignment:
                continue
            heuristics[variable] = len(self.domains[variable])

        # Sort the amount of words in ascending order.
        h_words = dict(sorted(heuristics.items(), key=lambda k: k[1]))

        # Get the max_value, to check if there is a tie.
        max_value = list(h_words.values())[0]

        for h in h_words.copy():
            if h_words[h] != max_value:
                del h_words[h]

        # If no tie, return the key with the least amount of words in it's
        # domain.
        if len(h_words) == 1:
            return list(h_words.keys())[0]

        # Add the list of the variables that have a tie to another dictionary.
        # And give them the value of the amount of neighbors.
        h_neighbors = {}        
        h_vars = list(h_words.keys())
        for var in h_vars:
            h_neighbors[var] = len(self.crossword.neighbors(var))

        # Sort the amount of neighbors in descending order.
        h_neighbors = sorted(h_neighbors, key=lambda k: h_neighbors[k], reverse=True)

        return h_neighbors[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment): 
            return assignment
        
        var = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(var, assignment):
            assignment[var] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result != None:
                    return result
            del assignment[var]
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
