# Football Predictor AI v0.6 Advanced Mobile
Base completa dashboard v0.4 + motore advanced_engine.py + configurazione deployment.
## Windows
1. Python 3.11+ (Add Python to PATH)
2. Copia `.env.example` in `.env` e imposta `API_FOOTBALL_KEY=...`
3. Doppio clic start_windows.bat
## iPhone sulla stessa Wi-Fi
`python -m streamlit run dashboard.py --server.address 0.0.0.0`
Poi Safari `http://IP-DEL-PC:8501`; PC acceso e firewall abilitato.
## iPhone ovunque (cloud)
Carica il progetto su repo GitHub privata (mai .env), deploy Streamlit Community Cloud/VPS; in Secrets imposta `API_FOOTBALL_KEY = "..."`; apri URL su Safari > Condividi > Aggiungi alla schermata Home. Per app personale, aggiungere autenticazione e non esporre pubblicamente.
## Funzionalità
Dashboard: scanner fixtures API-Football, analisi Poisson, mercati, quote fair, shortlist, schedina e export. advanced_engine: Poisson scoreline/markets, shrinkage, fair odds, EV e accumulator.
## Limiti importanti
Non è ancora AI addestrata/calibrata; non incorpora ancora quote bookmaker, lineup, injury, xG reali nel modello né un backtest validato. Probabilità indicative, no garanzia. Le multiple assumono indipendenza; selezioni correlate possono distorcere il calcolo. API limitate dal piano.
