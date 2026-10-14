"""Grid search. Cost is paid on entry; the start cell costs zero."""
import heapq
import random
from collections import deque
from dataclasses import dataclass, field
from .engine import Event, event, DELETE


def frontier_view(state):
    """Materialize pop order only when requested by a renderer or inspector."""
    records = state.get('frontier', {}).values()
    algorithm = state.get('algorithm', 'BFS')
    weighted = algorithm in ('Dijkstra', 'A*')
    ordered = sorted(records, key=(lambda e:(e[1],e[2])) if weighted else
                     (lambda e:-e[2]) if algorithm == 'DFS' else (lambda e:e[2]))
    return [(p,k,serial if weighted else i,g,
             weighted and (state.get('dist',{}).get(p)!=g or state.get('settled',{}).get(p,False)))
            for i,(p,k,serial,g) in enumerate(ordered)]


@dataclass
class Grid:
    width: int = 16
    height: int = 10
    start: tuple = (1, 5)
    goal: tuple = (14, 5)
    walls: set = field(default_factory=set)
    weights: dict = field(default_factory=dict)
    seed: int = 42

    def contains(self, p):
        return 0 <= p[0] < self.width and 0 <= p[1] < self.height

    def neighbors(self, p):
        x, y = p
        for q in ((x, y-1), (x+1, y), (x, y+1), (x-1, y)):
            if self.contains(q) and q not in self.walls:
                yield q

    def cost(self, p):
        return self.weights.get(p, 1)

    def validate(self):
        if self.width < 1 or self.height < 1:
            raise ValueError("Grid dimensions must be positive")
        if not self.contains(self.start) or not self.contains(self.goal):
            raise ValueError("Start and goal must be inside the grid")
        if any(not self.contains(p) or c < 1 or not isinstance(c, int) for p, c in self.weights.items()):
            raise ValueError("Weights must be positive integers inside the grid")


def maze(width=16, height=10, seed=42):
    rng = random.Random(seed)
    grid = Grid(width, height, (0, 0), (width-1, height-1), seed=seed)
    grid.walls = {(x,y) for y in range(height) for x in range(width)
                  if rng.random() < .26 and (x,y) not in (grid.start, grid.goal)}
    return grid


def search(grid, algorithm="BFS", heuristic_weight=1):
    grid.validate()
    if algorithm not in ("BFS", "DFS", "Dijkstra", "A*"):
        raise ValueError("Unknown search algorithm")
    if heuristic_weight < 0:
        raise ValueError("Heuristic weight must be nonnegative")
    start, goal = grid.start, grid.goal
    weighted = algorithm in ("Dijkstra", "A*")
    def h(p):
        return abs(p[0]-goal[0]) + abs(p[1]-goal[1])
    def key(p, g):
        return g + (heuristic_weight*h(p) if algorithm == "A*" else 0)
    yield event("init", "Ready: choose the next frontier cell", kind="path", algorithm=algorithm,
                dist={}, visited={}, settled={}, frontier={}, current=None, path=[],
                expanded=0, max_frontier=0, relaxations=0, cost=None, length=None,
                done=False, heuristic_weight=heuristic_weight)
    if start in grid.walls or goal in grid.walls:
        yield event("done", "No path: start or goal is blocked", done=True)
        return
    dist, parent, settled = {start:0}, {}, set()
    def finish(p):
        path = [p]
        while path[-1] != start:
            path.append(parent[path[-1]])
        path.reverse()
        cost = sum(grid.cost(q) for q in path[1:])
        yield event("done", f"Path found: {len(path)-1} edges, cost {cost}",
                    path=path, cost=cost, length=len(path)-1, done=True)
    queue = deque([(start,0)])
    heap = [(key(start, 0), 0, start, 0)]
    serial, expanded, relaxations, peak = 1, 0, 0, 1
    yield Event("discover", "Enqueue start (entry cost 0)", {
        ("dist", start):0, ("frontier",0):(start,key(start,0),0,0), ("max_frontier",):1})
    while heap if weighted else queue:
        if weighted:
            _, entry_id, p, g = heapq.heappop(heap)
            if dist.get(p) != g or p in settled:
                yield Event("stale", "Discard stale priority-queue entry", {("frontier",entry_id):DELETE})
                continue
        else:
            p,entry_id = queue.popleft() if algorithm == "BFS" else queue.pop()
        settled.add(p)
        expanded += 1
        updates = {("current",):p, ("visited", p):True, ("expanded",):expanded,
                   ("frontier",entry_id):DELETE}
        if weighted:
            updates[("settled", p)] = True
        yield Event("expand", f"Expand {p}: g={dist[p]}" + (f", h={h(p)}, f={key(p,dist[p])}" if algorithm == "A*" else ""), updates)
        if p == goal:
            yield from finish(p)
            return
        neighbors = list(grid.neighbors(p))
        if algorithm == "DFS":
            neighbors.reverse()
        for q in neighbors:
            new = dist[p] + grid.cost(q)
            if (not weighted and q in dist) or (weighted and new >= dist.get(q, float("inf"))):
                continue
            dist[q], parent[q] = new, p
            relaxations += 1
            if weighted:
                settled.discard(q)
                heapq.heappush(heap, (key(q,new), serial, q, new))
            else:
                queue.append((q,serial))
            peak = max(peak, len(heap) if weighted else len(queue))
            yield Event("relax", f"Set g{q}={new} via {p}", {
                ("dist",q):new, ("frontier",serial):(q,key(q,new) if weighted else new,serial,new), ("relaxations",):relaxations,
                ("max_frontier",):peak, ("settled",q):False})
            serial += 1
            if not weighted and q == goal:
                yield from finish(q)
                return
    yield event("done", "No path: frontier is empty", done=True, current=None)
