import streamlit as st
import pandas as pd
import importlib

from backend.database import get_db
from backend.models.pool import Pool
from backend.models.league import League
from backend.models.user import User

db = next(get_db())

@st.cache_data(ttl=3600)
def get_pools():
    pools = (
        db.query(Pool)
        .distinct(Pool.label, Pool.pool_type)
        .filter(Pool.pool_subtype.in_(["season", "season_cumulative", "season_high"]))
        .order_by(Pool.pool_type)
        .all()
    )
    return pools

def get_leaderboard(_selected_pool):
    leaderboard = _selected_pool.get_leaderboard()
    leaderboard_df = pd.DataFrame(leaderboard)
    # Add a rank column to the DataFrame
    leaderboard_df = leaderboard_df.reset_index(drop=True)  # Reset the index
    try:
        leaderboard_df["rank"] = leaderboard_df["score"].rank(
            method="dense", ascending=False
        )
    except:
        pass

    user_info_df = pd.DataFrame([user.to_dict() for user in db.query(User).all()])

    # Merge leaderboard DataFrame with user information DataFrame
    leaderboard_df = leaderboard_df.merge(
        user_info_df[["username", "name"]],
        how="left",
        left_on="username",
        right_on="username",
    )

    return st.dataframe(
        leaderboard_df,
        use_container_width=True,
        hide_index=True,
        height=(12 + 1) * 35 + 3,
        column_order=(
            "rank",
            "name",
            "week",
            "player_name",
            "position",
            "opponent",
            "score",
            "wins",
            "losses",
            "ties",
        ),
        column_config={
            "rank": "Rank",
            "name": "Owner",
            "week": "Week",
            "player_name": "Player Name",
            "position": "Player Position",
            "opponent": "Opponent",
            "score": "Score",
            "wins": "Wins",
            "losses": "Losses",
            "ties": "Ties",
        },
    )


def main():
    st.header(f"Leaderboards")
    pools = get_pools()
    pool_labels = [pool.label for pool in pools]
    selected_pool_label = st.selectbox("Select a pool", pool_labels)
    selected_pool = next(
        (pool for pool in pools if pool.label == selected_pool_label), None
    )
    selected_pool.league = (
        db.query(League).filter(League.league_id == selected_pool.league_id).first()
    )
    with st.spinner('Crunching numbers...'):
        get_leaderboard(selected_pool)


if __name__ == "__main__":
    main()
