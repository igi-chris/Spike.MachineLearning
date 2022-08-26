import { saveModel } from './modules/persist.js'
import { isWebView, postMsgToWebViewHost } from './modules/webview.js'
import { dropHandler, dragOverHandler, endDragOver }  from './modules/filedrop.js'
import { selectExperiment, deselectExperiment, 
    highlightSelectedExperiment } from './modules/experiment.js'
import { showModelOptions, showGPRKernelOptions } from './modules/modeloptions.js'

const version = "0.0.3";  // todo: get from api??

window.onload = function() {
    window.version = version;
    console.info(`using version: ${version}`);

    if (isWebView()) {
        var webViewMsg = document.getElementById("is-webview");
        if (webViewMsg) {
            webViewMsg.innerHTML="webview"
        }
        postMsgToWebViewHost('notification', 'ML web app started via WebView');
    }

    if (location.pathname == "/regression" ||
        location.pathname == "/regression/train" || 
        location.pathname == "/regression/evaluate" || 
        location.pathname == "/regression/retrain") {
        showOrHideConstValueField();
        highlightSelectedExperiment();
        setupTrainingListeners();
    }
    else if (location.pathname == "/regression/apply") {
        setupApplyListeners();
    }
}

function setupTrainingListeners() {
    setupDropHandlers('train')
    setupTrainingOptionsListeners();

    var nullRepl = document.getElementById("null-replacement");
    var argsForm = document.getElementById("args-form");
    var trnBtn = document.getElementById("train-btn");
    var saveBtn = document.getElementById("save-model-btn");

    nullRepl.addEventListener('input', showOrHideConstValueField, false);
    argsForm.addEventListener('submit', showProgress, false);
    trnBtn.addEventListener('click', deselectExperiment, false);
    if (saveBtn) {  // only available in evaluation mode
        saveBtn.addEventListener('click', () => saveModel('regression'), false);
    }    

    // set up listener for each "previous experiment" listed
    var prevExpElements = document.getElementsByClassName('prev-experiment');
    Array.from(prevExpElements).forEach(el => {
        var id = el.id.replace("exp-", "");
        //console.log(`Got id ${id} from ${el.id}`);
        el.addEventListener('click', () => selectExperiment(id), false)
    })

    // set up listener to show the appropriate model options when model selection is changed
    var modelSelector = document.getElementById('regression-model');
    modelSelector.addEventListener('change', 
        () => showModelOptions(modelSelector), false);
    showModelOptions(modelSelector);  // call first time in case in eval mode and one is already selected

    var gprKernelSelector = document.getElementById('kernel-options');
    gprKernelSelector.addEventListener('change', 
        () => showGPRKernelOptions(gprKernelSelector), false);
    showGPRKernelOptions(gprKernelSelector)
}

function setupApplyListeners() {    
    // tmp - plan to remove apply screen and work into main training/eval
    setupDropHandlers('apply');  // file drop for input data to apply model to
    setupDropHandlers('model');  // file drop for model file

    var retrainBtn = document.getElementById("retrain-btn");
    retrainBtn.addEventListener('click', reTrainModel, false);
}

function setupDropHandlers(desc) { // desc train | apply | model (later two just for apply.html)
    var dropzoneId = `drop-zone-${desc}`
    var dropzone = document.getElementById(dropzoneId);
    if (dropzone) {
        dropzone.addEventListener('drop', (ev) => {dropHandler(ev, desc)}, false);
        dropzone.addEventListener('dragover', (ev) => {dragOverHandler(ev, desc)}, false);
        dropzone.addEventListener('dragleave', () => {endDragOver(desc)}, false);
        dropzone.addEventListener('dragend', () => {endDragOver(desc)}, false);
    } else {
        console.log(`No dropzone element found for id: ${dropzoneId} (expected in some cases e.g. if evaluating)`)
    }
}

function setupTrainingOptionsListeners() {
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
        var ref = document.getElementById("session-ref-apply").value
        location.assign(`/regression/retrain?session_ref=${ref}`);
    }
}