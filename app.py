# Library
import numpy as np
import pandas as pd
import streamlit as st

# Judul
st.title('APLIKASI REKON BANK')
    
st.markdown('---'*10)

#Upload File 
#st.write(f'<b>Produk {df.Produk[produk]} = {pyo.value(pro[pabrik,produk]):,.0f} pcs</b>', unsafe_allow_html=True)
data_sap = st.file_uploader("Upload Excel Data SAP", type=["xlsx"])

#Upload
if data_sap is not None:
    try:
        df = pd.read_excel(data_sap)
        data_bank = st.file_uploader("Upload Excel Data Bank", type=["xlsx"])

    except Exception as e:
        st.error(f"Error reading the Excel file: {e}")

    if st.button("Run"):
        try:
            optimization(df, capacity)
        except Exception as e:
            st.error(f"Error : {e}")

