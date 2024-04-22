import pymysql
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import joblib
from datetime import datetime
import requests
from io import StringIO  
import re

# Load your trained model
model = joblib.load('best_model.joblib')

# Function to connect to the database and fetch data
def fetch_data():
    # Database connection parameters - replace these with your details
    conn = pymysql.connect(
        host='dev.cs.smu.ca',
        user='r_khevaria',
        password='islandENGLISH72',
        database='r_khevaria'
    )
    # SQL query to fetch data
    query = "SELECT * FROM rentListings"
    # Reading the data into a Pandas DataFrame
    data = pd.read_sql(query, conn)
    # Closing the connection
    conn.close()
    return data

# Function to convert DataFrame to CSV and download
def convert_df_to_csv(df):
    # Convert DataFrame to CSV
    csv = df.to_csv(index=False)
    # Convert CSV string to bytes
    return csv.encode('utf-8')

def show_data_page():
    st.header("Database to CSV Downloader")
    if st.button("Fetch Data from Database"):
        data = fetch_data()
        st.write(data)
        
        # Convert data to CSV and then to bytes
        csv_bytes = convert_df_to_csv(data)
        
        # Create a CSV download link
        st.download_button(
            label="Download data as CSV",
            data=csv_bytes,
            file_name='database_data.csv',
            mime='text/csv'
        )

def calculate_multiplier(annual_rate, days_future):
    # Convert annual rate percentage to a decimal
    rate_decimal = annual_rate / 100
    
    # Calculate the multiplier using the compound interest formula
    multiplier = (1 + rate_decimal) ** (days_future / 365)
    return multiplier

# Function to validate Canadian postal code
def validate_postal_code(postal_code):
    # Strict Canadian postal code pattern
    pattern = r"^[A-Za-z]\d[A-Za-z][ -]?\d[A-Za-z]\d$"
    # Remove any accidental additional spaces and ensure uppercase
    formatted_postal_code = postal_code.replace(" ", "").upper()
    # Check if formatted postal code matches the pattern
    if re.match(pattern, formatted_postal_code):
        # Properly format with a space
        proper_postal_code = formatted_postal_code[:3] + ' ' + formatted_postal_code[3:]
        return True, proper_postal_code
    else:
        return False, None

# Define a function to display Tableau dashboards
def display_tableau_dashboard(embed_code):
    components.html(embed_code, height=800, scrolling=True)

def show_prediction_page(model):
    st.header("Real Estate Price Prediction")

    # Dropdown for Property Type
    property_type = st.selectbox("Property Type", ['Apartment', 'House'])
    
    # Numeric inputs
    rooms = st.number_input("Rooms", min_value=1, max_value=10, step=1, value=1)
    den_included = 1
    num_bathrooms = st.number_input("Number of Bathrooms", min_value=1.0, max_value=5.0, step=0.5, value=1.0)
    
    # Inputs for building information
    building_info = st.text_input("Building No. or Name and Street Name")
    postal_code = st.text_input("Postal Code")
    selected_date = st.date_input("Date in Future")  
    # Get today's date
    today = datetime.now().date()

    # Calculate difference in days
    difference = (selected_date - today).days

    multiplier = calculate_multiplier(13, difference)

    # Check postal code validity
    if st.button("Validate Postal Code"):
        valid, formatted_code = validate_postal_code(postal_code)
        if valid:
            st.success(f"Postal code is valid: {formatted_code}")
        else:
            st.error("Invalid Canadian postal code. Please enter a valid format (e.g., M4B 1B4).")

    # Additional inputs
    try:
        address = f"{building_info}, Halifax, {postal_code}"
        # API call
        api_url = f"https://api.opencagedata.com/geocode/v1/json?q={address}&key=a73eb199a18e47bfbc0520f1918023e8"
        response = requests.get(api_url)
        data = response.json()
        latitude = data['results'][0]['geometry']['lat']
        longitude = data['results'][0]['geometry']['lng']
    except:
        latitude = 44.64796
        longitude = -63.58848
    size_sqft = st.number_input("Size (sqft)", min_value=100, max_value=10000, step=1, value=100)
    walk_score = 88
    transit_score = 65
    bike_score = 72
    time_to_nearest_hospital = 350
    time_to_nearest_police_station = 385
    time_to_nearest_store = 238
    time_to_nearest_pharmacy = 184

    # Button to make prediction
    if st.button("Predict Price"):
        # Organize inputs into the same structure as the model expects
        features = pd.DataFrame([[
            property_type, rooms, den_included, num_bathrooms, latitude, longitude, 
            size_sqft, walk_score, transit_score, bike_score, 
            time_to_nearest_hospital, time_to_nearest_police_station, 
            time_to_nearest_store, time_to_nearest_pharmacy
        ]], columns=[
            'Property Type', 'Rooms', 'Den Included', 'Number of Bathrooms', 'Latitude', 'Longitude', 
            'Size (sqft)', 'Walk Score', 'Transit Score', 'Bike Score', 
            'Time to Nearest Hospital', 'Time to Nearest Police Station', 
            'Time to Nearest Store', 'Time to Nearest Pharmacy'
        ])

        # Predict using the loaded model
        prediction = model.predict(features)
        st.write(f"The predicted price is: ${prediction[0]*multiplier:,.2f}")

def main():
    st.set_page_config(layout="wide")
    page = st.sidebar.radio(
        "Choose a page:",
        ['Dashboard', 'Predict', 'Show/Download Data']
    )
    
    if page == 'Dashboard':
        st.title('Real Estate Dashboard')
        st.write('Select a dashboard from the dropdown to display:')

        # Dict to hold dashboard names and their corresponding embed codes
        tableau_dashboards = {
        "Parking Rates": """
        <div class='tableauPlaceholder' id='viz1712964941288' style='position: relative'><noscript><a href='#'><img alt='Parkings  ' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Pa&#47;Parkings_17129622556500&#47;Sheet1&#47;1_rss.png' style='border: none' /></a></noscript><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='site_root' value='' /><param name='name' value='Parkings_17129622556500&#47;Sheet1' /><param name='tabs' value='no' /><param name='toolbar' value='yes' /><param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Pa&#47;Parkings_17129622556500&#47;Sheet1&#47;1.png' /> <param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /><param name='language' value='en-US' /><param name='filter' value='publish=yes' /></object></div>                <script type='text/javascript'>                    var divElement = document.getElementById('viz1712964941288');                    var vizElement = divElement.getElementsByTagName('object')[0];                    vizElement.style.width='100%';vizElement.style.height=(divElement.offsetWidth*0.75)+'px';                    var scriptElement = document.createElement('script');                    scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';                    vizElement.parentNode.insertBefore(scriptElement, vizElement);                </script>
        """,
        "Under Construction Properties": """
        <div class='tableauPlaceholder' id='viz1712964881255' style='position: relative'><noscript><a href='#'><img alt='UnderConstruction Properties ' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Un&#47;UnderConstructionProperties&#47;Sheet1&#47;1_rss.png' style='border: none' /></a></noscript><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='path' value='views&#47;UnderConstructionProperties&#47;Sheet1?:language=en-US&amp;:embed=true&amp;publish=yes&amp;:sid=' /> <param name='toolbar' value='yes' /><param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Un&#47;UnderConstructionProperties&#47;Sheet1&#47;1.png' /> <param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /><param name='language' value='en-US' /><param name='filter' value='publish=yes' /></object></div>                <script type='text/javascript'>                    var divElement = document.getElementById('viz1712964881255');                    var vizElement = divElement.getElementsByTagName('object')[0];                    vizElement.style.width='100%';vizElement.style.height=(divElement.offsetWidth*0.75)+'px';                    var scriptElement = document.createElement('script');                    scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';                    vizElement.parentNode.insertBefore(scriptElement, vizElement);                </script>
        """,
        "Rental Listings": """
        <div class='tableauPlaceholder' id='viz1712964814102' style='position: relative'><noscript><a href='#'><img alt='Properties Overview ' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Bo&#47;Book3_17129635972140&#47;PropertiesOverview&#47;1_rss.png' style='border: none' /></a></noscript><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='site_root' value='' /><param name='name' value='Book3_17129635972140&#47;PropertiesOverview' /><param name='tabs' value='no' /><param name='toolbar' value='yes' /><param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Bo&#47;Book3_17129635972140&#47;PropertiesOverview&#47;1.png' /> <param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /><param name='language' value='en-US' /><param name='filter' value='publish=yes' /></object></div>                <script type='text/javascript'>                    var divElement = document.getElementById('viz1712964814102');                    var vizElement = divElement.getElementsByTagName('object')[0];                    if ( divElement.offsetWidth > 800 ) { vizElement.style.width='1000px';vizElement.style.height='827px';} else if ( divElement.offsetWidth > 500 ) { vizElement.style.width='1000px';vizElement.style.height='827px';} else { vizElement.style.width='100%';vizElement.style.height='777px';}                     var scriptElement = document.createElement('script');                    scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';                    vizElement.parentNode.insertBefore(scriptElement, vizElement);                </script>
        """
    }

        selected_dashboard_name = st.selectbox('Choose a Dashboard:', options=list(tableau_dashboards.keys()))
        embed_code = tableau_dashboards[selected_dashboard_name]
        display_tableau_dashboard(embed_code)

    elif page == 'Predict':
        show_prediction_page(model)

    elif page == 'Show/Download Data':
        show_data_page()

if __name__ == "__main__":
    main()