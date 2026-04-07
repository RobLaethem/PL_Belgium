import pandas as pd
import streamlit as st
import numpy as np

st.title("Belgian powerlifting percentiles")
# read the csv file that is in the same repo as this script, and is called ipf2026_belgium_raw.csv
df = pd.read_csv("ipf2026_belgium_raw.csv", sep=',', decimal='.', encoding='utf-8-sig')
# convert Date to datetime
df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')


#make a dropdown to select weightclass
weight_classes = ["52","57","63","69","76","84","84+","59","66","74","83","93","105","120","120+"]
selected_weight_class = st.selectbox("Select weight class", weight_classes)
#make a dropdown to select a year
years = [2024,2025]
selected_year = st.selectbox("Select year", years)
#make a textbox to input a total (ensure it is a number, else ask again)
total_input = st.text_input("Enter total in kg")
try:
    total_input = float(total_input)
except ValueError:
    st.warning("Please enter a valid number for total")
    st.stop()

# filter the dataframe for the selected weight class and year
df_filtered0 = df[(df['WeightClassKg'] == selected_weight_class) & (df['Date'].dt.year == selected_year)]
#drop duplicate entries for the same name in one weightclass, keep the best result per lifter
df_filtered = df_filtered0.sort_values('TotalKg', ascending=False).drop_duplicates('Name')
#calculate the percentile of the input total compared to the filtered dataframe

totals = df_filtered['TotalKg'].astype(float).dropna().values
if float(total_input) >= np.nanmax(totals):
    percentile = 100.0
else:
    totals_with_input = np.append(totals, float(total_input))
    percentile = (totals_with_input <= float(total_input)).mean() * 100
st.write(f"The percentile of a total of {total_input} kg in the {selected_weight_class} kg class for the year {selected_year} is: {percentile:.2f}%")
