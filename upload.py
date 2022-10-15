import csv
import os

from flask import Flask, render_template, request
from models import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

def main():
    while True:
        c = input("1 to load contents, 2 to load aphorisms, 3 to load words, 4 to load verbs, 5 to load meanings, 6 to load notes, 7 to exit: ")
        
        try:
            c = int(c)
        except ValueError:
            pass

        if c == 1:
            load_contents()
        elif c == 2:
            load_aphorisms()
        elif c == 3:
            load_words()
        elif c ==4:
            load_verbs()
        elif c == 5:
            load_meanings()
        elif c == 6:
            load_notes()
        elif c == 7:
            db.session.commit()
            break
        else:
            print("Invalid request! Try again.")


def load_notes():
    f = open("csvfiles/notes.csv")
    reader = csv.reader(f)
    for row in reader:
        note = Note(
            key = row[0].strip(),
            value1 = row[1].strip(),
            value2 = row[2].strip(),
            value3 = row[3].strip(),
            value4 = row[4].strip(),
            value5 = row[5].strip(),
            value6 = row[6].strip(),
            value7 = row[7].strip(),
            value8 = row[8].strip(),
            value9 = row[9].strip(),
            value10 = row[10].strip(),
            value11 = row[11].strip(),
            value12 = row[12].strip(),
            value13 = row[13].strip(),
            value14 = row[14].strip(),
            value15 = row[15].strip()
        )
        db.session.add(note)
    f.close()


def load_meanings():
    f = open("csvfiles/meanings.csv")
    reader = csv.reader(f)
    for chapter, word, wordClass, meaning1, meaning2, meaning3, meaning4, meaning5 in reader:
        meaning = Meaning(
            chapter = chapter.strip(),
            word = word.strip(),
            wordClass = wordClass.strip(),
            meaning1 = meaning1.strip(),
            meaning2 = meaning2.strip(),
            meaning3 = meaning3.strip(),
            meaning4 = meaning4.strip(),
            meaning5 = meaning5.strip()
        )
        db.session.add(meaning)
    f.close()
    

def load_verbs():
    f = open("csvfiles/verbs.csv")
    reader = csv.reader(f)
    for row in reader:
        verb = Verb(
            chapter = row[0].strip(),
            verb = row[1].strip(),
            meaning = row[2].strip(),
            verbClass = row[3].strip(),
            verbForm = row[4].strip(),
            info = row[5].strip(),
            present31 = row[6].strip(),
            present32 = row[7].strip(),
            present33 = row[8].strip(),
            present21 = row[9].strip(),
            present22 = row[10].strip(),
            present23 = row[11].strip(),
            present11 = row[12].strip(),
            present12 = row[13].strip(),
            present13 = row[14].strip(),
            imperative31 = row[15].strip(),
            imperative32 = row[16].strip(),
            imperative33 = row[17].strip(),
            imperative21 = row[18].strip(),
            imperative22 = row[19].strip(),
            imperative23 = row[20].strip(),
            imperative11 = row[21].strip(),
            imperative12 = row[22].strip(),
            imperative13 = row[23].strip(),
            past31 = row[24].strip(),
            past32 = row[25].strip(),
            past33 = row[26].strip(),
            past21 = row[27].strip(),
            past22 = row[28].strip(),
            past23 = row[29].strip(),
            past11 = row[30].strip(),
            past12 = row[31].strip(),
            past13 = row[32].strip(),
            potential31 = row[33].strip(),
            potential32 = row[34].strip(),
            potential33 = row[35].strip(),
            potential21 = row[36].strip(),
            potential22 = row[37].strip(),
            potential23 = row[38].strip(),
            potential11 = row[39].strip(),
            potential12 = row[40].strip(),
            potential13 = row[41].strip(),
            ffuture31 = row[42].strip(),
            ffuture32 = row[43].strip(),
            ffuture33 = row[44].strip(),
            ffuture21 = row[45].strip(),
            ffuture22 = row[46].strip(),
            ffuture23 = row[47].strip(),
            ffuture11 = row[48].strip(),
            ffuture12 = row[49].strip(),
            ffuture13 = row[50].strip(),
            sfuture31 = row[51].strip(),
            sfuture32 = row[52].strip(),
            sfuture33 = row[53].strip(),
            sfuture21 = row[54].strip(),
            sfuture22 = row[55].strip(),
            sfuture23 = row[56].strip(),
            sfuture11 = row[57].strip(),
            sfuture12 = row[58].strip(),
            sfuture13 = row[59].strip(),
            conditional31 = row[60].strip(),
            conditional32 = row[61].strip(),
            conditional33 = row[62].strip(),
            conditional21 = row[63].strip(),
            conditional22 = row[64].strip(),
            conditional23 = row[65].strip(),
            conditional11 = row[66].strip(),
            conditional12 = row[67].strip(),
            conditional13 = row[68].strip(),
            benedictive31 = row[69].strip(),
            benedictive32 = row[70].strip(),
            benedictive33 = row[71].strip(),
            benedictive21 = row[72].strip(),
            benedictive22 = row[73].strip(),
            benedictive23 = row[74].strip(),
            benedictive11 = row[75].strip(),
            benedictive12 = row[76].strip(),
            benedictive13 = row[77].strip(),
            pastperfect31 = row[78].strip(),
            pastperfect32 = row[79].strip(),
            pastperfect33 = row[80].strip(),
            pastperfect21 = row[81].strip(),
            pastperfect22 = row[82].strip(),
            pastperfect23 = row[83].strip(),
            pastperfect11 = row[84].strip(),
            pastperfect12 = row[85].strip(),
            pastperfect13 = row[86].strip(),
            perfect31 = row[87].strip(),
            perfect32 = row[88].strip(),
            perfect33 = row[89].strip(),
            perfect21 = row[90].strip(),
            perfect22 = row[91].strip(),
            perfect23 = row[92].strip(),
            perfect11 = row[93].strip(),
            perfect12 = row[94].strip(),
            perfect13 = row[95].strip()            
        )
        db.session.add(verb)
    f.close()


def load_words():
    f = open("csvfiles/words.csv")
    reader = csv.reader(f)
    for row in reader:
        word = Word(
            chapter=row[0].strip(),
            word=row[1].strip(),
            meaning=row[2].strip(),
            gender=row[3].strip(),
            form=row[4].strip(),
            info=row[5].strip(),
            nominative1=row[6].strip(),
            nominative2=row[7].strip(),
            nominative3=row[8].strip(),
            accusative1=row[9].strip(),
            accusative2=row[10].strip(),
            accusative3=row[11].strip(),
            instrumental1=row[12].strip(),
            instrumental2=row[13].strip(),
            instrumental3=row[14].strip(),
            dative1=row[15].strip(),
            dative2=row[16].strip(),
            dative3=row[17].strip(),
            ablative1=row[18].strip(),
            ablative2=row[19].strip(),
            ablative3=row[20].strip(),
            genitive1=row[21].strip(),
            genitive2=row[22].strip(),
            genitive3=row[23].strip(),
            locative1=row[24].strip(),
            locative2=row[25].strip(),
            locative3=row[26].strip()
        )
        db.session.add(word)
    f.close()


def load_contents():
    f = open("csvfiles/contents.csv")
    reader = csv.reader(f)
    for chapter, words, verbs, case, compound, suffix, meanings in reader:
        content = Content(
            chapter=chapter.strip(),
            words=words.strip(),
            verbs=verbs.strip(),
            case=case.strip(),
            compound=compound.strip(),
            suffix=suffix.strip(),
            meanings=meanings.strip()
        )
        db.session.add(content)
    f.close()


def load_aphorisms():
    f = open("csvfiles/aphorisms.csv")
    reader = csv.reader(f)
    for chapter, rule_number, topic, subtopic, rule in reader:
        aphorism = Aphorism(
            chapter=chapter.strip(),
            rule_number=rule_number.strip(),
            topic=topic.strip(),
            subtopic=subtopic.strip(),
            rule=rule.strip()
        )
        db.session.add(aphorism)
    f.close()
    

if __name__ == "__main__":
    with app.app_context():
        main()