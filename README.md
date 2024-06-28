# Polar Vantage V Satellites

Polar Vantage V has several options for positioning satellites:

- GPS + Glonass (default)
- GPS + Galileo
- GPS + QZSS

Which of these give better accuracy for my location?

## How it works

- Upload route and GPX files to PostGIS
- Calculate distance between GPX and route


## Use with your own routes

- Create GPX route of a segment you want to use for testing accuracy ([route.gpx](singapore/benjamin-sheares-bridge/route.gpx))
  - It is important that this is as precise as possible
- Go to Strava and correct elevevation on the activity. Download resulting GPX ([elevation.gpx](singapore/benjamin-sheares-bridge/elevation.gpx))
  - This will serve as the ground truth for the elevation
- Set Polar watch satellites to Glonass / Galileo / QZSS and record runs with each


