import streamlit as st
#import streamlit as st
from PIL import Image
import re
import pandas as pd
from streamlit_option_menu import option_menu


st.set_page_config(
    
    layout = "wide",

)
st.image('SnowPatrol.png',width=300)


# with st.sidebar:/
selected=option_menu(
        menu_title=None,
        options=['home','buisness','work'],
        default_index=0,
        orientation="horizontal"
    )

if selected=="home":
    st.title(f'you have selected {selected}')
if selected=="buisness":
    st.title(f'you have selected {selected}')
if selected=="work":
    st.title(f'you have selected {selected}')



option = st.selectbox('Who is  your fav crickter',('Dhoni', 'Virat', 'Sachin'))
st.write('You selected:', option)
if option =='Dhoni':
    st.title('Dhoni')
    st.header('7/7/1981')
    st.subheader('Ranchi')
    st.text('Former Indian Captain-G.O.A.T')
    st.markdown("""
            # Captain Cool
            ## Thala
            ### Finisher""")
    #st.image('pic//1.png')
    #st.audio('de.mp3')
    st.title('widgets')    
elif option=='Virat':
    st.write('vk')



if 'count1' not in st.session_state:
    st.session_state.count1 = 0

if 'count2' not in st.session_state:
    st.session_state.count2 = 0

like = st.button('like')
dislike=st.button('dislike')
if like:
    st.session_state.count1 += 1
else :
    st.session_state.count2 +=1


st.write('Likes = ', st.session_state.count1)
st.write('Dislikes = ', st.session_state.count2)


Word=st.text_area('Comments')
st.write('add ur comment here')






def count():
    hi=like*2
    st.write('hi')
    return count()



# with st.sidebar:
#     selected=option_menu(
#         menu_title=None,
#         options=['home','buisness','work'],
#         default_index=0,
#         orientation="horizontal"
#     )

# if selected=="home":
#     st.title(f'you have selected{selected}')
# if selected=="buisness":
#     st.title(f'you have selected{selected}')
# if selected=="work":
#     st.title(f'you have selected{selected}')

