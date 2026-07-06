import pandas as pd
import streamlit as st

st.title("Belgian powerlifting percentiles")
# Add custom CSS to scale down UI elements
st.markdown(
    """
    <style>
    .css-18e3th9 {padding: 0.5rem 0.5rem;}
    .css-1d391kg {font-size: 0.9rem;}
    .stSelectbox label, .stTextInput label {font-size: 0.9rem;}
    </style>
    """,
    unsafe_allow_html=True
)
# read the csv file that is in the same repo as this script, and is called ipf2026_belgium_raw.csv
df = pd.read_csv("ipf2026_belgium_raw.csv", sep=',', decimal='.', encoding='utf-8-sig')
# convert Date to datetime
df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
# Fill NaN with a placeholder string
df['WeightClassKg'] = df['WeightClassKg'].fillna('Unknown')

#make a dropdown to select 'squat', 'bench', 'deadlift' or 'total'
lift = st.selectbox("Select lift", ["Squat", "Bench", "Deadlift", "Total"])
#make a dropdown to select weightclass
weight_classes = ["52","57","63","69","76","84","84+","59","66","74","83","93","105","120","120+"]
selected_weight_class = st.selectbox("Select weight class", weight_classes)
#make a dropdown to select a year
years = [2024,2025]
selected_year = st.selectbox("Select year", years)
#make a textbox to input a total (ensure it is a number, else ask again)
total_input = st.text_input("Enter weight in kg")
try:
    total_input = float(total_input)
except ValueError:
    st.warning("Please enter a valid number for this lift")
    st.stop()

"""#TESTCASE: 120+ kg class, year 2024, total 500 kg, lift Total (result 50%)
lift = "Total"
selected_weight_class = "120+"
selected_year = 2024
total_input = 500"""

# filter the dataframe for the selected weight class and year
df_filtered0 = df[(df['WeightClassKg'] == selected_weight_class) & (df['Date'].dt.year == selected_year)]
#make string to filter the dataframe for the selected lift, by adding 'Kg' to the end of the lift name, and using that as the column name
#if the lift is 'Total', then use 'TotalKg' as the column name, else add "Best3" before it
if lift == "Total":
    lift_selection = "TotalKg"
else:
    lift_selection = "Best3" + lift + "Kg"

#drop duplicate entries for the same name in one weightclass, keep the best result per lifter
df_filtered = df_filtered0.sort_values(lift_selection, ascending=False).drop_duplicates('Name')

#calculate the percentile of the input total compared to the filtered dataframe
import numpy as np

totals = df_filtered[lift_selection].astype(float).dropna().values
if float(total_input) >= np.nanmax(totals):
    percentile = 100.0
else:
    totals_with_input = np.append(totals, float(total_input))
    percentile = (totals_with_input <= float(total_input)).mean() * 100
print(f"The percentile of a {lift_selection} of {total_input} kg in the {selected_weight_class} kg class for the year {selected_year} is: {percentile:.2f}%")
st.write(f"The percentile of a {lift_selection} of {total_input} kg in the {selected_weight_class} kg class for the year {selected_year} is: {percentile:.2f}%")

# make a histogram of the filtered dataframe for the selected lift, with the input total as a vertical line
import matplotlib.pyplot as plt

df_class = df_filtered.sort_values(lift_selection, ascending=False).drop_duplicates('Name')
n = len(df_class)
#calculate mean and median of the TotalKg column
mean = df_class[lift_selection].mean()
median = df_class[lift_selection].median()
#calculate 10% and 90% of the TotalKg column
#rank-based percentiles
totals_sorted = np.sort(df_class[lift_selection].values)
rank_10 = int(0.1 * len(totals_sorted))
if rank_10 >= len(totals_sorted):
    rank_10 = len(totals_sorted) - 1
p10 = totals_sorted[rank_10]

rank_90 = int(0.9 * len(totals_sorted))
if rank_90 >= len(totals_sorted):
    rank_90 = len(totals_sorted) - 1
p90 = totals_sorted[rank_90]
 #calculate the min and max of the TotalKg column
min_total = df_class[lift_selection].min()
max_total = df_class[lift_selection].max()
# set binrange (number of kg per bin)
binrange = 50
# Find the nearest multiples of binrange for min and max
min_edge = binrange * (min_total // binrange)
max_edge = binrange * ((max_total // binrange) + 1)
# Create bin edges at every 10kg
bins = np.arange(min_edge, max_edge + binrange, binrange)
# create a plot containing a histogram of the TotalKg column showing how many lifters lifted a certain total weight
plt.figure(figsize=(7,4))
plt.hist(df_class[lift_selection], bins=bins, edgecolor='black')
# add a vertical line in different colors for the mean and median, p10,and p90 add them in a legend
plt.axvline(p10, color='green', linestyle='dashed', linewidth=1, label=f'10th Percentile: {p10:.2f}')
plt.axvline(mean, color='orange', linestyle='dashed', linewidth=1, label=f'Mean: {mean:.2f}')
plt.axvline(median, color='blue', linestyle='dashed', linewidth=1, label=f'Median: {median:.2f}')
plt.axvline(p90, color='red', linestyle='dashed', linewidth=1, label=f'90th Percentile: {p90:.2f}')
plt.legend(fontsize=10)
plt.xticks(fontsize=10)
if selected_weight_class ==  '84':
    selected_weight_class = '-84'
if selected_weight_class ==  '120':
    selected_weight_class = '-120'
plt.title(f"Raw Total for {selected_weight_class} in {selected_year} (n={n})")
st.pyplot (plt)
