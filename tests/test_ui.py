"""Inject actual SDL/Pygame events; no claim of a human desktop test."""
import os
os.environ['SDL_VIDEODRIVER']='dummy'
os.environ['SDL_AUDIODRIVER']='dummy'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT']='1'
import ast
import unittest
from copy import deepcopy
from pathlib import Path
import pygame
from algoviz.app import App
from algoviz.engine import Timeline
from algoviz.lessons import LESSONS
from algoviz.pathfinding import Grid,search
from algoviz.dp import fibonacci,lcs,knapsack
from algoviz.greedy import coins_compare,activity_compare,bag_compare


class UITests(unittest.TestCase):
    def setUp(self):
        self.app=App(); pygame.event.clear(); self.app.draw()
    def tearDown(self): pygame.quit()
    def send(self,event):
        pygame.event.post(event)
        for e in pygame.event.get(): self.app.handle(e)
        self.app.draw()
    def click(self,key):
        self.app.draw()
        self.send(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=self.app.buttons[key].center))
        self.send(pygame.event.Event(pygame.MOUSEBUTTONUP,button=1,pos=self.app.buttons.get(key,pygame.Rect(0,0,1,1)).center))
    def key(self,key,unicode=''):
        self.send(pygame.event.Event(pygame.KEYDOWN,key=key,unicode=unicode,mod=0))
    def finish_play(self):
        for _ in range(600):
            self.app.tick(.25)
            if not self.app.playing: break
        self.assertFalse(self.app.playing,'Playback did not reach its stage boundary')
    def field(self,name,raw,apply=False):
        self.click('field:'+name)
        for _ in range(len(self.app.edit_text)): self.key(pygame.K_BACKSPACE)
        for c in raw: self.key(ord(c),c)
        if apply: self.click('apply')
        else: self.key(pygame.K_RETURN,'\r')

    def test_every_lesson_and_step_at_both_sizes(self):
        for size in ((1280,720),(1366,768)):
            self.send(pygame.event.Event(pygame.VIDEORESIZE,w=size[0],h=size[1],size=size))
            for index,lesson in enumerate(LESSONS):
                self.app.load(index); self.app.draw()
                original=deepcopy(self.app.timeline.state)
                for step in range(len(lesson.steps)):
                    with self.subTest(size=size,lesson=lesson.title,step=step):
                        self.click('step'+str(step)); self.finish_play()
                        self.assertTrue(self.app.timeline.cursor>1 or lesson.steps[step]=='Add swamp')
                        self.app.draw()
                        for rect in self.app.buttons.values(): self.assertTrue(self.app.screen.get_rect().contains(rect))
                self.app.load(index); self.assertEqual(self.app.timeline.state,original)

    def test_dropdown_scroll_enter_tab_and_resized_clicks(self):
        self.click('lessons')
        self.click('group:Bits')
        self.send(pygame.event.Event(pygame.MOUSEWHEEL,x=0,y=-1))
        self.assertEqual(self.app.menu_scroll,1)
        self.click('group:Greedy')
        self.click('lesson11'); self.assertEqual(self.app.lesson_index,11)
        self.key(pygame.K_TAB); self.assertIn(self.app.focus,self.app.buttons)
        self.app.focus='help'; self.key(pygame.K_RETURN); self.assertTrue(self.app.help)
        self.key(pygame.K_ESCAPE); self.assertFalse(self.app.help)
        self.send(pygame.event.Event(pygame.VIDEORESIZE,w=1366,h=768,size=(1366,768)))
        self.click('reset'); self.assertEqual(self.app.screen.get_size(),(1366,768))
        self.click('next'); self.assertEqual(self.app.timeline.cursor,2)

    def test_dropdown_modal_gaps_and_keyboard(self):
        self.click('lessons'); self.key(pygame.K_TAB); self.assertEqual(self.app.focus,'group:Path')
        self.app.focus='lesson0'
        self.key(pygame.K_TAB); self.key(pygame.K_RETURN); self.assertEqual(self.app.lesson_index,1)
        self.click('lessons'); count=self.app.timeline.cursor
        self.send(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=(300,90)))
        self.assertEqual(self.app.timeline.cursor,count); self.assertFalse(self.app.playing)

    def test_stage_boundaries_and_path_counterexamples(self):
        self.app.load(1)
        self.click('algoBFS'); self.finish_play(); self.assertEqual(self.app.timeline.state['cost'],29)
        self.click('algoDijkstra'); self.finish_play(); self.assertEqual(self.app.timeline.state['cost'],17)
        self.app.load(3)
        self.click('algoA*'); self.finish_play()
        optimal=self.app.timeline.state['cost']; expanded=self.app.timeline.state['expanded']
        self.click('algoA* (h×3)'); self.finish_play()
        self.assertGreater(self.app.timeline.state['cost'],optimal); self.assertLess(self.app.timeline.state['expanded'],expanded)
        self.app.load(5); self.click('step0'); self.finish_play()
        self.assertTrue(self.app.timeline.state['table_ready']); self.assertFalse(self.app.timeline.state['done']); self.assertEqual(self.app.timeline.state['trace'],[])
        self.click('step1'); self.finish_play(); self.assertTrue(self.app.timeline.state['done']); self.assertTrue(self.app.timeline.state['trace'])
        self.app.load(7); self.click('step0'); self.finish_play()
        self.assertTrue(self.app.timeline.state['greedy_ready']); self.assertFalse(self.app.timeline.state['done'])
        self.click('step1'); self.finish_play(); self.assertTrue(self.app.timeline.state['failed'])

    def test_all_modules_backward_forward(self):
        sources=[search(Grid(),'BFS'),search(Grid(),'DFS'),search(Grid(),'Dijkstra'),search(Grid(),'A*',3),
                 fibonacci(6),lcs('ABAB','BABA'),knapsack([(2,12),(4,20),(6,24)],10),
                 coins_compare([1,3,4],6),activity_compare([(0,4),(4,8),(3,5)],'duration'),
                 bag_compare([(2,12),(4,20),(6,24)],10)]
        for source in sources:
            t=Timeline(source); snapshots=[{}]
            while t.forward(): snapshots.append(deepcopy(t.state))
            for snapshot in reversed(snapshots[:-1]): t.back(); self.assertEqual(t.state,snapshot)
            for snapshot in snapshots[1:]: t.forward(); self.assertEqual(t.state,snapshot)

    def test_ui_keys_preserve_history(self):
        self.click('algoBFS'); self.finish_play(); final=deepcopy(self.app.timeline.state)
        count=self.app.timeline.cursor
        self.key(pygame.K_LEFT); self.key(pygame.K_RIGHT); self.assertEqual(self.app.timeline.state,final)
        self.key(pygame.K_r); self.assertEqual(self.app.timeline.cursor,0)
        self.key(pygame.K_SPACE); self.finish_play(); self.assertEqual(self.app.timeline.state,final)
        self.assertEqual(self.app.timeline.cursor,count)
        self.key(pygame.K_SPACE); self.finish_play(); self.assertEqual(self.app.timeline.state,final)
        self.assertEqual(self.app.timeline.cursor,count)
        self.key(pygame.K_UP); self.assertEqual(self.app.speed,31)
        self.key(pygame.K_DOWN); self.assertEqual(self.app.speed,30)

    def test_input_edit_errors_and_apply_button(self):
        self.app.load(7); self.app.draw()
        before=deepcopy(self.app.timeline.state)
        self.field('coins','0,3,4'); self.assertTrue(self.app.error); self.assertEqual(self.app.coins,[1,3,4]); self.assertEqual(self.app.timeline.state,before)
        self.field('coins','1,2,7',apply=True); self.assertFalse(self.app.error); self.assertEqual(self.app.coins,[1,2,7])
        self.field('amount','11'); self.assertEqual(self.app.amount,11)
        self.app.timeline.finish(); self.assertEqual(sum(self.app.timeline.state['optimal']),11)
        self.app.load(4); self.app.draw(); self.field('n','9'); self.assertTrue(self.app.error); self.assertEqual(self.app.n,6)
        self.field('n','8'); self.app.timeline.finish(); self.assertEqual(self.app.timeline.state['naive_calls'],67)
        self.app.load(5); self.app.draw(); self.field('a','HELLO'); self.assertEqual(self.app.a,'HELLO')
        self.app.load(6); self.app.draw(); self.field('items','3:7, 4:9'); self.field('capacity','25'); self.assertEqual(self.app.items,[(3,7),(4,9)])
        self.assertNotIn('colsright',self.app.buttons)
        self.app.load(9); self.app.draw(); self.field('activities','0:2, 2:4'); self.assertEqual(self.app.activities,[(0,2),(2,4)])

    def test_grid_paint_drag_start_goal_maze_clear(self):
        ox,oy=self.app.grid_origin; cell=self.app.cell_size
        def point(x,y): return (int(ox+(x+.5)*cell),int(oy+(y+.5)*cell))
        self.send(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=point(3,3)))
        self.send(pygame.event.Event(pygame.MOUSEMOTION,pos=point(4,3),rel=(1,0),buttons=(1,0,0)))
        self.send(pygame.event.Event(pygame.MOUSEBUTTONUP,button=1,pos=point(4,3)))
        self.assertTrue({(3,3),(4,3)}<=self.app.grid.walls)
        self.click('toolSwamp'); self.send(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=point(3,3))); self.assertEqual(self.app.grid.weights[(3,3)],5)
        self.click('toolStart'); self.send(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=point(2,2))); self.assertEqual(self.app.grid.start,(2,2))
        self.click('toolGoal'); self.send(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=point(9,7))); self.assertEqual(self.app.grid.goal,(9,7))
        self.click('maze'); first=deepcopy(self.app.grid); self.click('maze'); self.assertEqual(self.app.grid,first)
        self.click('clear'); self.assertFalse(self.app.grid.walls); self.assertFalse(self.app.grid.weights)
        self.field('seed','97'); self.assertEqual(self.app.grid.seed,97)
        after=deepcopy(self.app.grid); self.click('maze'); self.assertEqual(self.app.grid,after)

    def test_panel_scroll_without_table_pan(self):
        self.app.timeline.finish(); self.app.draw()
        self.send(pygame.event.Event(pygame.MOUSEWHEEL,x=0,y=-3)); self.assertGreater(self.app.scroll,0)
        self.app.load(6); self.app.capacity=25; self.app.prepare(); self.app.draw()
        self.assertNotIn('colsleft',self.app.buttons)
        self.assertTrue(all(self.app.main.contains(r) for r in self.app.table_rects.values()))

    def test_hover_astar_values_and_no_path(self):
        self.click('algoA*'); self.app.timeline.finish(); self.app.draw()
        ox,oy=self.app.grid_origin; size=self.app.cell_size
        pos=(int(ox+2.5*size),int(oy+5.5*size))
        self.send(pygame.event.Event(pygame.MOUSEMOTION,pos=pos,rel=(0,0),buttons=(0,0,0)))
        self.assertEqual(self.app.hover,(2,5))
        self.assertTrue(any('g=1  h=12  f=13' in line for line in self.app.panel_lines()))
        self.app.grid.walls.add(self.app.grid.goal); self.app.prepare(); self.app.timeline.finish()
        self.assertTrue(self.app.timeline.state['done']); self.assertIsNone(self.app.timeline.state['cost'])
        self.assertIn('No path',self.app.timeline.message)

    def test_dp_greedy_share_custom_input(self):
        self.app.load(6); self.app.items=[(3,17),(5,20)]; self.app.capacity=8; self.app.prepare()
        self.click('step2'); self.assertEqual(self.app.lesson.module,'bag'); self.assertEqual(self.app.items,[(3,17),(5,20)])
        self.click('step2'); self.assertEqual(self.app.lesson.module,'knapsack'); self.assertEqual(self.app.capacity,8)

    def test_algorithm_modules_do_not_import_pygame(self):
        for name in ('pathfinding','dp','greedy','engine','bits'):
            tree=ast.parse(Path('algoviz',name+'.py').read_text())
            for node in ast.walk(tree):
                if isinstance(node,ast.Import): self.assertTrue(all(not n.name.startswith('pygame') for n in node.names))
                if isinstance(node,ast.ImportFrom): self.assertFalse((node.module or '').startswith('pygame'))

    def test_quit_and_minimum_window_size(self):
        self.send(pygame.event.Event(pygame.VIDEORESIZE,w=800,h=600,size=(800,600)))
        self.assertEqual(self.app.screen.get_size(),(1280,720))
        self.send(pygame.event.Event(pygame.QUIT)); self.assertFalse(self.app.running)

    def test_end_button_key_and_undo(self):
        for size in ((1280,720),(1366,768)):
            self.send(pygame.event.Event(pygame.VIDEORESIZE,w=size[0],h=size[1],size=size))
            self.app.load(0); self.click('end'); final=deepcopy(self.app.timeline.state)
            self.assertTrue(final['done']); self.assertEqual(final['cost'],13)
            self.click('back'); self.click('next'); self.assertEqual(self.app.timeline.state,final)
            self.click('home'); self.key(pygame.K_END); self.assertEqual(self.app.timeline.state,final)

    def test_module_legends_and_coin_dependencies(self):
        self.app.load(4); self.assertNotIn('Dependency',[k for k,c in self.app.legend_entries()])
        self.app.load(7); self.assertNotIn('Rejected',[k for k,c in self.app.legend_entries()])
        while not (self.app.timeline.state.get('current')==6 and self.app.timeline.state.get('best_coin')==3): self.app.timeline.forward()
        self.assertEqual(self.app.timeline.state['dependencies'],[2,3,5])
        self.assertEqual(self.app.timeline.state['dp'][6],self.app.timeline.state['dp'][3]+1)
        self.app.draw(); self.assertGreaterEqual(self.app.main.height,396)
