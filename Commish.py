import streamlit as st
from dotenv import load_dotenv
import os
from backend.database import get_db
from backend.models.pool import Pool

# # Load environment variables
# load_dotenv()
# postgresql = os.environ.get("postgresql")

# # set basic page config
# st.set_page_config(page_title="Commish",
#                     page_icon='assets/app_icons/favicon.ico',
#                     layout='wide',
#                     initial_sidebar_state='expanded')

# # apply custom css styles
# with open('assets/css/style.css') as css:
#     st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)


db = next(get_db())
print(db.query(Pool).all())