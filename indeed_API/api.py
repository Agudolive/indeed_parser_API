import json
import csv
import types
import pandas as pd
from pathlib import Path
from flask import Flask
from flask import Response
from flask_restplus import Resource, Api, inputs

# I decided to use the Flask RestPlus extension for Flask,
# it makes building APIs easier and Swagger is embed by default
app = Flask(__name__)
api = Api(app, title="indeed_API", validate=True)

CURRENT_PATH = Path(__file__)

JOB_OFFERS_CSV_FILE_PATH = str(CURRENT_PATH.parent.parent) + '\\indeed_scrapper\\job_offers.csv'

# I use pandas to manipulate my dataset
# There is no need to convert it into JSON
# I use cp1250 encoding since my dataset contains french accents and symbols like €
df = pd.read_csv(JOB_OFFERS_CSV_FILE_PATH, encoding='cp1250')

jo = api.namespace('job_offers')

# Using REST's standards means one resource = one URI
# Since it's a dataset and not a database, the purpose is different,
# there is no need to add a POST or PUT verb. Data are scrapped online, not added manually
@jo.route("/",)
@jo.param('department', 'Department where the job offer is located (ex: 75)', 'query', type='string')
@jo.param('location', 'Location of the job offer (ex: Paris)', 'query', type='string')
@jo.param('company', 'Company emitting the job offer (ex: Apple)', 'query', type='string')
@jo.param('company_rating', 'Minimum rating of the company emiting the offer (ex: 4)', 'query', type='float')
@jo.param('easy_apply', 'Whether you can apply using embed tool', 'query', type='boolean')
@jo.param('remote', 'Whether the job is remote', 'query', type='boolean')
@jo.param('urgently_hiring', 'Whether the company is hiring urgently', 'query', type='boolean')
class JobOffers(Resource):
    def get(self):
        # Here I add all the URI params I will use to filter data
        parser = jo.parser()
        parser.add_argument('department')
        parser.add_argument('location')
        parser.add_argument('company', help='Some param')
        parser.add_argument('company_rating', type=float)
        parser.add_argument('easy_apply', type=inputs.boolean)
        parser.add_argument('remote', type=inputs.boolean)
        parser.add_argument('urgently_hiring', type=inputs.boolean)
        args = parser.parse_args()
        # Return the filtered dataframe converted to JSON
        return Response(request_builder(args, df).to_json(orient="records"), mimetype='application/json')

# Custom pandas request builder to dynamically handle request parameters
# It takes args and the dataframe in parameters
# args is a dictionnary containing the names of the params as the key and their values as the value
def request_builder(args, df) -> pd.DataFrame:
    filtered_df = df
    # For each key, I query the dataframe
    for key in args:
        if args[key] != None:
            # Queries are different for each type
            if isinstance(args[key], bool):
                req = key + '==' + str(args[key])
            elif isinstance(args[key], float):
                req = key + '>=' + str(args[key])
            else:
                req = key + '==\"' + str(args[key]) + "\""
            filtered_df = filtered_df.query(req)
    return filtered_df

if __name__ == "__main__":
    app.run(debug=True)
