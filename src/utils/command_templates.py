from dataclasses import dataclass


@dataclass
class CommandTemplate:
    command: str
    examples: list[str]
    threshold: float = 0.80


COMMAND_TEMPLATES = [
    CommandTemplate(
        command='go',
        examples=[
            # Imperativ
            "Geh irgendwohin",
            "Gehe zu einem Ort",
            "Gehe in einen Raum",
            "Lauf dorthin",
            "Laufe zu einem Platz",
            "Beweg dich fort",
            "Bewege dich zu einem Ziel",
            "Marschier los",
            "Marschiere dorthin",
            "Wander umher",
            "Wandere durch die Gegend",
            "Renn dorthin",
            "Renne zu einem Ort",
            "Komm an einen Ort",

            # 1. Person
            "Ich gehe irgendwohin",
            "Ich gehe zu einem Ort",
            "Ich laufe dorthin",
            "Ich bewege mich fort",
            "Ich marschiere los",
            "Ich wandere umher",
            "Ich renne zu einem Ort",
            "Ich komme an einen Ort",

            # Infinitiv
            "Gehen zu einem Ort",
            "Laufen in einen Raum",
            "Bewegen zu einem Platz"
        ],
        threshold=0.80
    ),

    CommandTemplate(
        command='take',
        examples=[
            # Imperativ
            "Nimm etwas",
            "Nimm etwas auf",
            "Hol dir etwas",
            "Hole etwas",
            "Pack etwas",
            "Packe etwas ein",
            "Greif nach etwas",
            "Greife etwas",
            "Sammel etwas auf",
            "Sammle etwas",
            "Heb etwas auf",
            "Hebe etwas auf",

            # 1. Person
            "Ich nehme etwas",
            "Ich nehme etwas auf",
            "Ich hole mir etwas",
            "Ich packe etwas ein",
            "Ich greife nach etwas",
            "Ich sammle etwas auf",
            "Ich hebe etwas auf",

            # Infinitiv
            "Nehmen von etwas",
            "Holen von etwas",
            "Aufheben von etwas"
        ],
        threshold=0.80
    ),

    CommandTemplate(
        command='drop',
        examples=[
            # Imperativ
            "Leg etwas ab",
            "Lege etwas ab",
            "Wirf etwas weg",
            "Wirf etwas",
            "Stell etwas hin",
            "Stelle etwas hin",
            "Leg etwas hin",
            "Lass etwas fallen",

            # 1. Person
            "Ich lege etwas ab",
            "Ich werfe etwas weg",
            "Ich stelle etwas hin",
            "Ich lege etwas hin",
            "Ich lasse etwas fallen",

            # Infinitiv
            "Ablegen von etwas",
            "Wegwerfen von etwas",
            "Hinstellen von etwas"
        ],
        threshold=0.80
    ),

    CommandTemplate(
        command='use',
        examples=[
            # Imperativ
            "Benutz etwas",
            "Benutze etwas",
            "Verwend etwas",
            "Verwende etwas",
            "Wende etwas an",
            "Öffne etwas",
            "Öffne etwas mit etwas",
            "Setz etwas ein",
            "Setze etwas ein",
            "Nutz etwas",
            "Nutze etwas",
            "Gebrauch etwas",
            "Gebrauche etwas",
            "Bedien etwas",
            "Bediene etwas",

            # 1. Person
            "Ich benutze etwas",
            "Ich verwende etwas",
            "Ich wende etwas an",
            "Ich öffne etwas",
            "Ich setze etwas ein",
            "Ich nutze etwas",
            "Ich gebrauche etwas",
            "Ich bediene etwas",

            # Infinitiv
            "Benutzen von etwas",
            "Verwenden von etwas",
            "Öffnen von etwas"
        ],
        threshold=0.80
    ),

    CommandTemplate(
        command='examine',
        examples=[
            # Imperativ
            "Untersuch etwas",
            "Untersuche etwas",
            "Betracht etwas",
            "Betrachte etwas",
            "Inspizier etwas",
            "Inspiziere etwas",
            "Muster etwas",
            "Mustere etwas",
            "Prüf etwas",
            "Prüfe etwas",
            "Begutacht etwas",
            "Begutachte etwas",
            "Analysier etwas",
            "Analysiere etwas",

            # 1. Person
            "Ich untersuche etwas",
            "Ich betrachte etwas",
            "Ich inspiziere etwas",
            "Ich mustere etwas",
            "Ich prüfe etwas",
            "Ich begutachte etwas",
            "Ich analysiere etwas",

            # Infinitiv
            "Untersuchen von etwas",
            "Betrachten von etwas",
            "Prüfen von etwas"
        ],
        threshold=0.80
    ),

    CommandTemplate(
        command='read',
        examples=[
            # Imperativ
            "Lies etwas",
            "Lese etwas",
            "Lies etwas durch",
            "Lies etwas vor",
            "Studier etwas",
            "Studiere einen Text",
            "Entziffr etwas",
            "Entziffere etwas",

            # 1. Person
            "Ich lese etwas",
            "Ich lese etwas durch",
            "Ich lese etwas vor",
            "Ich studiere einen Text",
            "Ich entziffere etwas",

            # Infinitiv
            "Lesen von etwas",
            "Durchlesen von etwas",
            "Studieren von etwas"
        ],
        threshold=0.80
    ),

    CommandTemplate(
        command='talk',
        examples=[
            # Imperativ
            "Sprich mit jemandem",
            "Rede mit jemandem",
            "Red mit jemandem",
            "Unterhalt dich mit jemandem",
            "Unterhalte dich",
            "Quatsch mit jemandem",
            "Quatsche mit jemandem",
            "Plauder mit jemandem",
            "Plaudere mit jemandem",
            "Kommunizier mit jemandem",
            "Kommuniziere mit jemandem",

            # 1. Person
            "Ich spreche mit jemandem",
            "Ich rede mit jemandem",
            "Ich unterhalte mich",
            "Ich unterhalte mich mit jemandem",
            "Ich quatsche mit jemandem",
            "Ich plaudere mit jemandem",
            "Ich kommuniziere mit jemandem",

            # Infinitiv
            "Sprechen mit jemandem",
            "Reden mit jemandem",
            "Unterhalten mit jemandem"
        ],
        threshold=0.80
    ),

    CommandTemplate(
        command='look',
        examples=[
            # Imperativ
            "Schau dich um",
            "Schaue dich um",
            "Sieh dich um",
            "Siehe dich um",
            "Guck dich um",
            "Gucke dich um",
            "Schau umher",
            "Blick umher",
            "Blicke umher",
            "Späh umher",
            "Spähe umher",
            "Schau an einen Ort",

            # 1. Person
            "Ich schaue mich um",
            "Ich sehe mich um",
            "Ich gucke mich um",
            "Ich schaue umher",
            "Ich blicke umher",
            "Ich spähe umher",

            # Infinitiv
            "Umschauen",
            "Umsehen",
            "Schauen an einen Ort"
        ],
        threshold=0.80
    )
]
