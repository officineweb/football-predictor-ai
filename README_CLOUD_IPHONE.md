## Deploy cloud (iPhone + PC)

Questo progetto resta Python/Streamlit: **non caricarlo come sito statico Netlify**.
Per renderlo raggiungibile da iPhone senza PC acceso, pubblicalo su un hosting Python
(ad esempio Streamlit Community Cloud).

### Preparazione
1. Estrai questo ZIP.
2. Carica il contenuto della cartella in un repository GitHub (privato consigliato).
3. Su Streamlit Community Cloud crea una nuova app collegando il repository.
4. Imposta il file principale su `dashboard.py`.
5. In **App settings → Secrets** aggiungi:
   ```toml
   API_FOOTBALL_KEY = "INCOLLA_QUI_LA_TUA_API_KEY"
   ```
   Non inserire la chiave nel codice, nel repository o in chat.
6. Avvia il deploy. Apri l'URL assegnato da Safari su iPhone.
7. Safari → Condividi → **Aggiungi alla schermata Home**.

### Avvio locale Windows
- Doppio clic su `start_windows.bat` (se Python e dipendenze sono installati).
- In alternativa: `python -m pip install -r requirements.txt` e `streamlit run dashboard.py`.

### Nota sulla persistenza
Il file `schema.sql` definisce lo schema, ma la persistenza effettiva dipende da come
l'app usa il database. I filesystem degli hosting gratuiti possono essere temporanei:
esportare regolarmente lo storico oppure collegare un database persistente.

### Verifica prima del deploy
- Controlla la versione Python richiesta dalle dipendenze.
- Verifica i limiti e la copertura del tuo piano API-Football.
- Non tutte le competizioni dispongono di quote, formazioni o statistiche complete.
