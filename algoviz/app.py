"""Pygame adapter: input, rendering and playback only."""
import os
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
import argparse
from copy import deepcopy
import pygame
from .engine import Timeline
from .pathfinding import search, maze, frontier_view
from .lessons import LESSONS, path_input
from .capture import save_png
from .dp import fibonacci, lcs, knapsack, validate_items
from .greedy import coins_compare, activity_compare, bag_compare
from .bits_view import BitsView
from .education import about_lines, about_rows, help_sections, TOOLTIPS

from . import theme, bits_view

theme.apply(None, globals())  # BG, PANEL, TEXT, ACCENT, ... from ALGOVIZ_THEME (default: arcade)


def use_theme(name):
    """Switch colors for every renderer module; 'classic' restores the original look."""
    theme.apply(name, globals(), vars(bits_view))

class App(BitsView):
    def __init__(self, size=(1280,720)):
        pygame.init()
        self.screen=pygame.display.set_mode(size,pygame.RESIZABLE)
        pygame.display.set_caption('Algorithm Lab — Path / DP / Greedy / Bits')
        self.font=pygame.font.SysFont('Arial',19)
        self.small=pygame.font.SysFont('Arial',16)
        self.titlefont=pygame.font.SysFont('Arial',25,bold=True)
        self.heading=pygame.font.SysFont('Arial',17,bold=True)
        self.bold=pygame.font.SysFont('Arial',16,bold=True)
        self.boldbig=pygame.font.SysFont('Arial',19,bold=True)
        self._backdrop=None
        self.clock=pygame.time.Clock()
        self.running=True; self.playing=False; self.speed=60; self.lesson_speeds={}; self.elapsed=0
        self.buttons={}; self.dropdown=False; self.menu_scroll=0; self.scroll=0
        self.help=False; self.about=False; self.modal_text_rects=[]; self.focus=None; self.edit_text=''; self.error=''; self.notice=''
        self.tool='Wall'; self.hover=None; self.dragging=False; self.pointer=(0,0)
        self.fields={}; self.fill_only=False; self.results={}
        self.shared_items=[(2,12),(4,20),(6,24)]; self.shared_capacity=10; self.menu_group='Path'
        self.load(0,initial=True)

    def load(self,index,initial=False,reset=False):
        if hasattr(self, "lesson_index") and not reset:
            self.lesson_speeds[self.lesson_index]=self.speed
        self.lesson_index=index; self.lesson=LESSONS[index]
        if reset: self.lesson_speeds.pop(index,None)
        self.speed=self.lesson_speeds.get(index,self.lesson.default_speed)
        self.grid=path_input(index); self.algorithm='BFS'; self.hw=1
        self.seed=42
        self.n=6; self.fib_mode='both'; self.a='ABCBDAB'; self.b='BDCABA'
        self.items=[(2,12),(4,20),(6,24)]; self.capacity=10
        self.coins=[1,5,10,25] if index==8 else [1,3,4]; self.amount=63 if index==8 else 6
        self.activities=[(0,4),(4,8),(3,5)] if index==10 else [(0,10),(1,2),(2,3),(3,4)]
        self.rule='duration' if index==10 else 'start'; self.greedy_only=False
        self.bit_width=8; self.bit_signed=self.lesson.module=='bit_negate'; self.bit_op='AND'
        self.bit_shift=2; self.bit_shift_op='LOGICAL'; self.bit_repeat=True
        self.bit_a=5 if self.lesson.module=='bit_negate' else 12 if self.lesson.module=='bit_power' else 152
        self.bit_b=60; self.bit_values=[5,12,5,7,12]
        if self.lesson.module=='bit_subset': self.items=self.shared_items[:]; self.capacity=self.shared_capacity
        self.menu_group=self.lesson.group; self.menu_scroll=0
        self.fill_only=False; self.results={}
        self.playing=False; self.scroll=0; self.error=''; self.focus=None
        self.dropdown=False; self.help=False; self.about=False
        self.notice='' if initial else 'Lesson loaded: input replaced'
        self.prepare()

    def prepare(self):
        self.fill_only=False; self.greedy_only=False
        module=self.lesson.module
        if module=='path': source=search(deepcopy(self.grid),self.algorithm,self.hw)
        elif module=='fib': source=fibonacci(self.n,self.fib_mode)
        elif module=='lcs': source=lcs(self.a,self.b)
        elif module=='knapsack': source=knapsack(self.items,self.capacity)
        elif module.startswith('bit_'): source=self.bits_source()
        else: source=self.greedy_source()
        if module in ('knapsack','bag'): self.shared_items=self.items[:]; self.shared_capacity=self.capacity
        self.timeline=Timeline(source)
        self.timeline.forward(); self.playing=False; self.elapsed=0; self.scroll=0

    def execute_step(self,index):
        label=self.lesson.steps[index]
        self.error=''
        self.execute_other_step(label)

    def execute_other_step(self,label):
        if self.lesson.module.startswith('bit_'): self.bits_step(label)
        elif label=='Run naive': self.fib_mode='naive'; self.prepare(); self.playing=True
        elif label=='Run memo': self.fib_mode='both'; self.prepare(); self.playing=True
        elif label=='Compare n=8': self.n=8; self.fib_mode='both'; self.prepare(); self.playing=True
        elif label=='Fill table': self.prepare(); self.fill_only=True; self.playing=True
        elif label=='Trace back': self.fill_only=False; self.playing=True
        elif label=='Swap strings': self.a,self.b=self.b,self.a; self.prepare(); self.playing=True
        elif label=='Compare greedy':
            inputs=(self.items[:],self.capacity)
            self.load(next(i for i,l in enumerate(LESSONS) if l.module=='bag'))
            self.items,self.capacity=inputs; self.prepare(); self.playing=True
        else: self.greedy_step(label)
        self.notice=label

    def greedy_source(self):
        if self.lesson.module=='coin': return coins_compare(self.coins,self.amount)
        if self.lesson.module=='activity': return activity_compare(self.activities,self.rule)
        return bag_compare(self.items,self.capacity)

    def greedy_step(self,label):
        if label in ('Run greedy','Run ratios'):
            self.prepare(); self.greedy_only=True; self.playing=True
        elif label=='Run optimal':
            self.greedy_only=False; self.playing=True
        elif label in ('Canonical coins','Counterexample'):
            self.coins=[1,5,10,25] if label=='Canonical coins' else [1,3,4]
            self.amount=63 if label=='Canonical coins' else 6
            self.prepare(); self.greedy_only=False; self.playing=True
        elif label in ('Run start','Run finish','Run duration'):
            if self.timeline.state.get('done'):
                s=self.timeline.state; self.results[self.rule]=(s.get('greedy_count'),s.get('optimal_count'))
            self.rule=label.split()[1]; self.prepare(); self.playing=True; self.greedy_only=False
        elif label in ('Try duration trap','Try start trap'):
            self.load(10 if label=='Try duration trap' else 9); self.playing=True
        elif label=='Open DP table':
            items=self.items[:]; capacity=self.capacity
            self.load(6); self.items=items; self.capacity=capacity; self.prepare(); self.playing=True

    def draw_greedy(self):
        s=self.timeline.state; m=self.lesson.module
        if m=='coin':
            self.text('GREEDY: '+str(s.get('greedy_count') if s.get('greedy_count') is not None else 'pending')+' coins  |  OPTIMAL: '+str(s.get('optimal_count') if s.get('optimal_count') is not None else 'pending')+' coins',self.main.x+16,self.main.y+12,ACCENT)
            self.draw_coin_table()
        elif m=='activity':
            self.text('GREEDY: '+self.rule+'  |  OPTIMAL: exhaustive search',self.main.x+16,self.main.y+14,ACCENT)
            intervals=self.activities; maximum=max((b for a,b in intervals),default=1)
            ox=self.main.x+280; tw=self.main.width-306; top=self.main.y+76
            for t in range(0,maximum+1,max(1,(maximum+7)//8)):
                x=ox+tw*t/maximum; pygame.draw.line(self.screen,GRIDLINE,(x,top-14),(x,self.main.bottom-32))
                self.text(t,x-5,top-37,MUTED,True)
            row_height=min(42,(self.main.height-118)//max(1,len(intervals)))
            for i,(a,b) in enumerate(intervals):
                y=top+i*row_height
                label=f'{i+1}: '+('selected' if i in s.get('selected',[]) else s.get('rejected',{}).get(i,'pending'))
                self.text(label,self.main.x+16,y+3,small=True)
                color=SETTLED if i in s.get('selected',[]) else SWAMP if i in s.get('rejected',{}) else VISIT
                if i==s.get('current'): color=CURRENT
                pygame.draw.rect(self.screen,color,(ox+tw*a/maximum,y,max(2,tw*(b-a)/maximum),17),border_radius=3)
                if i in s.get('optimal',[]): pygame.draw.rect(self.screen,ROUTE,(ox+tw*a/maximum,y+20,max(2,tw*(b-a)/maximum),5))
            self.text('Thick bars: greedy choices  |  yellow underline: optimal set',self.main.x+16,self.main.bottom-26,MUTED,True)
        else:
            self.text('SAME ITEMS: capacity '+str(self.capacity),self.main.x+16,self.main.y+14,ACCENT)
            x0=self.main.x+16; x1=x0+252; x2=x1+180; x3=x2+180
            for x,title in [(x0,'ITEM / ratio'),(x1,'FRACTIONAL'),(x2,'0/1 GREEDY'),(x3,'0/1 DP')]: self.text(title,x,self.main.y+53,small=True)
            optimal=s.get('dp',{}).get('selected',[])
            for i,(w,v) in enumerate(self.items):
                y=self.main.y+88+i*32
                self.text(f'{i+1}: w={w}, v={v}  r={v/w:.2f}',x0,y,small=True)
                fraction=s.get('fractional',{}).get(i,0)
                pygame.draw.rect(self.screen,VISIT,(x1,y+2,128,18),border_radius=3)
                if fraction: pygame.draw.rect(self.screen,SETTLED,(x1,y+2,float(fraction)*128,18),border_radius=3)
                self.text(f'{float(fraction):.2f}',x1+135,y,small=True)
                for x,selected in [(x2,s.get('whole',[])),(x3,optimal)]:
                    pygame.draw.rect(self.screen,SETTLED if i in selected else VISIT,(x,y+2,18,18),border_radius=3)
                    self.text('take' if i in selected else '-',x+26,y,small=True)
            y=self.main.bottom-72
            for x,value in [(x1,s.get('fractional_value',0)),(x2,s.get('greedy_value',0)),(x3,s.get('optimal_value'))]: self.text('Value: '+str(value),x,y,ROUTE)
            self.text('Open DP table to inspect every cell and the traceback.',x0,self.main.bottom-26,MUTED,True)

    def draw_coin_table(self):
        s=self.timeline.state; values=s.get('dp',[]); self.coin_rects={}
        current=s.get('current') if s.get('phase')=='optimal' else None
        coin=s.get('best_coin')
        formula=f'dp[{current}] = dp[{current-coin}] + 1' if current is not None and coin is not None else 'dp[t] = 1 + min(dp[t - coin])'
        self.text(formula+'  |  cells show amount: coin count',self.main.x+16,self.main.y+37,ACCENT,True)
        deps=set(s.get('dependencies',[])); cell=(self.main.width-32)//10
        rows=max(1,(len(values)+9)//10); height=min(32,(self.main.height-76)//rows)
        for t,value in enumerate(values):
            rect=pygame.Rect(self.main.x+16+(t%10)*cell,self.main.y+64+(t//10)*height,cell-3,height-1)
            self.coin_rects[t]=rect
            color=VISIT if value is not None else CELL
            if t in deps: color=FRONT
            if t==current: color=CURRENT
            pygame.draw.rect(self.screen,color,rect,border_radius=3)
            image=self.small.render(f'{t}: {"-" if value is None else value}',True,BG if color==CURRENT else TEXT)
            self.screen.blit(image,image.get_rect(center=rect.center))

    def greedy_panel_lines(self):
        s=self.timeline.state; m=self.lesson.module
        if m=='coin':
            lines=[f'Denominations: {sorted(set(self.coins),reverse=True)}','Choice: largest fitting coin',
                   f'Greedy count: {s.get("greedy_count")}',f'Optimal count: {s.get("optimal_count")}',
                   f'Computed DP cells: {s.get("cells",0)}','DP ties: larger coin first',
                   'Dependencies: '+str(s.get('dependencies',[])),
                   'Greedy: '+str(s.get('greedy',[])), 'Optimal: '+str(s.get('optimal',[])), '', 'Amount -> fewest coins']
            return lines+[f'{i}: {v if v is not None else "unreachable"}'+(' < current' if s.get('phase')=='optimal' and i==s.get('current') else '') for i,v in enumerate(s.get('dp',[]))]
        if m=='activity':
            return ['Rule: earliest '+self.rule,'Ties: original input order',f'Greedy count: {s.get("greedy_count")}',
                    f'Optimal count: {s.get("optimal_count")}',f'Subsets checked: {s.get("subsets",0)}',
                    'Touching endpoints are compatible','', 'Earlier: greedy / optimal']+[f'{k}: {a} / {b}' for k,(a,b) in self.results.items()]+[
                    'Next candidates (in order):']+[f'{i+1}: {self.activities[i]}' for i in s.get('order',[])]+[
                    'Optimal meetings: '+str([i+1 for i in s.get('optimal',[])])]
        return [f'Phase: {s.get("phase")}',f'Remaining capacity: {s.get("remaining")}',
                'Priority: value / weight descending','Ties: original input order',
                f'Fractional value: {s.get("fractional_value")}',f'0/1 greedy: {s.get("greedy_value")}',
                f'0/1 optimal: {s.get("optimal_value")}',f'DP cells: {s.get("dp",{}).get("cells",0)}',
                'Current DP cell: '+str(s.get('dp',{}).get('current')),
                'Dependencies: '+str(s.get('dp',{}).get('dependencies',[])),
                '', 'Next ratio candidates:']+[f'{i+1}: {self.items[i][1]}/{self.items[i][0]}' for i in s.get('order',[])]+[
                'Value gap: '+str(s['optimal_value']-s['greedy_value']) if s.get('optimal_value') is not None else 'Objective: total value']

    def text(self,value,x,y,color=TEXT,small=False):
        font=self.small if small else self.font
        self.screen.blit(font.render(str(value),True,color),(x,y))

    def fit(self,value,width,small=False):
        font=self.small if small else self.font
        value=str(value)
        if font.size(value)[0]<=width: return value
        while value and font.size(value+'...')[0]>width:
            value=value[:-1]
        return value+'...'

    def wrap(self,value,width,font):
        lines=['']
        for word in str(value).split():
            trial=(lines[-1]+' '+word).strip()
            if font.size(trial)[0]<=width or not lines[-1]: lines[-1]=trial
            else: lines.append(word)
        return lines

    def blit_text(self,value,font,color,pos):
        surface=font.render(value,True,color)
        self.screen.blit(surface,pos)
        self.modal_text_rects.append(surface.get_rect(topleft=pos))

    def draw_rows(self,rows,x,y,width,key_width,font,line_height,draw=True):
        """Key/description rows; descriptions wrap inside their column. Returns the next y."""
        for key,value in rows:
            lines=self.wrap(value,width-key_width,font)
            if draw:
                if key: self.blit_text(key,self.bold,ACCENT,(x,y+(line_height-self.bold.get_height())//2))
                for i,line in enumerate(lines): self.blit_text(line,font,TEXT,(x+key_width,y+i*line_height))
            y+=len(lines)*line_height+6
        return y

    def draw_section(self,title,rows,x,y,width,draw=True):
        if draw:
            self.blit_text(title,self.heading,HEADING,(x,y))
            pygame.draw.line(self.screen,DIVIDER,(x,y+24),(x+width,y+24))
        return self.draw_rows(rows,x,y+32,width,124,self.small,21,draw)+10

    def modal_frame(self,title,subtitle,body_height):
        w,h=self.screen.get_size()
        height=74+body_height+30
        r=pygame.Rect(150,max(16,(h-height)//2),w-300,height)
        self.modal_rect=r; self.modal_text_rects=[]
        if ARCADE:
            shade=pygame.Surface(self.screen.get_size(),pygame.SRCALPHA); shade.fill((0,0,0,110))
            self.screen.blit(shade,(0,0))
        pygame.draw.rect(self.screen,MODAL,r,border_radius=10)
        pygame.draw.rect(self.screen,ACCENT if ARCADE else DIVIDER,r,2 if ARCADE else 1,border_radius=10)
        self.blit_text(title,self.titlefont,ACCENT,(r.x+24,r.y+16))
        self.blit_text(subtitle,self.small,MUTED,(r.x+26+self.titlefont.size(title)[0]+14,r.y+24))
        self.blit_text('Esc or click outside to close',self.small,MUTED,(r.x+24,r.bottom-30))
        return r

    def draw_help(self):
        sections=help_sections(self.lesson.module)
        half=(len(sections)+1)//2
        columns=(sections[:half],sections[half:])
        width=self.screen.get_width()-300; col=(width-48-36)//2
        def column_height(column):
            y=0
            for title,rows in column: y=self.draw_section(title,rows,0,y,col,False)
            return y
        r=self.modal_frame('Help',self.lesson.group+' lessons',max(map(column_height,columns)))
        for c,column in enumerate(columns):
            x=r.x+24+c*(col+36); y=r.y+66
            for title,rows in column: y=self.draw_section(title,rows,x,y,col)
        pygame.draw.line(self.screen,DIVIDER,(r.x+24+col+18,r.y+66),(r.x+24+col+18,r.bottom-42))

    def draw_about(self):
        rows=about_rows(about_lines(self.lesson,self.lesson_index))
        width=self.screen.get_width()-300-48
        body=self.draw_rows(rows,0,0,width,124,self.font,25,False)
        r=self.modal_frame(self.lesson.title,'About this lesson',body)
        self.draw_rows(rows,r.x+24,r.y+70,width,124,self.font,25)

    def button(self,key,label,rect,active=False):
        r=pygame.Rect(rect); self.buttons[key]=r
        font=self.small if r.height<32 else self.font
        if not ARCADE:
            pygame.draw.rect(self.screen,BUTTON_ON if active else BUTTON,r,border_radius=6)
            pygame.draw.rect(self.screen,ACCENT if active else BUTTON_EDGE,r,1,border_radius=6)
            img=font.render(label,True,TEXT)
            self.screen.blit(img,(r.centerx-img.get_width()/2,r.centery-img.get_height()/2))
            return
        # Arcade key: a darker drop edge under a raised face, all inside the same hit box.
        face=BUTTON_ON if active else BUTTON
        if not active and r.collidepoint(self.pointer): face=tuple(min(255,c+24) for c in face)
        top=pygame.Rect(r.x,r.y,r.w,r.h-3)
        pygame.draw.rect(self.screen,tuple(c//2 for c in face),r,border_radius=9)
        pygame.draw.rect(self.screen,face,top,border_radius=9)
        pygame.draw.line(self.screen,tuple(min(255,c+55) for c in face),(top.x+9,top.y+2),(top.right-10,top.y+2))
        pygame.draw.rect(self.screen,ACCENT if active else BUTTON_EDGE,top,1,border_radius=9)
        bold=self.bold if font is self.small else self.boldbig
        if bold.size(label)[0]<=r.w-8: font=bold
        img=font.render(label,True,TEXT)
        self.screen.blit(img,(top.centerx-img.get_width()/2,top.centery-img.get_height()/2))

    def draw_backdrop(self):
        if not ARCADE:
            self.screen.fill(BG); return
        size=self.screen.get_size()
        if self._backdrop is None or self._backdrop.get_size()!=size:
            w,h=size; surf=pygame.Surface(size); bottom=(38,14,62)
            for y in range(h):
                t=y/max(1,h-1)
                pygame.draw.line(surf,[round(a+(b-a)*t) for a,b in zip(BG,bottom)],(0,y),(w,y))
            line=[min(255,c+10) for c in BG]
            for x in range(0,w,32): pygame.draw.line(surf,line,(x,0),(x,h))
            for y in range(0,h,32): pygame.draw.line(surf,line,(0,y),(w,y))
            self._backdrop=surf
        self.screen.blit(self._backdrop,(0,0))

    def panel(self,rect):
        if not ARCADE:
            pygame.draw.rect(self.screen,PANEL,rect,border_radius=8); return
        halo=pygame.Surface((rect.w+16,rect.h+16),pygame.SRCALPHA)
        pygame.draw.rect(halo,(*ACCENT,26),halo.get_rect(),border_radius=18)
        self.screen.blit(halo,(rect.x-8,rect.y-8))
        pygame.draw.rect(self.screen,PANEL,rect,border_radius=12)
        pygame.draw.rect(self.screen,DIVIDER,rect,2,border_radius=12)
        pygame.draw.line(self.screen,ACCENT,(rect.x+16,rect.y),(rect.x+96,rect.y),3)

    def layout(self):
        w,h=self.screen.get_size()
        self.main=pygame.Rect(20,184,w-398,h-324)
        self.side=pygame.Rect(w-358,184,338,h-324)
        self.bottom=h-120

    def draw(self):
        self.layout(); self.buttons={}; self.fields={}
        w,h=self.screen.get_size()
        self.draw_backdrop()
        if ARCADE: self.screen.blit(self.titlefont.render('ALGORITHM LAB',True,BUTTON_ON),(23,17))
        self.screen.blit(self.titlefont.render('ALGORITHM LAB',True,ACCENT),(20,14))
        self.button('lessons',self.lesson.title+'  v',(268,12,382,38))
        self.button('about','i',(824,12,38,38),self.about)
        self.button('reset','Reset lesson',(666,12,144,38))
        self.button('help','?',(w-60,12,40,38),self.help)
        for i,label in enumerate(self.lesson.steps):
            self.button(f'step{i}',f'{i+1}. {label}',(20+i*250,62,238,38))
        self.text('Observe: '+self.lesson.question,20,110)
        self.draw_toolbar()
        self.panel(self.main); self.panel(self.side)
        if self.lesson.module=='path': self.draw_path()
        elif self.lesson.module=='fib': self.draw_fib()
        elif self.lesson.module in ('lcs','knapsack'): self.draw_table()
        elif self.lesson.module.startswith('bit_'): self.draw_bits()
        else: self.draw_greedy()
        self.draw_side()
        for key,label,x,wd in [('back','< Back',20,90),('play','Pause' if self.playing else 'Play',120,90),
                              ('next','Step >',220,90),('home','|< Start',320,100),('end','End >|',430,100),
                              ('speed:slow','Slow',550,68),('speed:normal','Normal',626,80),('speed:fast','Fast',714,68),
                              ('slower','-',794,30),('faster','+',928,30)]:
            mode='normal' if self.speed==self.lesson.default_speed else 'fast' if self.speed==min(240,self.lesson.default_speed*2) else 'slow' if self.speed==max(1,self.lesson.default_speed*.5) else None
            active=key=='speed:'+str(mode)
            self.button(key,label,(x,self.bottom,wd,38),active)
        self.text(f'{self.speed:g} ev/s',832,self.bottom+10,small=True)
        self.text(f'Event {self.timeline.cursor} / {len(self.timeline.events)}'+(' (end)' if self.timeline.exhausted else ''),978,self.bottom+10,small=True)
        self.draw_legend()
        pygame.draw.rect(self.screen,STATUS,(0,h-34,w,34))
        if ARCADE: pygame.draw.line(self.screen,ACCENT,(0,h-34),(w,h-34),2)
        msg=self.error or ((self.notice+' · ') if self.notice else '')+self.timeline.message
        guide=' · Space play/pause · arrows step/back · R rewind'
        self.text(self.fit(msg+guide,w-30,True),15,h-26,ERROR if self.error else TEXT,True)
        if self.help: self.draw_help()
        if self.about: self.draw_about()
        self.tooltip_rect=None
        if not (self.about or self.help or self.dropdown):
            for i,label in enumerate(self.lesson.steps):
                if self.buttons['step'+str(i)].collidepoint(self.pointer):
                    message=TOOLTIPS[label]; width=self.small.size(message)[0]+24
                    self.tooltip_rect=pygame.Rect(min(self.pointer[0],w-width-12),104,width,30)
                    pygame.draw.rect(self.screen,TOOLTIP,self.tooltip_rect,border_radius=5)
                    self.text(message,self.tooltip_rect.x+12,self.tooltip_rect.y+7,small=True)
        if self.dropdown:
            indices=self.menu_indices(); visible=min(6,len(indices))
            self.menu=pygame.Rect(268,54,550,50+visible*34)
            pygame.draw.rect(self.screen,BUTTON,self.menu,border_radius=6)
            for i,group in enumerate(('Path','DP','Greedy','Bits')):
                self.button('group:'+group,group,(274+i*134,58,128,30),group==self.menu_group)
            for offset,index in enumerate(indices[self.menu_scroll:self.menu_scroll+visible]):
                self.button('lesson'+str(index),LESSONS[index].title,(274,98+offset*34,538,30),index==self.lesson_index)
        if self.focus in self.buttons:
            pygame.draw.rect(self.screen,CURRENT,self.buttons[self.focus].inflate(4,4),2,border_radius=7)
        pygame.display.flip()

    def draw_toolbar(self):
        if self.lesson.module.startswith('bit_'):
            self.draw_bits_toolbar(); return
        if self.lesson.module!='path':
            self.draw_other_toolbar()
            return
        for i,a in enumerate(('BFS','DFS','Dijkstra','A*','A* (h×3)')):
            self.button('algo'+a,a,(20+i*132,62,124,38),a==self.path_label())
        for i,t in enumerate(('Wall','Swamp','Erase','Start','Goal')):
            self.button('tool'+t,t,(20+i*78,143,72,30),self.tool==t)
        self.button('maze','Random maze',(420,143,140,30))
        self.button('clear','Clear',(574,143,78,30))
        self.field('seed','Seed: ',666,140)

    def path_label(self):
        return 'A* (h×3)' if self.algorithm=='A*' and self.hw==3 else self.algorithm

    def record_result(self):
        state=self.timeline.state
        if self.lesson.module=='path' and state.get('done'):
            self.results[self.path_label()]=(state.get('cost'),state.get('length'),state.get('expanded'))

    def draw_path(self):
        state=self.timeline.state
        size=min((self.main.width-24)/self.grid.width,(self.main.height-24)/self.grid.height)
        self.cell_size=size
        self.grid_origin=(self.main.x+(self.main.width-size*self.grid.width)/2,self.main.y+(self.main.height-size*self.grid.height)/2)
        ox,oy=self.grid_origin
        frontier={e[0] for e in frontier_view(state) if not e[4]}
        path=set(state.get('path',[]))
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                p=(x,y); color=CELL
                if p in self.grid.weights: color=SWAMP
                if p in state.get('dist',{}): color=CELL_SEEN
                if p in state.get('visited',{}): color=VISIT
                if state.get('settled',{}).get(p): color=SETTLED
                if p in frontier: color=FRONT
                if p==state.get('current'): color=CURRENT
                if p in path: color=ROUTE
                if p in self.grid.walls: color=WALL
                rect=pygame.Rect(round(ox+x*size),round(oy+y*size),max(1,int(size)-2),max(1,int(size)-2))
                pygame.draw.rect(self.screen,color,rect,border_radius=2 if size>10 else 0)
                label='S' if p==self.grid.start else 'G' if p==self.grid.goal else str(self.grid.weights[p]) if p in self.grid.weights else str(state['dist'][p]) if p in state.get('dist',{}) and self.algorithm!='A*' else ''
                if size>=28 and label:
                    img=self.small.render(label,True,TEXT if p not in path and p!=state.get('current') else BG)
                    self.screen.blit(img,img.get_rect(center=rect.center))
        self.hover=self.cell_at(self.pointer)

    def cell_at(self,pos):
        ox,oy=self.grid_origin; s=self.cell_size
        p=(int((pos[0]-ox)//s),int((pos[1]-oy)//s))
        return p if self.grid.contains(p) and pos[0]>=ox and pos[1]>=oy else None

    def panel_lines(self):
        if self.lesson.module!='path': return self.other_panel_lines()
        s=self.timeline.state
        lines=[f'{self.algorithm}  |  seed {self.grid.seed}',
               'Neighbors: Up > Right > Down > Left',
               'PQ ties: first insertion wins',
               f'Expanded: {s.get("expanded",0)} | peak: {s.get("max_frontier",0)}',
               f'Relaxations: {s.get("relaxations",0)}',
               ('Path: unreachable' if s.get('done') and s.get('cost') is None else
                f'Path: cost {s.get("cost") if s.get("cost") is not None else "-"} / edges {s.get("length") if s.get("length") is not None else "-"}')]
        if self.hover is not None:
            p=self.hover; g=s.get('dist',{}).get(p); hh=abs(p[0]-self.grid.goal[0])+abs(p[1]-self.grid.goal[1])
            lines += [f'Hover {p}: entry cost {self.grid.cost(p)}',f'g={g}  h={hh}  f={g+self.hw*hh if g is not None else "?"} (h x {self.hw})']
        comparison=dict(self.results)
        if s.get('done'): comparison[self.path_label()]=(s.get('cost'),s.get('length'),s.get('expanded'))
        lines += ['Compare: algorithm / cost / edges / exp']
        lines += [f'{a}: {c} / {length} / {expanded}' for a,(c,length,expanded) in comparison.items()]
        lines += [('Priority queue' if self.algorithm in ('Dijkstra','A*') else 'Stack' if self.algorithm=='DFS' else 'Queue')+' — next pop first']
        for p,k,order,g,stale in frontier_view(s):
            lines.append(f'{p} key={k} g={g} #{order}'+(' stale' if stale else ''))
        if not s.get('frontier'): lines.append('(empty)')
        return lines

    def field_value(self,name):
        if name=='bit_values': return ', '.join(map(str,self.bit_values))
        if name=='items': return ', '.join(f'{w}:{v}' for w,v in self.items)
        if name=='coins': return ', '.join(map(str,self.coins))
        if name=='activities': return ', '.join(f'{a}:{b}' for a,b in self.activities)
        return str(getattr(self,name))

    def field(self,name,label,x,width):
        key='field:'+name; rect=pygame.Rect(x,143,width,30)
        self.fields[name]=rect; self.buttons[key]=rect
        pygame.draw.rect(self.screen,BUTTON,rect,border_radius=5)
        value=self.edit_text if self.focus==key else self.field_value(name)
        self.text(self.fit(label+value+('|' if self.focus==key else ''),width-14,True),x+7,149,small=True)

    def draw_other_toolbar(self):
        m=self.lesson.module
        if m=='fib':
            self.field('n','n: ',20,140)
            self.text('n <= 8 keeps every call node readable',340,149,MUTED,True)
            apply_x=175
        elif m=='lcs':
            self.field('a','A: ',20,260); self.field('b','B: ',294,260); apply_x=568
        elif m in ('knapsack','bag'):
            self.field('items','weight:value  ',20,410); self.field('capacity','Capacity: ',444,160); apply_x=618
        elif m=='coin':
            self.field('coins','Coins: ',20,300); self.field('amount','Amount: ',334,160); apply_x=508
        else:
            self.field('activities','start:end  ',20,670); apply_x=704
        self.button('apply','Apply',(apply_x,143,82,30))
    def commit_field(self):
        if not self.focus or not self.focus.startswith('field:'): return
        name=self.focus[6:]; raw=self.edit_text.strip()
        try:
            if name in ('bit_a','bit_b','bit_shift'): value=int(raw,0)
            elif name in ('n','capacity','amount','seed'): value=int(raw)
            elif name in ('items','activities'):
                value=[tuple(map(int,p.strip().split(':'))) for p in raw.split(',') if p.strip()]
                if any(len(p)!=2 for p in value): raise ValueError('Use comma-separated pairs, e.g. 2:12, 4:20')
            elif name=='coins': value=[int(p.strip()) for p in raw.split(',') if p.strip()]
            elif name=='bit_values': value=[int(p.strip(),0) for p in raw.split(',') if p.strip()]
            else: value=raw
            old=getattr(self,name); setattr(self,name,value)
            try:
                if self.lesson.module.startswith('bit_'):
                    next(self.bits_source())
                    if self.lesson.module=='bit_subset': self.validate_table_input()
                elif self.lesson.module=='path':
                    replacement=maze(self.grid.width,self.grid.height,self.seed); replacement.validate()
                elif self.lesson.module=='fib': next(fibonacci(self.n))
                elif self.lesson.module=='lcs':
                    next(lcs(self.a,self.b)); self.validate_table_input()
                elif self.lesson.module in ('knapsack','bag'):
                    validate_items(self.items,self.capacity); self.validate_table_input()
                elif self.lesson.module=='coin': next(self.greedy_source())
                else: next(self.greedy_source())
            except (ValueError,TypeError):
                setattr(self,name,old); raise
            if self.lesson.module=='path': self.grid=replacement
            self.results={}; self.prepare(); self.notice='Input applied: history restarted'; self.focus=None; self.error=''; self.fill_only=False
        except (ValueError,TypeError) as exc:
            self.error='Input error: '+str(exc)

    def table_geometry(self, rows, cols, module=None):
        module=module or self.lesson.module
        label_width=max([104]+[self.small.size(f'{i}: {w}/{v}')[0]+8 for i,(w,v) in enumerate(self.items,1)]) if module in ('knapsack','bag') else 42
        width=(self.main.width-label_width-24)//cols
        height=(self.main.height-88)//rows
        minimum_width=28
        if module in ('knapsack','bag'):
            minimum_width=max(28,self.small.size(str(sum(v for w,v in self.items)))[0]+8)
        if width<minimum_width or height<22:
            raise ValueError('Table too large: use shorter strings, fewer items or lower capacity (<= 25)')
        cell_width=min(max(42,minimum_width),width)
        return pygame.Rect(self.main.x+12+label_width,self.main.y+54,cols*cell_width,rows*min(32,height)),cell_width,min(32,height)

    def validate_table_input(self):
        self.layout()
        if self.lesson.module=='lcs': self.table_geometry(len(self.a)+1,len(self.b)+1)
        else:
            if self.capacity>25: raise ValueError('Display capacity must be 0..25 to fit at 1280 x 720')
            self.table_geometry(len(self.items)+1,self.capacity+1,'knapsack')

    def draw_table(self):
        s=self.timeline.state; table=s.get('table',[])
        self.table_rects={}
        if not table: return
        m=self.lesson.module; area,cell,row_height=self.table_geometry(len(table),len(table[0]))
        ox,oy=area.topleft; current=s.get('current')
        self.text('LCS: longest common subsequence' if m=='lcs' else '0/1 knapsack: one item per row',self.main.x+16,self.main.y+12,ACCENT)
        for j in range(len(table[0])):
            header=('0' if j==0 else s['b'][j-1]) if m=='lcs' else str(j)
            image=self.small.render(header,True,MUTED)
            self.screen.blit(image,image.get_rect(midbottom=(ox+j*cell+cell//2,oy-4)))
        trace=set(s.get('trace',[])); deps=set(s.get('dependencies',[]))
        for i,row in enumerate(table):
            label=('0' if i==0 else s['a'][i-1]) if m=='lcs' else 'none' if i==0 else f'{i}: {s["items"][i-1][0]}/{s["items"][i-1][1]}'
            self.text(label,self.main.x+15,oy+i*row_height+(row_height-19)//2,small=True)
            for j,value in enumerate(row):
                pos=(i,j); color=VISIT if value is not None else CELL
                if pos in deps: color=FRONT
                if pos in trace: color=ROUTE
                if pos==current: color=CURRENT
                rect=pygame.Rect(ox+j*cell,oy+i*row_height,cell-2,row_height-2)
                self.table_rects[pos]=rect
                pygame.draw.rect(self.screen,color,rect,border_radius=3)
                image=self.small.render('-' if value is None else str(value),True,BG if color in (CURRENT,ROUTE) else TEXT)
                self.screen.blit(image,image.get_rect(center=rect.center))
        self.text('Trace: '+s.get('sequence','') if m=='lcs' else 'Selected items: '+str([i+1 for i in s.get('selected',[])]),self.main.x+16,self.main.bottom-26,MUTED,True)

    def draw_fib(self):
        s=self.timeline.state; all_nodes=s.get('nodes',{})
        for variant,top,region_height in [('naive',self.main.y+38,218),('memo',self.main.y+284,80)]:
            self.text(variant.upper()+f' — {s.get(variant+"_calls",0)} calls',self.main.x+16,top-25,ACCENT)
            nodes={k:v for k,v in all_nodes.items() if v['variant']==variant}
            if not nodes: continue
            children={k:[] for k in nodes}; roots=[]
            for k,v in nodes.items():
                if v['parent'] in nodes: children[v['parent']].append(k)
                else: roots.append(k)
            coords={}; leaves=[]
            def place(k,depth):
                child=sorted(children[k],key=lambda c:nodes[c]['side'])
                if not child:
                    x=len(leaves); leaves.append(k)
                else:
                    xs=[place(c,depth+1) for c in child]; x=sum(xs)/len(xs)
                coords[k]=(x,depth); return x
            for root in roots: place(root,0)
            depth=max(y for x,y in coords.values())
            spacing=min(72,(self.main.width-42)/max(1,len(leaves)))
            width=max(1,len(leaves)-1)*spacing
            base=self.main.centerx-width/2
            coords={k:(base+x*spacing,top+12+y*max(10,min(28,(region_height-22)/max(1,depth)))) for k,(x,y) in coords.items()}
            # Unbalanced subtrees can put internal nodes too close on the same row.
            for level in range(depth+1):
                row=sorted((k for k in coords if abs(coords[k][1]-(top+12+level*max(10,min(28,(region_height-22)/max(1,depth)))))<.01),key=lambda k:coords[k][0])
                if not row: continue
                center=(coords[row[0]][0]+coords[row[-1]][0])/2
                last=-float('inf')
                for k in row:
                    x,y=coords[k]; x=max(x,last+26); coords[k]=(x,y); last=x
                shift=(coords[row[0]][0]+coords[row[-1]][0])/2-center
                for k in row: coords[k]=(coords[k][0]-shift,coords[k][1])
            for k,v in nodes.items():
                if v['parent'] in coords: pygame.draw.line(self.screen,MUTED,coords[v['parent']],coords[k],1)
            counts={}
            for v in nodes.values(): counts[v['n']]=counts.get(v['n'],0)+1
            for k,v in nodes.items():
                color=SETTLED if v['hit'] else ROUTE if variant=='naive' and counts[v['n']]>1 else VISIT
                if k==s.get('current'): color=CURRENT
                pygame.draw.circle(self.screen,color,coords[k],11)
                img=self.small.render(str(v['n']),True,BG if color in (ROUTE,CURRENT) else TEXT)
                self.screen.blit(img,img.get_rect(center=coords[k]))

    def other_panel_lines(self):
        s=self.timeline.state; m=self.lesson.module
        if m.startswith('bit_'): return self.bits_panel_lines()
        if m=='fib':
            return [f'Fibonacci n={self.n}',f'Naive calls: {s.get("naive_calls",0)}',f'Memo calls: {s.get("memo_calls",0)}',
                    f'Naive result: {s.get("naive_result") if s.get("naive_result") is not None else "pending"}',f'Memo result: {s.get("memo_result") if s.get("memo_result") is not None else "pending"}',
                    'Naive: 2 * F(n+1) - 1 calls','Memo: 2n - 1 calls (n >= 2)','',
                    'Yellow nodes: repeated n','Teal nodes: memo cache hits','Cache:']+[f'F({k}) = {v}' for k,v in sorted(s.get('memo',{}).items())]
        if m in ('lcs','knapsack'):
            lines=[f'Calculated cells: {s.get("cells",0)}',f'Current: {s.get("current")}',
                   'Dependencies: '+str(s.get('dependencies',[])),f'Result: {s.get("result") if s.get("result") is not None else "pending"}',
                   'Ties: up' if m=='lcs' else 'Ties: skip the current item','',
                   'Traceback:']+[str(p) for p in s.get('trace',[])]
            if m=='knapsack': lines += ['','Items (weight / value):']+[f'{i+1}: {w} / {v}'+(' SELECTED' if i in s.get('selected',[]) else '') for i,(w,v) in enumerate(self.items)]
            return lines
        return self.greedy_panel_lines()

    def draw_side(self):
        if self.lesson.module.startswith('bit_'): self.draw_bits_side(); return
        lines=self.panel_lines(); visible=(self.side.height-80)//24
        self.scroll=max(0,min(self.scroll,max(0,len(lines)-visible)))
        self.text('DATA / DECISION',self.side.x+16,self.side.y+12,ACCENT)
        old=self.screen.get_clip(); self.screen.set_clip(self.side.inflate(-12,-12))
        for i,line in enumerate(lines[self.scroll:self.scroll+visible]):
            self.text(self.fit(line,self.side.width-28,True),self.side.x+16,self.side.y+44+i*24,small=True)
        self.screen.set_clip(old)
        if len(lines)>visible:
            self.text(f'Scroll {self.scroll+1}-{min(len(lines),self.scroll+visible)} / {len(lines)}',self.side.x+16,self.side.bottom-23,MUTED,True)

    def legend_entries(self):
        m=self.lesson.module
        if m.startswith('bit_'):
            legend=[('Bit',VISIT)]+([] if m in ('bit_shift','bit_subset') else [('Current bit',CURRENT)])
            if m in ('bit_clear','bit_power'): legend.append(('Flipped bits',ROUTE))
            if m=='bit_shift': legend += [('New fill',FRONT),('Discarded',SWAMP)]
            if m=='bit_subset': legend += [('Selected item',SETTLED),('Best value',ROUTE)]
            return legend
        if m=='path': return [('Visited',VISIT),('Frontier',FRONT),('Current',CURRENT),('Settled',SETTLED),('Path',ROUTE),('Swamp: 5',SWAMP),('Wall',WALL)]
        if m=='fib': return [('Call',VISIT),('Current',CURRENT),('Cache hit',SETTLED),('Repeated n',ROUTE)]
        if m=='coin': return [('Computed',VISIT),('Dependency',FRONT),('Current / greedy',CURRENT),('Optimal coins',SETTLED)]
        if m=='activity': return [('Pending',VISIT),('Current',CURRENT),('Selected',SETTLED),('Optimal set',ROUTE),('Rejected',SWAMP)]
        if m=='bag': return [('Unused',VISIT),('Taken fraction',SETTLED),('Final values',ROUTE)]
        return [('Computed',VISIT),('Dependency',FRONT),('Current',CURRENT),('Trace',ROUTE)]

    def draw_legend(self):
        y=self.bottom+57
        for i,(label,color) in enumerate(self.legend_entries()):
            x=20+i*(180 if self.lesson.module=='coin' else 150); pygame.draw.rect(self.screen,color,(x,y,18,18),border_radius=3)
            self.text(label,x+25,y,small=True)

    def activate(self,key):
        self.error=''
        if key=='lessons':
            self.dropdown=not self.dropdown; self.menu_group=self.lesson.group; self.menu_scroll=0
        elif key.startswith('group:'): self.menu_group=key[6:]; self.menu_scroll=0
        elif key.startswith('lesson'): self.load(int(key[6:]))
        elif key=='reset': self.load(self.lesson_index,reset=True)
        elif key=='help': self.help=not self.help; self.playing=False; self.dragging=False; self.focus=None
        elif key=='about': self.about=not self.about; self.playing=False; self.focus=None
        elif key.startswith('step'): self.execute_step(int(key[4:]))
        elif key=='play':
            replay=self.timeline.state.get('done') and not self.playing
            if replay: self.timeline.rewind()
            self.playing=not self.playing
            self.notice='Replaying recorded input' if replay else 'Playing' if self.playing else 'Paused'
        elif key=='next': self.playing=False; self.timeline.forward(); self.notice='One event forward'
        elif key=='back': self.playing=False; self.timeline.back(); self.notice='One event back'
        elif key=='home': self.playing=False; self.timeline.rewind(); self.notice='Rewound recorded input'
        elif key=='end': self.playing=False; self.fill_only=False; self.greedy_only=False; self.timeline.finish(); self.record_result(); self.notice='Finished all recorded steps'
        elif key=='faster': self.speed=min(240,self.speed+1)
        elif key=='slower': self.speed=max(1,self.speed-1)
        elif key.startswith('speed:'):
            self.speed=max(1,min(240,self.lesson.default_speed*{'slow':.5,'normal':1,'fast':2}[key[6:]]))
        elif key.startswith('algo'):
            self.record_result()
            self.hw=3 if key[4:]=='A* (h×3)' else 1
            self.algorithm='A*' if self.hw==3 else key[4:]; self.prepare(); self.playing=True
        elif key.startswith('tool'): self.tool=key[4:]
        elif key=='maze': self.grid=maze(seed=self.seed); self.results={}; self.prepare(); self.notice=f'Maze regenerated: seed {self.seed}'
        elif key=='clear': self.grid.walls.clear(); self.grid.weights.clear(); self.results={}; self.prepare(); self.notice='Walls and weights cleared'
        elif key.startswith('field:'):
            name=key[6:]; self.focus=key; self.edit_text=self.field_value(name); self.notice='Edit '+name+'; Enter applies, Esc cancels'
        elif key=='apply': self.commit_field()
        elif key.startswith(('width:','bitop:','shiftop:')) or key in ('signed','usebag'): self.bits_activate(key)

    def menu_indices(self):
        return [i for i,lesson in enumerate(LESSONS) if lesson.group==self.menu_group]

    def paint(self,pos,erase=False):
        p=self.cell_at(pos)
        if p is None: return
        t='Erase' if erase else self.tool
        if t=='Wall':
            if p in (self.grid.start,self.grid.goal): return
            self.grid.walls.add(p); self.grid.weights.pop(p,None)
        elif t=='Swamp': self.grid.walls.discard(p); self.grid.weights[p]=5
        elif t=='Erase': self.grid.walls.discard(p); self.grid.weights.pop(p,None)
        elif t=='Start': self.grid.start=p; self.grid.walls.discard(p)
        elif t=='Goal': self.grid.goal=p; self.grid.walls.discard(p)
        self.results={}; self.prepare(); self.notice=f'{t} at {p}: history restarted'

    def handle(self,e):
        if e.type==pygame.QUIT: self.running=False
        elif e.type==pygame.VIDEORESIZE:
            self.screen=pygame.display.set_mode((max(1280,e.w),max(720,e.h)),pygame.RESIZABLE); self.draw()
        elif e.type==pygame.KEYDOWN:
            if self.about or self.help:
                if e.key==pygame.K_ESCAPE: self.about=False; self.help=False
                return
            if self.focus and self.focus.startswith('field:'):
                if e.key in (pygame.K_RETURN,pygame.K_KP_ENTER): self.commit_field()
                elif e.key==pygame.K_ESCAPE: self.focus=None; self.notice='Edit canceled'
                elif e.key==pygame.K_TAB:
                    current=self.focus; self.commit_field()
                    keys=list(self.buttons); self.focus=keys[(keys.index(current)+1)%len(keys)]
                    if self.focus.startswith('field:'): self.edit_text=self.field_value(self.focus[6:])
                elif e.key==pygame.K_BACKSPACE: self.edit_text=self.edit_text[:-1]
                elif e.unicode and e.unicode.isprintable() and len(self.edit_text)<100: self.edit_text+=e.unicode
                return
            mapping={pygame.K_SPACE:'play',pygame.K_RIGHT:'next',pygame.K_LEFT:'back',pygame.K_r:'home',pygame.K_END:'end',pygame.K_UP:'faster',pygame.K_DOWN:'slower'}
            if e.key==pygame.K_ESCAPE:
                if self.dropdown or self.help: self.dropdown=False; self.help=False; self.about=False
                else: self.running=False
            elif e.key==pygame.K_TAB:
                keys=(['lessons']+[k for k in self.buttons if k.startswith('group:') or k.startswith('lesson') and k!='lessons']) if self.dropdown else ['help'] if self.help else list(self.buttons)
                self.focus=keys[(keys.index(self.focus)+1)%len(keys)] if self.focus in keys else keys[0]
                self.notice='Focus: '+self.focus
                if self.focus.startswith('field:'): self.edit_text=self.field_value(self.focus[6:])
            elif e.key in (pygame.K_RETURN,pygame.K_KP_ENTER) and self.focus in self.buttons: self.activate(self.focus)
            elif e.key in mapping: self.activate(mapping[e.key])
        elif e.type==pygame.MOUSEWHEEL:
            if self.help or self.about: return
            if self.dropdown: self.menu_scroll=max(0,min(max(0,len(self.menu_indices())-6),self.menu_scroll-e.y))
            else: self.scroll=max(0,self.scroll-e.y*3)
        elif e.type==pygame.MOUSEBUTTONDOWN:
            self.pointer=e.pos
            if self.about or self.help:
                if not self.modal_rect.collidepoint(e.pos) or self.buttons['help' if self.help else 'about'].collidepoint(e.pos):
                    self.about=False; self.help=False
                return
            if e.button in (4,5): self.scroll=max(0,self.scroll+(3 if e.button==5 else -3)); return
            if e.button not in (1,3): return
            for key,r in reversed(list(self.buttons.items())):
                if self.dropdown and not (key.startswith('lesson') or key.startswith('group:')): continue
                if self.help and key!='help': continue
                if r.collidepoint(e.pos):
                    if key!='apply': self.focus=key
                    self.activate(key); return
            if self.dropdown: self.dropdown=False; return
            if self.help or self.about: return
            if self.main.collidepoint(e.pos) and self.lesson.module=='path': self.dragging=True; self.paint(e.pos,e.button==3)
        elif e.type==pygame.MOUSEBUTTONUP: self.dragging=False
        elif e.type==pygame.MOUSEMOTION:
            self.pointer=e.pos
            if self.dragging and not (self.about or self.help or self.dropdown): self.paint(e.pos,e.buttons[2] if len(e.buttons)>2 else False)

    def tick(self,dt):
        if self.playing:
            self.elapsed+=dt
            # Bound event work per frame to keep input responsive.
            count=min(24,int(self.elapsed*self.speed)); self.elapsed-=count/self.speed
            for _ in range(count):
                if not self.timeline.forward() or self.timeline.state.get('done'):
                    self.playing=False; self.record_result(); break
                if (self.fill_only and self.timeline.state.get('table_ready')) or (self.greedy_only and self.timeline.state.get('greedy_ready')):
                    self.playing=False; self.fill_only=False; self.greedy_only=False; break

    def run(self,frames=None,screenshot=None):
        count=0
        while self.running and (frames is None or count<frames):
            dt=self.clock.tick(60)/1000
            for e in pygame.event.get(): self.handle(e)
            self.tick(dt); self.draw(); count+=1
        if screenshot: save_png(self.screen,screenshot)
        pygame.quit()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--headless',action='store_true'); parser.add_argument('--frames',type=int)
    parser.add_argument('--screenshot'); parser.add_argument('--lesson',type=int,default=0)
    parser.add_argument('--finish',action='store_true')
    parser.add_argument('--theme',choices=sorted(theme.THEMES),help='arcade (default) or classic (original look)')
    args=parser.parse_args()
    if args.theme: use_theme(args.theme)
    if args.headless:
        os.environ['SDL_VIDEODRIVER']='dummy'; os.environ['SDL_AUDIODRIVER']='dummy'
    app=App(); app.load(args.lesson,initial=True)
    if args.finish: app.timeline.finish()
    app.run(args.frames,args.screenshot)

if __name__=='__main__': main()
