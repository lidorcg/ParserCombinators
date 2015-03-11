# Parser Combinator
__author__ = 'LidorCG'

import re


class NoMatch(Exception):
    pass


class AbstractParser:
    def match(self, s):
        pass

    def __str__(self):
        pass

    def __add__(self, other):
        return And(self, other)

    def __or__(self, other):
        return Or(self, other)

    def star(self):
        return Star(self)

    def plus(self):
        return Plus(self)

    def __sub__(self, other):
        return ButNot(self, other)

    def maybe(self):
        return Maybe(self)

    def pack(self, foo):
        return Pack(self, foo)

    def debug(self, msg):
        return Debug(self, msg)


class Parser(AbstractParser):
    def __init__(self, regex):
        self.p = re.compile(regex)

    def match(self, s):
        if self.p.match(s):
            i = self.p.match(s).end()
            return s[:i], s[i:]
        else:
            raise NoMatch

    def __str__(self):
        return 'Parser<' + self.p.pattern + '>'


class And(AbstractParser):
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def match(self, s):
        m1, r = self.p1.match(s)
        m2, r = self.p2.match(r)
        if type(m1) is not tuple:
            m1 = (m1,)
        if type(m2) is not tuple:
            m2 = (m2,)
        return m1 + m2, r

    def __str__(self):
        return str(self.p1) + ' + ' + str(self.p2)


class Or(AbstractParser):
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def match(self, s):
        try:
            return self.p1.match(s)
        except NoMatch:
            return self.p2.match(s)

    def __str__(self):
        return str(self.p1) + ' | ' + str(self.p2)


class Star(AbstractParser):
    def __init__(self, p):
        self.p = p

    def match(self, s):
        try:
            result, r = self.p.match(s)
            m, r = self.match(r)
            if m is ():
                return result, r
            if type(result) is not tuple:
                result = (result,)
            if type(m) is not tuple:
                m = (m,)
            return result + m, r
        except NoMatch:
            return (), s

    def __str__(self):
        return str(self.p) + '*'


class Plus(AbstractParser):
    def __init__(self, p):
        self.p = p + p.star()

    def match(self, s):
        return self.p.match(s)

    def __str__(self):
        return str(self.p) + '+'


class ButNot(AbstractParser):
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def match(self, s):
        try:
            self.p2.match(s)
        except NoMatch:
            return self.p1.match(s)
        raise NoMatch

    def __str__(self):
        return str(self.p1) + ' - ' + str(self.p2)


class Maybe(AbstractParser):
    def __init__(self, p):
        self.p = p

    def match(self, s):
        try:
            return self.p.match(s)
        except NoMatch:
            return (), s

    def __str__(self):
        return str(self.p) + '?'


class Pack(AbstractParser):
    def __init__(self, p, foo):
        self.p = p
        self.foo = foo

    def match(self, s):
        m, r = self.p.match(s)
        return self.foo(m), r


class Debug(AbstractParser):
    def __init__(self, p, msg):
        self.p = p
        self.msg = msg

    def match(self, s):
        print('\nAbout to pass the input:\n' + s + '\nto the <' + self.msg + '> parser\n')
        return self.p.match(s)


class Delayed(AbstractParser):
    def __init__(self, p):
        self.p = p

    def match(self, s):
        return self.p().match(s)


done = lambda m: ''.join(m)
