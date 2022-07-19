export function showModelOptions(modelSelector) {
    // reset any visible options to hidden
    var gprOptions = document.getElementById("GaussianProcessRegressor-options");
    var options = [gprOptions]
    options.forEach(el => {
        if (el) {
            el.style.display = 'none';
        }
    })

    // model options
    console.log(`model selector value: ${modelSelector.value}`);
    if (modelSelector && modelSelector.value === 'GaussianProcessRegressor') {        
        if (gprOptions) {
            gprOptions.style.display = 'block';
        }
    }
}