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
            # Kurze Formen ohne Artikel
            "geh wald",
            "lauf taverne",
            "renn weg",
            "komm zurück",
            "marschiere los",
            "spaziere see",
            "schlendere marktplatz",
            "eile ausgang",
            "hetze fort",
            "flüchte weg",
            "stürm wald",
            "haste taverne",
            "trabe see",

            # Mit Präposition "zum/zur"
            "geh zum wald",
            "lauf zur taverne",
            "renn zum ausgang",
            "marschiere zum schloss",
            "spaziere zum see",
            "schlendere zur taverne",
            "eile zum ausgang",
            "hetze zum wald",
            "flüchte zum ausgang",
            "stürme zur festung",
            "haste zum ausgang",
            "trabe zum see",
            "schreite zur taverne",
            "pirsch zum lager",
            "stapfe zum wald",

            # Mit Präposition "in/in den/in die"
            "geh in den wald",
            "lauf in die taverne",
            "renn in die taverne",
            "eile in den raum",
            "hetze in den wald",
            "stürme in die festung",

            # Mit Präposition "auf"
            "geh auf den marktplatz",
            "lauf auf den turm",
            "steig auf den turm",
            "kletter auf den turm",

            # Mit Präposition "an"
            "geh an den see",
            "lauf an den fluss",
            "tritt an die tür",

            # Mit "nach" (Richtungen)
            "geh nach norden",
            "lauf nach osten",
            "renn nach süden",
            "eile nach westen",

            # Ich-Form (1. Person Singular)
            "ich gehe zum wald",
            "ich gehe in die taverne",
            "ich gehe auf den marktplatz",
            "ich gehe an den see",
            "ich laufe zum wald",
            "ich renne weg",
            "ich komme zurück",

            # Wir-Form (1. Person Plural)
            "wir gehen zum wald",
            "wir gehen in die taverne",
            "wir laufen zum see",

            # Aufforderung/Vorschlag
            "lass uns zum wald gehen",
            "lass uns in die taverne gehen",
            "gehen wir zum wald",
            "gehen wir in die taverne",
            "laufen wir zum see",

            # Du-Form (Anweisung an Teammitglied)
            "geh du zum wald",
            "gehe du zur taverne",
            "lauf du zum see",
            "geh du in die taverne",

            # Infinitiv (Antwort-Stil)
            "zum wald gehen",
            "zur taverne gehen",
            "in die taverne gehen",
            "auf den marktplatz gehen",
            "an den see gehen",
            "nach norden gehen",

            # Weitere Synonyme
            "spaziere zum wald",
            "spazieren zum see",
            "schlendere zur taverne",
            "schlendern zum marktplatz",
            "eile zum ausgang",
            "eilen zur tür",
            "hetze zum wald",
            "hetzen weg",
            "flüchte zum ausgang",
            "fliehe weg",
            "zieh zum wald",
            "ziehe zur taverne",
            "stürm zum wald",
            "stürme zur festung",
            "haste zum ausgang",
            "hasten weg",
            "trabe zum see",
            "traben wald",
            "schreite zur taverne",
            "schreiten vorwärts",
            "pirsch zum lager",
            "pirschen wald",
            "stapfe durch wald",
            "stapfen see",

            # Komplexe Sätze
            "geh zur taverne und rede mit dem wirt",
            "ich gehe zum wald um den see zu finden",
            "lauf schnell zur taverne",
            "gehe vorsichtig in den wald",
            "können wir zum wald gehen",
            "kann ich zur taverne gehen",
            "darf ich zum see gehen"
        ],
        threshold=0.80
    ),

    CommandTemplate(
        command='take',
        examples=[
            # Kurze Formen ohne Artikel
            "nimm schlüssel",
            "hole beutel",
            "hol fackel",
            "pack seil",
            "greif schwert",
            "sammel münzen",
            "heb hammer auf",
            "raff schlüssel auf",
            "schnapp beutel",
            "klau gold",
            "steck fackel ein",
            "ergreif schwert",
            "fass schlüssel",
            "sicher beutel",

            # Mit Artikel (den/das/die)
            "nimm den schlüssel",
            "nimm das buch",
            "nimm die fackel",
            "hole den beutel",
            "hol dir den beutel",
            "pack die fackel ein",
            "greif nach schwert",
            "sammel die münzen auf",
            "heb das schwert auf",
            "raffe münzen auf",
            "schnapp dir schlüssel",
            "klau das gold",
            "steck den schlüssel ein",
            "ergreife das schwert",
            "fasse den hammer",
            "nehm schlüssel mit",
            "nimm beutel mit",
            "beschaff dir schlüssel",
            "birg das gold",
            "sicher dir beutel",

            # Ich-Form (1. Person Singular)
            "ich nehme schlüssel",
            "ich nehme den schlüssel",
            "ich hole mir schlüssel",
            "ich packe schlüssel ein",
            "ich greife nach schlüssel",
            "ich sammle münzen auf",
            "ich hebe schwert auf",

            # Wir-Form (1. Person Plural)
            "wir nehmen schlüssel",
            "wir nehmen den schlüssel",
            "wir holen uns schlüssel",

            # Vorschlag
            "lass uns schlüssel nehmen",
            "lass uns den schlüssel nehmen",

            # Du-Form (Anweisung an Teammitglied)
            "nimm du schlüssel",
            "nimm du den schlüssel",
            "hol du den beutel",
            "pack du die fackel ein",

            # Infinitiv (Antwort-Stil)
            "schlüssel nehmen",
            "den schlüssel nehmen",
            "beutel holen",
            "fackel einpacken",
            "schwert aufheben",

            # Weitere Synonyme
            "raff schlüssel auf",
            "raffe schlüssel auf",
            "schnapp schlüssel",
            "schnappe dir schlüssel",
            "schnapp dir den schlüssel",
            "klau schlüssel",
            "klaue schlüssel",
            "steck schlüssel ein",
            "stecke schlüssel ein",
            "steck den schlüssel ein",
            "ergreif schlüssel",
            "ergreife schlüssel",
            "fass schlüssel",
            "fasse schlüssel",
            "trag schlüssel weg",
            "nehm schlüssel mit",
            "nehme schlüssel mit",
            "nimm schlüssel mit",
            "beschaff dir schlüssel",
            "beschaffen schlüssel",
            "birg schlüssel",
            "bergen schlüssel",
            "sicher schlüssel",
            "sichere dir schlüssel",
            "sicher dir schlüssel",

            # Komplexe Sätze
            "nimm den schlüssel und öffne die truhe",
            "ich nehme den schlüssel um die truhe zu öffnen",
            "nimm schnell den schlüssel",
            "nimm vorsichtig das buch",
            "kann ich den schlüssel nehmen",
            "darf ich den schlüssel nehmen",
            "nimm alles mit",
            "nimm nicht das schwert"
        ],
        threshold=0.80
    ),

    CommandTemplate(
        command='drop',
        examples=[
            # Kurze Formen ohne Artikel
            "leg schwert ab",
            "wirf fackel weg",
            "stell beutel hin",
            "lass hammer fallen",
            "entsorge schwert",
            "platziere beutel",
            "deponiere hammer",
            "pack schwert aus",
            "verstaue fackel",
            "setz hammer ab",
            "lass schwert liegen",
            "lass schwert los",

            # Mit Artikel (den/das/die)
            "leg das schwert ab",
            "wirf die fackel weg",
            "stell den beutel hin",
            "lass den hammer fallen",
            "entsorge das schwert",
            "platziere den beutel",
            "deponiere den hammer",
            "pack das schwert aus",
            "verstaue die fackel",
            "setz hammer ab",
            "lass schwert zurück",
            "lass schwert da",
            "lad schwert ab",

            # Ich-Form (1. Person Singular)
            "ich lege schwert ab",
            "ich lege das schwert ab",
            "ich werfe schwert weg",
            "ich werfe die fackel weg",
            "ich stelle fackel hin",
            "ich lasse schwert fallen",

            # Wir-Form (1. Person Plural)
            "wir legen schwert ab",
            "wir werfen schwert weg",
            "wir lassen schwert fallen",

            # Vorschlag
            "lass uns schwert ablegen",
            "lass uns das schwert ablegen",

            # Du-Form (Anweisung an Teammitglied)
            "leg du schwert ab",
            "leg du das schwert ab",
            "wirf du die fackel weg",
            "stell du den beutel hin",

            # Infinitiv (Antwort-Stil)
            "schwert ablegen",
            "das schwert ablegen",
            "fackel wegwerfen",
            "beutel hinstellen",
            "hammer fallen lassen",

            # Weitere Synonyme
            "entsorge schwert",
            "entsorgen schwert",
            "platziere schwert",
            "platzieren schwert hier",
            "deponiere beutel",
            "deponieren beutel hier",
            "pack schwert aus",
            "packe schwert aus",
            "lass schwert liegen",
            "lasse schwert liegen",
            "lass schwert los",
            "verstaue schwert",
            "verstauen schwert",
            "setz schwert ab",
            "setze schwert ab",
            "lass schwert zurück",
            "lass schwert da",
            "lad schwert ab",
            "lade schwert ab",
            "laden ab",

            # Komplexe Sätze
            "wirf das schwert weg und nimm den hammer",
            "ich lege das schwert ab um platz zu schaffen",
            "wirf schnell die fackel weg",
            "leg vorsichtig den hammer ab",
            "kann ich das schwert ablegen",
            "darf ich das ablegen",
            "wirf alles weg",
            "leg nicht das schwert ab"
        ],
        threshold=0.80
    ),

    CommandTemplate(
        command='use',
        examples=[
            # Kurze Formen ohne Artikel
            "benutz schlüssel",
            "verwende schlüssel",
            "nutze fackel",
            "öffne truhe",
            "bedien hebel",
            "aktiviere hebel",
            "betätige hebel",
            "drück hebel",
            "zieh hebel",
            "schließ truhe auf",
            "mach truhe auf",
            "entriegle truhe",
            "entsperre truhe",
            "knack truhe",

            # Mit Artikel (den/das/die)
            "benutze den schlüssel",
            "verwende das seil",
            "nutze die fackel",
            "öffne die truhe",
            "bediene den hebel",
            "aktiviere den hebel",
            "betätige den hebel",
            "drücke den hebel",
            "ziehe den hebel",
            "schließ die truhe auf",
            "mach die truhe auf",
            "entriegle die truhe",
            "entsperre die truhe",
            "knacke die truhe auf",
            "spreng truhe auf",
            "leg hebel um",

            # Mit "mit" (Werkzeug/Mittel)
            "öffne truhe mit schlüssel",
            "öffne die truhe mit schlüssel",
            "öffne die truhe mit dem schlüssel",
            "benutze schlüssel an truhe",
            "verwende schlüssel für truhe",

            # Mit "an/auf" (anwenden/einsetzen)
            "wende schlüssel an",
            "wende den schlüssel an",
            "setz schlüssel ein",
            "setze schlüssel ein",
            "setze den schlüssel ein",

            # Ich-Form (1. Person Singular)
            "ich benutze schlüssel",
            "ich benutze den schlüssel",
            "ich öffne truhe",
            "ich öffne die truhe mit schlüssel",
            "ich verwende schlüssel",
            "ich bediene hebel",

            # Wir-Form (1. Person Plural)
            "wir benutzen schlüssel",
            "wir öffnen die truhe",
            "wir verwenden schlüssel",

            # Vorschlag
            "lass uns schlüssel benutzen",
            "lass uns die truhe öffnen",

            # Du-Form (Anweisung an Teammitglied)
            "benutze du schlüssel",
            "benutze du den schlüssel",
            "öffne du die truhe",
            "verwende du das seil",

            # Infinitiv (Antwort-Stil)
            "schlüssel benutzen",
            "den schlüssel benutzen",
            "truhe öffnen",
            "die truhe öffnen",
            "truhe mit schlüssel öffnen",
            "hebel bedienen",

            # Weitere Synonyme
            "aktiviere hebel",
            "aktivieren hebel",
            "betätige hebel",
            "betätigen hebel",
            "drück hebel",
            "drücke hebel",
            "zieh hebel",
            "ziehe hebel",
            "schließ truhe auf",
            "schließe truhe auf",
            "schließ die truhe auf",
            "mach truhe auf",
            "mache truhe auf",
            "krieg truhe auf",
            "kriege truhe auf",
            "entriegle truhe",
            "entriegeln truhe",
            "riegle truhe auf",
            "entsperre truhe",
            "entsperren truhe",
            "sperr truhe auf",
            "knack truhe",
            "knacke truhe auf",
            "spreng truhe auf",
            "leg hebel um",
            "lege hebel um",

            # Komplexe Sätze
            "benutze den schlüssel um die truhe zu öffnen",
            "öffne die truhe mit dem schlüssel und nimm das gold",
            "ich benutze den schlüssel an der truhe",
            "öffne vorsichtig die truhe",
            "benutze schnell den hebel",
            "kann ich den schlüssel benutzen",
            "darf ich die truhe öffnen",
            "öffne nicht die truhe"
        ],
        threshold=0.80
    ),

    CommandTemplate(
        command='examine',
        examples=[
            # Kurze Formen ohne Artikel
            "untersuch truhe",
            "betrachte hammer",
            "inspiziere buch",
            "mustere inschrift",
            "prüf mechanismus",
            "begutachte runen",
            "analysiere karte",
            "schau truhe an",
            "check truhe",
            "kontrolliere truhe",
            "erforsche truhe",
            "durchsuche truhe",
            "scan truhe",
            "beobachte truhe",
            "sichte truhe",
            "überprüf truhe",

            # Mit Artikel (den/das/die)
            "untersuche die truhe",
            "betrachte den hammer",
            "inspiziere das buch",
            "mustere die inschrift",
            "prüfe den mechanismus",
            "begutachte die runen",
            "analysiere die karte",
            "schau die truhe an",
            "checke die truhe",
            "kontrolliere den hammer",
            "erforsche das buch",
            "durchsuche die truhe",
            "such truhe durch",
            "scanne die truhe",
            "beobachte den mechanismus",
            "sichte die runen",
            "überprüfe die truhe",
            "durchleuchte truhe",
            "begucke truhe",

            # Ich-Form (1. Person Singular)
            "ich untersuche truhe",
            "ich untersuche die truhe",
            "ich betrachte truhe",
            "ich inspiziere truhe",
            "ich schaue truhe an",

            # Wir-Form (1. Person Plural)
            "wir untersuchen truhe",
            "wir betrachten die truhe",
            "wir schauen truhe an",

            # Vorschlag
            "lass uns truhe untersuchen",
            "lass uns die truhe untersuchen",

            # Du-Form (Anweisung an Teammitglied)
            "untersuche du truhe",
            "untersuche du die truhe",
            "betrachte du den hammer",
            "schau du die truhe an",

            # Infinitiv (Antwort-Stil)
            "truhe untersuchen",
            "die truhe untersuchen",
            "hammer betrachten",
            "inschrift mustern",
            "buch inspizieren",

            # Weitere Synonyme
            "check truhe",
            "checke truhe",
            "checken truhe",
            "kontrolliere truhe",
            "kontrollieren truhe",
            "beschau truhe",
            "beschaue truhe",
            "beäuge truhe",
            "beäugen truhe",
            "studiere truhe",
            "studieren truhe",
            "erforsche truhe",
            "erforschen truhe",
            "durchsuche truhe",
            "durchsuchen truhe",
            "such truhe durch",
            "suche truhe durch",
            "scan truhe",
            "scanne truhe",
            "scannen truhe",
            "observiere truhe",
            "observieren truhe",
            "beobachte truhe",
            "beobachten truhe",
            "sichte truhe",
            "sichten truhe",
            "überprüf truhe",
            "überprüfe truhe",
            "prüf truhe nach",
            "durchleuchte truhe",
            "durchleuchten truhe",
            "leuchte truhe durch",
            "beguck truhe",
            "begucke truhe",

            # Komplexe Sätze
            "untersuche die truhe genau",
            "betrachte die truhe genauer",
            "ich untersuche die truhe um hinweise zu finden",
            "schau die truhe genau an",
            "untersuche vorsichtig die truhe",
            "kann ich die truhe untersuchen",
            "darf ich das untersuchen",
            "untersuche alles",
            "untersuche nicht die truhe"
        ],
        threshold=0.80
    ),

    CommandTemplate(
        command='read',
        examples=[
            # Kurze Formen ohne Artikel
            "lies buch",
            "studiere text",
            "entziffere inschrift",
            "überfliege buch",
            "durchstöbere buch",
            "dekodiere runen",
            "entschlüssle inschrift",
            "deute runen",
            "verschlinge buch",
            "konsultiere buch",
            "schmökere buch",
            "interpretiere text",
            "übersetze runen",

            # Mit Artikel (den/das/die)
            "lies das buch",
            "studiere den text",
            "entziffere die inschrift",
            "überfliege das buch",
            "flieg buch über",
            "durchstöbere das buch",
            "stöber buch durch",
            "dekodiere die runen",
            "entschlüssle die inschrift",
            "schlüssle inschrift auf",
            "deute die runen",
            "verschlinge das buch",
            "konsultiere das buch",
            "schlag nach in buch",
            "schmökere in buch",
            "interpretiere den text",
            "übersetze die runen",

            # Mit Partikel (durch/vor)
            "lies buch durch",
            "lies text vor",

            # Ich-Form (1. Person Singular)
            "ich lese buch",
            "ich lese das buch",
            "ich lese das buch durch",
            "ich studiere text",
            "ich entziffere inschrift",

            # Wir-Form (1. Person Plural)
            "wir lesen buch",
            "wir lesen das buch",
            "wir studieren text",

            # Vorschlag
            "lass uns buch lesen",
            "lass uns das buch lesen",

            # Du-Form (Anweisung an Teammitglied)
            "lies du buch",
            "lies du das buch",
            "lese du die inschrift",
            "studiere du den text",

            # Infinitiv (Antwort-Stil)
            "buch lesen",
            "das buch lesen",
            "inschrift lesen",
            "text studieren",
            "runen entziffern",

            # Weitere Synonyme
            "überfliege buch",
            "überfliegen buch",
            "flieg buch über",
            "durchstöbere buch",
            "durchstöbern buch",
            "stöber buch durch",
            "stöbere buch durch",
            "studier text",
            "dekodiere runen",
            "dekodieren runen",
            "entschlüssle inschrift",
            "entschlüsseln inschrift",
            "schlüssle inschrift auf",
            "schlüssel inschrift auf",
            "deute runen",
            "deuten runen",
            "verschlinge buch",
            "verschlingen buch",
            "konsultiere buch",
            "konsultieren buch",
            "schlag nach in buch",
            "schlage nach in buch",
            "nachschlagen in buch",
            "schmökere in buch",
            "schmökern buch",
            "vertiefe mich in buch",
            "vertiefen text",
            "interpretiere text",
            "interpretieren runen",
            "übersetze inschrift",
            "übersetzen runen",
            "setz inschrift über",

            # Komplexe Sätze
            "lies das buch um hinweise zu finden",
            "ich lese das buch durch um informationen zu bekommen",
            "lies das buch genau",
            "lies vorsichtig die inschrift",
            "studiere den text genauer",
            "kann ich das buch lesen",
            "darf ich das lesen",
            "lies alles",
            "lies nicht das buch"
        ],
        threshold=0.80
    ),

    CommandTemplate(
        command='talk',
        examples=[
            # Kurze Formen mit "mit"
            "sprich mit wirt",
            "rede mit wirt",
            "unterhalte dich mit wirt",
            "quatsch mit wirt",
            "plaudere mit wirt",
            "frag wirt",
            "befrage wirt",
            "konversiere mit wirt",
            "diskutiere mit wirt",
            "schnacke mit wirt",
            "labere mit wirt",
            "schwatze mit wirt",

            # Kurze Formen ohne "mit" (umgangssprachlich)
            "sprich wirt",
            "rede wirt",
            "quatsch wirt",
            "frag wirt",

            # Mit Artikel (dem/der)
            "sprich mit dem wirt",
            "rede mit dem händler",
            "unterhalte dich mit dem wirt",
            "quatsche mit der hexe",
            "plaudere mit dem schmied",
            "frage den wirt",
            "befrage den wirt",
            "konversiere mit der hexe",
            "diskutiere mit dem händler",
            "schnacke mit dem wirt",
            "labere mit dem händler",
            "schwatze mit der hexe",
            "erzähl wirt etwas",
            "sage wirt etwas",
            "antworte wirt",
            "grüße wirt",

            # Ich-Form (1. Person Singular)
            "ich spreche mit wirt",
            "ich spreche mit dem wirt",
            "ich rede mit wirt",
            "ich rede mit dem händler",
            "ich unterhalte mich mit wirt",
            "ich quatsche mit wirt",

            # Wir-Form (1. Person Plural)
            "wir sprechen mit wirt",
            "wir sprechen mit dem wirt",
            "wir reden mit händler",

            # Vorschlag
            "lass uns mit wirt sprechen",
            "lass uns mit dem wirt reden",

            # Du-Form (Anweisung an Teammitglied)
            "sprich du mit wirt",
            "sprich du mit dem wirt",
            "rede du mit händler",
            "rede du mit dem händler",

            # Infinitiv (Antwort-Stil)
            "mit wirt sprechen",
            "mit dem wirt sprechen",
            "mit händler reden",
            "mit der hexe reden",

            # Weitere Synonyme
            "frag wirt",
            "frage wirt",
            "frag den wirt",
            "befrage wirt",
            "befragen wirt",
            "befrage den wirt",
            "konversiere mit wirt",
            "konversieren mit wirt",
            "diskutiere mit wirt",
            "diskutieren mit wirt",
            "schnack mit wirt",
            "schnacke mit wirt",
            "labere mit wirt",
            "labern mit wirt",
            "schwatze mit wirt",
            "schwatzen mit wirt",
            "parliere mit wirt",
            "parlieren mit wirt",
            "erzähl wirt",
            "erzähle wirt etwas",
            "sage wirt etwas",
            "sagen zu wirt",
            "antworte wirt",
            "grüße wirt",
            "grüßen wirt",

            # Komplexe Sätze
            "sprich mit dem wirt über den schlüssel",
            "ich rede mit dem händler um informationen zu bekommen",
            "rede freundlich mit dem wirt",
            "sprich höflich mit der hexe",
            "frage den wirt nach dem weg",
            "kann ich mit dem wirt sprechen",
            "darf ich mit ihm reden",
            "rede mit allen",
            "sprich nicht mit dem wirt"
        ],
        threshold=0.80
    ),

    CommandTemplate(
        command='look',
        examples=[
            # Kurze Formen (reflexiv "dich um")
            "schau dich um",
            "sieh dich um",
            "guck dich um",
            "blick dich um",
            "späh dich um",

            # Kurze Formen (nur "um")
            "schau um",
            "sieh um",
            "guck um",
            "blick um",

            # Mit "umher"
            "schau umher",
            "blick umher",
            "späh umher",

            # Weitere Synonyme
            "orientiere mich",
            "kundschafte aus",
            "schaft aus",
            "erkunde umgebung",
            "muster umgebung",
            "sondiere umgebung",
            "inspiziere umgebung",
            "erfass umgebung",
            "nimm umgebung wahr",
            "scanne raum",
            "überblicke raum",

            # Allgemein (ohne Partikel)
            "schau",
            "sieh",
            "guck",

            # Ich-Form (1. Person Singular)
            "ich schaue mich um",
            "ich sehe mich um",
            "ich gucke mich um",
            "ich schaue umher",
            "ich blicke umher",
            "ich schaue",

            # Wir-Form (1. Person Plural)
            "wir schauen uns um",
            "wir sehen uns um",
            "wir gucken uns um",

            # Vorschlag
            "lass uns umschauen",
            "lass uns umsehen",

            # Du-Form (Anweisung an Teammitglied)
            "schau du dich um",
            "schaue du dich um",
            "sieh du dich um",
            "guck du dich um",

            # Infinitiv (Antwort-Stil)
            "umschauen",
            "umsehen",
            "sich umschauen",
            "sich umsehen",

            # Weitere Synonyme
            "orientiere mich",
            "orientieren",
            "kundschafte aus",
            "kundschaften aus",
            "schaft aus",
            "schafte aus",
            "erkunde umgebung",
            "erkunden umgebung",
            "verschaff mir überblick",
            "verschaffen überblick",
            "muster umgebung",
            "mustern umgebung",
            "sondiere umgebung",
            "sondieren umgebung",
            "inspiziere umgebung",
            "inspizieren raum",
            "erfass umgebung",
            "erfassen raum",
            "fass umgebung auf",
            "nimm umgebung wahr",
            "wahrnehmen umgebung",
            "scanne raum",
            "scannen umgebung",
            "überblicke raum",
            "überblicken umgebung",
            "blick raum über",

            # Komplexe Sätze
            "schau dich genau um",
            "ich schaue mich um um die umgebung zu erkunden",
            "schau dich vorsichtig um",
            "sieh dich aufmerksam um",
            "kann ich mich umschauen",
            "darf ich mich umsehen",
            "schau dich überall um"
        ],
        threshold=0.80
    )
]
