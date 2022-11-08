# GerbilExperimentApiWrapper

This API wrapper is meant to automate the testing of QA results with a standardized process
using [Gerbil for QA](http://gerbil-qa.aksw.org/gerbil/) 
(see also [Paper](https://dl.acm.org/doi/pdf/10.1145/2736277.2741626) and [GitHub repository](https://github.com/dice-group/gerbil)).

## initialization

The `Gerbil` object is initialized with a *Gold standard dataset*, 
a *test dataset* or alternatively a *live annotator*, as well as the used *language*. 

As part of the initialization, the files are uploaded to the Gerbil service and an experiment
is started. 
If upload of the experiment configuration fails or the received results page URL is not valid, 
then an exception is thrown and the api wrapper is *not* initialized.

**Note:** File names for the upload to the Gerbil API must not exceed 100 characters.

## Examples

Running an expeiment with a local test results file: 

```python
from gerbil_api_wrapper.gerbil import Gerbil

wrapper = Gerbil(
    gold_standar_file="results_gold.json",
    test_results_file="result_test.json",
    language="en")
```

Running an experiment with a live annotator: 

```python
from gerbil_api_wrapper.gerbil import Gerbil

wrapper = Gerbil(
    gold_standard_file="results_gold.json",
    live_annotator_name="QAnswer",
    live_annotator_url="http://qanswer-core1.univ-st-etienne.fr/api/gerbil",
    language="en")
```

After successful initialization the results can be accessed with the following functions: 

* `get_results_url()` returns the URL of the Gerilb website for the started experiment.
* `get_results()` returns a dict containing the JSON-LD data for the started experiment.

