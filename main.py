import streamlit as st
import sys
from os.path import basename
from os.path import dirname
import os
import pandas as pd
from PIL import Image
sys.path.append(dirname("src/"))
import ImageDB

show_image = 20
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

@st.cache_resource
def load_db():
    return ImageDB.ImageDB()

# def do_query(q):
#     print(q)

imdb = load_db()

# col1, col2 = st.columns([0.7, 0.3])

result = {}

image_file = st.sidebar.file_uploader(label="Upload Sample Image", type=['png','jpeg','jpg'])
st.sidebar.write("Image will be available in sample directory (sample/filename)")

if image_file is not None:
    file_details = {"FileName":image_file.name,"FileType":image_file.type}
    with open(os.path.join("sample",image_file.name),"wb") as f: 
      f.write(image_file.getbuffer())

# with col1:
    # st.header("Query")
st.header("Image Database")
query = st.text_area(label="Query", height=300, placeholder="Input Query Here")
if query != "":
    result = imdb.query(query)
    # print(result)
# st.button("Run", on_click=lambda: do_query(query))
st.button("Run")
st.header("Results")
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
elif result.get('type') == "SHOWIMAGE":
    st.info(f"Showing {show_image} from {len(result['data'])} images in Database")
    # table = pd.DataFrame(result['data'])
    # st.write(table)
elif result.get('type') == "ERROR":
    st.error(result['error'])
elif result.get('type') is not None:
    st.info(result['data'])

# with col2:
if result.get('type') == "SELECT":
    st.header("Images")
    n_col = 5
    im_cols = st.columns(n_col)
    i = 0
    for d in result['data']:
        col = im_cols[i]
        im = Image.open(d['path'])
        im = im.resize((225, 225))
        col.image(im, use_column_width='always')
        col.write(basename(d['path']))
        i += 1
        i = i % n_col

if result.get('type') == "SHOWIMAGE":
    st.header("Images")
    n_col = 5
    im_cols = st.columns(n_col)
    i = 0
    for d in result['data'][:show_image]:
        col = im_cols[i]
        im = Image.open(d)
        im = im.resize((225, 225))
        col.image(im, use_column_width='always')
        col.write(basename(d))
        i += 1
        i = i % n_col

# print(query)

