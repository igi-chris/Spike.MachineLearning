export function selectExperiment(id) {
    var el = document.getElementById("selected-experiment-id")
    if (el.value == id) {
        deselectExperiment()
    } else {
        el.value = id;
        document.args_form.submit();  // reload with selected experiment
        console.log(`selected-experiment-id set to: ${document.getElementById("selected-experiment-id").value}`);
    }
}

export function deselectExperiment() {
    var el = document.getElementById("selected-experiment-id")
    var id = el.value;
    el.value = null;

    var expEl = document.getElementById(`exp-${id}`);
    if (expEl) {
        expEl.classList.remove('selected-experiment');
        expEl.blur();  // remove focus from element        
    }
}

export function highlightSelectedExperiment() {
    var selectedId = document.getElementById("selected-experiment-id");
    if (!selectedId || !selectedId.value) { return; }
    var selExpBtn = document.getElementById(`exp-${selectedId.value}`);
    selExpBtn.classList.add('selected-experiment')
}