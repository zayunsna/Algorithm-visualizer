"""Fresh-process end-to-end elapsed time, tracemalloc peak and process RSS."""
import gc
import json
import resource
import sys
import time
import tracemalloc
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from algoviz.engine import Timeline
from algoviz.pathfinding import Grid, search

def measure(traced=False):
    gc.collect()
    if traced: tracemalloc.start()
    start=time.perf_counter()
    timeline=Timeline(search(Grid(80,60,(0,30),(79,30)),'Dijkstra'))
    state=timeline.finish()
    elapsed=time.perf_counter()-start
    peak=tracemalloc.get_traced_memory()[1] if traced else None
    if traced: tracemalloc.stop()
    assert state['cost']==79 and state['length']==79
    return {'elapsed_seconds':round(elapsed,4),'tracemalloc_peak_bytes':peak,
            'process_peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform=='darwin' else 1024),
            'events':timeline.cursor,'expanded':state['expanded'],'cost':state['cost']}

if __name__=='__main__':
    print(json.dumps({'python':sys.version.split()[0],'grid':[80,60],'start':[0,30],'goal':[79,30],
                      'algorithm':'Dijkstra','normal':measure(),'traced':measure(True),
                      'note':'RSS is process lifetime peak; tracemalloc includes retained history. Traced timing includes instrumentation overhead.'}))
