# Ometry Atlas API - App Engine Standard

## Summary
This is a Flask application for Ometry Atlas API.
It contains five services
- /find_crashinfo_by_country (GET)
- /map_pts_roads (POST)
- /point_radius (POST)
- /road_fuzzy_match (GET)
- /vin_search/{vinCode} (GET)

## Resource Breakdown
- app.yaml
  - The app.yaml file describes an app's deployment configuration:
- requirements.txt
  - App Engine automatically installs dependencies found in your requirements.txt file.
- main.py
  - main.py is a Flask app for Ometry Atlas

## Deployment
- To deploy a version of the application's service, run the following command from the directory where the app.yaml file of your service is located
    - ```gcloud app deploy```
- Specifying no files with the command deploys the application(app.yaml, main.py and requirements.txt) in the current directory. By default, the deploy command generates a unique ID for the version that you deploy, deploys the version to the Google Cloud project you configured the gcloud tool to use, and routes all traffic to the new version.
