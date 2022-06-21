export function saveDataFile(file, desc) {

    console.log(file.name);
    document.getElementById(`file-display-${desc}`).value = file.name;  // need to set value for later lookup
    document.getElementById(`file-display-${desc}`).innerHTML = file.name;
      
    var formData = new FormData();
    form_label = desc;
    if (desc == 'train' || desc == 'apply') {
        form_label = 'data';
    }
    formData.append(form_label, file);
    var oReq = new XMLHttpRequest();
    oReq.responseType = 'json';
    var uri = "/api/add_session_data";
    
    // add session ref as query param if already set
    refEl = document.getElementById("session-ref-apply")
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
    
            heads = this.response['headers']
            var resultColSelect = document.getElementById("result-column");
            for(i in heads) {
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