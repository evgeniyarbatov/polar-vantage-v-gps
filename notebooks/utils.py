import gpxpy
import psycopg2

import pandas as pd

from pytz import timezone
from geopy.distance import geodesic

FIXED_TIMESTAMP = '2024-05-26 22:19:06+00:00'

def get_db_conn():
  return psycopg2.connect(
    host="localhost",
    database="gpx",
    user="root",
    password="root"
  )

def parse_gpx(gpx_filepath):
  with open(gpx_filepath, 'r') as gpx_file:
    gpx = gpxpy.parse(gpx_file)

  data = []

  for track in gpx.tracks:
    for segment in track.segments:
      for point in segment.points:
        data.append((
          point.time if point.time else FIXED_TIMESTAMP,
          point.latitude, 
          point.longitude,
        ))
        
  return data

def init_postgis(table_name, gpx_filepath):  
  query = f"""
DROP TABLE IF EXISTS {table_name};

CREATE TABLE IF NOT EXISTS {table_name} (
  id SERIAL PRIMARY KEY,
  time TIMESTAMPTZ,
  location GEOMETRY(Point, 4326)
);
"""

  conn = get_db_conn()
  with conn.cursor() as cur:
    cur.execute(query)

  try:
      gpx_points = parse_gpx(gpx_filepath)
      for point in gpx_points:
          time, latitude, longitude = point
          with conn.cursor() as cur:
            cur.execute(f"""
              INSERT INTO {table_name} (time, location)
              VALUES ('{time}', ST_SetSRID(ST_MakePoint({longitude}, {latitude}), 4326))
            """) 
      conn.commit()
  except Exception as e:
    print(e)
    conn.rollback()

def get_location_error(table_name):
  query = f"""
WITH ordered_route_points AS (
    SELECT location
    FROM gpx_route
    ORDER BY id
),
route_linestring AS (
    SELECT ST_MakeLine(ST_Transform(location, 3857)) AS route
    FROM ordered_route_points
)

SELECT
    time,
    ST_Y(location) AS latitude,
    ST_X(location) AS longitude,
    ST_Distance(ST_Transform(location, 3857), (SELECT route FROM route_linestring)) AS distance_to_route
FROM
    {table_name};
"""
  conn = get_db_conn()
  with conn.cursor() as cur:
      cur.execute(query)
      rows = cur.fetchall()

  df = pd.DataFrame(rows, columns=["time", "latitude", "longitude", "distance_to_route"])
  df['time'] = df['time'].apply(lambda x: x.astimezone(timezone('Asia/Singapore')))

  return df

def crop_route(df, start_location, stop_location, start_point_count):
  df['start_distance'] = df.apply(lambda row: geodesic((row['latitude'], row['longitude']), start_location).meters, axis=1)
  df['stop_distance'] = df.apply(lambda row: geodesic((row['latitude'], row['longitude']), stop_location).meters, axis=1)
  
  start_point_idx = df.iloc[:start_point_count]['start_distance'].idxmin()
  end_point_idx = df.iloc[-200:]['stop_distance'].idxmin()
  
  df = df.iloc[start_point_idx:end_point_idx]
  
  return df

def get_total_distance(df):
  df['prev_latitude'] = df['latitude'].shift(1)
  df['prev_longitude'] = df['longitude'].shift(1)

  df = df.dropna().reset_index(drop=True)

  df['distance'] = df.apply(lambda x: geodesic((x['prev_latitude'], x['prev_longitude']), (x['latitude'], x['longitude'])).meters, axis=1)
  df['accumulated_distance'] = df['distance'].cumsum()
  
  return df