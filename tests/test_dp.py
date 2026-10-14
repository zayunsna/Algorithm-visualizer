import itertools
import random
import unittest
from algoviz.dp import fibonacci,lcs,knapsack
from algoviz.engine import Timeline


def brute_bag(items,cap):
    return max((sum(v for i,(w,v) in enumerate(items) if mask>>i&1)
                for mask in range(1<<len(items))
                if sum(w for i,(w,v) in enumerate(items) if mask>>i&1)<=cap),default=0)


def brute_lcs(a,b):
    options={''.join(a[i] for i in range(len(a)) if m>>i&1) for m in range(1<<len(a))}
    def subsequence(s):
        iterator=iter(b)
        return all(any(c==v for v in iterator) for c in s)
    return max((len(s) for s in options if subsequence(s)),default=0)


class DPTests(unittest.TestCase):
    def test_fibonacci_formula(self):
        values=[0,1]
        for _ in range(9): values.append(sum(values[-2:]))
        for n in range(9):
            state=Timeline(fibonacci(n)).finish()
            self.assertEqual(state['naive_result'],values[n])
            self.assertEqual(state['memo_result'],values[n])
            self.assertEqual(state['naive_calls'],2*values[n+1]-1)
            self.assertEqual(state['memo_calls'],1 if n<2 else 2*n-1)
            self.assertEqual(len(state['nodes']),state['naive_calls']+state['memo_calls'])

    def test_knapsack_250_bruteforce(self):
        rng=random.Random(502)
        for _ in range(250):
            items=[(rng.randint(1,9),rng.randint(0,20)) for _ in range(rng.randint(0,8))]
            cap=rng.randint(0,20)
            s=Timeline(knapsack(items,cap)).finish()
            self.assertEqual(s['result'],brute_bag(items,cap))
            self.assertEqual(sum(items[i][1] for i in s['selected']),s['result'])
            self.assertLessEqual(sum(items[i][0] for i in s['selected']),cap)
            self.assertEqual(s['cells'],len(items)*(cap+1))

    def test_lcs_250_bruteforce(self):
        rng=random.Random(205)
        for _ in range(250):
            a=''.join(rng.choice('ABC') for _ in range(rng.randint(0,7)))
            b=''.join(rng.choice('ABC') for _ in range(rng.randint(0,7)))
            s=Timeline(lcs(a,b)).finish()
            self.assertEqual(s['result'],brute_lcs(a,b))
            self.assertEqual(len(s['sequence']),s['result'])
            for source in (a,b):
                it=iter(source)
                self.assertTrue(all(any(c==v for v in it) for c in s['sequence']))
            self.assertEqual(s['cells'],len(a)*len(b))

    def test_invalid(self):
        for gen in (fibonacci(9),lcs('A'*13,'B'),knapsack([(0,2)],3),knapsack([],31)):
            with self.assertRaises(ValueError): list(gen)
