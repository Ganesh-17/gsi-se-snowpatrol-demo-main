
from datetime import datetime, timedelta
from snowflake.snowpark import Session
import snowflake.connector
import plotly.graph_objects as go
from app_data_model_1 import SnowpatrolDataModel
import json 
import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_toggle import st_toggle_switch
from streamlit_option_menu import option_menu
from streamlit_extras.stylable_container import stylable_container
from PIL import Image
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
#from sqlalchemy import URL
import pandas as pd



#################################
#
#   Utility functions
#
#################################
def build_snowpark_session(kwargs) -> Session:
    try:
        res=Session.builder.configs({
        "account": kwargs["account"],
        "user": kwargs["username"],
        "password": kwargs["password"],
        "warehouse": kwargs.get("warehouse", ""),
        "database": kwargs.get("database", ""),
        "schema": kwargs.get("schema", ""),
        "role": kwargs.get("role", "")
            }).create() 
    except:
        st.error(":warning: Incorrect login credentials")
        res = None
    return res

def connect_to_snowflake(**kwargs):
    if 'SNOWPARK_SESSION' not in st.session_state:
        if (kwargs["account"].strip() != "") & (kwargs["username"].strip() != "") & (kwargs["password"].strip() is not None):
            SNOWPARK_SESSION=build_snowpark_session(kwargs)
            st.session_state['SNOWPARK_SESSION']=SNOWPARK_SESSION
            st.info(f":+1: Connected to {SNOWPARK_SESSION.get_current_account()} as your default role - {SNOWPARK_SESSION.get_current_role()}")
        else:
            st.error(":warning: Missing fields")

@st.cache_data
def get_available_roles_for_user():
    return st.session_state['sdm'].get_available_roles()

@st.cache_data
def get_available_databases(role):
    return st.session_state['sdm'].get_available_databases(role)

@st.cache_data
def get_available_schemas(role, db):
    return st.session_state['sdm'].get_available_schemas(role, db)

@st.cache_data
def get_available_warehouses(role):
    return st.session_state['sdm'].get_available_warehouses(role)


#################################
#
#   UI Builder
#
#################################
# st.set_page_config(
#      page_title="Snowpatrol - License Optimization",
#      page_icon=":rotating_light:",
#      layout="wide",
#      initial_sidebar_state="expanded"
# )
# #st.header(":rotating_light: Snowpatrol - License Optimization")
image = Image.open("SnowPatrol.png")
with st.container() as mp:
    st.markdown('<style>div.block-container{padding-bottom :0px; padding-right :10px; padding-top :30px;padding-left :10px; margin:10px; }</style>',unsafe_allow_html=True)
    m1,m2=st.columns(2,gap="small")
    with m1:
        st.image(image,width=250 )
    with m2:
        st.markdown(
        "<div style='text-align: right; font-size: 20px; font-family: Arial; color:rgb(0,0,100); font-weight: bold; '>Export Data</div>",
        unsafe_allow_html=True,
        )
st.markdown('<hr style="margin-top: 0px; margin-bottom: 0px;">', unsafe_allow_html=True)
# with col3:
#     # st.write("")
#     st.header(":blue[OVERVIEW]")

# colored_header(
#                         label='',
#                         description="",
#                         color_name="blue-70",
#                         )

def init_session() -> Session:
    with st.form("snowflake_connection"):
        colored_header(
                label="Connect to Snowflake's Snowpatrol data source",
                description="Provide your Snowflake credentials to login",
                color_name="red-70",
        )
        account = st.text_input('Snowflake Account Identifier* : ')
        mandatory_fields_col1, mandatory_fields_col2 = st.columns(2, gap="small")        
        with mandatory_fields_col1:
            username = st.text_input('Username* : ')
        with mandatory_fields_col2:
            password = st.text_input('Password* : ', type="password")
        
        """__*must fill__"""
        connect = st.form_submit_button("Connect")

        if connect:
            connect_to_snowflake(account=account , username=username , password=password)
            session_sdm = SnowpatrolDataModel(st.session_state['SNOWPARK_SESSION'])
            st.session_state['sdm']=session_sdm


def build_UI():
    image = Image.open("SnowPatrol.png")
    with st.container() as mp:
        st.markdown('<style>div.block-container{padding-bottom :0px; padding-right :10px; padding-top :30px;padding-left :10px; margin:10px; }</style>',unsafe_allow_html=True)
        m1,m2=st.columns(2,gap="small")
        with m1:
            st.image(image,width=250 )
        with m2:
            st.markdown(
            "<div style='text-align: right; font-size: 20px; font-family: Arial; color:rgb(0,0,100); font-weight: bold; '>Export Data</div>",
            unsafe_allow_html=True,
            )
    st.markdown('<hr style="margin-top: 0px; margin-bottom: 0px;">', unsafe_allow_html=True)    
    if 'sdm' in st.session_state:
        session_sdm=st.session_state['sdm']
        available_roles=get_available_roles_for_user()
        session_sdm.role=selected_role = "ACCOUNTADMIN"
        session_sdm.db=selected_db = "SNOWPATROL"
        session_sdm.schema=selected_scm = "MAIN"
        session_sdm.wh=selected_wh = "COMPUTE_WH"
        active_licenses=session_sdm.get_active_licenses()
        
        metrics_section_col1,ee, metrics_section_col2 = st.columns([20,5,75])
        with metrics_section_col1:
            start_date = st.date_input("From Date")

            end_date = st.date_input("To Date")
            
            session_sdm = SnowpatrolDataModel(st.session_state['SNOWPARK_SESSION'])
            st.session_state['sdm']=session_sdm
            active_licenses=session_sdm.get_active_licenses()
            al = 0 if active_licenses.empty else active_licenses['ACTIVE_LICENSES'].sum()
            #app_name = st.selectbox(label="**App Name**", options=app_list)
            app_list = active_licenses['APP_NAME'].unique()
            app_name = st.selectbox(label="**Application**", options=app_list)
            app_id = int(active_licenses[active_licenses.APP_NAME == app_name].reset_index().at[0,'APP_ID'])            
            #app_name = st.selectbox(label="**App Name**", options=app_list)
            include = st.selectbox(
                label="User",
                options=["All User","Revocation Recommendations"],  # Replace with your department options
                index=0  # Set the default selected department
            )
            styles={

            #"container": {"padding": "0!important", "background-color": "#fafafa"},

            "nav-link": {"font-size": "17px", "text-align": "left", "margin":"30px", "--hover-color": "#eee"},

            #"nav-link-selected": {"background-color": "#0096FF"},
            "icon":{"display":"inline-block"},
            

        }
        
        conn_params={
            "user":"Ganesh",
            "password":"G@nesh#123",
            "account":"ejtvpfq-rnb18138",
            "warehouse":"COMPUTE_WH",
            "database":"SNOWPATROL",
            "schema":"MAIN"
        }
        
        conn = snowflake.connector.connect(**conn_params)
        #cursor= conn.cursor()
        cursor1 = conn.cursor()
        cursor2 = conn.cursor()

        query1=f'''select distinct e.app_id,e.session_user,e.division,e.title,e.department,a.snapshot_datetime from sample_emp_metadata e, sample_okta_logs a where a.snapshot_datetime BETWEEN '{start_date}' and '{end_date}' and a.session_user=e.session_user and a.app_id=e.app_id and a.app_id={app_id}'''
        query2=f'''select distinct e.app_id,e.session_user,e.division,e.title,e.department,a.snapshot_datetime from sample_emp_metadata e, sample_okta_logs a where a.snapshot_datetime  NOT BETWEEN '{start_date}' and '{end_date}' and a.session_user=e.session_user and a.app_id=e.app_id and a.app_id={app_id}'''

        
        with metrics_section_col2:
            if include=="All User":
                cursor1.execute(query1)
                data1 = cursor1.fetchall()
                
                #st.write('Data from table')
                column_names = [desc[0] for desc in cursor1.description]
                #column_names[0] = "Sr.No"
                # Create a DataFrame with column names
                Data1 = pd.DataFrame(data1, columns=column_names)
                Data1.index = Data1.index + 1
                Data1.index.name="Sr.No"
                st.write("")
                st.dataframe(Data1)
                csv = Data1.to_csv(index=False)
                # Generate and set a download link
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="data.csv",
                    mime="text/csv",
                )
            if include=="Revocation Recommendations":
                cursor2.execute(query2)
                data1 = cursor2.fetchall()
                #st.write('Data from table')
                column_names = [desc[0] for desc in cursor2.description]
                # Create a DataFrame with column names
                Data1 = pd.DataFrame(data1, columns=column_names)
                Data1.index = Data1.index + 1
                Data1.index.name="Sr.No"
                st.write("")
                st.dataframe(Data1)
                csv = Data1.to_csv(index=False)
                # Generate and set a download link
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="data.csv",
                    mime="text/csv",
                ) 
            conn.close()


          
            
    #################################
    #
    #   Execution
    #
    #################################

    if __name__ == '__main__':
        if 'SNOWPARK_SESSION' not in st.session_state:
            init_session()
        build_UI()
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

