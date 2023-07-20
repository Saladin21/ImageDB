import streamlit as st
import sys
from os.path import basename
from os.path import dirname
import pandas as pd
sys.path.append(dirname("src/"))
import ImageDB

st.set_page_config(layout="wide")

@st.cache_resource
def load_db():
    return ImageDB.ImageDB()

# def do_query(q):
#     print(q)

imdb = load_db()

col1, col2 = st.columns([0.7, 0.3])

result = {}

with col1:
    # st.header("Query")
    query = st.text_area(label="Query", height=300, placeholder="Input Query Here")
    if query != "":
        result = imdb.query(query)
        print(result)
    # st.button("Run", on_click=lambda: do_query(query))
    st.write("Result")
    if result.get('type') == "SELECT":
        st.info(f"{len(result['data'])} images retrieved in {result['time']} s")
        table = pd.DataFrame(result['data'])
        st.write(table)
    elif result.get('type') == "SHOWDB":
        st.info(f"{len(result['data'])} Database found")
        table = pd.DataFrame(result['data'])
        table.rename(columns={0:'Database'}, inplace=True)
        st.write(table)
    elif result.get('type') == "SHOWTABLE":
        st.info(f"{len(result['data'])} Table found")
        table = pd.DataFrame(result['data'])
        st.write(table)
    elif result.get('type') == "SHOWFEATURE":
        st.info(f"{len(result['data'])} features found")
        table = pd.DataFrame(result['data'])
        st.write(table)
    elif result.get('type') == "SHOWINDEX":
        st.info(f"{len(result['data'])} index found")
        table = pd.DataFrame(result['data'])
        table.rename(columns={0:'Index'}, inplace=True)
        st.write(table)
    elif result.get('type') == "ERROR":
        st.error(result['error'])
    elif result.get('type') is not None:
        st.info(result['data'])
with col2:
    if result.get('type') == "SELECT":
        st.header("Image results")
        for d in result['data']:
            st.write(basename(d['path']))
            st.image(d['path'], width=300)

# print(query)

