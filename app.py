import json
from flask import Flask, request, jsonify
import math
from geopy.distance import geodesic

app=Flask(__name__)

with open('data.json') as json_file:
    data = json.load(json_file)

@app.route('/api/accidents')
def get_users():
    return jsonify(data)


@app.route('/api/accidentIndex/<Accident_Index>')
def get_user(Accident_Index):
    user = None
    for item in data:
        if item["Accident_Index"] == Accident_Index:
            user = item
            break    
    if user:
        return jsonify(user)
    else:
        return jsonify({"message": "User not found"}), 404

@app.route('/api/accidentDate/<Accident_Date>')
def get_date(Accident_Date):
    user = None
    for item in data:
        if item["Accident Date"] == Accident_Date:
            user = item
            break    
    if user:
        return jsonify(user)
    else:
        return jsonify({"message": "User not found"}), 404

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth's radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance


@app.route('/api/locations/<Latitude>/<Longitude>', methods=['GET'])
def get_locations_within_100_meters(Latitude, Longitude):
    # Filter locations within 100 meters using the Haversine formula
    Latitude = float(Latitude)
    Longitude = float(Longitude)
    locations_within_100_meters = []
    for location in data:
        distance = haversine(Latitude, Longitude, location['Latitude'], location['Longitude'])
        if distance <= 0.1:  # 0.1 = 100 meters in km
            locations_within_100_meters.append(location)
    return jsonify(locations_within_100_meters)




def get_matched_data(source_lat, source_lon, dest_lat, dest_lon):
    # Convert source and destination coordinates to floats
    source_lat = float(source_lat)
    source_lon = float(source_lon)
    dest_lat = float(dest_lat)
    dest_lon = float(dest_lon)

    # Assuming the 'data.json' file is in the same directory as this script
    with open('data.json', 'r') as json_file:
        all_data = json.load(json_file)

    matched_data = []
    for item in all_data:
        # Check if the dictionary has both 'latitude' and 'longitude' keys
        if 'Latitude' in item and 'Longitude' in item:
            # Convert latitude and longitude from string to float
            lat = float(item['Latitude'])
            lon = float(item['Longitude'])
            # Check if the item's coordinates are between the source and destination
            if (source_lat <= lat <= dest_lat or
                dest_lat <= lat <= source_lat) and \
               (source_lon <= lon <= dest_lon or
                dest_lon <= lon <= source_lon):
                matched_data.append(item)

    return matched_data

@app.route('/<source_lat>,<source_lon>/<dest_lat>,<dest_lon>', methods=['GET'])
def get_matched_data_between_source_and_dest(source_lat, source_lon, dest_lat, dest_lon):
    matched_data = get_matched_data(source_lat, source_lon, dest_lat, dest_lon)

    if matched_data:
        return jsonify(matched_data)
    else:
        return jsonify({'error': 'No matching data found.'}), 404

if __name__=="__main__":
    app.run(debug=True)

    