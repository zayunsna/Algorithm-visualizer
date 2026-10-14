"""Reproducible inputs and executable lesson steps."""
from dataclasses import dataclass
from .pathfinding import Grid

@dataclass(frozen=True)
class Lesson:
    title: str
    module: str
    question: str
    steps: tuple

    @property
    def default_speed(self):
        return (60 if 'Guided' in self.title else 30) if self.group=='Path' else 12 if self.group=='DP' else (3 if self.module=='activity' else 6 if self.module=='bag' else 10) if self.group=='Greedy' else 3 if self.module in ('bit_negate','bit_clear') else 1 if self.module in ('bit_shift','bit_subset') else 2 if self.module in ('bit_logic','bit_power') else 4

    @property
    def group(self):
        return 'Bits' if self.module.startswith('bit_') else 'Path' if self.module=='path' else 'DP' if self.module in ('fib','lcs','knapsack') else 'Greedy'

LESSONS = [
    Lesson('Path: BFS vs DFS', 'path', 'Does choosing depth first preserve the shortest path?', ()),
    Lesson('Path: Swamp costs', 'path', 'Fewest edges or lowest cost: which route avoids the swamp?', ()),
    Lesson('Path: Guided search', 'path', 'How many cells can a safe heuristic save?', ()),
    Lesson('Path: Heuristic trap', 'path', 'Can h x 3 choose a faster but more expensive route?', ()),
    Lesson('DP: Fibonacci calls', 'fib', 'Which repeated calls disappear after memoization?', ('Run naive','Run memo','Compare n=8')),
    Lesson('DP: LCS traceback', 'lcs', 'Which neighboring values determine the current cell?', ('Fill table','Trace back','Swap strings')),
    Lesson('DP: 0/1 knapsack', 'knapsack', 'Why does each item refer only to the previous row?', ('Fill table','Trace back','Compare greedy')),
    Lesson('Greedy: Coin counterexample', 'coin', 'Why does taking 4 prevent a two-coin solution for 6?', ('Run greedy','Run optimal','Canonical coins')),
    Lesson('Greedy: Canonical coins', 'coin', 'Do the greedy and optimal coin counts agree?', ('Run greedy','Run optimal','Counterexample')),
    Lesson('Greedy: Earliest start trap', 'activity', 'Can one early long meeting block three shorter ones?', ('Run start','Run finish','Try duration trap')),
    Lesson('Greedy: Shortest meeting trap', 'activity', 'Can a short middle meeting block two compatible ones?', ('Run duration','Run finish','Try start trap')),
    Lesson('Greedy: Fractional vs 0/1', 'bag', 'Why does a ratio order work only when items are divisible?', ('Run ratios','Run optimal','Open DP table')),
    Lesson('Bits: Logic gates', 'bit_logic', 'Which truth-table row explains each output bit?', ('Run AND','Run XOR','Run NOT')),
    Lesson('Bits: Shift and sign', 'bit_shift', 'Why do arithmetic and logical right shifts differ?', ('Logical right','Arithmetic right','Shift left')),
    Lesson("Bits: Two's complement", 'bit_negate', 'Why does complement plus one negate a W-bit word?', ('Negate x','Try zero','Minimum value')),
    Lesson('Bits: Clear and count', 'bit_clear', 'Why does x - 1 flip the lowest 1 and trailing zeros?', ('Clear once','Count all ones','Try zero')),
    Lesson('Bits: Isolate lowest one', 'bit_isolate', 'Why does x AND -x leave only the lowest set bit?', ('Isolate x','Try zero','Try odd x')),
    Lesson('Bits: Power of two', 'bit_power', 'Why is the nonzero guard essential for this test?', ('Test x','Try zero','Try power')),
    Lesson('Bits: XOR singleton', 'bit_unique', 'How do paired words cancel in the XOR accumulator?', ('Find singleton','Reorder words','Change example')),
    Lesson('Bits: Subsets and knapsack', 'bit_subset', 'How does each mask encode one 0/1 item choice?', ('List subsets','Use bag input','Open knapsack DP')),
]

def path_input(index=0):
    if index == 1:
        return Grid(weights={(x,y):5 for x in range(6,10) for y in range(4,7)})
    if index == 2:
        return Grid(24,14,(1,7),(22,7))
    if index == 3:
        return Grid(weights={(7,5):5})
    # A deep northern detour competes with the direct eastward path.
    return Grid(walls={(x,3) for x in range(3,13)})
