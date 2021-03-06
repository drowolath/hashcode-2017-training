#!/usr/bin/env python
# encoding: utf-8

"""
Simple library to cut correct slices out of a pizza,
maximizing the total number of cells in all slices
"""

import collections
import math
import sys


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

    def neighbours(self, pizza, direction='all'):
        """A cell has at most 4 adjacent cells; we don't count diagonals"""
        neighbours = []
        if self.row+1 < pizza.rows:
            neighbours.append(Cell(self.row+1, self.column))
            if direction == 'down':
                cell = [
                    i for i in pizza.cells
                    if i == Cell(self.row+1, self.column)
                    ][0]
                return cell
        if self.row-1 >= 0:
            neighbours.append(Cell(self.row-1, self.column))
            if direction == 'up':
                cell = [
                    i for i in pizza.cells
                    if i == Cell(self.row-1, self.column)
                    ][0]
                return cell
        if self.column+1 < pizza.columns:
            neighbours.append(Cell(self.row, self.column+1))
            if direction == 'right':
                cell = [
                    i for i in pizza.cells
                    if i == Cell(self.row, self.column+1)
                    ][0]
                return cell
        if self.column-1 >= 0:
            neighbours.append(Cell(self.row, self.column-1))
            if direction == 'left':
                cell = [
                    i for i in pizza.cells
                    if i == Cell(self.row, self.column-1)
                    ][0]
                return cell
        if direction == 'all':
            return neighbours
        else:
            return None

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


class Pizza:
    """A pizza is represented by a RxC rectangle; each cell of the pizza
    contains either a mushroom or a tomato"""
    def __init__(self, rows, columns, tomatoes, mushrooms):
        """"rows" and "columns" are integers in range(1, 1001);
        "tomatoes" and mushrooms" are arrays of Cell objects
        """
        self.rows = rows
        self.columns = columns
        self.tomatoes = tomatoes
        self.mushrooms = mushrooms

    def __repr__(self):
        return '<Pizza {r}x{c} T={t} M={m}>'.format(
            r=self.rows, c=self.columns,
            t=len(self.tomatoes), m=len(self.mushrooms)
            )

    def __contains__(self, item):
        return item in self.cells

    @staticmethod
    def readfromfile(filepath):
        tomatoes = []
        mushrooms = []
        with open(filepath) as infile:
            lines = infile.readlines()
            rows, columns, L, H = [
                int(i) for i in lines[0].rstrip('\n').split()
                ]
            r = 0
            for line in lines[1:]:
                line = line.rstrip('\n')
                for i in range(len(line)):
                    if line[i] == 'T':
                        tomatoes.append(Cell(r, i, 'T'))
                    else:
                        mushrooms.append(Cell(r, i, 'M'))
                r += 1
        p = Pizza(rows, columns, tomatoes, mushrooms)
        p.L = L
        p.H = H
        return p

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

    def slice(self, rows, columns):
        """get valid slices in a pizza: starting from the upper left cell,
        so that each valid slice contains rows*columns cells"""
        start = sorted(list(self.cells))[0]
        upper_left = start
        lower_right = upper_left + Cell(rows-1, columns-1)
        result = []
        slice = Slice(
            rows,
            columns,
            list(
                filter(
                    lambda x: x in cell_range(upper_left, lower_right),
                    self.tomatoes
                    )
                ),
            list(
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
                slice = Slice(
                    rows,
                    columns,
                    list(
                        filter(
                            lambda x: x in cell_range(upper_left, lower_right),
                            self.tomatoes
                            )
                        ),
                    list(
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


class Slice(Pizza):
    def __repr__(self):
        return '<Slice {r}x{c} T={t} M={m}>'.format(
            r=self.rows, c=self.columns,
            t=len(self.tomatoes), m=len(self.mushrooms)
            )

    @property
    def upper_left(self):
        return self.cells[0]

    @property
    def lower_right(self):
        return self.cells[-1]

    @property
    def is_divisible(self):
        """Verifies if we can get more than one valid slice in the pizza"""
        t = len(self.tomatoes)
        m = len(self.mushrooms)
        return (t >= 2*self.L and m >= 2*self.L)

    @property
    def left_edge(self):
        cell = self.upper_left
        r = 1
        yield cell
        while r < self.rows:
            cell += Cell(1, 0)
            r += 1
            yield [i for i in self.cells if i == cell][0]

    @property
    def down_edge(self):
        cell = self.lower_right
        c = 1
        yield cell
        while c < self.columns:
            cell -= Cell(0, 1)
            c += 1
            yield [i for i in self.cells if i == cell][0]

    @property
    def right_edge(self):
        cell = self.lower_right
        r = 1
        yield cell
        while r < self.rows:
            cell -= Cell(1, 0)
            r += 1
            yield [i for i in self.cells if i == cell][0]

    @property
    def up_edge(self):
        cell = self.upper_left
        c = 1
        yield cell
        while c < self.columns:
            cell += Cell(0, 1)
            c += 1
            yield [i for i in self.cells if i == cell][0]

    def overlaps(self, other):
        """Verifies if (part of) the pizza overlaps another one"""
        if not hasattr(other, 'cells'):
            return False
        return bool([i for i in self.cells if i in other.cells])


def execute(filepath):
    p = None
    p = Pizza.readfromfile(filepath)
    slices = p.getslices()
    # this already contains the max number of valid slices
    result = []
    cells_in_slices = []
    for slice in slices:
        for cell in slice.cells:
            cells_in_slices.append(cell)
    cells_in_slices = sorted(cells_in_slices)
    for slice in slices:
        if slice.rows*slice.columns == p.H:
            result.append(slice)
        else:
            # We'll try to expand the slice to it's maximum.
            left = True
            down = True
            right = True
            up = True
            while left or down or right or up:
                if left:
                    neighbours = []
                    for _ in slice.left_edge:
                        cell = _.neighbours(p, direction='left')
                        if cell:
                            neighbours.append(cell)
                    overlapping = []
                    for cell in neighbours:
                        if cell in cells_in_slices:
                            overlapping.append(cell)
                    if overlapping or not neighbours:
                        # if at least one neighbouring cell on the left
                        # is already part of another slice, we block direction
                        left = False
                    else:
                        # expand the slice on the left
                        if slice.rows*(slice.columns+1) > p.H:
                            left = False
                        else:
                            slice.columns += 1
                            slice.tomatoes += [
                                i for i in neighbours
                                if i.ingredient == 'T'
                                ]
                            slice.mushrooms += [
                                i for i in neighbours
                                if i.ingredient == 'M'
                                ]
                            cells_in_slices += neighbours
                if down:
                    neighbours = []
                    for _ in slice.down_edge:
                        cell = _.neighbours(p, direction='down')
                        if cell:
                            neighbours.append(cell)
                    overlapping = []
                    for cell in neighbours:
                        if cell in cells_in_slices:
                            overlapping.append(cell)
                    if overlapping or not neighbours:
                        # if at least one neighbouring cell on the down side
                        # is already part of another slice, we block direction
                        down = False
                    else:
                        # expand the slice on the down side
                        if (slice.rows+1)*slice.columns > p.H:
                            down = False
                        else:
                            slice.rows += 1
                            slice.tomatoes += [
                                i for i in neighbours
                                if i.ingredient == 'T'
                                ]
                            slice.mushrooms += [
                                i for i in neighbours
                                if i.ingredient == 'M'
                                ]
                            cells_in_slices += neighbours
                if right:
                    neighbours = []
                    for _ in slice.right_edge:
                        cell = _.neighbours(p, direction='right')
                        if cell:
                            neighbours.append(cell)
                    overlapping = []
                    for cell in neighbours:
                        if cell in cells_in_slices:
                            overlapping.append(cell)
                    if overlapping or not neighbours:
                        # if at least one neighbouring cell on the right
                        # is already part of another slice, we block direction
                        right = False
                    else:
                        # expand the slice on the right
                        if slice.rows*(slice.columns+1) > p.H:
                            right = False
                        else:
                            slice.columns += 1
                            slice.tomatoes += [
                                i for i in neighbours
                                if i.ingredient == 'T'
                                ]
                            slice.mushrooms += [
                                i for i in neighbours
                                if i.ingredient == 'M'
                                ]
                            cells_in_slices += neighbours
                if up:
                    neighbours = []
                    for _ in slice.up_edge:
                        cell = _.neighbours(p, direction='up')
                        if cell:
                            neighbours.append(cell)
                    overlapping = []
                    for cell in neighbours:
                        if cell in cells_in_slices:
                            overlapping.append(cell)
                    if overlapping or not neighbours:
                        # if at least one neighbouring cell on the up side
                        # is already part of another slice, we block direction
                        up = False
                    else:
                        # expand the slice on the up side
                        if (slice.rows+1)*slice.columns > p.H:
                            up = False
                        else:
                            slice.rows += 1
                            slice.tomatoes += [
                                i for i in neighbours
                                if i.ingredient == 'T'
                                ]
                            slice.mushrooms += [
                                i for i in neighbours
                                if i.ingredient == 'M'
                                ]
                            cells_in_slices += neighbours
            result.append(slice)
    answer = '{}\n'.format(len(result))
    for slice in result:
        answer += '{up_row} {left_column} {down_row} {right_column}\n'.format(
            up_row=slice.upper_left.row,
            down_row=slice.lower_right.row,
            left_column=slice.upper_left.column,
            right_column=slice.lower_right.column
            )
    print(answer)
    with open('/tmp/pizza_answer', 'w') as f:
        f.write(answer)

if __name__ == '__main__':
    execute(sys.argv[1])
# EOF
