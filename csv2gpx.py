import csv
import gpxpy
import gpxpy.gpx
from datetime import datetime, timedelta
from geopy.distance import geodesic

# Function to convert Unix timestamp to datetime
def unix_timestamp_to_datetime(unix_timestamp):
    return datetime.fromtimestamp(int(unix_timestamp))

# Function to smooth GPS coordinates
def smooth_coordinates(coordinates, tolerance):
    smoothed_coords = [coordinates[0]]

    for i in range(1, len(coordinates)-1):
        dist_prev = geodesic(coordinates[i-1][:2], coordinates[i][:2]).meters
        dist_next = geodesic(coordinates[i][:2], coordinates[i+1][:2]).meters

        if min(dist_prev, dist_next) > tolerance:
            smoothed_coords.append(coordinates[i])

    smoothed_coords.append(coordinates[-1])
    return smoothed_coords

# Function to convert CSV to GPX
def convert_csv_to_gpx(csv_file, gpx_file):
    gpx = gpxpy.gpx.GPX()

    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)

    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        coordinates = []

        for row in reader:
            lat = float(row['latitude'])
            lon = float(row['longitude'])
            ele = float(row['altitude'])
            timestamp = unix_timestamp_to_datetime(row['dataTime'])

            coordinates.append((lat, lon, ele, timestamp))

    # Smoothing the coordinates
    smoothed_coordinates = smooth_coordinates(coordinates, tolerance=10)  # Adjust tolerance as needed

    segment = None
    prev_date = None

    for coord in smoothed_coordinates:
        lat, lon, ele, timestamp = coord
        date = timestamp.date()

        if date != prev_date:
            segment = gpxpy.gpx.GPXTrackSegment()
            gpx_track.segments.append(segment)

        point = gpxpy.gpx.GPXTrackPoint(lat, lon, elevation=ele)
        point.time = timestamp
        segment.points.append(point)

        prev_date = date

    with open(gpx_file, 'w') as file:
        file.write(gpx.to_xml())

    print('Conversion completed successfully.')

# Usage example
csv_file = 'backUpData.csv'  # Replace with your CSV file path
gpx_file = 'data.gpx'  # Replace with the desired GPX file path

convert_csv_to_gpx(csv_file, gpx_file)
