import json
import requests
import time
from bs4 import BeautifulSoup
import validators
from pathlib import Path
import logging
from urllib.parse import urlparse


logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)


class Gerbil:

    #file_upload_url = "http://gerbil-qa.cs.uni-paderborn.de:8080/gerbil/file/upload"
    file_upload_url = "https://gerbil-qa.aksw.org/gerbil/file/upload"
    upload_configuration_url = "https://gerbil-qa.aksw.org/gerbil/execute?"
    check_running_url = "https://gerbil-qa.aksw.org/gerbil/running"
    get_experiment_url = "https://gerbil-qa.aksw.org/gerbil/experiment?id="

    gold_standard_name = "GoldStandard"
    test_results_name = "TestResults"

    live_annotator_prefix = "NIFWS"
    uploaded_dataset_prefix = "NIFDS"
    dataset_reference_prefix = "AFDS"
    answer_files_prefix = "AF"

    upload_data_template = """experimentData={{"type":"QA","matching":"STRONG_ENTITY_MATCH","annotator":[{annotator}],"dataset":["{dataset}"],"answerFiles":[{answerFiles}],"questionLanguage":"{questionLanguage}"}}"""

    check_for_another_experiments = False

    def __init__(self, language, gold_standard_file, **kwargs):
        """
        Parameters
        ---------
        gold_standard_file : str, required
            The path to a gold standard dataset
        gold_standard_name : str, optional
            The name of the gold standard dataset
        test_results_file : str, optional
            The path to a test result dataset to be used *instead* of a live annotator
        test_results_name : str, optional
            The name of the test results dataset
        live_annotator_name : str, optional
            The name of a live annotator to be used *instead* of local test results; 
            requires a value for 'live_annotator_url'
        live_annotator_url : str, optional
            The URL for a live annotator; requires a value for 'live_annotator_name'
        language : str, required
            The question language
        """

        # gold standard file and language always needs to be defined
        self.gold_standard_file = gold_standard_file
        self.language = language
        self.test_results_file = kwargs.get('test_results_file')
        self.live_annotator_name = kwargs.get('live_annotator_name')
        self.live_annotator_url = kwargs.get('live_annotator_url')

        self.gold_standard_name = kwargs.get('gold_standard_name', self.gold_standard_name)
        self.test_results_name = kwargs.get('test_results_name', self.test_results_name)

        self.check_for_another_experiments = kwargs.get('check_for_another_experiments', self.check_for_another_experiments)

        # upload files / set live annotator (prefer local files)
        self.upload_file(self.gold_standard_file, self.gold_standard_name, 'application/json')

        # setup with local files
        if self.test_results_file:
            self.use_live_annotator = False
            self.upload_file(self.test_results_file, self.test_results_name, 'application/json')

        # setup with live annotator
        if self.live_annotator_url:
            self.use_live_annotator = True
            self.set_live_annotator(self.live_annotator_name, self.live_annotator_url)
        elif not self.test_results_file and not self.live_annotator_url:
            raise Exception(f"Could not initialize GerbilBenchmarkService!"
                            + "Missing results file or live annotator.")

        # run experiment with set configuration
        self.experiment_id = self.upload_experiment_configuration()
        if self.is_url_valid(self.get_results_url()):
            logging.info(f"initialized GerbilExperimentApiWrapper with experiment: {self.get_experiment_url}{self.experiment_id}")
        else:
            raise Exception(f"Could not initialize GerbilBenchmarkService!"
                            + "The experiment did not return valid results.")


    def is_url_valid(self, results_url):
        # basic validation of the result url
        if validators.url(results_url):
            return True
        else:
            return False


    def set_live_annotator(self, name, url):
        if self.is_url_valid(url):
            self.annotator = f"{self.live_annotator_prefix}_{name}({url})"
        else:
            raise Exception(f"Invalid annotator URL for annotator {name}: {url}")


    def upload_experiment_configuration(self):
        execute_url = self.upload_configuration_url + self.upload_data_template.format(
            dataset = f"{self.uploaded_dataset_prefix}_{self.gold_standard_name}({self.gold_standard_name})",
            answerFiles = f"\"{self.answer_files_prefix}_{self.test_results_name}({self.test_results_name})(undefined)({self.dataset_reference_prefix}_{self.gold_standard_name})\""
                if not self.use_live_annotator else "",
            annotator = f"\"{self.annotator}\"" if self.use_live_annotator else "",
            questionLanguage = self.language
        )

        logging.info(f"\nUpload experiment configuration: {execute_url}")

        cnt = 0
        while cnt < 5:
            try:
                # check that no other experiment is running
                if not self.check_for_another_experiments or requests.get(self.check_running_url).text == '':
                    # execute reauest with experiment configuration
                    response = requests.get(execute_url)
                    if response.status_code == 200:
                        return response.text # return the experiment id 
                else:
                    logging.info("another experiment is running, waiting for 60 seconds ...")
                    cnt += 1
                    time.sleep(60)
            except:
                logging.info("request failed, retrying ...")
                cnt += 1
        raise Exception(f"could not complete request after {cnt} attempts")


    def get_results_url(self):
        return self.get_experiment_url + self.experiment_id


    def get_results(self):
        query_url = self.get_results_url()
        # extract json-ld from response content
        soup = BeautifulSoup(requests.get(query_url).text, "html.parser")
        data = [
            json.loads(x.string) for x in soup.find_all("script", type="application/ld+json")
        ]
        return data[0]


    def upload_file(self, file, name, type):
        """Upload gold starndard or test results file to be used in the experiment

        Parameters
        ----------
        file : str, required
            The file path
        name : str, required
            The name to be used in the experiment configuration
        type : str, required
            The application type for the file
        multiselect : bool, optional
            The path to the referenced gold standard file when uploading test results
        """

        if len(name) > 100:
            raise Exception("File names must not exceed 100 characters!")
        # TODO: figure out how upload handles file paths
        # currently the server responds with 500, seeminly because it's out of space
        files = {
            "file": (name, open(file, 'rb'), type)
        }
        data = {
            'name': name
            # 'multiselect': multiselect
        }
        try:
            logging.info(f"\nRequest to: {self.file_upload_url}\n" + \
                         f"Data: {data}\n" + \
                         f"Files: {files}")
            request = requests.post(self.file_upload_url, data=data, files=files)
            response = request.json()
            # store the response, mainly for test purposes
            # TODO: change? 
            logging.info(f"Got response: {response} ({request.status_code})")
            if request.status_code != 200:
                raise Exception(f"file upload not successful: {request.status_code}: {request.content}")
            else: return response
        except Exception as e:
            raise Exception(f"file upload not successful: {e}")
