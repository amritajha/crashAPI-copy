from flask import Flask, jsonify, request, make_response
from google.cloud import bigquery
import pandas as pd
import json
from pytz import timezone
from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests
import os

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

@app.route('/point_radius', methods=['GET'])
def point_radius():
    client = bigquery.Client(project='crash-api-281519')
    tz = timezone('EST')
    
    address = request.args.get('address')
    if address:
        url = 'https://maps.googleapis.com/maps/api/geocode/json'
        apiKey = os.environ.get('APIKEY')
        
        params = {'key': apiKey, 'address': address}
        res = requests.get(url, params=params)
        data = res.json()
        
        if res.ok and data['status'] == 'REQUEST_DENIED':
            return jsonify(data), 403

        elif res.ok and data['status'] == 'OK' and len(data['results']) > 0:
            latLong = data['results'][0]['geometry']['location']
            latitude = latLong['lat']
            longitude = latLong['lng']
        else:
            latitude = 0.0
            longitude = 0.0
    else:
        longitude = request.args.get('longitude', 0.0, type=float)
        latitude = request.args.get('latitude', 0.0, type=float)

    radius = request.args.get('radius', 24140.0, type=float)
    year = request.args.get('year', int(datetime.now(tz).strftime('%Y')), type=int)
    month = request.args.get('month', 1, type=int)

    query = """
        CALL `crash-api-281519.crashData.point_radius_p3`(@lon, @lat, @distance, @in_year, @in_month);
    """

    query_params = [bigquery.ScalarQueryParameter('lon', 'FLOAT64', longitude),
                    bigquery.ScalarQueryParameter('lat', 'FLOAT64', latitude),
                    bigquery.ScalarQueryParameter('distance', 'FLOAT64', radius),
                    bigquery.ScalarQueryParameter('in_year', 'INT64', year),
                    bigquery.ScalarQueryParameter('in_month', 'INT64', month)]

    job_config = bigquery.QueryJobConfig(dry_run=False, use_query_cache=True)
    job_config.query_parameters = query_params
    query_job = client.query(
        query,
        location="US",
        job_config=job_config,
    )

    rows = query_job.result()
    data = rows.to_dataframe()
    data = data.to_dict(orient='records')
    
    return jsonify(data), 200

@app.route('/road_fuzzy_match', methods=['GET'])
def road_fuzzy_match():
    client = bigquery.Client()

    tz = timezone('EST')
    dateFormat = '%Y-%m-%d'
    past = (datetime.now(tz) - relativedelta(years=1)).strftime(dateFormat)
    today = datetime.now(tz).strftime(dateFormat)

    roadName = request.args.get('road_name')
    if roadName == None:
        return jsonify('{status: 400, message: Invalid request}'), 400
    distance = request.args.get('distance', 10.0, type=float)
    startDate = request.args.get('start_date', past)
    endDate = request.args.get('end_date', today)
    threshold = request.args.get('threshold', 0.8, type=float)

    query = "CALL `crash-api-281519.crashData.road_fuzzy`('%s', %f, '%s', '%s', %f);" \
            %(roadName, distance, startDate, endDate, threshold) 
    
    job = client.query(query, location="US")
    rows = job.result()
    data = rows.to_dataframe()
    data = data.to_dict(orient='records')

    return jsonify(data), 200

@app.route('/find_crashinfo_by_county', methods=['GET'])
def find_crashinfo_by_county():
    client = bigquery.Client()

    tz = timezone('EST')
    dateFormat = '%Y-%m-%d'
    past = (datetime.now(tz) - relativedelta(years=1)).strftime(dateFormat)
    today = datetime.now(tz).strftime(dateFormat)

    countyString = request.args.get('county_string')
    if countyString == None:
        return jsonify('{status: 400, message: Invalid request}'), 400

    startDate = request.args.get('start_date', past)
    endDate = request.args.get('end_date', today)
    threshold = request.args.get('threshold', 0.8, type=float)

    query = "CALL `crash-api-281519.crashData.crashinfo_by_county`('%s', '%s', '%s', %f);" \
            %(countyString, startDate, endDate, threshold)

    job = client.query(query, location="US")
    rows = job.result()
    data = rows.to_dataframe()
    data = data.to_dict(orient='records')

    return jsonify(data), 200

@app.route('/vin_search/<string:vinCode>', methods=['GET'])
def vin_search(vinCode):
    client = bigquery.Client()

    query = "CALL `crash-api-281519.crashData.vin_search`('%s');" % vinCode

    job = client.query(query, location="US")
    rows = job.result()
    data = rows.to_dataframe()
    data = data.to_dict(orient='records')

    return jsonify(data), 200

@app.route('/map_pts_roads', methods=['POST'])
def map_pts_roads():
    if request.content_type and request.content_type.startswith('application/json'):
        client = bigquery.Client()
        data = request.get_json()
        points = data['pointInfo']
        radius = 30
        geopts = ['POINT(%s %s)' % (str(point['longitude']), str(point['latitude'])) for point in points]
        query = 'CALL `crash-api-281519.crashData.map_pts_roads`(@pts, @distance);'
        queryParams = [bigquery.ArrayQueryParameter('pts', 'GEOGRAPHY', geopts), 
                        bigquery.ScalarQueryParameter('distance', 'FLOAT64', radius)]
        jobConfig = bigquery.QueryJobConfig(dry_run=False, use_query_cache=True)

        jobConfig.query_parameters = queryParams
        queryJob = client.query(
            query,
            location='US',
            job_config=jobConfig,
        )
        res = queryJob.to_dataframe()
        res = res.to_dict(orient='records')
        
        return jsonify(res), 200
    else:
        return jsonify('Bad Request'), 400

@app.route('/_ah/warmup')
def warmup():
    return '', 200, {}

if __name__ == '__main__':
    app.run(host ='127.0.0.1', port=8080, debug=True)
