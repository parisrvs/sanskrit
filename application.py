import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, url_for, redirect, request, jsonify, session
from flask_session import Session
from flask_socketio import SocketIO, emit
from werkzeug.security import check_password_hash, generate_password_hash
import random
import requests
import envs
from models import *
import util
from datetime import datetime
import json
#from aws_xray_sdk.core import xray_recorder, patch_all
#from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
#from aws_xray_sdk.core import xray_recorder

application = Flask(__name__)
application.config["SESSION_PERMANENT"] = True
application.config["SESSION_TYPE"] = "filesystem"
Session(application)

application.config["SQLALCHEMY_DATABASE_URI"] = envs.DATABASE_URL
application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(application)

application.config["SECRET_KEY"] = envs.SECRET_KEY
socketio = SocketIO(application)

#plugins = ('EC2Plugin', 'ElasticBeanstalkPlugin')
#xray_recorder.configure(service='ParisSanskrit', plugins=plugins)
#XRayMiddleware(application, xray_recorder)
#patch_all()

connected_users = set()

verbTenses = {
    "present": "लट् (वर्तमान)",
    "imperative": "लोट् (आज्ञा देना)",
    "past": "लङ् (अनद्यतन भूतकाल)",
    "potential": "विधिलिङ् (आज्ञा, चाहिए)",
    "ffuture": "लुट् (अनद्यतन भविष्यत्)",
    "sfuture": "लृट् (भविष्यत्)",
    "conditional": "लृङ् (हेतुहेतुमद् भविष्यत्)",
    "benedictive": "आशीर्लिङ्",
    "pastperfect": "लिट् (परोक्ष भूत)",
    "perfect": "लुङ् (सामान्य भूतकाल)"
}

def load_contents():
    c = []
    contents = Content.query.order_by(Content.chapter).all()
    for content in contents:
        ch = {
            "chapter": content.chapter,
            "words": content.words,
            "verbs":content.verbs,
            "case": content.case,
            "compound": content.compound,
            "suffix": content.suffix,
            "meanings": content.meanings
        }
        c.append(ch)

    return c


def load_chapter(chapter_id):
    try:
        chapter_id = int(chapter_id)
    except ValueError:
        return False    

    if session.get("chapters") == None:
        session["chapters"] = {}

    if chapter_id in session["chapters"]:
        return True

    content = Content.query.filter_by(chapter=chapter_id).first()
    if content == None:
        return False

    session["chapters"][content.chapter] = {
        "content": content,
        "aphorisms": Aphorism.query.filter_by(chapter=content.chapter).order_by(Aphorism.rule_number).all(),
        "words": content.allwords,
        "verbs": content.allverbs,
        "meanings": Meaning.query.filter_by(chapter=content.chapter).order_by(Meaning.wordClass.desc()).all()
    }
    return True


def get_user():
    if session.get("userinfo") == None:
        return False
    else:
        return session["userinfo"]

    
def get_usernames():
    data = []
    users = User.query.order_by(User.username).all()
    for user in users:
        data.append(user.username)
    return data

def get_pvtchats(start, end, user):
    data = []
    chats = Chat.query.filter(
        (Chat.username == user) | (Chat.username == session["userinfo"]["username"])
    ).filter(
        (Chat.sendTo == user) | (Chat.sendTo == session["userinfo"]["username"])
    ).order_by(Chat.id.desc()).slice(start, end).all()
    #chats = Chat.query.filter(or_(Chat.username == user, Chat.username == session["userinfo"]["username"])).filter(or_(Chat.sendTo == user, Chat.sendTo == session["userinfo"]["username"])).order_by(Chat.id.desc()).slice(start, end).all()
    for chat in chats:
        c = {
            "chat_id": chat.id,
            "username": chat.username,
            "message": chat.message,
            "time": chat.time,
            "sendTo": chat.sendTo
        }
        data.append(c)
    return data


def get_chats(start, end):
    data = []
    chats = Chat.query.filter_by(sendTo="everyone").order_by(Chat.id.desc()).slice(start, end).all()
    for chat in chats:
        c = {
            "chat_id": chat.id,
            "username": chat.username,
            "message": chat.message,
            "time": chat.time,
            "sendTo": chat.sendTo
        }
        data.append(c)
    return data


def get_time(a):
    a = a.split('+')
    a = a[0]
    a = a[:-4]
    a = a[4:]
    return a


@socketio.on("submit chat")
def chat(data):
    message = data["message"]
    time = get_time(data["date"])
    c = Chat(message=message, username=session["userinfo"]["username"], time=time)
    db.session.add(c)
    db.session.commit()
    c = Chat.query.filter_by(username=session["userinfo"]["username"]).filter_by(time=time).first()
    mychat = {"message": message, "username": session["userinfo"]["username"], "time": time, "chat_id": c.id}
    emit("receive chat", mychat, broadcast=True)


def increaseCounter(data, username, user):
    time = get_time(data["date"])
    if not user.counter:
        c = {
            username: {
                "times": [time],
                "time": time,
                "counter": 1
            }
        }
        return c
    else:
        counter = json.loads(user.counter)
        if counter.get(username) == None:
            counter[username] = {                
                "times": [time],
                "time": time,
                "counter": 1                
            }
        else:
            (counter[username]["times"]).append(time)
            counter[username]["time"] = time
            counter[username]["counter"] += 1

        return counter


@application.route("/decreaseCounter", methods=["POST"])
def decreaseCounter():
    if session.get("userinfo") == None:
        return jsonify({"success": False})
    
    sender = request.form.get("sender")
    time = request.form.get("time")

    if not sender or not time:
        return jsonify({"success": False})

    user = User.query.filter_by(username=session["userinfo"]["username"]).first()
    if user == None or user.counter == "":
        return jsonify({"success": False})

    counter = json.loads(user.counter)
    if counter.get(sender) == None:
        return jsonify({"success": False})

    try:
        (counter[sender]["times"]).remove(time)
    except:
        return jsonify({"success": False})

    counter[sender]["time"] = ""
    counter[sender]["counter"] -= 1

    user.counter = json.dumps(counter)
    db.session.commit()

    return jsonify({"success": True})


@application.route("/clearCounter", methods=["POST"])
def clearCounter():
    if session.get("userinfo") == None:
        return jsonify({"success": False})
    
    name = request.form.get("selectedUsername")    

    if not name:
        return jsonify({"success": False})

    user = User.query.filter_by(username=session["userinfo"]["username"]).first()
    if user == None:
        return jsonify({"success": False})
    elif not user.counter:
        return jsonify({"success": True, "counter": user.counter})

    counter = json.loads(user.counter)
    if counter.get(name) == None:
        return jsonify({"success": True, "counter": json.dumps(user.counter)})

    del counter[name]
    user.counter = json.dumps(counter)
    db.session.commit()

    return jsonify({"success": True, "counter": json.dumps(user.counter)})


@socketio.on("submit pvtChat")
def pvtchat(data):
    if session.get("userinfo") == None:
        pass
    else:        
        message = data["message"]
        time = get_time(data["date"])
        sendTo = data["sendTo"]
        user = User.query.filter_by(username=sendTo).first()
        if user == None:
            pass
        else:
            counter = json.dumps(increaseCounter(data, session["userinfo"]["username"], user))
            c = Chat(message=message, username=session["userinfo"]["username"], time=time, sendTo=sendTo)
            user.counter = counter
            db.session.add(c)
            db.session.commit()
            c = Chat.query.filter_by(username=session["userinfo"]["username"]).filter_by(time=time).filter_by(sendTo=sendTo).first()
            mychat = {"message": message, "username": session["userinfo"]["username"], "time": time, "chat_id": c.id, "sendTo": sendTo, "counter": counter}
            emit("receive pvtChat", mychat, broadcast=True)


@socketio.on('update chat')
def update_chat(data):
    try:
        chat_id = int(data["chat_id"])
    except ValueError:
        emit("updated chat", {"success": False}, broadcast=False)

    c = Chat.query.get(chat_id)
    if c == None:
        emit("updated chat", {"success": False}, broadcast=False)
    
    if c.username != session["userinfo"]["username"]:
        emit("updated chat", {"success": False}, broadcast=False)

    c.message = data["message"]
    db.session.commit()

    emit("updated chat", {"success": True, "chat_id": chat_id, "message": data["message"]}, broadcast=True)


@socketio.on('connect')
def user_connected():
    if session.get("userinfo") == None:
        emit("unregistered user", {"username": False}, broadcast=True)
    else:
        connected_users.add(session["userinfo"]["username"])
        emit("user loggedin", {"username": session["userinfo"]["username"]}, broadcast=True)


@socketio.on('disconnect')
def user_disconnected():
    if session.get("userinfo") == None:
        emit("unregistered user", {"username": False}, broadcast=True)
    else:
        connected_users.discard(session["userinfo"]["username"])
        emit("user loggedout", {"username": session["userinfo"]["username"]}, broadcast=True)
    

@application.route("/get_username")
def get_username():
    if session.get("userinfo") == None:
        return jsonify({"success": False})
    else:
        user = User.query.filter_by(username=session["userinfo"]["username"]).first()
        if user == None:
            return jsonify({"success": False})
        allusers = get_usernames()
        return jsonify({
            "success": True,
            "username": session["userinfo"]["username"],
            "connected_users": list(connected_users),
            "allusers": allusers,
            "counter": user.counter
        })

    
@application.route("/retrieve_username")
def retrieve_username():
    if session.get("userinfo") == None:
        return jsonify({"success": False})
    else:
        user = User.query.filter_by(username=session["userinfo"]["username"]).first()
        if user == None:
            return jsonify({"success": False})
        return jsonify({
            "success": True,
            "username": session["userinfo"]["username"],
            "counter": user.counter
        })


@application.route("/deletechat/<int:chat_id>")
def deletechat(chat_id):
    if session.get("userinfo") == None:
        return jsonify({"success": False})
    
    try:
        chat_id = int(chat_id)
    except ValueError:
        return jsonify({"success": False})

    c = Chat.query.get(chat_id)
    if c == None:
        return jsonify({"success": False})
    
    if c.username != session["userinfo"]["username"]:
        return jsonify({"success": False})

    counter_str = None
    if c.sendTo == "everyone":
        pvtchat = False        
    else:
        pvtchat = True
        user = User.query.filter_by(username=c.sendTo).first()
        if user == None:
            return jsonify({"success": False})
        counter = json.loads(user.counter)
        if counter.get(c.username) != None and c.time in counter[c.username]["times"]:
            (counter[c.username]["times"]).remove(c.time)
            counter[c.username]["counter"] -= 1
            counter_str = json.dumps(counter)
            user.counter = counter_str

    db.session.delete(c)
    db.session.commit()

    socketio.emit("deleted chat", {"chat_id": chat_id, "pvtchat": pvtchat, "sendTo": c.sendTo, "username": c.username, "counter": counter_str}, broadcast=True)
    return jsonify({"success": True})


@application.route("/", methods=["POST", "GET"])
def homepage():
    user = get_user()
    if not user:
        #return redirect(url_for('contents'))
        return redirect(url_for('login'))

    if session.get("administrator") == None:
        session["administrator"] = False

    if request.method == "GET":
        return render_template(
            "homepage.html",
            admin=session["administrator"],
            user=user
        )

    start = int(request.form.get("start") or 0)
    end = int(request.form.get("end") or (start + 10))
    chats = get_chats(start, end)

    return jsonify({"chats": chats})


@application.route("/get_pvt_chats", methods=["POST"])
def get_pvt_chats():
    user = get_user()
    if not user:
        return jsonify({"success": False})
    
    start = int(request.form.get("start") or 0)
    end = int(request.form.get("end") or (start + 10))
    selectedUsername = request.form.get("selectedUsername")
    if not selectedUsername:
        return jsonify({"success": False})

    chats = get_pvtchats(start, end, selectedUsername)

    return jsonify({"chats": chats, "success": True})



@application.route("/notes")
def notes():
    user = get_user()
    if session.get("administrator") == None:
        session["administrator"] = False

    if session.get("notes") == None:
        session["notes"] = Note.query.order_by(Note.key).all()
    return render_template(
        "notes.html",
        notes=session["notes"],
        admin=session["administrator"],
        user=user
    )


@application.route("/contents", methods=["POST", "GET"])
def contents():
    user = get_user()
    if session.get("administrator") == None:
        session["administrator"] = False

    if session.get("contents") == None:
        session["contents"] = load_contents()

    if request.method == "GET":        
        return render_template(
            "contents.html",
            admin=session["administrator"],
            user=user
        )
    
    start = int(request.form.get("start") or 0)
    end = int(request.form.get("end") or (start + 10))

    data = session["contents"][start:end]
    return jsonify(data)


@application.route("/contents/chapter/<int:chapter_id>")
def chapter(chapter_id):
    user = get_user()
    if session.get("administrator") == None:
        session["administrator"] = False

    if not load_chapter(chapter_id):
        return redirect(url_for('contents'))

    return render_template(
        "chapter.html",
        content=session["chapters"][chapter_id],
        admin=session["administrator"],
        user=user
    )


@application.route("/refresh")
def refresh():
    if session.get("administrator") == True:
        admin = True
    else:
        admin = False

    if session.get("userinfo") == None:
        userinfo = None
    else:
        userinfo = session["userinfo"]

    session.clear()
    session["administrator"] = admin
    session["userinfo"] = userinfo
    return jsonify({"success": True})


@application.route("/editcontent/<int:chapter_id>", methods=["POST", "GET"])
def editcontent(chapter_id):
    user = get_user()
    if session.get("administrator") != True:
        return redirect(url_for('login'))
    
    try:
        cid = int(chapter_id)
    except ValueError:
        return redirect(url_for('homepage'))
        
    content = Content.query.filter_by(chapter=cid).first()
    if content == None:
        return redirect(url_for('homepage'))
    
    if request.method == "GET":
        return render_template(
            "admin/editcontent.html",
            admin=session["administrator"],
            content=content,
            user=user
        )

    words = request.form.get("words")
    verbs = request.form.get("verbs")
    case = request.form.get("case")
    compound = request.form.get("compound")
    suffix = request.form.get("suffix")
    meanings = request.form.get("meanings")

    if not words or not verbs or not meanings:
        return render_template(
            "admin/editcontent.html",
            admin=session["administrator"],
            user=user,
            content=content,
            content_update_error="fields marked with (*) are required"
        )
    
    content.words = words
    content.verbs = verbs
    content.case = case
    content.compound = compound
    content.suffix = suffix
    content.meanings = meanings

    db.session.commit()

    userinfo = session["userinfo"]
    session.clear()
    session["administrator"] = True
    session["userinfo"] = userinfo

    return redirect(url_for('chapter', chapter_id=cid))


@application.route("/editaphorism/<int:aphorism_id>", methods=["POST"])
def editaphorism(aphorism_id):
    if session.get("administrator") != True:
        return jsonify({"success": False})
    
    try:
        aphorism_id = int(aphorism_id)
    except ValueError:
        return jsonify({"success": False})

    topic = request.form.get("topic")
    subtopic = request.form.get("subtopic")
    rule = request.form.get("rule")
    chapter = request.form.get("chapter")
    rule_number = request.form.get("rule_number")

    if not topic or not subtopic or not rule or not chapter or not rule_number:
        return jsonify({"success": False})
    
    try:
        chapter = int(chapter)
        rule_number = int(rule_number)
    except ValueError:
        return jsonify({"success": False})

    c = Content.query.filter_by(chapter=chapter).first()
    if c == None:
        return jsonify({"success": False})

    aphorism = Aphorism.query.get(aphorism_id)
    if aphorism == None:
        return jsonify({"success": False})

    if aphorism.rule_number != rule_number:
        r = Aphorism.query.filter_by(rule_number=rule_number).first()
        if r != None:
            return jsonify({"success": False})

    aphorism.topic = topic
    aphorism.subtopic = subtopic
    aphorism.rule = rule
    aphorism.chapter = chapter
    aphorism.rule_number = rule_number

    db.session.commit()

    userinfo = session["userinfo"]
    session.clear()
    session["administrator"] = True
    session["userinfo"] = userinfo

    return jsonify({"success": True, "topic": topic, "subtopic": subtopic, "rule": rule, "id": aphorism_id, "rule_number": rule_number, "chapter": chapter})


@application.route("/editword/<int:word_id>", methods=["POST", "GET"])
def editword(word_id):
    user = get_user()
    if session.get("administrator") != True:
        return redirect(url_for('login'))

    try:
        word_id = int(word_id)
    except ValueError:
        return redirect(url_for('homepage'))

    word = Word.query.get(word_id)    
    if word == None:
        return redirect(url_for('homepage'))

    if request.method == "GET":
        return render_template(
            "admin/editword.html",
            admin=session["administrator"],
            word=word,
            user=user
        )

    ch = word.chapter

    chapter = request.form.get("chapter")
    wordname = request.form.get("word")
    meaning = request.form.get("meaning")
    gender = request.form.get("gender")
    form = request.form.get("form")
    info = request.form.get("info")

    if not chapter or not wordname or not meaning or not gender or not form:
        return render_template(
            "admin/editword.html",
            admin=session["administrator"],
            user=user,
            word=word,
            updateWordError = "All fields marked with (*) are required"
        )
    
    try:
        chapter = int(chapter)
    except ValueError:
        return render_template(
            "admin/editword.html",
            admin=session["administrator"],
            word=word,
            user=user,
            updateWordError = "Chapter Number must be an integer."
        )
    
    C = Content.query.filter_by(chapter=chapter).first()
    if C == None:
        return render_template(
            "admin/editword.html",
            admin=session["administrator"],
            word=word,
            user=user,
            updateWordError = f"Chapter {chapter} does not exist."
        )
    
    wordname = wordname.strip()
    if wordname != word.word:
        w = Word.query.filter_by(word=wordname).first()
        if w != None:
            return render_template(
                "admin/editword.html",
                admin=session["administrator"],
                word=word,
                user=user,
                updateWordError = "A word with this name already exists."
            )

    nominative1 = request.form.get("nominative1")
    nominative2 = request.form.get("nominative2")
    nominative3 = request.form.get("nominative3")

    accusative1 = request.form.get("accusative1")
    accusative2 = request.form.get("accusative2")
    accusative3 = request.form.get("accusative3")

    instrumental1 = request.form.get("instrumental1")
    instrumental2 = request.form.get("instrumental2")
    instrumental3 = request.form.get("instrumental3")

    dative1 = request.form.get("dative1")
    dative2 = request.form.get("dative2")
    dative3 = request.form.get("dative3")

    ablative1 = request.form.get("ablative1")
    ablative2 = request.form.get("ablative2")
    ablative3 = request.form.get("ablative3")

    genitive1 = request.form.get("genitive1")
    genitive2 = request.form.get("genitive2")
    genitive3 = request.form.get("genitive3")

    locative1 = request.form.get("locative1")
    locative2 = request.form.get("locative2")
    locative3 = request.form.get("locative3")
    
    word.chapter = chapter
    word.word = wordname
    word.meaning = meaning.strip()
    word.gender = gender.strip()
    word.form = form.strip()
    word.info = info.strip()

    word.nominative1 = nominative1.strip()
    word.nominative2 = nominative2.strip()
    word.nominative3 = nominative3.strip()

    word.accusative1 = accusative1.strip()
    word.accusative2 = accusative2.strip()
    word.accusative3 = accusative3.strip()
    
    word.instrumental1 = instrumental1.strip()
    word.instrumental2 = instrumental2.strip()
    word.instrumental3 = instrumental3.strip()

    word.dative1 = dative1.strip()
    word.dative2 = dative2.strip()
    word.dative3 = dative3.strip()

    word.ablative1 = ablative1.strip()
    word.ablative2 = ablative2.strip()
    word.ablative3 = ablative3.strip()

    word.genitive1 = genitive1.strip()
    word.genitive2 = genitive2.strip()
    word.genitive3 = genitive3.strip()

    word.locative1 = locative1.strip()
    word.locative2 = locative2.strip()
    word.locative3 = locative3.strip()

    db.session.commit()

    userinfo = session["userinfo"]
    session.clear()
    session["administrator"] = True
    session["userinfo"] = userinfo

    return redirect(url_for('chapter', chapter_id=ch))


@application.route("/getVerbInfo/<int:verbID>/<string:verbForm>", methods=["GET"])
def getVerbInfo(verbID, verbForm):
    try:
        verbID = int(verbID)
    except ValueError:
        return jsonify({"success": False})

    verb = Verb.query.get(verbID)
    if verb == None:
        return jsonify({"success": False})
    
    if verbForm == "present":
        data = {
            "form31": verb.present31,
            "form32": verb.present32,
            "form33": verb.present33,
            "form21": verb.present21,
            "form22": verb.present22,
            "form23": verb.present23,
            "form11": verb.present11,
            "form12": verb.present12,
            "form13": verb.present13,
            "tense": verbTenses["present"],
            "id": verb.id,
            "verbForm": "present"
        }
    elif verbForm == "imperative":
        data = {
            "form31": verb.imperative31,
            "form32": verb.imperative32,
            "form33": verb.imperative33,
            "form21": verb.imperative21,
            "form22": verb.imperative22,
            "form23": verb.imperative23,
            "form11": verb.imperative11,
            "form12": verb.imperative12,
            "form13": verb.imperative13,
            "tense": verbTenses["imperative"],
            "id": verb.id,
            "verbForm": "imperative"
        }
    elif verbForm == "past":
        data = {
            "form31": verb.past31,
            "form32": verb.past32,
            "form33": verb.past33,
            "form21": verb.past21,
            "form22": verb.past22,
            "form23": verb.past23,
            "form11": verb.past11,
            "form12": verb.past12,
            "form13": verb.past13,
            "tense": verbTenses["past"],
            "id": verb.id,
            "verbForm": "past"
        }
    elif verbForm == "potential":
        data = {
            "form31": verb.potential31,
            "form32": verb.potential32,
            "form33": verb.potential33,
            "form21": verb.potential21,
            "form22": verb.potential22,
            "form23": verb.potential23,
            "form11": verb.potential11,
            "form12": verb.potential12,
            "form13": verb.potential13,
            "tense": verbTenses["potential"],
            "id": verb.id,
            "verbForm": "potential"
        }
    elif verbForm == "ffuture":
        data = {
            "form31": verb.ffuture31,
            "form32": verb.ffuture32,
            "form33": verb.ffuture33,
            "form21": verb.ffuture21,
            "form22": verb.ffuture22,
            "form23": verb.ffuture23,
            "form11": verb.ffuture11,
            "form12": verb.ffuture12,
            "form13": verb.ffuture13,
            "tense": verbTenses["ffuture"],
            "id": verb.id,
            "verbForm": "ffuture"
        }
    elif verbForm == "sfuture":
        data = {
            "form31": verb.sfuture31,
            "form32": verb.sfuture32,
            "form33": verb.sfuture33,
            "form21": verb.sfuture21,
            "form22": verb.sfuture22,
            "form23": verb.sfuture23,
            "form11": verb.sfuture11,
            "form12": verb.sfuture12,
            "form13": verb.sfuture13,
            "tense": verbTenses["sfuture"],
            "id": verb.id,
            "verbForm": "sfuture"
        }
    elif verbForm == "conditional":
        data = {
            "form31": verb.conditional31,
            "form32": verb.conditional32,
            "form33": verb.conditional33,
            "form21": verb.conditional21,
            "form22": verb.conditional22,
            "form23": verb.conditional23,
            "form11": verb.conditional11,
            "form12": verb.conditional12,
            "form13": verb.conditional13,
            "tense": verbTenses["conditional"],
            "id": verb.id,
            "verbForm": "conditional"
        }
    elif verbForm == "benedictive":
        data = {
            "form31": verb.benedictive31,
            "form32": verb.benedictive32,
            "form33": verb.benedictive33,
            "form21": verb.benedictive21,
            "form22": verb.benedictive22,
            "form23": verb.benedictive23,
            "form11": verb.benedictive11,
            "form12": verb.benedictive12,
            "form13": verb.benedictive13,
            "tense": verbTenses["benedictive"],
            "id": verb.id,
            "verbForm": "benedictive"
        }
    elif verbForm == "pastperfect":
        data = {
            "form31": verb.pastperfect31,
            "form32": verb.pastperfect32,
            "form33": verb.pastperfect33,
            "form21": verb.pastperfect21,
            "form22": verb.pastperfect22,
            "form23": verb.pastperfect23,
            "form11": verb.pastperfect11,
            "form12": verb.pastperfect12,
            "form13": verb.pastperfect13,
            "tense": verbTenses["pastperfect"],
            "id": verb.id,
            "verbForm": "pastperfect"
        }
    elif verbForm == "perfect":
        data = {
            "form31": verb.perfect31,
            "form32": verb.perfect32,
            "form33": verb.perfect33,
            "form21": verb.perfect21,
            "form22": verb.perfect22,
            "form23": verb.perfect23,
            "form11": verb.perfect11,
            "form12": verb.perfect12,
            "form13": verb.perfect13,
            "tense": verbTenses["perfect"],
            "id": verb.id,
            "verbForm": "perfect"
        }
    else:
        return jsonify({"success": False})

    return jsonify({"success": True, "data": data})


@application.route("/updateverb", methods=["POST"])
def updateverb():
    if session.get("administrator") != True:
        return jsonify({"success": False})

    verbID = request.form.get("verbID")
    verbForm = request.form.get("verbForm")

    try:
        verbID = int(verbID)
    except ValueError:
        return jsonify({"success": False})

    verb = Verb.query.get(verbID)
    if verb == None:
        return jsonify({"success": False})

    form31 = request.form.get("form31")
    form32 = request.form.get("form32")
    form33 = request.form.get("form33")
    form21 = request.form.get("form21")
    form22 = request.form.get("form22")
    form23 = request.form.get("form23")
    form11 = request.form.get("form11")
    form12 = request.form.get("form12")
    form13 = request.form.get("form13")

    if not form11 or not form12 or not form13 or not form21 or not form22 or not form23 or not form31 or not form32 or not form33:
        return jsonify({"success": False})

    if verbForm == "present":
        verb.present31 = form31
        verb.present32 = form32
        verb.present33 = form33
        verb.present21 = form21
        verb.present22 = form22
        verb.present23 = form23
        verb.present11 = form11
        verb.present12 = form12
        verb.present13 = form13
    elif verbForm == "imperative":
        verb.imperative31 = form31
        verb.imperative32 = form32
        verb.imperative33 = form33
        verb.imperative21 = form21
        verb.imperative22 = form22
        verb.imperative23 = form23
        verb.imperative11 = form11
        verb.imperative12 = form12
        verb.imperative13 = form13
    elif verbForm == "past":
        verb.past31 = form31
        verb.past32 = form32
        verb.past33 = form33
        verb.past21 = form21
        verb.past22 = form22
        verb.past23 = form23
        verb.past11 = form11
        verb.past12 = form12
        verb.past13 = form13
    elif verbForm == "potential":
        verb.potential31 = form31
        verb.potential32 = form32
        verb.potential33 = form33
        verb.potential21 = form21
        verb.potential22 = form22
        verb.potential23 = form23
        verb.potential11 = form11
        verb.potential12 = form12
        verb.potential13 = form13
    elif verbForm == "ffuture":
        verb.ffuture31 = form31
        verb.ffuture32 = form32
        verb.ffuture33 = form33
        verb.ffuture21 = form21
        verb.ffuture22 = form22
        verb.ffuture23 = form23
        verb.ffuture11 = form11
        verb.ffuture12 = form12
        verb.ffuture13 = form13
    elif verbForm == "sfuture":
        verb.sfuture31 = form31
        verb.sfuture32 = form32
        verb.sfuture33 = form33
        verb.sfuture21 = form21
        verb.sfuture22 = form22
        verb.sfuture23 = form23
        verb.sfuture11 = form11
        verb.sfuture12 = form12
        verb.sfuture13 = form13
    elif verbForm == "conditional":
        verb.conditional31 = form31
        verb.conditional32 = form32
        verb.conditional33 = form33
        verb.conditional21 = form21
        verb.conditional22 = form22
        verb.conditional23 = form23
        verb.conditional11 = form11
        verb.conditional12 = form12
        verb.conditional13 = form13
    elif verbForm == "benedictive":
        verb.benedictive31 = form31
        verb.benedictive32 = form32
        verb.benedictive33 = form33
        verb.benedictive21 = form21
        verb.benedictive22 = form22
        verb.benedictive23 = form23
        verb.benedictive11 = form11
        verb.benedictive12 = form12
        verb.benedictive13 = form13
    elif verbForm == "pastperfect":
        verb.pastperfect31 = form31
        verb.pastperfect32 = form32
        verb.pastperfect33 = form33
        verb.pastperfect21 = form21
        verb.pastperfect22 = form22
        verb.pastperfect23 = form23
        verb.pastperfect11 = form11
        verb.pastperfect12 = form12
        verb.pastperfect13 = form13
    elif verbForm == "perfect":
        verb.perfect31 = form31
        verb.perfect32 = form32
        verb.perfect33 = form33
        verb.perfect21 = form21
        verb.perfect22 = form22
        verb.perfect23 = form23
        verb.perfect11 = form11
        verb.perfect12 = form12
        verb.perfect13 = form13
    else:
        return jsonify({"success": False})

    db.session.commit()

    userinfo = session["userinfo"]
    session.clear()
    session["administrator"] = True
    session["userinfo"] = userinfo

    data = {
        "verbTense": verbTenses[verbForm],
        "form31": form31,
        "form32": form32,
        "form33": form33,
        "form21": form21,
        "form22": form22,
        "form23": form23,
        "form11": form11,
        "form12": form12,
        "form13": form13,
        "verbForm": verbForm,
        "id": verbID
    }

    return jsonify({
        "success": True,
        "data": data
    })


@application.route("/updateverbHeader", methods=["POST"])
def updateverbHeader():
    if session.get("administrator") != True:
        return jsonify({"success": False, "message": "Login in and try again."})
    
    verbID = request.form.get("verbID")
    verbName = request.form.get("verbName")
    verbMeaning = request.form.get("verbMeaning")
    verbClass = request.form.get("verbClass")
    verbForm = request.form.get("verbForm")
    verbInfo = request.form.get("verbInfo")
    verbChapter = request.form.get("verbChapter")

    try:
        verbID = int(verbID)
        verbChapter = int(verbChapter)
    except ValueError:
        return jsonify({"success": False, "message": "Invalid verb ID or Chapter number."})

    verb = Verb.query.get(verbID)
    if verb == None:
        return jsonify({"success": False, "message": "Invalid Verb ID"})

    ch = Content.query.filter_by(chapter=verbChapter).first()
    if ch == None:
        return jsonify({"success": False, "message": "This chapter does not exist."})

    if verbName != verb.verb:
        v = Verb.query.filter_by(verb=verbName).first()
        if v != None:
            return jsonify({"success": False, "message": "A verb with this name already exists."})
    
    verb.chapter = verbChapter
    verb.verb = verbName
    verb.meaning = verbMeaning
    verb.verbClass = verbClass
    verb.verbForm = verbForm
    verb.info = verbInfo
    
    db.session.commit()

    userinfo = session["userinfo"]
    session.clear()
    session["administrator"] = True
    session["userinfo"] = userinfo

    data = {
        "id": verbID,
        "verbName": verbName,
        "verbMeaning": verbMeaning,
        "verbClass": verbClass,
        "verbForm": verbForm,
        "verbInfo": verbInfo,
        "chapter": verbChapter,
        "admin": True
    }

    return jsonify({"success": True, "data": data})


@application.route("/updateMeaning", methods=["POST"])
def updateMeaning():
    if session.get("administrator") != True:
        return jsonify({"success": False, "message": "Invalid Credentials"})

    chapter = request.form.get("chapter")
    word = request.form.get("word")
    wordClass = request.form.get("wordClass")
    meaning1 = request.form.get("meaning1")
    meaning2 = request.form.get("meaning2")
    meaning3 = request.form.get("meaning3")
    meaning4 = request.form.get("meaning4")
    meaning5 = request.form.get("meaning5")
    mid = request.form.get("id")

    if not mid or not chapter or not word or not meaning1:
        return jsonify({"success": False, "message": "Incomplete Form"})

    try:
        chapter = int(chapter)
        mid = int(mid)
    except ValueError:
        return jsonify({"success": False, "message": "Invalid Form Data"})

    meaning = Meaning.query.get(mid)
    if meaning == None:
        return jsonify({"success": False, "message": "Invalid Form Data"})
    
    ch = Content.query.filter_by(chapter=chapter).first()
    if ch == None:
        return jsonify({"success": False, "message": "Invalid Form Data"})

    if word != meaning.word:
        m = Meaning.query.filter_by(word=word).first()
        if m != None:
            return jsonify({"success": False, "message": "This word already exists in database."})

    
    meaning.word = word
    meaning.chapter = chapter
    meaning.wordClass = wordClass
    meaning.meaning1 = meaning1
    meaning.meaning2 = meaning2
    meaning.meaning3 = meaning3
    meaning.meaning4 = meaning4
    meaning.meaning5 = meaning5

    db.session.commit()

    userinfo = session["userinfo"]
    session.clear()
    session["administrator"] = True
    session["userinfo"] = userinfo

    data = {
        "id": mid,
        "wordClass": wordClass,
        "word": word,
        "meaning1": meaning1,
        "meaning2": meaning2,
        "meaning3": meaning3,
        "meaning4": meaning4,
        "meaning5": meaning5,
        "chapter": chapter,
        "admin": True
    }

    return jsonify({"success": True, "data": data})


@application.route("/addContent", methods=["POST"])
def addContent():
    if session.get("administrator") != True:
        return jsonify({"success": False, "message": "Invalid Credentials"})

    chapter = request.form.get("chapter")
    if not chapter:
        return jsonify({"success": False, "message": "Incomplete Form"})

    try:
        chapter = int(chapter)
    except ValueError:
        return jsonify({"success": False, "message": "Chapter number is not an integer."})

    c = Content.query.filter_by(chapter=chapter).first()
    if c != None:
        return jsonify({"success": False, "message": "This chapter already exists."})
    
    words = request.form.get("words")
    verbs = request.form.get("verbs")
    cases = request.form.get("cases")
    compound = request.form.get("compound")
    suffix = request.form.get("suffix")
    meanings = request.form.get("meanings")

    if not words or not verbs or not meanings:
        return jsonify({"success": False, "message": "Incomplete Form"})

    content = Content(
        chapter = chapter,
        words = words.strip(),
        verbs = verbs.strip(),
        case = cases.strip(),
        compound = compound.strip(),
        suffix = suffix.strip(),
        meanings = meanings.strip()
    )
    db.session.add(content)
    db.session.commit()

    userinfo = session["userinfo"]
    session.clear()
    session["administrator"] = True
    session["userinfo"] = userinfo

    return jsonify({"success": True})


@application.route("/addNewRule", methods=["POST"])
def addNewRule():
    if session.get("administrator") != True:
        return jsonify({"success": False, "message": "Invalid Credentials"})

    chapter = request.form.get("chapter")
    if not chapter:
        return jsonify({"success": False, "message": "Incomplete Form"})

    try:
        chapter = int(chapter)
    except ValueError:
        return jsonify({"success": False, "message": "Chapter number is not an integer."})

    c = Content.query.filter_by(chapter=chapter).first()
    if c == None:
        return jsonify({"success": False, "message": "This chapter does not exist."})

    rule_number = request.form.get("rule_number")
    if not rule_number:
        return jsonify({"success": False, "message": "Incomplete Form"})

    try:
        rule_number = int(rule_number)
    except ValueError:
        return jsonify({"success": False, "message": "Rule number is not an integer."})

    r = Aphorism.query.get(rule_number)
    if r != None:
        return jsonify({"success": False, "message": "This rule number already exists."})
    
    topic = request.form.get("topic")
    subtopic = request.form.get("subtopic")
    rule = request.form.get("rule")

    if not topic or not subtopic or not rule:
        return jsonify({"success": False, "message": "Incomplete Form"})

    aphorism = Aphorism(
        chapter = chapter,
        rule_number = rule_number,
        topic = topic,
        subtopic = subtopic,
        rule = rule
    )

    db.session.add(aphorism)
    db.session.commit()

    userinfo = session["userinfo"]
    session.clear()
    session["administrator"] = True
    session["userinfo"] = userinfo

    a = Aphorism.query.filter_by(rule_number=rule_number).first()

    data = {
        "id": a.id,
        "rule_number": a.rule_number,
        "topic": a.topic,
        "subtopic": a.subtopic,
        "rule": a.rule,
        "chapter": a.chapter
    }

    return jsonify({"success": True, "data": data})


@application.route("/addverb", methods=["POST"])
def addverb():
    if session.get("administrator") != True:
        return jsonify({"success": False, "message": "Invalid Credentials"})

    chapter = request.form.get("chapter")
    verb = request.form.get("verb")
    meaning = request.form.get("meaning")
    verbClass = request.form.get("verbClass")
    verbForm = request.form.get("verbForm")
    info = request.form.get("info")

    if not chapter or not verb or not meaning:
        return jsonify({"success": False, "message": "Fields marked with(*) are required."})

    try:
        chapter = int(chapter)
    except ValueError:
        return jsonify({"success": False, "message": "Chapter number is not an integer."})

    c = Content.query.filter_by(chapter=chapter).first()
    if c == None:
        return jsonify({"success": False, "message": "This chapter does not exist."})

    verb=verb.strip()
    vr = Verb.query.filter_by(verb=verb).first()
    if vr != None:
        return jsonify({"success": False, "message": "A verb with this name already exists."})

    v = Verb(
        chapter=chapter,
        verb=verb,
        meaning=meaning.strip(),
        verbClass=verbClass.strip(),
        verbForm=verbForm.strip(),
        info=info.strip()
    )

    db.session.add(v)
    db.session.commit()

    userinfo = session["userinfo"]
    session.clear()
    session["administrator"] = True
    session["userinfo"] = userinfo

    return jsonify({"success": True})


@application.route("/addword", methods=["POST"])
def addword():
    if session.get("administrator") != True:
        return jsonify({"success": False, "message": "Invalid Credentials"})
    
    chapter = request.form.get("chapter")
    word = request.form.get("word")
    meaning = request.form.get("meaning")
    gender = request.form.get("gender")
    form = request.form.get("form")
    info = request.form.get("info")

    if not chapter or not meaning or not word or not gender or not form:
        return jsonify({"success": False, "message": "Incomplete form"})

    try:
        chapter = int(chapter)
    except ValueError:
        return jsonify({"success": False, "message": "Chapter number must be an integer."})

    c = Content.query.filter_by(chapter=chapter).first()
    if c == None:
        return jsonify({"success": False, "message": "This chapter does not exist."})

    word = word.strip()
    wrd = Word.query.filter_by(word=word).first()
    if wrd != None:
        return jsonify({"success": False, "message": "A word with this name already exists."})
    
    w = Word(
        chapter=chapter,
        word=word,
        meaning=meaning.strip(),
        gender=gender.strip(),
        form=form.strip(),
        info=info.strip()
    )

    db.session.add(w)
    db.session.commit()

    userinfo = session["userinfo"]
    session.clear()
    session["administrator"] = True
    session["userinfo"] = userinfo

    return jsonify({"success": True})


@application.route("/addmeaning", methods=["POST"])
def addmeaning():
    if session.get("administrator") != True:
        return jsonify({"success": False, "message": "Invalid Credentials"})

    chapter = request.form.get("chapter")
    word = request.form.get("word")
    wordClass = request.form.get("wordClass")
    meaning1 = request.form.get("meaning1")
    meaning2 = request.form.get("meaning2")
    meaning3 = request.form.get("meaning3")
    meaning4 = request.form.get("meaning4")
    meaning5 = request.form.get("meaning5")

    if not chapter or not meaning1 or not word:
        return jsonify({"success": False, "message": "Incomplete form."})

    try:
        chapter = int(chapter)
    except ValueError:
        return jsonify({"success": False, "message": "Chapter number is not an integer."})

    c = Content.query.filter_by(chapter=chapter).first()
    if c == None:
        return jsonify({"success": False, "message": "This chapter does not exist."})

    word = word.strip()
    w = Meaning.query.filter_by(word=word).first()
    if w != None:
        return jsonify({"success": False, "message": "A word with this name already exists."})

    m = Meaning(
        chapter=chapter,
        word=word,
        wordClass=wordClass.strip(),
        meaning1=meaning1.strip(),
        meaning2=meaning2.strip(),
        meaning3=meaning3.strip(),
        meaning4=meaning4.strip(),
        meaning5=meaning5.strip()
    )

    db.session.add(m)
    db.session.commit()

    userinfo = session["userinfo"]
    session.clear()
    session["administrator"] = True
    session["userinfo"] = userinfo

    mng = Meaning.query.filter_by(word=word).first()
    data = {
        "word": mng.word,
        "wordClass": mng.wordClass,
        "id": mng.id,
        "chapter": mng.chapter,
        "meaning1": mng.meaning1,
        "meaning2": mng.meaning2,
        "meaning3": mng.meaning3,
        "meaning4": mng.meaning4,
        "meaning5": mng.meaning5,
        "admin": True
    }

    return jsonify({"success": True, "data": data})


@application.route("/deleteRule/<int:rule_id>")
def deleteRule(rule_id):
    if session.get("administrator") != True:
        return jsonify({"success": False})

    try:
        rule_id = int(rule_id)
    except ValueError:
        return jsonify({"success": False})

    rule = Aphorism.query.get(rule_id)
    if rule == None:
        return jsonify({"success": False})

    db.session.delete(rule)
    db.session.commit()

    userinfo = session["userinfo"]
    session.clear()
    session["administrator"] = True
    session["userinfo"] = userinfo

    return jsonify({"success": True})


@application.route("/deleteWord/<int:word_id>")
def deleteWord(word_id):
    if session.get("administrator") != True:
        return jsonify({"success": False})

    try:
        word_id = int(word_id)
    except ValueError:
        return jsonify({"success": False})

    word = Word.query.get(word_id)
    if word == None:
        return jsonify({"success": False})

    db.session.delete(word)
    db.session.commit()

    userinfo = session["userinfo"]
    session.clear()
    session["administrator"] = True
    session["userinfo"] = userinfo

    return jsonify({"success": True})


@application.route("/deleteVerb/<int:verb_id>")
def deleteVerb(verb_id):
    if session.get("administrator") != True:
        return jsonify({"success": False})

    try:
        verb_id = int(verb_id)
    except ValueError:
        return jsonify({"success": False})

    verb = Verb.query.get(verb_id)
    if verb == None:
        return jsonify({"success": False})

    db.session.delete(verb)
    db.session.commit()

    userinfo = session["userinfo"]
    session.clear()
    session["administrator"] = True
    session["userinfo"] = userinfo

    return jsonify({"success": True})


@application.route("/deleteMeaning/<int:meaning_id>")
def deleteMeaning(meaning_id):
    if session.get("administrator") != True:
        return jsonify({"success": False})

    try:
        meaning_id = int(meaning_id)
    except ValueError:
        return jsonify({"success": False})

    m = Meaning.query.get(meaning_id)
    if m == None:
        return jsonify({"success": False})

    db.session.delete(m)
    db.session.commit()

    userinfo = session["userinfo"]
    session.clear()
    session["administrator"] = True
    session["userinfo"] = userinfo

    return jsonify({"success": True})


@application.route("/deleteChapter/<int:chapter_id>")
def deleteChapter(chapter_id):
    if session.get("administrator") != True:
        return jsonify({"success": False})

    try:
        chapter_id = int(chapter_id)
    except ValueError:
        return jsonify({"success": False})

    c = Content.query.filter_by(chapter=chapter_id).first()
    if c == None:
        return jsonify({"success": False})

    aphorisms = c.aphorisms
    allwords = c.allwords
    allverbs = c.allverbs
    allmeanings = c.allmeanings

    for a in aphorisms:
        db.session.delete(a)
    
    for w in allwords:
        db.session.delete(w)

    for v in allverbs:
        db.session.delete(v)
    
    for m in allmeanings:
        db.session.delete(m)

    db.session.delete(c)
    db.session.commit()

    userinfo = session["userinfo"]
    session.clear()
    session["administrator"] = True
    session["userinfo"] = userinfo

    return jsonify({"success": True})


@application.route("/editnotes/<int:note_id>", methods=["POST", "GET"])
def editnotes(note_id):
    user = get_user()
    if session.get("administrator") != True:
        return redirect(url_for('notes'))

    try:
        note_id = int(note_id)
    except ValueError:
        return redirect(url_for('notes'))

    note = Note.query.get(note_id)
    if note == None:
        return redirect(url_for('notes'))

    if request.method == "GET":
        return render_template(
            "admin/editnote.html",
            admin=session["administrator"],
            note=note,
            user=user
        )

    key = request.form.get("key")
    value1 = request.form.get("value1")
    value2 = request.form.get("value2")
    value3 = request.form.get("value3")
    value4 = request.form.get("value4")
    value5 = request.form.get("value5")
    value6 = request.form.get("value6")
    value7 = request.form.get("value7")
    value8 = request.form.get("value8")
    value9 = request.form.get("value9")
    value10 = request.form.get("value10")
    value11 = request.form.get("value11")
    value12 = request.form.get("value12")
    value13 = request.form.get("value13")
    value14 = request.form.get("value14")
    value15 = request.form.get("value15")

    if not key or not value1:
        return render_template(
            "admin/editnote.html",
            admin=session["administrator"],
            note=note,
            user=user,
            note_update_error="a key and a value is required"
        )

    key = key.strip()
    if key != note.key:
        k = Note.query.filter_by(key=key).first()
        if k != None:
            return render_template(
                "admin/editnote.html",
                admin=session["administrator"],
                note=note,
                user=user,
                note_update_error="This key already exists"
            )

    note.key = key
    note.value1 = value1.strip()
    note.value2 = value2.strip()
    note.value3 = value3.strip()
    note.value4 = value4.strip()
    note.value5 = value5.strip()
    note.value6 = value6.strip()
    note.value7 = value7.strip()
    note.value8 = value8.strip()
    note.value9 = value9.strip()
    note.value10 = value10.strip()
    note.value11 = value11.strip()
    note.value12 = value12.strip()
    note.value13 = value13.strip()
    note.value14 = value14.strip()
    note.value15 = value15.strip()

    db.session.commit()
    session["notes"].clear()
    session["notes"] = Note.query.order_by(Note.key).all()

    return redirect(url_for('notes'))


@application.route("/addnote", methods=["POST", "GET"])
def addnote():
    user = get_user()
    if session.get("administrator") != True:
        return redirect(url_for('notes'))

    if request.method == "GET":
        return render_template(
            "admin/addnote.html",
            admin=session["administrator"],
            user=user
        )
    
    key = request.form.get("key")
    value1 = request.form.get("value1")
    value2 = request.form.get("value2")
    value3 = request.form.get("value3")
    value4 = request.form.get("value4")
    value5 = request.form.get("value5")
    value6 = request.form.get("value6")
    value7 = request.form.get("value7")
    value8 = request.form.get("value8")
    value9 = request.form.get("value9")
    value10 = request.form.get("value10")
    value11 = request.form.get("value11")
    value12 = request.form.get("value12")
    value13 = request.form.get("value13")
    value14 = request.form.get("value14")
    value15 = request.form.get("value15")

    if not key or not value1:
        return render_template(
            "admin/addnote.html",
            admin=session["administrator"],
            user=user,
            note_add_error="a key and a value is required"
        )

    key = key.strip()
    k = Note.query.filter_by(key=key).first()
    if k != None:
        return render_template(
            "admin/addnote.html",
            admin=session["administrator"],
            user=user,
            note_add_error="This key already exists"
        )

    n = Note(
        key = key,
        value1 = value1.strip(),
        value2 = value2.strip(),
        value3 = value3.strip(),
        value4 = value4.strip(),
        value5 = value5.strip(),
        value6 = value6.strip(),
        value7 = value7.strip(),
        value8 = value8.strip(),
        value9 = value9.strip(),
        value10 = value10.strip(),
        value11 = value11.strip(),
        value12 = value12.strip(),
        value13 = value13.strip(),
        value14 = value14.strip(),
        value15 = value15.strip()
    )
    db.session.add(n)
    db.session.commit()

    session["notes"].clear()
    session["notes"] = Note.query.order_by(Note.key).all()

    return redirect(url_for('notes'))


@application.route("/deleteNote/<int:note_id>")
def deleteNote(note_id):
    if session.get("administrator") != True:
        return jsonify({"success": False})
    
    try:
        note_id = int(note_id)
    except ValueError:
        return jsonify({"success": False})

    n = Note.query.get(note_id)
    if n == None:
        return jsonify({"success": False})

    db.session.delete(n)
    db.session.commit()

    session["notes"].clear()
    session["notes"] = Note.query.order_by(Note.key).all()

    return jsonify({"success": True})


@application.route("/search", methods=["POST", "GET"])
def search():
    user = get_user()
    if session.get("administrator") == None:
        session["administrator"] = False

    if request.method == "GET":
        return render_template(
            "search.html",
            admin=session["administrator"],
            user=user,
            results=None
        )

    keyword = request.form.get("keyword")
    if not keyword:
        return render_template(
            "search.html",
            admin=session["administrator"],
            user=user,
            search_error = "Enter a keyword",
            results=None
        )

    keyword = keyword.strip()
    results = {}

    aphorisms = Aphorism.query.all()
    results["aphorisms"] = []
    for a in aphorisms:
        if keyword in a.topic or keyword in a.subtopic or keyword in a.rule:
            results["aphorisms"].append(a)

    words = Word.query.all()
    results["words"] = []
    for w in words:
        if w.search(keyword):
            results["words"].append(w)

    verbs = Verb.query.all()
    results["verbs"] = []
    for v in verbs:
        if v.search(keyword):
            results["verbs"].append(v)

    meanings = Meaning.query.all()
    results["meanings"] = []
    for m in meanings:
        if m.search(keyword):
            results["meanings"].append(m)

    return render_template(
        "search.html",
        admin=session["administrator"],
        user=user,
        results=results,
        keyword=keyword
    )


@application.route("/login", methods=["POST", "GET"])
def login():
    if session.get("userinfo") != None:
        return redirect(url_for('homepage'))

    if request.method == "GET":
        return render_template(
            "auth/login.html"
        )

    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        return render_template(
            "auth/login.html",
            login_error="enter email address and password"
        )

    user = User.query.filter_by(email=email).first()
    if user == None:
        return render_template(
            "auth/login.html",
            login_error="Invalid Credentials"
        )

    if check_password_hash(user.password, password):
        session["userinfo"] = {"username": user.username, "email": user.email}
        if user.admin:
            session["administrator"] = True
        return redirect(url_for('homepage'))
        
    return render_template(
        "auth/login.html",
        login_error="Invalid Credentials"
    )


@application.route("/register", methods=["POST", "GET"])
def register():
    if session.get("userinfo") != None:
        return redirect(url_for('homepage'))

    if request.method == "GET":
        return render_template(
            "auth/register.html"
        )

    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    password1 = request.form.get("password1")

    if not username or not email or not password or not password1:
        return render_template(
            "auth/register.html",
            register_error="All fields marked with (*) are required."
        )

    username = username.strip().lower()
    email = email.strip()
    password = password.strip()
    password1 = password1.strip()
    
    
    if "admin" in username or username in envs.reserved_keywords:
        return render_template(
            "auth/register.html",
            register_error="Username not available."
        )
    

    if password1 != password:
        return render_template(
            "auth/register.html",
            register_error="Passwords don't match."
        )


    if not util.validate_email(email):
        return render_template(
            "auth/register.html",
            register_error="Enter a valid email address"
        )

    if not util.validate_password(password):
        return render_template(
            "auth/register.html",
            register_error="Atleast 6 characters long alpha-numeric password."
        )
        
    if not util.validate_username(username):
        return render_template(
            "auth/register.html",
            register_error="Username can have alphanumeric, ( . ), ( - ) or ( _ ) characters."
        )

    u = User.query.filter_by(username=username).first()
    if u != None:
        return render_template(
            "auth/register.html",
            register_error="This username is not available."
        )

    e = User.query.filter_by(email=email).first()
    if e != None:
        return render_template(
            "auth/register.html",
            register_error="This email is associated with another account"
        )

    password = generate_password_hash(password)
    code = str(random.randint(100000, 999999))

    session["registration"] = {
        "username": username,
        "password": password,
        "email": email,
        "code": code
    }
    
    if util.sendemail(email, code):
        return redirect(url_for('verification'))
    
    return redirect(url_for('cancelverification'))
    
    


@application.route("/verification", methods=["POST", "GET"])
def verification():
    if session.get("registration") == None or session.get("userinfo") != None:
        return redirect(url_for('homepage'))
    
    if request.method == "GET":
        return render_template(
            "auth/verify.html",
            email=session["registration"]["email"]
        )

    code = request.form.get("code")
    if not code:
        return render_template(
            "auth/verify.html",
            email=session["registration"]["email"],
            verify_error="enter the verification code"
        )
    
    if code != session["registration"]["code"]:
        return render_template(
            "auth/verify.html",
            email=session["registration"]["email"],
            verify_error="Incorrect verification code."
        )
    
    return redirect(url_for('confirmation'))


@application.route("/confirmation")
def confirmation():
    if session.get("registration") == None or session.get("userinfo") != None:
        return redirect(url_for('homepage'))
    
    user = User(
        username=session["registration"]["username"],
        email=session["registration"]["email"],
        password=session["registration"]["password"]
    )

    db.session.add(user)
    db.session.commit()
    socketio.emit("newuser registered", {"username": session["registration"]["username"]}, broadcast=True)

    session["registration"].clear()
    session["registration"] = None

    return redirect(url_for('login'))


@application.route("/cancelverification")
def cancelverification():
    if session.get("registration") != None:
        session["registration"].clear()
        session["registration"] = None

    return redirect(url_for('homepage'))


@application.route("/resendVerificationCode")
def resendVerificationCode():
    if session.get("registration") == None or session.get("userinfo") != None:
        return redirect(url_for('homepage'))

    code = str(random.randint(100000, 999999))

    session["registration"]["code"] = code
    
    if util.sendemail(session["registration"]["email"], code):
        return redirect(url_for('verification'))
    
    return redirect(url_for('cancelverification'))
    

@application.route("/logout")
def logout():
    session.clear()
    return jsonify({"success": True})


@application.route("/recover", methods=["POST", "GET"])
def recover():
    if session.get("userinfo") != None:
        return redirect(url_for('homepage'))
    
    if request.method == "GET":
        return render_template(
            "auth/recover.html"
        )

    email = request.form.get("email")

    if not email:
        return render_template(
            "auth/recover.html",
            recover_error="Enter Your Email Address"
        )

    user = User.query.filter_by(email=email).first()
    if user == None:
        return render_template(
            "auth/recover.html",
            recover_error="This email address is not associated with any account."
        )
    
    code = str(random.randint(100000, 999999))
    session["recoverpassword"] = {
        "username": user.username,
        "email": user.email,
        "code": code
    }
    
    if util.sendemail(user.email, code):
        return redirect(url_for('verify'))
    
    return redirect(url_for('cancelRecoverPassword'))


@application.route("/verify", methods=["POST", "GET"])
def verify():
    if session.get("recoverpassword") == None:
        return redirect(url_for('homepage'))

    if request.method == "GET":
        return render_template(
            "auth/verify.html",
            recoverpassword = True,
            email=session["recoverpassword"]["email"]
        )
    
    code = request.form.get("code")
    if not code:
        return render_template(
            "auth/verify.html",
            recoverpassword = True,
            email=session["recoverpassword"]["email"],
            verify_error="Enter the recovery code."
        )

    if code != session["recoverpassword"]["code"]:
        return render_template(
            "auth/verify.html",
            recoverpassword = True,
            email=session["recoverpassword"]["email"],
            verify_error="Incorrect Code"
        )
    
    return redirect(url_for('resetpassword'))


@application.route("/resetpassword", methods=["POST", "GET"])
def resetpassword():
    if session.get("recoverpassword") == None:
        return redirect(url_for('homepage'))

    if request.method == "GET":
        return render_template(
            "auth/reset.html"
        )

    password = request.form.get("password")
    password1 = request.form.get("password1")

    if not password or not password1:
        return render_template(
            "auth/reset.html",
            reset_error="All fields marked with (*) are required."
        )
    
    if password != password1:
        return render_template(
            "auth/reset.html",
            reset_error="Passwords don't match"
        )
    
    if not util.validate_password(password):
        return render_template(
            "auth/reset.html",
            reset_error="Atleast 6 characters long alpha-numeric password."
        )

    user = User.query.filter_by(email=session["recoverpassword"]["email"]).first()
    password = generate_password_hash(password)

    user.password = password
    db.session.commit()

    session["recoverpassword"].clear()
    session["recoverpassword"] = None

    return redirect(url_for('login'))


@application.route("/resendRecoveryCode")
def resendRecoveryCode():
    if session.get("recoverpassword") == None:
        return redirect(url_for('homepage'))

    code = str(random.randint(100000, 999999))
    session["recoverpassword"]["code"] = code
    
    if util.sendemail(session["recoverpassword"]["email"], code):
        return redirect(url_for('verify'))
    
    return redirect(url_for('cancelRecoverPassword'))


@application.route("/cancelRecoverPassword")
def cancelRecoverPassword():
    if session.get("recoverpassword") != None:
        session["recoverpassword"].clear()
        session["recoverpassword"] = None
    
    return redirect(url_for('homepage'))


if __name__ == '__main__':
    socketio.run(application, port=8080)