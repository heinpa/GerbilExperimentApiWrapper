# TODO: test with live Gerbil API url 
# TODO: disable by default? -> how to enable via param
from gerbil_api_wrapper.gerbil import Gerbil
from unittest import TestCase
import logging
from urllib.parse import urlparse
import time


class TestWrapperLive(TestCase):

    logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

    gold_standard_file = "./tests/results_gold.json"
    test_results_file = "./tests/result_test.json"
    language = "en"
    live_annotator_name = "QAnswer"
    live_annotator_url = "http://porque.cs.upb.de:40123/qanswer/gerbil"


    def test_initialize_live_wrapper_with_local_files(self):
        try:
            wrapper = Gerbil(
                gold_standard_file=self.gold_standard_file, language=self.language,
                test_results_file=self.test_results_file
            )
        except Exception:
            assert False

        expected_query = urlparse(wrapper.get_results_url()).query
        expected_annotator = f"http://gerbil-qa.aksw.org/gerbil/dataId/annotators/{wrapper.gold_standard_name}_(uploaded)"
        expected_dataset = f"http://gerbil-qa.aksw.org/gerbil/dataId/corpora/{wrapper.test_results_name}_(uploaded)"
        expected_language = f"http://gerbil-qa.aksw.org/gerbil/dataId/languages/{self.language}"

        query = None
        annotator = None
        dataset = None
        language = None

        assert wrapper.gold_standard_file == self.gold_standard_file
        assert wrapper.test_results_file == self.test_results_file
        assert wrapper.language == self.language

        assert wrapper.use_live_annotator == False
        assert wrapper.experiment_id != None

        cnt = 0
        while cnt < 5:
            if cnt > 0: time.sleep(60)
            try:
                results = wrapper.get_results()
                graph = results["@graph"]

                query = urlparse(graph[0]["@id"]).query
                annotator = graph[1]["annotator"]
                dataset = graph[1]["gerbil:dataset"]
                language = graph[1]["language"]
                break

            except Exception as e:
                logging.debug(e)
                logging.info("experiment not done, retrying ...")
                cnt += 1

        results = wrapper.get_results()
        graph = results["@graph"]

        assert query == expected_query
        assert annotator == expected_annotator
        assert dataset == expected_dataset
        assert language == expected_language


    def test_initialize_live_wrapper_with_live_annotator(self):
        try:
            wrapper = Gerbil(
                    gold_standard_file=self.gold_standard_file, language=self.language,
                    live_annotator_name=self.live_annotator_name,
                    live_annotator_url=self.live_annotator_url
            )
        except Exception:
            assert False

        expected_query = urlparse(wrapper.get_results_url()).query
        expected_annotator = f"http://gerbil-qa.aksw.org/gerbil/dataId/annotators/{wrapper.gold_standard_name}_(uploaded)"
        expected_dataset = f"http://gerbil-qa.aksw.org/gerbil/dataId/corpora/{wrapper.live_annotator_name}_(WS)"
        expected_language = f"http://gerbil-qa.aksw.org/gerbil/dataId/languages/{self.language}"

        query = None
        annotator = None
        dataset = None
        language = None

        assert wrapper.gold_standard_file == self.gold_standard_file
        assert wrapper.live_annotator_name == self.live_annotator_name
        assert wrapper.live_annotator_url == self.live_annotator_url
        assert wrapper.language == self.language

        assert wrapper.use_live_annotator == True
        assert wrapper.experiment_id != None

        cnt = 0
        while cnt < 5:
            if cnt > 0: time.sleep(60)
            try:
                results = wrapper.get_results()
                graph = results["@graph"]

                query = urlparse(graph[0]["@id"]).query
                annotator = graph[1]["annotator"]
                dataset = graph[1]["gerbil:dataset"]
                language = graph[1]["language"]
                break

            except Exception as e:
                logging.debug(e)
                logging.info("experiment not done, retrying ...")
                cnt += 1

        results = wrapper.get_results()
        graph = results["@graph"]

        assert query == expected_query
        assert annotator == expected_annotator
        assert dataset == expected_dataset
        assert language == expected_language
