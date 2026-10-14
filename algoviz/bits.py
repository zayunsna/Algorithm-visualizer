"""Finite-width bit lessons. No renderer or pygame dependency."""
from collections import Counter
from .engine import event
from .dp import validate_items

WIDTHS=(4,8,16)


def mask_for(width):
    if width not in WIDTHS: raise ValueError('Width must be 4, 8 or 16')
    return (1<<width)-1


def unsigned(value,width):
    return value & mask_for(width)


def signed(value,width):
    word=unsigned(value,width)
    return word-(1<<width) if word & (1<<(width-1)) else word


def logic_result(a,b,width,op):
    a,b=unsigned(a,width),unsigned(b,width)
    if op=='AND': result=a&b
    elif op=='OR': result=a|b
    elif op=='XOR': result=a^b
    elif op=='NOT': result=~a
    else: raise ValueError('Unknown logic operation')
    return unsigned(result,width)


def shift_result(a,width,amount,op):
    if not isinstance(amount,int) or not 0<=amount<=width:
        raise ValueError('Shift amount must be 0..W')
    word=unsigned(a,width)
    if op=='LEFT': result=word<<amount
    elif op=='LOGICAL': result=word>>amount
    elif op=='ARITHMETIC': result=signed(word,width)>>amount
    else: raise ValueError('Unknown shift operation')
    return unsigned(result,width)


def negate_result(a,width):
    return unsigned(~unsigned(a,width)+1,width)


def row(label,value): return {'label':label,'value':value}


def begin(mode,width,a=0,b=0,**values):
    mask=mask_for(width)
    return event('init','Ready: inspect one bit at a time',kind='bits',mode=mode,width=width,
                 a=unsigned(a,width),b=unsigned(b,width),raw_a=a,raw_b=b,mask=mask,
                 rows=[row('A' if mode=='logic' else 'X',unsigned(a,width))]+([row('B',unsigned(b,width))] if mode=='logic' else []),current_bit=None,flipped=[],filled=[],discarded=[],truth=None,op=None,
                 result=None,iterations=0,bits_computed=0,carry=0,done=False,**values)


def bit_steps(a,b,width,op,labels=('A','B','Result')):
    a,b=unsigned(a,width),unsigned(b,width)
    out=[None]*width
    for i in range(width):
        k=width-1-i; aa=(a>>k)&1; bb=(b>>k)&1
        digit=(aa and bb) if op=='AND' else (aa or bb) if op=='OR' else (aa!=bb) if op=='XOR' else (1-aa)
        out[i]=int(digit)
        rows=[row(labels[0],a)]
        if op!='NOT': rows.append(row(labels[1],b))
        rows.append(row(labels[2],out[:]))
        yield event('bit',f'{op} at bit {k}: {aa}'+('' if op=='NOT' else f', {bb}')+f' -> {int(digit)}',
                    rows=rows,current_bit=i,bits_computed=i+1,truth=(aa,None if op=='NOT' else bb,int(digit)),op=op)
    return logic_result(a,b,width,op)


def logic(a,b,width=8,op='AND'):
    mask_for(width); logic_result(a,b,width,op)
    yield begin('logic',width,a,b)
    result=yield from bit_steps(a,b,width,op)
    raw={'AND':lambda:a&b,'OR':lambda:a|b,'XOR':lambda:a^b,'NOT':lambda:~a}[op]()
    yield event('done',f'{op}: W-bit result {result}',result=result,python_result=raw,done=True)


def shifts(a,width=8,amount=2,op='LOGICAL'):
    shift_result(a,width,amount,op)
    word=unsigned(a,width); logical=arithmetic=word; discarded=[]
    yield begin('shift',width,a,rows_input=word,shift_op=op,shift_amount=amount)
    labels=('Source','Left <<') if op=='LEFT' else ('Source','Logical >>','Arithmetic >>')
    yield event('setup','Both right shifts start with the same W-bit word',rows=[row(label,word) for label in labels])
    for step in range(1,amount+1):
        if op=='LEFT':
            discarded.append((logical>>(width-1))&1)
            logical=unsigned(logical<<1,width)
            rows=[row('Source',word),row('Left <<',logical)]
            filled=list(range(width-step,width))
        else:
            discarded.append(logical&1)
            logical=unsigned(logical>>1,width)
            arithmetic=unsigned(signed(arithmetic,width)>>1,width)
            rows=[row('Source',word),row('Logical >>',logical),row('Arithmetic >>',arithmetic)]
            filled=list(range(step))
        yield event('shift',f'Shift {step}/{amount}: discard {discarded[-1]}; '+('replicate sign in arithmetic row' if op!='LEFT' else 'fill with zero'),
                    rows=rows,discarded=discarded[:],filled=filled,iterations=step,
                    logical=logical,arithmetic=arithmetic,current_bit=None)
    result=arithmetic if op=='ARITHMETIC' else logical
    raw=a<<amount if op=='LEFT' else a>>amount
    yield event('done',f'{op} shift by {amount}: W-bit result {result}',result=result,logical=logical,
                arithmetic=arithmetic,python_result=raw,done=True)


def complement(a,width=8,finish=True):
    word=unsigned(a,width)
    yield begin('negate',width,a)
    inverse=yield from bit_steps(word,0,width,'NOT',('X','', '~X (masked)'))
    digits=[None]*width; carry=1
    for i in range(width-1,-1,-1):
        bit=(inverse>>(width-1-i))&1
        total=bit+carry; digits[i]=total%2; carry=total//2
        yield event('add',f'Add one at bit {width-1-i}: sum {total}; carry {carry}',
                    rows=[row('X',word),row('~X',inverse),row('~X + 1',digits[:])],
                    op=None,truth=None,current_bit=i,carry=carry,bits_computed=width-i)
    result=negate_result(word,width)
    minimum=word==(1<<(width-1))
    yield event('done' if finish else 'negated','Sign minimum wraps to itself' if minimum else 'Negation is complement plus one, masked to W bits',
                result=result,overflow=minimum,discarded_carry=carry,python_result=-a,done=finish)


def isolate(a,width=8):
    yield from complement(a,width,finish=False)
    word=unsigned(a,width); negative=negate_result(word,width)
    yield event('and_ready','AND with -x keeps only the lowest set bit',mode='isolate',flipped=[])
    result=yield from bit_steps(word,negative,width,'AND',('X','-X (masked)','X & -X'))
    yield event('done',f'Lowest set bit: {result}',result=result,python_result=a&(-a),done=True)


def clear_lowest(a,width=8,repeat=True,power=False):
    word=unsigned(a,width); initial=word; iterations=0
    yield begin('power' if power else 'popcount' if repeat else 'clear',width,a)
    if not word and not power:
        yield event('done','Zero has no set bit to clear',rows=[row('X',0)],result=0,iterations=0,popcount=0,done=True)
        return
    while word or power:
        minus=unsigned(word-1,width)
        flipped=[i for i in range(width) if ((word^minus)>>(width-1-i))&1]
        yield event('subtract','x - 1 flips the lowest 1 and all trailing zeros',rows=[row('X',word),row('X - 1',minus)],
                    flipped=flipped,op=None,truth=None,current_bit=None,remaining=word)
        result=yield from bit_steps(word,minus,width,'AND',('X','X - 1','X & (X - 1)'))
        iterations+=int(bool(word))
        yield event('clear',f'Clear one set bit: {word} -> {result}',result=result,iterations=iterations,
                    remaining=result,current_bit=None,truth=None)
        word=result
        if power or not repeat: break
    if power:
        yes=initial!=0 and word==0
        yield event('done',f'Unsigned word power of two: {yes} (zero guard: {initial!=0})',
                    result=word,is_power=yes,nonzero=initial!=0,done=True)
    else:
        yield event('done',f'{iterations} iteration(s): '+('one per original set bit' if repeat else 'one lowest bit cleared'),
                    result=word,popcount=iterations if repeat else None,done=True)


def unique_xor(values,width=8):
    mask_for(width)
    if not 1<=len(values)<=12 or any(not isinstance(v,int) for v in values): raise ValueError('Use 1..12 integers')
    words=[unsigned(v,width) for v in values]; counts=Counter(words)
    if list(counts.values()).count(1)!=1 or any(n not in (1,2) for n in counts.values()):
        raise ValueError('Masked words must occur twice, except one singleton')
    yield begin('unique',width,values=words,item_index=None,accumulator=0)
    accumulator=0
    for index,word in enumerate(words):
        yield event('item',f'Accumulate item {index+1}: {word}',item_index=index)
        accumulator=yield from bit_steps(accumulator,word,width,'XOR',('Accumulator','Item','Next XOR'))
        yield event('accumulate',f'Accumulator is now {accumulator}',accumulator=accumulator,iterations=index+1,result=accumulator)
    yield event('done',f'Unpaired word: {accumulator}; a XOR a = 0, a XOR 0 = a',result=accumulator,done=True)


def subsets(items,capacity=10,width=8):
    items=tuple(items); validate_items(items,capacity); mask_for(width)
    if len(items)>width: raise ValueError('The number of items must fit in W bits')
    yield begin('subset',width,items=items,capacity=capacity,selected=[],subsets=0,best=0,best_selected=[],weight=0,value=0,feasible=True)
    best=0; best_selected=[]
    for mask in range(1<<len(items)):
        selected=[i for i in range(len(items)) if (mask>>i)&1]
        weight=sum(items[i][0] for i in selected); value=sum(items[i][1] for i in selected)
        feasible=weight<=capacity
        if feasible and value>best: best=value; best_selected=selected[:]
        yield event('subset',f'Mask {mask}: '+('within capacity' if feasible else 'over capacity'),
                    rows=[row('Subset mask',unsigned(mask,width))],selected=selected,subsets=mask+1,
                    weight=weight,value=value,feasible=feasible,best=best,best_selected=best_selected[:],result=unsigned(mask,width))
    yield event('done',f'Enumerated {1<<len(items)} subsets; best 0/1 value {best}',done=True)
