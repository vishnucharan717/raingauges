import pandas as pd
from flask import Flask, send_file, render_template, send_from_directory, request
from tools import map_plotting, retrieve_guage_plot
from datetime import datetime, timedelta

app = Flask(__name__)

IMAGE_ROOT = r'X:\vishnu71\raingauge\Plots_Data'

@app.route('/api/map')
def generate_map():
    return send_from_directory('static', 'disd_map.html')

@app.route('/gauge/<station_id>', methods=['GET', 'POST'])
def gauge_page(station_id):
    selected_date = None
    if request.method == 'POST':
        selected_date_str = request.form.get('date')  # assuming date is passed from a form
        if selected_date_str:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d')  # Convert to datetime object
    
    # If no date is selected, set it to yesterday
    print("DATEE")
    print(selected_date)
    if not selected_date:
        selected_date = datetime.now() - timedelta(days=1)
    
    plot_image_path = retrieve_guage_plot(station_id, selected_date)
    
    # Load station data from CSV
    main_sensors_path = r'C:\Users\vishnu71\Desktop\API_Code_Python\Sensor_Data\main_sensors.csv'
    df_combined = pd.read_csv(main_sensors_path)
    gauge_info = df_combined[df_combined['Station Id'] == station_id].to_dict(orient='records')

    if not gauge_info:
        return "Station ID not found", 404
    
    return render_template("gauge.html", gauge=gauge_info[0], plot_image_path=plot_image_path, selected_date=selected_date)