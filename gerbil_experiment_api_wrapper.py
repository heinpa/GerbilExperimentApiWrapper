import urllib, urllib3
import json
import requests
import time
from bs4 import BeautifulSoup
import pprint

class GerbilBenchmarkService:

    headers = {'Content-Type': 'multipart/form-data'}
    file_upload_url = "http://gerbil-qa.cs.uni-paderborn.de:8080/gerbil/file/upload"
    upload_configuration_url = "http://gerbil-qa.aksw.org/gerbil/execute?"
    check_running_url = "http://gerbil-qa.aksw.org/gerbil/running"
    get_experiment_url = "http://gerbil-qa.aksw.org/gerbil/experiment?id="

    gold_standard_name = "GoldStandard"
    test_results_name = "TestResults"

    anser_files_prefix = "AF"
    uploaded_dataset_prefix = "NIFDS"

    success = False


    def __init__(self, gold_standard_file, test_results_file, language):
        self.gold_standard_file = gold_standard_file
        self.test_results_file = test_results_file
        self.language = language
        # TODO: only return if data uploaded successfully? 

        self.upload_file(self.gold_standard_file, self.gold_standard_name, 'application/json')
        self.upload_file(self.test_results_file, self.test_results_name, 'application/json', self.gold_standard_file)
        self.upload_experment_configuration()

        if self.success:
            return
        else:
            raise Exception(f"could not init GerbilBenchmarkService")
        
        
    def upload_experment_configuration(self):
        # TODO: return status code and response?

        ## QUERY service with configuration
        url_postfix = """experimentData={{"type":"QA","matching":"STRONG_ENTITY_MATCH","annotator":[],"dataset":["{dataset}"],"answerFiles":["{answerFiles}"],"questionLanguage":"{questionLanguage}"}}"""

        execute_url = self.upload_configuration_url + url_postfix.format(
            dataset = f"{self.uploaded_dataset_prefix}_{self.gold_standard_name}({self.gold_standard_file})",
            answerFiles = f"{self.anser_files_prefix}_{self.test_results_name}({self.test_results_file})(undefined)(AFDS_{self.gold_standard_file})",
            questionLanguage = self.language
        )
        is_ok = False
        while not is_ok:
            try:
                # if no other experiment is running
                if requests.get(self.check_running_url).text == '':
                    # get experient id
                    response = requests.get(execute_url)
                    if response.status_code == 200:
                        self.experiment_id = response.text
                        print(f"started experiment: {self.get_experiment_url}{self.experiment_id}")
                        is_ok = True
                        self.success = True
                else:
                    print("waiting ...")
                    time.sleep(60)
            except:
                print("request failed")
                # TODO: handle?

        # TODO: check and return


    def get_results_url(self):
        # TODO: return URL of specific gerbil website for started experiment
        return self.get_experiment_url + self.experiment_id


    def get_results(self):
        query_url = self.get_results_url()

        soup = BeautifulSoup(requests.get(query_url).text, "html.parser")
        data = json.loads(
            "".join(soup.find("script", type="application/ld+json").contents)
        )
        data = [
            json.loads(x.string) for x in soup.find_all("script", type="application/ld+json")
        ]
        pprint.pprint(data)
        
        
        # TODO: return JSON-LD data as dict, extracted from specific Gerbil website for exp.
        # post to get_experiment_url
        # read html and extract jsonLD data
        # pack into json object, return (or just string, idfk)
        # **might need to wait for experiement to be finished**


    def read_file_bytes(self, file):
        return open(file, 'rb')


    def upload_file(self, file, name, type, multiselect=None):
        files = {
            # refactor
            # application type can be part of file object information
            "file": (file, self.read_file_bytes(file), type)
        }
        data = {
            'name': name,
            'multiselect': multiselect # TODO: check how None value influences upload
        }
        request = requests.post(self.file_upload_url, data=data, files=files)
        response = request.json()
        # check response
        if request.status_code == 200:
            print(response)
            return response
        else: 
            raise Exception(f"file upload not successful: {request.status_code}: {request.content}")


