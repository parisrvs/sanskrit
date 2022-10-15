var username = false;
document.addEventListener("DOMContentLoaded", ()=>{

    if (!sessionStorage.getItem('counter') || !sessionStorage.getItem('username')) {
        const request = new XMLHttpRequest();
        request.open('GET', "/retrieve_username");
        request.onload = () => {
            const resp = JSON.parse(request.responseText);
            if (resp.success) {
                sessionStorage.setItem('username', resp.username);
                sessionStorage.setItem('counter', resp.counter);
                document.querySelector("#counter_div").style.display = "block";
                username = resp.username;
                displayMsgCount(JSON.parse(resp.counter));
            }
        };
        request.send();
    } else {
        document.querySelector("#counter_div").style.display = "block";
        displayMsgCount(JSON.parse(sessionStorage.getItem('counter')));
        username = sessionStorage.getItem('username');
    }

    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    socket.on("receive pvtChat", data=> {
        if (username && data["sendTo"] === username) {
            sessionStorage.setItem('counter', data["counter"]);
            displayMsgCount(JSON.parse(data["counter"]))
        }
    });

    socket.on('deleted chat', data => {
        if (username && data["pvtchat"] && data["sendTo"] === username && data["counter"]) {
            sessionStorage.setItem('counter', data["counter"]);
            displayMsgCount(JSON.parse(data["counter"]))
        }
    });

    
});


function displayMsgCount(counter) {
    let c = 0;
    for (user in counter) {
        c = c + counter[user]["counter"];
    }
    if (c >= 0) {
        document.querySelector("#newPvtMsgs").innerHTML = c;        
    } else {
        document.querySelector("#newPvtMsgs").innerHTML = 0;        
    }    
}