from gerbil_api_wrapper.gerbil import Gerbil
from unittest.mock import patch
import pytest
from unittest import TestCase
import logging


class TestWrapper(TestCase):

    logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

    gold_standard_file = "./tests/results_gold.json"
    test_results_file = "./tests/result_test.json"
    language = "en"
    live_annotator_name = "QAnswer"
    live_annotator_url = "http://porque.cs.upb.de:40123/qanswer/gerbil"


    def test_initialize_wrapper_with_local_files(self):
        with patch('gerbil_api_wrapper.gerbil.Gerbil.upload_experiment_configuration') as mocked_upload_experiment_configuration, \
                patch('gerbil_api_wrapper.gerbil.Gerbil.upload_file') as mocked_upload_file, \
                patch('gerbil_api_wrapper.gerbil.Gerbil.is_url_valid') as mocked_is_url_valid:
            try:
                wrapper = Gerbil(
                    gold_standard_file=self.gold_standard_file, language=self.language,
                    test_results_file=self.test_results_file
                )
                assert wrapper.use_live_annotator == False

                assert mocked_upload_file.call_count == 2
                assert mocked_upload_file.call_args_list[0].args == (
                    self.gold_standard_file, 
                    'GoldStandard',
                    'application/json')
                assert mocked_upload_file.call_args_list[1].args == (
                    self.test_results_file,
                    'TestResults',
                    'application/json',
                    self.gold_standard_file)

                # assert values are stored in wrapper object
                assert wrapper.gold_standard_file == self.gold_standard_file
                assert wrapper.test_results_file == self.test_results_file
                assert wrapper.language == self.language

                # assert the configuration upload function was called
                mocked_upload_experiment_configuration.assert_called()
                mocked_is_url_valid.assert_called()
            except Exception:
                assert False


    def test_initialize_wrapper_with_live_annotator(self):

        with patch('gerbil_api_wrapper.gerbil.Gerbil.upload_experiment_configuration') as mocked_upload_experiment_configuration, \
                patch('gerbil_api_wrapper.gerbil.Gerbil.upload_file') as mocked_upload_file, \
                patch('gerbil_api_wrapper.gerbil.Gerbil.is_url_valid') as mocked_is_url_valid:
            try:
                wrapper = Gerbil(
                    gold_standard_file=self.gold_standard_file, language=self.language,
                    live_annotator_name=self.live_annotator_name,
                    live_annotator_url=self.live_annotator_url
                )
                assert wrapper.use_live_annotator == True

                assert mocked_upload_file.call_count == 1
                assert mocked_upload_file.call_args_list[0].args == (
                    self.gold_standard_file, 
                    'GoldStandard',
                    'application/json')

                # assert values are stored in wrapper object
                assert wrapper.gold_standard_file == self.gold_standard_file
                assert wrapper.live_annotator_name == self.live_annotator_name
                assert wrapper.live_annotator_url == self.live_annotator_url
                assert wrapper.language == self.language

                # assert the configuration upload function was called
                mocked_upload_experiment_configuration.assert_called()
                mocked_is_url_valid.assert_called()
            except Exception:
                assert False


    def test_initialization_without_files_or_annotator_fails(self):
        with pytest.raises(Exception):
            Gerbil(
                gold_standard_file=self.gold_standard_file, language=self.language)
