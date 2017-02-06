#!/usr/bin/env python
# encoding: utf-8

"""
Simple library to cut correct slices out of a pizza,
maximizing the total number of cells in all slices
"""


def gcd(a, b):
    """Calculates the greater common divisor of a and b.
    This will be helpful to get the maximum size possible
    of a slice.
    Given the size of a pizza (RxC),
    if the maximum size of slice is rxc=H,
    then, a slice is either
     * r = gcd((RxC), H) rows and c = H/gcd((RxC), H) columns,
     * r = H/gcd((RxC), H) rows and c = H/ columns
    """
    if b == 0:
        return a
    else:
        r = a % b
        return gcd(b, r)


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
    def elementary_slices(self):
        """An elementary slice in a pizza contains at least 1 of each
        ingredient"""
        result = []
        if not self.tomatoes.count or not self.mushrooms.count:
            # the pizza contains only one ingredient;
            # every cell is an elementary slice
            for i in self.rows:
                for j in self.columns:
                    result.append([Cell(i, j), Cell(i, j)])
        else:
            a = [
                i for i in [self.tomatoes, self.mushrooms]
                if i.count == min(self.tomatoes.count, self.mushrooms.count)
                ][0]
            if a == self.tomatoes:
                b = self.mushrooms
            else:
                b = self.tomatoes
            result = []
            seen = []
            for i in a.cells:
                for j in i.neighbours(self.rows, self.columns):
                    if j in b.cells and j not in seen:
                        result.append(sorted([i, j]))
                        seen.append(j)
                        break
        return result

    def slices(self):
        """We should recursively expand each elementary slice
        to a maximum by including only free cells.
        At the very end, when we have only valid slices,
        we will use the gcd() to calculate how many column or row
        we should add to the existing slices to maximize them
        (e.g. grouping valid slices to a maximum)
        """
        pass
# EOF
