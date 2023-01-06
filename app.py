import streamlit as st
import pandas as pd

# Constants
COLUMNS = ("Day", "Category", "Amount", "Allocation Name", "Automatic",
"Paid", "Cleared")
INDEX = ["Description"]

# Functions
def initialize_table():
    st.session_state.df = pd.DataFrame(columns=COLUMNS)

def append_rows(dataframe):
    st.session_state.df = pd.concat([st.session_state.df, dataframe])

# Initial Session State
if 'df' not in st.session_state:
    initialize_table()

# Debugging
st.write("Session State", st.session_state)

# Streamlit componenets
st.markdown("# It's a Good Day for Budgeting!")
data, insights = st.tabs(['Data', 'Insights'])

with st.sidebar:
    upload = st.file_uploader('Upload budget CSV', 'csv')
    if upload is not None:
        df = pd.read_csv(upload, index_col=INDEX)
        button = st.button('Add rows', on_click=append_rows, args=[df]) # type: ignore
        if button:
            st.success('Rows added!', icon="✅")

with data:
    df = pd.DataFrame(st.session_state.df)
    st.dataframe(df.style.format(precision=2, thousands=',', na_rep=' '), use_container_width=True)
    st.button('Clear table', on_click=initialize_table)
