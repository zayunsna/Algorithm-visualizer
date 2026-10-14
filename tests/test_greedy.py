import random
import unittest
from fractions import Fraction
from functools import lru_cache
from algoviz.engine import Timeline
from algoviz.greedy import coins_compare,activity_compare,bag_compare
from tests.test_dp import brute_bag


def brute_coin(coins,amount):
    @lru_cache(None)
    def visit(value):
        if value==0: return 0
        results=[visit(value-c) for c in coins if c<=value]
        return min((v+1 for v in results if v is not None),default=None)
    return visit(amount)


def brute_activity(intervals):
    ordered=sorted(intervals)
    def visit(index,end):
        if index==len(ordered): return 0
        skip=visit(index+1,end)
        a,b=ordered[index]
        return max(skip,1+visit(index+1,b)) if a>=end else skip
    return visit(0,0)


def fractional_vertices(items,cap):
    best=Fraction(0)
    # Every LP vertex has at most one strictly fractional item.
    for mask in range(1<<len(items)):
        weight=sum(w for i,(w,v) in enumerate(items) if mask>>i&1)
        value=sum(v for i,(w,v) in enumerate(items) if mask>>i&1)
        if weight>cap: continue
        best=max(best,Fraction(value))
        for i,(w,v) in enumerate(items):
            if not mask>>i&1:
                best=max(best,value+min(Fraction(1),Fraction(cap-weight,w))*v)
    return best


class GreedyTests(unittest.TestCase):
    def test_empty_unreachable_and_invalid(self):
        self.assertEqual(Timeline(coins_compare([2],0)).finish()['optimal_count'],0)
        self.assertIsNone(Timeline(coins_compare([2],3)).finish()['optimal_count'])
        stuck=Timeline(coins_compare([3,4],6)).finish()
        self.assertIsNone(stuck['greedy_count']); self.assertEqual(stuck['optimal_count'],2); self.assertTrue(stuck['failed'])
        self.assertEqual(Timeline(activity_compare([])).finish()['optimal_count'],0)
        self.assertEqual(Timeline(bag_compare([],0)).finish()['optimal_value'],0)
        for source in (coins_compare([],3),coins_compare([0,1],3),coins_compare([1],151),
                       activity_compare([(2,2)]),activity_compare([(0,101)]),bag_compare([(1,-1)],3)):
            with self.assertRaises(ValueError): list(source)
    def test_coin_counterexample_and_canonical(self):
        s=Timeline(coins_compare([1,3,4],6)).finish()
        self.assertEqual(s['greedy'],[4,1,1]); self.assertEqual(s['optimal'],[3,3]); self.assertTrue(s['failed'])
        for amount in range(151):
            s=Timeline(coins_compare([1,5,10,25],amount)).finish()
            self.assertEqual(s['greedy_count'],s['optimal_count'])
            self.assertEqual(s['optimal_count'],brute_coin((1,5,10,25),amount))

    def test_random_coins(self):
        rng=random.Random(51)
        for _ in range(150):
            coins=rng.sample(range(1,12),rng.randint(1,5)); amount=rng.randint(0,25)
            s=Timeline(coins_compare(coins,amount)).finish()
            self.assertEqual(s['optimal_count'],brute_coin(tuple(coins),amount))
            if s['optimal_count'] is not None: self.assertEqual(sum(s['optimal']),amount)

    def test_activity_counterexamples(self):
        for intervals,rule in [([(0,10),(1,2),(2,3),(3,4)],'start'), ([(0,4),(4,8),(3,5)],'duration')]:
            s=Timeline(activity_compare(intervals,rule)).finish(); self.assertTrue(s['failed'])
            good=Timeline(activity_compare(intervals,'finish')).finish(); self.assertFalse(good['failed'])

    def test_random_activity(self):
        rng=random.Random(42)
        for _ in range(160):
            intervals=[]
            for _ in range(rng.randint(0,8)):
                a=rng.randint(0,15); intervals.append((a,a+rng.randint(1,8)))
            s=Timeline(activity_compare(intervals,'finish')).finish()
            self.assertEqual(s['greedy_count'],brute_activity(intervals))
            self.assertEqual(s['optimal_count'],brute_activity(intervals))

    def test_bag_vertices_and_enumeration(self):
        rng=random.Random(37)
        for _ in range(150):
            items=[(rng.randint(1,8),rng.randint(0,18)) for _ in range(rng.randint(0,7))]; cap=rng.randint(0,20)
            s=Timeline(bag_compare(items,cap)).finish()
            self.assertEqual(s['optimal_value'],brute_bag(items,cap))
            self.assertEqual(s['fractional_value'],fractional_vertices(items,cap))
        s=Timeline(bag_compare([(2,12),(4,20),(6,24)],10)).finish()
        self.assertEqual((s['fractional_value'],s['greedy_value'],s['optimal_value']),(48,32,44))
        self.assertTrue(s['failed'])
