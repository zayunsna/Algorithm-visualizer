"""Greedy choices alongside exhaustive or DP optimal solutions."""
from fractions import Fraction
from .engine import Event, event
from .dp import knapsack, validate_items


def coins_compare(coins,amount):
    if not isinstance(amount,int) or not 0<=amount<=150:
        raise ValueError('Amount must be an integer 0..150')
    if not coins or len(coins)>12 or any(not isinstance(c,int) or c<1 for c in coins):
        raise ValueError('Use 1..12 positive integer denominations')
    coins=sorted(set(coins),reverse=True)
    yield event('init','Ready: greedy chooses the largest coin that fits',kind='coin',coins=coins,amount=amount,
                remaining=amount,greedy=[],optimal=[],greedy_count=None,optimal_count=None,
                dp=[0]+[None]*amount,current=None,dependencies=[],best_coin=None,phase='greedy',done=False,cells=0)
    remaining=amount; chosen=[]
    for coin in coins:
        while remaining>=coin:
            remaining-=coin; chosen.append(coin)
            yield event('choose',f'Greedy: take {coin}; remaining {remaining}',current=coin,greedy=chosen[:],remaining=remaining)
    greedy_count=len(chosen) if remaining==0 else None
    yield event('greedy_done','Greedy complete' if remaining==0 else 'Greedy stuck: no coin fits the remainder',greedy_count=greedy_count,greedy_ready=True)
    dp=[0]+[None]*amount; previous={}
    for value in range(1,amount+1):
        candidates=[(dp[value-c]+1,-c,c) for c in coins if c<=value and dp[value-c] is not None]
        deps=[value-c for c in coins if c<=value]
        yield event('inspect',f'dp[{value}] = 1 + min(reachable predecessors)',current=value,
                    dependencies=deps,best_coin=None,phase='optimal')
        coin=None
        if candidates:
            best,_,coin=min(candidates); dp[value]=best; previous[value]=coin
        yield event('cell',f'dp[{value}] = dp[{value-coin}] + 1 = {dp[value]}' if coin is not None else f'Amount {value} is unreachable',
                    dp=dp[:],current=value,phase='optimal',cells=value,best_coin=coin)
    optimal=[]; value=amount
    while value and value in previous:
        coin=previous[value]; optimal.append(coin); value-=coin
        yield event('trace',f'Optimal: take {coin}; back to amount {value}',optimal=optimal[:],current=value,dependencies=[],best_coin=None)
    optimal_count=dp[amount]
    failed=optimal_count is not None and (greedy_count is None or greedy_count>optimal_count)
    message='Greedy fails on this input' if failed else 'No exact solution' if optimal_count is None else 'Greedy matches the optimum on this input'
    yield event('done',message,optimal_count=optimal_count,failed=failed,done=True,current=None)


def activity_compare(activities,rule='finish'):
    if len(activities)>10 or any(len(p)!=2 or not all(isinstance(x,int) for x in p) or p[0]<0 or p[0]>=p[1] or p[1]>100 for p in activities):
        raise ValueError('Use at most 10 intervals, 0 <= start < end <= 100')
    if rule not in ('finish','start','duration'): raise ValueError('Unknown activity rule')
    activities=tuple(activities)
    key={'finish':lambda i:(activities[i][1],i),'start':lambda i:(activities[i][0],i),
         'duration':lambda i:(activities[i][1]-activities[i][0],i)}[rule]
    order=sorted(range(len(activities)),key=key)
    yield event('init',f'Ready: choose earliest {rule}; ties use input order',kind='activity',activities=activities,
                rule=rule,order=order,current=None,selected=[],rejected={},optimal=[],greedy_count=None,
                optimal_count=None,phase='greedy',subsets=0,done=False)
    selected=[]; rejected={}
    for index,i in enumerate(order):
        a,b=activities[i]
        conflict=next((j for j in selected if a<activities[j][1] and activities[j][0]<b),None)
        if conflict is None: selected.append(i); message=f'Take meeting {i+1}: no overlap'
        else: rejected[i]=f'overlaps meeting {conflict+1}'; message=f'Reject meeting {i+1}: {rejected[i]}'
        yield event('choose',message,current=i,order=order[index+1:],selected=selected[:],rejected=rejected.copy())
    yield event('greedy_done',f'Greedy selected {len(selected)} meetings',greedy_count=len(selected),greedy_ready=True)
    best=[]
    for mask in range(1<<len(activities)):
        subset=[i for i in range(len(activities)) if mask>>i&1]
        valid=all(activities[i][1]<=activities[j][0] or activities[j][1]<=activities[i][0]
                  for k,i in enumerate(subset) for j in subset[k+1:])
        if valid and len(subset)>len(best): best=subset
        yield event('subset',f'Optimal reference: subset {mask} is '+('compatible' if valid else 'overlapping'),
                    phase='optimal',optimal=best[:],subsets=mask+1)
    failed=len(selected)<len(best)
    yield event('done','Greedy fails on this input' if failed else 'Greedy matches the optimum on this input',
                optimal_count=len(best),failed=failed,done=True,current=None)


def bag_compare(items,capacity):
    items=tuple(items); validate_items(items,capacity)
    order=sorted(range(len(items)),key=lambda i:(-Fraction(items[i][1],items[i][0]),i))
    yield event('init','Ready: choose highest value / weight; ties use input order',kind='bag',items=items,
                capacity=capacity,order=order,current=None,fractional={},whole=[],fractional_value=Fraction(0),
                greedy_value=0,optimal_value=None,remaining=capacity,phase='fractional',dp={},done=False)
    remaining=Fraction(capacity); fractions={}; fractional_value=Fraction(0)
    for index,i in enumerate(order):
        w,v=items[i]; fraction=min(Fraction(1),remaining/w)
        if fraction:
            fractions[i]=fraction; remaining-=w*fraction; fractional_value+=v*fraction
        yield event('choose',f'Fractional: item {i+1}, ratio {Fraction(v,w)}, take {fraction}',
                    current=i,fractional=fractions.copy(),fractional_value=fractional_value,
                    remaining=remaining,order=order[index+1:])
    remaining=capacity; whole=[]; greedy_value=0
    for index,i in enumerate(order):
        w,v=items[i]; fits=w<=remaining
        if fits: whole.append(i); remaining-=w; greedy_value+=v
        yield event('choose',f'0/1 greedy: '+('take' if fits else 'skip')+f' item {i+1}',phase='whole',current=i,
                    whole=whole[:],greedy_value=greedy_value,remaining=remaining,order=order[index+1:])
    yield event('greedy_done','Greedy comparison complete: now compute 0/1 DP',greedy_ready=True)
    optimal=None
    for e in knapsack(items,capacity):
        changes={('dp',)+path:value for path,value in e.changes.items()}
        changes[('phase',)]='dp'
        if ('result',) in e.changes and e.changes[('result',)] is not None: optimal=e.changes[('result',)]
        yield Event('dp_'+e.action,e.message,changes)
    yield event('done',f'Fractional value {fractional_value}; 0/1 greedy {greedy_value}; DP {optimal}',
                optimal_value=optimal,failed=greedy_value<optimal,done=True)
