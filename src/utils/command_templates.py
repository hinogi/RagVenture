from dataclasses import dataclass
from typing import List


@dataclass
class CommandTemplate:
    command: str
    verbs:  List[str]  # Liste von Verben (Infinitiv + wichtige Formen)
    threshold: float = 0.80


COMMAND_TEMPLATES = [
    CommandTemplate(
        command='go',
        verbs=[
            # Hauptverben
            "gehen", "geh", "gehe",
            "laufen", "lauf", "laufe",
            "rennen", "renn", "renne",
            "kommen", "komm", "komme",
            "marschieren", "marschier", "marschiere",

            # Weitere Bewegungsverben
            "spazieren", "spazier", "spaziere",
            "schlendern", "schlender", "schlendere",
            "eilen", "eil", "eile",
            "hetzen", "hetz", "hetze",
            "flüchten", "flücht", "flüchte",
            "fliehen", "flieh", "fliehe",
            "ziehen", "zieh", "ziehe",

            # Aus Tests ergänzt (fehlende Verben)
            "stürmen", "stürm", "stürme",
            "hasten", "hast", "haste",
            "traben", "trab", "trabe",
            "schreiten", "schreit", "schreite",
            "pirschen", "pirsch", "pirsche",
            "stapfen", "stapf", "stapfe",

            # Weitere sinnvolle Synonyme
            "wandern", "wander", "wandere",
            "steigen", "steig", "steige",
            "klettern", "kletter", "klettere",
            "treten", "tret", "trete",
        ],
        threshold=0.80
    ),

    CommandTemplate(
        command='take',
        verbs=[
            # Hauptverben
            "nehmen", "nimm", "nehme",
            "holen", "hol", "hole",
            "packen", "pack", "packe",
            "greifen", "greif", "greife",

            # Trennbare Verben (wichtig!)
            "aufheben", "heb auf", "hebe auf",
            "mitnehmen", "nehm mit", "nehme mit",
            "aufsammeln", "sammel auf", "sammle auf",
            "einsammeln", "sammel ein", "sammle ein",
            "aufraffen", "raff auf", "raffe auf",
            "einpacken", "pack ein", "packe ein",
            "einstecken", "steck ein", "stecke ein",

            # Weitere Synonyme
            "schnappen", "schnapp", "snappe",
            "ergreifen", "ergreif", "ergreife",
            "klauen", "klau", "klaue",

            # Aus Tests ergänzt (fehlende Verben)
            "fassen", "fass", "fasse",
            "tragen", "trag", "trage",
            "beschaffen", "beschaff", "beschaffe",
            "bergen", "birg", "berge",
            "sichern", "sicher", "sichere",
        ],
        threshold=0.80
    ),

    CommandTemplate(
        command='drop',
        verbs=[
            # Hauptverben (meist trennbar!)
            "ablegen", "leg ab", "lege ab",
            "wegwerfen", "wirf weg", "werfe weg",
            "hinstellen", "stell hin", "stelle hin",
            "hinlegen", "leg hin", "lege hin",
            "fallenlassen", "lass fallen", "lasse fallen",
            "loslassen", "lass los", "lasse los",
            "liegenlassen", "lass liegen", "lasse liegen",

            # Weitere Synonyme
            "entsorgen", "entsorg", "entsorge",
            "platzieren", "platzier", "platziere",
            "deponieren", "deponier", "deponiere",

            # Trennbare Verben
            "auspacken", "pack aus", "packe aus",
            "absetzen", "setz ab", "setze ab",

            # Aus Tests ergänzt
            "verstauen", "verstau", "verstaue",
            "zurücklassen", "lass zurück", "lasse zurück",
            "dalassen", "lass da", "lasse da",
            "abladen", "lad ab", "lade ab",
        ],
        threshold=0.80
    ),

    CommandTemplate(
        command='use',
        verbs=[
            # Hauptverben
            "benutzen", "benutz", "benutze",
            "verwenden", "verwend", "verwende",
            "nutzen", "nutz", "nutze",
            "öffnen", "öffne",
            "bedienen", "bedien", "bediene",
            "anwenden", "wend an", "wende an",

            # Weitere Synonyme
            "aktivieren", "aktivier", "aktiviere",
            "betätigen", "betätig", "betätige",
            "drücken", "drück", "drücke",
            "ziehen", "zieh", "ziehe",
            "gebrauchen", "gebrauch", "gebrauche",
            "einsetzen", "setz ein", "setze ein",

            # Trennbare Verben
            "aufschließen", "schließ auf", "schließe auf",
            "aufmachen", "mach auf", "mache auf",
            "aufkriegen", "krieg auf", "kriege auf",
            "umlegen", "leg um", "lege um",

            # Aus Tests ergänzt (fehlende Verben)
            "entriegeln", "entriegle",  # "entriegle" hatte Probleme
            "entsperren", "entsperr", "entsperre",
            "knacken", "knack", "knacke",  # "knack" hatte Probleme
            "sprengen", "spreng", "sprenge",
        ],
        threshold=0.80
    ),

    CommandTemplate(
        command='examine',
        verbs=[
            # Hauptverben
            "untersuchen", "untersuch", "untersuche",
            "betrachten", "betracht", "betrachte",
            "inspizieren", "inspizier", "inspiziere",
            "mustern", "muster", "mustere",
            "prüfen", "prüf", "prüfe",
            "begutachten", "begutacht", "begutachte",
            "analysieren", "analysier", "analysiere",

            # Weitere Synonyme
            "checken", "check", "checke",
            "kontrollieren", "kontrollier", "kontrolliere",
            "beschauen", "beschau", "beschaue",
            "beäugen", "beäug", "beäuge",
            "studieren", "studier", "studiere",
            "erforschen", "erforsch", "erforsche",
            "durchsuchen", "durchsuch", "durchsuche",

            # Mit "an" (trennbar)
            "anschauen", "schau an", "schaue an",
            "ansehen", "sieh an", "sehe an",

            # Aus Tests ergänzt (fehlende Verben)
            "scannen", "scan", "scanne",
            "observieren", "observier", "observiere",
            "beobachten", "beobacht", "beobachte",
            "sichten", "sicht", "sichte",
            "überprüfen", "überprüf", "überprüfe",
            "durchleuchten", "durchleucht", "durchleuchte",
            "begucken", "beguck", "begucke",
        ],
        threshold=0.80
    ),

    CommandTemplate(
        command='read',
        verbs=[
            # Hauptverben
            "lesen", "lies", "lese",
            "studieren", "studier", "studiere",
            "entziffern", "entziffere",

            # Trennbare Verben
            "durchlesen", "lies durch", "lese durch",
            "vorlesen", "lies vor", "lese vor",
            "überfliegen", "überflieg", "überfliege",
            "durchstöbern", "durchstöber", "durchstöbere",

            # Weitere Synonyme (Runen, Inschriften etc.)
            "dekodieren", "dekodier", "dekodiere",
            "entschlüsseln", "entschlüssel", "entschlüssle",
            "deuten", "deut", "deute",

            # Aus Tests ergänzt (fehlende Verben)
            "verschlingen", "verschling", "verschlinge",
            "konsultieren", "konsultier", "konsultiere",
            "nachschlagen", "schlag nach", "schlage nach",
            "schmökern", "schmöker", "schmökere",
            "vertiefen", "vertief", "vertiefe",  # "sich vertiefen in"
            "interpretieren", "interpretier", "interpretiere",
            "übersetzen", "übersetz", "übersetze",
        ],
        threshold=0.80
    ),

    CommandTemplate(
        command='talk',
        verbs=[
            # Hauptverben
            "sprechen", "sprich", "spreche",
            "reden", "red", "rede",
            "unterhalten", "unterhalte",  # "sich unterhalten"
            "quatschen", "quatsch", "quatsche",
            "plaudern", "plauder", "plaudere",
            "kommunizieren", "kommunizier", "kommuniziere",

            # Weitere Synonyme
            "fragen", "frag", "frage",
            "ansprechen", "sprich an", "spreche an",
            "diskutieren", "diskutier", "diskutiere",
            "konversieren", "konversier", "konversiere",
            "schwatzen", "schwatz", "schwatze",
            "palavern", "palaver", "palavere",

            # Informelle
            "labern", "laber", "labere",
            "schnacken", "schnack", "schnacke",
        ],
        threshold=0.80
    ),

    CommandTemplate(
        command='look',
        verbs=[
            # Hauptverben (reflexiv: "sich umschauen")
            "umschauen", "schau um", "schaue um",
            "umsehen", "sieh um", "sehe um",
            "umgucken", "guck um", "gucke um",
            "umblicken", "blick um", "blicke um",

            # Einfache Formen
            "schauen", "schau", "schaue",
            "sehen", "sieh", "sehe",
            "gucken", "guck", "gucke",
            "blicken", "blick", "blicke",
            "spähen", "späh", "spähe",

            # Erkundung
            "orientieren",  # "sich orientieren"
            "auskundschaften", "kundschaft aus", "kundschafte aus",
            "erkunden", "erkunde",

            # Aus Tests ergänzt (fehlende Verben)
            "mustern", "muster", "mustere",
            "sondieren", "sondier", "sondiere",
            "inspizieren", "inspizier", "inspiziere",
            "erfassen", "erfass", "erfasse",
            "wahrnehmen", "nimm wahr", "nehme wahr",
            "scannen", "scan", "scanne",
            "überblicken", "überblick", "überblicke",
        ],
        threshold=0.80
    ),
]
