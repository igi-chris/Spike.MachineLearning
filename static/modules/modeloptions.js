export function showModelOptions(modelSelector) {
    // reset any visible options to hidden
    var gprOptions = document.getElementById("GaussianProcessRegressor-options");
    var options = [gprOptions];
    options.forEach(el => {
        if (el) {
            el.style.display = 'none';
        }
    })

    // model options
    console.log(`model selector value: ${modelSelector.value}`);
    if (modelSelector.value === 'GaussianProcessRegressor') {        
        if (gprOptions) {
            gprOptions.style.display = 'block';
            // kernel options needs to be triggered the first time as options
            // are hidden until dropdown is changed (so if first selector value
            // has options these would not show unless you change away then back)
            showGPRKernelOptions(document.getElementById('kernel-options'));
        }
    } else {
       console.log(`No dislay handler for option: ${modelSelector.value}`) 
    }
}

export function showGPRKernelOptions(gprKernelSelector) {    
    // reset any visible options to hidden
    var defKernelOpt = document.getElementById("default");
    var rbfKernelOpt = document.getElementById("rbf");
    var matKernelOpt = document.getElementById("matern");
    var options = [defKernelOpt, rbfKernelOpt, matKernelOpt];
    options.forEach(el => {
        if (el) {
            el.style.display = 'none';
        }
    })

    // model options
    console.log(`GPR kernel selector value: ${gprKernelSelector.value}`);
    if (gprKernelSelector.value === 'Default') {        
        if (defKernelOpt) {
            defKernelOpt.style.display = 'block';
        }
    } else if (gprKernelSelector.value === 'RBF') {        
        if (rbfKernelOpt) {
            rbfKernelOpt.style.display = 'block';
        }
    } else if (gprKernelSelector.value === 'Matern') {        
        if (matKernelOpt) {
            matKernelOpt.style.display = 'block';
        }
    } else {
        console.log(`No dislay handler for option: ${gprKernelSelector.value}`) 
     }
}