import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
import time
import re

# Configurazione Pagina
st.set_page_config(page_title="Base Protection - Area Manager Tool", page_icon="🥾")

st.title("📍 Localizzatore Rivenditori Michele")
st.markdown("""
Questo strumento cerca la **Regione** dei tuoi rivenditori partendo dalla Ragione Sociale.
*Nota: Utilizza OpenStreetMap (Gratuito). Se il nome è troppo generico, potrebbe non trovarlo.*
""")

# Inizializzazione Geocoder
geolocator = Nominatim(user_agent="michele_base_tool_v2")

def pulisci_nome(nome):
    """Rimuove sigle societarie per facilitare la ricerca"""
    nome = str(nome).upper()
    sigle = [r'\bSRL\b', r'\bSPA\b', r'\bS\.R\.L\.\b', r'\bS\.P\.A\.\b', r'\bSAS\b', r'\bSNC\b']
    for sigla in sigle:
        nome = re.sub(sigla, '', nome)
    return nome.strip()

def get_info(ragione_sociale):
    nome_pulito = pulisci_nome(ragione_sociale)
    try:
        # Cerchiamo l'azienda in Italia
        location = geolocator.geocode(f"{nome_pulito}, Italia", addressdetails=True, timeout=10)
        
        if location and 'address' in location.raw:
            addr = location.raw['address']
            # Estraiamo Regione e Provincia
            regione = addr.get('state', 'Non trovata')
            provincia = addr.get('county', 'Non trovata')
            return regione, provincia
        return "Non trovato", "Non trovata"
    except:
        return "Errore connessione", "Errore"

# Caricamento File
uploaded_file = st.file_uploader("Carica il tuo file Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    colonna = st.selectbox("Seleziona la colonna con i nomi delle aziende:", df.columns)
    
    if st.button("🚀 Avvia Ricerca"):
        bar = st.progress(0)
        status = st.empty()
        
        regioni = []
        province = []
        
        for i, row in df.iterrows():
            nome = row[colonna]
            status.text(f"Analizzando: {nome}...")
            
            reg, prov = get_info(nome)
            regioni.append(reg)
            province.append(prov)
            
            # Aggiornamento progresso
            bar.progress((i + 1) / len(df))
            # Pausa obbligatoria per non essere bloccati dal server (gratuito)
            time.sleep(1.1)
            
        df['Regione_Trovata'] = regioni
        df['Provincia_Trovata'] = province
        
        st.success("✅ Analisi completata!")
        st.dataframe(df)
        
        # Preparazione Download
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Scarica Risultati (CSV)",
            data=csv,
            file_name="rivenditori_regioni_michele.csv",
            mime="text/csv",
        )
