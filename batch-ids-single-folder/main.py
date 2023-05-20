import pathlib
import sys
import os
import requests
import base64
import json
import time
import datetime
from flatten_json import flatten
import pandas as pd

BASE_URL = 'https://demo-api.incodesmile.com/omni/'
API_KEY = '<your-api-key>'
FLOW_ID = '<your-flow-id>'
DIRECTORY = '<your-folder-name>'
OUTFILE_NAME = '<your-output-filename>'


def do_base64_encoded(path):
    file = open(path, 'rb')
    file_bytes = file.read()
    file.close()
    return base64.b64encode(file_bytes).decode('utf-8')

def to_excel(data, file_name):
    df = pd.DataFrame(data)
    excel_file = file_name + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + '.xlsx'
    df.to_excel(excel_file, index=False)
    print("Excel file created: ", excel_file)


class Session:
    def __init__(self, base_url, api_key, documents, flow_id=None) -> None:
        self.base_url = base_url
        self.api_key = api_key
        self.flow_id = flow_id
        self.documents = documents
        self.interview_id = ''
        self.s = requests.Session()
        self.s.stream = False
        self.s.headers.update({
            'x-api-key': self.api_key,
            'api-version': '1.0'
        })
        
    def start(self):
   
        r = self.s.post(
            self.base_url + 'start',
            json = {
                "countryCode": 'US',
                "configurationId": self.flow_id,
                "customFields": self.documents
            }
        )
        resp = r.json()
        self.interview_id = resp['interviewId']
        self.s.headers.update({
            'x-api-key': self.api_key,
            'X-Incode-Hardware-Id': resp['token'],
            'api-version': '1.0',
            'Content-type': 'application/json'
        })

        interview = {}
        interview['_id'] = resp['interviewId']
        interview['documents'] = self.documents
        print("Processing " + str(interview))
        return interview
        
        
    def upload_front_id(self):
        data = do_base64_encoded(self.documents['front_id'])
        r = self.s.post(
            self.base_url + 'add/front-id/v2',
            json = {
                "base64Image": data
            }
        )
        return r.json()
    
    def upload_back_id(self):
        data = do_base64_encoded(self.documents['back_id'])
        r = self.s.post(
            self.base_url + 'add/back-id/v2',
            json = {
                "base64Image": data
            }
        )
        return r.json()
    
    
    def upload_selfie(self):
        data = do_base64_encoded(self.documents['selfie'])
        r = self.s.post(
            self.base_url + 'add/face/third-party?imageType=selfie',
            json = {
                "base64Image": data
            }
        )
        return r.json()
        
    def poll(self):
        def _poll():
            r = self.s.get(
                self.base_url + 'get/postprocess/isfinished?id=' + self.interview_id
            )
            status = r.json()
            if not status['finished']:
                time.sleep(.34)
                _poll()
        _poll()
        
        
    def process_id(self):
        r = self.s.post(
            self.base_url + 'process/id',
            json={},
        )
        return r.json()
    
    
    def process_face(self):
        r = self.s.post(
            self.base_url + 'process/face',
            json={},
        )
        return r.json()
        
        
    def government_validation(self):
        r = self.s.post(
            self.base_url + 'process/government-validation',
            json={},
        )
        return r.json()


    def finish(self):
        r = self.s.get(
            self.base_url + 'finish-status'
        )
    
    def get_scores(self):
        r = self.s.get(
            self.base_url + 'get/score'
        )

        return r.json()
    
    def get_ocr(self):
        r = self.s.get(
            self.base_url + 'get/ocr-data?id='+ self.interview_id
        )
        return r.json()
        
    
        
    def run(self):
        interview = self.start()
        self.upload_front_id()
        self.upload_back_id()
        self.process_id()
        self.government_validation()
        self.poll()
        scores = self.get_scores()
        return { **interview, **scores }
    

def main():
    print("Starting to execute the batch!")

    jobs = []
    scores = []

    files = os.listdir(DIRECTORY)
    for file in files:
        docs = {}
        needle = file[:-5]
        if os.path.isfile(os.path.join(DIRECTORY, file)):
            for f in files:
                if needle in f:
                    docs['key'] = needle
                    if f[-5] == 'F':
                        docs['front'] = os.path.join(DIRECTORY, f)
                    else:
                        docs['back'] = os.path.join(DIRECTORY, f)

            filtered_data = list(filter(lambda item: item.get('key') == needle, jobs))
            if len(filtered_data) == 0:
                jobs.append(docs)

    
    for job in jobs:
        if 'front' in job and 'back' in job:
            docs = { "front_id": job['front'], "back_id": job['back']}
            sess = Session(BASE_URL, API_KEY, docs, FLOW_ID)
            result = sess.run()
            flat_result = flatten(result)
            scores.append(flat_result)

    to_excel(scores, OUTFILE_NAME)
    

if __name__ == "__main__":
    main()


