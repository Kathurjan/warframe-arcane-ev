from packs import *
from depth import walk
import fodder
F=json.load(open('fodder.json'))
W1000=walk(1000); C=W1000['c200']/200
print('DATA', market['fetched_utc_start'], market['fetched_utc_end'])
print(f"c200 used = {W1000['c200']:.2f}p (avg cost of 200 Vosfor when spending 1000p through the order book)\n")

print("## Fodder top 20")
print("| Arcane | Rank | Buy Price | Vosfor Received | Vosfor/Plat | Cost per 200 Vosfor | Qty at price | Sold 48h |")
print("|---|---:|---:|---:|---:|---:|---:|---:|")
for r in F[:20]:
    print(f"| {r['name']} | {r['rank']} | {r['buy']}p | {r['vos']} | {r['vpp']:.2f} | {r['c200']:.2f}p | {r['depth']} | {r['vol48']} |")

def table(mode):
    print(f"\n## Packs mode={mode}")
    print("| Pack | Cost 200V | Sale EV (sell all) | Recycled Vosfor Value | Adjusted EV | Profit | ROI | Break-even 200V | P(profit) | SD/pack | p50/p90/p99 value | Vosfor back/pack |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    res=[]
    for p in PACKS:
        r=analyze(p,C,mode); s=analyze(p,C,'sell'); be=breakeven(p,mode)
        res.append(r)
        print(f"| {p} | {r['c200']:.2f} | {s['ev_pack']:.2f} | {r['vos_back_plat']:.2f} | {r['ev_pack']:.2f} | {r['profit']:+.2f} | {r['roi']:+.0f}% | {be:.2f} | {r['pprofit']*100:.1f}% | {r['sd_pack']:.2f} | {r['pct'][0.5]:.1f}/{r['pct'][0.9]:.1f}/{r['pct'][0.99]:.1f} | {r['vos_back']:.1f} |")
    return res
th=table('recycle'); re_=table('real')

print("\n## Per-arcane EV detail (recycle mode): sale EV per arcane, top item")
for r in th:
    print(r['pack'], f"EV/arcane={r['ev_arcane']:.3f}", 'top', r['top'], r['top_val'], f"P(>=1 top in pack)={r['p_top']*100:.2f}%")

print("\n## Investment levels")
for b in (100,500,1000,5000):
    w=walk(b); c=w['c200']/200
    print(f"\n### {b}p -> {w['vos']} Vosfor, avg {w['c200']:.2f}p/200, {w['trades']} buy-trades")
    for mode in ('recycle','real'):
        for p in PACKS:
            r=analyze(p,c,mode)
            R=r['vos_back']; net=200-R
            packs_n=w['vos']/net
            sales=0; 
            for i,v in zip(r['items'],r['vals']):
                if slot_value(i,c,mode)[1]=='sell': sales+=3*i['p']*packs_n
            profit=packs_n*r['sale_pack']-w['spent']
            print(f"  {mode:7} {p:10} packs={packs_n:7.1f} (first-pass {w['vos']/200:.1f}) revenue={packs_n*r['sale_pack']:8.1f} profit={profit:+8.1f} sales-needed={sales:6.0f} credits={packs_n*50000/1e6:.1f}M")
