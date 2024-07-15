import streamlit as st
import pandas as pd
from backend.models.payout import get_payouts

@st.cache_data(ttl=60, show_spinner=False)
def get_cached_payouts():
    return get_payouts()

# Assuming get_payouts returns a list of dictionaries or a pandas DataFrame
payouts_data = get_cached_payouts()

# If get_payouts returns a list of dictionaries
if isinstance(payouts_data, list):
    payouts_df = pd.DataFrame(payouts_data)
else:
    payouts_df = payouts_data

# Display the DataFrame in Streamlit
st.dataframe(payouts_df)
