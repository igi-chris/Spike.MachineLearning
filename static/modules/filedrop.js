export function dropHandler(ev, desc) {
    endDragOver(desc);
    console.log(`File(s) dropped (${desc} mode)`);
  
    // Prevent default behavior (Prevent file from being opened)
    ev.preventDefault();
    var file = getDroppedFile();
    saveDataFile(file, desc);
    
    function getDroppedFile() {
        if (ev.dataTransfer.items) {
            // Use DataTransferItemList interface to access the file(s)
            for (var i = 0; i < ev.dataTransfer.items.length; i++) {
                // If dropped items aren't files, reject them
                if (ev.dataTransfer.items[i].kind === 'file') {
                    var file = ev.dataTransfer.items[i].getAsFile();
                    return file;                
                } 
            }
        } else {
            // Use DataTransfer interface to access the file(s)
            for (var i = 0; i < ev.dataTransfer.files.length; i++) {
                var file = ev.dataTransfer.files[i];
                return file;  
            }
        }
    }
}

export function dragOverHandler(ev, desc) {
    document.getElementById(`drop-zone-${desc}`).classList.add('dragging');
    // Prevent default behavior (Prevent file from being opened in browser)
    ev.preventDefault();
}

export function endDragOver(desc) {
    document.getElementById(`drop-zone-${desc}`).classList.remove('dragging');
}

export function saveDataFile(file, desc) {

    console.log(file.name);
    document.getElementById(`file-display-${desc}`).value = file.name;  // need to set value for later lookup
    document.getElementById(`file-display-${desc}`).innerHTML = file.name;
      
    var formData = new FormData();
    var form_label = desc;
    if (desc == 'train' || desc == 'apply') {
        form_label = 'data';
    }
    formData.append(form_label, file);
    var oReq = new XMLHttpRequest();
    oReq.responseType = 'json';
    var uri = "/api/add_session_data";
    
    // add session ref as query param if already set
    var refEl = document.getElementById("session-ref-apply")
    if (desc != 'train' && refEl) {
        ref = refEl.value;
        if (ref) {
            uri = `${uri}?session_ref=${ref}`;
            console.log(`URI set to: ${uri}`);
        }
    } else if (desc == 'train') {
        uri = `${uri}?return_headers=${true}`;
    }

    oReq.open("POST", uri, true);

    if (desc == 'train') {
        oReq.onload = function(e) {
            document.getElementById("session-ref").value = this.response['session_ref']
    
            var heads = this.response['headers']
            var resultColSelect = document.getElementById("result-column");
            for(var i in heads) {
                resultColSelect.options[resultColSelect.options.length] = new Option(heads[i], heads[i]);
            }
            resultColSelect.value = heads[i]  // default to last col for now
        }
    } else {        
        oReq.onload = function(e) {
            console.log("handling apply onload func");
            console.log(this.response);
            document.getElementById("session-ref-apply").value = this.response['session_ref'];
        }
    }
    oReq.send(formData);
}