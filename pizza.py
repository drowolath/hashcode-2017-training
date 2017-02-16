#!/usr/bin/env python
# encoding: utf-8

"""
Simple library to cut correct slices out of a pizza,
maximizing the total number of cells in all slices
"""

import collections
import itertools
import math

__all__ = [
    'Cell',
    'Pizza',
    'Slice'
    ]


def cell_range(upper_left, lower_right):
    """Given two Cell objects, return all the Cell objects
    comprised in the rectangle formed by those two"""
    for i in range(upper_left.row, lower_right.row + 1):
        for j in range(upper_left.column, lower_right.column + 1):
            yield(Cell(i, j))


class Cell(object):
    """A cell is recognized by a pair of 0 based coordinates (r,c)
    denoting respectively its row and its column, and an ingredient"""
    def __init__(self, row=0, column=0, ingredient=None):
        self.row = row
        self.column = column
        self.ingredient = ingredient

    def neighbours(self, pizza):
        """A cell has at most 4 adjacent cells; we don't count diagonals"""
        neighbours = []
        if self.row+1 < pizza.rows:
            neighbours.append(Cell(self.row+1, self.column))
        if self.row-1 >= 0:
            neighbours.append(Cell(self.row-1, self.column))
        if self.column+1 < pizza.columns:
            neighbours.append(Cell(self.row, self.column+1))
        if self.column-1 >= 0:
            neighbours.append(Cell(self.row, self.column-1))
        return neighbours

    def __repr__(self):
        return '<Cell ({0}, {1}) contains {2}>'.format(
            self.row, self.column, self.ingredient
            )

    def __eq__(self, other):
        if not hasattr(other, 'row') and not hasattr(other, 'column'):
            return False
        return self.row == other.row and self.column == other.column

    def __gt__(self, other):
        if not hasattr(other, 'row') and not hasattr(other, 'column'):
            return False
        return (
            self.row > other.row or
            self.row == other.row and self.column > other.column
            )

    def __lt__(self, other):
        if not hasattr(other, 'row') and not hasattr(other, 'column'):
            return False
        return (
            self.row < other.row or
            self.row == other.row and self.column < other.column
            )

    def __add__(self, other):
        if not hasattr(other, 'row') and not hasattr(other, 'column'):
            return False
        return self.__class__(self.row+other.row, self.column+other.column)

    def __sub__(self, other):
        if not hasattr(other, 'row') and not hasattr(other, 'column'):
            return False
        if self.row-other.row < 0 or self.column-other.column < 0:
            raise StopIteration("This went too far. Your cell is off grid")
        return self.__class__(self.row-other.row, self.column-other.column)


class Pizza(object):
    """A pizza is represented by a RxC rectangle; each cell of the pizza
    contains either a mushroom or a tomato"""
    def __init__(self, rows=0, columns=0, tomatoes=[], mushrooms=[], **kwargs):
        """"rows" and "columns" are integers in range(1, 1001);
        "tomatoes" and mushrooms" are arrays of Cell objects
        """
        self.rows = rows
        self.columns = columns
        self.tomatoes = tomatoes
        self.mushrooms = mushrooms
        if kwargs.get('data'):
            # kwargs['data']: filepath to a dataset representing the pizza
            with open(kwargs['data']) as infile:
                lines = infile.readlines()
                self.rows, self.columns, self.L, self.H = [
                    int(i) for i in lines[0].rstrip('\n').split()
                    ]
                r = 0
                for line in lines[1:]:
                    line = line.rstrip('\n')
                    for i in range(len(line)):
                        if line[i] == 'T':
                            self.tomatoes.append(Cell(r, i, 'T'))
                        else:
                            self.mushrooms.append(Cell(r, i, 'M'))
                    r += 1

    def __repr__(self):
        return '<Pizza {r}x{c} T={t} M={m}>'.format(
            r=self.rows, c=self.columns,
            t=len(self.tomatoes), m=len(self.mushrooms)
            )

    def __contains__(self, item):
        return item in self.cells

    @property
    def cells(self):
        t = sorted(self.tomatoes)
        m = sorted(self.mushrooms)
        return sorted(t+m)

    @property
    def sizes_of_slices(self):
        """Given the surface of the biggest slices possible in a pizza (H),
        and the minimum number of each ingredient in a slice (L),
        we determine the possible numbers of rows and columns any valid slice
        need"""
        result = collections.OrderedDict()
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
            result[h] = [[int(r), int(c)] for r, c in bar]
        return result

    @property
    def is_divisible(self):
        """Verifies if we can get more than one valid slice in the pizza"""
        t = len(self.tomatoes)
        m = len(self.mushrooms)
        return (t >= 2*self.L and m >= 2*self.L)

    def overlaps(self, other):
        """Verifies if (part of) the pizza overlaps another one"""
        if not hasattr(other, 'cells'):
            return False
        return bool([i for i in self.cells if i in other.cells])

    def slice(self, rows, columns):
        """get valid slices in a pizza: starting from the upper left cell,
        so that each valid slice contains rows*columns cells"""
        start = sorted(list(self.cells))[0]
        upper_left = start
        lower_right = upper_left + Cell(rows-1, columns-1)
        result = []
        slice = Pizza(
            rows=rows,
            columns=columns,
            tomatoes=list(
                filter(
                    lambda x: x in cell_range(upper_left, lower_right),
                    self.tomatoes
                    )
                ),
            mushrooms=list(
                filter(
                    lambda x: x in cell_range(upper_left, lower_right),
                    self.mushrooms
                    )
                )
            )
        slice.L = self.L
        slice.H = rows*columns
        while lower_right in self:
            # check if surface covered is a valid slice
            t = len(slice.tomatoes)
            m = len(slice.mushrooms)
            if t >= self.L and m >= self.L and t+m <= self.H:
                # slice is valid, store it
                result.append(slice)
            if self.rows-lower_right.row-1 >= rows:
                upper_left += Cell(lower_right.row+1, 0)
            else:
                upper_left = Cell(start.row, lower_right.column+1)
            if upper_left not in self:
                break
            else:
                lower_right = upper_left + Cell(rows-1, columns-1)
                slice = Pizza(
                    rows=rows,
                    columns=columns,
                    tomatoes=list(
                        filter(
                            lambda x: x in cell_range(upper_left, lower_right),
                            self.tomatoes
                            )
                        ),
                    mushrooms=list(
                        filter(
                            lambda x: x in cell_range(upper_left, lower_right),
                            self.mushrooms
                            )
                        )
                    )
                slice.L = self.L
                slice.H = rows*columns
        return result

    def getslices(self):
        """Going through all possible dimensions of a valid slice,
        starting from the biggest, we keep non overlapping slices"""
        result = [None]
        part_result = []
        for key, values in self.sizes_of_slices.items():
            foo = []
            for rows, columns in values:
                bar = self.slice(rows, columns)
                count = []
                for i in bar:
                    for j in result:
                        if i.overlaps(j):
                            break
                    else:
                        count.append(i)
                # we keep the valid slices that don't overlap
                # with the previous valid ones
                if len(count) > len(foo):
                    foo = count
                    # for a given size we keep the slicing
                    # that covers most of the remaining parts
            if result == [None]:
                result = foo
            else:
                result += foo
        # check if there is any remaining pizza
        bar = [cell for slice in result for cell in slice.cells]
        remaining_cells = sorted(
            list(filter(lambda x: x not in bar, self.cells))
            )
        if remaining_cells:
            # check if there is any slice that can be reduced
            # reduce it and then re-slice the remaining parts
            # accordingly
            for slice in result:
                if slice.is_divisible:
                    result.remove(slice)
                    slice.H = len(list(slice.cells)) - 1
                    part_result = slice.getslices()
        result += part_result
        return result
# EOF
