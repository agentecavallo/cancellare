import streamlit as st
import pandas as pd
from duckduckgo_search import DDGS
import time
import re

st.set_page_config(page_title="Base Protection - Pro Finder", page_icon="🥾")

st.title("🚀 Localizzatore Avanzato Rivenditori")
st.write("Questo metodo cerca su internet la sede delle aziende. È molto più preciso!")

def trova_regione_web(nome_azienda):
    regioni_italia = [
        "Abruzzo", "Basilicata", "Calabria", "Campania", "Emilia-Romagna", 
        "Friuli-Venezia Giulia", "Lazio", "Liguria", "Lombardia", "Marche", 
        "Molise", "Piemonte", "Puglia", "Sardegna", "Sicilia", "Toscana", 
        "Trentino-Alto Adige", "Umbria", "Valle d'Aosta", "Veneto"
    ]
    
    try:
        with DDGS() as ddgs:
            # Cerchiamo l'azienda + "sede legale" o "contatti"
            query = f"{nome_azienda} sede legale regione"
            results = list(ddgs.text(query, max_results=3))
            
            # Uniamo i testi dei primi risultati per analizzarli
            testo_completo = " ".join([r['body'] for r in results]).lower()
            
            # Cerchiamo se nel testo appare una delle regioni italiane
            for regione in regioni_italia:
                if regione.lower() in testo_completo:
                    return regione
        return "Non trovato"
    except Exception as e:
        return f"Errore ricerca"

uploaded_file = st.file_uploader("Carica Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    colonna = st.selectbox("Colonna Ragione Sociale:", df.columns)
    
    if st.button("Avvia Ricerca Intelligente"):
        bar = st.progress(0)
        status = st.empty()
        risultati = []
        
        for i, row in df.iterrows():
            nome = row[colonna]
            status.text(f"Cercando sul web: {nome}...")
            
            regione = trova_regione_web(nome)
            risultati.append(regione)
            
            bar.progress((i + 1) / len(df))
            time.sleep(1.5) # Pausa per non essere scambiati per bot
            
        df['Regione_Trovata'] = risultati
        st.success("Completato!")
        st.dataframe(df)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Scarica Risultati", csv, "rivenditori_web.csv", "text/csv")
