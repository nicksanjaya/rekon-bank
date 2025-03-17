# Library
import numpy as np
import pandas as pd
import streamlit as st

# Judul
st.title('APLIKASI REKON BANK')
    
st.markdown('---'*10)

#Rekon
def rekon(df_sap,df_bank):
    rekonsiliasi = pd.merge(df_sap, df_bank, on="Dokumen", suffixes=('_SAP', '_Bank'), how="outer", indicator=True)
    rekonsiliasi['selisih'] = rekonsiliasi['Amount_SAP'] - rekonsiliasi['Amount_Bank']
    rekonsiliasi['_merge'] = rekonsiliasi['_merge'].replace({'left_only': 'SAP_Only', 'right_only': 'Bank_Only'})
    st.write(f"<b>Hasil Rekonsiliasi:<b>", unsafe_allow_html=True)
    st.write(rekonsiliasi)
    rekonsiliasi_tidak_cocok = rekonsiliasi[rekonsiliasi['selisih']!= 0]
    rekonsiliasi_tidak_cocok = rekonsiliasi_tidak_cocok[['Dokumen', 'Amount_SAP', 'Amount_Bank', 'selisih', '_merge']]
    st.write(f"<b>Rekonsiliasi Tidak Cocok:<b>", unsafe_allow_html=True)
    st.write(rekonsiliasi_tidak_cocok)

#Upload File 
#st.write(f'<b>Produk {df.Produk[produk]} = {pyo.value(pro[pabrik,produk]):,.0f} pcs</b>', unsafe_allow_html=True)
data_sap = st.file_uploader("Upload Excel Data SAP", type=["xlsx"])
df_sap = pd.read_excel(data_sap)
st.write(df_sap)

#Upload
if data_sap is not None:
    try:
        data_bank = st.file_uploader("Upload Excel Data Bank", type=["xlsx"])
        df_bank = pd.read_excel(data_bank)
        st.write(df_bank)

    except Exception as e:
        st.error(f"Error reading the Excel file: {e}")

    if st.button("Run"):
        try:
            rekon(df_sap,df_bank)
        except Exception as e:
            st.error(f"Error : {e}")

