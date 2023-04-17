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

st.markdown(page_bg_img, unsafe_allow_html=True)
# Fxn Make Execution
def sql_executor(raw_code):
	c.execute(raw_code)
	data = c.fetchall()
	return data 


city = ['ID,', 'Name,', 'CountryCode,', 'District,', 'Population']
country = ['Code,', 'Name,', 'Continent,', 'Region,', 'SurfaceArea,', 'IndepYear,', 'Population,', 'LifeExpectancy,', 'GNP,', 'GNPOld,', 'LocalName,', 'GovernmentForm,', 'HeadOfState,', 'Capital,', 'Code2']
countrylanguage = ['CountryCode,', 'Language,', 'IsOfficial,', 'Percentage']
cluster_id="0"
cluster_id2="0"
                

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
    st.markdown("# Upload CSV Data to Table")
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
    sqlite_dbs = [file.endswith('.db')]
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
def main():
	st.title("SQLSpace")
	
	with st.sidebar:
    		choice = option_menu("SQLSPACE", ["Sign Up","Sign In"], 
        	icons=['person','key'], menu_icon="server", default_index=1,orientation="horizontal")
    	
	#menu = ["Home","About"]
	#choice = st.sidebar.selectbox("Menu",menu)

	if choice == "Home":
		st.subheader("HomePage")

		# Columns/Layout
		col1,col2 = st.beta_columns(2)

		with col1:
			with st.form(key='query_form'):
				raw_code = st.text_area("SQL Code Here")
				submit_code = st.form_submit_button("Execute")

			# Table of Info

			with st.beta_expander("Table Info"):
				table_info = {'city':city,'country':country,'countrylanguage':countrylanguage}
				st.json(table_info)
			
		# Results Layouts
		with col2:
			if submit_code:
				st.info("Query Submitted")
				st.code(raw_code)

				# Results 
				query_results = sql_executor(raw_code)
				with st.beta_expander("Results"):
					st.write(query_results)

				with st.beta_expander("Pretty Table"):
					query_df = pd.DataFrame(query_results)
					st.dataframe(query_df)


	elif choice =="Sign In":
		#st.subheader("About")
		username = st.text_input("Username")
		password = st.text_input("Password",type='password')
  
		if st.checkbox("Login"):
			create_usertable()
			result = login_user(username,password)
			# result = login_user_unsafe(username,password)
			# if password == "12345":
            
			if result:
				st.success("Logged In as {}".format(username))
				with st.sidebar:
                        		choicee = option_menu( menu_title=None,options=["Cluster","Database","Table", 'Query','Cluster Admin'],
        		        	icons=['people',"server",'table', 'code','widget'],default_index=1,orientation="vertical")
                		
				if choicee == "Cluster":
					
					st.title("Create Cluster")
					cluster_id=st.text_input
					st.info(cluster_id)
					if cluster_id:
					    cluster_id2=st.text_input
					    st.info(cluster_id2)

					    


				elif choicee =="Database":
					create_database()
				    

				elif choicee =="Table":
					upload_data()
					run_query()
				              

				else:
					run_query()
				    

				    

				
			else:
				st.warning("Incorrect Username/Password")

	else:
		st.subheader("Create An Account")
		new_username = st.text_input("User name")
		new_password = st.text_input("Password",type='password')
		confirm_password = st.text_input('Confirm Password',type='password')

		if new_password == confirm_password:
			st.success("Valid Password Confirmed")
		else:
			st.warning("Password not the same")

		if st.button("Sign Up"):
			create_usertable()
			add_userdata(new_username,new_password)
			st.success("Successfully Created an Account")



if __name__ == '__main__':
	main()

