# p:IGI+ Interaction

As of the time of writing (4th Oct 2022) the following base URLs can be used:

`base_api_uri`: https://igi-ml.azurewebsites.net/ (this is the backend - this is a spike that is being reviewed / replaced)

`website`: https://proud-grass-00b32de03.1.azurestaticapps.net/ (front end - this is a vue js app, this deployment is for the dev branch)

`csv_file_path`: example csv files can be found here: https://github.com/IGILtd/IGI.ML.UI/tree/main/cypress/fixtures

Note the backend {{base_api_uri}} is still a spike at the moment (v1 in progress). The v1 implementation will have swagger docs to replace this documentation. I have documented here what we have done in the spike along with a section discussing changes that will be needed.

The current p:IGI integration spike is: https://github.com/IGILtd/IGI.Apps/tree/feature_spike_regression_integration

## Train a regression model

At a high level pIGI identifies the data (for training) and the target property to write to then hands off to the web app to choose modelling options, perform preprocessing, train the model and provide evaluation plots / metrics.

Launching the app for the training is done as a two step process, which allows us to first send the data and get a session_ref, then open the training site. 

### Step 1 - Save file via the API

Request:

```http
POST {{base_api_uri}}/api/add_session_data
Form: data="{{csv_file_path}}"
```

*I propose that we add a version e.g.*: `{{base_api_uri}}/api/v1/add_session_data`

Example Response:

```json
{
    "session_ref": "d44886a3-fb73-4506-af8c-22a436b27321"
}
```

*Note*: We will likely need to send more data than just the csv file at some point. Ideally we would have any relevant guids for the `p[i].a<u>{r}` so that if there are PM renames the app can tell that they are still the same columns. TBD whether we do this for v1...

### Step 2 - Launch the website with the session_ref as a query param

```
{{website}}?session_ref=d44886a3-fb73-4506-af8c-22a436b27321
```

This way when you hit the site it already has the source data, can offer the column headers for options as the result column etc.

## Save a regression model / get predictions for the training data

This part is initiated via the web app. When the user has finished the training/evaluation loop and selects save model the app uses webview to send data back to the host application (p:IGI+).

### Webview message ML App -> pIGI

We have followed the same basic structure used for Discover integration, messages from the web app are in json form with two top level keys: `action` and `data`. The action can be used in pigi to route the message to an appropriate handler.

```json
{
    "action": "persist_model_artefact_data",
    "data": {
        "predictions": [
            46.886704593042246,
            58.894895072188994,
            ...],
        "serialised_model_artefact": "..."
    }
}
```

The `predictions` key is an array of numbers (float). The number and order should match the samples passed in (these will be written to the target property by pIGI).

The `serialised_model_artefact` key is an encoded binary string (pickle format base64 encoded) that allows python to rebuild the model when needed later for predictions/changes (this will be stored with the artefact).

Example with data [on Trello here](https://trello.com/c/2YQlvZ6f/3793-ml-project-spike-pigi-interaction-with-web-app#comment-62a9a828a2ecb56a73b74923).

**Todo**: If we allow datasets with null in the result column to be sent (note the result column is currently defined in the web app), then we will need to handle these - at present they are just removed from the dataset in the spike (to prevent a trainin error), but this would make the predictions returned out of sync with the samples sent and p:IGI would not know which samples are missing. Options to resolve:

1. Keep existing predictions structure, do not predict any values that have null result column (at the training stage) and add an excluded indices key (this is the least work on the web app).
2. Send sample ids with the source data and change the structure of the predictions response to give a result for each sample id so that it's clear which value must be written for each sample (we can then also decide whether the prediction is returned for unlabled data i.e. null result column at training stage).
3. Keep existing predictions structure, but change the web app to first train the model with the rows that have result column data, apply the model to the nulls and return all (retaining the original order) - seems a bit risky as it would not be possible to validate that the order is correct.

*Note*: Future versions will include more data e.g. uncertainty data.

## Apply a regression model

This can be done via the web service rather than launching the website again. 

Example scenario: you want to predict pX from various input columns (pA, pB, pC). You already know pX for 100 samples. The 100 "labelled" samples are used to train the model, the model is then applied to the unlabelled samples (using pA, pB & pC).

Request:

```http
POST {{base_api_uri}}/api/regression/apply
Form: data="{{csv_file_path}}"
      model="{{path_to_model_file}}"
```

*I propose that we add a version e.g.*: `{{base_api_uri}}/api/v1/regression/apply`

Example Response:

```json
{
    "predictions": [
        46.32978184645892,
        59.28284061293915,
        47.79245867506524,
        ...]
}
```

One prediction (float) should be returned per sample sent in. **The columns in the file submitted {{csv_file_path}} must match the columns used to train the model** (except the result column which can be excluded or left in to be excl by the web service).

*Note*: Future versions will include more data e.g. uncertainty data.

## Errors

At present in the spike error responses take the form:

```json
{
    "error": "{msg}",
    "traceback": [...]
}
```

e.g.

```json
{
    "error": "'SimpleImputer' object has no attribute '_fit_dtype'",
    "traceback": [
        "Traceback (most recent call last):",
        "  File \"/tmp/8daa6c126c97069/antenv/lib/python3.9/site-packages/flask/app.py\", line 1820, in full_dispatch_request",
        ...
        "AttributeError: 'SimpleImputer' object has no attribute '_fit_dtype'"
    ]
}

We can discuss whether it is appropriate to send this kind of detail as the web response or whether we should log the error and send a more generic response.

# Other APIs

I have not yet documented the APIs used by the vue app. These can be added here if needed, otherwise they will be in the swagger docs when we have replaced the spike with a v1. It may be worth just discussing conventions if we want an easy way to differentiate endpoints that are for consumption by the vue app vs end points integration with p:IGI.

We have not yet added an API for p:IGI to ask which services are available e.g. regression, classification etc - this will need to be planned.