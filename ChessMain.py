import pygame as pg
import sys
import multiprocessing

from Chess.ChessEngine import MatchState, Action
from Chess.my_logger import log
import Chess.ai as bot

class GameApp:
    BOARD_SIZE = 640
    GRID_SIZE = 8
    CELL_SIZE = BOARD_SIZE // GRID_SIZE
    FPS = 30
    COLOR_LIGHT = (238, 238, 210)
    COLOR_DARK = (118, 150, 86)

    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((self.BOARD_SIZE, self.BOARD_SIZE))
        pg.display.set_caption("My Chess AI")
        self.clock = pg.time.Clock()
        self.assets = {}
        self._load_assets()

    @log(level="INFO")
    def _load_assets(self) -> None:
        pieces = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'bR', 'bN', 'bB', 'bQ', 'bK']
        for p in pieces:
            img = pg.image.load(f"Images/{p}.png")
            self.assets[p] = pg.transform.smoothscale(img, (self.CELL_SIZE, self.CELL_SIZE))

    def _draw_scene(self, state: MatchState) -> None:
        for r in range(self.GRID_SIZE):
            for c in range(self.GRID_SIZE):
                color = self.COLOR_LIGHT if (r + c) % 2 == 0 else self.COLOR_DARK
                rect = pg.Rect(c * self.CELL_SIZE, r * self.CELL_SIZE, self.CELL_SIZE, self.CELL_SIZE)
                pg.draw.rect(self.screen, color, rect)
                
                piece = state.matrix[r][c]
                if piece != "--":
                    self.screen.blit(self.assets[piece], rect)

    def run(self) -> None:
        state = MatchState()
        valid_actions = state.generate_legal_actions()
        action_performed = False 
        
        selected_square = ()
        player_clicks = []
        
        human_plays_white = True
        human_plays_black = False 
        
        ai_is_thinking = False
        ai_process = None
        queue = multiprocessing.Queue()

        running = True
        while running:
            is_human_turn = (state.active_color == 'w' and human_plays_white) or \
                            (state.active_color == 'b' and human_plays_black)
            
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    
                elif event.type == pg.MOUSEBUTTONDOWN and is_human_turn:
                    if not state.is_mate and not state.is_draw:
                        mouse_x, mouse_y = pg.mouse.get_pos()
                        col = mouse_x // self.CELL_SIZE
                        row = mouse_y // self.CELL_SIZE
                        
                        if selected_square == (row, col):
                            selected_square = ()
                            player_clicks = []
                        else:
                            selected_square = (row, col)
                            player_clicks.append(selected_square)
                        
                        if len(player_clicks) == 2:
                            attempt = Action(player_clicks[0], player_clicks[1], state.matrix)
                            
                            if attempt in valid_actions:
                                real_action = valid_actions[valid_actions.index(attempt)]
                                state.apply(real_action)
                                action_performed = True
                                selected_square = ()
                                player_clicks = []
                            else:
                                player_clicks = [selected_square]

                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_z:
                        state.revert()
                        if not human_plays_white or not human_plays_black: 
                            state.revert()
                        action_performed = True
                        ai_is_thinking = False
                        if ai_process: 
                            ai_process.terminate()

            if not state.is_mate and not state.is_draw and not is_human_turn:
                if not ai_is_thinking:
                    ai_is_thinking = True
                    ai_process = multiprocessing.Process(target=bot.compute_best_action, args=(state, valid_actions, queue))
                    ai_process.start()

                if not ai_process.is_alive():
                    chosen_action = queue.get() if not queue.empty() else bot.get_random(valid_actions)
                    state.apply(chosen_action)
                    action_performed = True
                    ai_is_thinking = False

            if action_performed:
                valid_actions = state.generate_legal_actions()
                action_performed = False

            self._draw_scene(state)
            
            if state.is_mate:
                winner = "Black" if state.active_color == 'w' else "White"
                pg.display.set_caption(f"Checkmate! {winner} wins.")
            elif state.is_draw:
                pg.display.set_caption("Stalemate!")

            self.clock.tick(self.FPS)
            pg.display.flip()

        pg.quit()
        sys.exit()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = GameApp()
    app.run()