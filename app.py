import streamlit as st
from pandas import DataFrame
import pandas as pd
from enum import Enum
import plotly.graph_objects as go
import numpy as np
import friendlywords as fw
from st_aggrid import GridOptionsBuilder, ColumnsAutoSizeMode, JsCode, AgGrid

# Layout changes
st.set_page_config(layout="wide")
hide_streamlit_style = '''
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.block-container {
    padding-top: 1rem;
}
</style>

'''
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Constants
S_COLS = ('Day', 'Description', 'Category', 'Amount', 'Allocation', 'Automatic', 'Paid', 'Cleared')
S_DATA = [(1, 'Paycheck 1', 'Income', 2000.59, 'ABC Bank', 'True', 'False', 'True'),
          (2, 'Rent', 'Housing', 1000, 'Paycheck 1', 'False', 'True', 'True'),
          (2, 'Electric', 'Housing', 205.42, 'Paycheck 1', 'False', 'False', 'False'),
          (7, 'Paycheck 2', 'Income', 500, 'Ameri-bank', 'True', 'False', 'False'),
          (12, 'Doctor appt.', 'Medical', 60, 'Paycheck 2', 'False', 'False', 'False'),
          (14, 'Car payment', 'Loans', 300, 'Paycheck 1', 'True', 'False', 'False'),
          (15, 'Walmart', 'Groceries', 150, 'Paycheck 2', 'False', 'False', 'False')]
SAMPLE = pd.DataFrame([dict(zip(S_COLS, S_DATA[i])) for i in range(len(S_DATA))])

class Mode(Enum):
    APPEND = 1
    PREPEND = 2
    REMOVE = 3
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
fw.preload() # type: ignore
lookup = dict(zip(S_COLS, [0, fw.generate(3), fw.generate(1), 0.0, ' ', 'False', 'False', 'False'])) # type: ignore
new_row = pd.DataFrame([[lookup[c] if c in lookup.keys() else ' ' for c in cur.columns]], columns=cur.columns)
column_size_mode = ColumnsAutoSizeMode.FIT_CONTENTS
if 'mode' in st.session_state:
    column_size_mode = st.session_state.mode
else:
    st.session_state.mode = column_size_mode

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
    rows['Day'] = rows['Day'].astype(int)
    rows['Amount'] = rows['Amount'].astype(float)
    if mod.empty:
        global cur
        if cur.empty:
            rows['Automatic'] = rows['Automatic'].astype(str)
            rows['Paid'] = rows['Paid'].astype(str)
            rows['Cleared'] = rows['Cleared'].astype(str)
        if mode == Mode.APPEND:
            cur = pd.concat([cur, rows])
        elif mode == Mode.PREPEND:
            cur = pd.concat([rows, cur])
        elif mode == Mode.REMOVE:
            cur = pd.merge(cur, rows, how='outer', indicator=True).query("_merge != 'both'").drop('_merge', axis=1).reset_index(drop=True)
        st.session_state.storage = cur
    else:
        mod['Day'] = mod['Day'].astype(int)
        mod['Amount'] = mod['Amount'].astype(float)
        temp = pd.DataFrame()
        if mode == Mode.APPEND:
            temp = pd.concat([mod, rows])
        elif mode == Mode.PREPEND:
            temp = pd.concat([rows, mod])
        elif mode == Mode.REMOVE:
            temp = pd.merge(mod, rows, how='outer', indicator=True).query("_merge != 'both' & _merge != 'right_only'").drop('_merge', axis=1).reset_index(drop=True)
        st.session_state.storage = temp

def convert_to_csv():
    global mod
    if mod.empty:
        global cur
        data = cur
    else:
        data = mod
    data['Day'] = data['Day'].astype(int)
    st.session_state.csv = data.sort_values('Day').to_csv(index=False).encode('utf-8')

def switch_size_mode():
    global column_size_mode
    if column_size_mode == ColumnsAutoSizeMode.FIT_CONTENTS:
        column_size_mode = ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW
    elif column_size_mode == ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW:
        column_size_mode = ColumnsAutoSizeMode.FIT_CONTENTS
    st.session_state.mode = column_size_mode

# Streamlit componenets
st.header("It's a Good Day for Budgeting! :slightly_smiling_face:")
data_tab, insights_tab, about_tab = st.tabs(['Data', 'Insights', 'About'])

with st.sidebar:
    upload = st.file_uploader('Upload budget CSV', 'csv')
    if upload is not None:
        dataframe = pd.read_csv(upload)
        add = st.button('Add rows', use_container_width=True, on_click=mutate, args=[dataframe, Mode.APPEND]) # type: ignore
        if add:
            st.success('Rows added!', icon="✅")

    st.markdown('---')
    name = st.text_input('Download File Name', value='budget')
    ready = st.button('Prepare Budget for Download!', use_container_width=True, on_click=convert_to_csv)
    if ready:
        file_name = name + '.csv'
        st.download_button(label=f'Download "{file_name}"', use_container_width=True, data=st.session_state.csv, file_name=file_name, mime='text/csv')

with data_tab:
    if cur.empty:
        st.dataframe(pd.DataFrame(columns=S_COLS))
    else:
        gb = GridOptionsBuilder.from_dataframe(cur)
        gb.configure_pagination(paginationAutoPageSize=False)
        gb.configure_default_column(editable=True)
        gb.configure_column(field='Amount', type=['numericColumn', 'numberColumnFilter', 'customCurrencyFormat'], custom_currency_symbol='$')
        cb_renderer = JsCode("""
        class CBRenderer {
            init(params) {
                this.params = params;
                this.eGui = document.createElement('input');
                this.eGui.type = 'checkbox';
                this.eGui.checked = params.value == 'True' || params.value == true;
                this.checkedHandler = this.checkedHandler.bind(this);
                this.eGui.addEventListener('click', this.checkedHandler);
            }

            checkedHandler(e) {
                let checked = e.target.checked;
                let colId = this.params.column.colId;
                this.params.node.setDataValue(colId, checked);
            }

            getGui() {
                return this.eGui;
            }

            destroy() {
                this.eGui.removeEventListener('click', this.checkedHandler);
            }
        }
        """)
        gb.configure_columns(column_names=['Automatic', 'Paid', 'Cleared'], cellRenderer=cb_renderer)
        income_checker = JsCode("""
        class IncomeChecker {
            init(params) {
                this.eGui = document.createElement('span');
                this.eGui.innerHTML = this.getInnerHtml(params.value);
            }

            getGui(params) {
                return this.eGui;
            }

            refresh(params) {
                this.eGui.innerHTML = this.getInnerHtml(params.value);
                return true;
            }

            getInnerHtml(value) {
                if (value == 'Income') {
                    return `<span style="background-color:palegreen">${value}</span>`;
                }
                return `<span>${value}</span>`;
            }
        }
        """)
        gb.configure_column(field='Category', cellRenderer=income_checker)
        gb.configure_selection(selection_mode='multiple', use_checkbox=True, suppressRowDeselection=True, suppressRowClickSelection=True)
        grid_options = gb.build()
        row_coloring = JsCode("""
        function(params) {
            if (params.rowIndex % 2 == 1) {
                return {
                    'backgroundColor': 'whitesmoke'
                }
            }
        };
        """)
        grid_options['getRowStyle'] = row_coloring
        modified_grid = AgGrid(cur, gridOptions=grid_options, columns_auto_size_mode=column_size_mode, enable_enterprise_modules=False, allow_unsafe_jscode=True)
        mod = modified_grid['data']
        cur = mod
        selected = pd.DataFrame(modified_grid['selected_rows'])
        if not selected.empty:
            selected['Day'] = selected['Day'].astype(int)
            selected['Amount'] = selected['Amount'].astype(float)
            selected = selected.drop('_selectedRowNodeInfo', axis=1)
    left, cent, _, right = st.columns([1,1,2,1], gap="medium")

    with left:
        disabled = selected is None or selected.empty
        st.button('Delete Selection', use_container_width=True, disabled=disabled, on_click=mutate, args=[selected, Mode.REMOVE]) # type: ignore
        st.checkbox('Fit Columns to Screen', on_change=switch_size_mode)

    with cent:
        st.button('Add New Row', use_container_width=True, on_click=mutate, args=[new_row, Mode.PREPEND]) # type: ignore

    with right:
        st.button('Clear Table', use_container_width=True, type='primary', on_click=initialize_df)
        st.button('Load Sample', use_container_width=True, type='primary', on_click=load_sample)

with insights_tab:
    left, buff, right = st.columns([2,1,3])
    if not cur.empty:
        with left: # Bar graph of Income and Allocated Expenses
            bar_data = {'Income': [], 'Expenses': []}
            stores = np.unique((cur[(cur['Category'] == 'Income')]['Allocation'])).tolist()
            for store in stores:
                store = str(store)
                incomes = cur[(cur['Category'] == 'Income') & (cur['Allocation'] == store)]
                tot_income = incomes['Amount'].sum()
                income_names = np.unique(incomes['Description']).tolist()
                tot_expenses = 0.0
                for name in income_names:
                    name = str(name)
                    tot_expenses = tot_expenses + cur[(cur['Category'] != 'Income') & (cur['Allocation'] == name)]['Amount'].sum()
                bar_data['Income'] += [tot_income]
                bar_data['Expenses'] += [tot_expenses]
            if len(bar_data['Income']) > 0:
                st.bar_chart(pd.DataFrame.from_dict(bar_data, orient='index', columns=stores), height=480)

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

with about_tab:
    st.markdown('Budgeteer documentation coming soon!')
    st.markdown('Currently serving `v0.11.0`')

# Debugging
# st.write("Session State", st.session_state)
