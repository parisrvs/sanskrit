function selectNotes(key) {
    document.querySelectorAll(".notes").forEach(d => {
        if (d.dataset.note === key) {
            d.style.display = "block";
        } else {
            d.style.display = "none";
        }
    });
    return false;
}

function selectAllNotes() {
    document.querySelectorAll(".notes").forEach(d => {
        d.style.display = "block";
    });
    return false;
}

function deletenote(link, note_id) {
    var r = confirm("Are you sure?");
    if (r === true) {
        link.removeAttribute('href');
        const request = new XMLHttpRequest();
        request.open('GET', `/deleteNote/${note_id}`);
        request.onload = () => {
            const resp = JSON.parse(request.responseText);
            if (resp.success) {
                document.getElementById(`${note_id}`).remove();
                document.getElementById(`note_${note_id}`).remove();
                document.querySelector("#showallnotes").click();
            } else {
                alert("Invalid Request");
            }
        };
        request.send();
    } else {
        return false;
    }
}