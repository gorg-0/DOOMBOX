function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
  
async function parsePage() {

    var urlRegex = /(https?:\/\/[^\s]+)/g;
    var pageSource = document.documentElement.innerHTML
    let urlFound = pageSource.matchAll(urlRegex);

    for (match of urlFound) {
        if (match[0].search("jpg") != -1) {
            var index = match[0].search("jpg");
            var url = match[0].slice(0, index + 3);
            
            const webSocketClient = new WebSocket("ws://127.0.0.1:42069");
            webSocketClient.addEventListener("open", () => {
                webSocketClient.send(url);
            });
        } 
        else if (match[0].search("png") != -1) {
            var index = match[0].search("png");
            var url = match[0].slice(0, index + 3);
            
            const webSocketClient = new WebSocket("ws://127.0.0.1:42069");
            webSocketClient.addEventListener("open", () => {
                webSocketClient.send(url);
            });
        }
        else if (match[0].search("jpeg") != -1) {
            var index = match[0].search("jpeg");
            var url = match[0].slice(0, index + 3);
            
            const webSocketClient = new WebSocket("ws://127.0.0.1:42069");
            webSocketClient.addEventListener("open", () => {
                webSocketClient.send(url);
            });
        }
        else {
            continue;
        }
        await sleep(1000);
    }

}
  
parsePage();