from packs import *
from depth import walk
SHARE=0.25; TRADES_WEEK=210
w=walk(1000); c=w['c200']/200; buy_trades_per_pack=w['trades']/(w['vos']/200)
def week(pack, N):
    items=pack_items(pack)
    rev=0; vos_back=0; sales=0
    cand=[]
    for i in items:
        n=3*i['p']*N
        sale=i['real']*(0.75 if i['vol48']<5 else 1)
        if sale>=MIN_SALE and sale>i['vos']*c:
            cap=i['vol48']*3.5*SHARE
            s=min(n,cap); cand.append((sale,s)); rev+=s*sale; sales+=s; vos_back+=(n-s)*i['vos']
        else: vos_back+=n*i['vos']
    net_vos=N*200-vos_back
    trades=sales+buy_trades_per_pack*net_vos/200
    return rev-net_vos*c, trades, sales, rev, net_vos*c
if __name__=='__main__':
    print(f"c200={c*200:.2f}, buy trades per pack ~{buy_trades_per_pack:.3f}")
    print("| Pack | Best packs/week | Sales/week | Trades/week | Revenue | Vosfor cost | Profit/week |")
    for p in PACKS:
        best=(0,0)
        for N in range(0,3001,2):
            prof,tr,s,rev,cost=week(p,N)
            if tr<=TRADES_WEEK and prof>best[0]: best=(prof,N,tr,s,rev,cost)
        if best[0]<=0: print(f"| {p} | 0 | - | - | - | - | 0 (never profitable after trade/min-sale filter) |"); continue
        prof,N,tr,s,rev,cost=best
        print(f"| {p} | {N} | {s:.0f} | {tr:.0f} | {rev:.0f}p | {cost:.0f}p | {prof:+.0f}p |")
