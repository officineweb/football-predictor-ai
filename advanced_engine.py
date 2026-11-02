from math import exp, factorial
from statistics import mean
def poisson(k,lam):
    lam=max(.01,float(lam)); return exp(-lam)*lam**k/factorial(k)
def score_matrix(lh,la,cap=9):
    return {(h,a):poisson(h,lh)*poisson(a,la) for h in range(cap+1) for a in range(cap+1)}
def market_probs(lh,la):
    m=score_matrix(lh,la)
    p1=sum(v for (h,a),v in m.items() if h>a); px=sum(v for (h,a),v in m.items() if h==a); p2=sum(v for (h,a),v in m.items() if h<a)
    btts=sum(v for (h,a),v in m.items() if h>0 and a>0)
    o15=sum(v for (h,a),v in m.items() if h+a>=2); o25=sum(v for (h,a),v in m.items() if h+a>=3); o35=sum(v for (h,a),v in m.items() if h+a>=4)
    scores=sorted(m.items(),key=lambda x:x[1],reverse=True)[:8]
    return {"1":p1,"X":px,"2":p2,"Over 1.5":o15,"Over 2.5":o25,"Over 3.5":o35,"Under 2.5":1-o25,"Goal":btts,"No Goal":1-btts,"scores":[{"score":f"{h}-{a}","prob":p} for (h,a),p in scores]}
def shrink_avg(vals,prior,weight=3):
    xs=[float(x) for x in vals if x is not None];return (sum(xs)+prior*weight)/(len(xs)+weight)
def estimate_lambdas(h_for,h_against,a_for,a_against,league_home=1.45,league_away=1.15):
    hf=shrink_avg(h_for,league_home); hc=shrink_avg(h_against,league_away); af=shrink_avg(a_for,league_away); ac=shrink_avg(a_against,league_home)
    return max(.1,.55*hf+.45*ac),max(.1,.55*af+.45*hc)
def fair_odds(p):return round(1/p,3) if p>0 else None
def expected_value(p,odds):return p*float(odds)-1 if odds and float(odds)>1 else None
def accumulator(legs):
    p=1.;o=1.
    for x in legs:p*=float(x["prob"]);o*=float(x["odds"])
    return {"probability":p,"fair_odds":fair_odds(p),"combined_odds":o,"ev":p*o-1,"warning":"Assume indipendenza; mercati correlati invalidano la stima."}
