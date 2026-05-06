import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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
            # RÄTTAT: 'value' istället för 'values'
            slag = st.number_input('Antal slag', min_value=50, max_value=150, value=100)
            hcp = st.number_input('Ditt HCP', value=25.4)
        
        submit = st.form_submit_button('Spara runda')

        if submit:
            new_data = pd.DataFrame([[datum, bana, 'Gul', slag, hcp]],
                                    columns=['Datum', 'Bana', 'Tee', 'Slag', 'HCP'])
            # Uppdatera både lokalt i minnet och i filen
            df = pd.concat([df, new_data], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success('Rundan är sparad!')
            st.balloons()

elif choice == 'Se Statistik':
    st.header('Din utveckling')
    
    if not df.empty:
        # Skapa figuren för grafen
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Förbered data med NumPy
        x = np.arange(1, len(df) + 1)
        y = df['Slag'].values
        snitt = np.mean(y)
        
        # 1. Rita linjesegment med dynamisk färg
        for i in range(len(x) - 1):
            mellan = (y[i] + y[i+1]) / 2
            linje_farg = '#2ecc71' if mellan <= snitt else '#e74c3c'
            ax.plot([x[i], x[i+1]], [y[i], y[i+1]], color=linje_farg, linewidth=1.5, zorder=1)

        # 2. Rita plupparna (inkl. guld för bästa och svart för sämsta)
        basta = np.min(y)
        samsta = np.max(y)
        
        for i in range(len(x)):
            punkt_farg = '#2ecc71' if y[i] <= snitt else '#e74c3c'
            storlek = 50
            kant = 'none'
            
            if y[i] == basta:
                punkt_farg = 'gold'
                storlek = 130
                kant = 'black'
            elif y[i] == samsta:
                punkt_farg = 'black'
                storlek = 100
                kant = 'red'
                
            ax.scatter(x[i], y[i], color=punkt_farg, s=storlek, edgecolors=kant, zorder=2)

        # 3. Snittlinjen
        ax.axhline(snitt, color='blue', linestyle='--', linewidth=1, label=f'Snitt: {snitt:.1f}', zorder=0)

        # 4. Inställningar för diagrammet
        ax.set_ylim(70, 130)
        ax.set_xlim(1, 50)
        ax.set_xticks([1] + list(np.arange(5, 51, 5)))
        ax.set_xlabel('Antal rundor')
        ax.set_ylabel('Antal slag')
        ax.grid(True, alpha=0.2)
        ax.legend()
        
        # Visa grafen i Streamlit
        st.pyplot(fig)
        
        # Visa rådatan som en snygg tabell underst
        st.write("### Senaste rundorna")
        st.dataframe(df.sort_index(ascending=False))
        
    else:
        st.info('Inga rundor registrerade än. Gå till "Registrera Runda" i menyn till vänster!')