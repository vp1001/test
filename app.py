from flask import Flask, render_template, request
import pandas as pd

import os
import requests
from requests.auth import HTTPBasicAuth
import json
from dotenv import load_dotenv

load_dotenv()
#const port = process.env.PORT || 4000;

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/data', methods=['GET', 'POST'])
def data():
    if request.method == 'POST':
        file = request.form['upload-file']
        data = pd.read_excel(file,0)
        return render_template('data.html', data=data.to_html())#to_dict())

@app.route('/test')
def test():
    r = requests.post(
    "https://api.glideapp.io/api/function/queryTables",
    headers={"Authorization": "Bearer 19293213-a3a7-44db-bd93-7d8eb8fa67db"},
    json={
        "appID": "b8XL8g5V6S6wVUsfiviW",
        "queries": [
            {
                "tableName": "native-table-mzI1lKt2bZvmkT5bS9eY",
                "utc": True
            }
        ]
    }
    )
    result = r.json()
    #print(json.dumps(result, sort_keys=True, indent=4, separators=(",", ": ")))
    # Extract and print each 'Name' from the rows
    names = [row['Name'] for row in result[0]['rows']]
    rowID = [row['$rowID'] for row in result[0]['rows']]
    print(names[0])
    print(rowID[0])
 
    cql1 = 'space=FirstSpace and title ~ "'+names[0]+'"'
    print(cql1)
    url1 = "https://adaptiveaiventures.atlassian.net/wiki/rest/api/content/search"
 
    auth1 = HTTPBasicAuth(os.getenv("USER"), os.getenv("CONFLUENCE_API"))
    headers1 = {
        "Accept": "application/json"
    }
 
    query1 = {
       'cql': cql1
    }
 
    response = requests.request(
        "GET",
        url1,
        headers=headers1,
        params=query1,
        auth=auth1
    )
 
    #print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
 
    response_data = json.loads(response.text)
    base_url = response_data['_links']['base']
    for result in response_data['results']:
        title = result['title']
        history_link = base_url + result['_expandable']['history']
        print(f"Title: {title}, History Link: {history_link}")
 
        resp = requests.request(
            "GET",
            history_link,
            auth=auth1,
            headers=headers1
        )
 
        data = json.loads(resp.text)
        created_date = data['createdDate']
        email_last_updated = data['lastUpdated']['by']['email']
        friendly_when_last_updated = data['lastUpdated']['friendlyWhen']
        email_created_by = data['createdBy']['email']
 
        print("Created Date:", created_date)
        print("Email from Last Updated:", email_last_updated)
        print("Friendly When from Last Updated:", friendly_when_last_updated)
        print("Email from Created By:", email_created_by)
 
        webui_link = base_url + response_data['results'][0]['_links']['webui']
 
        t = requests.post(
        "https://api.glideapp.io/api/function/mutateTables",
        headers={"Authorization": "Bearer 19293213-a3a7-44db-bd93-7d8eb8fa67db"},
        json={
            "appID": "b8XL8g5V6S6wVUsfiviW",
            "mutations": [
            {
                "kind": "add-row-to-table",
                "tableName": "native-table-mShQaQDjhWALfGMOnUCM",
                "columnValues": {
                    "Name": rowID[0],
                    "RoNW7": title,
                    "Q1yAQ": webui_link,
                    "G7gJh": email_created_by,
                    "huCmP": created_date,
                    "iwU4x": email_last_updated,
                    "zzU8R": friendly_when_last_updated
                }
            }
        ]
        }
        )
        result = t.json()


if __name__ == '__main__':
    app.run(host="0.0.0.0", port = "10000")
