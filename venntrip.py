from xml.etree.ElementInclude import include
import gspread
import gmaps
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials


import streamlit as st

import requests
import urllib.parse
import numpy as np

from PIL import Image

from streamlit_folium import st_folium
import folium

image = Image.open('banner.jpg')
st.image(image)


@st.cache
def get_data():
    #GET DATA FROM GOOGLE SHEET
    # defining the scope of the application
    scope_app = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive'] 

    #credentials to the account
    cred = ServiceAccountCredentials.from_json_keyfile_name('venntrip-e7a6f71bd13c.json',scope_app) 

    # authorize the clientsheet 
    client = gspread.authorize(cred)

    # get the sample of the Spreadsheet
    sheet = client.open('VENN-EUROTRIP')

    # get the first sheet of the Spreadsheet
    sheet_instance = sheet.get_worksheet(0)

    # get all the records of the data
    records = sheet_instance.get_all_records()

    records_df = pd.DataFrame.from_dict(records)

    records_df['Stripped links'] = records_df['Google link'].str.lstrip("https://www.google.com/maps/place/")

    new_cols = records_df['Stripped links'].str.split("@",n=1,expand=True)

    records_df['trash'] = new_cols[0]
    records_df['keep'] = new_cols[1]

    records_df.drop(columns=['Stripped links'],inplace=True)
    records_df['keep']

    new_cols = records_df['keep'].str.split(",",n=1,expand=True)
    records_df['lat'] = new_cols[0]
    records_df['keep_for_lon'] = new_cols[1]

    new_cols = records_df['keep_for_lon'].str.split(",",n=1,expand=True)
    records_df['lon'] = new_cols[0]

    records_df.drop(columns=['keep_for_lon'],inplace=True)
    records_df.drop(columns=['trash'],inplace=True)
    records_df.drop(columns=['keep'],inplace=True)

    df_after_lon_lat_merge = records_df

    return(df_after_lon_lat_merge)

df_after_lon_lat_merge = get_data()

if st.checkbox('Add a suggestion here:'):
    st.write("When you find a place that you would like to visit add it to the list!")
    st.write("[Click here to add a suggestion](https://docs.google.com/spreadsheets/d/12ZQKfUnnnPuWtn0BYLCK_E2BxNigchI7HryYQSEOvI4/edit?usp=sharing)")
    st.write("Make sure to fill out all of the columns - or youll probably break the program")
    st.write("The google link needs start with https://www.google.com/maps/place/ or your suggestion will not be added to the map")
    image1 = Image.open("1.jpg")
    st.image(image1)


#user input location
show_map_scope = st.radio('What part of the trip do you want to view?',('Whole trip','Switzerland','Germany','Czech Republic'))

if show_map_scope == 'Whole trip':
    df_after_lon_lat_merge = df_after_lon_lat_merge
    location=[48.1351, 11.5820]
    zoom_start = 7

elif show_map_scope == 'Switzerland':
    df_after_lon_lat_merge = df_after_lon_lat_merge.loc[df_after_lon_lat_merge['Country']=='Switzerland']
    location=[47.3769, 8.5417]
    zoom_start = 8

elif show_map_scope == 'Germany':
    df_after_lon_lat_merge = df_after_lon_lat_merge.loc[df_after_lon_lat_merge['Country']=='Germany']
    location=[48.1351, 11.5820]
    zoom_start = 11

elif show_map_scope == 'Czech Republic':
    df_after_lon_lat_merge = df_after_lon_lat_merge.loc[df_after_lon_lat_merge['Country']=='Czech Republic']
    location=[50.0755, 14.4378]
    zoom_start = 11


#user input activity type
activity_type = st.radio('What type of activity?',('All','Food & Drink','Cool Place','History'))

if activity_type == 'All':
    df_after_lon_lat_merge = df_after_lon_lat_merge

if activity_type == 'Food & Drink':
    df_after_lon_lat_merge = df_after_lon_lat_merge.loc[df_after_lon_lat_merge['Idea type']=='Food & Drink']

if activity_type == 'Cool Place':
    df_after_lon_lat_merge = df_after_lon_lat_merge.loc[df_after_lon_lat_merge['Idea type']=='Cool Place']

if activity_type == 'History':
    df_after_lon_lat_merge = df_after_lon_lat_merge.loc[df_after_lon_lat_merge['Idea type']=='History']


#user input suggestion bool
include_suggestions = st.radio('Do you want to include suggestions?',('Yes','No'))
if include_suggestions == 'Yes':
     df_after_lon_lat_merge = df_after_lon_lat_merge
elif include_suggestions == 'No':
     df_after_lon_lat_merge = df_after_lon_lat_merge.loc[df_after_lon_lat_merge['Idea by']!='Tim']

m = folium.Map(location=location,zoom_start=zoom_start)
for index,row in df_after_lon_lat_merge.iterrows():
    folium.Marker([row['lat'],row['lon']],
    popup=(f"""Link to <a href={row['Google link']}>{row['Name']}</a><br><br> Description:{row['Description']}"""),
    tooltip=f"""Name:{row['Name']} <br><br> Suggested by:{row['Idea by']} """).add_to(m)
    

st_data = st_folium(m,width=725)




