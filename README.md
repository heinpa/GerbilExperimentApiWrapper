# GerbilExperimentApiWrapper

This API wrapper is meant to automate the testing of QA results with a standardized process
using [Gerbil for QA](http://gerbil-qa.aksw.org/gerbil/).

The `GerbilExperimentApiWrapper` object is initialized with a *Gold standard dataset*, 
a *test dataset* and the used *language*. 

As part of the initialization, the files are uploaded to the Gerbil service and an experiment
is started. 
If upload of the experiment configuration fails or the received results page URL is not valid, 
then an exception is thrown and the GerbilExperimentApiWrapper is *not* initialized.

**Example:** 

```
from gerbil_experiment_api_wrapper import GerbilExperimentApiWrapper

wrapper = GerbilExperimentApiWrapper(results_gold.json, result_test.json, "en")
```

* `get_results_url()` returns the URL of the Gerilb website for the started experiment.
* `get_results()` returns a dict containing the JSON-LD data for the started experiment.

**Note:** File names for the upload to the Gerbil API must not exceed 100 characters.
