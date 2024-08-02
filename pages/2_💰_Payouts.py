import streamlit as st
import pandas as pd
import altair as alt
from backend.models.payout import get_user_payouts, get_payout_details
# from utils.css_utils import load_color_scheme_from_css

# Constants
CACHE_TTL = 3600  # 1 hour

@st.cache_data(ttl=CACHE_TTL)
def get_cached_user_payouts(season):
    return get_user_payouts(season)


def prepare_user_payouts_data(season):
    payouts_data = get_cached_user_payouts(season)
    payouts_df = pd.DataFrame(payouts_data)
    payouts_df = payouts_df.sort_values(by='amount', ascending=False)
    return payouts_df


def create_user_payouts_chart(payouts_df, color_scheme, season=None):
    chart = alt.Chart(payouts_df).mark_bar().encode(
        x=alt.X('amount', axis=alt.Axis(title='Total Payouts', format='$,.0f')),
        y=alt.Y('name', sort='-x', axis=alt.Axis(title='User')),
        color=alt.Color('pool_type', sort=list(color_scheme.keys()),
                        scale=alt.Scale(domain=list(color_scheme.keys()),
                                        range=list(color_scheme.values())))
    ).properties(
    )
    return chart


def main():
    seasons = ['All Time', '2023', '2022']  # Replace with your actual season options
    selected_season = st.selectbox('Select a season', seasons)
    st.header(f'Payouts - {selected_season}')


    if selected_season == 'All Time':
        selected_season = None
    else:
        selected_season
    payouts_df = prepare_user_payouts_data(selected_season)
    color_scheme = {
        'main': '#1c6866',
        'side': '#70afb8',
    }

    chart = create_user_payouts_chart(payouts_df, color_scheme, selected_season)

    st.altair_chart(chart, use_container_width=True)

    payout_details = get_payout_details(selected_season)
    payout_details_df = pd.DataFrame(payout_details)
    st.dataframe(payout_details_df, use_container_width=True)


if __name__ == "__main__":
    main()
