# Library
import pyomo.environ as pyo
from pyomo.environ import *
from pyomo.opt import SolverFactory
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from datetime import datetime

# Judul
st.title('OPTIMASI PERENCANAAN PRODUKSI DAN DISTRIBUSI GLOBAL')

#Imputasi
def preprocessing(df):
    columns_to_impute = [col for col in df.columns if col != 'Produk']
    preprocessor = ColumnTransformer([
        ('imputasi', SimpleImputer(strategy='constant', fill_value=0), columns_to_impute)],
        remainder='passthrough',
        verbose_feature_names_out=False
    )
    preprocessor.fit(df)
    df = preprocessor.transform(df)
    df = pd.DataFrame(df, columns=preprocessor.get_feature_names_out())
    cols = df.columns.tolist()
    cols.insert(0, cols.pop(-1))
    df = df[cols]
    return df

#Converter
def convert_df(df):
    required_columns = ['Produk','Sales','Cost Pabrik 1','Cost Pabrik 2','Cost Pabrik 3','Demand Area 1','Demand Area 2','Demand Area 3']
    for col in required_columns:
        if col not in df.columns:
            st.error(f'Missing required columns: {col}')
            return
        
    for i in df.columns:
        if i != 'Produk':
            df[i] = df[i].astype(int)
            
    df.columns = [col.replace(' ','_') for col in df.columns]
    return df
            
#Margin
def margin(df):
    df['Margin_1'] = df['Sales'] - df['Cost_Pabrik_1']
    df['Margin_2'] = df['Sales'] - df['Cost_Pabrik_2']
    df['Margin_3'] = df['Sales'] - df['Cost_Pabrik_3']

#Optimasi
def optimization(df,capacity):
    #Variable
    model = pyo.ConcreteModel()
    model.Pro = pyo.Var(range(3), range(len(df.Produk)), domain=pyo.NonNegativeReals)
    pro = model.Pro
    
    #Batasan kapasitas
    model.limits = pyo.ConstraintList()
    for pabrik in range(3):
        for produk in range(len(df.Produk)):
            model.limits.add(expr = pro[pabrik,produk] <= capacity[pabrik])

    #Batasan Pasar
    pro_sums = {kolom: sum(pro[pabrik, kolom] for pabrik in range(3)) for kolom in range(len(df.Produk))}
    model.demand = pyo.ConstraintList()
    for kolom, pro_sum in pro_sums.items():
        model.demand.add(expr = pro_sum <= sum(df[f'Demand_Area_{i}'][kolom] for i in range(1, 5)))
        
    # Objektif
    Margin_1 = df['Margin_1'].tolist()
    Margin_2 = df['Margin_2'].tolist()
    Margin_3 = df['Margin_3'].tolist()

    koefisien = [
        Margin_1,  # Koefisien untuk pabrik 0
        Margin_2,  # Koefisien untuk pabrik 1
        Margin_3   # Koefisien untuk pabrik 2
    ]
    
    pro_sum_obj = sum(koefisien[pabrik][kolom] * pro[pabrik, kolom] for pabrik in range(3) for kolom in range(len(df.Produk)))
    model.obj = pyo.Objective(expr = pro_sum_obj, sense = maximize)

    #Solver
    opt = SolverFactory('glpk')
    results = opt.solve(model, tee=True) # tee=True untuk menampilkan output solver di konsol
    
    #Cek hasil solusi
    if results.solver.status != SolverStatus.ok or results.solver.termination_condition != TerminationCondition.optimal:
        st.error(f"Solusi tidak ditemukan! Status solver: {results.solver.status}, Termination condition: {results.solver.termination_condition}")
        return
    
    # Menambahkan garis pembatas
    st.markdown('---'*10)
    
    #Hasil optimasi
    for pabrik in range (3):
        st.write(f"<b>Produksi Pabrik {pabrik+1}<b>", unsafe_allow_html=True)
        for produk in range(len(df.Produk)):
            st.write(f'<b>Produk {df.Produk[produk]} = {pyo.value(pro[pabrik,produk]):,.0f} pcs</b>', unsafe_allow_html=True)
        st.markdown('---'*10)

#Upload File 
uploaded_file = st.file_uploader("Upload Excel Master Data", type=["xlsx"])

#Upload
if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        df = preprocessing(df)
        df = convert_df(df)
        margin(df)
        st.write(df)
    except Exception as e:
        st.error(f"Error reading the Excel file: {e}")

    #Input Capacity
    capacity_1 = st.number_input("Kapasitas Pabrik 1:", min_value=0)
    capacity_2 = st.number_input("Kapasitas Pabrik 2:", min_value=0)
    capacity_3 = st.number_input("Kapasitas Pabrik 3:", min_value=0)
    capacity = [capacity_1, capacity_2, capacity_3]
    
    if st.button("Calculate"):
        try:
            optimization(df, capacity)
        except Exception as e:
            st.error(f"Error : {e}")

