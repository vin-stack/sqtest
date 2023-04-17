# Core Pkgs
import streamlit as st 
import base64
import pandas as pd
from streamlit_option_menu import  option_menu
import os
# DB Mgm
import sqlite3 
from db_fxns import *
conn = sqlite3.connect('data/world.sqlite')
c = conn.cursor()

def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


img = get_img_as_base64("image.jpg")

page_bg_img = f"""
<style>


[data-testid="stSidebar"] > div:first-child {{
background-image: url("https://d2gg9evh47fn9z.cloudfront.net/1600px_COLOURBOX11140963.jpg");
background-position: left; 
background-repeat: no-repeat;
background-attachment: local;
}}

[data-testid="stHeader"] {{
background: rgba(0,0,0,0);
}}

[data-testid="stToolbar"] {{
right: 2rem;
}}
</style>
"""
st.title("SQLSpace")
st.markdown(page_bg_img, unsafe_allow_html=True)
# Fxn Make Execution
def sql_executor(raw_code):
	c.execute(raw_code)
	data = c.fetchall()
	return data 


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Exception as e:
        st.write(e)

    return conn


def create_database():
    st.markdown("# Create Database")

    st.write("""A database in SQLite is just a file on same server. 
    By convention their names always end in .db""")


    db_filename = st.text_input("DB Filename")
    create_db = st.button('Create Database')

    if create_db:
        if db_filename.endswith('.db'):
            conn = create_connection(db_filename)
            st.write(conn) # success message?
        else: 
            st.write('DB filename must end with .db, please retry.')


def upload_data():
    st.markdown("# Upload Data")
    # https://discuss.streamlit.io/t/uploading-csv-and-excel-files/10866/2
    sqlite_dbs = [file for file in os.listdir('.') if file.endswith('.db')]
    db_filename = st.selectbox('DB Filename', sqlite_dbs)
    table_name = st.text_input('Table Name to Insert')
    conn = create_connection(db_filename)
    uploaded_file = st.file_uploader('Choose a file')
    if uploaded_file is not None:
        #read csv
        try:
            df = pd.read_csv(uploaded_file)
            df.to_sql(name=table_name, con=conn)
            st.write('Data uploaded successfully. These are the first 5 rows.')
            st.dataframe(df.head(5))

        except Exception as e:
            st.write(e)


def run_query():
    st.markdown("# Run Query")
    sqlite_dbs = [file for file in os.listdir('.') if file.endswith('.db')]
    db_filename = st.selectbox('DB Filename', sqlite_dbs)

    query = st.text_area("SQL Query", height=100)
    conn = create_connection(db_filename)

    submitted = st.button('Run Query')

    if submitted:
        try:
            query = conn.execute(query)
            cols = [column[0] for column in query.description]
            results_df= pd.DataFrame.from_records(
                data = query.fetchall(), 
                columns = cols
            )
            st.dataframe(results_df)
        except Exception as e:
            st.write(e)

    st.sidebar.markdown("# Run Query")

page_names_to_funcs = {
    "Create Database": create_database,
    "Upload Data": upload_data,
    "Run Query": run_query,
}

selected_page = st.sidebar.selectbox("Select a page", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]()
