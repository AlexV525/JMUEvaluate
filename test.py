# -*- coding: utf-8 -*-

# The Bit class.
__author__ = "yche829"


class Bit:

    def __init__(self, a_val):
        if a_val not in [0, 1, 4, 5]:
            raise ValueError
        self.val = a_val

    def nor(self, b):
        if self:
            return ZERO
        elif b:
            return ZERO
        else:
            return ONE

    def __str__(self):
        return str(self.val)

    def __bool__(self):
        if self.val > 3:
            return True
        elif self.val < 2:
            return False

    def __invert__(self):
        if self.nor(self):
            return ONE
        else:
            return ZERO

    def __or__(self, b):
        if not self.nor(b):
            return ONE
        else:
            return ZERO

    def __and__(self, b):
        if not ((not self) or (not b)):
            return ONE
        else:
            return ZERO

    def __xor__(self, b):
        """Custom XOR. Using this for full adder.
        Yes native XOR worked as well but this version doesn't
        use any binary logical operators. :P
        Build on OR, AND, NOT.
        """
        return (self or b) and (not (self and b))

    def full_adder(self, b):
        global carry
        bitsum = (self ^ b or carry) and (not (self ^ b and carry))  # Using custom XOR
        carry = (self and b) or (self and carry) or (b and carry)
        """bitsum and carry need to be convert before return."""
        if bitsum:
            bitsum = ONE
        else:
            bitsum = ZERO
        if carry:
            carry = ONE
        else:
            carry = ZERO
        return bitsum


ZERO = Bit(0)
ONE = Bit(5)


class SInteger:

    def __init__(self, bit_str=''):
        self.val = []
        bit_len = len(bit_str)
        for i in range(LEN):
            if i < bit_len:
                self.val.append(Bit(int(bit_str[i])) | Bit(int(bit_str[i])))
            elif bit_len > 0:
                self.val.insert(0, Bit(int(bit_str[0])) | Bit(int(bit_str[0])))
            else:
                self.val.insert(0, ZERO)

    def __str__(self):
        strval = ''
        for i in range(LEN):
            strval = strval + str(self.val[i])
        return strval

    def __len__(self):
        return len(self.val)

    def __invert__(self):
        invrlt = SInteger('')
        for i in range(LEN):
            invrlt.val[i] = ~self.val[i]
        return invrlt

    def __int__(self):
        """Using is_negative flag to deal with unsigned bitwise."""
        is_negative = False
        temp_list = []
        if int(str(self)[0]) == int(str(ONE)):
            is_negative = True
            self = ~self
        bit_str = str(int(str(self)))
        for i in range(len(bit_str)):
            if int(bit_str[i]) == int(str(ONE)):
                temp_list.append("1")
            else:
                temp_list.append("0")
        bitrlt = ''.join(temp_list)
        if is_negative:
            intrlt = 0 - (int(bitrlt, 2) + 1)
        else:
            intrlt = int(bitrlt, 2)
        return intrlt

    def __ge__(self, other):
        return int(self) >= int(other)

    def __or__(self, other):
        orrlt = ""
        bit_list = []
        self_str = str(self)
        other_str = str(other)
        for i in (range(LEN)):
            if int(self_str[i]) or int(other_str[i]):
                bit_list.append(str(ONE))
            else:
                bit_list.append(str(ZERO))
        orrlt = orrlt.join(bit_list)
        return orrlt

    def __and__(self, other):
        andrlt = ""
        bit_list = []
        self_str = str(self)
        other_str = str(other)
        for i in (range(LEN)):
            if int(self_str[i]) and int(other_str[i]):
                bit_list.append(str(ONE))
            else:
                bit_list.append(str(ZERO))
        andrlt = andrlt.join(bit_list)
        return andrlt

    def __lshift__(self, k):
        if k <= 0:  # Prevent reverse shift.
            raise ValueError
        fill_str = ""
        fill_bit = []
        for i in range(k):
            fill_bit.append(str(ZERO))
        fill_str = fill_str.join(fill_bit)
        return str(self)[k:] + fill_str

    def __rshift__(self, k):
        """Prevent reverse shift."""
        if k <= 0:
            raise ValueError
        fill_str = ""
        fill_bit = []
        """Check if it's unsigned and use different fill."""
        if str(self)[0] == str(ONE):
            for i in range(k):
                fill_bit.append(str(ONE))
        else:
            for i in range(k):
                fill_bit.append(str(ZERO))
        fill_str = fill_str.join(fill_bit)
        return fill_str + str(self)[:-k]

    def __add__(self, other):
        global carry
        carry = ZERO
        self_bit = []
        other_bit = []
        add_bit = []
        add_str = ""
        for i in reversed(range(LEN)):
            """Using FOR to build a custom length of full adder from low bitwise to high bitwise."""
            rev_order = LEN-(i+1)  # Reversed order.
            self_bit.append(str(self)[i])
            other_bit.append(str(other)[i])
            add_bit.append(str(
                Bit(int(self_bit[rev_order]))
                .full_adder(
                    Bit(int(other_bit[rev_order]))
                )
            ))
        add_bit.reverse()  # Reverse again for correct bitwise.
        addrlt = SInteger(add_str.join(add_bit))
        return addrlt


    def __sub__(self, other):
        other += SInteger(str(ONE))  # Plus ONE for complement.
        other = ~other  # Invert for reversed binary.
        subrlt = self + other
        return subrlt

print(""" Test 1 Part 1 """)
carry = ZERO
c = Bit(4)
d = Bit(5)
e = Bit(5)
f = Bit(5)
print(c.full_adder(d))
print(carry)
print(e.full_adder(f))
print(carry)

print("")  # Blank line.
print(""" Test 1 Part 2 """)
carry = ZERO
c = Bit(4)
d = Bit(4)
e = Bit(1)
f = Bit(1)
print(c.full_adder(d))
print(carry)
print(e.full_adder(f))
print(carry)

print(""" Test 1 Part 3 """)
carry = ZERO
c = Bit(4)
d = Bit(0)
e = Bit(1)
f = Bit(1)
print(c.full_adder(d))
print(carry)
print(e.full_adder(f))
print(carry)

print(""" Test 1 Part 4 """)
carry = ZERO
c = Bit(4)
d = Bit(0)
e = Bit(5)
f = Bit(4)

print(c.full_adder(d))
print(carry)
print(e.full_adder(f))
print(carry)

print("")  # Blank line.
print(""" Test 2 Part 1 """)
LEN=16
inta = SInteger('1050405')
print('a is', inta)
print('Length of a is', len(inta))
print('Integer value of a is', int(inta))
intb = SInteger('55111140')
print('b is', intb)
print('Length of b is', len(intb))
print('Integer value of b is', int(intb))

print("")  # Blank line.
print(""" Test 2 Part 2 """)
LEN=16
inta = SInteger('1050405')
print('a is', inta)
print('Length of a is', len(inta))
print('Integer value of a is', int(inta))
intb = SInteger('55111140')
print('b is', intb)
print('Length of b is', len(intb))
print('Integer value of b is', int(intb))

intc = ~inta
print('NOT value of a is', intc)
print('Boolean value of a >= b is', inta >= intb)
print('a or b is', inta|intb)
print('a and b is', inta&intb)

print("")  # Blank line.
print(""" Test 2 Part 3 """)
LEN=32
inth = SInteger('551050405')
print('h is', inth)
print('Length of h is', len(inth))
print('Integer value of h is', int(inth))
inti = SInteger('41055111140')
print('i is', inti)
print('Length of i is', len(inti))
print('Integer value of i is', int(inti))

print("")  # Blank line.
print(""" Test 2 Part 4 """)
LEN=32
inth = SInteger('551050405')
print('h is', inth)
print('Length of h is', len(inth))
print('Integer value of h is', int(inth))
inti = SInteger('41055111140')
print('i is', inti)
print('Length of i is', len(inti))
print('Integer value of i is', int(inti))

intj = ~inti
print('NOT value of i is', intj)
print('Boolean value of h >= i is', inth >= inti)
print('h or i is', inth|inti)
print('h and i is', inth&inti)

print("")  # Blank line.
print(""" Test 3 Part 1 """)
LEN=16
inta = SInteger('1050405')
print('a is', inta)
intb = SInteger('55111140')
print('b is', intb)
print('b left shift by 7 is', intb<<7)
print('b left shift by 1 is', intb<<1)
print('a left shift by 7 is', inta<<7)
print('a left shift by 1 is', inta<<1)

print("")  # Blank line.
print(""" Test 3 Part 2 """)
LEN=16
inta = SInteger('1050405')
print('a is', inta)
intb = SInteger('55111140')
print('b is', intb)
carry = ZERO
rlt = inta + intb
carry = ZERO
print('a + b is', rlt, 'carry is', carry, 'integer is', int(rlt))
carry = ZERO
rlt = inta - intb
carry = ZERO
print('a - b is', rlt, 'carry is', carry, 'integer is', int(rlt))

print("")  # Blank line.
print(""" Test 3 Part 3 """)
LEN=32
inth = SInteger('551050405')
print('h is', inth)
inti = SInteger('41055111140')
print('i is', inti)
print('h left shift by 7 is', inth<<7)
print('h left shift by 7 is', inth<<17)
print('i left shift by 7 is', inti<<7)
print('i left shift by 7 is', inti<<27)

print("")  # Blank line.
print(""" Test 3 Part 4 """)
LEN=32
inth = SInteger('551050405')
print('h is', inth)
inti = SInteger('41055111140')
print('i is', inti)
carry = ZERO
rlt = inth+inti
carry = ZERO
print('h + i is', rlt, 'carry is', carry, 'integer is', int(rlt))
carry = ZERO
rlt = inth-inti
carry = ZERO
print('h - i is', rlt, 'carry is', carry, 'integer is', int(rlt))

print("")  # Blank line.
print(""" Test 3 Part 5 """)
LEN=8
inth = SInteger('55550405')
inti = SInteger('05111140')
print('h right shift by 2 is', inth>>2)
print('h right shift by 1 is', inth>>1)
print('i right shift by 3 is', inti>>3)
print('i right shift by 2 is', inti>>2)