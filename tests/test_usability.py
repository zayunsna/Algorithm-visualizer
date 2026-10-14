"""Usability regressions using real Pygame events and independent path references."""
import unittest
from copy import deepcopy
import pygame
from tests import test_ui as ui
from tests.test_path import reference
from algoviz.engine import Timeline
from algoviz.pathfinding import search, Grid
from algoviz.lessons import LESSONS, path_input
from algoviz.education import about_lines, TOOLTIPS
from algoviz.bits import clear_lowest

class SearchUsabilityTests(unittest.TestCase):
    def test_stop_on_discovery_and_not_priority_insertion(self):
        for algorithm in ('BFS','DFS'):
            timeline=Timeline(search(path_input(),algorithm)); timeline.finish()
            self.assertEqual(timeline.events[-2].action,'relax')
            self.assertIn(('dist',path_input().goal),timeline.events[-2].changes)
            self.assertEqual(timeline.events[-1].action,'done')
            self.assertNotIn(path_input().goal,timeline.state['visited'])
        dfs=Timeline(search(path_input(),'DFS')).finish()
        self.assertEqual((dfs['expanded'],dfs['length']),(25,25))
        for algorithm in ('Dijkstra','A*'):
            timeline=Timeline(search(path_input(3),algorithm)); timeline.finish()
            self.assertEqual(timeline.events[-2].action,'expand')
            self.assertEqual(timeline.state['current'],path_input(3).goal)
        for grid in (Grid(1,1,(0,0),(0,0)),Grid(2,1,(0,0),(1,0),{(1,0)})):
            for algorithm in ('BFS','DFS','Dijkstra','A*'):
                self.assertEqual(Timeline(search(grid,algorithm)).finish()['cost'],reference(grid))

    def test_fixed_maps_claims_and_repeatability(self):
        for index in range(4):
            self.assertEqual(path_input(index),path_input(index))
            grid=path_input(index)
            results={name:Timeline(search(grid,name)).finish() for name in ('BFS','DFS','Dijkstra','A*')}
            optimum=reference(grid)
            self.assertEqual(results['Dijkstra']['cost'],optimum)
            self.assertEqual(results['A*']['cost'],optimum)
            if index==0: self.assertGreater(results['DFS']['length'],results['BFS']['length'])
            if index==1:
                self.assertGreater(results['BFS']['cost'],results['Dijkstra']['cost'])
                self.assertLess(results['BFS']['length'],results['Dijkstra']['length'])
            if index==2: self.assertLess(results['A*']['expanded']*5,results['Dijkstra']['expanded'])
            if index==3: self.assertGreater(Timeline(search(grid,'A*',3)).finish()['cost'],optimum)

    def test_zero_popcount_recorded(self):
        self.assertEqual(Timeline(clear_lowest(0)).finish()['popcount'],0)

class UsabilityUITests(unittest.TestCase):
    setUp=ui.UITests.setUp; tearDown=ui.UITests.tearDown
    send=ui.UITests.send; click=ui.UITests.click; key=ui.UITests.key; field=ui.UITests.field

    def test_help_and_about_text_stays_inside_popup(self):
        for size in ((1280,720),(1366,768)):
            self.send(pygame.event.Event(pygame.VIDEORESIZE,w=size[0],h=size[1],size=size))
            for index in range(len(LESSONS)):
                self.app.load(index)
                for flag in ('help','about'):
                    setattr(self.app,flag,True); self.app.draw()
                    with self.subTest(size=size,lesson=index,popup=flag):
                        self.assertTrue(self.app.screen.get_rect().contains(self.app.modal_rect))
                        self.assertGreater(len(self.app.modal_text_rects),4)
                        for rect in self.app.modal_text_rects: self.assertTrue(self.app.modal_rect.contains(rect),rect)
                    setattr(self.app,flag,False)

    def test_theme_switch_and_unknown_theme(self):
        from algoviz import app as app_module, bits_view, theme
        try:
            app_module.use_theme('classic')
            self.assertEqual((app_module.BG,bits_view.BG,app_module.ARCADE),(theme.CLASSIC['BG'],)*2+(False,))
            self.app.draw()
            self.assertEqual(self.app.screen.get_at((5,5))[:3],theme.CLASSIC['BG'])
            with self.assertRaises(ValueError): app_module.use_theme('neon')
        finally:
            app_module.use_theme(None)

    def test_about_rows_split_labels(self):
        from algoviz.education import about_rows
        rows=about_rows(['What it is: a.','Key idea: b.','Key idea: c.','Free note.'])
        self.assertEqual(rows,[('What it is','A.'),('Key idea','B.'),('','C.'),('Note','Free note.')])

    def test_path_buttons_and_comparison_history(self):
        for index in range(4):
            self.app.load(index); self.app.draw()
            self.assertFalse(any(key.startswith('step') for key in self.app.buttons))
            for algorithm in ('BFS','DFS','Dijkstra','A*','A* (h×3)'):
                self.click('algo'+algorithm); self.click('end')
                self.assertIn(algorithm,self.app.results)
                final=deepcopy(self.app.timeline.state)
                self.click('back'); self.click('next'); self.assertEqual(self.app.timeline.state,final)
            self.assertEqual(len(self.app.results),5)
            self.assertTrue(any('cost / edges / exp' in line for line in self.app.panel_lines()))
            self.click('reset'); self.assertFalse(self.app.results)

    def test_maximum_tables_and_dependencies_inside_main(self):
        for size in ((1280,720),(1366,768)):
            self.send(pygame.event.Event(pygame.VIDEORESIZE,w=size[0],h=size[1],size=size))
            for lesson in (5,6,7):
                self.app.load(lesson)
                if lesson==5: self.app.a='ABCDEFGHIJKL'; self.app.b='LKJIHGFEDCBA'
                elif lesson==6: self.app.items=[(i+1,10) for i in range(8)]; self.app.capacity=25
                else: self.app.amount=150
                self.app.prepare()
                while self.app.timeline.forward():
                    self.app.draw()
                    rects=self.app.coin_rects if lesson==7 else self.app.table_rects
                    self.assertTrue(all(self.app.main.contains(r) for r in rects.values()))
                    state=self.app.timeline.state
                    for dep in state.get('dependencies',[]): self.assertIn(dep,rects)
                    current=state.get('current')
                    if current is not None: self.assertIn(current,rects)
                    self.assertTrue(all(r.height>=19 for r in rects.values()))
                self.assertFalse(any('cols' in key for key in self.app.buttons))
                self.assertFalse(hasattr(self.app,'col_offset'))
        self.app.load(5); self.app.draw(); self.field('a','A'*13)
        self.assertTrue(self.app.error); self.assertNotEqual(self.app.a,'A'*13)
        self.app.load(6); self.app.draw(); self.field('capacity','30')
        self.assertTrue(self.app.error); self.assertEqual(self.app.capacity,10)
        self.field('items',','.join('1:1' for _ in range(9))); self.assertTrue(self.app.error)
        self.field('capacity','2'); self.field('items','1:1234567890'); self.click('end')
        self.assertFalse(self.app.error); self.assertTrue(all(self.app.main.contains(r) for r in self.app.table_rects.values()))
        self.assertGreater(self.app.table_rects[(1,2)].width,self.app.small.size('1234567890')[0])
        self.app.load(7); self.app.draw(); self.field('amount','151'); self.assertTrue(self.app.error)

    def test_about_modal_all_lessons_and_tooltips(self):
        for size in ((1280,720),(1366,768)):
            self.send(pygame.event.Event(pygame.VIDEORESIZE,w=size[0],h=size[1],size=size))
            for index,lesson in enumerate(LESSONS):
                self.app.load(index); self.app.draw(); self.assertFalse(self.app.about)
                lines=about_lines(lesson,index); self.assertTrue(4<=len(lines)<=6)
                self.click('about'); self.assertTrue(self.app.about)
                self.assertTrue(self.app.screen.get_rect().contains(self.app.modal_rect))
                self.assertTrue(all(self.app.font.size(line)[0]<=self.app.modal_rect.width-44 for line in lines))
                count=self.app.timeline.cursor
                self.key(pygame.K_END); self.key(pygame.K_SPACE); self.key(pygame.K_RETURN)
                self.assertEqual(self.app.timeline.cursor,count); self.assertFalse(self.app.playing)
                self.send(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=self.app.modal_rect.center))
                self.assertTrue(self.app.about)
                self.click('next'); self.assertFalse(self.app.about); self.assertEqual(self.app.timeline.cursor,count)
                self.click('about'); self.key(pygame.K_ESCAPE); self.assertFalse(self.app.about); self.assertTrue(self.app.running)
                for step,label in enumerate(lesson.steps):
                    self.assertIn(label,TOOLTIPS)
                    self.send(pygame.event.Event(pygame.MOUSEMOTION,pos=self.app.buttons['step'+str(step)].center,rel=(0,0),buttons=(0,0,0)))
                    self.assertIsNotNone(self.app.tooltip_rect)
                    self.assertTrue(self.app.screen.get_rect().contains(self.app.tooltip_rect))

    def test_speed_presets_memory_reset_and_clamps(self):
        for i in range(len(LESSONS)):
            self.app.load(i); self.app.draw(); self.assertEqual(self.app.speed,LESSONS[i].default_speed)
            self.click('speed:slow'); self.assertEqual(self.app.speed,max(1,LESSONS[i].default_speed*.5))
            self.click('speed:fast'); self.assertEqual(self.app.speed,min(240,LESSONS[i].default_speed*2))
            self.click('speed:normal'); self.assertEqual(self.app.speed,LESSONS[i].default_speed)
            self.click('faster'); remembered=self.app.speed
            self.app.load((i+1)%len(LESSONS)); self.app.load(i); self.assertEqual(self.app.speed,remembered)
            self.click('reset'); self.assertEqual(self.app.speed,LESSONS[i].default_speed)
        for speed,key,expected in ((240,'faster',240),(1,'slower',1)):
            self.app.speed=speed; self.click(key); self.assertEqual(self.app.speed,expected)

    def test_shift_interpretations_and_untruncated_result(self):
        self.app.load(13); self.app.bit_a=-8; self.app.bit_width=16; self.app.bit_signed=True
        self.app.prepare(); self.click('end')
        lines=self.app.bits_panel_lines()
        self.assertIn('Logical: 16382',lines); self.assertIn('Arithmetic: -2',lines)
        self.assertIn('Result decimal: 16382',lines)
        self.assertTrue(all(self.app.small.size(line)[0]<=self.app.side.width-30 for line in lines))
        self.click('signed'); self.assertIn('Arithmetic: 65534',self.app.bits_panel_lines())
