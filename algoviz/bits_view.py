"""Bit-specific renderer and controls, using the shared App adapter."""
import pygame
from . import bits
from .lessons import LESSONS
from . import theme

theme.apply(None, globals())  # BG, TEXT, ACCENT, ... ; rebound by app.use_theme()

class BitsView:
    def bits_source(self):
        mode=self.lesson.module
        a,b,w=self.bit_a,self.bit_b,self.bit_width
        if mode=='bit_logic': return bits.logic(a,b,w,self.bit_op)
        if mode=='bit_shift': return bits.shifts(a,w,self.bit_shift,self.bit_shift_op)
        if mode=='bit_negate': return bits.complement(a,w)
        if mode=='bit_clear': return bits.clear_lowest(a,w,self.bit_repeat)
        if mode=='bit_isolate': return bits.isolate(a,w)
        if mode=='bit_power': return bits.clear_lowest(a,w,repeat=False,power=True)
        if mode=='bit_unique': return bits.unique_xor(self.bit_values,w)
        return bits.subsets(self.items,self.capacity,w)

    def bits_step(self,label):
        if label.startswith('Run '): self.bit_op=label[4:]
        elif label in ('Logical right','Arithmetic right','Shift left'):
            self.bit_shift_op={'Logical right':'LOGICAL','Arithmetic right':'ARITHMETIC','Shift left':'LEFT'}[label]
        elif label=='Clear once': self.bit_repeat=False
        elif label=='Count all ones': self.bit_repeat=True
        elif label=='Try zero': self.bit_a=0
        elif label=='Minimum value': self.bit_a=-(1<<(self.bit_width-1)); self.bit_signed=True
        elif label=='Try odd x': self.bit_a=37
        elif label=='Try power': self.bit_a=1<<(self.bit_width//2)
        elif label=='Reorder words': self.bit_values=list(reversed(self.bit_values))
        elif label=='Change example': self.bit_values=[9,2,9,11,2]
        elif label=='Use bag input':
            self.items=self.shared_items[:]; self.capacity=self.shared_capacity
            if len(self.items)>self.bit_width: self.bit_width=8
        elif label=='Open knapsack DP':
            items=self.items[:]; capacity=self.capacity
            self.load(6); self.items=items; self.capacity=capacity; self.prepare(); self.playing=True
            return
        self.prepare(); self.playing=True

    def bits_activate(self,key):
        if key.startswith('width:'):
            old=self.bit_width; old_shift=self.bit_shift; self.bit_width=int(key.split(':')[1])
            self.bit_shift=min(self.bit_shift,self.bit_width)
            try: next(self.bits_source())
            except ValueError as exc: self.bit_width=old; self.bit_shift=old_shift; self.error='Input error: '+str(exc); return
            self.prepare(); self.notice='Width changed: inputs masked, history restarted'
        elif key=='signed': self.bit_signed=not self.bit_signed; self.notice='Signed view' if self.bit_signed else 'Unsigned view'
        elif key.startswith('bitop:'): self.bit_op=key.split(':')[1]; self.prepare()
        elif key.startswith('shiftop:'): self.bit_shift_op=key.split(':')[1]; self.prepare()
        elif key=='usebag': self.bits_step('Use bag input')

    def draw_bits_toolbar(self):
        for x,w in [(20,4),(84,8),(148,16)]: self.button('width:'+str(w),'W='+str(w),(x,143,58,30),w==self.bit_width)
        self.button('signed','Signed' if self.bit_signed else 'Unsigned',(226,143,114,30),self.bit_signed)
        mode=self.lesson.module
        if mode=='bit_unique': self.field('bit_values','Words: ',356,500); apply_x=870
        elif mode=='bit_subset':
            self.field('items','w:v  ',356,400); self.field('capacity','Capacity: ',770,145); apply_x=929
            self.button('usebag','Use bag input',(1025,143,180,30))
        else:
            self.field('bit_a','A: ',356,140); apply_x=510
            if mode=='bit_logic':
                self.field('bit_b','B: ',510,140); apply_x=664
                for i,op in enumerate(('AND','OR','XOR','NOT')): self.button('bitop:'+op,op,(876+i*90,143,82,30),op==self.bit_op)
            elif mode=='bit_shift':
                self.field('bit_shift','Shift: ',510,140); apply_x=664
                for i,(op,label) in enumerate([('LEFT','<<'),('LOGICAL','>> zero'),('ARITHMETIC','>> sign')]): self.button('shiftop:'+op,label,(876+i*118,143,110,30),op==self.bit_shift_op)
        self.button('apply','Apply',(apply_x,143,82,30))

    def word_text(self,value):
        if value is None: return 'pending'
        word=bits.unsigned(value,self.bit_width)
        dec=bits.signed(word,self.bit_width) if self.bit_signed else word
        return f'{dec} decimal   0x{word:0{self.bit_width//4}X}'+(f'   (unsigned {word})' if self.bit_signed else '')

    def draw_bits(self):
        s=self.timeline.state; width=self.bit_width
        self.text(f'{width}-BIT WORDS  |  '+('two\'s complement signed view' if self.bit_signed else 'unsigned view'),self.main.x+16,self.main.y+12,ACCENT)
        base=self.main.x+154; cell=min(76,(self.main.width-172)/width)
        for r,record in enumerate(s.get('rows',[])):
            y=self.main.y+56+r*74; value=record['value']
            digits=value if isinstance(value,list) else [(value>>(width-1-i))&1 for i in range(width)]
            self.text(self.fit(record['label'],128,True),self.main.x+16,y+9,small=True)
            complete=all(v is not None for v in digits)
            word=sum(v<<(width-1-i) for i,v in enumerate(digits)) if complete else None
            for i,v in enumerate(digits):
                color=VISIT if v is not None else CELL
                if i in s.get('flipped',[]): color=ROUTE
                if r>0 and i in s.get('filled',[]): color=FRONT
                if s.get('mode')=='shift' and r==0:
                    count=s.get('iterations',0)
                    lost=range(count) if s.get('shift_op')=='LEFT' else range(width-count,width)
                    if i in lost: color=SWAMP
                if i==s.get('current_bit'): color=CURRENT
                rect=pygame.Rect(base+i*cell,y,cell-2,45)
                pygame.draw.rect(self.screen,color,rect,border_radius=3)
                img=self.font.render('-' if v is None else str(v),True,BG if color in (CURRENT,ROUTE) else TEXT)
                self.screen.blit(img,img.get_rect(center=(rect.centerx,rect.y+13)))
                img=self.small.render(f'2^{width-1-i}',True,BG if color in (CURRENT,ROUTE) else MUTED)
                self.screen.blit(img,img.get_rect(center=(rect.centerx,rect.y+34)))
            self.text(self.word_text(word),base,y+50,MUTED,True)
        mode=s.get('mode')
        if mode=='unique':
            words=s.get('values',[])
            for i,value in enumerate(words):
                x=self.main.x+16+(i%6)*135; y=self.main.bottom-78+(i//6)*32
                color=CURRENT if i==s.get('item_index') else VISIT
                pygame.draw.rect(self.screen,color,(x,y,125,27),border_radius=4)
                self.text(f'{i+1}: {value}',x+8,y+5,BG if color==CURRENT else TEXT,True)
        elif mode=='subset':
            selected=s.get('selected',[])
            self.text('Item -> bit k  |  weight / value',self.main.x+16,self.main.y+137,ACCENT,True)
            for i,(weight,value) in enumerate(self.items):
                y=self.main.y+164+i*24
                pygame.draw.rect(self.screen,SETTLED if i in selected else VISIT,(self.main.x+16,y,18,18),border_radius=3)
                self.text(f'Item {i+1} -> bit {i}:  {weight} / {value}'+('  selected' if i in selected else ''),self.main.x+44,y,small=True)
            self.text(f'Weight {s.get("weight",0)} / {self.capacity}  |  value {s.get("value",0)}  |  best {s.get("best",0)}',self.main.x+16,self.main.bottom-26,ROUTE,True)
        elif mode=='shift':
            self.text('Purple: discarded source bits  |  blue: newly filled bits',self.main.x+16,self.main.bottom-46,MUTED,True)
            self.text('Discarded (in order): '+str(s.get('discarded',[])),self.main.x+16,self.main.bottom-24,SWAMP,True)
        elif mode=='power': self.text('Power-of-two test uses the unsigned W-bit word.',self.main.x+16,self.main.bottom-30,MUTED,True)
        elif mode=='negate': self.text('The sign minimum wraps to itself; the final carry is discarded.',self.main.x+16,self.main.bottom-30,MUTED,True)

    def display_value(self,value):
        if value is None: return 'pending'
        return str(bits.signed(value,self.bit_width) if self.bit_signed else bits.unsigned(value,self.bit_width))

    def bits_panel_lines(self):
        s=self.timeline.state; mode=s.get('mode'); result=s.get('result')
        lines=[f'W={self.bit_width}; mask 0x{bits.mask_for(self.bit_width):X}',
               'Result decimal: '+self.display_value(result),
               'Result hex: '+('pending' if result is None else f'0x{result:0{self.bit_width//4}X}')]
        if mode in ('logic','negate','isolate'): lines += [f'Bits filled: {s.get("bits_computed",0)}/{self.bit_width}']
        if mode in ('clear','popcount'): lines += [f'Iterations: {s.get("iterations",0)}',f'Original ones: {bin(bits.unsigned(self.bit_a,self.bit_width)).count("1")}',f'Remaining: {s.get("remaining",bits.unsigned(self.bit_a,self.bit_width))}']
        elif mode=='negate': lines += [f'Carry: {s.get("carry",0)}',f'Sign minimum wrap: {s.get("overflow",False)}']
        elif mode=='power': lines += [f'Nonzero guard: {s.get("nonzero","pending")}',f'Power of two: {s.get("is_power","pending")}']
        elif mode=='shift':
            lines += [f'Steps: {s.get("iterations",0)}/{self.bit_shift}']
            if s.get('shift_op')=='LEFT': lines += ['Left: '+self.display_value(s.get('logical'))]
            else: lines += ['Logical: '+self.display_value(s.get('logical')), 'Arithmetic: '+self.display_value(s.get('arithmetic'))]
        elif mode=='subset': lines += [f'Subsets visited: {s.get("subsets",0)}',f'Fits: {s.get("feasible",True)}',f'Best value: {s.get("best",0)}','Best items: '+str([i+1 for i in s.get('best_selected',[])])]
        elif mode=='unique': lines += [f'Words processed: {s.get("iterations",0)}',f'Accumulator: {s.get("accumulator",0)}','Pairs cancel: a XOR a = 0']
        if 'python_result' in s: lines += ['Raw Python result: '+str(s['python_result'])]
        return lines

    def draw_bits_side(self):
        s=self.timeline.state; op=s.get('op'); truth=s.get('truth')
        self.text('DECISION / TRUTH',self.side.x+16,self.side.y+12,ACCENT)
        if op:
            self.text(op+' truth table',self.side.x+16,self.side.y+47)
            self.text('A        B       OUT',self.side.x+26,self.side.y+78,MUTED,True)
            pairs=[(0,None),(1,None)] if op=='NOT' else [(0,0),(0,1),(1,0),(1,1)]
            for i,(a,b) in enumerate(pairs):
                result=bits.logic_result(a,b or 0,4,op)&1
                y=self.side.y+105+i*28; selected=truth is not None and (a,b,result)==truth
                pygame.draw.rect(self.screen,CURRENT if selected else VISIT,(self.side.x+16,y,220,25),border_radius=3)
                self.text(f'{a}        {"-" if b is None else b}         {result}',self.side.x+26,y+4,BG if selected else TEXT,True)
            top=self.side.y+228
        else: top=self.side.y+48
        lines=self.bits_panel_lines(); visible=max(1,(self.side.bottom-24-top)//24)
        self.scroll=max(0,min(self.scroll,max(0,len(lines)-visible)))
        for i,line in enumerate(lines[self.scroll:self.scroll+visible]): self.text(self.fit(line,self.side.width-30,True),self.side.x+16,top+i*24,small=True)
        if len(lines)>visible: self.text('Scroll for more data',self.side.x+16,self.side.bottom-23,MUTED,True)
