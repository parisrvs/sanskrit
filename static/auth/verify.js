
document.addEventListener("DOMContentLoaded", ()=>{

    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    socket.on('newuser registered', data=>{
        alert("Registration Successful!");
    });
    
});