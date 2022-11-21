import random
import math


class Tape:
    def __init__(self, hex_=0x1, bits:int=7):
        self._bits = bits
        self.tape = hex_ - (hex_>>bits<<bits)

    def __str__(self) -> str:
        return format(self.tape, f'0{math.ceil(self._bits/4)}x')
        # return format(self.tape, f'0{self._bits}b')

    def copy(self) -> 'Tape':
        return Tape(self.tape, self._bits)

    def __eq__(self, o: 'Tape') -> bool:
        return self.tape == o.tape

    def __hash__(self) -> int:
        return self.tape.__hash__()

    def get_bit_from_left(self, i):
        i = i % self._bits
        return self.tape >> (self._bits-i-1) & 1

    def search(self, pattern: int, bits: int = 4, start_idx: int = 0) -> int:
        """Return index (from left)."""
        for i in range(start_idx, start_idx+self._bits):
            i %= self._bits
            matched = 1
            for j in range(bits):
                matched &= ~ (self.get_bit_from_left(i+j) ^ (pattern >> (bits-j-1) & 1))
            if matched == 1:
                return i
        return None

class Machine:
    def __init__(self):   # head_bits:int=4, tail_bits:int=4
        self.tranT = 0
        self.tranM = 0
        self.head = 0
        self.tail = 0
        self.initial_state = 1

    def __str__(self) -> str:
        h = self.get_hex()
        # return format(h, '016b')
        return format(h, '04x')

    def __eq__(self, o: 'Machine') -> bool:
        return self.tranT==o.tranT and self.tranM==o.tranM and self.head==o.head and self.tail==o.tail

    def __hash__(self) -> int:
        return (self.tranT, self.tranM, self.head, self.tail).__hash__()

    @classmethod
    def from_hex(cls, hex_) -> 'Machine':
        m = cls()
        m.tranT = hex_ >> 12 & 0b1111
        m.tranM = hex_ >> 8 & 0b1111
        m.head = hex_ >> 4 & 0b1111
        m.tail = hex_ & 0b1111
        return m

    @classmethod
    def from_tape(cls, tape: Tape) -> 'Machine':
        m = cls()
        m.tranT = (tape.get_bit_from_left(0) << 3) + (tape.get_bit_from_left(2) << 2) + (tape.get_bit_from_left(4) << 1) + (tape.get_bit_from_left(6))
        m.tranM = (tape.get_bit_from_left(1) << 3) + (tape.get_bit_from_left(3) << 2) + (tape.get_bit_from_left(5) << 1) + (tape.get_bit_from_left(7))
        m.head = (tape.get_bit_from_left(8) << 3) + (tape.get_bit_from_left(10) << 2) + (tape.get_bit_from_left(12) << 1) + (tape.get_bit_from_left(14))
        m.tail = (tape.get_bit_from_left(9) << 3) + (tape.get_bit_from_left(11) << 2) + (tape.get_bit_from_left(13) << 1) + (tape.get_bit_from_left(15))
        return m

    def get_hex(self) -> int:
        return (self.tranT<<12) + (self.tranM<<8) + (self.head<<4) + self.tail

    def rewrite_tape(self, tape: Tape, noise: float = 0) -> Tape:
        ihead = tape.search(self.head)
        if ihead is None:
            # return tape.copy()  # TODO ?
            return None
        itail = tape.search(self.tail, start_idx=ihead+1)
        if itail is None or ihead == itail:
            # return tape.copy()
            return None

        state = self.initial_state
        t = tape.tape
        for i in range(ihead, itail + tape._bits if itail < ihead else itail):
            i %= tape._bits
            key = (tape.get_bit_from_left(i) << 1) + state
            t_ = self.tranT >> (3-key) & 1
            state = self.tranM >> (3-key) & 1
            if random.random() < noise:
                t_ = 1-t_
            t = (t-(t>>(tape._bits-i-1)<<(tape._bits-i-1))) + (t>>(tape._bits-i)<<(tape._bits-i)) + (t_<<(tape._bits-i-1))
        return Tape(t, tape._bits)
