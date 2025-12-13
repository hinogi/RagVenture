from controller.game_controller import GameController

def main():
    controller = GameController()
    try:
        controller.run_game()
    finally:
        controller.model.close()

if __name__ == '__main__':
    main()