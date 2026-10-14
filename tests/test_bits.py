"""Independent digit-list references for finite-width operations."""
import itertools
import random
import unittest
from copy import deepcopy
from algoviz import bits
from algoviz.engine import Timeline
from tests.test_dp import brute_bag


def digits(value,width):
    value=value % (2**width)
    return [int(c) for c in format(value,f'0{width}b')]


def decode(values):
    return sum(v*2**(len(values)-1-i) for i,v in enumerate(values))


def reference_logic(aa,bb,op):
    if op=='AND': return decode([int(a==1 and b==1) for a,b in zip(aa,bb)])
    if op=='OR': return decode([int(a==1 or b==1) for a,b in zip(aa,bb)])
    if op=='XOR': return decode([int(a!=b) for a,b in zip(aa,bb)])
    return decode([1-a for a in aa])


def reference_shift(a,width,amount,op):
    values=digits(a,width)
    if op=='LEFT': return decode(values[amount:]+[0]*amount)
    fill=values[0] if op=='ARITHMETIC' else 0
    return decode([fill]*amount+values[:width-amount])


def result(source,check_render=False):
    final=None
    rendered=None
    for e in source:
        if ('result',) in e.changes: final=e.changes[('result',)]
        rows=e.changes.get(('rows',))
        if rows and isinstance(rows[-1]['value'],list) and all(v is not None for v in rows[-1]['value']):
            rendered=decode(rows[-1]['value'])
    if check_render and rendered!=final: raise AssertionError((rendered,final))
    return final


class BitTests(unittest.TestCase):
    def test_all_65536_pairs_each_logic_generator(self):
        cached=[digits(a,8) for a in range(256)]
        for a in range(256):
            for b in range(256):
                for op in ('AND','OR','XOR'):
                    expected=reference_logic(cached[a],cached[b],op)
                    self.assertEqual(bits.logic_result(a,b,8,op),expected)
                    self.assertEqual(result(bits.logic(a,b,8,op),True),expected,(a,b,op))
                    self.assertTrue(0<=expected<256)
        for a in range(256): self.assertEqual(result(bits.logic(a,0,8,'NOT'),True),reference_logic(cached[a],cached[0],'NOT'))

    def test_all_8bit_shifts_and_negation(self):
        for a in range(256):
            for amount in range(9):
                for op in ('LEFT','LOGICAL','ARITHMETIC'):
                    expected=reference_shift(a,8,amount,op)
                    self.assertEqual(bits.shift_result(a,8,amount,op),expected)
                    self.assertEqual(result(bits.shifts(a,8,amount,op)),expected)
            self.assertEqual(result(bits.complement(a,8)),(-a)%256)
            signed_ref=decode(digits(a,8)[1:])-digits(a,8)[0]*128
            self.assertEqual(bits.signed(a,8),signed_ref)
            for op in ('LOGICAL','ARITHMETIC'):
                self.assertEqual(result(bits.shifts(signed_ref,8,8,op)),reference_shift(signed_ref,8,8,op))

    def test_all_8bit_tricks_and_counters(self):
        for a in range(256):
            s=Timeline(bits.clear_lowest(a,8)).finish()
            self.assertEqual(s['iterations'],bin(a).count('1')); self.assertEqual(s['result'],0)
            values=digits(a,8)
            lowest=next((2**k for k,v in enumerate(reversed(values)) if v==1),0)
            self.assertEqual(result(bits.isolate(a,8)),lowest)
            original=values[:]
            if 1 in original: original[len(original)-1-original[::-1].index(1)]=0
            self.assertEqual(result(bits.clear_lowest(a,8,repeat=False)),decode(original))
            power=Timeline(bits.clear_lowest(a,8,power=True)).finish()
            self.assertEqual(power['is_power'],a in [2**k for k in range(8)])
            self.assertEqual(power['nonzero'],a!=0)

    def test_subsets_against_combinations_and_knapsack(self):
        rng=random.Random(184)
        for width in (4,8,16):
            for n in range(min(8,width)+1):
                items=[(rng.randint(1,8),rng.randint(0,20)) for _ in range(n)]
                s=Timeline(bits.subsets(items,10,width))
                actual=[]
                while s.forward():
                    if s.events[s.cursor-1].action=='subset': actual.append(tuple(s.state['selected']))
                expected=set(itertools.chain.from_iterable(itertools.combinations(range(n),k) for k in range(n+1)))
                self.assertEqual(set(actual),expected); self.assertEqual(len(actual),2**n)
                self.assertEqual(s.state['best'],brute_bag(items,10))

    def test_4_and_16bit_boundaries_and_outside_width(self):
        for width in (4,16):
            limit=2**width
            for a in (0,1,limit-1,limit//2,-limit//2,-1,limit+1,2*limit+5):
                for b in (0,1,limit-1,limit//2,limit+1,-1):
                    for op in ('AND','OR','XOR','NOT'):
                        self.assertEqual(result(bits.logic(a,b,width,op)),reference_logic(digits(a,width),digits(b,width),op))
                self.assertEqual(result(bits.complement(a,width)),(-a)%limit)
                for amount in (0,1,width):
                    for op in ('LEFT','LOGICAL','ARITHMETIC'):
                        self.assertEqual(result(bits.shifts(a,width,amount,op)),reference_shift(a,width,amount,op))
                self.assertEqual(Timeline(bits.clear_lowest(a,width)).finish()['iterations'],bin(a%limit).count('1'))
                lowest=next((2**k for k,v in enumerate(reversed(digits(a,width))) if v),0)
                self.assertEqual(result(bits.isolate(a,width)),lowest)
                self.assertEqual(Timeline(bits.clear_lowest(a,width,power=True)).finish()['is_power'],a%limit in [2**k for k in range(width)])
            minimum=Timeline(bits.complement(-limit//2,width)).finish()
            self.assertTrue(minimum['overflow']); self.assertEqual(minimum['result'],limit//2)

    def test_xor_singleton_by_frequencies(self):
        rng=random.Random(201)
        for width in (4,8,16):
            for _ in range(30):
                words=rng.sample(range(2**width),5); values=[words[0]]+words[1:]*2; rng.shuffle(values)
                self.assertEqual(result(bits.unique_xor(values,width)),words[0])
        with self.assertRaises(ValueError): list(bits.unique_xor([1,1,2,2],8))
        with self.assertRaises(ValueError): list(bits.unique_xor([1,1,1,2],8))
        self.assertEqual(result(bits.unique_xor([-1,5,-1,0x103,5],8)),3)
        self.assertEqual(result(bits.unique_xor([0],8)),0)

    def test_all_generators_reversible_and_rows_masked(self):
        sources=[bits.logic(-5,300,8,op) for op in ('AND','OR','XOR','NOT')]+[
            bits.shifts(-8,8,8,'ARITHMETIC'),bits.shifts(255,8,8,'LEFT'),bits.complement(-128,8),
            bits.clear_lowest(152,8),bits.isolate(152,8),bits.clear_lowest(0,8,power=True),
            bits.unique_xor([5,12,5,7,12],8),bits.subsets([(2,12),(4,20),(6,24)],10,8)]
        for source in sources:
            t=Timeline(source); snapshots=[{}]
            while t.forward():
                snapshot=deepcopy(t.state); snapshots.append(snapshot)
                if snapshot.get('result') is not None: self.assertTrue(0<=snapshot['result']<256)
                for row in snapshot.get('rows',[]):
                    if isinstance(row['value'],int): self.assertTrue(0<=row['value']<256)
                    else:
                        self.assertEqual(len(row['value']),8)
                        self.assertTrue(all(d in (0,1,None) for d in row['value']))
            for snapshot in reversed(snapshots[:-1]): t.back(); self.assertEqual(t.state,snapshot)
            for snapshot in snapshots[1:]: t.forward(); self.assertEqual(t.state,snapshot)

    def test_invalid_parameters(self):
        for source in (bits.logic(1,2,7),bits.logic(1,2,8,'NAND'),bits.shifts(1,8,9),
                       bits.shifts(1,8,-1),bits.subsets([(1,1)]*5,3,4)):
            with self.assertRaises(ValueError): list(source)
