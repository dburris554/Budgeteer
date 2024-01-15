import streamlit as st
from pandas import DataFrame
import pandas as pd
from enum import Enum
import plotly.graph_objects as go
import altair as alt
import numpy as np
import friendlywords as fw
from st_aggrid import GridOptionsBuilder, ColumnsAutoSizeMode, JsCode, AgGrid

# Layout changes
st.set_page_config(page_title='Budgeteer', page_icon='🚀', layout="wide", initial_sidebar_state='expanded')
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
SAMPLE_COLS = ('Day', 'Description', 'Category', 'Amount', 'Allocation', 'Automatic', 'Paid', 'Cleared')
SAMPLE_ROWS = [(1, 'Paycheck 1', 'Income', 2000.59, 'ABC Bank', 'True', 'False', 'True'),
          (2, 'Rent', 'Housing', 1000, 'Paycheck 1', 'False', 'True', 'True'),
          (2, 'Electric', 'Housing', 205.42, 'Paycheck 1', 'False', 'False', 'False'),
          (7, 'Paycheck 2', 'Income', 500, 'Ameri-bank', 'True', 'False', 'False'),
          (12, 'Doctor appt.', 'Medical', 60, 'Paycheck 2', 'False', 'False', 'False'),
          (14, 'Car payment', 'Loans', 300, 'Paycheck 1', 'True', 'False', 'False'),
          (15, 'Walmart', 'Groceries', 150, 'Paycheck 2', 'False', 'False', 'False')]
SAMPLE = pd.DataFrame([dict(zip(SAMPLE_COLS, SAMPLE_ROWS[i])) for i in range(len(SAMPLE_ROWS))])

class DataFrameMutateMode(Enum):
    APPEND = 1
    PREPEND = 2
    REMOVE = 3
    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self.value == other.value
        return NotImplemented

# Global data
stable = pd.DataFrame(columns=SAMPLE_COLS) # initial loaded data or updated data to be the source of truth
modified = pd.DataFrame() # data post-AgGrid modifications
selected = None # rows selected from AgGrid
if 'dataframe' in st.session_state:
    stable = pd.DataFrame(st.session_state.dataframe)
else:
    st.session_state.dataframe = stable
if 'csv' not in st.session_state:
   st.session_state.csv = ''
fw.preload() # type: ignore
sample_values = dict(zip(SAMPLE_COLS, [0, fw.generate(3), fw.generate(1), 0.0, ' ', 'False', 'False', 'False'])) # type: ignore
new_row = pd.DataFrame([[sample_values[col] if col in sample_values.keys() else ' ' for col in stable.columns]], columns=stable.columns) # type: ignore
column_size_mode = ColumnsAutoSizeMode.FIT_CONTENTS
if 'size_mode' in st.session_state:
    column_size_mode = st.session_state.size_mode
else:
    st.session_state.size_mode = column_size_mode

# Callback Functions
def load_empty():
    global stable
    stable = pd.DataFrame(columns=SAMPLE_COLS)
    st.session_state.dataframe = stable
    st.session_state.size_mode = ColumnsAutoSizeMode.FIT_CONTENTS

def load_sample():
    global stable
    stable = SAMPLE
    st.session_state.dataframe = stable

def mutate(rows: DataFrame, mode: DataFrameMutateMode):
    global modified
    rows['Day'] = rows['Day'].astype(int)
    rows['Amount'] = rows['Amount'].astype(float)
    if modified.empty:
        global stable
        if stable.empty:
            rows['Automatic'] = rows['Automatic'].astype(str)
            rows['Paid'] = rows['Paid'].astype(str)
            rows['Cleared'] = rows['Cleared'].astype(str)
        if mode == DataFrameMutateMode.APPEND:
            stable = pd.concat([stable, rows])
        elif mode == DataFrameMutateMode.PREPEND:
            stable = pd.concat([rows, stable])
        elif mode == DataFrameMutateMode.REMOVE:
            stable = pd.merge(stable, rows, how='outer', indicator=True).query("_merge != 'both'").drop('_merge', axis=1).reset_index(drop=True)
        st.session_state.dataframe = stable
    else:
        modified['Day'] = modified['Day'].astype(int)
        modified['Amount'] = modified['Amount'].astype(float)
        if mode == DataFrameMutateMode.APPEND:
            st.session_state.dataframe = pd.concat([modified, rows])
        elif mode == DataFrameMutateMode.PREPEND:
            st.session_state.dataframe = pd.concat([rows, modified])
        elif mode == DataFrameMutateMode.REMOVE:
            st.session_state.dataframe = pd.merge(modified, rows, how='outer', indicator=True).query("_merge != 'both' & _merge != 'right_only'").drop('_merge', axis=1).reset_index(drop=True)

def convert_to_csv():
    global modified
    global stable
    if not modified.empty:
        stable = modified
    stable['Day'] = stable['Day'].astype(int)
    st.session_state.csv = stable.sort_values('Day').to_csv(index=False).encode('utf-8')

def switch_size_mode():
    global column_size_mode
    global stable
    if column_size_mode == ColumnsAutoSizeMode.FIT_CONTENTS:
        column_size_mode = ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW
    elif column_size_mode == ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW:
        column_size_mode = ColumnsAutoSizeMode.FIT_CONTENTS
    st.session_state.size_mode = column_size_mode
    st.session_state.dataframe = stable

# Streamlit componenets
st.header('Welcome fellow Budgeteer! :wave:')
data_tab, insights_tab, about_tab = st.tabs(['Data', 'Insights', 'About'])

with st.sidebar:
    default_file_name = 'budget'
    upload = st.file_uploader('Upload budget CSV', 'csv')
    if upload is not None:
        default_file_name = upload.name[:upload.name.find('.')]
        dataframe = pd.read_csv(upload)
        add = st.button('Add rows', use_container_width=True, on_click=mutate, args=[dataframe, DataFrameMutateMode.APPEND]) # type: ignore
        if add:
            st.success('Rows added!', icon='✅')

    st.markdown('---')
    name = st.text_input('Download File Name', value=default_file_name)
    ready = st.button('Create Download File!', use_container_width=True, on_click=convert_to_csv)
    if ready:
        file_name = name + '.csv'
        st.download_button(label=f'Download "{file_name}"', use_container_width=True, data=st.session_state.csv, file_name=file_name, mime='text/csv')

with data_tab:
    if stable.empty:
        st.dataframe(pd.DataFrame(columns=SAMPLE_COLS))
    else:
        gb = GridOptionsBuilder.from_dataframe(stable)
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
        grid_options['suppressHorizontalScroll'] = True
        modified_grid = AgGrid(stable, gridOptions=grid_options, columns_auto_size_mode=column_size_mode, enable_enterprise_modules=False, allow_unsafe_jscode=True)
        modified = modified_grid['data']
        stable = modified
        selected = pd.DataFrame(modified_grid['selected_rows'])
        if not selected.empty:
            selected['Day'] = selected['Day'].astype(int)
            selected['Amount'] = selected['Amount'].astype(float)
            selected = selected.drop('_selectedRowNodeInfo', axis=1)
    left, center, _, right = st.columns([1,1,2,1], gap="medium")

    with left:
        disabled = selected is None or selected.empty
        st.button('Delete Selection', use_container_width=True, disabled=disabled, on_click=mutate, args=[selected, DataFrameMutateMode.REMOVE]) # type: ignore
        st.checkbox('Fit Columns to Screen', value=column_size_mode == ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW, on_change=switch_size_mode)

    with center:
        st.button('Add New Row', use_container_width=True, on_click=mutate, args=[new_row, DataFrameMutateMode.PREPEND]) # type: ignore

    with right:
        st.button('Clear', use_container_width=True, type='primary', on_click=load_empty)
        st.button('Load Sample', use_container_width=True, type='primary', on_click=load_sample)

with insights_tab:
    stable['Amount'] = stable['Amount'].astype(float)
    stable[stable['Automatic'] == 'true']['Allocation'] = 'True'
    stable[stable['Automatic'] == 'false']['Allocation'] = 'False'
    stable[stable['Paid'] == 'true']['Paid'] = 'True'
    stable[stable['Paid'] == 'false']['Paid'] = 'False'
    stable[stable['Cleared'] == 'true']['Cleared'] = 'True'
    stable[stable['Cleared'] == 'false']['Cleared'] = 'False'
    with st.expander('**Pending Charges**'):
        if not stable.empty:
            stores = np.unique(stable[(stable['Category'] == 'Income')]['Allocation']).tolist()
            for store in stores:
                with st.container():
                    left, right = st.columns([1,2])
                    right.markdown('')
                    left.markdown(f'## {store}')
                    store_incomes = stable[(stable['Category'] == 'Income') & (stable['Allocation'] == store)]
                    store_income_names = np.unique(store_incomes['Description']).tolist()
                    didClear = [True if 'True' in store_incomes[store_incomes['Description'] == name]['Cleared'].values else False for name in store_income_names]
                    cleared_sum = 0
                    for income_name, cleared in zip(store_income_names, didClear): # type: ignore
                        rLeft, rCenter = right.columns(2, gap='medium')
                        expenses = stable[(stable['Category'] != 'Income') & (stable['Allocation'] == income_name)]
                        data_auto = expenses[(expenses['Automatic'] == 'True') & (expenses['Cleared'] == 'False')] # issue combining filters
                        data_paid = expenses[(expenses['Paid'] == 'True') & (expenses['Cleared'] == 'False')]
                        income_df = pd.concat([data_auto, data_paid])
                        income_df = income_df.loc[:, ['Day', 'Description', 'Category', 'Amount']].set_index('Day').sort_index()
                        sum = income_df['Amount'].sum()
                        income_df['Amount'] = income_df['Amount'].apply(lambda x: f'${x:,.2f}')
                        rLeft.markdown(f'### {income_name}')
                        if cleared:
                            cleared_sum += sum
                            rCenter.success('Has Cleared', icon='💲')
                        else:
                            rCenter.info('Has Not Cleared', icon='🚫')
                        right.metric(label='**Sum of Pending**', value=f'${sum:,.2f}')
                        right.dataframe(income_df, use_container_width=True)
                        if income_name != store_income_names[len(store_income_names)-1]:
                            right.markdown('---')
                            right.markdown('')
                    left.metric(label='**Total from Cleared Incomes**', value=f'${cleared_sum:,.2f}')
                if store != stores[len(stores)-1]:
                    st.markdown('---')

    st.markdown('')
    with st.expander('**Unpaid Charges**'):
        if not stable.empty:
            stores = np.unique(stable[(stable['Category'] == 'Income')]['Allocation']).tolist()
            for store in stores:
                with st.container():
                    left, right = st.columns([1,2])
                    left.markdown(f'## {store}')
                    right.markdown('')
                    store_incomes = stable[(stable['Category'] == 'Income') & (stable['Allocation'] == store)]
                    store_income_names = np.unique(store_incomes['Description']).tolist()
                    didClear = [True if 'True' in store_incomes[store_incomes['Description'] == name]['Cleared'].values else False for name in store_income_names]
                    cleared_sum = 0
                    for income_name, cleared in zip(store_income_names, didClear): # type: ignore
                        rLeft, rCenter = right.columns(2, gap='medium')
                        expenses = stable[(stable['Category'] != 'Income') & (stable['Allocation'] == income_name)]
                        income_df = expenses[(expenses['Automatic'] == 'False') & (expenses['Paid'] == 'False') & (expenses['Cleared'] == 'False')]
                        income_df = income_df.loc[:, ['Day', 'Description', 'Category', 'Amount']].set_index('Day').sort_index()
                        sum = income_df['Amount'].sum()
                        income_df['Amount'] = income_df['Amount'].apply(lambda x: f'${x:,.2f}')
                        rLeft.markdown(f'### {income_name}')
                        if cleared:
                            cleared_sum += sum
                            rCenter.success('Has Cleared', icon='💲')
                        else:
                            rCenter.info('Has Not Cleared', icon='🚫')
                        right.metric(label='**Sum of Unpaid**', value=f'${sum:,.2f}')
                        right.dataframe(income_df, use_container_width=True)
                        if income_name != store_income_names[len(store_income_names)-1]:
                            right.markdown('---')
                            right.markdown('')
                    left.metric(label='**Total from Cleared Incomes**', value=f'${cleared_sum:,.2f}')
                if store != stores[len(stores)-1]:
                    st.markdown('---')

    st.markdown('')
    with st.expander('**Income Burndowns**'):
        if not stable.empty:
            incomes = np.unique(stable[(stable['Category'] == 'Income')]['Description']).tolist()
            for income in incomes:
                with st.container():
                    left, right = st.columns([2,1])
                    left.markdown(f'## {income}')
                    right.markdown('')
                    chart_df = pd.DataFrame({'Day': [1, 1, 4, 11],
                                            'Charges': ['INCOME', 'Rent', 'Electric', 'Car payment'],
                                            'Balance': [1200, 500, 300, 200.25]}, columns=['Day', 'Charges', 'Balance'])
                    left.altair_chart(alt.Chart(chart_df).mark_line(point=True, interpolate='step-after', strokeWidth=3, strokeCap='round').encode(x='Day:O', y=alt.Y('Balance', scale=alt.Scale(padding=20, nice=100)), order='Day').interactive(), # type: ignore
                                      use_container_width=True, theme=None)
                    right.metric(label='**Total remaining**', value=f'$200.25')


    st.markdown('')
    with st.expander('**Data Exploration**'):
        left, _, right = st.columns([2,1,3])
        if not stable.empty:
            with left: # Bar graph of Income and Allocated Expenses
                with st.container():
                    bar_data = {'Income': [], 'Expenses': []}
                    stores = np.unique(stable[(stable['Category'] == 'Income')]['Allocation']).tolist()
                    for store in stores:
                        store = str(store)
                        incomes = stable[(stable['Category'] == 'Income') & (stable['Allocation'] == store)]
                        total_income = incomes['Amount'].sum()
                        income_names = np.unique(incomes['Description']).tolist()
                        total_expenses = 0.0
                        for name in income_names:
                            name = str(name)
                            total_expenses = total_expenses + stable[(stable['Category'] != 'Income') & (stable['Allocation'] == name)]['Amount'].sum()
                        bar_data['Income'] += [total_income]
                        bar_data['Expenses'] += [total_expenses]
                    if len(bar_data['Income']) > 0:
                        st.markdown('### Income Allocation')
                        st.bar_chart(pd.DataFrame.from_dict(bar_data, orient='index', columns=stores), height=480)

            with right: # Sankey Chart of Income to Total Income to Expense Categories
                with st.container():
                    source, target, value = 'source', 'target', 'value'
                    rows = []
                    income_data = stable[(stable['Category'] == 'Income')].loc[:, ['Description', 'Amount']]
                    for description, amount in zip(income_data['Description'].tolist(), income_data['Amount'].tolist()): # type: ignore
                        rows.append({source: description, target: 'Total Income', value: amount})
                    expense_data = stable[(stable['Category'] != 'Income')].loc[:, ['Category', 'Amount']]
                    categories = np.unique(expense_data['Category']).tolist()
                    for category in categories:
                        category_amount = expense_data[(expense_data['Category'] == category)]['Amount'].sum()
                        rows.append({source: 'Total Income', target: category, value: category_amount})
                    if len(rows) > 0:
                        st.markdown('### Income-Expense Distribution')
                        sankey_df = pd.DataFrame(rows)
                        nodes = np.unique(sankey_df[['source', 'target']], axis=None)
                        nodes = pd.Series(index=nodes, data=range(len(nodes)))
                        sankey = go.Sankey(node={'label': nodes.index},
                            link={'source': nodes.loc[sankey_df['source']],
                                'target': nodes.loc[sankey_df['target']],
                                'value': sankey_df['value']})
                        fig = go.Figure(data=sankey)
                        fig.update_layout(margin=dict(l=0, r=0, t=5, b=30), font_size=14)
                        st.plotly_chart(fig, use_container_width=True, theme=None)

with about_tab:
    st.markdown('Budgeteer documentation coming soon!')
    st.markdown('Currently serving `v0.13.3`')

# Debugging
# st.write("Session State", st.session_state)
