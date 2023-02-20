import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from st_aggrid import GridOptionsBuilder, ColumnsAutoSizeMode, AgGrid

# Constants
S_COLS = ('Day', 'Description', 'Category', 'Amount', 'Allocation', 'Cleared')
S_DATA = [(1, 'Paycheck 1', 'Income', 2000.59, 'ABC Bank', 'Yes'),
          (2, 'Rent', 'Housing', 1000, 'Paycheck 1', 'Yes'),
          (2, 'Electric', 'Housing', 205.42, 'Paycheck 1', 'No'),
          (7, 'Paycheck 2', 'Income', 500, 'Ameri-bank', 'No'),
          (12, 'Doctor appt.', 'Medical', 60, 'Paycheck 2', 'No'),
          (14, 'Car payment', 'Loans', 300, 'Paycheck 1', 'No'),
          (15, 'Walmart', 'Groceries', 150, 'Paycheck 2', 'No')]
SAMPLE = pd.DataFrame([dict(zip(S_COLS, S_DATA[i])) for i in range(len(S_DATA))])

# Global data
df = pd.DataFrame(columns=S_COLS)
if 'df' in st.session_state:
    df = pd.DataFrame(st.session_state.df)
else:
    st.session_state.df = df

# Functions
def initialize_df():
    global df
    df = pd.DataFrame(columns=S_COLS)
    st.session_state.df = df

def load_sample():
    global df
    df = SAMPLE
    st.session_state.df = df

def append_rows(dataframe):
    global df
    df = pd.concat([df, dataframe])
    st.session_state.df = df

# Streamlit componenets
st.header("It's a Good Day for Budgeting!")
data, insights = st.tabs(['Data', 'Insights'])

with st.sidebar:
    upload = st.file_uploader('Upload budget CSV', 'csv')
    if upload is not None:
        dataframe = pd.read_csv(upload)
        add = st.button('Add rows', on_click=append_rows, args=[dataframe]) # type: ignore
        if add:
            st.success('Rows added!', icon="✅")

with data:
    if df.empty:
        st.dataframe(pd.DataFrame(columns=S_COLS))
    else:
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_default_column(editable=True, groupable=True)
        gb.configure_grid_options(domLayout='normal')
        modified_grid = AgGrid(df, gridOptions=gb.build(), columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
        st.session_state.df = modified_grid['data']
    left, buff, right = st.columns([1,2,1])

    with left:
        st.button('Clear table', on_click=initialize_df)

    with right:
        st.button('Load sample data', on_click=load_sample)

with insights:
    left, buff, right = st.columns([2,1,3])
    if not df.empty:
        with left: # Bar graph of Income and Allocated Expenses
            bar_data = {'Income': [], 'Expenses': []}
            accounts = np.unique((df[(df['Category'] == 'Income')]['Allocation'])).tolist()
            for account in accounts:
                account = str(account)
                inc_des_amt = df[(df['Category'] == 'Income') & (df['Allocation'] == account)]
                tot_income = inc_des_amt['Amount'].sum()
                income_names = np.unique(inc_des_amt['Description']).tolist()
                tot_expenses = 0.0
                for name in income_names:
                    name = str(name)
                    tot_expenses = tot_expenses + df[(df['Allocation'] == name)]['Amount'].sum()
                bar_data['Income'] += [tot_income]
                bar_data['Expenses'] += [tot_expenses]
            if len(bar_data['Income']) > 0:
                st.bar_chart(pd.DataFrame.from_dict(bar_data, orient='index', columns=accounts))

        with right: # Sankey Chart of Income to Total Income to Expense Categories
            s, t, v = 'source', 'target', 'value'
            s_t_v_data = []
            inc_des_amt = df[(df['Category'] == 'Income')].loc[:, ['Description', 'Amount']]
            for description, amount in zip(inc_des_amt['Description'].tolist(), inc_des_amt['Amount'].tolist()):
                s_t_v_data.append({s: description, t: 'Total Income', v: amount})
            exp_cat_amt = df[(df['Category'] != 'Income')].loc[:, ['Category', 'Amount']]
            categories = np.unique(exp_cat_amt['Category']).tolist()
            for category in categories:
                tot_amount = exp_cat_amt[(exp_cat_amt['Category'] == category)]['Amount'].sum()
                s_t_v_data.append({s: 'Total Income', t: category, v: tot_amount})
            if len(s_t_v_data) > 0:
                sankey_df = pd.DataFrame(s_t_v_data)
                nodes = np.unique(sankey_df[['source', 'target']], axis=None)
                nodes = pd.Series(index=nodes, data=range(len(nodes)))
                sankey = go.Sankey(node={'label': nodes.index},
                    link={'source': nodes.loc[sankey_df['source']],
                        'target': nodes.loc[sankey_df['target']],
                        'value': sankey_df['value']})
                fig = go.Figure(data=sankey)
                fig.update_layout(margin=dict(l=0, r=0, t=5, b=100))
                st.plotly_chart(fig, use_container_width=True)

# Debugging
st.write("Session State", st.session_state)
