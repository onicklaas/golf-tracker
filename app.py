import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
from datetime import date

# --- SETUP ---
DATA_FILE = 'golf_rundor.csv'

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=['Datum', 'Bana', 'Tee', 'Slag', 'HCP'])

df = load_data()

# Sätt sidans konfiguration (Viktigt för att vit bakgrund ska se bra ut)
st.set_page_config(page_title="Holms GK Tracker", layout="centered")

st.title('⛳ Holms GK Tracker')

# --- MENY ---
choice = st.sidebar.selectbox('Meny', ['Se Statistik', 'Registrera Runda'])

if choice == 'Registrera Runda':
    st.header('Registrera ny runda')

    with st.form('golf_form'):
        col1, col2 = st.columns(2)
        with col1:
            datum = st.date_input('Datum', date.today())
            bana = st.text_input('Bana', 'Holms GK')
        with col2:
            slag = st.number_input('Antal slag', min_value=50, max_value=150, value=100)
            hcp = st.number_input('Ditt HCP', value=25.4)
        
        submit = st.form_submit_button('Spara runda')

        if submit:
            new_data = pd.DataFrame([[datum, bana, 'Gul', slag, hcp]],
                                    columns=['Datum', 'Bana', 'Tee', 'Slag', 'HCP'])
            df = pd.concat([df, new_data], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success('Rundan är sparad!')
            st.balloons()

elif choice == 'Se Statistik':
    st.header('Din utveckling')
    
    if not df.empty:
        # 1. Förbered data
        df['Runda'] = np.arange(1, len(df) + 1)
        y = df['Slag'].values
        snitt = np.mean(y)
        basta = np.min(y)
        samsta = np.max(y)
        trend = df['Slag'].rolling(window=10, min_periods=1).mean()

        # 2. Skapa figuren (Plotly)
        fig = go.Figure()

        # BLÅ LINJE MELLAN PUNKTER
        fig.add_trace(go.Scatter(
            x=df['Runda'], y=y,
            mode='lines',
            line=dict(color='#3498db', width=2),
            name='Runda till runda',
            hoverinfo='skip'
        ))

        # TRENDLINJE (Prickad mörkgrå för att inte störa den blå linjen för mycket)
        fig.add_trace(go.Scatter(
            x=df['Runda'], y=trend,
            mode='lines',
            name='Trend (10 senaste)',
            line=dict(color='#2c3e50', width=2, dash='dot')
        ))

        # RITA PLUPPARNA
        for i in range(len(df)):
            # Standardfärg (Mörkgrå för vanliga rundor)
            punkt_farg = '#34495e' 
            storlek = 10
            kant_farg = 'white'
            namn = "Runda"
            
            # Specialfall: Bästa och Sämsta
            if y[i] == basta:
                punkt_farg = '#f1c40f' # Guld
                kant_farg = 'black'
                storlek = 9
                namn = "Bästa runda"
            elif y[i] == samsta:
                punkt_farg = '#e74c3c' # Röd
                kant_farg = 'black'
                storlek = 9
                namn = "Sämsta runda"

            fig.add_trace(go.Scatter(
                x=[df['Runda'].iloc[i]], 
                y=[y[i]],
                mode='markers',
                name=namn,
                marker=dict(size=storlek, color=punkt_farg, line=dict(width=1, color=kant_farg)),
                hovertemplate=f"<b>Runda {i+1}</b><br>Resultat: {y[i]} slag<extra></extra>",
                # Visar bara unika etiketter i legenden
                showlegend=True if (y[i] in [basta, samsta] or i == 0) else False 
            ))

        # SNITTLINJE
        fig.add_hline(y=snitt, line_dash="dash", line_color="rgba(0,0,0,0.2)", 
                      annotation_text=f"Snitt: {snitt:.1f}", annotation_font_color="black")

        # 3. Layout-inställningar (Korrigerad för vit bakgrund och Plotly-version)
        fig.update_layout(
            plot_bgcolor='white', 
            paper_bgcolor='white',
            hovermode="closest",
            xaxis=dict(
                title=dict(text="Antal rundor", font=dict(color='black')),
                range=[0.5, max(50, len(df)+1)],
                gridcolor='#f0f0f0',
                linecolor='black',
                tickfont=dict(color='black')
            ),
            yaxis=dict(
                title=dict(text="Antal slag", font=dict(color='black')),
                range=[135, 65], # Lägre slag högre upp
                gridcolor='#f0f0f0',
                linecolor='black',
                tickfont=dict(color='black')
            ),
            legend=dict(
                font=dict(color='black'),
                orientation="h", 
                yanchor="bottom", 
                y=-0.3,
                xanchor="center", 
                x=0.5
            ),
            height=500,
            margin=dict(l=10, r=10, t=20, b=10)
        )

        # Visa grafen
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabell underst
        st.write("### Senaste rundorna")
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)
        
    else:
        st.info('Inga rundor registrerade än. Gå till "Registrera Runda" i menyn!')