"""Dynamic programming events: dependencies, decisions and traceback."""
from .engine import Event, event


def fibonacci(n, mode='both'):
    if not isinstance(n,int) or not 0 <= n <= 8:
        raise ValueError('Fibonacci n must be 0..8: larger trees exceed readable space')
    if mode not in ('naive','memo','both'):
        raise ValueError('Unknown Fibonacci mode')
    yield event('init','Ready: each node is one function call',kind='fib',n=n,nodes={},
                naive_calls=0,memo_calls=0,naive_result=None,memo_result=None,
                memo={},current=None,done=False,cells=0)
    serial=0
    for variant in (('naive','memo') if mode=='both' else (mode,)):
        cache={}; calls=0
        def visit(k,parent=None,side=0):
            nonlocal serial,calls
            node=serial; serial+=1; calls+=1
            hit=variant=='memo' and k in cache
            yield Event('call',f'{variant}: F({k})'+(' — cache hit' if hit else ''),{
                ('nodes',node):{'n':k,'parent':parent,'side':side,'variant':variant,'hit':hit,'value':None},
                (variant+'_calls',):calls,('current',):node})
            if hit:
                value=cache[k]
            elif k<2:
                value=k
            else:
                left=yield from visit(k-1,node,0)
                right=yield from visit(k-2,node,1)
                value=left+right
            changes={('nodes',node):{'n':k,'parent':parent,'side':side,'variant':variant,'hit':hit,'value':value},('current',):node}
            if variant=='memo' and not hit:
                cache[k]=value; changes[('memo',k)]=value
            yield Event('return',f'{variant}: return F({k})={value}',changes)
            return value
        result=yield from visit(n)
        yield event('result',f'{variant}: F({n})={result}, calls={calls}',**{variant+'_result':result})
    yield event('done','Finished: compare repeated subproblems and call counts',done=True)


def lcs(a,b):
    if not isinstance(a,str) or not isinstance(b,str) or len(a)>12 or len(b)>12:
        raise ValueError('LCS strings must each have at most 12 characters')
    rows,cols=len(a)+1,len(b)+1
    table=[[None]*cols for _ in range(rows)]
    for i in range(rows): table[i][0]=0
    for j in range(cols): table[0][j]=0
    yield event('init','Ready: zero row and column are empty prefixes',kind='lcs',a=a,b=b,table=table,
                current=None,dependencies=[],trace=[],cells=0,result=None,sequence='',done=False)
    count=0
    for i in range(1,rows):
        for j in range(1,cols):
            match=a[i-1]==b[j-1]
            deps=[(i-1,j-1)] if match else [(i-1,j),(i,j-1)]
            value=table[i-1][j-1]+1 if match else max(table[i-1][j],table[i][j-1])
            yield event('inspect',f'Compare {a[i-1]} / {b[j-1]}: '+('match; diagonal + 1' if match else 'max(up, left); ties go up'),current=(i,j),dependencies=deps)
            table[i][j]=value; count+=1
            yield event('cell',f'LCS[{i},{j}]={value}',table=[row[:] for row in table],cells=count)
    yield event('filled','Table complete: trace back to recover the subsequence',table_ready=True)
    i,j=len(a),len(b); trace=[]; letters=[]
    while i and j:
        trace.append((i,j))
        if a[i-1]==b[j-1]: letters.append(a[i-1]); i-=1; j-=1
        elif table[i-1][j]>=table[i][j-1]: i-=1
        else: j-=1
        yield event('trace','Trace back: matching diagonals form the subsequence',trace=trace[:],current=(i,j),sequence=''.join(reversed(letters)),dependencies=[])
    trace.append((i,j))
    yield event('done',f'LCS length {table[-1][-1]}: {"".join(reversed(letters)) or "(empty)"}',
                trace=trace,result=table[-1][-1],sequence=''.join(reversed(letters)),done=True)


def validate_items(items,capacity):
    if not isinstance(capacity,int) or not 0 <= capacity <= 30:
        raise ValueError('Capacity must be an integer 0..30')
    if len(items)>8 or any(not isinstance(w,int) or not isinstance(v,int) or w<1 or v<0 for w,v in items):
        raise ValueError('Use at most 8 items with positive integer weight and nonnegative value')


def knapsack(items,capacity):
    items=tuple(items); validate_items(items,capacity)
    table=[[None]*(capacity+1) for _ in range(len(items)+1)]
    table[0]=[0]*(capacity+1)
    yield event('init','Ready: row 0 uses no items',kind='knapsack',items=items,capacity=capacity,
                table=table,current=None,dependencies=[],trace=[],selected=[],cells=0,result=None,done=False)
    count=0
    for i,(weight,value) in enumerate(items,1):
        for c in range(capacity+1):
            deps=[(i-1,c)]; best=table[i-1][c]; take=False
            if weight<=c:
                deps.append((i-1,c-weight)); candidate=table[i-1][c-weight]+value
                if candidate>best: best=candidate; take=True
            yield event('inspect',f'Item {i} at capacity {c}: '+('take' if take else 'skip (ties skip)'),current=(i,c),dependencies=deps)
            table[i][c]=best; count+=1
            yield event('cell',f'DP[{i},{c}]={best}',table=[row[:] for row in table],cells=count)
    yield event('filled','Table complete: trace back to recover selected items',table_ready=True)
    c=capacity; trace=[]; selected=[]
    for i in range(len(items),0,-1):
        trace.append((i,c))
        if table[i][c]>table[i-1][c]: selected.append(i-1); c-=items[i-1][0]
        yield event('trace',f'Trace item {i}: '+('selected' if i-1 in selected else 'skipped'),
                    trace=trace[:],selected=sorted(selected),current=(i-1,c),dependencies=[])
    trace.append((0,c))
    yield event('done',f'Optimal value {table[-1][-1]}; items {[i+1 for i in sorted(selected)]}',
                result=table[-1][-1],trace=trace,selected=sorted(selected),done=True)
