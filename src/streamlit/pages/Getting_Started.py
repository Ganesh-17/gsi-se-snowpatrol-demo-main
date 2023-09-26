
from datetime import datetime, timedelta
from snowflake.snowpark import Session
import plotly.graph_objects as go
from app_data_model import SnowpatrolDataModel
import json 

import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_toggle import st_toggle_switch


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
st.set_page_config(
     page_title="Snowpatrol - License Optimization",
     page_icon=":rotating_light:",
     layout="wide",
     initial_sidebar_state="expanded"
)
st.header(":rotating_light: Snowpatrol - License Optimization")

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

    # with st.container() as snowflake_connection:
    #     colored_header(
    #             label="Connect to Snowflake's Snowpatrol data source",
    #             description="Provide your Snowflake credentials to login",
    #             color_name="red-70",
    #     )        
    #     with st.container() as mandatory_fields:
    #         account = st.text_input('Snowflake Account Identifier* : ')
    #         mandatory_fields_col1, mandatory_fields_col2 = st.columns(2, gap="small")
    #         with mandatory_fields_col1:
    #             username = st.text_input('Username* : ')
    #         with mandatory_fields_col2:
    #             password = st.text_input('Password* : ', type="password")

    #     """__*must fill__"""

    #     connect = st.button("Connect", type="primary")

    #     if connect:
    #         connect_to_snowflake(account=account , username=username , password=password)
    #         session_sdm = SnowpatrolDataModel(st.session_state['SNOWPARK_SESSION'])
    #         st.session_state['sdm']=session_sdm


def build_UI():            
    if 'sdm' in st.session_state:
        session_sdm=st.session_state['sdm']
        available_roles=get_available_roles_for_user()

        with st.container() as execution_context:
            execution_context_col1,execution_context_col2, execution_context_col3, execution_context_col4 = st.columns(4, gap="small")
            selected_role = selected_db = selected_scm = selected_wh = ""
            
            with execution_context_col1:
                if available_roles:
                    selected_role = st.selectbox("Role: ", options=available_roles)
                    if selected_role != session_sdm.role:
                        session_sdm.role = selected_role 
            with execution_context_col2:
                available_databases=get_available_databases(session_sdm.role)       
                if available_databases:
                    selected_db = st.selectbox('Database : ', options=available_databases)
                    if selected_db != session_sdm.db:
                        session_sdm.db = selected_db
            with execution_context_col3:
                available_schemas=get_available_schemas(session_sdm.role, session_sdm.db)
                if available_schemas:
                    selected_scm = st.selectbox('Schema : ', options=available_schemas)
                    if selected_scm != session_sdm.schema:
                        session_sdm.schema = selected_scm
            with execution_context_col4:
                available_warehouses=get_available_warehouses(session_sdm.role)
                if available_warehouses:
                    selected_wh = st.selectbox('Warehouse : ', options=available_warehouses)
                    if selected_wh != session_sdm.wh:
                        session_sdm.wh = selected_wh
                
        active_licenses=session_sdm.get_active_licenses()

        with st.container() as login_history_section:
            with st.container() as metrics_section:
                colored_header(
                    label="Login history",
                    description="",
                    color_name="red-70",
                )     
                metrics_section_col1, metrics_section_col2 = st.columns(2, gap="small")
                with metrics_section_col1:
                    al = 0 if active_licenses.empty else active_licenses['ACTIVE_LICENSES'].sum()
                    st.metric(label="**Total Active Licenses**", value=al)
                with metrics_section_col2:
                    apps_tracked= 0 if active_licenses.empty else active_licenses['APP_NAME'].nunique()
                    st.metric(label="**Applications Tracked**", value=apps_tracked)
                style_metric_cards()
            # with st.container() as charts_section:
            #     if not active_licenses.empty:
            #         # """**License usage by Department**"""
            #         _z = active_licenses.groupby(['APP_NAME', 'DEPARTMENT'])['ACTIVE_LICENSES'].sum().reset_index()
            #         temp = _z.pivot(index='APP_NAME', columns='DEPARTMENT')['ACTIVE_LICENSES'].fillna(0)
            #         fig_active_license_heatgrid = go.Figure(data=go.Heatmap(
            #                                     z=temp.values,
            #                                     x=temp.columns,
            #                                     y=temp.index,
            #                                     hoverongaps = True
            #                                     ))
            #         fig_active_license_heatgrid = fig_active_license_heatgrid.update_traces(
            #             text=temp.values, texttemplate="%{text}",
            #         )
            #         fig_active_license_heatgrid.update_layout(title={
            #                                 'text': "License usage by Department",
            #                                 'font' : {'size' : 20},
            #                                 'y':0.9,
            #                                 'x':0.5,
            #                                 'xanchor': 'center',
            #                                 'yanchor': 'top'})
            #         st.plotly_chart(fig_active_license_heatgrid, use_container_width=True, theme="streamlit")
        with st.container() as revocation_recommendations:
            colored_header(
                label="Revocation recommendations",
                description="",
                color_name="red-70",
            )
            
            if not active_licenses.empty:
                app_list = active_licenses['APP_NAME'].unique()
                app_name = st.selectbox(label="**App Name**: Select an app to train for", options=app_list)
                app_id = int(active_licenses[active_licenses.APP_NAME == app_name].reset_index().at[0,'APP_ID'])
            
                cutoff_days = st.slider(label="**Cutoff Days**: Number of days to go back from today to look for authentication patterns between the beginning and this cutoff date", min_value=0, max_value=365, step=5, value=30)
                run_date = datetime.now().date() 
                f"""(Cutoff Date): {run_date - timedelta(days = cutoff_days)}""" 
                # target_variable_days_no_login = st.slider(label="**Tolerance period for no login**: Maximum length of time in days after cutoff date that a user is expected to login for continued usage", min_value=0, max_value=45, step=5, value=30)
                # half_life_variable = st.slider(label="**Half life variable**: Add weights to authentications made before cutoff date", min_value=0, max_value=30, step=5, value=30)
                probability_no_login_revocation_threshold = st.slider(label="**Login probability threshold**: Predicted probabilities greater than or equal to threshold are recommended for revocations", min_value=0.0, max_value=1.0, value=0.5)
            
                with st.container() as get_recomm:
                    with st.expander("**Pull recommendations from an older run:**"):                            
                        runs_df=session_sdm.get_revocation_recommendations(app_id)
                        run_list = runs_df['RUN_ID'].unique().tolist() if not runs_df.empty else []
                        run_id= st.selectbox("Select a run id :- ", options=run_list)

                        get_older_recommendations = st.button("Get", disabled=True if runs_df.empty else False)

                    with st.expander("**Retrain & get fresh recommendations:**"):
                        get_recomm_c1, get_recomm_c2, get_recomm_c3, get_recomm_c4, = st.columns(4, gap="small")
                        with get_recomm_c1:
                            include_dept = st_toggle_switch(label="Include 'department' attribute?",
                                            default_value=False,
                                            inactive_color="#D3D3D3",  # optional
                                            active_color="red",  # optional
                                            track_color="#FA8268",  # optional
                                        )
                        with get_recomm_c2:
                            include_div = st_toggle_switch(label="Include 'division' attribute?",
                                            default_value=False,
                                            inactive_color="#D3D3D3",  # optional
                                            active_color="red",  # optional
                                            track_color="#FA8268",  # optional
                                        )

                        with get_recomm_c3: 
                            include_title = st_toggle_switch(label="Include 'title' attribute?",
                                            default_value=False,
                                            inactive_color="#D3D3D3",  # optional
                                            active_color="red",  # optional
                                            track_color="#FA8268",  # optional
                                        )

                        with get_recomm_c4: 
                            save_model = st_toggle_switch(label="Save model after training?",
                                            default_value=False,
                                            inactive_color="#D3D3D3",  # optional
                                            active_color="red",  # optional
                                            track_color="#FA8268",  # optional
                                        )
                            
                        generate_new_recommendations = st.button("Generate")  

                    if get_older_recommendations | generate_new_recommendations:

                        response={'status':''}

                        if get_older_recommendations:
                            response = {"status": "SUCCESS"}
                            recommendations_df = runs_df[runs_df.RUN_ID == run_id]
                            run_date = recommendations_df['TRAINING_DATE'].unique()[0]
                            probability_threshold = recommendations_df['THRESHOLD_PROBABILITY'].unique()[0]

                        if generate_new_recommendations:
                            run_date = datetime.now().date()
                            probability_threshold = probability_no_login_revocation_threshold

                            response = session_sdm.run_model_today(app_id=app_id
                                                , cutoff_days=cutoff_days
                                                ,probability_no_login_revocation_threshold=probability_no_login_revocation_threshold
                                                ,include_dept=include_dept,include_div=include_div,include_title=include_title
                                                ,save_model=save_model)
                            response = json.loads(response)
                            recommendations_df = session_sdm.get_revocation_recommendations(app_id, response['run_id'])

                        if 'ERROR' in response['status']:
                            st.error(f"**{response['status']}**", icon="☠️")
                        else:
                            st.snow()
                            # st.success(f"**{response['status']}**", icon="👍")
                            st.divider()
                            with st.container() as recomm_results:
                                
                                f"""**Run Date** : {run_date}""" 
                                f"""**Login probability threshold** : {probability_threshold}""" 

                                recomm_results_col0_spacer1, recomm_results_c1, recomm_results_col0_spacer2 = st.columns((5, 25, 5))
                                
                                with recomm_results_col0_spacer1:
                                    st.markdown("""""")

                                with recomm_results_c1:
                                    _total_active = int(active_licenses[active_licenses.APP_ID == app_id]['ACTIVE_LICENSES'].sum())
                                    _revocable = int(recommendations_df[recommendations_df.REVOKE == 1]["SESSION_USER"].nunique())
                                    fig_active_vs_revocable = go.Figure(data=go.Pie(values=[(_total_active - _revocable),_revocable],
                                                                        labels=['ACTIVE', 'REVOCABLE'], hole=0.4)
                                                                )
                                    fig_active_vs_revocable.update_traces(hoverinfo='label+value',
                                                                textinfo='percent', textfont_size=20, marker=dict(colors=['gold', 'mediumturquoise'])
                                                                )
                                    fig_active_vs_revocable.add_annotation(x=0.5, y=0.47,
                                                                text=f"{_revocable} / {_total_active}",
                                                                font=dict(size=15, family='Verdana',
                                                                            color='black'),
                                                                showarrow=False)
                                    
                                    fig_active_vs_revocable.update_layout(title={
                                                'text': "Active vs. Revocable Licenses",
                                                'font' : {'size' : 20},
                                                'y':0.9,
                                                'x':0.45,
                                                'xanchor': 'center',
                                                'yanchor': 'top'})

                                    st.plotly_chart(fig_active_vs_revocable, use_container_width=True, theme="streamlit")

                                with recomm_results_col0_spacer2:
                                    st.markdown("""""")


#################################
#
#   Execution
#
#################################

if __name__ == '__main__':
    if 'SNOWPARK_SESSION' not in st.session_state:
        init_session()
    build_UI()
