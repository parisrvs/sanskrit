document.addEventListener('DOMContentLoaded', () => {
    document.querySelector("#login_form").onsubmit = ()=> {
        let email = document.querySelector("#email").value;
        let username = document.querySelector("#username").value;
        let password = document.querySelector("#password").value;
        if (email === "" || username === "" || password === "") {
            alert("All fields marked with (*) are required.");
            return false;
        }
    }
});