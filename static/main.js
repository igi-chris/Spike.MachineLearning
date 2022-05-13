window.onload = function() {
    setupBrowseListener();
}


function setupBrowseListener() {
    var browseFile = document.getElementById("browseFile");
    var browseLink = document.getElementById("browseLink");
    if (browseLink) {browseLink.addEventListener('click', handleBrowseLinkClick, false);}
    if (browseFile) {browseFile.addEventListener('change', handleBrowseFileChange, false);}

    function handleBrowseLinkClick(e) {
        browseFile.dispatchEvent(new MouseEvent('click'));
        e.preventDefault();
    }

    function handleBrowseFileChange(e) {
        var fileList = browseFile.files;
        for (var i = 0; i < fileList.length; i++) {
            callProcessFile(fileList[i]);
            e.preventDefault();
        }       
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
                callProcessFile(file);                
            } 
        }
    } else {
        // Use DataTransfer interface to access the file(s)
        for (var i = 0; i < ev.dataTransfer.files.length; i++) {
            var file = ev.dataTransfer.files[i];
            callProcessFile(file);  
        }
    }
}

function callProcessFile(file) {
    console.log('... input file name = ' + file.name);
    var formData = new FormData();
    formData.append("file", file);

    // options = document.getElementsByClassName("transformer-option")
    // Array.prototype.forEach.call(options, function(el) {
    //     if (!el.disabled) {
    //         console.log(`Found element - ${el.id}: ${el.value}`)
    //         formData.append(el.id, el.value);
    //     }
    // });
    console.log(`route: ${route}`);
    processFile(formData);
}

function dragOverHandler(ev) {
    dropZone = document.getElementById('dropZone');
    dropZone.classList.add('dragging');
    // Prevent default behavior (Prevent file from being opened in browser)
    ev.preventDefault();
  }

function endDragOver() {
    dropZone = document.getElementById('dropZone');
    dropZone.classList.remove('dragging');
}

function resetResults(progressBar) {
    progressBar.classList.remove('bg-danger')
    progressBar.classList.add('bg-success', 'progress-bar-animated')
    progressBar.innerHTML = 'File Transformation in progress...';

    errDetails = document.getElementById('errorDetails');
    errDetails.innerHTML = '';
    errInfo = document.getElementById('errorInfo');
    errInfo.style.display = 'none';
}

function processFile(formData) {
    document.getElementById('progress').style.visibility = 'visible';
    progressBar = document.getElementById('progressBar');
    resetResults(progressBar)  // in case of reusing without refreshing page first

    var oReq = new XMLHttpRequest();
    route = document.getElementById("route").value;
    oReq.open("POST", route, true);
    oReq.responseType = 'json';

    oReq.onload = function(e) {
        if (oReq.status == 200) {
            handleFileTransSuccess(this.response);
        } else {
            handleFileTransFailure(this.response);
        }

        function handleFileTransSuccess(response) {
            console.log('Handling success response...');
            progressBar.classList.remove('progress-bar-animated');
            progressBar.innerHTML = 'Finished';

            var blob = response;
            var contentDispo = e.currentTarget.getResponseHeader('Content-Disposition');
            var filename = contentDispo.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)[1];
            console.log(`calling saveBlob for ${filename}`)
            saveBlob(blob, filename);
        }

        function handleFileTransFailure(response) {
            console.log('Handling failure response...');
            progressBar.innerHTML = 'Error';
            progressBar.classList.remove('progress-bar-animated', 'bg-success');
            progressBar.classList.add('bg-danger');

            response.text().then(data => {
                errDetails = document.getElementById('errorDetails');
                console.log(data);
                respJson = JSON.parse(data);
                errText = respJson["user_error_details"];
                console.log(errText);
                if (errText) {
                    errDetails.innerHTML = errText;
                }
                errInfo = document.getElementById('errorInfo');
                errInfo.style.display = 'block';
            });
        }
    }
    oReq.send(formData);  
}

function saveBlob(blob, filename) {
    var a = document.createElement('a');
    a.href = window.URL.createObjectURL(blob);
    a.download = filename;
    a.dispatchEvent(new MouseEvent('click'));
}