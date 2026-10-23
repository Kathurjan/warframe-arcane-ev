from common import *
rows=[]
for slug,it in M.items():
    w=WIKI.get(it['name'].lower())
    if not w or not w['vosfor']: continue
    for rank in sorted({0,it['maxRank']}):
        a=ask(it,rank)
        if a is None: continue
        s=ingame(it,'sell',rank)
        depth=sum(o['quantity'] for o in s if o['platinum']==a)
        vos=w['vosfor']*copies(rank)
        v48,m48=stat(it,rank,'48hours')
        rows.append(dict(name=it['name'],slug=slug,rank=rank,buy=a,vos=vos,vpp=vos/a,c200=200*a/vos,depth=depth,vol48=v48,med48=m48,rarity=w['rarity']))
rows.sort(key=lambda r:-r['vpp'])
json.dump(rows,open('fodder.json','w'))
if __name__=='__main__':
    print(f"{'Arcane':28}{'rk':>3}{'buy':>6}{'vos':>6}{'v/p':>7}{'p/200':>7}{'qty@ask':>8}{'vol48':>6}{'med48':>6}")
    for r in rows[:40]:
        print(f"{r['name']:28}{r['rank']:>3}{r['buy']:>6}{r['vos']:>6}{r['vpp']:>7.2f}{r['c200']:>7.2f}{r['depth']:>8}{r['vol48']:>6}{str(r['med48']):>6}")
