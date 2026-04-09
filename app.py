import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
import time

# Configurazione pagina
st.set_page_config(page_title="Geolocalizzatore Rivenditori", layout="centered")

st.title("📍 Assegnazione Regioni Rivenditori")
st.write("Carica il tuo file Excel con le ragioni sociali e io cercherò la regione di appartenenza.")

# Inizializza il geolocalizzatore
geolocator = Nominatim(user_agent="michele_area_manager_app")

def get_region(name):
    try:
        # Cerchiamo solo in Italia per maggiore precisione
        location = geolocator.geocode(f"{name}, Italia", addressdetails=True, timeout=10)
        if location and 'address' in location.raw:
            return location.raw['address'].get('state', 'Non trovata')
        return "Non trovato"
    except:
        return "Errore connessione"

uploaded_file = st.file_uploader("Scegli un file Excel", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    colonna_scelta = st.selectbox("Seleziona la colonna con la Ragione Sociale:", df.columns)
    
    if st.button("Avvia Elaborazione"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        results = []
        
        total = len(df)
        
        for i, row in df.iterrows():
            nome_azienda = row[colonna_scelta]
            status_text.text(f"Ricerca in corso per: {nome_azienda} ({i+1}/{total})")
            
            regione = get_region(nome_azienda)
            results.append(regione)
            
            # Aggiorna barra progresso
            progress_bar.progress((i + 1) / total)
            
            # Rispetto delle policy di OpenStreetMap (1 richiesta al secondo)
            time.sleep(1)
        
        df['Regione_Trovata'] = results
        st.success("Elaborazione completata!")
        
        # Anteprima e Download
        st.dataframe(df.head(10))
        
        @st.cache_data
        def convert_df(df_to_save):
            return df_to_save.to_csv(index=False).encode('utf-8')

        csv = convert_df(df)
        st.download_button(
            label="Scarica Risultato in CSV",
            data=csv,
            file_name="rivenditori_regioni.csv",
            mime="text/csv",
        )
