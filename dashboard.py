import os, datetime, itertools, math
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from predictor import analyze, fair_odds, estimate_lambdas
from provider_api_football import api_get, fixtures as api_fixtures
load_dotenv()
st.set_page_config(page_title='Football Predictor AI',page_icon='⚽',layout='wide')
st.title('⚽ Football Predictor AI')
st.caption('v0.4 PRO • Scanner, analisi probabilistica, shortlist mercati e builder — stime, non garanzie')
with st.sidebar:
    st.header('Menu'); page=st.radio('Sezione',['Scanner partite','Analisi singola','Costruttore schedina','Storico / limiti'])
    st.divider(); st.caption('API-Football: '+('key configurata' if os.getenv('API_FOOTBALL_KEY') else 'key mancante'))

def history(team_id, season, n=10):
    data=api_get('fixtures',{'team':team_id,'last':n,'season':season,'status':'FT'}).get('response',[])
    out=[]
    for x in data:
        t=x.get('teams',{}); g=x.get('goals',{}); ishome=t.get('home',{}).get('id')==team_id
        gf=g.get('home') if ishome else g.get('away'); ga=g.get('away') if ishome else g.get('home')
        if gf is not None and ga is not None: out.append({'is_home':ishome,'goals_for':gf,'goals_against':ga})
    return out

def fixture_model(x, season):
    f=x.get('fixture',{}); t=x.get('teams',{}); league=x.get('league',{}); gh=x.get('goals',{})
    hid=t.get('home',{}).get('id'); aid=t.get('away',{}).get('id')
    hhist=history(hid,season,10); ahist=history(aid,season,10)
    lh,la=estimate_lambdas(hhist,ahist)
    r=analyze(lh,la); r.update({'fixture_id':f.get('id'),'date':f.get('date'),'league':league.get('name'),'home':t.get('home',{}).get('name'),'away':t.get('away',{}).get('name'),'lh':lh,'la':la,'status':f.get('status',{}).get('short'),'goals_home':gh.get('home'),'goals_away':gh.get('away')})
    return r

def picks_for(r):
    return [('1',r['home_win']),('X',r['draw']),('2',r['away_win']),('Over 1.5',r['over_1_5']),('Over 2.5',r['over_2_5']),('Under 2.5',r['under_2_5']),('Goal',r['btts_yes']),('No Goal',r['btts_no'])]

if page=='Scanner partite':
    st.subheader('Scanner automatico')
    c1,c2,c3=st.columns(3); day=c1.date_input('Data',datetime.date.today()); season=c2.number_input('Stagione',2010,2035,day.year); league=c3.number_input('ID campionato (0=tutti)',0,99999,0)
    n=st.slider('Ultime partite per squadra',5,20,10); threshold=st.slider('Probabilità minima selezione (%)',50,90,65)/100
    if st.button('ANALIZZA PARTITE',type='primary'):
        if not os.getenv('API_FOOTBALL_KEY'): st.error('Inserisci API_FOOTBALL_KEY nel file .env e riavvia.')
        else:
            try:
                raw=api_fixtures(date=day.isoformat(),league=int(league) or None,season=int(season) if league else None).get('response',[])
                if not raw: st.warning('Nessuna partita trovata per questa data/filtri.')
                results=[]; prog=st.progress(0); status=st.empty()
                for i,x in enumerate(raw):
                    status.write(f"Analisi {i+1}/{len(raw)}: {x.get('teams',{}).get('home',{}).get('name')} - {x.get('teams',{}).get('away',{}).get('name')}")
                    try: results.append(fixture_model(x,int(season)))
                    except Exception as e: st.warning(f"Partita saltata: {e}")
                    prog.progress((i+1)/max(1,len(raw)))
                st.session_state.scan=results; st.session_state.scan_threshold=threshold; status.empty(); st.success(f'Analizzate {len(results)} partite.')
            except Exception as e: st.error(str(e))
    if 'scan' in st.session_state:
        rows=[]; candidates=[]
        for r in st.session_state.scan:
            best=max(picks_for(r),key=lambda z:z[1]); rows.append({'Campionato':r['league'],'Partita':f"{r['home']} - {r['away']}",'λ casa':r['lh'],'λ ospite':r['la'],'1':f"{r['home_win']:.1%}",'X':f"{r['draw']:.1%}",'2':f"{r['away_win']:.1%}",'Over 2.5':f"{r['over_2_5']:.1%}",'Goal':f"{r['btts_yes']:.1%}",'Top score':f"{r['top_scores'][0][0]}-{r['top_scores'][0][1]}",'Pick migliore':best[0],'Prob pick':best[1]})
            for market,p in picks_for(r):
                if p>=st.session_state.scan_threshold and market not in ('X',): candidates.append({'Partita':f"{r['home']} - {r['away']}",'Mercato':market,'Probabilità modello':p,'Quota fair':fair_odds(p),'fixture_id':r['fixture_id']})
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
        st.subheader('Shortlist mercati sopra soglia (non sono garanzie)')
        st.caption('Le quote fair sono il reciproco della probabilità stimata; non sono quote bookmaker e non includono margini.')
        if candidates: st.dataframe(pd.DataFrame(candidates).drop(columns=['fixture_id']),use_container_width=True,hide_index=True)
        else: st.info('Nessun mercato supera la soglia impostata. Non abbassarla solo per trovare picks.')
        st.download_button('Esporta analisi CSV',pd.DataFrame(rows).to_csv(index=False).encode(),file_name='football_predictor_scan.csv')
        if candidates:
            cand_df=pd.DataFrame(candidates)
            st.download_button('Esporta shortlist CSV',cand_df.to_csv(index=False).encode(),file_name='football_predictor_shortlist.csv')
            st.subheader('Builder rapido da shortlist')
            st.info('Per evitare combinazioni correlate, seleziona con prudenza. Il builder manuale non corregge la dipendenza tra mercati della stessa partita.')
elif page=='Analisi singola':
    st.subheader('Analisi Poisson manuale')
    a,b=st.columns(2); home=a.text_input('Casa','Inter'); away=b.text_input('Ospite','Juventus')
    a,b=st.columns(2); lh=a.slider('Expected goals casa λ',0.1,4.5,1.55,.05); la=b.slider('Expected goals ospite λ',0.1,4.5,1.05,.05)
    r=analyze(lh,la); st.write(f'Modello: {home} {lh} — {away} {la}')
    cols=st.columns(3)
    for col,(name,key) in zip(cols,[('1','home_win'),('X','draw'),('2','away_win')]): col.metric(name,f"{r[key]:.1%}",f"Quota fair {fair_odds(r[key]):.2f}")
    cols=st.columns(6)
    for col,(name,p) in zip(cols,[('Over 1.5',r['over_1_5']),('Over 2.5',r['over_2_5']),('Over 3.5',r['over_3_5']),('Under 2.5',r['under_2_5']),('Goal',r['btts_yes']),('No Goal',r['btts_no'])]): col.metric(name,f'{p:.1%}',f'Fair {fair_odds(p):.2f}')
    st.subheader('Correct score più probabili'); st.dataframe(pd.DataFrame([{'Risultato':f'{i}-{j}','Probabilità':f'{p:.2%}'} for i,j,p in r['top_scores']]),hide_index=True,use_container_width=True)
elif page=='Costruttore schedina':
    st.subheader('Builder multipla (calcolo matematico)'); st.warning('La probabilità combinata moltiplica le probabilità selezionate e assume indipendenza. Eventi correlati e margini bookmaker non sono inclusi.')
    n=st.number_input('Numero selezioni',1,12,3); probs=[]; labels=[]
    for i in range(int(n)):
        c1,c2=st.columns([3,1]); labels.append(c1.text_input(f'Evento {i+1}',f'Pick {i+1}',key=f'label{i}')); probs.append(c2.number_input('Probabilità %',1.,99.,65.,key=f'prob{i}')/100)
    stake=st.number_input('Importo (€)',.5,1000.,5.); p=math.prod(probs); fair=1/p; offered=st.number_input('Quota totale bookmaker (facoltativa)',0.,100000.,0.)
    c1,c2,c3=st.columns(3); c1.metric('Probabilità stimata',f'{p:.4%}'); c2.metric('Quota fair',f'{fair:.2f}'); c3.metric('Ritorno lordo alla quota inserita',f'€ {stake*offered:.2f}' if offered else 'Inserisci quota')
    if offered: st.metric('EV teorico netto',f"€ {stake*(offered*p-1):.2f}",help='Stima matematica, valida solo se le probabilità inserite sono corrette.')
    st.write('Selezioni:'); st.write('\n'.join(f'{i+1}. {x} — {q:.1%}' for i,(x,q) in enumerate(zip(labels,probs))))
else:
    st.subheader('Come leggere il programma e limiti')
    st.markdown('''- **Dati**: usa API-Football. La copertura e le richieste dipendono dal piano API e dal campionato.
- **Modello attuale**: Poisson con λ derivati da gol segnati/subiti nelle ultime 10 gare, distinguendo casa/trasferta e facendo blending con baseline. È un modello base, non xG avanzato.
- **Non include ancora**: xG provider, formazioni confermate, infortuni completi, quote live, calibrazione per campionato, modelli ML addestrati e backtest validato.
- **Quote fair** = 1/probabilità; non è una quota offerta dal bookmaker.
- Nessuna selezione è sicura. Usa limiti di spesa e non inseguire perdite.''')
