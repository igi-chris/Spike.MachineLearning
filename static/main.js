window.onload = function() {
    training_filepath = "";
    setupBrowseListener();
    setupTrainingOptionsListerners();
    showOrHideConstValueField();
    highlightSelectedExperiment();
}

function setupBrowseListener() {
    var browseFile = document.getElementById("browse-file");
    var browseLink = document.getElementById("browse-link");
    if (browseLink) {browseLink.addEventListener('click', handleBrowseLinkClick, false);}
    if (browseFile) {browseFile.addEventListener('change', handleBrowseFileChange, false);}

    function handleBrowseLinkClick(e) {
        browseFile.dispatchEvent(new MouseEvent('click'));
        e.preventDefault();
    }

    function handleBrowseFileChange(e) {
        var fileList = browseFile.files;
        for (var i = 0; i < fileList.length; i++) {
            saveTrainingFile(fileList[i]);
            e.preventDefault();
        }       
     }
}

function setupTrainingOptionsListerners() {
    var trainingSplitSlider = document.getElementById("trn-split");
    if (trainingSplitSlider) {
        trainingSplitSlider.addEventListener('input', handleTrainingSplitInputChange, false);
    }

    function handleTrainingSplitInputChange(e) {
        var pct = trainingSplitSlider.value * 100;
        var displayTrainingSplit = document.getElementById("trn-pct-display");
        displayTrainingSplit.value = `${pct}%`
        e.preventDefault();
    }
}

function highlightSelectedExperiment() {
    selIdEl = document.getElementById("selected-experiment-id");
    if (!selIdEl || !selIdEl.value) { return; }
    selExpBtn = document.getElementById(`exp-${selIdEl.value}`);
    selExpBtn.classList.add('selected-experiment')
}

function dropHandler(ev) {
    endDragOver();
    console.log('File(s) dropped');
  
    // Prevent default behavior (Prevent file from being opened)
    ev.preventDefault();
  
    if (ev.dataTransfer.items) {
        // Use DataTransferItemList interface to access the file(s)
        for (var i = 0; i < ev.dataTransfer.items.length; i++) {
            // If dropped items aren't files, reject them
            if (ev.dataTransfer.items[i].kind === 'file') {
                var file = ev.dataTransfer.items[i].getAsFile();
                saveTrainingFile(file);                
            } 
        }
    } else {
        // Use DataTransfer interface to access the file(s)
        for (var i = 0; i < ev.dataTransfer.files.length; i++) {
            var file = ev.dataTransfer.files[i];
            saveTrainingFile(file);  
        }
    }
}

function saveTrainingFile(file) {

    console.log(file.name);
    document.getElementById('file-display').innerHTML = file.name;
      
    var formData = new FormData();
    formData.append("file", file);
    var oReq = new XMLHttpRequest();
    oReq.responseType = 'json';
    oReq.open("POST", "/api/savefile", true);

    oReq.onload = function(e) {
        // handle failure, progress etc later
        //console.log(this.response);

        document.getElementById("csv-path").value = this.response['filepath']
        document.getElementById("session-ref").value = this.response['session_ref']

        // tmp
        //document.getElementById("csv-path-display").value = training_filepath

        heads = this.response['headers']
        var resultColSelect = document.getElementById("result-column");
        //resultColSelect.options = heads;
        for(i in heads) {
            resultColSelect.options[resultColSelect.options.length] = new Option(heads[i], heads[i]);
        }
        resultColSelect.value = heads[i]  // default to last col for now
    }

    oReq.send(formData);
}

function dragOverHandler(ev) {
    document.getElementById('drop-zone').classList.add('dragging');
    // Prevent default behavior (Prevent file from being opened in browser)
    ev.preventDefault();
}

function endDragOver() {
    document.getElementById('drop-zone').classList.remove('dragging');
}

function showProgress() {
    document.getElementById('progress').style.visibility = 'visible';
}

function showOrHideConstValueField() {
    var option = document.getElementById("null-replacement").value;
    var fillValueEl = document.getElementById("fill-value");
    //console.log(`option set to: ${option}`)
    if (option == "constant") {
        fillValueEl.style.visibility = "visible";
        fillValueEl.required = true;
    } else {
        fillValueEl.style.visibility = "hidden";
        fillValueEl.required = false;
    }
}

function selectExperiment(id) {
    el = document.getElementById("selected-experiment-id")
    if (el.value == id) {
        deselectExperiment()
    } else {
        el.value = id;
        document.args_form.submit();
        console.log(`selected-experiment-id set to: ${document.getElementById("selected-experiment-id").value}`);
    }
}

function deselectExperiment() {
    el = document.getElementById("selected-experiment-id")
    id = el.value;
    el.value = null;
    expEl = document.getElementById(`exp-${id}`);
    expEl.classList.remove('selected-experiment');
    expEl.blur();  // remove focus from element
}

function saveModel(model_type) {
    url = `/api/${model_type}/download`;
    session_ref = document.getElementById('session-ref').value
    exp_id = document.getElementById('selected-experiment-id').value
    params = `session_ref=${session_ref}`
    if (exp_id) {
        params += `&selected_experiment_id=${exp_id}`
    }

    var oReq = new XMLHttpRequest();
    oReq.responseType = 'blob';
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
