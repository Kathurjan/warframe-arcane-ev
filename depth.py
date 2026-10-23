from common import *
def book():
    """Every in-game sell order for every dissolvable arcane at any rank, as Vosfor offers."""
    offers=[]
    for slug,it in M.items():
        w=WIKI.get(it['name'].lower())
        if not w or not w['vosfor']: continue
        for o in it['orders']:
            if o['type']=='sell' and o['visible'] and o['status']=='ingame' and o['platinum']>0:
                vos=w['vosfor']*copies(o['rank'])
                offers.append(dict(name=it['name'],rank=o['rank'],plat=o['platinum'],qty=o['quantity'],vos=vos,ppv=o['platinum']/vos))
    offers.sort(key=lambda x:x['ppv'])
    return offers

def walk(budget):
    spent=vos=trades=0; units=0; last=None
    for o in book():
        if spent+o['plat']>budget: continue
        n=min(o['qty'], int((budget-spent)//o['plat']))
        if n<=0: continue
        spent+=n*o['plat']; vos+=n*o['vos']; units+=n
        trades+= -(-n//6)   # max 6 item slots per trade, one seller per trade
        last=o
        if budget-spent<1: break
    return dict(budget=budget,spent=spent,vos=vos,units=units,trades=trades,c200=200*spent/vos,marg_c200=200*last['ppv'])

if __name__=='__main__':
    for b in (100,500,1000,5000,20000):
        print(walk(b))
    tot=sum(o['qty']*o['plat'] for o in book()); tv=sum(o['qty']*o['vos'] for o in book())
    print('whole in-game book: plat',tot,'vosfor',tv,'avg c200',200*tot/tv)
