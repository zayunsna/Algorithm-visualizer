import random
import unittest
from copy import deepcopy
from algoviz.engine import Timeline
from algoviz.pathfinding import Grid, search, maze
from algoviz.pathfinding import frontier_view
from pathlib import Path
from types import ModuleType


def reference(grid):
    # Independent Bellman-Ford: construct edges without using Grid.neighbors.
    if grid.start in grid.walls or grid.goal in grid.walls:
        return None
    cells = [(x,y) for y in range(grid.height) for x in range(grid.width) if (x,y) not in grid.walls]
    edges = [(a,b,grid.weights.get(b,1)) for a in cells for b in cells
             if abs(a[0]-b[0])+abs(a[1]-b[1]) == 1]
    d = {p:float("inf") for p in cells}
    d[grid.start] = 0
    for _ in range(len(cells)-1):
        changed = False
        for a,b,c in edges:
            if d[a]+c < d[b]:
                d[b] = d[a]+c
                changed = True
        if not changed:
            break
    return None if d[grid.goal] == float("inf") else d[grid.goal]


class PathTests(unittest.TestCase):
    def test_frontier_deltas_match_prechange_snapshots(self):
        baseline=ModuleType('algoviz._baseline')
        baseline.__package__='algoviz'
        exec(Path('tests/fixtures/pathfinding.py.txt').read_text(),baseline.__dict__)
        for algorithm in ('Dijkstra','A*'):
            grid=maze(8,6,19); grid.weights[(3,2)]=5
            original=Timeline(baseline.search(grid,algorithm))
            compact=Timeline(search(grid,algorithm))
            while original.forward():
                self.assertTrue(compact.forward())
                expected=deepcopy(original.state)
                actual=deepcopy(compact.state)
                actual['frontier']=frontier_view(actual)
                self.assertEqual(actual,expected)
            self.assertFalse(compact.forward())
            self.assertTrue(all(('frontier',) not in e.changes for e in compact.events[1:]))

    def test_400_random_grids(self):
        rng = random.Random(9031)
        for i in range(400):
            w,h = rng.randint(1,6), rng.randint(1,6)
            g = maze(w,h,i)
            for p in [(x,y) for y in range(h) for x in range(w)]:
                if rng.random() < .3:
                    g.weights[p] = rng.randint(1,8)
            expected = reference(g)
            for a in ("Dijkstra", "A*", "DFS"):
                result = Timeline(search(g,a)).finish()
                if a == "DFS":
                    self.assertEqual(result["cost"] is not None, expected is not None)
                else:
                    self.assertEqual(result["cost"], expected, (i,a))
                if result["path"]:
                    path = result["path"]
                    self.assertEqual((path[0],path[-1]),(g.start,g.goal))
                    self.assertTrue(all(b in list(g.neighbors(a)) for a,b in zip(path,path[1:])))
                    self.assertEqual(sum(g.cost(p) for p in path[1:]),result["cost"])
            g.weights.clear()
            self.assertEqual(Timeline(search(g,"BFS")).finish()["cost"], reference(g))

    def test_boundaries(self):
        cases = [Grid(1,1,(0,0),(0,0)), Grid(2,1,(0,0),(1,0),{(0,0)}),
                 Grid(2,1,(0,0),(1,0),{(1,0)}),Grid(3,1,(0,0),(2,0),{(1,0)}),
                 Grid(2,2,(1,1),(1,1))]
        for g in cases:
            for a in ("BFS","DFS","Dijkstra","A*"):
                self.assertEqual(Timeline(search(g,a)).finish()["cost"],reference(g))

    def test_reversible_and_deterministic(self):
        for a in ("BFS","DFS","Dijkstra","A*"):
            t = Timeline(search(maze(),a))
            snapshots = [{}]
            while t.forward():
                snapshots.append(deepcopy(t.state))
            for snapshot in reversed(snapshots[:-1]):
                t.back()
                self.assertEqual(t.state,snapshot)
            for snapshot in snapshots[1:]:
                t.forward()
                self.assertEqual(t.state,snapshot)
            other = Timeline(search(maze(),a))
            other.finish()
            self.assertEqual(t.events,other.events)

    def test_invalid(self):
        for g in (Grid(0,1), Grid(weights={(1,1):0})):
            with self.assertRaises(ValueError):
                list(search(g))
