window.onload = function() {
    training_filepath = "";
    setupBrowseListener();
    setupTrainingOptionsListerners();
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
    document.getElementById('file-display').innerHTML = `File: ${file.name}`;
      
    var formData = new FormData();
    formData.append("file", file);
    var oReq = new XMLHttpRequest();
    oReq.responseType = 'json';
    oReq.open("POST", "/api/savefile", true);

    oReq.onload = function(e) {
        // handle failure, progress etc later
        console.log(this.response);

        document.getElementById("csv-path").value = this.response['filepath']
        document.getElementById("df-ref").value = this.response['df_ref']

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
