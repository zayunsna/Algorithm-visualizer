"""Repeatable headless captures, measured frame work and lesson playback time."""
import os
os.environ['SDL_VIDEODRIVER']='dummy'
os.environ['SDL_AUDIODRIVER']='dummy'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT']='1'
import json
import statistics
import sys
import time
import subprocess
import hashlib
import struct
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pygame
from algoviz.app import App
from algoviz.capture import save_png
from algoviz.pathfinding import Grid

OUT=Path('docs/screenshots')
OUT.mkdir(parents=True,exist_ok=True)
app=App()

def capture(name):
    assert not app.help or name in ('22-dfs-help','36-bits-help'), 'Help must not obscure lesson captures'
    if name!='45-tooltip': app.pointer=(0,0)
    app.draw(); save_png(app.screen,OUT/(name+'.png'))

def step(index,finish=True):
    app.draw()
    event=pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=app.buttons['step'+str(index)].center)
    pygame.event.post(event)
    for event in pygame.event.get(): app.handle(event)
    if finish:
        for _ in range(1000):
            app.tick(.1)
            if not app.playing: break
        assert not app.playing

report={'environment':{'python':sys.version.split()[0],'pygame':pygame.version.ver,'SDL':pygame.get_sdl_version(),
                       'driver':pygame.display.get_driver(),'size':[1280,720]},'path':{}}
app.load(0,initial=True); capture('01-first-screen')
for lesson,algorithms,name in [(0,['BFS'],'02-bfs'),(0,['BFS','DFS'],'03-dfs'),(1,['BFS'],'04-bfs-swamp'),
                              (1,['BFS','Dijkstra'],'05-dijkstra'),(2,['Dijkstra','A*'],'06-astar'),(3,['A*','A* (h×3)'],'07-astar-overestimate')]:
    app.load(lesson)
    for algorithm in algorithms: app.activate('algo'+algorithm); app.activate('end')
    capture(name)
    state=app.timeline.state
    report['path'][name]={k:state[k] for k in ('cost','length','expanded','max_frontier','relaxations')}
report['path_maps']={}
for index in range(4):
    app.load(index)
    for algorithm in ('BFS','DFS','Dijkstra','A*','A* (h×3)'):
        app.activate('algo'+algorithm); app.activate('end')
    report['path_maps'][app.lesson.title]={'size':[app.grid.width,app.grid.height],
        'walls':sorted(app.grid.walls),'swamps':sorted(app.grid.weights),
        'columns':['cost','edges','expanded'],'results':app.results}
for lesson,name in [(4,'08-fibonacci'),(5,'09-lcs-trace'),(6,'10-knapsack-trace'),
                    (7,'11-coin-failure'),(9,'12-activity-start'),(10,'13-activity-duration'),(11,'14-bag-comparison')]:
    app.load(lesson); app.timeline.finish(); capture(name)
app.handle(pygame.event.Event(pygame.VIDEORESIZE,w=1366,h=768,size=(1366,768)))
app.load(7); app.timeline.finish(); capture('15-size-1366x768')
app.handle(pygame.event.Event(pygame.VIDEORESIZE,w=1280,h=720,size=(1280,720)))
app.activate('field:coins'); app.edit_text='0, 3, 4'; app.commit_field(); capture('16-input-error')
app.load(4); step(2); capture('17-fibonacci-n8')
app.load(0); app.dropdown=True; app.menu_group='Greedy'; capture('18-dropdown')
app.load(5)
for _ in range(12): app.timeline.forward()
capture('19-dp-dependencies')
app.load(2); app.algorithm='A*'; app.prepare()
for _ in range(40): app.timeline.forward()
capture('20-priority-frontier')
app.load(7)
while not (app.timeline.state.get('current')==6 and app.timeline.state.get('best_coin')==3): app.timeline.forward()
capture('21-coin-dependencies')
app.load(0); app.help=True; capture('22-dfs-help')
report['bits']={}
for index in range(12,20):
    app.load(index); app.timeline.finish()
    name=f'{23+index-12:02d}-bits-{app.lesson.module[4:]}'
    capture(name)
    report['bits'][name]={key:app.timeline.state.get(key) for key in ('width','result','iterations','is_power','best','subsets')}
app.load(15); app.timeline.forward(); capture('31-bits-borrow')
app.load(14); step(2); capture('32-bits-sign-minimum')
app.load(13); app.bit_width=16; app.bit_a=-8; app.bit_signed=True; app.bit_shift_op='ARITHMETIC'; app.prepare(); app.timeline.finish(); capture('33-bits-shift-16')
app.load(17); step(1); capture('34-bits-zero-guard')
app.load(19); app.dropdown=True; app.menu_group='Bits'; app.menu_scroll=2; capture('35-bits-group-menu')
app.load(13); app.help=True; capture('36-bits-help')
app.handle(pygame.event.Event(pygame.VIDEORESIZE,w=1366,h=768,size=(1366,768)))
app.load(12); app.bit_width=16; app.prepare(); app.timeline.finish(); capture('37-bits-1366')
app.handle(pygame.event.Event(pygame.VIDEORESIZE,w=1280,h=720,size=(1280,720)))
# Additional usability captures include each changed map and maximum input sizes.
for index,algorithms,name in [(0,['BFS','DFS'],'38-map-depth'),(1,['BFS','Dijkstra'],'39-map-swamp'),
                              (2,['Dijkstra','A*'],'40-map-guided'),(3,['A*','A* (h×3)'],'41-map-trap')]:
    app.load(index)
    for algorithm in algorithms: app.activate('algo'+algorithm); app.activate('end')
    capture(name)
app.load(5); app.a='ABCDEFGHIJKL'; app.b='LKJIHGFEDCBA'; app.prepare(); app.timeline.finish(); capture('42-lcs-maximum')
app.load(7); app.amount=150; app.prepare()
while not (app.timeline.state.get('phase')=='optimal' and app.timeline.state.get('current')==150): app.timeline.forward()
capture('43-coin-150')
app.load(0); app.activate('about'); capture('44-about')
app.load(5); app.draw(); app.pointer=app.buttons['step0'].center; capture('45-tooltip')
app.pointer=(0,0); app.activate('speed:fast'); capture('46-speed-presets')
app.load(6); app.items=[(i+1,10) for i in range(8)]; app.capacity=25; app.prepare(); app.timeline.finish(); capture('47-knapsack-maximum')
app.load(13); app.bit_a=-8; app.bit_signed=True; app.bit_shift_op='ARITHMETIC'; app.prepare(); app.timeline.finish(); capture('48-shift-signed')
app.handle(pygame.event.Event(pygame.VIDEORESIZE,w=1366,h=768,size=(1366,768)))
app.load(5); app.a='ABCDEFGHIJKL'; app.b='LKJIHGFEDCBA'; app.prepare(); app.timeline.finish(); capture('49-lcs-1366')
app.load(7); app.amount=150; app.prepare(); app.timeline.finish(); capture('50-coin-1366')
app.handle(pygame.event.Event(pygame.VIDEORESIZE,w=1280,h=720,size=(1280,720)))
# Animation timing is simulated event pacing, not measured human comprehension.
report['lesson_stage_timing']=[]
for lesson_index in range(20):
    app.load(lesson_index,reset=True)
    actions=['algoBFS','algoDFS'] if lesson_index==0 else ['algoBFS'] if lesson_index<4 else ['step0','step1','step2']
    for action in actions:
        app.activate(action); elapsed=0; start_cursor=app.timeline.cursor
        while app.playing:
            app.tick(1/60); elapsed+=1/60
            assert elapsed<600,'A lesson stage failed to terminate'
        report['lesson_stage_timing'].append({'lesson':lesson_index,'action':action,'seconds':round(elapsed,2),
            'events':app.timeline.cursor-start_cursor,'speed':app.speed})
report['first_lesson_animation_seconds']=round(sum(row['seconds'] for row in report['lesson_stage_timing'] if row['lesson']==0),2)
app.load(0); end_start=time.perf_counter()
for algorithm in ('BFS','DFS'): app.activate('algo'+algorithm); app.activate('end'); app.draw()
report['first_lesson_end_work_seconds']=round(time.perf_counter()-end_start,4)
report['usability']={'tests_total':unittest.defaultTestLoader.discover('tests').countTestCases(),'maximum_lcs_chars':12,'maximum_items':8,'display_capacity_limit':25,'maximum_coin_amount':150,
    'table_scrolling':False,'path_numbered_steps':False,'about_modal':True,
    'step_review':'Use bag input repeats the default input if no custom bag is shared; Reorder words intentionally preserves the singleton result.',
    'human_desktop_test':False}
# Measure tick + complete draw + dummy display flip, with the large search in progress.
app.load(0); app.grid=Grid(80,60,(0,30),(79,30)); app.algorithm='Dijkstra'; app.prepare()
for _ in range(2800): app.timeline.forward()
app.speed=240; app.playing=True; times=[]
for _ in range(300):
    start=time.perf_counter(); app.tick(1/60); app.draw(); times.append((time.perf_counter()-start)*1000)
report['frame_work_80x60']={'frames':len(times),'events_per_second':app.speed,'events_at_end':app.timeline.cursor,
                          'expanded_at_end':app.timeline.state['expanded'],
                          'mean_ms':round(statistics.mean(times),3),'p95_ms':round(sorted(times)[int(.95*len(times))-1],3),
                          'max_ms':round(max(times),3),'driver':'dummy','includes':'tick + draw + display.flip; excludes sleep'}
pygame.quit()
after=json.loads(subprocess.check_output([sys.executable,'tools/benchmark_end.py'],text=True))
Path('docs/end-after.json').write_text(json.dumps(after,indent=2)+'\n')
report['end_80x60']={'before':json.loads(Path('docs/end-before.json').read_text()),
                    'initial_after':json.loads(Path('docs/end-after-initial.json').read_text()),'after':after}
report['installation']={'clean_pygame_verified':False,'attempted_python':'3.12.13','reason':'PyPI DNS connection unavailable',
                        'used_for_ui':'Python 3.14.2 with locally patched pygame 2.6.1'}
Path('docs/verification.json').write_text(json.dumps(report,indent=2)+'\n')
manifest=[]
for path in sorted(OUT.glob('*.png')):
    data=path.read_bytes()
    manifest.append({'file':str(path),'size':list(struct.unpack('!II',data[16:24])), 'sha256':hashlib.sha256(data).hexdigest()})
Path('docs/capture-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(report,indent=2))
