import streamlit as st
from loguru import logger
from dawndungeon.api.story import StoryManager
from dawndungeon.db.mongodb.entities.world import World
from dawndungeon import mongodb
from google.oauth2 import id_token
from google.auth.transport import requests
from dawndungeon import config
from dawndungeon.api.streamlit_auth import *

st.title("⛓️🔗DawnDungeon")

if "auth" not in st.session_state:
    st.subheader("Authentication")
    st.markdown(f"[Click me to authenticate!]({get_auth_url()})")

    if "code" in st.experimental_get_query_params():
        id_, email = get_user_details()
        st.session_state["auth"] = {
            "id": id_,
            "email": email,
        }
        st.experimental_rerun()
    else:
        st.stop()

st.sidebar.subheader(f"Welcome {st.session_state['auth']['email']} to our dungeon!")

if "session" not in st.session_state:
    with st.spinner("Initializing..."):
        st.session_state["session"] = StoryManager(
            # TODO: Get this from the database.
            mongodb.get_world(random=True),
            mongodb.get_user(username="victor"),
        )
        st.session_state["session"].execute()

session: StoryManager = st.session_state["session"]
st.write(session.get_storylines())
prompt: str = st.text_input("Action")

if prompt:
    with st.spinner("Executing..."):
        result: dict = session.execute(action=prompt)
    st.write(result["content"])

metadata: dict = session.get_latest_metadata()

with st.sidebar:
    logger.info("Generating Character metadata panel...")
    character: dict = metadata["character"]
    for key, value in character.items():
        st.info(f"{key.title()}:\n\n{value}")

with st.expander("World"):
    logger.info("Generating World metadata panel...")
    world: dict = metadata["world"]
    for key, value in world.items():
        st.info(f"{key.title()}:\n\n{value}")

with st.expander("Developer"):
    st.info(session.memory.buffer)
