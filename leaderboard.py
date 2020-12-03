# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 09:03:48 2020

@author: kenne
"""


import streamlit as st
import pandas as pd 
import pandas as pd 
import datetime
import altair as alt
from streamlit_vega_lite import vega_lite_component, altair_component
import numpy as np
import requests as req
import json 


#get data in --> Need to make a database and an api call 
@st.cache
def get_comments():
    response = req.get("https://8g3954uola.execute-api.us-east-1.amazonaws.com/dbtest")
    x = response.text
    dic_json = json.loads(x)
    df = pd.DataFrame(dic_json)
    df['Date'] = pd.to_datetime(df['Date'],errors ='coerce')
    df['just_date'] = df['Date'].dt.date
    return df


#read from api & cache 
df = get_comments()

#remove myself from data
ken_yn = st.sidebar.radio("Include Ken?",('No', 'Yes'))
if ken_yn == 'No':
    df = df[df['Author_Name'] != 'Ken Jee']
else: 
    df = df

today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)
month = today.replace(day=1)
year = today.replace(day=1).replace(month=1)


time_period = st.sidebar.radio("Time Period",('This Month', 'This Year'))
if time_period == 'This Month':
    start_date = month
else: 
    start_date = year

end_date = tomorrow
df_dates = df[(df.just_date >= start_date) & (df.just_date <= end_date)].sort_values('just_date',ascending=False)  
 
option = st.selectbox('Select which leaderboard you want to see:', ('Engagement Points','Likes', '# of Comments', 'Replies', 'Top Comments'))

if option == 'Engagement Points':
    like_winners = pd.pivot_table(df_dates, index='Author_Name', values=['Like_Count','Reply_Count'], aggfunc='sum').reset_index()
    comment_leaders = pd.pivot_table(df_dates, index='Author_Name', values='Comments', aggfunc='count').reset_index()
    eps = pd.merge(comment_leaders, like_winners, on = 'Author_Name')
    eps['Engagement Points'] = eps.Like_Count + eps.Comments + eps.Reply_Count*.5
    eps = eps.sort_values('Engagement Points', ascending =False)
    b_chart = alt.Chart(eps.head(20)).mark_bar().encode(
        x=alt.X('Engagement Points:Q'),
        y=alt.Y("Author_Name:O", sort ='-x'),
        color= alt.Color('Engagement Points:Q', scale=alt.Scale(scheme='reds'), legend=None))    
    st.write("""
    # Ken Jee Engagement Point Leaderboard 
    """)    
    st.write(b_chart)
elif option == 'Likes':
    like_winners = pd.pivot_table(df_dates, index='Author_Name', values='Like_Count', aggfunc='sum').reset_index().sort_values('Like_Count', ascending=False)
    b_chart = alt.Chart(like_winners.head(20)).mark_bar().encode(
        x=alt.X('Like_Count:Q'),
        y=alt.Y("Author_Name:O", sort ='-x'),
        color= alt.Color('Like_Count:Q', scale=alt.Scale(scheme='reds'), legend=None))    
    st.write("""
    # Ken Jee Comment Like Leaderboard 
    """)    
    st.write(b_chart)
elif option == '# of Comments':
    comment_leaders = pd.pivot_table(df_dates, index='Author_Name', values='Comments', aggfunc='count').reset_index().sort_values('Comments', ascending=False)
    b_chart = alt.Chart(comment_leaders.head(20)).mark_bar().encode(
        x=alt.X('Comments:Q'),
        y=alt.Y("Author_Name:O", sort ='-x'),
        color= alt.Color('Comments:Q', scale=alt.Scale(scheme='reds'), legend=None))    
    st.write("""
    # Ken Jee Comment Leaderboard 
    """)    
    st.write(b_chart)
elif option == 'Replies':
    reply_leaders = pd.pivot_table(df_dates, index='Author_Name', values='Reply_Count', aggfunc='sum').reset_index().sort_values('Reply_Count', ascending=False)
    b_chart = alt.Chart(reply_leaders.head(20)).mark_bar().encode(
        x=alt.X('Reply_Count:Q'),
        y=alt.Y("Author_Name:O", sort ='-x'),
        color= alt.Color('Reply_Count:Q', scale=alt.Scale(scheme='reds'), legend=None))    
    st.write("""
    # Ken Jee Comment Reply Leaderboard 
    """)    
    st.write(b_chart)
elif option == 'Top Comments':
    top_comments = df_dates[['Like_Count','Author_Name','Comments']].sort_values('Like_Count',ascending=False).head(20)
    st.table(top_comments.assign(hack='').set_index('hack'))
    
    
#Add emojis next to names 
#greater than 5 comments
