# Screen review

Review from the 2026-10-14 usability update. All **50 PNGs were generated with the SDL dummy
video/audio drivers and opened one by one**. This is not a record of a person using a real desktop
window. Every image was regenerated with the current UI.
Captures are 1280×720 except 15/37/49/50, which are 1366×768. Fonts stay at 19 px (regular) and
16 px (small).

> Update 2026-10-14: the current PNGs were regenerated with the default **arcade theme**. Button and
> panel positions and sizes are the same as in classic; only colors and decorations differ. After the
> arcade regeneration, captures 01 and 44 were opened and checked; the content review in the table
> below was done on the classic captures. The `classic` theme (`--theme classic`) is pixel-identical
> to the screens before themes were added (60 captures compared).

Path lessons use the algorithm row with fixed maps and a comparison table instead of numbered buttons.
DP and coin tables fit the panel automatically; there are no horizontal pan buttons or wheel-pan code.
Current cells, dependency cells and traceback cells stay on screen. Long data listings on the right
scroll on purpose. The tooltip is a callout that covers part of the Observe line while hovering and
disappears when the pointer moves. About, the shared help and the dropdown cover the background by
design (modal behavior). Clicking outside About or help only closes it and is not passed to the
controls behind it.

| Capture | What was checked |
|---|---|
| [01-first-screen.png](screenshots/01-first-screen.png) | Fixed map with long text tucked away; algorithm row, About and playback controls directly reachable |
| [02-bfs.png](screenshots/02-bfs.png) | BFS cost 13 / edges 13 / expanded 102; stops after discovering the goal |
| [03-dfs.png](screenshots/03-dfs.png) | DFS cost 25 / edges 25 / expanded 25; BFS comparison values and the remaining stack |
| [04-bfs-swamp.png](screenshots/04-bfs-swamp.png) | BFS crosses the swamp block: cost 29 / edges 13; cost labels and path |
| [05-dijkstra.png](screenshots/05-dijkstra.png) | Dijkstra detours around the swamp: cost 17 / edges 17 / expanded 150; BFS comparison table |
| [06-astar.png](screenshots/06-astar.png) | Open map cost 21; expanded Dijkstra 267 vs A* 22 |
| [07-astar-overestimate.png](screenshots/07-astar-overestimate.png) | Regular A* cost 15 vs h×3 cost 17; h×3 expands 14 cells |
| [08-fibonacci.png](screenshots/08-fibonacci.png) | n=6 call tree: 25 vs memoized 11 calls, result 8, repeat/cache colors |
| [09-lcs-trace.png](screenshots/09-lcs-trace.png) | LCS table with 42 cells, length 4 "BCBA", traceback; no column-pan buttons |
| [10-knapsack-trace.png](screenshots/10-knapsack-trace.png) | Knapsack table: value 44, items 2 and 3 selected, traceback |
| [11-coin-failure.png](screenshots/11-coin-failure.png) | Coins: greedy 3 vs optimal 2; `amount: fewest coins` cells and chosen coins on the right |
| [12-activity-start.png](screenshots/12-activity-start.png) | Earliest start 1 vs optimal 3; take/reject reasons and optimal underline |
| [13-activity-duration.png](screenshots/13-activity-duration.png) | Shortest duration 1 vs optimal 2; middle-interval counterexample |
| [14-bag-comparison.png](screenshots/14-bag-comparison.png) | Same items: fractional 48 / greedy 32 / DP 44 |
| [15-size-1366x768.png](screenshots/15-size-1366x768.png) | 1366×768 coin comparison with the same fonts and playback controls |
| [16-input-error.png](screenshots/16-input-error.png) | Invalid coin 0 rejected; previous valid input kept, error in the bottom bar |
| [17-fibonacci-n8.png](screenshots/17-fibonacci-n8.png) | n=8: 67 vs memoized 15 calls, result 21, tree and playback controls |
| [18-dropdown.png](screenshots/18-dropdown.png) | Grouped dropdown items covering the background; event tests confirm the background is blocked |
| [19-dp-dependencies.png](screenshots/19-dp-dependencies.png) | LCS current cell and diagonal dependency colors, with every table cell visible |
| [20-priority-frontier.png](screenshots/20-priority-frontier.png) | A* in progress on the open map: priority-queue key / g / order and the current cell |
| [21-coin-dependencies.png](screenshots/21-coin-dependencies.png) | dp[6] = dp[3] + 1 with dependencies 2, 3, 5 highlighted; current cell 6 in the amount table |
| [22-dfs-help.png](screenshots/22-dfs-help.png) | Help explaining BFS/DFS stop-on-discovery vs weighted stop-on-pop, and the DFS order caveat |
| [23-bits-logic.png](screenshots/23-bits-logic.png) | Logic AND 24, truth table, bit place values, Result split into decimal/hex |
| [24-bits-shift.png](screenshots/24-bits-shift.png) | Logical 38 / arithmetic 230; discarded bits and newly filled bits |
| [25-bits-negate.png](screenshots/25-bits-negate.png) | Negating 5 gives −5 (word 251), carry, and the raw Python result |
| [26-bits-clear.png](screenshots/26-bits-clear.png) | 152 cleared in 3 iterations (popcount), remainder 0, iteration count |
| [27-bits-isolate.png](screenshots/27-bits-isolate.png) | 152 AND −152 gives 8; the lowest set bit isolated |
| [28-bits-power.png](screenshots/28-bits-power.png) | Default 12 is not a power of two; distinct from Try power (16) |
| [29-bits-unique.png](screenshots/29-bits-unique.png) | XOR singleton 7, 5 words processed, current word and accumulated bits |
| [30-bits-subset.png](screenshots/30-bits-subset.png) | 8 subsets, mask 7, over-capacity case and best value 44 |
| [31-bits-borrow.png](screenshots/31-bits-borrow.png) | 152 → 151 flips the low 4 bits; the step before AND |
| [32-bits-sign-minimum.png](screenshots/32-bits-sign-minimum.png) | Negating the signed minimum −128 gives −128; raw Python gives 128 |
| [33-bits-shift-16.png](screenshots/33-bits-shift-16.png) | 16-bit signed shift panel: logical 16382 / arithmetic −2; Result not truncated |
| [34-bits-zero-guard.png](screenshots/34-bits-zero-guard.png) | x = 0 is not a power of two thanks to the nonzero guard |
| [35-bits-group-menu.png](screenshots/35-bits-group-menu.png) | Last lesson reachable after scrolling the Bits group |
| [36-bits-help.png](screenshots/36-bits-help.png) | Help on W-bit masking vs unbounded Python integers and negative `>>` |
| [37-bits-1366.png](screenshots/37-bits-1366.png) | 1366×768 16-bit AND 24, place values, truth table, Result |
| [38-map-depth.png](screenshots/38-map-depth.png) | New depth map with BFS/DFS cost, edges and expanded compared |
| [39-map-swamp.png](screenshots/39-map-swamp.png) | New swamp-block map: BFS 29 vs Dijkstra 17 |
| [40-map-guided.png](screenshots/40-map-guided.png) | Open 24×14 map: expanded Dijkstra 267 vs A* 22 |
| [41-map-trap.png](screenshots/41-map-trap.png) | Heuristic counterexample: regular cost 15 vs h×3 cost 17 |
| [42-lcs-maximum.png](screenshots/42-lcs-maximum.png) | 1280×720 maximum 12×12-character LCS: 13 rows, 13 columns and traceback inside the main panel |
| [43-coin-150.png](screenshots/43-coin-150.png) | 1280×720 amount 150: 151 cells, 10 per row, current 150 and dependencies 146/147/149 visible |
| [44-about.png](screenshots/44-about.png) | About with 6 rows (What it is / Key idea / Watch for / Cost / Space) and the close hint |
| [45-tooltip.png](screenshots/45-tooltip.png) | One-line Fill table tooltip; covers part of Observe while hovering, by design |
| [46-speed-presets.png](screenshots/46-speed-presets.png) | Slow / Normal / Fast, fine-tuning, Fast selected at 24 ev/s, playback buttons reachable |
| [47-knapsack-maximum.png](screenshots/47-knapsack-maximum.png) | 8 items, capacity 25: 9 rows × 26 columns, value 60, items 1..6 selected, no overlap with the footer |
| [48-shift-signed.png](screenshots/48-shift-signed.png) | 8-bit signed shift: logical 62 / arithmetic −2; Result decimal −2 / hex FE |
| [49-lcs-1366.png](screenshots/49-lcs-1366.png) | 1366×768 maximum LCS: 13 rows, 13 columns and traceback inside |
| [50-coin-1366.png](screenshots/50-coin-1366.png) | 1366×768 amount 150: whole table, optimal 38, greedy 39, playback controls |

## Tests and measurements

At the time of this review, **52 tests passed**: [verify run log](usability-verify-output.txt),
[unit test log](test-results.txt). The suite now has **55 tests**; the three added later cover the
redesigned help/About popups and the theme switch, and all pass under both themes.
The pure algorithm tests also ran on a separate Python 3.12.13: **23 passed** ([log](python312-algorithm-tests.txt)).
After the canonical-coins About text was made specific to the lesson's observed values (63 → 6 coins),
the About and tooltip regressions were rerun for 20 lessons at both resolutions and passed ([log](about-final-test.txt)).

The headless start/quit smoke test and `verify.sh` were run with real injected Pygame events: click,
drag, key, wheel, Tab/Enter, resize and QUIT. Covered: the 5 algorithm buttons in the 4 path lessons,
the 48 numbered buttons in the other 16 lessons, and bit widths 4/8/16.
The tests include the existing comparison with Bellman-Ford on 400 random grids, DFS reachability,
edge cases and event undo/replay. The stop tests separate BFS/DFS finishing right after the goal relax
from weighted searches finishing after the goal is expanded.

The maximum inputs (LCS 12 characters, knapsack 8 items / capacity 25, coins 150) draw the table at
**every event** and check that every cell, current cell and dependency cell rectangle stays inside the
main panel at both resolutions. Long knapsack numbers widen the cells and row labels; inputs that do
not fit are rejected with an error. Capacity 30, 9 items, 13-character strings and amount 151 are
rejected in the UI while keeping the previous input. A regression shows a 10-digit knapsack value
without shrinking the font.

The numbers and algorithm properties in About were checked against the path references, the DP and
greedy exhaustive searches and the exhaustive bit tests. Complexities describe the algorithms without
recording or rendering. The complexity of safe A* is not a guarantee for the reopening h×3 search.
The Python integer explanations were checked against the official documentation linked in the README.

Step review: in Bits, Use bag input reuses the default input if no custom bag was shared.
Reorder words keeps the final answer on purpose to show that the accumulation order does not matter.
The duplicate where Test x and Try power both used 16 was fixed (defaults 12 and 16).
LCS Swap strings can keep the same optimal length; the step is there to compare table dimensions,
dependencies and traceback.

Auto-playing BFS and DFS on the first map takes **9.76 s** in total; with End, the automated input,
render and compute work takes **0.0151 s**. The earlier 44.33 s run used a different map, stop point
and button flow, so it is not a like-for-like speed comparison.
The default speeds and the measured time of each step are recorded in `lesson_stage_timing` in
[verification.json](verification.json). Most explanatory compute steps take about 5–15 s; DFS,
traceback, zero cases and greedy runs with few choices are shorter. Not every step is claimed to fall
in that range, and a person's clicking and reading time is not included.

300 frames during 80×60 Dijkstra: mean **9.163 ms**, p95 **9.578 ms**, max **10.117 ms**.
The latest 80×60 End compute is **0.0818 s** with 3,871 expanded cells and cost 79; the before/after
raw measurements are in verification.json. These values come from the latest `verify.sh` run and vary
slightly between runs. The frame measurement covers tick + draw + dummy display.flip and excludes
waiting; it does not guarantee real GPU, HiDPI or 60 fps over the whole search.
The capture manifest records the relative path, resolution and SHA-256 of all 50 files and is checked
against their contents.

## Not verified

- **A clean install of the official pygame wheel and a UI run on it have not been verified since PyPI
  was unreachable (DNS).** The UI tests, smoke test and verify ran only on Python 3.14.2 with a
  locally patched pygame 2.6.1.
- Keys, trackpad and HiDPI in a real macOS window, and other OS/Python combinations, were not checked.
- Whether a beginner blog reader can finish a lesson within three minutes without instructions still
  needs testing with real users.

The earlier 30- and 44-test logs and the first End before/after numbers are historical records.
The reference for current features, screens and expected values is this document, the README,
verification.json and capture-manifest.json.
