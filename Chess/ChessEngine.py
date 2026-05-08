class MatchState:
    def __init__(self):
        self.matrix = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.active_color = 'w'
        self.action_stack = []
        self.king_positions = {'w': (7, 4), 'b': (0, 4)}
        self.is_mate = False
        self.is_draw = False
        self.en_passant_target = None
        self.castling_rights = {'w_ks': True, 'w_qs': True, 'b_ks': True, 'b_qs': True}
        self.rights_history = [self.castling_rights.copy()]

    def get_hash(self) -> str:
        board_str = "".join(["".join(row) for row in self.matrix])
        return f"{board_str}_{self.active_color}_{self.en_passant_target}"

    def apply(self, action) -> None:
        self.matrix[action.start[0]][action.start[1]] = "--"
        self.matrix[action.end[0]][action.end[1]] = action.piece
        self.action_stack.append(action)
        self.active_color = 'b' if self.active_color == 'w' else 'w'

        if action.piece[1] == 'K': 
            self.king_positions[action.piece[0]] = action.end
        if action.is_promotion: 
            self.matrix[action.end[0]][action.end[1]] = action.piece[0] + 'Q'
        if action.is_en_passant: 
            self.matrix[action.start[0]][action.end[1]] = "--"

        if action.piece[1] == 'p' and abs(action.start[0] - action.end[0]) == 2:
            self.en_passant_target = ((action.start[0] + action.end[0]) // 2, action.start[1])
        else:
            self.en_passant_target = None

        if action.is_castle:
            if action.end[1] - action.start[1] > 0:
                self.matrix[action.end[0]][action.end[1] - 1] = self.matrix[action.end[0]][7]
                self.matrix[action.end[0]][7] = '--'
            else:
                self.matrix[action.end[0]][action.end[1] + 1] = self.matrix[action.end[0]][0]
                self.matrix[action.end[0]][0] = '--'

        self._update_castling(action)
        self.rights_history.append(self.castling_rights.copy())

    def revert(self) -> None:
        if len(self.action_stack) == 0:
            return
            
        action = self.action_stack.pop()
        self.matrix[action.start[0]][action.start[1]] = action.piece
        self.matrix[action.end[0]][action.end[1]] = action.captured
        self.active_color = 'b' if self.active_color == 'w' else 'w'
        
        if action.piece[1] == 'K': 
            self.king_positions[action.piece[0]] = action.start
        if action.is_en_passant:
            self.matrix[action.end[0]][action.end[1]] = "--"
            self.matrix[action.start[0]][action.end[1]] = action.captured
            self.en_passant_target = action.end
        if action.piece[1] == 'p' and abs(action.start[0] - action.end[0]) == 2:
            self.en_passant_target = None
            
        self.rights_history.pop()
        self.castling_rights = self.rights_history[-1].copy()
        
        if action.is_castle:
            if action.end[1] - action.start[1] > 0:
                self.matrix[action.end[0]][7] = self.matrix[action.end[0]][action.end[1] - 1]
                self.matrix[action.end[0]][action.end[1] - 1] = '--'
            else:
                self.matrix[action.end[0]][0] = self.matrix[action.end[0]][action.end[1] + 1]
                self.matrix[action.end[0]][action.end[1] + 1] = '--'
            
        self.is_mate = False
        self.is_draw = False

    def _update_castling(self, action) -> None:
        p = action.piece
        if p == 'wK': 
            self.castling_rights['w_ks'] = False
            self.castling_rights['w_qs'] = False
        elif p == 'bK': 
            self.castling_rights['b_ks'] = False
            self.castling_rights['b_qs'] = False
        elif p == 'wR':
            if action.start == (7, 0): self.castling_rights['w_qs'] = False
            elif action.start == (7, 7): self.castling_rights['w_ks'] = False
        elif p == 'bR':
            if action.start == (0, 0): self.castling_rights['b_qs'] = False
            elif action.start == (0, 7): self.castling_rights['b_ks'] = False

    def generate_legal_actions(self) -> list:
        temp_ep = self.en_passant_target
        temp_rights = self.castling_rights.copy()
        
        all_moves = list(self._get_all_moves())
        legal_moves = []
        
        for move in all_moves:
            self.apply(move)
            self.active_color = 'b' if self.active_color == 'w' else 'w'
            if not self._is_attacked(self.king_positions[self.active_color][0], self.king_positions[self.active_color][1]):
                legal_moves.append(move)
            self.active_color = 'b' if self.active_color == 'w' else 'w'
            self.revert()
            
        if not self._is_attacked(self.king_positions[self.active_color][0], self.king_positions[self.active_color][1]):
            self._get_castle_moves(self.king_positions[self.active_color][0], self.king_positions[self.active_color][1], legal_moves)
        else:
            if len(legal_moves) == 0:
                self.is_mate = True
                
        if len(legal_moves) == 0 and not self.is_mate:
            self.is_draw = True
            
        self.en_passant_target = temp_ep
        self.castling_rights = temp_rights
        return legal_moves

    def _is_attacked(self, r: int, c: int) -> bool:
        self.active_color = 'b' if self.active_color == 'w' else 'w'
        enemy_moves = list(self._get_all_moves())
        self.active_color = 'b' if self.active_color == 'w' else 'w'
        
        for move in enemy_moves:
            if move.end == (r, c):
