var topic;
var subtopic;
var rule;
var aphorism_id;
var li_id;
var innerLI;

function disableEditLinks () {
    document.querySelectorAll(".toDisable").forEach(b => {
        b.style.visibility = "hidden";
    });
}

function enableEditLinks () {
    document.querySelectorAll(".toDisable").forEach(b => {
        b.style.visibility = "visible";
    });
}

function editaphorism (link, chapter) {
    disableEditLinks()
    aphorism_id = link.dataset.aphorism_id;
    li_id = `aphorism_${aphorism_id}`;

    let topic_id = `topic_${aphorism_id}`;
    let subtopic_id = `subtopic_${aphorism_id}`;
    let rule_id = `rule_${aphorism_id}`;
    let ruleNumber_id = `ruleNumber_${aphorism_id}`;

    topic = document.getElementById(topic_id).innerHTML;
    subtopic = document.getElementById(subtopic_id).innerHTML;
    rule = document.getElementById(rule_id).innerHTML;
    ruleNumber = document.getElementById(ruleNumber_id).innerHTML;

    const post_template = Handlebars.compile(document.querySelector('#aphorism_li').innerHTML);
    const post = post_template({'topic': topic, 'subtopic': subtopic, 'rule': rule, 'id': aphorism_id, "chapter": chapter, "rulenumber": ruleNumber});

    innerLI = document.getElementById(li_id).innerHTML;

    document.getElementById(li_id).innerHTML = post;

    return false;
}

function CancelUpdateAphorism() {
    document.getElementById(li_id).innerHTML = innerLI;
    enableEditLinks()
    return false;
}


function updateAphorism(btn) {
    let rule_id = btn.dataset.rule_id;

    let a = `updateAphorism_${rule_id}`;
    let b = `CancelUpdateAphorism_${rule_id}`

    document.getElementById(a).disabled = true;
    document.getElementById(b).disabled = true;

    let topic_id = `inputTopic_${rule_id}`;
    let subtopic_id = `inputSubtopic_${rule_id}`;
    let ruleID = `inputRule_${rule_id}`;
    let chapter_id = `inputChapterNumber_${rule_id}`;
    let ruleNumber_id = `inputRuleNumber_${rule_id}`;

    let topic = document.getElementById(topic_id).value;
    let subtopic = document.getElementById(subtopic_id).value;
    let rule = document.getElementById(ruleID).value;
    let chapter = document.getElementById(chapter_id).value;
    let ruleNumber = document.getElementById(ruleNumber_id).value;

    if (topic === "" || subtopic === "" || rule === "" || chapter === "" || ruleNumber === "") {
        alert("Fields marked with (*) are required.");
        document.getElementById(a).disabled = false;
        document.getElementById(b).disabled = false;
        return false;
    }

    const request = new XMLHttpRequest();
    request.open('POST', `/editaphorism/${rule_id}`);
    request.onload = () => {
        const resp = JSON.parse(request.responseText);
        if (resp.success) {
            const li_template = Handlebars.compile(document.querySelector('#updatedAphorism').innerHTML);
            const li = li_template({'topic': resp.topic, 'subtopic': resp.subtopic, 'rule': resp.rule, 'id': resp.id, 'rule_number': resp.rule_number, 'chapter': resp.chapter});
            let i = `aphorism_${resp.id}`;
            document.getElementById(i).innerHTML = li;
            enableEditLinks()
        } else {
            document.getElementById(a).disabled = false;
            document.getElementById(b).disabled = false;
            alert("Invalid Request");
            let i = `CancelUpdateAphorism_${rule_id}`;
            document.getElementById(i).click();
        }
    };

    const data = new FormData();
    data.append('topic', topic);
    data.append('subtopic', subtopic);
    data.append('rule', rule);
    data.append('chapter', chapter);
    data.append('rule_number', ruleNumber);

    request.send(data);
}

var verbInnerHTML;
var verbDivID;

function editverb(link, verbForm, verbID) {
    disableEditLinks()
    verbDivID = `${verbForm}_${verbID}`;
    verbInnerHTML = document.getElementById(verbDivID).innerHTML;
    const request = new XMLHttpRequest();
    request.open('GET', `/getVerbInfo/${verbID}/${verbForm}`);
    request.onload = () => {
        const resp = JSON.parse(request.responseText);
        if (resp.success) {
            const verb_template = Handlebars.compile(document.querySelector('#editVerbTemplate').innerHTML);
            const d = verb_template(resp.data);
            document.getElementById(verbDivID).innerHTML = d;
        } else {
            alert("Invalid Request");
        }
    };

    request.send();
}

function cancelEditVerb () {
    document.getElementById(verbDivID).innerHTML = verbInnerHTML;
    enableEditLinks()
    return false;
}


function updateVerb(verbForm, verbID) {
    let a = `updateVerbButton_${verbID}`;
    let b = `cancelVerbButton_${verbID}`;

    document.getElementById(a).disabled = true;
    document.getElementById(b).disabled = true;

    let form31 = document.querySelector(`#form31_${verbID}`).value;
    let form32 = document.querySelector(`#form32_${verbID}`).value;
    let form33 = document.querySelector(`#form33_${verbID}`).value;

    let form21 = document.querySelector(`#form21_${verbID}`).value;
    let form22 = document.querySelector(`#form22_${verbID}`).value;
    let form23 = document.querySelector(`#form23_${verbID}`).value;

    let form11 = document.querySelector(`#form11_${verbID}`).value;
    let form12 = document.querySelector(`#form12_${verbID}`).value;
    let form13 = document.querySelector(`#form13_${verbID}`).value;

    if (form11 === "" || form12 === "" || form13 === "" || form21 === "" || form22 === "" || form23 === "" || form31 === "" || form32 === "" || form33 === "" ) {
        alert("All Fielad marked with (*) are required");
        document.getElementById(a).disabled = false;
        document.getElementById(b).disabled = false;
        return false;
    }

    const request = new XMLHttpRequest();
    request.open('POST', "/updateverb");
    request.onload = () => {
        const resp = JSON.parse(request.responseText);
        if (resp.success) {
            const verbTemplate = Handlebars.compile(document.querySelector('#newVerbTemplate').innerHTML);
            const vt = verbTemplate(resp.data);
            let i = `${verbForm}_${verbID}`;
            document.getElementById(i).innerHTML = vt;
            enableEditLinks()
            return false;
        } else {
            enableEditLinks()
            alert("Invalid Request");
            document.getElementById(a).disabled = false;
            document.getElementById(b).disabled = false;
            document.getElementById(b).click();
            return false;
        }
    };

    const data = new FormData();
    data.append('form31', form31);
    data.append('form32', form32);
    data.append('form33', form33);
    data.append('form21', form21);
    data.append('form22', form22);
    data.append('form23', form23);
    data.append('form11', form11);
    data.append('form12', form12);
    data.append('form13', form13);
    data.append('verbForm', verbForm);
    data.append('verbID', verbID);
    request.send(data);
    return false;
}

var verbHeaderInnerHTML;

function editVerbHeader(verbID, chapter) {
    disableEditLinks()

    let verbName = document.getElementById(`verbName_${verbID}`).innerHTML;
    let verbMeaning = document.getElementById(`verbMeaning_${verbID}`).innerHTML;

    let verbClass = "";
    if (document.getElementById(`verbClass_${verbID}`)) {
        verbClass = document.getElementById(`verbClass_${verbID}`).innerHTML;
    }

    let verbForm = "";
    if (document.getElementById(`verbForm_${verbID}`)) {
        verbForm = document.getElementById(`verbForm_${verbID}`).innerHTML;
    }

    let verbInfo = "";
    if (document.getElementById(`verbInfo_${verbID}`)) {
        verbInfo = document.getElementById(`verbInfo_${verbID}`).innerHTML;
    }

    verbHeaderInnerHTML = document.getElementById(`verbHeader_${verbID}`).innerHTML;

    const verbHeaderTemplate = Handlebars.compile(document.querySelector('#editVerbHeaderTemplate').innerHTML);
    const vt = verbHeaderTemplate({
        "verbName": verbName,
        "verbMeaning": verbMeaning,
        "verbForm": verbForm,
        "verbClass": verbClass,
        "verbInfo": verbInfo,
        "verbChapter": chapter,
        "id": verbID
    });

    document.getElementById(`verbHeader_${verbID}`).innerHTML = vt;
    return false;
}

function cancelEditVerbHeader(verbID) {
    document.getElementById(`verbHeader_${verbID}`).innerHTML = verbHeaderInnerHTML;
    enableEditLinks()
    return false;
}


function updateVerbHeader(verbID) {
    document.getElementById(`updateVerbHeaderButton_${verbID}`).disabled = true;
    document.getElementById(`cancelVerbHeaderButton_${verbID}`).disabled = true;

    let verbName = document.getElementById(`verbName_${verbID}`).value;
    let verbMeaning = document.getElementById(`verbMeaning_${verbID}`).value;
    let verbClass = document.getElementById(`verbClass_${verbID}`).value;
    let verbForm = document.getElementById(`verbForm_${verbID}`).value;
    let verbInfo = document.getElementById(`verbInfo_${verbID}`).value;
    let verbChapter = document.getElementById(`verbChapter_${verbID}`).value;

    if (verbName === "" || verbMeaning === "" || verbChapter === "") {
        alert("fields marked with (*) re required");
        document.getElementById(`updateVerbHeaderButton_${verbID}`).disabled = false;
        document.getElementById(`cancelVerbHeaderButton_${verbID}`).disabled = false;
        return false;
    }


    const request = new XMLHttpRequest();
    request.open('POST', "/updateverbHeader");
    request.onload = () => {
        const resp = JSON.parse(request.responseText);
        if (resp.success) {
            const newVerbHeaderTemplate = Handlebars.compile(document.querySelector('#newVerbHeaderTemplate').innerHTML);
            const vt = newVerbHeaderTemplate(resp.data);
            document.getElementById(`verbHeader_${verbID}`).innerHTML = vt;
            enableEditLinks()
            return false;
        } else {
            enableEditLinks()
            alert(resp.message);
            document.getElementById(`updateVerbHeaderButton_${verbID}`).disabled = false;
            document.getElementById(`cancelVerbHeaderButton_${verbID}`).disabled = false;
            document.getElementById(`cancelVerbHeaderButton_${verbID}`).click();
            return false;
        }
    };

    const data = new FormData();
    data.append('verbName', verbName);
    data.append('verbMeaning', verbMeaning);
    data.append('verbClass', verbClass);
    data.append('verbForm', verbForm);
    data.append('verbInfo', verbInfo);
    data.append('verbChapter', verbChapter);
    data.append('verbID', verbID);
    request.send(data);
    return false;
}

var meaningInnerHTML;

function editmeanings(mid, chapter) {
    disableEditLinks()
    meaningInnerHTML = document.getElementById(`meaning_${mid}`).innerHTML;

    let word = document.getElementById(`word_${mid}`).innerHTML;

    let wordClass = "";
    if (document.getElementById(`wordClass_${mid}`)) {
        wordClass = document.getElementById(`wordClass_${mid}`).innerHTML;
    }

    let meaning1 = document.getElementById(`meaning1_${mid}`).innerHTML;

    let meaning2 = "";
    if (document.getElementById(`meaning2_${mid}`)) {
        meaning2 = document.getElementById(`meaning2_${mid}`).innerHTML;
    }

    let meaning3 = "";
    if (document.getElementById(`meaning3_${mid}`)) {
        meaning3 = document.getElementById(`meaning3_${mid}`).innerHTML;
    }

    let meaning4 = "";
    if (document.getElementById(`meaning4_${mid}`)) {
        meaning4 = document.getElementById(`meaning4_${mid}`).innerHTML;
    }
    
    let meaning5 = "";
    if (document.getElementById(`meaning5_${mid}`)) {
        meaning5 = document.getElementById(`meaning5_${mid}`).innerHTML;
    }

    const newEditMeaningTemplate = Handlebars.compile(document.querySelector('#editMeaningTemplate').innerHTML);
    const emt = newEditMeaningTemplate({
        "id": mid,
        "editWord": word,
        "editChapter": chapter,
        "editMeaning1": meaning1,
        "editMeaning2": meaning2,
        "editMeaning3": meaning3,
        "editMeaning4": meaning4,
        "editMeaning5": meaning5,
        "editWordClass": wordClass
    });

    document.getElementById(`meaning_${mid}`).innerHTML = emt;
    return false;
}

function cancelEditMeaning(mid) {
    document.getElementById(`meaning_${mid}`).innerHTML = meaningInnerHTML;
    enableEditLinks()
    return false;
}


function updateMeaning(mid) {
    document.getElementById(`updateMeaningButton_${mid}`).disabled = true;
    document.getElementById(`cancelUpdteMeaningButton_${mid}`).disabled = true;

    let word = document.getElementById(`editWord_${mid}`).value;
    let chapter = document.getElementById(`editChapter_${mid}`).value;
    let meaning1 = document.getElementById(`editMeaning1_${mid}`).value;
    let meaning2 = document.getElementById(`editMeaning2_${mid}`).value;
    let meaning3 = document.getElementById(`editMeaning3_${mid}`).value;
    let meaning4 = document.getElementById(`editMeaning4_${mid}`).value;
    let meaning5 = document.getElementById(`editMeaning5_${mid}`).value;
    let wordClass = document.getElementById(`editWordClass_${mid}`).value;

    if (word === "" || chapter === "" || meaning1 === "") {
        alert("All fields marked with (*) are required");
        document.getElementById(`updateMeaningButton_${mid}`).disabled = false;
        document.getElementById(`cancelUpdteMeaningButton_${mid}`).disabled = false;
        return false;
    }

    const request = new XMLHttpRequest();
    request.open('POST', "/updateMeaning");
    request.onload = () => {
        const resp = JSON.parse(request.responseText);
        if (resp.success) {
            const newMeaningTemplate = Handlebars.compile(document.querySelector('#newMeaningTemplate').innerHTML);
            const mnt = newMeaningTemplate(resp.data);
            document.getElementById(`meaning_${mid}`).innerHTML = mnt;
            enableEditLinks()
            return false;
        } else {
            enableEditLinks()
            alert(resp.message);
            document.getElementById(`updateMeaningButton_${mid}`).disabled = false;
            document.getElementById(`cancelUpdteMeaningButton_${mid}`).disabled = false;
            document.getElementById(`cancelUpdteMeaningButton_${mid}`).click();
            return false;
        }
    };

    const data = new FormData();
    data.append('chapter', chapter);
    data.append('word', word);
    data.append('wordClass', wordClass);
    data.append('meaning1', meaning1);
    data.append('meaning2', meaning2);
    data.append('meaning3', meaning3);
    data.append('meaning4', meaning4);
    data.append('meaning5', meaning5);
    data.append('id', mid);

    request.send(data);
    return false;
}

function addNewRuleLink(link) {
    let chapter = link.dataset.chapter;
    const newRuleTemplate = Handlebars.compile(document.querySelector('#addNewRuleTemplate').innerHTML);
    const nrt = newRuleTemplate({"chapter": chapter});
    document.querySelector("#addNewRuleDiv").innerHTML = nrt;
    return false;
}


function cancelAddNewRule() {
    document.querySelector("#addNewRuleDiv").innerHTML = "";
    return false;
}

function addNewRule(chapter) {
    document.querySelector("#addNewRuleButton").disabled = true;
    document.querySelector("#cancelAddNewRuleButton").disabled = true;

    
    let rule_number = document.querySelector("#rule_number").value;
    let topic = document.querySelector("#topic").value;
    let subtopic = document.querySelector("#subtopic").value;
    let rule = document.querySelector("#rule").value;

    if (rule_number === "" || topic === "" || subtopic === "" || rule === "") {
        alert("All fields marked with (*) are required");
        document.querySelector("#addNewRuleButton").disabled = false;
        document.querySelector("#cancelAddNewRuleButton").disabled = false;
        return false;
    }

    const request = new XMLHttpRequest();
    request.open('POST', "/addNewRule");
    request.onload = () => {
        const resp = JSON.parse(request.responseText);
        if (resp.success) {
            const li = document.createElement('li');
            li.className = "aphorisms";
            li.id = `aphorism_${resp.data.id}`;
            const newRuleTemplate = Handlebars.compile(document.querySelector('#updatedAphorism').innerHTML);
            const nrt = newRuleTemplate(resp.data);
            li.innerHTML = nrt;
            document.querySelector("#allrules").append(li);
            document.querySelector("#addNewRuleButton").disabled = false;
            document.querySelector("#cancelAddNewRuleButton").disabled = false;
            document.querySelector("#addNewRuleDiv").innerHTML = "";
            alert("Success");
        } else {
            alert(resp.message);
            document.querySelector("#addNewRuleButton").disabled = false;
            document.querySelector("#cancelAddNewRuleButton").disabled = false;
        }
    };

    const data = new FormData();
    data.append('chapter', chapter);
    data.append('rule_number', rule_number);
    data.append('topic', topic);
    data.append('subtopic', subtopic);
    data.append('rule', rule);

    request.send(data);
    return false;
}


function addverb(link) {
    let chapter = link.dataset.chapter;
    const newVerbTemplate = Handlebars.compile(document.querySelector('#addVerbHeaderTemplate').innerHTML);
    const nvt = newVerbTemplate({"chapter": chapter});    
    document.querySelector("#addVerbHeaderDiv").innerHTML = nvt;
    return false;
}


function cancelAddVerbHeader() {
    document.querySelector("#addVerbHeaderDiv").innerHTML = "";
    return false;
}

function addVerbHeader(chapter) {
    document.querySelector("#addVerbHeaderButton").disabled = true;
    document.querySelector("#cancelAddVerbHeaderButton").disabled = true;

    let verb = document.querySelector("#add_verbname").value;
    let meaning = document.querySelector("#add_verbmeaning").value;
    let verbClass = document.querySelector("#add_verbclass").value;
    let verbForm = document.querySelector("#add_verbform").value;
    let info = document.querySelector("#add_verbinfo").value;

    if (verb === "" || meaning === "") {
        alert("fields marked with(*) are required");
        document.querySelector("#addVerbHeaderButton").disabled = false;
        document.querySelector("#cancelAddVerbHeaderButton").disabled = false;
        return false;
    }

    const request = new XMLHttpRequest();
    request.open('POST', "/addverb");
    request.onload = () => {
        const resp = JSON.parse(request.responseText);
        if (resp.success) {
            location.reload();
        } else {
            alert(resp.message);
            document.querySelector("#addVerbHeaderButton").disabled = false;
            document.querySelector("#cancelAddVerbHeaderButton").disabled = false;
            return false;
        }
    };

    const data = new FormData();
    data.append('chapter', chapter);
    data.append('verb', verb);
    data.append('meaning', meaning);
    data.append('verbClass', verbClass);
    data.append('verbForm', verbForm);
    data.append('info', info);

    request.send(data);
    return false;
}


function addWordHeader(link) {
    let chapter = link.dataset.chapter;
    const newWordTemplate = Handlebars.compile(document.querySelector('#addWordHeaderTemplate').innerHTML);
    const nwt = newWordTemplate({"chapter": chapter});    
    document.querySelector("#wordHeaderDiv").innerHTML = nwt;
    return false;
}

function cancelAddWordHeader() {
    document.querySelector("#wordHeaderDiv").innerHTML = "";
    return false;
}

function addWord(chapter) {
    document.querySelector("#addWordHeaderButton").disabled = true;
    document.querySelector("#cancelAddWordHeaderButton").disabled = true;

    let word = document.querySelector("#add_word").value;
    let meaning = document.querySelector("#add_wordMeaning").value;
    let gender = document.querySelector("#add_wordGender").value;
    let form = document.querySelector("#add_wordForm").value;
    let info = document.querySelector("#add_wordInfo").value;

    if (word === "" || meaning === "" || gender === "" || form === "") {
        alert("Fields marked with (*) are required.");
        document.querySelector("#addWordHeaderButton").disabled = false;
        document.querySelector("#cancelAddWordHeaderButton").disabled = false;
        return false;
    }

    const request = new XMLHttpRequest();
    request.open('POST', "/addword");
    request.onload = () => {
        const resp = JSON.parse(request.responseText);
        if (resp.success) {
            location.reload();
        } else {
            alert(resp.message);
            document.querySelector("#addWordHeaderButton").disabled = false;
            document.querySelector("#cancelAddWordHeaderButton").disabled = false;
            return false;
        }
    };

    const data = new FormData();
    data.append('chapter', chapter);
    data.append('word', word);
    data.append('meaning', meaning);
    data.append('gender', gender);
    data.append('form', form);
    data.append('info', info);

    request.send(data);
    return false;
}


function addMeaningTemplate(link) {
    let chapter = link.dataset.chapter;
    const newMeaningTemplate = Handlebars.compile(document.querySelector('#addMeaningTemplate').innerHTML);
    const nmt = newMeaningTemplate({"chapter": chapter});    
    document.querySelector("#addMeaningDiv").innerHTML = nmt;
    return false;
}

function cancelAddMeaning() {
    document.querySelector("#addMeaningDiv").innerHTML = "";
    return false;
}


function addMeaning(chapter) {
    document.querySelector("#addMeaningButton").disabled = true;
    document.querySelector("#cancelAddMeaningButton").disabled = true;

    let word = document.querySelector("#addMeaning_word").value;
    let wordClass = document.querySelector("#addMeaning_wordClass").value;
    let meaning1 = document.querySelector("#addMeaning_meaning1").value;
    let meaning2 = document.querySelector("#addMeaning_meaning2").value;
    let meaning3 = document.querySelector("#addMeaning_meaning3").value;
    let meaning4 = document.querySelector("#addMeaning_meaning4").value;
    let meaning5 = document.querySelector("#addMeaning_meaning5").value;

    if (word === "" || meaning1 === "") {
        alert("All fields marked with (*) are required");
        document.querySelector("#addMeaningButton").disabled = false;
        document.querySelector("#cancelAddMeaningButton").disabled = false;
        return false;
    }

    const request = new XMLHttpRequest();
    request.open('POST', "/addmeaning");
    request.onload = () => {
        const resp = JSON.parse(request.responseText);
        if (resp.success) {

            const meaningTemplate = Handlebars.compile(document.querySelector('#newMeaningTemplate').innerHTML);
            const mt = meaningTemplate(resp.data);
            let d = document.createElement('div');
            d.id = `meaning_${resp.data.id}`;
            d.innerHTML = mt;
            document.querySelector("#allmeanings").append(d);
            document.querySelector("#addMeaningButton").disabled = false;
            document.querySelector("#cancelAddMeaningButton").disabled = false;
            document.querySelector("#addMeaningDiv").innerHTML = "";
            alert("Success");

        } else {
            alert(resp.message);
            document.querySelector("#addMeaningButton").disabled = false;
            document.querySelector("#cancelAddMeaningButton").disabled = false;
            return false;
        }
    };

    const data = new FormData();
    data.append('chapter', chapter);
    data.append('word', word);
    data.append('wordClass', wordClass);
    data.append('meaning1', meaning1);
    data.append('meaning2', meaning2);
    data.append('meaning3', meaning3);
    data.append('meaning4', meaning4);
    data.append('meaning5', meaning5);

    request.send(data);
    return false;
}


function deleteRule(rule_id) {
    var r = confirm("Are you sure?");
    if (r === true) {
        const request = new XMLHttpRequest();
        request.open('GET', `/deleteRule/${rule_id}`);
        request.onload = () => {
            const resp = JSON.parse(request.responseText);
            if (resp.success) {
                document.getElementById(`aphorism_${rule_id}`).remove();
            } else {
                alert("Invalid Request");
            }
        };
        request.send();
    } else {
        return false;
    }    
}


function deleteWord(word_id) {
    var r = confirm("Are you sure?");
    if (r === true) {
        const request = new XMLHttpRequest();
        request.open('GET', `/deleteWord/${word_id}`);
        request.onload = () => {
            const resp = JSON.parse(request.responseText);
            if (resp.success) {
                document.getElementById(`word_${word_id}`).remove();
            } else {
                alert("Invalid Request");
            }
        };
        request.send();
    } else {
        return false;
    }    
}


function deleteVerb(verb_id) {
    var r = confirm("Are you sure?")
    if (r === true) {
        const request = new XMLHttpRequest();
        request.open('GET', `/deleteVerb/${verb_id}`);
        request.onload = () => {
            const resp = JSON.parse(request.responseText);
            if (resp.success) {
                document.getElementById(`verb_${verb_id}`).remove();
            } else {
                alert("Invalid Request");
            }
        };
        request.send();
    } else {
        return false;
    }    
}


function deleteMeaning(meaning_id) {
    var r = confirm("Are you sure?");
    if (r === true) {
        const request = new XMLHttpRequest();
        request.open('GET', `/deleteMeaning/${meaning_id}`);
        request.onload = () => {
            const resp = JSON.parse(request.responseText);
            if (resp.success) {
                document.getElementById(`meaning_${meaning_id}`).remove();
            } else {
                alert("Invalid Request");
            }
        };
        request.send();
    } else {
        return false;
    }    
}


function deleteChapter(link) {
    var r = confirm("Are you sure?");
    if (r === true) {
        document.querySelectorAll("a").forEach(b => {
            b.removeAttribute('href');
        });
        let chapter = link.dataset.chapter;
        const request = new XMLHttpRequest();
        request.open('GET', `/deleteChapter/${chapter}`);
        request.onload = () => {
            const resp = JSON.parse(request.responseText);
            if (resp.success) {
                location.reload();
            } else {
                alert("Invalid Request");
            }
        };
        request.send();
    } else {
        return false;
    }
}