"""Bit lessons through actual Pygame input events at both supported sizes."""
import unittest
from copy import deepcopy
import pygame
from tests import test_ui as ui
from algoviz import bits


class BitUITests(unittest.TestCase):
    setUp=ui.UITests.setUp
    tearDown=ui.UITests.tearDown
    send=ui.UITests.send
    click=ui.UITests.click
    key=ui.UITests.key
    field=ui.UITests.field
    finish_play=ui.UITests.finish_play

    def test_all_bit_steps_widths_and_sizes(self):
        for size in ((1280,720),(1366,768)):
            self.send(pygame.event.Event(pygame.VIDEORESIZE,w=size[0],h=size[1],size=size))
            for lesson in range(12,20):
                for width in (4,8,16):
                    self.app.load(lesson); self.app.draw(); self.click('width:'+str(width))
                    for step in range(3):
                        with self.subTest(size=size,lesson=lesson,width=width,step=step):
                            self.click('step'+str(step)); self.finish_play(); self.app.draw()
                            self.assertTrue(self.app.timeline.state.get('done'))
                            for rect in self.app.buttons.values(): self.assertTrue(self.app.screen.get_rect().contains(rect))
                            final=deepcopy(self.app.timeline.state)
                            self.key(pygame.K_LEFT); self.key(pygame.K_RIGHT); self.assertEqual(self.app.timeline.state,final)

    def test_signed_view_preserves_history_and_hex_inputs(self):
        self.app.load(12); self.app.draw()
        self.field('bit_a','0xAA'); self.field('bit_b','-5')
        self.click('bitop:OR'); self.click('end')
        self.assertEqual(self.app.timeline.state['result'],bits.logic_result(170,-5,8,'OR'))
        before=deepcopy(self.app.timeline.state); count=self.app.timeline.cursor
        self.click('signed'); self.assertEqual(self.app.timeline.state,before); self.assertEqual(self.app.timeline.cursor,count)
        self.assertIn('-86 decimal',self.app.word_text(170))
        self.app.load(13); self.app.draw(); self.field('bit_a','-8'); self.field('bit_shift','2')
        self.click('shiftop:ARITHMETIC'); self.key(pygame.K_END)
        self.assertEqual(self.app.timeline.state['result'],254); self.assertEqual(self.app.timeline.state['logical'],62)
        state=deepcopy(self.app.timeline.state)
        self.field('bit_shift','9'); self.assertTrue(self.app.error); self.assertEqual(self.app.bit_shift,2); self.assertEqual(self.app.timeline.state,state)

    def test_negation_minimum_zero_and_xor_input(self):
        self.app.load(14); self.click('step2'); self.finish_play()
        self.assertEqual(self.app.bit_a,-128); self.assertEqual(self.app.timeline.state['result'],128)
        self.assertIn('-128 decimal',self.app.word_text(128)); self.assertTrue(self.app.timeline.state['overflow'])
        self.app.load(17); self.click('step1'); self.finish_play(); self.assertFalse(self.app.timeline.state['is_power'])
        self.app.load(18); self.app.draw(); self.field('bit_values','1, 2, 1, 7, 2'); self.click('end')
        self.assertEqual(self.app.timeline.state['result'],7)
        state=deepcopy(self.app.timeline.state); self.field('bit_values','1, 1'); self.assertTrue(self.app.error); self.assertEqual(self.app.timeline.state,state)

    def test_subset_shares_custom_knapsack_input(self):
        self.app.load(6); self.app.items=[(3,17),(5,20),(2,6),(4,11),(1,2)]; self.app.capacity=8; self.app.prepare()
        self.app.load(19); self.app.draw(); self.assertEqual(self.app.items,self.app.shared_items)
        self.click('width:4'); self.assertTrue(self.app.error); self.assertEqual(self.app.bit_width,8)
        self.click('end'); expected=self.app.timeline.state['best']; items=self.app.items[:]
        self.click('step2'); self.finish_play(); self.assertEqual(self.app.lesson.module,'knapsack')
        self.assertEqual(self.app.items,items); self.assertEqual(self.app.timeline.state['result'],expected)

    def test_group_menu_scroll_keyboard_resize_and_help(self):
        for size in ((1280,720),(1366,768)):
            self.send(pygame.event.Event(pygame.VIDEORESIZE,w=size[0],h=size[1],size=size))
            self.click('lessons'); self.click('group:Bits'); self.send(pygame.event.Event(pygame.MOUSEWHEEL,x=0,y=-2))
            self.assertEqual(self.app.menu_scroll,2); self.app.focus='lesson19'; self.key(pygame.K_RETURN)
            self.assertEqual(self.app.lesson_index,19)
            self.click('help'); self.assertTrue(self.app.help); self.key(pygame.K_ESCAPE); self.assertFalse(self.app.help)
            self.click('lessons'); self.click('group:Path'); self.click('lesson0'); self.assertEqual(self.app.lesson_index,0)

    def test_loading_closes_help_and_width_clamps_shift(self):
        self.app.help=True; self.app.load(13); self.assertFalse(self.app.help)
        self.app.draw(); self.field('bit_shift','8'); self.click('width:4')
        self.assertEqual(self.app.bit_width,4); self.assertEqual(self.app.bit_shift,4); self.assertFalse(self.app.error)
