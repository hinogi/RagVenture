from view.game_view import GameView
from model.world_model import GameModel
import model.game_state as gs
from utils.smart_parser import SmartParserUtils
from utils.embedding_utils import EmbeddingUtils


class GameController:

    def __init__(self):
        
        # init pattern
        self.view = GameView()
        self.model = GameModel()

        # load utils
        self.parser_utils = SmartParserUtils()        
        self.embedding_utils = EmbeddingUtils()
        
        # init states
        self.state = gs.GameState()

    def run_game(self):
        """
        Haupt-Game-Loop mit State-Machine Dispatcher.

        Initialisiert UI, lädt initiale Location-Daten und dispatched
        dann in endlosem Loop zu State-Handlern basierend auf loop_state.
        """
        self.state.running = True

        # Intro :)
        self.view.show_welcome()
        input()

        self.view.update_location(self.model.current_location())
        self.view.update_items(self.model.location_items())
        self.view.update_exits(self.model.location_exits())
        self.view.update_inventory(self.model.player_inventory())
        self.view.update_dialog()

        while self.state.running:

            # rendering
            self.view.refresh()

            if self.state.loop_state == gs.LoopState.PARSE:
                self._handle_parse()

            elif self.state.loop_state == gs.LoopState.VERIFY:
                self._handle_verify()

            elif self.state.loop_state == gs.LoopState.REQUEST:
                self._handle_request()

            elif self.state.loop_state == gs.LoopState.ACTION:
                self._handle_action()

    def _handle_target_candidates(self, exits, items, inventory):
        """
        Sammelt alle möglichen Targets für Entity-Matching.

        Kombiniert Exits, Items und Inventory zu einer Liste von Kandidaten
        für das Embedding-basierte Target-Matching.
        """
        candidates = []
        
        for e in exits:
            candidates.append(e)
        for i in items:
            candidates.append(i)
        for i in inventory:
            candidates.append(i)
        
        return candidates

    def _handle_parse(self):
        """
        PARSE State Handler - holt User-Input und extrahiert Verb/Noun.

        Verarbeitet User-Eingaben (quit, empty, parsing) und extrahiert
        mit spaCy Verb und Noun aus natürlicher Sprache.

        Transitions:
        - → VERIFY: Input erfolgreich geparst
        - Bleibt in PARSE: Empty input oder quit
        """
        # get input
        self.state.parse.input = self.view.get_input()

        # quit
        if self.state.parse.input in ['quit','exit',':q']:
            self.state.running = False
            return
    
        # empty inputs
        if not self.state.parse.input.strip():
            return

        # Parsing
        parsed = self.parser_utils.parse(self.state.parse.input)
        self.state.parse.verb = parsed[0]['verb']
        self.state.parse.noun = parsed[0]['noun']

        # State
        self.state.loop_state = gs.LoopState.VERIFY


    def _handle_verify(self):
        """
        VERIFY State Handler - matcht Command und Target via Embeddings.

        Validiert geparsten Input und nutzt Embedding-basiertes Matching
        um Verb → Command (Threshold 0.95) und Noun → Target (Threshold 0.75)
        zu finden. Bei eindeutigen Matches wird Action direkt gebaut.

        Transitions:
        - → ACTION: Command + Target eindeutig gefunden
        - → REQUEST: Mehrdeutige Matches (User muss wählen)
        - → PARSE: Validierungsfehler (kein Verb/Noun)
        """
        # validierung
        if not self.state.parse.verb or not self.state.parse.noun:
            self.state.dialog = gs.Dialog(
                type=gs.DialogState.MESSAGE,
                message="Das habe ich nicht verstanden."
            )

            self.view.update_dialog(self.state.dialog)
            self.state.loop_state = gs.LoopState.PARSE
            return


        # Command matching
        commands = self.embedding_utils.verb_to_command(self.state.parse.verb)
        good_commands = [c for c in commands if c['sim'] >= .95]

        if len(good_commands) == 1:
            # Eindeutig → direkt in Action
            self.state.action.command = gs.ActionCommands(good_commands[0]['command'])
        else:
            # Mehrdeutig/unklar → für REQUEST speichern
            self.state.parse.command_matches = good_commands


        # Target matching
        all_targets = self._handle_target_candidates(
            self.model.location_exits(),
            self.model.location_items(), 
            self.model.player_inventory()
        )
        sim_targets = self.embedding_utils.match_entities(self.state.parse.noun, all_targets)
        good_targets = [t for t in sim_targets if t['score'] >= .75]

        if len(good_targets) == 1:
            self.state.action.target = good_targets[0]['id']
        else:
            self.state.parse.target_matches = good_targets


        # Action komplett?
        if self.state.action.command and self.state.action.target:
            self.state.loop_state = gs.LoopState.ACTION
        else:
            self.state.loop_state = gs.LoopState.REQUEST



    def _handle_request(self):
        """
        REQUEST State Handler - zeigt Dialog für mehrdeutige Auswahl.

        Baut Dialog für Command- oder Target-Auswahl bei mehrdeutigen Matches.
        Verarbeitet User-Choice und setzt action.command bzw. action.target.

        Transitions:
        - → ACTION: Action komplett (command + target gesetzt)
        - → PARSE: User bricht ab (Choice 0)
        - Bleibt in REQUEST: Ungültige Eingabe oder noch nicht komplett
        """
        # verb/command request
        if len(self.state.parse.good_commands) > 1:

            # Dialog updaten
            self.state.dialog = gs.Dialog(
                type=gs.DialogState.REQUEST_VERB,
                message="Was möchtest Du tun?",
                choices=self.state.parse.good_commands
            )
            self.view.update_dialog(self.state.dialog)

        # noun/action request
        if len(self.state.parse.good_targets) > 1:

            # Dialog updaten
            self.state.dialog = gs.Dialog(
                type=gs.DialogState.REQUEST_NOUN,
                message="Was meinst Du?",
                choices=self.state.parse.good_targets
            )
            self.view.update_dialog(self.state.dialog)
        
        # choice?
        if self.state.dialog.type in [gs.DialogState.REQUEST_VERB, gs.DialogState.REQUEST_NOUN]:
            # validierung
            try:
                choice = int(self.state.parse.input)
            except ValueError:
                pass
                # message
                return
        
            # abbrechen
            if choice == 0:
                self.state.loop_state = gs.LoopState.PARSE
                self.state.parse = gs.Parse()
                self.state.dialog = gs.Dialog()
                self.state.action = gs.Action()
                return
            
            # command to action
            if self.state.dialog.type == gs.DialogState.REQUEST_VERB:
                self.state.action.command = self.state.parse.good_commands[choice - 1]['command']

            # target to action
            if self.state.dialog.type == gs.DialogState.REQUEST_NOUN:
                self.state.action.target = self.state.parse.good_targets[choice - 1]['id']

        return

    def _handle_action(self):
        """
        ACTION State Handler - führt validierte Action aus.

        Verarbeitet GO, TAKE, DROP Commands, updated DB via Model,
        aktualisiert View und setzt Feedback-Dialog.

        Transitions:
        - → PARSE: Nach erfolgreicher Ausführung (State wird resettet)
        """
        if self.state.action.command == gs.ActionCommands.GO:

            result = self.model.move_player(self.state.action.target)

            if result:
                self.state.dialog.message = f'Du bist jetzt in {result[0]['name']}'
            else:
                self.state.dialog.message = 'Ups, gestolpert?'

            # view updates
            self.view.update_location(self.model.current_location())
            self.view.update_exits(self.model.location_exits())
            self.view.update_items(self.model.location_items())
            self.view.update_dialog(self.state.dialog)

        elif self.state.action.command == gs.ActionCommands.TAKE:

            result = self.model.take_item(self.state.action.target)
            
            if result:
                self.state.dialog.message =  f'Du trägst jetzt {result[0]['name']}'
            else:
                self.state.dialog.message =  'Ups, fallengelassen?'

            self.view.update_items(self.model.location_items())
            self.view.update_inventory(self.model.player_inventory())
            self.view.update_dialog(self.state.dialog)

        elif self.state.action.command == gs.ActionCommands.DROP:
            result = self.model.drop_item(self.state.action.target)
            
            if result:
                self.state.dialog.message =  f'Du hast {result[0]['name']} abgelegt.'
            else:
                self.state.dialog.message =  'Ups, nicht da?'

            self.view.update_items(self.model.location_items())
            self.view.update_inventory(self.model.player_inventory())
            self.view.update_dialog(self.state.dialog)


        self.state.loop_state = gs.LoopState.PARSE
        self.state.parse = gs.Parse()
        self.state.action = gs.Action()
        self.state.action = gs.Dialog()
