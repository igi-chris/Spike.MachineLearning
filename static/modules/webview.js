export function isWebView() {
    return window.chrome.webview !== undefined;
}

export function postMsgToWebViewHost(action, data) {
    var msgObject = { 
        action: action, 
        data: data 
    };
    var json = JSON.stringify(msgObject);
    if (isWebView()) {
        console.log(`posting msg to WebView host: ${json}`)
        console.log(`from original: ${msgObject}`)
        window.chrome.webview.postMessage(json);
    } else {
        console.error(`Not running WebView, cannot post msg: ${json}`)
    }
}