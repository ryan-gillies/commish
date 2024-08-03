import streamlit as st
import pandas as pd
import altair as alt
from sqlalchemy import func, distinct

from backend.database import get_db
from backend.models.payout import get_user_payouts, get_payout_details
from backend.models.league import League
from backend.models.pool import Pool

# from utils.css_utils import load_color_scheme_from_css

# Constants
CACHE_TTL = 3600  # 1 hour


@st.cache_data(ttl=CACHE_TTL)
def get_cached_user_payouts(season):
    return get_user_payouts(season)


def prepare_user_payouts_data(season):
    payouts_data = get_cached_user_payouts(season)
    payouts_df = pd.DataFrame(payouts_data)
    payouts_df = payouts_df.sort_values(by="amount", ascending=False)
    return payouts_df


def create_user_payouts_chart(payouts_df, color_scheme, season=None):
    chart = (
        alt.Chart(payouts_df)
        .mark_bar()
        .encode(
            x=alt.X("amount", axis=alt.Axis(title="Total Payouts", format="$,.0f")),
            y=alt.Y("name", sort="-x", axis=alt.Axis(title="User")),
            color=alt.Color(
                "pool_type",
                sort=list(color_scheme.keys()),
                scale=alt.Scale(
                    domain=list(color_scheme.keys()), range=list(color_scheme.values())
                ),
            ),
        )
        .properties()
    )
    chart = st.altair_chart(chart, use_container_width=True)
    return chart


@st.cache_data(ttl=CACHE_TTL)
def get_cached_payout_details(season):
    return get_payout_details(season)


def prepare_payout_details_data(season):
    payouts_data = get_cached_payout_details(season)
    payouts_df = pd.DataFrame(payouts_data)
    payouts_df = st.dataframe(payouts_df, use_container_width=True, hide_index=True)
    return payouts_df


def main():
    db = next(get_db())
    seasons = db.query(League.season) \
             .join(Pool, League.league_id == Pool.league_id, isouter=True) \
             .filter(Pool.payout_amount != None) \
             .group_by(League.season) \
             .order_by(League.season.desc()) \
             .all()    
    seasons = [row.season for row in seasons]
    seasons.insert(0, "All Time")
    selected_season = st.selectbox("Select a season", seasons)
    st.header(f"Payouts - {selected_season}")

    if selected_season == "All Time":
        selected_season = None
    else:
        selected_season

    payouts_df = prepare_user_payouts_data(selected_season)
    color_scheme = {
        "main": "#1c6866",
        "side": "#70afb8",
    }
    create_user_payouts_chart(payouts_df, color_scheme, selected_season)
    prepare_payout_details_data(selected_season)


if __name__ == "__main__":
    main()
