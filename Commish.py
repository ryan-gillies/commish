import streamlit as st
from dotenv import load_dotenv
import os
from backend.database import get_db
from backend.models.pool import Pool

db = next(get_db())


# Load environment variables
load_dotenv()
postgresql = os.environ.get("postgresql")

# set basic page config
st.set_page_config(page_title="Commish",
                    layout='wide',
                    initial_sidebar_state='expanded')

# apply custom css styles
with open('assets/css/style.css') as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def get_pools():
    pools = (
        db.query(Pool)
        .distinct(Pool.label, Pool.pool_type)
        .order_by(Pool.pool_type)
        .all()
    )
    return pools

def main():
    st.title("Defending Champion")
    st.header("Christian Wagner")
    pools = get_pools()
    for pool in pools:
        st.columns(3)
        st.metric(pool.label, float(pool.payout_amount))
    st.balloons()

if __name__ == "__main__":
    main()