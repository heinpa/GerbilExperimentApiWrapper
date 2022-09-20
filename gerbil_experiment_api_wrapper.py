import json
import requests
import time
from bs4 import BeautifulSoup
import validators

class GerbilExperimentApiWrapper:

    file_upload_url = "http://gerbil-qa.cs.uni-paderborn.de:8080/gerbil/file/upload"
    upload_configuration_url = "http://gerbil-qa.aksw.org/gerbil/execute?"
    check_running_url = "http://gerbil-qa.aksw.org/gerbil/running"
    get_experiment_url = "http://gerbil-qa.aksw.org/gerbil/experiment?id="

    gold_standard_name = "GoldStandard"
    test_results_name = "TestResults"

    uploaded_dataset_prefix = "NIFDS"
    dataset_reference_prefix = "AFDS"
    anser_files_prefix = "AF"


    def __init__(self, gold_standard_file, test_results_file, language):
        self.gold_standard_file = gold_standard_file
        self.test_results_file = test_results_file
        self.language = language

        self.upload_file(self.gold_standard_file, self.gold_standard_name, 'application/json')
        self.upload_file(self.test_results_file, self.test_results_name, 'application/json', self.gold_standard_file)
        self.experiment_id = self.upload_experment_configuration()

        if self.result_url_valid(self.get_results_url()):
            print(f"initialized GerbilExperimentApiWrapper with experiment: {self.get_experiment_url}{self.experiment_id}")
        else:
            raise Exception(f"could not initialize GerbilBenchmarkService")
        

    def result_url_valid(self, results_url):
        if validators.url(results_url):
            return True
        else:
            return False

        
    def upload_experment_configuration(self):
        url_postfix = """experimentData={{"type":"QA","matching":"STRONG_ENTITY_MATCH","annotator":[],"dataset":["{dataset}"],"answerFiles":["{answerFiles}"],"questionLanguage":"{questionLanguage}"}}"""
        execute_url = self.upload_configuration_url + url_postfix.format(
            dataset = f"{self.uploaded_dataset_prefix}_{self.gold_standard_name}({self.gold_standard_file})",
            answerFiles = f"{self.anser_files_prefix}_{self.test_results_name}({self.test_results_file})(undefined)({self.dataset_reference_prefix}_{self.gold_standard_file})",
            questionLanguage = self.language
        )
        cnt = 0
        while cnt < 5:
            try:
                # if no other experiment is running
                if requests.get(self.check_running_url).text == '':
                    response = requests.get(execute_url)
                    if response.status_code == 200:
                        return response.text
                else:
                    print("another experiment is running, waiting for 60 seconds ...")
                    cnt += 1 
                    time.sleep(60)
            except:
                print("request failed, retrying ...")
                cnt += 1 
        raise Exception(f"could not complete request after {cnt} attempts")


    def get_results_url(self):
        return self.get_experiment_url + self.experiment_id


    def get_results(self):
        query_url = self.get_results_url()
        soup = BeautifulSoup(requests.get(query_url).text, "html.parser")
        data = [
            json.loads(x.string) for x in soup.find_all("script", type="application/ld+json")
        ]
        return data[0]
        

    def read_file_bytes(self, file):
        return open(file, 'rb')


    def upload_file(self, file, name, type, multiselect=None):
        if len(file) > 100:
            raise Exception("File names must not exceed 100 characters!")
        files = {
            "file": (file, self.read_file_bytes(file), type)
        }
        data = {
            'name': name,
            'multiselect': multiselect 
        }
        request = requests.post(self.file_upload_url, data=data, files=files)
        response = request.json()
        if request.status_code == 200:
            return response
        else: 
            raise Exception(f"file upload not successful: {request.status_code}: {request.content}")


