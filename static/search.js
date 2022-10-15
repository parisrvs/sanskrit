document.addEventListener('DOMContentLoaded', ()=> {
    document.querySelector("#searchForm").onsubmit = ()=> {
        let keyword = document.querySelector("#keyword").value;
        if (keyword === "") {
            alert("Enter a keyword to search.");
            document.querySelector("#keyword").focus();
            return false;
        }
    }
});


function selectBlock(keyword) {
    document.querySelectorAll(".searchresults").forEach(div => {
        if (div.dataset.query === keyword) {
            div.style.display = "block";
        } else {
            div.style.display = "none";
        }
    });
}

function selectAll() {
    document.querySelectorAll(".searchresults").forEach(div => {
        div.style.display = "block";
    });
}