"""Short lesson explanations and action descriptions, separate from algorithms."""
ABOUT = {
'path': ('What it is: grid search with a frontier of candidate cells.', 'Key idea: BFS uses a queue; DFS explores depth with a stack.', 'Key idea: Dijkstra settles the least cost; A* adds a heuristic.', 'Watch for: compare cost, edges and expanded cells on this map.', 'Cost: BFS/DFS O(V+E); heap Dijkstra/safe A* O((V+E) log V).', 'Space: O(V+E) search state; recorded events use extra memory.'),
'fib': ('What it is: Fibonacci by recursion and memoization.', 'Key idea: cache each F(n) instead of solving it repeatedly.', 'Watch for: repeated yellow nodes versus teal cache hits.', 'Cost: naive O(phi^n) calls; memo O(n) calls and storage.', 'The tree is limited to n <= 8 to keep all calls visible.'),
'lcs': ('What it is: the longest subsequence shared by two strings.', 'Key idea: match -> diagonal + 1; otherwise max(up, left).', 'Watch for: blue dependencies and yellow traceback cells.', 'Cost: O(mn) time and O(mn) table space.', 'Ties move up; swapping strings can change the chosen sequence.'),
'knapsack': ('What it is: choose whole items within a weight capacity.', 'Key idea: take or skip, using only the previous item row.', 'Watch for: a yellow trace recovering the selected items.', 'Cost: O(nC) time and O(nC) table space.', 'C is integer capacity; ties skip the current item.'),
'coin': ('What it is: make an amount using the fewest coins.', 'Key idea: greedy takes the largest fitting coin; DP tries all.', 'Watch for: {1,3,4}, amount 6 needs 3 greedy coins but 2 optimal.', 'Cost: DP O(Nk) time, O(N) space for k coin denominations.', 'US coins {1,5,10,25} agree with optimal on tested amounts.'),
'activity': ('What it is: choose the largest compatible meeting set.', 'Key idea: earliest finish leaves the most time for later meetings.', 'Watch for: start/duration rules can block a better schedule.', 'Cost: finish-rule greedy O(n log n); reference checks 2^n sets.', 'Touching endpoints are compatible; ties use input order.'),
'bag': ('What it is: compare fractional and whole-item knapsack.', 'Key idea: value/weight greedy is optimal when fractions are allowed.', 'Watch for: the same ratio rule can fail for whole items.', 'Cost: ratio sort O(n log n); whole-item DP O(nC).', 'Open DP to inspect the same items and capacity.'),
'bit_logic': ('What it is: AND, OR, XOR and NOT operate on individual bits.', 'Key idea: every output bit follows the highlighted truth-table row.', 'Watch for: corresponding input bits and the current output cell.', 'Cost: the visualizer emits O(W) bit steps.', 'All words are masked to W bits; signed changes interpretation.'),
'bit_shift': ('What it is: move bits left or right inside a W-bit word.', 'Key idea: logical right fills zero; arithmetic right copies sign.', 'Watch for: discarded purple bits and newly filled blue bits.', 'Cost: O(s) visual steps for shift amount s.', 'Python negative >> is arithmetic; left overflow is masked away.'),
'bit_negate': ('What it is: two\'s-complement negation inside W bits.', 'Key idea: invert every bit, then add one with a ripple carry.', 'Watch for: the signed minimum negates to the same bit pattern.', 'Cost: O(W) visual bit steps; final carry is discarded.', 'Python integers are unbounded: ~x = -x-1 before masking.'),
'bit_clear': ('What it is: clear the lowest 1, or count all set bits.', 'Key idea: x-1 flips the lowest 1 and every trailing zero.', 'Watch for: AND removes exactly one 1 on every iteration.', 'Cost: Kernighan O(k) word operations for k ones.', 'The visualizer emits O(Wk) bit steps; zero has popcount 0.'),
'bit_isolate': ('What it is: isolate the lowest set bit with x AND -x.', 'Key idea: complement + 1 preserves only that shared lowest 1.', 'Watch for: all higher set bits disappear after AND.', 'Cost: O(1) fixed-word operations; O(W) visual bit steps.', 'Zero has no lowest set bit, so its result is zero.'),
'bit_power': ('What it is: test whether an unsigned word is a power of two.', 'Key idea: a nonzero power has exactly one set bit.', 'Watch for: x AND (x-1) is zero, but x=0 must be rejected.', 'Cost: O(1) fixed-word operations; O(W) visual bit steps.', 'The test applies to the masked unsigned value.'),
'bit_unique': ('What it is: find a singleton among duplicated words.', 'Key idea: a XOR a = 0 and a XOR 0 = a.', 'Watch for: reordering pairs changes the trace, not the answer.', 'Cost: O(n) word operations; O(nW) visual bit steps.', 'After masking, exactly one word occurs once; all others twice.'),
'bit_subset': ('What it is: enumerate subsets using a binary mask.', 'Key idea: bit k selects item k+1; every mask is one subset.', 'Watch for: selected items, capacity and best feasible value.', 'Cost: O(n * 2^n) here, with O(n) working selection space.', 'This is the same enumeration principle as a 0/1 bag reference.'),
}
PATH_NOTES = (
'Watch for: DFS first follows the northern detour; BFS takes 13 edges.',
'Watch for: crossing the swamp costs 29; a 17-cost detour wins.',
'Watch for: A* expands 22 cells; Dijkstra expands 267.',
'Watch for: h x 3 takes cost 17 instead of the optimal cost 15.',
)

def about_lines(lesson, index):
    lines=list(ABOUT[lesson.module])
    if lesson.module=='path': lines[3]=PATH_NOTES[index]
    elif lesson.module=='coin' and index==8: lines[2]='Watch for: amount 63 uses six coins in both methods.'
    elif lesson.module=='activity': lines[2]='Watch for: '+('shortest middle meeting blocks two others.' if index==10 else 'an early long meeting blocks three shorter ones.')
    return lines

TOOLTIPS = {
'Run naive':'Show every recursive call, including repeated subproblems.',
'Run memo':'Compare recursion with cached subproblem results.',
'Compare n=8':'Increase n to expose the growth in repeated calls.',
'Fill table':'Compute the cells and pause before traceback.',
'Trace back':'Continue the filled table to recover a solution.',
'Swap strings':'Swap the strings; compare dependencies and tie choices.',
'Compare greedy':'Open ratio greedy with the same items and capacity.',
'Run greedy':'Pause after largest-fitting coin choices.',
'Run optimal':'Continue with DP to compare minimum coin counts.',
'Canonical coins':'Use US coins and amount 63 to compare both methods.',
'Counterexample':'Use {1,3,4}, amount 6 to expose greedy failure.',
'Run start':'Prioritize earliest start; watch the long meeting block others.',
'Run finish':'Prioritize earliest finish to maximize compatible meetings.',
'Run duration':'Prioritize shortest duration; compare the optimal set.',
'Try duration trap':'Load the short-middle-meeting counterexample.',
'Try start trap':'Load the early-long-meeting counterexample.',
'Run ratios':'Show fractional and whole-item ratio choices before DP.',
'Open DP table':'Open the same bag input in the DP table.',
'Run AND':'Fill output bits where both input bits are one.',
'Run XOR':'Fill output bits where the two input bits differ.',
'Run NOT':'Invert every input bit within the selected width.',
'Logical right':'Shift right with zero fill; compare sign extension.',
'Arithmetic right':'Shift right by copying the sign bit.',
'Shift left':'Shift left and display discarded overflow bits.',
'Negate x':'Invert bits, then add one with carry.',
'Try zero':'Run the zero boundary case.',
'Minimum value':'Negate the signed minimum and observe wraparound.',
'Clear once':'Remove exactly one lowest set bit.',
'Count all ones':'Repeat clearing; count one iteration per original 1.',
'Isolate x':'Keep only the lowest set bit using x AND -x.',
'Try odd x':'Use an odd word, whose lowest set bit has value 1.',
'Test x':'Apply the nonzero guard and single-set-bit test.',
'Try power':'Use a word with exactly one set bit.',
'Find singleton':'Accumulate XOR; duplicated words cancel.',
'Reorder words':'Reverse the input; verify the same final singleton.',
'Change example':'Use a different singleton and duplicated pairs.',
'List subsets':'Visit all masks and compare feasible bag values.',
'Use bag input':'Reload the most recently shared bag input.',
'Open knapsack DP':'Solve the same subset input with the DP table.',
}

ABOUT_LABELS = ('What it is', 'Key idea', 'Watch for', 'Cost', 'Space')


def about_rows(lines):
    """Split 'Label: text' lines into (label, text); repeated labels are shown once."""
    rows, previous = [], None
    for line in lines:
        label, sep, text = line.partition(': ')
        if not sep or label not in ABOUT_LABELS:
            label, text = 'Note', line
        rows.append(('' if label == previous else label, text[:1].upper() + text[1:]))
        previous = label
    return rows


# "?" help: titled sections of (key, description) rows, laid out in two columns.
PLAYBACK = ('Playback', (
    ('Space', 'Play or pause'),
    ('Right / Left', 'One event forward / undo one event'),
    ('End', 'Finish all events; Back still works'),
    ('R', 'Rewind to the first recorded event'),
    ('Up / Down', 'Change playback speed'),
))

PATH_HELP = (
    ('Editing', (
        ('Algorithm', 'BFS, DFS, Dijkstra, A* or A* (h×3)'),
        ('Tools', 'Wall, Swamp, Erase, Start, Goal; then paint'),
        ('New input', 'Starts a new history; Reset restores the map'),
    )),
    ('Search rules', (
        ('Neighbors', 'Up > Right > Down > Left'),
        ('Stop', 'BFS/DFS on goal discovery; Dijkstra/A* on pop'),
        ('DFS', 'Marks cells on push, so its order can differ from recursive DFS'),
    )),
    ('Colors', (
        ('Blue', 'Frontier'),
        ('Teal', 'Settled'),
        ('Yellow', 'Final path'),
        ('Right panel', 'Scroll to see the full data structure'),
    )),
    PLAYBACK,
)

STEP_HELP = (
    ('Lessons', (
        ('1  2  3', 'Run the stages of the lesson in order'),
        ('i', 'Background and key idea of this lesson'),
        ('Hover', 'A step button shows what it does'),
        ('New input', 'Starts a new history; Reset restores the lesson'),
    )),
    ('Reading the view', (
        ('Legend', 'Colors are listed under the main view'),
        ('Right panel', 'Scroll to see the full data'),
    )),
    PLAYBACK,
)

BITS_HELP = (
    ('Width and view', (
        ('W', '4, 8 or 16 bits; each cell shows a bit and 2^k'),
        ('Mask', 'Inputs and results use & ((1 << W) - 1)'),
        ('Signed', "Top bit is read as a two's complement sign"),
    )),
    ('Python vs W bits', (
        ('~5', 'Python gives -6: integers have no fixed width'),
        ('x >> k', 'Python shifts negative numbers arithmetically'),
        ('Logical >>', 'Shifts the masked unsigned word, filling 0'),
        ('Arithmetic >>', 'Copies the sign bit into new positions'),
        ('<<', 'Bits pushed past W are discarded'),
    )),
    ('Lesson notes', (
        ('Negate', 'The signed minimum wraps to itself'),
        ('Power of 2', 'Tests the unsigned word; zero is excluded'),
        ('XOR', 'After masking: pairs plus exactly one singleton'),
        ('Subsets', 'Bit k selects item k+1'),
    )),
    PLAYBACK,
)


def help_sections(module):
    if module == 'path':
        return PATH_HELP
    return BITS_HELP if module.startswith('bit_') else STEP_HELP
