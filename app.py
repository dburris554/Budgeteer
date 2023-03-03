import streamlit as st
from pandas import DataFrame
import pandas as pd
from enum import Enum
import plotly.graph_objects as go
import numpy as np
from st_aggrid import GridOptionsBuilder, ColumnsAutoSizeMode, AgGrid

# Layout changes
st.set_page_config(layout="wide")
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>

"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

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

class Mode(Enum):
    APPEND = 1
    REMOVE = 2
    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self.value == other.value
        return NotImplemented

# Global data
cur = pd.DataFrame(columns=S_COLS) # current data
mod = pd.DataFrame() # data post-AgGrid modifications
selected = None # rows selected from AgGrid
if 'storage' in st.session_state:
    cur = pd.DataFrame(st.session_state.storage)
else:
    st.session_state.storage = cur
if 'csv' not in st.session_state:
   st.session_state.csv = ''
empty_row = pd.DataFrame([["" if c != 'Amount' else 0 for c in cur.columns]], columns=cur.columns)

# Callback Functions
def initialize_df():
    global cur
    cur = pd.DataFrame(columns=S_COLS)
    st.session_state.storage = cur

def load_sample():
    global cur
    cur = SAMPLE
    st.session_state.storage = cur

def mutate(rows: DataFrame, mode):
    if mode not in Mode:
        raise ValueError('Invalid mode')
    global mod
    if mod.empty:
        global cur
        if mode == Mode.APPEND:
            cur = pd.concat([cur, rows])
        elif mode == Mode.REMOVE:
            cur = pd.merge(cur, rows, how='outer', indicator=True).query("_merge != 'both'").drop('_merge', axis=1).reset_index(drop=True)
        st.session_state.storage = cur
    else:
        temp = pd.DataFrame()
        if mode == Mode.APPEND:
            temp = pd.concat([mod, rows])
        elif mode == Mode.REMOVE:
            temp = pd.merge(mod, rows, how='outer', indicator=True).query("_merge != 'both'").drop('_merge', axis=1).reset_index(drop=True)
        st.session_state.storage = temp

def convert_to_csv():
    global mod
    if mod.empty:
        global cur
        data = cur
    else:
        data = mod
    st.session_state.csv = data.to_csv(index=False).encode('utf-8')

# Streamlit componenets
st.header("It's a Good Day for Budgeting!")
data_tab, insights_tab, about_tab = st.tabs(['Data', 'Insights', 'About'])

with st.sidebar:
    upload = st.file_uploader('Upload budget CSV', 'csv')
    if upload is not None:
        dataframe = pd.read_csv(upload)
        add = st.button('Add rows', on_click=mutate, args=[dataframe, Mode.APPEND]) # type: ignore
        if add:
            st.success('Rows added!', icon="✅")

    buffer1, buffer2 = st.empty(), st.empty()
    buffer1.text('')
    buffer2.text('')
    name = st.text_input('Download File Name', value='budget')
    ready = st.button('Prepare Budget for Download!', on_click=convert_to_csv)
    if ready:
        file_name = name + '.csv'
        st.download_button(
            label=f'Download "{file_name}"',
            data=st.session_state.csv,
            file_name=file_name,
            mime='text/csv',
    )

with data_tab:
    if cur.empty:
        st.dataframe(pd.DataFrame(columns=S_COLS))
    else:
        gb = GridOptionsBuilder.from_dataframe(cur)
        gb.configure_default_column(editable=True, groupable=True)
        gb.configure_column(field='Amount', header_name='Amount', type=['numericColumn', 'numberColumnFilter', 'customCurrencyFormat'], custom_currency_symbol='$')
        gb.configure_selection(selection_mode='multiple', use_checkbox=True, suppressRowDeselection=True, suppressRowClickSelection=True)
        modified_grid = AgGrid(cur, gridOptions=gb.build(), columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW)
        mod = modified_grid['data']
        cur = mod
        selected = pd.DataFrame(modified_grid['selected_rows'])
        if not selected.empty:
            selected = selected.drop('_selectedRowNodeInfo', axis=1)
    left, cent_left, cent_right, _, right = st.columns([1,1,1,2,1], gap="medium")

    with left:
        st.button('Delete Selection', use_container_width=True, on_click=mutate, args=[selected, Mode.REMOVE]) # type: ignore

    with cent_left:
        st.button('Clear Table', use_container_width=True, on_click=initialize_df)

    with cent_right:
        st.button('Add empty row', use_container_width=True, on_click=mutate, args=[empty_row, Mode.APPEND]) # type: ignore

    with right:
        st.button('Load Sample', use_container_width=True, on_click=load_sample)

with insights_tab:
    left, buff, right = st.columns([2,1,3])
    if not cur.empty:
        with left: # Bar graph of Income and Allocated Expenses
            bar_data = {'Income': [], 'Expenses': []}
            accounts = np.unique((cur[(cur['Category'] == 'Income')]['Allocation'])).tolist()
            for account in accounts:
                account = str(account)
                inc_des_amt = cur[(cur['Category'] == 'Income') & (cur['Allocation'] == account)]
                tot_income = inc_des_amt['Amount'].sum()
                income_names = np.unique(inc_des_amt['Description']).tolist()
                tot_expenses = 0.0
                for name in income_names:
                    name = str(name)
                    tot_expenses = tot_expenses + cur[(cur['Allocation'] == name)]['Amount'].sum()
                bar_data['Income'] += [tot_income]
                bar_data['Expenses'] += [tot_expenses]
            if len(bar_data['Income']) > 0:
                st.bar_chart(pd.DataFrame.from_dict(bar_data, orient='index', columns=accounts), height=480)

        with right: # Sankey Chart of Income to Total Income to Expense Categories
            s, t, v = 'source', 'target', 'value'
            s_t_v_data = []
            inc_des_amt = cur[(cur['Category'] == 'Income')].loc[:, ['Description', 'Amount']]
            for description, amount in zip(inc_des_amt['Description'].tolist(), inc_des_amt['Amount'].tolist()):
                s_t_v_data.append({s: description, t: 'Total Income', v: amount})
            exp_cat_amt = cur[(cur['Category'] != 'Income')].loc[:, ['Category', 'Amount']]
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
                fig.update_layout(margin=dict(l=0, r=0, t=5, b=30))
                st.plotly_chart(fig, use_container_width=True)

# Debugging
# st.write("Session State", st.session_state)
