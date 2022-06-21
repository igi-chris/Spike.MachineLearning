export function selectExperiment(id) {
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
    if (expEl) {
        expEl.classList.remove('selected-experiment');
        expEl.blur();  // remove focus from element        
    }
}