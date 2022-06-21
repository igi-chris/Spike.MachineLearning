export function saveModel(model_type) {
    session_ref = document.getElementById('session-ref').value
    exp_id = document.getElementById('selected-experiment-id').value
    params = `session_ref=${session_ref}`
    if (exp_id) {
        params += `&selected_experiment_id=${exp_id}`
    }

    if (isWebView()){
        sendArtefactDataToPigi(model_type, params);
    } else {
        downloadModel(model_type, params);
    }   
}

function sendArtefactDataToPigi(model_type, params) {
    var oReq = new XMLHttpRequest();
    oReq.responseType = 'json';
    url = `/api/${model_type}/get_model_artefact_json`
    url = url+"?"+params
    oReq.open("GET", url, true);

    oReq.onload = function(e) {
        if (oReq.status == 200) {
            handleFileTransSuccess(this.response);
        } else {
            handleFileTransFailure(this.response);
        }

        function handleFileTransSuccess(response) {
            console.log('Handling success response...');
            postMsgToWebViewHost(action="persist_model_artefact_data", data=response)
            
        }

        function handleFileTransFailure(response) {
            console.log('Something went wrong...');  // handle UI for err etc later
            console.log(response)
        }
    }
    console.log(`sending get req: ${url}`)
    oReq.send();  
}

function downloadModel(model_type, params) {    
    var oReq = new XMLHttpRequest();
    oReq.responseType = 'blob';
    url = `/api/${model_type}/download`;
    oReq.open("GET", url+"?"+params, true);

    oReq.onload = function(e) {
        if (oReq.status == 200) {
            handleFileTransSuccess(this.response);
        } else {
            handleFileTransFailure(this.response);
        }

        function handleFileTransSuccess(response) {
            console.log('Handling success response...');
            var blob = response;
            var contentDispo = e.currentTarget.getResponseHeader('Content-Disposition');
            var filename = contentDispo.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)[1];
            console.log(`calling saveBlob for ${filename}`)
            saveBlob(blob, filename);
        }

        function handleFileTransFailure(response) {
            console.log('Something went wrong...');  // handle UI for err etc later
            console.log(response)
        }
    }
    oReq.send();  
}

function saveBlob(blob, filename) {
    var a = document.createElement('a');
    a.href = window.URL.createObjectURL(blob);
    a.download = filename;
    a.dispatchEvent(new MouseEvent('click'));
}