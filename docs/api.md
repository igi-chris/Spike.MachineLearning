# p:IGI+ Interaction

As of the time of writing (4th Oct 2022) the following base URLs can be used:

`base_api_uri`: https://igi-ml.azurewebsites.net/ (this is the backend - this is a spike that is being reviewed / replaced)

`website`: https://proud-grass-00b32de03.1.azurestaticapps.net/ (front end - this is a vue js app, this deployment is for the dev branch)

`csv_file_path`: example csv files can be found here: https://github.com/IGILtd/IGI.ML.UI/tree/main/cypress/fixtures

Note the backend {{base_api_uri}} is still a spike at the moment (v1 in progress). The v1 implementation will have swagger docs to replace this documentation. I have documented here what we have done in the spike along with a section discussing changes that will be needed.

## Train a regression model

At a high level pIGI identifies the data (for training) and the target property to write to then hands off to the web app to choose modelling options, perform preprocessing, train the model and provide evaluation plots / metrics.

Launching the app for the training is done as a two step process, which allows us to first send the data and get a session_ref, then open the training site. 

### Step 1 - Save file via the API

Request:

```http
POST {{base_api_uri}}/api/add_session_data
Form: data="{{csv_file_path}}"
```

Example Response:

```json
{
    "session_ref": "d44886a3-fb73-4506-af8c-22a436b27321"
}
```

### Step 2 - Launch the website with the session_ref as a query param

```
{{website}}?session_ref=d44886a3-fb73-4506-af8c-22a436b27321
```

## Save a regression model / get predictions for the training data

This part is initiated via the web app. When the user has finished the training/evaluation loop and selects save model the app uses webview to send data back to the host application (p:IGI+).

### Webview message ML App -> pIGI

We have followed the same basic structure used for Discover integration, messages from the web app are in json form with two top level keys: `action` and `data`. The action can be used in pigi to route the message to an appropriate handler.

```json
{
    "action": "persist_model_artefact_data",
    "data": {
        "predictions": [...],
        "serialised_model_artefact": "..."
    }
}
```

The `predictions` key is an array of numbers. The number and order should match the samples passed in.

The `serialised_model_artefact` key is an encoded binary string (pickle format base64 encoded) that allows python to rebuild the model when needed later for predictions/changes.

Example with data [on Trello here](https://trello.com/c/2YQlvZ6f/3793-ml-project-spike-pigi-interaction-with-web-app#comment-62a9a828a2ecb56a73b74923).

