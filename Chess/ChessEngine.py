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
                return True
        return False

    def _get_all_moves(self):
        for r in range(8):
            for c in range(8):
                piece = self.matrix[r][c]
                if piece[0] == self.active_color:
                    if piece[1] == 'p': yield from self._get_pawn_moves(r, c)
                    elif piece[1] == 'R': yield from self._get_rook_moves(r, c)
                    elif piece[1] == 'B': yield from self._get_bishop_moves(r, c)
                    elif piece[1] == 'N': yield from self._get_knight_moves(r, c)
                    elif piece[1] == 'Q': yield from self._get_queen_moves(r, c)
                    elif piece[1] == 'K': yield from self._get_king_moves(r, c)

    def _get_pawn_moves(self, r: int, c: int):
        if self.active_color == 'w':
            if self.matrix[r-1][c] == "--":
                yield Action((r, c), (r-1, c), self.matrix)
                if r == 6 and self.matrix[r-2][c] == "--":
                    yield Action((r, c), (r-2, c), self.matrix)
            if c - 1 >= 0:
                if self.matrix[r-1][c-1][0] == 'b':
                    yield Action((r, c), (r-1, c-1), self.matrix)
                elif (r-1, c-1) == self.en_passant_target:
                    yield Action((r, c), (r-1, c-1), self.matrix, is_ep=True)
            if c + 1 <= 7:
                if self.matrix[r-1][c+1][0] == 'b':
                    yield Action((r, c), (r-1, c+1), self.matrix)
                elif (r-1, c+1) == self.en_passant_target:
                    yield Action((r, c), (r-1, c+1), self.matrix, is_ep=True)
        else:
            if self.matrix[r+1][c] == "--":
                yield Action((r, c), (r+1, c), self.matrix)
                if r == 1 and self.matrix[r+2][c] == "--":
                    yield Action((r, c), (r+2, c), self.matrix)
            if c - 1 >= 0:
                if self.matrix[r+1][c-1][0] == 'w':
                    yield Action((r, c), (r+1, c-1), self.matrix)
                elif (r+1, c-1) == self.en_passant_target:
                    yield Action((r, c), (r+1, c-1), self.matrix, is_ep=True)
            if c + 1 <= 7:
                if self.matrix[r+1][c+1][0] == 'w':
                    yield Action((r, c), (r+1, c+1), self.matrix)
                elif (r+1, c+1) == self.en_passant_target:
                    yield Action((r, c), (r+1, c+1), self.matrix, is_ep=True)

    def _get_rook_moves(self, r: int, c: int):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemy = "b" if self.active_color == 'w' else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    target = self.matrix[end_row][end_col]
                    if target == "--":
                        yield Action((r, c), (end_row, end_col), self.matrix)
                    elif target[0] == enemy:
                        yield Action((r, c), (end_row, end_col), self.matrix)
                        break
                    else: break
                else: break

    def _get_bishop_moves(self, r: int, c: int):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemy = "b" if self.active_color == 'w' else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    target = self.matrix[end_row][end_col]
                    if target == "--":
                        yield Action((r, c), (end_row, end_col), self.matrix)
                    elif target[0] == enemy:
                        yield Action((r, c), (end_row, end_col), self.matrix)
                        break
                    else: break
                else: break

    def _get_knight_moves(self, r: int, c: int):
        moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                if self.matrix[end_row][end_col][0] != self.active_color:
                    yield Action((r, c), (end_row, end_col), self.matrix)

    def _get_queen_moves(self, r: int, c: int):
        yield from self._get_rook_moves(r, c)
        yield from self._get_bishop_moves(r, c)

    def _get_king_moves(self, r: int, c: int):
        moves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        for i in range(8):
            end_row = r + moves[i][0]
            end_col = c + moves[i][1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                if self.matrix[end_row][end_col][0] != self.active_color:
                    yield Action((r, c), (end_row, end_col), self.matrix)

    def _get_castle_moves(self, r: int, c: int, moves: list):
        if self.castling_rights[f"{self.active_color}_ks"]:
            if self.matrix[r][c+1] == '--' and self.matrix[r][c+2] == '--':
                if not self._is_attacked(r, c+1) and not self._is_attacked(r, c+2):
                    moves.append(Action((r, c), (r, c+2), self.matrix, is_castle=True))
                    
        if self.castling_rights[f"{self.active_color}_qs"]:
            if self.matrix[r][c-1] == '--' and self.matrix[r][c-2] == '--' and self.matrix[r][c-3] == '--':
                if not self._is_attacked(r, c-1) and not self._is_attacked(r, c-2):
                    moves.append(Action((r, c), (r, c-2), self.matrix, is_castle=True))


class Action:
    def __init__(self, start: tuple, end: tuple, grid: list, is_ep=False, is_castle=False):
        self.start = start
        self.end = end
        self.piece = grid[start[0]][start[1]]
        self.captured = grid[end[0]][end[1]]
        
        self.is_promotion = (self.piece[1] == 'p' and end[0] in (0, 7))
        self.is_en_passant = is_ep
        if self.is_en_passant:
            self.captured = 'wp' if self.piece == 'bp' else 'bp'
            
        self.is_castle = is_castle
        self.uid = self.start[0] * 1000 + self.start[1] * 100 + self.end[0] * 10 + self.end[1]

    def __eq__(self, other) -> bool:
        return isinstance(other, Action) and self.uid == other.uid

    def __str__(self) -> str:
        cols = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}
        rows = {0: '8', 1: '7', 2: '6', 3: '5', 4: '4', 5: '3', 6: '2', 7: '1'}
        return f"{cols[self.start[1]]}{rows[self.start[0]]}{cols[self.end[1]]}{rows[self.end[0]]}"