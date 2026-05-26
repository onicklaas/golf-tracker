import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import date
from sqlalchemy import create_engine, text
import time

# Sätt sidans konfiguration först
st.set_page_config(page_title="Holms GK Tracker", layout="centered")

# --- KOPPLING TILL NEON POSTGRESQL ---
def get_db_engine():
    db_url = st.secrets["connections"]["postgresql"]["url"]
    return create_engine(db_url)

engine = get_db_engine()

def init_db():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS golf_rundor (
        id SERIAL PRIMARY KEY,
        anvandare VARCHAR(50),
        datum DATE,
        bana VARCHAR(100),
        tee VARCHAR(20),
        slag INT,
        hcp NUMERIC(4,1)
    );
    """
    with engine.connect() as conn:
        conn.execute(text(create_table_query))
        conn.commit()

init_db()

def load_sql_data():
    query = "SELECT anvandare, datum, bana, tee, slag, hcp FROM golf_rundor"
    try:
        df = pd.read_sql(text(query), engine)
        df['datum'] = df['datum'].astype(str)
        df.columns = ['Användare', 'Datum', 'Bana', 'Tee', 'Slag', 'HCP']
        return df
    except:
        return pd.DataFrame(columns=['Användare', 'Datum', 'Bana', 'Tee', 'Slag', 'HCP'])

full_df = load_sql_data()

st.title('⛳ Holms GK Tracker')

# --- ANVÄNDARVAL (Sidomeny) ---
anvandare = st.sidebar.selectbox('Vem är du?', ['Nicklas', 'Filiph'])

# --- INLOGGNINGS-LOGIK MED SESSION STATE ---
# Vi skapar en nyckel i minnet för att hålla koll på vem som är inloggad
if "inloggad_som" not in st.session_state:
    st.session_state["inloggad_som"] = None

# Om man byter namn i listan, eller inte är inloggad alls, visa lösenordsfältet
if st.session_state["inloggad_som"] != anvandare:
    st.header(f"🔒 Låst: {anvandare}")
    st.write(f"Ange lösenordet för {anvandare} för att se statistik och registrera rundor.")
    
    lozenord = st.text_input("Lösenord", type="password")
    if st.button("Logga in"):
        ratt_pin = st.secrets["golf_pins"][anvandare]
        
        if lozenord == ratt_pin:
            st.session_state["inloggad_som"] = anvandare
            st.success(f"Välkommen in, {anvandare}!")
            time.sleep(1)
            st.rerun()
        else:
            st.error("❌ Fel lösenord, försök igen.")
            
    # Stoppa appen här så att obehöriga inte ser menyn eller grafen
    st.stop()


# --- OM MAN ÄR INLOGGAD, VISA RESTEN AV APPEN ---
st.sidebar.success(f"Inloggad som: {anvandare}")
if st.sidebar.button("Logga ut"):
    st.session_state["inloggad_som"] = None
    st.rerun()

# Filtrera ut data för den inloggade spelaren
df = full_df[full_df['Användare'] == anvandare].copy()

# --- MENY ---
choice = st.sidebar.selectbox('Meny', ['Se Statistik', 'Registrera Runda'])

if choice == 'Registrera Runda':
    st.header(f'Registrera ny runda for {anvandare}')

    with st.form('golf_form'):
        col1, col2 = st.columns(2)
        with col1:
            datum = st.date_input('Datum', date.today())
            bana = st.text_input('Bana', 'Holms GK')
        with col2:
            slag = st.number_input('Antal slag', min_value=50, max_value=150, value=100)
            default_hcp = 21.6 if anvandare == 'Nicklas' else 25.4
            hcp = st.number_input('Ditt HCP', value=default_hcp, format="%.1f")
        
        submit = st.form_submit_button('Spara runda')

        if submit:
            insert_query = """
                INSERT INTO golf_rundor (anvandare, datum, bana, tee, slag, hcp)
                VALUES (:anvandare, :datum, :bana, :tee, :slag, :hcp)
            """
            with engine.connect() as conn:
                conn.execute(
                    text(insert_query), 
                    {
                        "anvandare": anvandare, 
                        "datum": datum, 
                        "bana": bana, 
                        "tee": 'Gul', 
                        "slag": int(slag), 
                        "hcp": float(hcp)
                    }
                )
                conn.commit()
            
            st.success(f'Rundan är sparad PERMANENT i molndatabasen för {anvandare}!')
            st.balloons()
            
            time.sleep(2)
            st.rerun()

elif choice == 'Se Statistik':
    st.header(f'Utveckling för {anvandare}')
    
    if not df.empty:
        df = df.sort_values('Datum').reset_index(drop=True)
        df['Runda'] = np.arange(1, len(df) + 1)
        
        y = df['Slag'].values
        snitt = np.mean(y)
        basta = np.min(y)
        samsta = np.max(y)
        trend = df['Slag'].rolling(window=10, min_periods=1).mean()

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df['Runda'], y=y, mode='lines',
            line=dict(color='#3498db', width=2), name='Runda till runda', hoverinfo='skip'
        ))

        fig.add_trace(go.Scatter(
            x=df['Runda'], y=trend, mode='lines', name='Trend (10 senaste)',
            line=dict(color='#2c3e50', width=2, dash='dot')
        ))

        for i in range(len(df)):
            punkt_farg = '#34495e' 
            storlek = 10
            kant_farg = 'white'
            namn = "Runda"
            
            if y[i] == basta:
                punkt_farg = '#f1c40f'
                kant_farg = 'black'
                storlek = 9
                namn = "Bästa runda"
            elif y[i] == samsta:
                punkt_farg = '#e74c3c'
                kant_farg = 'black'
                storlek = 9
                namn = "Sämsta runda"

            fig.add_trace(go.Scatter(
                x=[df['Runda'].iloc[i]], y=[y[i]], mode='markers', name=namn,
                marker=dict(size=storlek, color=punkt_farg, line=dict(width=1, color=kant_farg)),
                hovertemplate=f"<b>Runda {i+1}</b><br>Datum: {df['Datum'].iloc[i]}<br>Resultat: {y[i]} slag<extra></extra>",
                showlegend=True if (y[i] in [basta, samsta] or i == 0) else False 
            ))

        fig.add_hline(y=snitt, line_dash="dash", line_color="rgba(0,0,0,0.2)", 
                      annotation_text=f"Snitt: {snitt:.1f}", annotation_font_color="black")

        fig.update_layout(
            plot_bgcolor='white', 
            paper_bgcolor='white',
            hovermode="closest",
            xaxis=dict(
                title=dict(text="Antal rundor", font=dict(color='black')),
                range=[0.5, max(50, len(df)+1)],
                gridcolor='#f0f0f0',
                linecolor='black',
                tickfont=dict(color='black')  # Siffrorna på X-axeln blir svarta
            ),
            yaxis=dict(
                title=dict(text="Antal slag", font=dict(color='black')),
                range=[65, 135], 
                gridcolor='#f0f0f0',
                linecolor='black',
                tickfont=dict(color='black')  # Siffrorna på Y-axeln blir svarta
            ),
            legend=dict(
                font=dict(color='black'),      # Texten i förklaringen längst ner blir svart
                orientation="h", 
                yanchor="bottom", 
                y=-0.3,
                xanchor="center", 
                x=0.5
            ),
            height=500,
            margin=dict(l=10, r=10, t=20, b=10)
        )

        st.plotly_chart(fig, use_container_width=True)
        st.write(f"### Senaste rundorna för {anvandare}")
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    else:
        st.info(f'Inga rundor registrerade än. Gå till "Registrera Runda"!')