#!/usr/bin/env python
# encoding: utf-8


def gcd(a, b):
    if b == 0:
        return a
    else:
        r = a % b
        return gcd(b, r)


class Position(object):
    def __init__(self, row, column):
        self.row = row
        self.column = column

    def neighbours(self, R, C):
        neighbours = []
        if self.row+1 < R:
            neighbours.append(Position(self.row+1, self.column))
        if self.row-1 >= 0:
            neighbours.append(Position(self.row-1, self.column))
        if self.column+1 < C:
            neighbours.append(Position(self.row, self.column+1))
        if self.column-1 < C:
            neighbours.append(Position(self.row, self.column-1))
        return neighbours

    def __repr__(self):
        return '<Position ({0}, {1})>'.format(self.row, self.column)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Ingredient(object):
    """An ingredient has a count in a pizza, and at least one position"""
    def __init__(self, count, positions):
        self.count = count
        self.positions = positions

    def __repr__(self):
        return '<Ingredient {0}>'.format(self.positions)


class Pizza(object):
    def __init__(self, **kwargs):
        if kwargs.get('data'):
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
                            t_pos.append(Position(r, i))
                        else:
                            m_pos.append(Position(r, i))
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

    def slices(self):
        a = [
            i for i in [self.tomatoes, self.mushrooms]
            if i.count == min(self.tomatoes.count, self.mushrooms.count)
            ][0]
        if a == self.tomatoes:
            b = self.mushrooms
        else:
            b = self.tomatoes
        print(a, b)
        result = []
        seen = []
        for i in a.positions:
            for j in i.neighbours(self.rows, self.columns):
                if j in b.positions and j not in seen:
                    result.append((i, j))
                    seen.append(j)
                    break
        return result
