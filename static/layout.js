document.addEventListener('DOMContentLoaded', () => {
    document.querySelector("#refreshsite").onclick = ()=> {
        const request = new XMLHttpRequest();
        request.open('GET', "/refresh");
        request.onload = () => {
            let res = JSON.parse(request.responseText);
            if (res.success) {
                location.reload();
            }
        };
        request.send();
        return false;
    };

    document.querySelector("#adminLogout").onclick = ()=> {
        const request = new XMLHttpRequest();
        request.open('GET', "/logout");
        request.onload = () => {
            let res = JSON.parse(request.responseText);
            if (res.success) {
                sessionStorage.removeItem("selectedUsername");
                sessionStorage.removeItem('counter');
                sessionStorage.removeItem('username');
                location.reload();
            }
        };
        request.send();
        return false;
    };    
});