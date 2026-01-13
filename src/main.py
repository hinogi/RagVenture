"""
RagVenture - NLP Text Adventure Game

Entry Point für das Spiel. Initialisiert GameController und startet
den Main Game Loop mit State-Machine.
"""

from controller.game_controller import GameController

def main():
    """
    Startet das RagVenture Spiel.

    Initialisiert den GameController, startet den Game Loop und
    schließt die DB-Verbindung sauber nach Beendigung.
    """
    controller = GameController()
    try:
        controller.run_game()
    finally:
        controller.model.close()

if __name__ == '__main__':
    main()