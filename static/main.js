import { saveModel } from './modules/persist.js'
import { isWebView, postMsgToWebViewHost } from './modules/webview.js'
import { dropHandler, dragOverHandler, endDragOver }  from './modules/filedrop.js'
import { selectExperiment } from './modules/experiment.js'

window.onload = function() {
    if (isWebView()) {
        document.getElementById("is-webview").innerHTML="webview";
        postMsgToWebViewHost('notification', 'ML web app started via WebView');
        notified_webview = true;
    }

    if (location.pathname == "/regression/train" || 
        location.pathname == "/regression/evaluate" || 
        location.pathname == "/regression/retrain") {
        showOrHideConstValueField();
        highlightSelectedExperiment();
        setupTrainingListeners();
    }
    // tmp - plan to remove apply screen and work into main training/eval
    else if (location.pathname == "/regression/apply") {
    }
}

function setupTrainingListeners() {
    setupDropHandlers('train')
    setupTrainingOptionsListerners();

    var nullRepl = document.getElementById("null-replacement");
    nullRepl.addEventListener('input', showOrHideConstValueField, false);
}

function setupApplyListeners() {    
    setupDropHandlers('apply');  // file drop for input data to apply model to
    setupDropHandlers('model');  // file drop for model file

    var retrainBtn = document.getElementById("retrain-btn");
    retrainBtn.addEventListener('click', reTrainModel(), false);
}

function setupDropHandlers(desc) { // desc train | apply | model (later two just for apply.html)
    var dropTrn = document.getElementById(`drop-zone-${desc}`);
    dropTrn.addEventListener('drop', (ev) => {dropHandler(ev, desc)}, false);
    dropTrn.addEventListener('dragover', (ev) => {dragOverHandler(ev, desc)}, false);
    dropTrn.addEventListener('dragleave', () => {endDragOver(desc)}, false);
    dropTrn.addEventListener('dragend', () => {endDragOver(desc)}, false);
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
    var selIdEl = document.getElementById("selected-experiment-id");
    if (!selIdEl || !selIdEl.value) { return; }
    selExpBtn = document.getElementById(`exp-${selIdEl.value}`);
    selExpBtn.classList.add('selected-experiment')
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

function showProgress() {
    document.getElementById('progress').style.visibility = 'visible';
}

function reTrainModel() {
    if (!document.getElementById("file-display-model").value
        || !document.getElementById("file-display-apply").value) {
        alert("A data file and model must be uploaded first")
    } else {
        ref = document.getElementById("session-ref-apply").value
        location.assign(`/regression/retrain?session_ref=${ref}`);
    }
}