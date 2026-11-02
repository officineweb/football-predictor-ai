from scipy.stats import poisson

def score_matrix(lh, la, max_goals=10):
    return [[poisson.pmf(i, lh)*poisson.pmf(j, la) for j in range(max_goals+1)] for i in range(max_goals+1)]

def analyze(lh, la, max_goals=10):
    m=score_matrix(lh,la,max_goals); home=draw=away=over15=over25=over35=under25=btts=0.0; scores=[]
    for i,row in enumerate(m):
        for j,p in enumerate(row):
            if i>j: home+=p
            elif i==j: draw+=p
            else: away+=p
            if i+j>=2: over15+=p
            if i+j>=3: over25+=p
            if i+j>=4: over35+=p
            if i+j<=2: under25+=p
            if i and j: btts+=p
            scores.append((i,j,p))
    return {'home_win':home,'draw':draw,'away_win':away,'over_1_5':over15,'over_2_5':over25,'over_3_5':over35,'under_2_5':under25,'btts_yes':btts,'btts_no':1-btts,'top_scores':sorted(scores,key=lambda x:x[2],reverse=True)[:10],'model_coverage':sum(map(sum,m))}

def fair_odds(p): return None if p<=0 else 1/p

def estimate_lambdas(home_history, away_history, league_home=1.45, league_away=1.15):
    """History rows: {is_home: bool, goals_for:int, goals_against:int}. Basic transparent form model."""
    def avg(rows,key,default):
        vals=[r[key] for r in rows if r.get(key) is not None]
        return sum(vals)/len(vals) if vals else default
    hh=[r for r in home_history if r.get('is_home')]; ha=[r for r in home_history if not r.get('is_home')]
    ah=[r for r in away_history if r.get('is_home')]; aa=[r for r in away_history if not r.get('is_home')]
    # home attack vs away defence, and away attack vs home defence; fall back to all recent matches
    h_sc=avg(hh,'goals_for',avg(home_history,'goals_for',league_home)); a_con=avg(aa,'goals_against',avg(away_history,'goals_against',league_home))
    a_sc=avg(aa,'goals_for',avg(away_history,'goals_for',league_away)); h_con=avg(hh,'goals_against',avg(home_history,'goals_against',league_away))
    lh=max(.15,min(4.5,(h_sc+a_con)/2)); la=max(.15,min(4.5,(a_sc+h_con)/2))
    # Blend toward conservative league baseline to reduce small-sample extremes
    lh=.75*lh+.25*league_home; la=.75*la+.25*league_away
    return round(lh,3),round(la,3)
