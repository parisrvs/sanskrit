import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Content(db.Model):
    __tablename__ = "contents"
    id = db.Column(db.Integer, primary_key=True)
    chapter = db.Column(db.Integer, nullable=False, unique=True)
    words = db.Column(db.String, nullable=False)
    verbs = db.Column(db.String, nullable=False)    
    case = db.Column(db.String, nullable=True)    
    compound = db.Column(db.String, nullable=True)
    suffix = db.Column(db.String, nullable=True)
    meanings = db.Column(db.String, nullable=False)
    aphorisms = db.relationship("Aphorism", lazy=True)
    allwords = db.relationship("Word", lazy=True)
    allverbs = db.relationship("Verb", lazy=True)
    allmeanings = db.relationship("Meaning", lazy=True)

class Aphorism(db.Model):
    __tablename__ = "aphorisms"
    id = db.Column(db.Integer, primary_key=True)
    chapter = db.Column(db.Integer, db.ForeignKey("contents.chapter"), nullable=False)
    rule_number = db.Column(db.Integer, nullable=False, unique=True)
    topic = db.Column(db.String, nullable=False)
    subtopic = db.Column(db.String, nullable=False)
    rule = db.Column(db.String, nullable=False)

class Word(db.Model):
    __tablename__ = "words"
    id = db.Column(db.Integer, primary_key=True)
    chapter = db.Column(db.Integer, db.ForeignKey("contents.chapter"), nullable=False)
    word = db.Column(db.String, nullable=False, unique=True)
    meaning = db.Column(db.String, nullable=False)
    gender = db.Column(db.String, nullable=False)
    form = db.Column(db.String, nullable=False)
    info = db.Column(db.String, nullable=True)
    nominative1 = db.Column(db.String, nullable=True)
    nominative2 = db.Column(db.String, nullable=True)
    nominative3 = db.Column(db.String, nullable=True)
    accusative1 = db.Column(db.String, nullable=True)
    accusative2 = db.Column(db.String, nullable=True)
    accusative3 = db.Column(db.String, nullable=True)
    instrumental1 = db.Column(db.String, nullable=True)
    instrumental2 = db.Column(db.String, nullable=True)
    instrumental3 = db.Column(db.String, nullable=True)
    dative1 = db.Column(db.String, nullable=True)
    dative2 = db.Column(db.String, nullable=True)
    dative3 = db.Column(db.String, nullable=True)
    ablative1 = db.Column(db.String, nullable=True)
    ablative2 = db.Column(db.String, nullable=True)
    ablative3 = db.Column(db.String, nullable=True)
    genitive1 = db.Column(db.String, nullable=True)
    genitive2 = db.Column(db.String, nullable=True)
    genitive3 = db.Column(db.String, nullable=True)
    locative1 = db.Column(db.String, nullable=True)
    locative2 = db.Column(db.String, nullable=True)
    locative3 = db.Column(db.String, nullable=True)

    def search(self, keyword):
        if keyword in self.word or keyword in self.nominative1 or keyword in self.nominative2 or keyword in self.nominative3\
            or keyword in self.accusative1 or keyword in self.accusative2 or keyword in self.accusative3\
                or keyword in self.instrumental1 or keyword in self.instrumental2 or keyword in self.instrumental3\
                    or keyword in self.dative1 or keyword in self.dative2 or keyword in self.dative3\
                        or keyword in self.ablative1 or keyword in self.ablative2 or keyword in self.ablative3\
                            or keyword in self.genitive1 or keyword in self.genitive2 or keyword in self.genitive3\
                                or keyword in self.locative1 or keyword in self.locative2 or keyword in self.locative3:
                                return True
        else:
            return False


class Verb(db.Model):
    __tablename__ = "verbs"
    id = db.Column(db.Integer, primary_key=True)
    chapter = db.Column(db.Integer, db.ForeignKey("contents.chapter"), nullable=False)
    verb = db.Column(db.String, nullable=False, unique=True)
    meaning = db.Column(db.String, nullable=False)
    verbClass = db.Column(db.String, nullable=True)
    verbForm = db.Column(db.String, nullable=True)
    info = db.Column(db.String, nullable=True)
    present31 = db.Column(db.String, nullable=True)
    present32 = db.Column(db.String, nullable=True)
    present33 = db.Column(db.String, nullable=True)
    present21 = db.Column(db.String, nullable=True)
    present22 = db.Column(db.String, nullable=True)
    present23 = db.Column(db.String, nullable=True)
    present11 = db.Column(db.String, nullable=True)
    present12 = db.Column(db.String, nullable=True)
    present13 = db.Column(db.String, nullable=True)
    imperative31 = db.Column(db.String, nullable=True)
    imperative32 = db.Column(db.String, nullable=True)
    imperative33 = db.Column(db.String, nullable=True)
    imperative21 = db.Column(db.String, nullable=True)
    imperative22 = db.Column(db.String, nullable=True)
    imperative23 = db.Column(db.String, nullable=True)
    imperative11 = db.Column(db.String, nullable=True)
    imperative12 = db.Column(db.String, nullable=True)
    imperative13 = db.Column(db.String, nullable=True)
    past31 = db.Column(db.String, nullable=True)
    past32 = db.Column(db.String, nullable=True)
    past33 = db.Column(db.String, nullable=True)
    past21 = db.Column(db.String, nullable=True)
    past22 = db.Column(db.String, nullable=True)
    past23 = db.Column(db.String, nullable=True)
    past11 = db.Column(db.String, nullable=True)
    past12 = db.Column(db.String, nullable=True)
    past13 = db.Column(db.String, nullable=True)
    potential31 = db.Column(db.String, nullable=True)
    potential32 = db.Column(db.String, nullable=True)
    potential33 = db.Column(db.String, nullable=True)
    potential21 = db.Column(db.String, nullable=True)
    potential22 = db.Column(db.String, nullable=True)
    potential23 = db.Column(db.String, nullable=True)
    potential11 = db.Column(db.String, nullable=True)
    potential12 = db.Column(db.String, nullable=True)
    potential13 = db.Column(db.String, nullable=True)
    ffuture31 = db.Column(db.String, nullable=True)
    ffuture32 = db.Column(db.String, nullable=True)
    ffuture33 = db.Column(db.String, nullable=True)
    ffuture21 = db.Column(db.String, nullable=True)
    ffuture22 = db.Column(db.String, nullable=True)
    ffuture23 = db.Column(db.String, nullable=True)
    ffuture11 = db.Column(db.String, nullable=True)
    ffuture12 = db.Column(db.String, nullable=True)
    ffuture13 = db.Column(db.String, nullable=True)
    sfuture31 = db.Column(db.String, nullable=True)
    sfuture32 = db.Column(db.String, nullable=True)
    sfuture33 = db.Column(db.String, nullable=True)
    sfuture21 = db.Column(db.String, nullable=True)
    sfuture22 = db.Column(db.String, nullable=True)
    sfuture23 = db.Column(db.String, nullable=True)
    sfuture11 = db.Column(db.String, nullable=True)
    sfuture12 = db.Column(db.String, nullable=True)
    sfuture13 = db.Column(db.String, nullable=True)
    conditional31 = db.Column(db.String, nullable=True)
    conditional32 = db.Column(db.String, nullable=True)
    conditional33 = db.Column(db.String, nullable=True)
    conditional21 = db.Column(db.String, nullable=True)
    conditional22 = db.Column(db.String, nullable=True)
    conditional23 = db.Column(db.String, nullable=True)
    conditional11 = db.Column(db.String, nullable=True)
    conditional12 = db.Column(db.String, nullable=True)
    conditional13 = db.Column(db.String, nullable=True)
    benedictive31 = db.Column(db.String, nullable=True)
    benedictive32 = db.Column(db.String, nullable=True)
    benedictive33 = db.Column(db.String, nullable=True)
    benedictive21 = db.Column(db.String, nullable=True)
    benedictive22 = db.Column(db.String, nullable=True)
    benedictive23 = db.Column(db.String, nullable=True)
    benedictive11 = db.Column(db.String, nullable=True)
    benedictive12 = db.Column(db.String, nullable=True)
    benedictive13 = db.Column(db.String, nullable=True)
    pastperfect31 = db.Column(db.String, nullable=True)
    pastperfect32 = db.Column(db.String, nullable=True)
    pastperfect33 = db.Column(db.String, nullable=True)
    pastperfect21 = db.Column(db.String, nullable=True)
    pastperfect22 = db.Column(db.String, nullable=True)
    pastperfect23 = db.Column(db.String, nullable=True)
    pastperfect11 = db.Column(db.String, nullable=True)
    pastperfect12 = db.Column(db.String, nullable=True)
    pastperfect13 = db.Column(db.String, nullable=True)
    perfect31 = db.Column(db.String, nullable=True)
    perfect32 = db.Column(db.String, nullable=True)
    perfect33 = db.Column(db.String, nullable=True)
    perfect21 = db.Column(db.String, nullable=True)
    perfect22 = db.Column(db.String, nullable=True)
    perfect23 = db.Column(db.String, nullable=True)
    perfect11 = db.Column(db.String, nullable=True)
    perfect12 = db.Column(db.String, nullable=True)
    perfect13 = db.Column(db.String, nullable=True)


    def search(self, keyword):
        if keyword in self.verb or keyword in self.present31 or keyword in self.present32 or keyword in self.present33\
            or keyword in self.present21 or keyword in self.present22 or keyword in self.present23\
                or keyword in self.present11 or keyword in self.present12 or keyword in self.present13\
                    or keyword in self.imperative31 or keyword in self.imperative32 or keyword in self.imperative33\
                        or keyword in self.imperative21 or keyword in self.imperative22 or keyword in self.imperative23\
                            or keyword in self.imperative11 or keyword in self.imperative12 or keyword in self.imperative13\
                                or keyword in self.past31 or keyword in self.past32 or keyword in self.past33\
                                    or keyword in self.past21 or keyword in self.past22 or keyword in self.past23\
                                        or keyword in self.past11 or keyword in self.past12 or keyword in self.past13\
                                            or keyword in self.potential31 or keyword in self.potential32 or keyword in self.potential33\
                                                or keyword in self.potential21 or keyword in self.potential22 or keyword in self.potential23\
                                                    or keyword in self.potential11 or keyword in self.potential12 or keyword in self.potential13\
                                                        or keyword in self.ffuture31 or keyword in self.ffuture32 or keyword in self.ffuture33\
                                                            or keyword in self.ffuture21 or keyword in self.ffuture22 or keyword in self.ffuture23\
                                                                or keyword in self.ffuture11 or keyword in self.ffuture12 or keyword in self.ffuture13\
                                                                    or keyword in self.sfuture31 or keyword in self.sfuture32 or keyword in self.sfuture33\
                                                                        or keyword in self.sfuture21 or keyword in self.sfuture22 or keyword in self.sfuture23\
                                                                            or keyword in self.sfuture11 or keyword in self.sfuture12 or keyword in self.sfuture13\
                                                                                or keyword in self.conditional31 or keyword in self.conditional32 or keyword in self.conditional33\
                                                                                    or keyword in self.conditional21 or keyword in self.conditional22 or keyword in self.conditional23\
                                                                                        or keyword in self.conditional11 or keyword in self.conditional12 or keyword in self.conditional13\
                                                                                            or keyword in self.benedictive31 or keyword in self.benedictive32 or keyword in self.benedictive33\
                                                                                                or keyword in self.benedictive21 or keyword in self.benedictive22 or keyword in self.benedictive23\
                                                                                                    or keyword in self.benedictive11 or keyword in self.benedictive12 or keyword in self.benedictive13\
                                                                                                        or keyword in self.pastperfect31 or keyword in self.pastperfect32 or keyword in self.pastperfect33\
                                                                                                            or keyword in self.pastperfect21 or keyword in self.pastperfect22 or keyword in self.pastperfect23\
                                                                                                                or keyword in self.pastperfect11 or keyword in self.pastperfect12 or keyword in self.pastperfect13\
                                                                                                                    or keyword in self.perfect31 or keyword in self.perfect32 or keyword in self.perfect33\
                                                                                                                        or keyword in self.perfect21 or keyword in self.perfect22 or keyword in self.perfect23\
                                                                                                                            or keyword in self.perfect11 or keyword in self.perfect12 or keyword in self.perfect13:
                                                                                                                            return True
        else:
            return False
                                                                                                        


class Meaning(db.Model):
    __tablename__ = "meanings"
    id = db.Column(db.Integer, primary_key=True)
    chapter = db.Column(db.Integer, db.ForeignKey("contents.chapter"), nullable=False)
    word = db.Column(db.String, nullable=False, unique=True)
    wordClass = db.Column(db.String, nullable=True)
    meaning1 = db.Column(db.String, nullable=False)
    meaning2 = db.Column(db.String, nullable=True)
    meaning3 = db.Column(db.String, nullable=True)
    meaning4 = db.Column(db.String, nullable=True)
    meaning5 = db.Column(db.String, nullable=True)

    def search(self, keyword):
        if keyword in self.word or keyword in self.meaning1 or keyword in self.meaning2\
            or keyword in self.meaning3 or keyword in self.meaning4 or keyword in self.meaning5:
            return True
        else:
            return False


class Note(db.Model):
    __tablename__ = "notes"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String, nullable=False, unique=True)
    value1 = db.Column(db.String, nullable=False)
    value2 = db.Column(db.String, nullable=True)
    value3 = db.Column(db.String, nullable=True)
    value4 = db.Column(db.String, nullable=True)
    value5 = db.Column(db.String, nullable=True)
    value6 = db.Column(db.String, nullable=True)
    value7 = db.Column(db.String, nullable=True)
    value8 = db.Column(db.String, nullable=True)
    value9 = db.Column(db.String, nullable=True)
    value10 = db.Column(db.String, nullable=True)
    value11 = db.Column(db.String, nullable=True)
    value12 = db.Column(db.String, nullable=True)
    value13 = db.Column(db.String, nullable=True)
    value14 = db.Column(db.String, nullable=True)
    value15 = db.Column(db.String, nullable=True)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    counter = db.Column(db.String, nullable=True)
    chats = db.relationship("Chat", lazy=True)


class Chat(db.Model):
    __tablename__ = "chats"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, db.ForeignKey("users.username"), nullable=False)
    message = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False)
    sendTo = db.Column(db.String, nullable=False, default="everyone")