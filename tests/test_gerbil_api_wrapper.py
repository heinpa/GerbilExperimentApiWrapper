from gerbil_api_wrapper.gerbil import Gerbil
from unittest.mock import patch
import pytest


# TODO: live API tests
# TODO: mock return of API calls (result url, id)
# TODO: check if patches can be done with setUp or fixtures
# TODO: verify upload_file() params and final experiment_data

gold_standard_file = "./tests/results_gold.json"
test_results_file = "./tests/result_test.json"
language = "en"
live_annotator_name = "QAnswer"
live_annotator_url = "http://porque.cs.upb.de:40123/qanswer/gerbil"


@patch('gerbil_api_wrapper.gerbil.Gerbil.upload_experiment_configuration')
@patch('gerbil_api_wrapper.gerbil.Gerbil.upload_file')
@patch('gerbil_api_wrapper.gerbil.Gerbil.is_url_valid')
def test_initialize_wrapper_with_local_files(mock_upload_experiment_configuration, mock_upload_file, mock_is_url_valid):
    try:
        wrapper = Gerbil(
            gold_standard_file=gold_standard_file, language=language,
            test_results_file=test_results_file
        )
        assert wrapper.use_live_annotator == False
        assert mock_upload_file.called
        # assert values are stored in wrapper object
        assert wrapper.gold_standard_file == gold_standard_file
        assert wrapper.test_results_file == test_results_file
        assert wrapper.language == language
        # assert the configuration upload function was called
        assert mock_upload_experiment_configuration.called
        assert mock_is_url_valid.called
    except Exception:
        assert False


@patch('gerbil_api_wrapper.gerbil.Gerbil.upload_experiment_configuration')
@patch('gerbil_api_wrapper.gerbil.Gerbil.upload_file')
@patch('gerbil_api_wrapper.gerbil.Gerbil.is_url_valid')
def test_initialize_wrapper_with_live_annotator(mock_upload_experiment_configuration, mock_upload_file, mock_is_url_valid):
    try:
        wrapper = Gerbil(
            gold_standard_file=gold_standard_file, language=language,
            live_annotator_name=live_annotator_name,
            live_annotator_url=live_annotator_url
        )
        assert wrapper.use_live_annotator == True
        assert mock_upload_file.called
        # assert values are stored in wrapper object
        assert wrapper.gold_standard_file == gold_standard_file
        assert wrapper.live_annotator_name == live_annotator_name
        assert wrapper.live_annotator_url == live_annotator_url
        assert wrapper.language == language
        # assert the configuration upload function was called
        assert mock_upload_experiment_configuration.called
        assert mock_is_url_valid.called
    except Exception:
        assert False


def test_initialization_without_files_or_annotator_fails():
    with pytest.raises(Exception):
        Gerbil(
            gold_standard_file=gold_standard_file, language=language)
