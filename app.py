import streamlit as st
import pandas as pd

st.markdown('# Good Day')

with st.sidebar:
    upload = st.file_uploader('Upload a CSV', 'csv')
    if upload is not None:
        df = pd.read_csv(upload)
        st.dataframe(df)
