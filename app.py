import streamlit as st
import pandas as pd

# Constants
COLUMNS = ("Day", "Category", "Amount", "Allocation", "Automatic",
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

with insights:
    df = pd.DataFrame(st.session_state.df)
    left, middle, right = st.columns([1,1,1])
    with left:
        bar_data = {'Income': [], 'Expenses': []}
        accounts = list(set(df[(df['Category'] == 'Income')]['Allocation'].tolist()))
        for account in accounts:
            account = str(account)
            income_lines = df[(df['Category'] == 'Income') & (df['Allocation'] == account)]
            tot_income = income_lines['Amount'].sum()
            income_names = income_lines.index.values.tolist()
            tot_expenses = 0.0
            for name in income_names:
                name = str(name)
                tot_expenses = tot_expenses + df[(df['Allocation'] == name)]['Amount'].sum()
            bar_data['Income'] += [tot_income]
            bar_data['Expenses'] += [tot_expenses]
        st.bar_chart(pd.DataFrame.from_dict(bar_data, orient='index', columns=accounts))
