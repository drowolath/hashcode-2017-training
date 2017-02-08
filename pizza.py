#!/usr/bin/env python
# encoding: utf-8

"""
Simple library to cut correct slices out of a pizza,
maximizing the total number of cells in all slices
"""


class Slice(object):
    def __init__(self, upper_left, lower_right, pizza=None):
        self.upper_left = upper_left
        self.lower_right = lower_right
        self.pizza = pizza

    def __repr__(self):
        msg = ('<Slice ({0}, {1})'
               ' T={2} M={3}>').format(
                   self.upper_left,
                   self.lower_right,
                   self.tomatoes.count,
                   self.mushrooms.count
                   )
        return msg

    @property
    def cells(self):
        result = []
        for r in range(self.upper_left.row, self.lower_right.row+1):
            for c in range(self.upper_left.column, self.lower_right.column+1):
                result.append(Cell(r ,c))
        return result

    @property
    def tomatoes(self):
        cells = []
        count = 0
        if self.pizza:
            for cell in self.cells:
                if cell in self.pizza.tomatoes.cells:
                    count += 1
                    cells.append(cell)
        return Ingredient(count, cells)

    @property
    def mushrooms(self):
        cells = []
        count = 0
        if self.pizza:
            for cell in self.cells:
                if cell in self.pizza.mushrooms.cells:
                    count += 1
                    cells.append(cell)
        return Ingredient(count, cells)


class Cell(object):
    """A cell is recognized by a pair of 0 based coordinates (r,c)
    denoting respectively its row and its column"""
    def __init__(self, row, column):
        self.row = row
        self.column = column

    def neighbours(self, R, C):
        """A cell has at most 4 adjacent cells; we don't count diagonals.
        R is the number of rows in the rectangle containing the cell,
        anc C is the number of columns"""
        neighbours = []
        if self.row+1 < R:
            neighbours.append(Cell(self.row+1, self.column))
        if self.row-1 >= 0:
            neighbours.append(Cell(self.row-1, self.column))
        if self.column+1 < C:
            neighbours.append(Cell(self.row, self.column+1))
        if self.column-1 < C:
            neighbours.append(Cell(self.row, self.column-1))
        return neighbours

    def __repr__(self):
        return '<Cell ({0}, {1})>'.format(self.row, self.column)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __gt__(self, other):
        return (
            self.row > other.row or
            self.row == other.row and self.column > other.column
            )

    def __lt__(self, other):
        return (
            self.row < other.row or
            self.row == other.row and self.column < other.column
            )

    def __add__(self, other):
        return self.__class__(self.row+other.row, self.column+other.column)

    def __sub__(self, other):
        if self.row-other.row < 0 or self.column-other.column < 0:
            raise StopIteration("This went too far. Your cell is off any grid")
        return self.__class__(self.row-other.row, self.column-other.column)


class Ingredient(object):
    """An ingredient has a count in a Pizza, and occupies cells (or not?)"""
    def __init__(self, count, cells):
        self.count = count
        self.cells = cells

    def __repr__(self):
        return '<Ingredient {0}>'.format(self.cells)


class Pizza(object):
    """A pizza is represented by a RxC rectangle; each cell of the pizza
    contains either a mushroom or a tomato"""
    def __init__(self, **kwargs):
        if kwargs.get('data'):  # kwargs['data'] is the filepath to the dataset
            with open(kwargs['data']) as infile:
                lines = infile.readlines()
                self.rows, self.columns, self.L, self.H = [
                    int(i) for i in lines[0].rstrip('\n').split()
                    ]
                r = 0
                t = 0
                m = 0
                t_pos = []
                m_pos = []
                for line in lines[1:]:
                    line = line.rstrip('\n')
                    t += line.count('T')
                    m += line.count('M')
                    for i in range(len(line)):
                        if line[i] == 'T':
                            t_pos.append(Cell(r, i))
                        else:
                            m_pos.append(Cell(r, i))
                    r += 1
                self.tomatoes = Ingredient(t, t_pos)
                self.mushrooms = Ingredient(m, m_pos)
        else:
            for i, j in kwargs.items():
                if i != 'data':
                    vars(self)[i] = j

    def __repr__(self):
        return '<Pizza {r}x{c} T={t} M={m}>'.format(
            r=self.rows, c=self.columns,
            t=self.tomatoes.count, m=self.mushrooms.count
            )

    @property
    def cells(self):
        result = []
        for r in range(self.rows):
            for c in range(self.columns):
                result.append(Cell(r, c))
        return result

    @property
    def slices_sizes(self):
        """Given the surface of the biggest slices possible in the pizza,
        and the minimum number of each ingredient in a slice,
        we determine the possible numbers of rows and columns any valid slice
        need"""
        import math
        result = []
        for h in reversed(range(2*self.L, self.H+1)):
            bar = []
            i = 1
            while i <= math.sqrt(h):  # we list all the divisors of self.H
                if h % i == 0:
                    if (i, h/i) not in bar:
                        bar.append((i, h/i))
                    if (h/i, i) not in bar:
                        bar.append((h/i, i))
                i += 1
            bar = sorted(bar, key=lambda x: x[0], reverse=True)
            bar = filter(
                lambda x: x[0] <= self.rows and x[1] <= self.columns,
                bar
                )
            for element in bar:
                result.append(element)
        return [[int(r), int(c)] for r, c in result]

    def slice(self, start, rows, columns):
        """slice pizza from start according to
        a number of rows and number of columns
        """
        upper_left = start
        lower_right = upper_left + Cell(rows-1, columns-1)
        while lower_right in self.cells:
            # check surface covered is a valid slice
            s = Slice(upper_left, lower_right, self)
            t = s.tomatoes.count
            m = s.mushrooms.count
            if t >= self.L and m >= self.L and t+m <= self.H:
                # slice is valid, store it
                print(s)

            if self.rows-lower_right.row-1 >= rows:
                upper_left += Cell(lower_right.row+1, upper_left.column)
            else:
                upper_left = Cell(upper_left.row, lower_right.column+1)
            lower_right = upper_left + Cell(rows-1, columns-1)
# EOF
