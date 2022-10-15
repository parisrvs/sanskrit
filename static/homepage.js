var socket;
var username;
var selectedUsername;

let counter = 0;
const quantity = 20;
var pvtChatcounter = 0;
var pvtChatQuantity = 20;

var allusers = new Set();
var connected_users = new Set();
var displayAllUsers = false;

var msgCounter;

window.addEventListener("unload", () => {
    
    if (sessionStorage.getItem('counter') && sessionStorage.getItem('username')) {
        sessionStorage.setItem('username', username);
        sessionStorage.setItem('counter', JSON.stringify(msgCounter));
    }
    
});

document.addEventListener('DOMContentLoaded', ()=> {
    const request = new XMLHttpRequest();
    request.open('GET', "/get_username");
    request.onload = () => {
        const resp = JSON.parse(request.responseText);
        if (resp.success) {
            
            sessionStorage.setItem('username', resp.username);
            sessionStorage.setItem('counter', resp.counter);
            
            username = resp.username;
            msgCounter = JSON.parse(resp.counter);

            let cu = resp.connected_users;
            cu.forEach(user => {
                if (user != resp.username) {
                    connected_users.add(user);
                }
            })

            let au = resp.allusers;
            au.forEach(user => {
                if (user != resp.username) {
                    allusers.add(user);
                }
            })

            load(username);
            listUsers((Array.from(connected_users)).sort());
        } else {
            username = false;
            window.reload();
        }
    };
    request.send();

    if (!sessionStorage.getItem("selectedUsername")) {
        document.querySelector("#submitPvtChat").disabled = true;
        document.querySelector("#pvtmessage").disabled = true;
        document.querySelector("#submitPvtChat").innerHTML = "@select user";
    } else {
        selectedUsername = sessionStorage.getItem("selectedUsername");
        document.querySelector("#submitPvtChat").disabled = false;
        document.querySelector("#pvtmessage").disabled = false;
        document.querySelector("#submitPvtChat").innerHTML = `@${selectedUsername}`;
        loadPvtChats();
        clearCounter(selectedUsername);
    }

    let pvtChatDiv = document.querySelector("#pvtChats");
    pvtChatDiv.onscroll = ()=> {
        if (pvtChatDiv.scrollHeight - pvtChatDiv.scrollTop === pvtChatDiv.clientHeight) {
            loadPvtChats();
        }
    }

    let chatDiv = document.querySelector("#chats");
    chatDiv.onscroll = ()=> {
        if (chatDiv.scrollHeight - chatDiv.scrollTop === chatDiv.clientHeight) {            
            load(username);
        }
    }
    
    socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    socket.on('connect', ()=> {
        document.querySelector("#submitChat").onclick = ()=> {
            let d = new Date();
            let message = document.querySelector("#message").value;
            if (message === "") {
                alert("type a message");
                document.querySelector("#message").focus();
            } else {
                socket.emit('submit chat', {'message': message, "date": d.toString()});
                document.querySelector("#message").value = "";
                document.querySelector("#message").focus();
                
            }            
        }

        document.querySelector("#submitPvtChat").onclick = ()=> {
            let d = new Date();
            let message = document.querySelector("#pvtmessage").value;
            if (message === "") {
                alert("type a message");
                document.querySelector("#pvtmessage").focus();
            } else {
                socket.emit('submit pvtChat', {'message': message, "date": d.toString(), "sendTo": selectedUsername});
                document.querySelector("#pvtmessage").value = "";
                document.querySelector("#pvtmessage").focus();
            }            
        }

        document.querySelector("#updatePvtChat").onclick = ()=> {
            let message = document.querySelector("#pvtmessage").value;
            if (message === "") {
                alert("type a message");
                document.querySelector("#pvtmessage").focus();
            } else {
                let chat_id = document.querySelector("#updatePvtChatButton").dataset.chat_id;
                socket.emit('update chat', {'message': message, "chat_id": chat_id});
                document.querySelector("#pvtmessage").value = "";
                document.querySelector("#pvtmessage").focus();
                document.querySelector("#updatePvtChatButton").removeAttribute('data-chat_id');
                document.querySelector("#submitPvtChatButton").style.display = "block";
                document.querySelector("#updatePvtChatButton").style.display = "none";
            }            
        }

        document.querySelector("#updateChat").onclick = ()=> {
            let message = document.querySelector("#message").value;
            if (message === "") {
                alert("type a message");
                document.querySelector("#message").focus();
            } else {
                let chat_id = document.querySelector("#updateChatButton").dataset.chat_id;
                socket.emit('update chat', {'message': message, "chat_id": chat_id});
                document.querySelector("#message").value = "";
                document.querySelector("#message").focus();
                document.querySelector("#updateChatButton").removeAttribute('data-chat_id');
                document.querySelector("#submitChatButton").style.display = "block";
                document.querySelector("#updateChatButton").style.display = "none";
            }            
        }
    });

    socket.on('newuser registered', data=>{
        if (username != data["username"]) {
            allusers.add(data["username"]);
            if (displayAllUsers) {
                listUsers((Array.from(allusers)).sort());
                document.querySelectorAll(".allusers").forEach(s=>{
                    if (!connected_users.has(s.dataset.username)) {
                        s.style.color = "black";
                    } else {
                        s.style.color = "green";
                    }
                });            
            }
        }
    });

    socket.on('user loggedin', (data)=>{
        if (data["username"] != username) {
            connected_users.add(data["username"]);
            if (displayAllUsers) {
                document.getElementById(`${data["username"]}`).style.color = "green";
            } else {
                listUsers((Array.from(connected_users)).sort());
            }            
        }
    });

    socket.on('user loggedout', (data)=>{
        if (data["username"] != username) {
            connected_users.delete(data["username"]);
            if (displayAllUsers && document.getElementById(`${data["username"]}`)) {
                document.getElementById(`${data["username"]}`).style.color = "black";
            } else if (document.getElementById(`${data["username"]}`)) {
                document.getElementById(`${data["username"]}`).remove();
                document.getElementById(`counter_${data["username"]}`).remove();
            }
        }        
    });    

    socket.on('receive chat', data=>{
        if (data["username"] === username) {
            const chatTemplate = Handlebars.compile(document.querySelector('#myChatMessageTemplate').innerHTML);
            const c = chatTemplate(data);
            let chats = document.querySelector("#chats").innerHTML;
            document.querySelector("#chats").innerHTML = c + chats;
        } else {
            const chatTemplate = Handlebars.compile(document.querySelector('#chatMessageTemplate').innerHTML);
            const c = chatTemplate(data);
            let chats = document.querySelector("#chats").innerHTML;
            document.querySelector("#chats").innerHTML = c + chats;
        }
        counter++;
    });

    socket.on("receive pvtChat", data=> {
        if (data["username"] === username && data["sendTo"] === selectedUsername) {
            const chatTemplate = Handlebars.compile(document.querySelector('#myPvtChatMessageTemplate').innerHTML);
            const c = chatTemplate(data);
            let pvtchats = document.querySelector("#pvtChats").innerHTML;
            document.querySelector("#pvtChats").innerHTML = c + pvtchats;
            pvtChatcounter++;
        } else if (data["sendTo"] === username && data["username"] === selectedUsername) {
            const chatTemplate = Handlebars.compile(document.querySelector('#chatMessageTemplate').innerHTML);
            const c = chatTemplate(data);
            let pvtchats = document.querySelector("#pvtChats").innerHTML;
            document.querySelector("#pvtChats").innerHTML = c + pvtchats;
            pvtChatcounter++;
            decreaseCounter(data["username"], data["time"])
        } else if (data["sendTo"] === username && data["username"] != selectedUsername) {
            msgCounter = JSON.parse(data["counter"]);
            updateCounter(msgCounter);
        }        
    });
    

    socket.on('deleted chat', data => {
        if (document.getElementById(data.chat_id)) {
            const element = document.getElementById(data.chat_id);
            element.style.animationPlayState = 'running';
            element.addEventListener('animationend', () =>  {
                element.remove();
            });
        }
        if (data["pvtchat"] && ((data["sendTo"] === username && data["username"] === selectedUsername) || (data["username"] === username && data["sendTo"] === selectedUsername))) {
            pvtChatcounter--;
        } else if (data["pvtchat"] && ((data["sendTo"] === username) && (selectedUsername != data["username"]))) {
            if (data["counter"]) {
                msgCounter = JSON.parse(data["counter"]);
                updateCounter(msgCounter);
            }
        } else {
            counter--;
        }
    });

    socket.on('updated chat', data => {        
        if (data.success && document.getElementById(`chat_${data.chat_id}`)) {
            document.getElementById(`chat_${data.chat_id}`).innerHTML = data.message;
        }
    });

    document.querySelector("#listAllUsers").onclick = ()=> {        
        const userTemplate = Handlebars.compile(document.querySelector('#connectedUsersTemplate').innerHTML);
        if (displayAllUsers) {
            document.querySelector("#listAllUsers").innerHTML = "All Users";
            document.querySelector("#listAllUsers").className = "btn btn-warning btn-sm";
            displayAllUsers = false;
            listUsers((Array.from(connected_users)).sort());
        } else {
            document.querySelector("#listAllUsers").innerHTML = "Online";
            document.querySelector("#listAllUsers").className = "btn btn-success btn-sm";
            displayAllUsers = true;
            listUsers((Array.from(allusers)).sort());

            document.querySelectorAll(".allusers").forEach(s=>{
                if (!connected_users.has(s.dataset.username)) {
                    s.style.color = "black";
                } else {
                    s.style.color = "green";
                }
            });
        }
        document.querySelector("#listAllUsers").blur();
        return false;
    }
});

function deletechat(chat_id) {
    const request = new XMLHttpRequest();
    request.open('GET', `/deletechat/${chat_id}`);
    request.onload = () => {
        const resp = JSON.parse(request.responseText);
        if (!resp.success) {
            alert("Invalid Request");
        }
    };
    request.send();
}

//when edit link next to chat messages is clicked
function editchat(chat_id) {
    let message = document.getElementById(`chat_${chat_id}`).innerHTML;
    document.querySelector("#message").value = message;
    document.querySelector("#message").focus();
    document.querySelector("#submitChatButton").style.display = "none";
    document.querySelector("#updateChatButton").style.display = "block";
    document.querySelector("#updateChatButton").dataset.chat_id = chat_id;
    return false;
}

//when edit link next to pvt chat messages is clicked
function editpvtchat(chat_id) {
    let message = document.getElementById(`chat_${chat_id}`).innerHTML;
    document.querySelector("#pvtmessage").value = message;
    document.querySelector("#pvtmessage").focus();
    document.querySelector("#submitPvtChatButton").style.display = "none";
    document.querySelector("#updatePvtChatButton").style.display = "block";
    document.querySelector("#updatePvtChatButton").dataset.chat_id = chat_id;
    return false;
}


function cancelUpdateChat() {
    document.querySelector("#message").value = "";
    document.querySelector("#message").focus();
    document.querySelector("#updateChatButton").removeAttribute('data-chat_id');
    document.querySelector("#submitChatButton").style.display = "block";
    document.querySelector("#updateChatButton").style.display = "none";    
}


function cancelUpdatePvtChat() {
    document.querySelector("#pvtmessage").value = "";
    document.querySelector("#pvtmessage").focus();
    document.querySelector("#updatePvtChatButton").removeAttribute('data-chat_id');
    document.querySelector("#submitPvtChatButton").style.display = "block";
    document.querySelector("#updatePvtChatButton").style.display = "none";    
}


function load(username) {
    const start = counter;
    const end = start + quantity;
    counter = end;

    const request = new XMLHttpRequest();
    request.open('POST', '/');
    request.onload = () => {
        const data = JSON.parse(request.responseText);
        let chats=data.chats;
        for (let chat of chats) {
            if (chat["username"] === username) {
                const chatTemplate = Handlebars.compile(document.querySelector('#myChatMessageTemplate').innerHTML);
                const post = chatTemplate(chat);
                document.querySelector('#chats').innerHTML += post;
            } else {
                const chatTemplate = Handlebars.compile(document.querySelector('#chatMessageTemplate').innerHTML);
                const post = chatTemplate(chat);
                document.querySelector('#chats').innerHTML += post;
            }
        }
    };

    const data = new FormData();
    data.append('start', start);
    data.append('end', end);

    request.send(data);    
};


function listUsers(users) {
    const userTemplate = Handlebars.compile(document.querySelector('#connectedUsersTemplate').innerHTML);
    const user = userTemplate({"users": users});
    document.querySelector('#users').innerHTML = user;
    if (document.getElementById(`${username}`)) {
        document.getElementById(`${username}`).remove();
        document.getElementById(`counter_${username}`).remove();
    }
    updateCounter(msgCounter);
}

function selectUser(link) {
    if (selectedUsername === link.dataset.username) {
        return false;
    }
    selectedUsername = link.dataset.username;
    sessionStorage.setItem("selectedUsername", selectedUsername);
    document.querySelector("#submitPvtChat").disabled = false;
    document.querySelector("#pvtmessage").disabled = false;
    document.querySelector("#submitPvtChat").innerHTML = `@${selectedUsername}`;
    pvtChatcounter = 0;
    pvtChatQuantity = 20;
    document.querySelector("#pvtChats").innerHTML = "";
    loadPvtChats();
    clearCounter(selectedUsername);
    return false;    
}


function loadPvtChats() {
    const start = pvtChatcounter;
    const end = start + pvtChatQuantity;
    pvtChatcounter = end;

    const request = new XMLHttpRequest();
    request.open('POST', '/get_pvt_chats');
    request.onload = () => {
        const data = JSON.parse(request.responseText);
        let chats=data.chats;
        for (let chat of chats) {
            if (chat["username"] === username) {
                const chatTemplate = Handlebars.compile(document.querySelector('#myPvtChatMessageTemplate').innerHTML);
                const post = chatTemplate(chat);
                document.querySelector('#pvtChats').innerHTML += post;
            } else if (chat["sendTo"] === username) {
                const chatTemplate = Handlebars.compile(document.querySelector('#chatMessageTemplate').innerHTML);
                const post = chatTemplate(chat);
                document.querySelector('#pvtChats').innerHTML += post;
            }
        }
    };

    const data = new FormData();
    data.append('start', start);
    data.append('end', end);
    data.append('selectedUsername', selectedUsername);
    

    request.send(data);    
};


function decreaseCounter(sender, time) {
    const request = new XMLHttpRequest();
    request.open('POST', '/decreaseCounter');
    request.onload = () => {
        const data = JSON.parse(request.responseText);
        if (!data.success) {
            window.reload();
        }        
    };

    const data = new FormData();
    data.append('sender', sender);
    data.append('time', time);  

    request.send(data);
}

function clearCounter(selectedUsername) {
    const request = new XMLHttpRequest();
    request.open('POST', '/clearCounter');
    request.onload = () => {
        const data = JSON.parse(request.responseText);
        if (data.success) {
            msgCounter = JSON.parse(data.counter);
            if (document.getElementById(`counter_${selectedUsername}`)) {
                document.getElementById(`counter_${selectedUsername}`).innerHTML = "";
            }
        } else {
            window.reload();
        }
    };

    const data = new FormData();
    data.append('selectedUsername', selectedUsername);
    request.send(data);
    
}


function updateCounter(msgCounter) {
    for ( let user in msgCounter) {
        if (document.getElementById(`counter_${user}`) && msgCounter[user]["counter"] > 0) {
            document.getElementById(`counter_${user}`).innerHTML = `(${msgCounter[user]["counter"]})`;
        } else if (document.getElementById(`counter_${user}`) && msgCounter[user]["counter"] <= 0) {
            document.getElementById(`counter_${user}`).innerHTML = "";
        }
    }
}