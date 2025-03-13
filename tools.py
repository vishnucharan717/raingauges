from flask import Flask, jsonify
import pandas as pd
import plotly.express as px
from flask import url_for
import re
import plotly.graph_objects as go
from scp import SCPClient
import paramiko
import os
import subprocess
import shutil
import urllib.parse
from datetime import datetime, timedelta

def map_plotting():
    # Load data from the combined CSV file
    main_sensors_papth = r'C:\Users\vishnu71\Desktop\API_Code_Python\Sensor_Data\main_sensors.csv'
    df_combined = pd.read_csv(main_sensors_papth)

    # Ensure Latitude and Longitude columns are numeric
    df_combined['Latitude'] = pd.to_numeric(df_combined['Latitude'], errors='coerce')
    df_combined['Longitude'] = pd.to_numeric(df_combined['Longitude'], errors='coerce')

    # Drop rows with missing Latitude or Longitude
    df_combined = df_combined.dropna(subset=['Latitude', 'Longitude'])

    # Check for duplicate Station IDs
    duplicates = df_combined[df_combined.duplicated(subset=['Station Id'], keep=False)]
    if not duplicates.empty:
        print("Duplicate Station IDs found:")
        print(duplicates)

    # Create new columns with URLs for 15-min, hourly, and daily data
    # df_combined['URL1'] = '/api/map'

    df_combined['URL1'] = df_combined['Station Id'].apply(lambda x: f"/gauge/{x}")

    # Create the map with color markers
    fig = px.scatter_mapbox(
        df_combined, 
        lat="Latitude", 
        lon="Longitude", 
        hover_data=["Station Id", "Sensor Group"],
        zoom=6,
        color='Sensor Group',
        color_discrete_map={"Sonoma County": "#256b9c", "Valley Water": "#b09a25", "Contra Costa":"#9c4b4b"},
        opacity=0.9
    )
    
    # Customize marker symbol and size
    fig.update_traces(
        marker=dict(size=15, symbol="circle"),
        hovertemplate=(
            '<b>%{customdata[1]}</b><br>' 
            'Station Id: %{customdata[0]}<br>' 
            '<a href="%{customdata[2]}" target="_blank">QPE Gauge Comparison</a><br>'
        ),
        # customdata=df_combined[['Station Id', 'Sensor Group', 'URL1', 'URL2', 'URL3']].values
        customdata=df_combined[['Station Id', 'Rain Guage Name', 'URL1']].values
    )

    # Calculate map center based on the mean latitude and longitude
    center_lat = df_combined['Latitude'].mean()
    center_lon = df_combined['Longitude'].mean()

    # Update the map layout
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_zoom=6,
        mapbox_center={"lat": center_lat, "lon": center_lon},
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        showlegend=False,
        autosize=True,
        height=None,
        dragmode="zoom"
    )

    # Save the map as an HTML file
    output_path = r'C:\Users\vishnu71\Desktop\API_Code_Python\static\disd_map.html'
    fig.write_html(output_path, full_html=True, config={'displayModeBar': False, 'scrollZoom': True})

    return output_path

import shutil
import os

def retrieve_guage_plot(station_id, selected_date=None):
    # If selected_date is not provided, use yesterday's date
    if selected_date is None:
        selected_date = datetime.now() - timedelta(days=1)
    
    # Ensure selected_date is a datetime object
    if isinstance(selected_date, str):
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d')
    
    formatted_date = selected_date.strftime(r"\%Y\%m\%d\\")
    
    main_sensors_papth = r'C:\Users\vishnu71\Desktop\API_Code_Python\Sensor_Data\main_sensors.csv'
    df_combined = pd.read_csv(main_sensors_papth)
    gauge_info = df_combined[df_combined['Station Id'] == station_id].to_dict(orient='records')
    
    sensor_grp = gauge_info[0]['Sensor Group']
    dirmatching = {'Contra Costa': 'contracosta', "Sonoma County": "sonomawater", "Valley Water": "valleywater"}
    sensor_id = gauge_info[0]['Station Id']
    rootpath = r'X:\vishnu71\raingauge\Plots_Data'
    rootpath += formatted_date + dirmatching[sensor_grp]

    matching_files = []
    for filename in os.listdir(rootpath):
        if filename.startswith(sensor_id):
            matching_files.append(filename)
    
    if matching_files:
        filename_plot = matching_files[0]
        full_path = os.path.join(rootpath, filename_plot)
        
        # Copy the image to the static folder as placeholder.png
        static_image_path = os.path.join('static', 'images', 'placeholder.png')
        shutil.copy(full_path, static_image_path)  # Copy the image to static/images/placeholder.png
        
        # Convert the path to a relative path using forward slashes
        relative_image_path = os.path.join("images", 'placeholder.png').replace("\\", "/")
        return relative_image_path
    else:
        return 'images/placeholder.png'  # Return placeholder if no image found




