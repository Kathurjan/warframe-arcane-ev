from common import *
import itertools, sys
from collections import defaultdict

PACKS = {  # from wiki Loid (Original) page, per-slot rarity chances; 3 independent slots
 "Cavia": [(0.45,["Melee Fortification","Melee Retaliation"]),
           (0.50,["Arcane Battery","Arcane Ice Storm","Melee Afflictions","Melee Animosity","Melee Exposure","Melee Influence","Melee Vortex","Secondary Fortifier","Secondary Surge"]),
           (0.05,["Melee Crescendo","Melee Duplicate"])],
 "Duviri": [(0.45,["Arcane Intention","Magus Aggress"]),
            (0.50,["Arcane Power Ramp","Primary Blight","Primary Exhilarate","Primary Obstruct","Shotgun Vendetta","Akimbo Slip Shot","Secondary Outburst"]),
            (0.05,["Arcane Reaper","Longbow Sharpshot","Secondary Shiver"])],
 "Eidolon": [(0.40,["Arcane Consequence","Arcane Ice","Arcane Momentum","Arcane Nullifier","Arcane Tempo","Arcane Warmth"]),
             (0.35,["Arcane Acceleration","Arcane Agility","Arcane Awakening","Arcane Deflection","Arcane Eruption","Arcane Guardian","Arcane Healing","Arcane Phantasm","Arcane Resistance","Arcane Strike","Arcane Trickery","Arcane Velocity","Arcane Victory"]),
             (0.20,["Arcane Aegis","Arcane Arachne","Arcane Avenger","Arcane Fury","Arcane Precision","Arcane Pulse","Arcane Rage","Arcane Ultimatum"]),
             (0.05,["Arcane Barrier","Arcane Energize","Arcane Grace"])],
 "Holdfasts": [(1.0,["Arcane Blessing","Arcane Rise","Molt Augmented","Molt Efficiency","Molt Reconstruct","Molt Vigor","Fractalized Reset","Primary Frostbite","Cascadia Accuracy","Cascadia Empowered","Cascadia Flare","Cascadia Overcharge","Conjunction Voltage","Emergence Dissipate","Emergence Renewed","Emergence Savior","Eternal Eradicate","Eternal Logistics","Eternal Onslaught"])],
 "Höllvania": [(0.95,["Arcane Bellicose","Arcane Camisado","Arcane Crepuscular","Arcane Impetus","Arcane Truculence","Melee Doughty","Primary Crux","Secondary Enervate"]),
               (0.05,["Arcane Escapist","Arcane Hot Shot","Arcane Universal Fallout"])],
 "Necralisk": [(1.0,["Arcane Double Back","Arcane Steadfast","Theorem Contagion","Theorem Demulcent","Theorem Infection","Primary Plated Round","Secondary Encumber","Secondary Kinship","Residual Boils","Residual Malodor","Residual Shock","Residual Viremia"])],
 "Ostron": [(0.60,["Magus Husk","Magus Vigor","Virtuos Null","Virtuos Tempo"]),
            (0.30,["Exodia Triumph","Exodia Valor","Magus Cadence","Magus Cloud","Magus Replenish","Virtuos Fury","Virtuos Strike"]),
            (0.10,["Exodia Brave","Exodia Force","Exodia Hunt","Exodia Might","Magus Elevate","Magus Nourish","Virtuos Ghost","Virtuos Shadow"])],
 "Solaris": [(0.60,["Magus Accelerant","Magus Anomaly","Magus Drive","Magus Firewall","Magus Overload","Virtuos Spike","Virtuos Surge"]),
             (0.30,["Magus Glitch","Magus Repair","Virtuos Forge","Virtuos Trojan"]),
             (0.10,["Pax Bolt","Pax Charge","Pax Seeker","Pax Soar","Magus Destruct","Magus Lockdown","Magus Melt","Magus Revert"])],
 "Steel": [(1.0,["Arcane Blade Charger","Arcane Bodyguard","Arcane Pistoleer","Arcane Primary Charger","Arcane Tanker","Primary Deadhead","Primary Dexterity","Primary Merciless","Secondary Deadhead","Secondary Dexterity","Secondary Merciless"])],
}

def pack_items(pack):
    out=[]
    for p,names in PACKS[pack]:
        for n in names:
            s=by_name(n); assert s, n
            w=WIKI[n.lower()]
            out.append(dict(name=n, slug=s, p=p/len(names), grp=p, vos=w['vosfor'], rarity=w['rarity'], **price_info(s,0)))
    assert abs(sum(i['p'] for i in out)-1)<1e-9
    return out

def slot_value(i, c, mode):
    """Value of one pulled arcane. c = plat per Vosfor.
    mode 'sell'   : sell everything at realistic price
    mode 'recycle': best of (sell at realistic) vs (dissolve -> Vosfor worth c each)
    mode 'real'   : like recycle, but a sale must be >= MIN_SALE plat to be worth a trade,
                    and low-volume items (<5 sold/48h) are haircut 25%"""
    if mode=='sell': return i['real'], 'sell'
    sale=i['real']
    if mode=='real':
        if i['vol48']<5: sale*=0.75
        if sale<MIN_SALE: sale=0
    rec=i['vos']*c
    return (sale,'sell') if sale>=rec else (rec,'dissolve')

MIN_SALE=5

def analyze(pack, c, mode='recycle'):
    items=pack_items(pack)
    vals=[slot_value(i,c,mode)[0] for i in items]
    ps=[i['p'] for i in items]
    ev1=sum(p*v for p,v in zip(ps,vals))
    sale1=sum(p*v for p,v,i in zip(ps,vals,items) if slot_value(i,c,mode)[1]=='sell')
    vos1=sum(p*i['vos'] for p,i in zip(ps,items) if slot_value(i,c,mode)[1]=='dissolve')
    var1=sum(p*(v-ev1)**2 for p,v in zip(ps,vals))
    cost=200*c
    # exact distribution of 3-slot pack value
    dist=defaultdict(float)
    for a,b,d in itertools.product(range(len(items)),repeat=3):
        dist[round(vals[a]+vals[b]+vals[d],4)]+=ps[a]*ps[b]*ps[d]
    pprofit=sum(p for v,p in dist.items() if v>cost+1e-9)
    # percentiles
    acc=0; pct={}
    for v in sorted(dist):
        acc+=dist[v]
        for q in (0.5,0.9,0.99):
            if q not in pct and acc>=q: pct[q]=v
    top=max(items,key=lambda i:i['real'])
    p_top_pack=1-(1-top['p'])**3
    return dict(pack=pack,c200=cost,ev_arcane=ev1,ev_pack=3*ev1,sale_pack=3*sale1,vos_back=3*vos1,
                vos_back_plat=3*vos1*c,profit=3*ev1-cost,roi=(3*ev1-cost)/cost*100,
                sd_pack=(3*var1)**0.5,pprofit=pprofit,pct=pct,top=top['name'],top_val=top['real'],p_top=p_top_pack,
                breakeven_c200=None, items=items, vals=vals)

def breakeven(pack, mode='recycle'):
    """Cost of 200 Vosfor at which EV(pack)=cost. With recycling, EV depends on c, so bisect."""
    lo,hi=0.001,2000.0
    for _ in range(80):
        mid=(lo+hi)/2
        r=analyze(pack, mid/200, mode)
        if r['ev_pack']>mid: lo=mid
        else: hi=mid
    return lo
