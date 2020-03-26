# The sample http url is:
# http://127.0.0.1:5000/api/v1/meeting?id=139016136604805407078985976850150049467&id=12&length=35&earliest_date=2-19-2014&earliest_time=10:30%20AM&latest_date=3-18-2014&latest_time=09:30%20AM&office_hours=08-12


from datetime import *

import flask
from flask import request


def time2halfanhour(minutes):
    if minutes % 30 == 0:
        return minutes // 30
    else:
        return (minutes // 30) + 1


with open('freebusy.txt', 'r') as f:
    lines = f.read().splitlines()

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return '''<h1>Meeting Suggestions</h1>
<p>An API to get suggestions for suitable meeting times.</p>'''


@app.route('/api/v1/meeting', methods=['GET'])
def api_id():
    # Check if necessary arguments were provided as part of the URL.
    # If they were provided, assign them to variables.
    # If at least one of them was not provided, display an error in the browser.
    if 'id' not in request.args:
        return "Error: No id field provided. Please specify an id."
    else:
        employeeid = request.args['id']
        if 'length' not in request.args:
            return "Error: No length field provided. Please specify a length"
        else:
            length = time2halfanhour(int(request.args['length']))
            if 'earliest_date' not in request.args:
                return "Error: No earliest_date field provided. Please specify an earliest_date"
            else:
                earliest_date = request.args['earliest_date']
                if 'earliest_time' not in request.args:
                    return "Error: No earliest_time field provided. Please specify an earliest_time"
                else:
                    earliest_time = request.args['earliest_time']
                    if 'latest_date' not in request.args:
                        return "Error: No latest_date field provided. Please specify a latest_date"
                    else:
                        latest_date = request.args['latest_date']
                        if 'latest_time' not in request.args:
                            return "Error: No latest_time field provided. Please specify a latest_time"
                        else:
                            latest_time = request.args['latest_time']
                            if 'office_hours' not in request.args:
                                return "Error: No office_hours field provided. Please specify office_hours"
                            else:
                                office_hours = request.args['office_hours']

    # Set variables
    result = ""
    UTC_OFFSET_TIMEDELTA = datetime.utcnow() - datetime.now()
    initial_time = datetime.strptime((earliest_date + " " + earliest_time), '%m-%d-%Y %I:%M %p') + UTC_OFFSET_TIMEDELTA
    end_time = datetime.strptime((latest_date + " " + latest_time), '%m-%d-%Y %I:%M %p') + UTC_OFFSET_TIMEDELTA
    office_hours_start = int(office_hours[1:2])
    office_hours_end = int(office_hours[3:5])

    suggested_time = initial_time
    found = False
    while suggested_time <= end_time:
        # Checks every line in the text file
        for line in lines:
            # Checks if the line is related to the employee we want
            if line.split(';')[0] == employeeid:
                # Checks if the line says the busy hours, not the name
                try:
                    busy_time_start = datetime.strptime(line.split(';')[1], '%m/%d/%Y %I:%M:%S %p')
                    busy_time_end = datetime.strptime(line.split(';')[2], '%m/%d/%Y %I:%M:%S %p')
                except:
                    continue
                # Checks if the suggested time is not in the busy hours
                if ((suggested_time + timedelta(minutes=(30 * length))).replace(tzinfo=None) <= busy_time_start.replace(tzinfo=None)) or (
                        suggested_time.replace(tzinfo=None) >= busy_time_end.replace(tzinfo=None)):
                    # Checks if the suggested time is in the office hours
                    if (int(str(suggested_time.strftime('%H'))) >= office_hours_start) and (
                            int(str((suggested_time + timedelta(minutes=30)).strftime('%H'))) <= office_hours_end) and (
                            int(str((suggested_time + timedelta(minutes=30)).strftime('%H'))) >= office_hours_start):
                        result += str(suggested_time - UTC_OFFSET_TIMEDELTA)
                        found = True
                        break
        # Checks if any result has been found
        if found:
            break
        else:
            suggested_time += timedelta(minutes=30)
    # Showing the result
    result = "The first time we could find is " + result
    return result


app.run()
