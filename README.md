# ⛳ Holms GK Tracker

En liten webbapp för att logga golfrundor och följa sin utveckling över tid. Byggd med
[Streamlit](https://streamlit.io/) och en PostgreSQL-databas i molnet ([Neon](https://neon.tech/)).

**Live:** https://golf-tracker-holm.streamlit.app/ (samma adress finns även i [`.README.md`](.README.md))

## Vad appen gör

- **Registrera runda** – spara datum, bana, antal slag och aktuellt HCP. Rundan lagras
  permanent i molndatabasen.
- **Se statistik** – en interaktiv [Plotly](https://plotly.com/python/)-graf som visar:
  - resultat runda för runda
  - en trendlinje över de 10 senaste rundorna
  - snittlinje samt markering av bästa (guld) och sämsta (röd) runda
- **Radera runda** – ta bort en felmatad runda via dess ID.
- **Fleranvändarstöd** – varje spelare (t.ex. Nicklas och Filiph) har en egen vy som är
  låst med ett lösenord/PIN och ser bara sina egna rundor.

## Teknik

| Del            | Används till                                        |
| -------------- | --------------------------------------------------- |
| Streamlit      | Webbgränssnitt och inloggningslogik                 |
| pandas / numpy | Läsa in och bearbeta runddata                       |
| Plotly         | Interaktiva grafer i appen                          |
| SQLAlchemy     | Databaskoppling och SQL-frågor                      |
| psycopg2       | PostgreSQL-driver                                   |
| PostgreSQL (Neon) | Permanent lagring av alla rundor                 |

Tabellen `golf_rundor` skapas automatiskt vid start om den inte redan finns
(kolumner: `id`, `anvandare`, `datum`, `bana`, `tee`, `slag`, `hcp`).

## Kom igång lokalt

### 1. Klona och installera

```bash
git clone <repo-url>
cd golf-tracker
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

### 2. Konfigurera hemligheter

Skapa filen `.streamlit/secrets.toml` (den är gitignore:ad och ska aldrig checkas in):

```toml
[connections.postgresql]
url = "postgresql://<användare>:<lösenord>@<host>/<dbnamn>?sslmode=require"

[golf_pins]
Nicklas = "<pin för Nicklas>"
Filiph = "<pin för Filiph>"
```

Fyll i era egna värden – filen ska aldrig checkas in.

### 3. Kör appen

```bash
streamlit run app.py
```

Appen öppnas på `http://localhost:8501`.

## Filer i projektet

| Fil                 | Innehåll                                                              |
| ------------------- | ------------------------------------------------------------------- |
| `app.py`            | Hela Streamlit-appen (inloggning, formulär, grafer, radering)        |
| `golf_analys.ipynb` | Jupyter-notebook med den ursprungliga CSV-baserade prototypen och `matplotlib`-grafer |
| `golf_rundor.csv`   | Exempeldata / ursprunglig datakälla från prototypen                  |
| `requirements.txt`  | Python-beroenden                                                     |

## Bakgrund

Projektet började som ett analysskript i `golf_analys.ipynb` där rundor sparades i en
CSV-fil och ritades med matplotlib. `app.py` är vidareutvecklingen: samma idé men som en
publik webbapp med molndatabas och stöd för flera spelare.

## Distribution

Appen driftas på [Streamlit Community Cloud](https://streamlit.io/cloud). Vid deploy läggs
innehållet i `secrets.toml` in under appens **Settings → Secrets** i Streamlit-dashboarden
i stället för i en lokal fil.
