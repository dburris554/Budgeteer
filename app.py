import streamlit as st
import pandas as pd
# import plotly.graph_objects as go
import numpy as np

# Constants
COLUMNS = ('Day', 'Category', 'Amount', 'Allocation', 'Automatic',
'Paid', 'Cleared')
INDEX = ['Description']
S_COLS = ('Day', 'Description', 'Category', 'Amount', 'Allocation', 'Cleared')
S_DATA = [(1, 'Paycheck 1', 'Income', 2000.59, 'ABC Bank', 'Yes'),
          (2, 'Rent', 'Housing', 1000, 'Paycheck 1', 'Yes'),
          (2, 'Electric', 'Housing', 205.42, 'Paycheck 1', 'No'),
          (7, 'Paycheck 2', 'Income', 500, 'Ameri-bank', 'No'),
          (12, 'Doctor appt.', 'Medical', 60, 'Paycheck 2', 'No'),
          (14, 'Car payment', 'Loans', 300, 'Paycheck 1', 'No'),
          (15, 'Walmart', 'Groceries', 150, 'Paycheck 2', 'No')]
SAMPLE = pd.DataFrame([
    dict(zip(S_COLS, S_DATA[i])) for i in range(len(S_DATA))
], index=[row[1] for row in S_DATA]).drop('Description', axis=1)

# Functions
def initialize_table():
    st.session_state.df = pd.DataFrame(columns=COLUMNS)

def load_sample():
    st.session_state.df = SAMPLE

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
    left, buff, right = st.columns([1,2,1])

    with left:
        st.button('Clear table', on_click=initialize_table)

    with right:
        st.button('Load sample data', on_click=load_sample)

with insights:
    df = pd.DataFrame(st.session_state.df)
    left, right = st.columns([1,2])

    with left: # Total Income vs Expenses
        bar_data = {'Income': [], 'Expenses': []}
        accounts = np.unique((df[(df['Category'] == 'Income')]['Allocation'])).tolist()
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

    # with right:
        # sankey = go.Sankey(link=link, node=node)
        # fig = go.Figure(sankey)
        # fig.update_layout(margin=dict(l=0, r=0, t=5, b=5))
        # st.plotly_chart(fig, use_container_width=True)
