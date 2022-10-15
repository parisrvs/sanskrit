let counter = 0;
const quantity = 10;

document.addEventListener('DOMContentLoaded', load);
            
window.onscroll = () => {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
        load();
    }
};

function load() {    
    const start = counter;
    const end = start + quantity;
    counter = end;

    const request = new XMLHttpRequest();
    request.open('POST', '/contents');
    request.onload = () => {
        const data = JSON.parse(request.responseText);
        const post_template = Handlebars.compile(document.querySelector('#content_row').innerHTML);
        const post = post_template({'contents': data});
        document.querySelector('#chapters').innerHTML += post;
    };

    const data = new FormData();
    data.append('start', start);
    data.append('end', end);

    request.send(data);
};


function addcontent() {
    const template = Handlebars.compile(document.querySelector('#addContentDiv').innerHTML);
    const post = template();
    document.querySelector('#addContent').innerHTML = post;
    return false;
}

function cancelAddContent () {
    document.querySelector('#addContent').innerHTML = "";
    return false;
}

function addNewContent() {
    document.querySelector("#addContentButton").disabled = true;
    document.querySelector("#cancelAddContentButton").disabled = true;

    let chapter = document.querySelector("#chapter").value;
    let words = document.querySelector("#words").value;
    let verbs = document.querySelector("#verbs").value;
    let cases = document.querySelector("#cases").value;
    let compound = document.querySelector("#compound").value;
    let suffix = document.querySelector("#suffix").value;
    let meanings = document.querySelector("#meanings").value;

    if (chapter === "" || words === "" || verbs === "" || meanings === "") {
        alert("Fields marked with (*) are required");
        document.querySelector("#addContentButton").disabled = false;
        document.querySelector("#cancelAddContentButton").disabled = false;
        return false;
    }
    

    const request = new XMLHttpRequest();
    request.open('POST', "/addContent");
    request.onload = () => {
        const resp = JSON.parse(request.responseText);
        if (resp.success) {
            alert("Success");
            document.querySelector("#addContentButton").disabled = false;
            document.querySelector("#cancelAddContentButton").disabled = false;
            document.querySelector('#addContent').innerHTML = "";
        } else {
            alert(resp.message);
            document.querySelector("#addContentButton").disabled = false;
            document.querySelector("#cancelAddContentButton").disabled = false;
            return false;
        }
    };

    const data = new FormData();
    data.append('chapter', chapter);
    data.append('words', words);
    data.append('verbs', verbs);
    data.append('cases', cases);
    data.append('compound', compound);
    data.append('suffix', suffix);
    data.append('meanings', meanings);

    request.send(data);
    return false;
}