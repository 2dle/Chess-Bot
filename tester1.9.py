import tkinter as tk
from PIL import Image, ImageTk

minify_hashes = {}

def get_hash(board):
    tmp = ""
    for row in range(8):
        for col in range(8):
            tmp += str(board[row][col])
    return hash(tmp)

def is_check_by_pos(pos, board, color):
    for row in range(8):
        for col in range(8):
            if isinstance(board[row][col], Piece) and board[row][col].color != color:
                for atacked in board[row][col].get_moves(board):
                    if atacked == pos:
                        return True
    return False


def find_king_for_board(color, board):
    for row in range(8):
        for col in range(8):
            if isinstance(board[row][col], King) and board[row][col].color == color:
                return (row, col)
    return (-1, -1)

def get_available_moves_for_board(board, color):
    available_moves = []

    for row in range(8):
        for col in range(8):
            elem = board[row][col]
            if isinstance(elem, Piece) and elem.color == color:
                for new_pos in elem.get_moves(board):
                    tmp_elem = elem.Clone()
                    tmp_board = [row[:] for row in board]
                    tmp_board = tmp_elem.move(tmp_board, new_pos)
                    pos_king = find_king_for_board(color, tmp_board)
                    if not is_check_by_pos(pos_king, tmp_board, color):
                        available_moves.append((row, col, new_pos[0], new_pos[1]))

    return available_moves

def clone_board(board):
    tmp_board = []
    for row in range(8):
        tmp_board.append([])
        for col in range(8):
            tmp_board[row].append(board[row][col])
    return tmp_board

class Piece:
    def __init__(self, color, pos):
        self.color = color
        self.pos = pos

    def get_moves(self, board):
        pass

    def on_move(self, board):
        return board

    def move(self, board, end_pos):
        board[self.pos[0]][self.pos[1]] = '.'
        board[end_pos[0]][end_pos[1]] = self
        self.pos = end_pos
        board = self.on_move(board)
        return board

    def Clone(self):
        return Piece(self.color, self.pos)


class Pawn(Piece):
    def __str__(self):
        return 'pw' if self.color == 'white' else 'pb'
    
    def Clone(self):
        return Pawn(self.color, self.pos)

    def get_moves(self, board):
        moves = []
        row = self.pos[0]
        col = self.pos[1]
        if self.color == 'white':
            if row > 0:
                if board[row - 1][col] == '.':
                    moves.append((row - 1, col))
                # Атака по диагонали влево
                if col > 0 and isinstance(board[row - 1][col - 1], Piece) and board[row - 1][col - 1].color != self.color:
                    moves.append((row - 1, col - 1))
                # Атака по диагонали вправо
                if col < 7 and isinstance(board[row - 1][col + 1], Piece) and board[row - 1][col + 1].color != self.color:
                    moves.append((row - 1, col + 1))
                # Ход на две клетки вперед, если пешка находится на начальной позиции
                if row == 6 and board[row - 1][col] == '.' and board[row - 2][col] == '.':
                    moves.append((row - 2, col))
        else:
            if row < 7:
                if board[row + 1][col] == '.':
                    moves.append((row + 1, col))
                # Атака по диагонали влево
                if col > 0 and isinstance(board[row + 1][col - 1], Piece) and board[row + 1][col - 1].color != self.color:
                    moves.append((row + 1, col - 1))
                # Атака по диагонали вправо
                if col < 7 and isinstance(board[row + 1][col + 1], Piece) and board[row + 1][col + 1].color != self.color:
                    moves.append((row + 1, col + 1))
                # Ход на две клетки вперед, если пешка находится на начальной позиции
                if row == 1 and board[row + 1][col] == '.' and board[row + 2][col] == '.':
                    moves.append((row + 2, col))
        return moves
    
    def on_move(self, board):
        if (self.color == 'black' and self.pos[0] == 7) or (self.color == 'white' and self.pos[0] == 0):
            board[self.pos[0]][self.pos[1]] = Queen(self.color, self.pos)
        return board


class Rook(Piece):
    def __init__(self, color, pos):
        super().__init__(color, pos) 
        self.was_turn = False
    
    def Clone(self):
        result = Rook(self.color, self.pos)
        result.was_turn = self.was_turn
        return result

    def __str__(self):
        return 'rw' if self.color == 'white' else 'rb'

    def on_move(self, board):
        self.was_turn = True
        return board

    def get_moves(self, board):
        moves = []
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        row = self.pos[0]
        col = self.pos[1]
        for dr, dc in directions:
            for i in range(1, 8):
                r, c = row + dr * i, col + dc * i
                if 0 <= r < 8 and 0 <= c < 8:
                    if board[r][c] == '.':
                        moves.append((r, c))
                    elif board[r][c].color != self.color:
                        moves.append((r, c))
                        break
                    else:
                        break
                else:
                    break
        return moves


class Knight(Piece):
    def __str__(self):
        return 'nw' if self.color == 'white' else 'nb'

    def Clone(self):
        return Knight(self.color, self.pos)

    def get_moves(self, board):
        moves = []
        directions = [(1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1)]
        row = self.pos[0]
        col = self.pos[1]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                if board[r][c] == '.' or board[r][c].color != self.color:
                    moves.append((r, c))
        return moves


class Bishop(Piece):
    def __str__(self):
        return 'bw' if self.color == 'white' else 'bb'
    
    def Clone(self):
        return Bishop(self.color, self.pos)

    def get_moves(self, board):
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        row = self.pos[0]
        col = self.pos[1]
        for dr, dc in directions:
            for i in range(1, 8):
                r, c = row + dr * i, col + dc * i
                if 0 <= r < 8 and 0 <= c < 8:
                    if board[r][c] == '.':
                        moves.append((r, c))
                    elif board[r][c].color != self.color:
                        moves.append((r, c))
                        break
                    else:
                        break
                else:
                    break
        return moves


class Queen(Piece):
    def __str__(self):
        return 'qw' if self.color == 'white' else 'qb'
    
    def Clone(self):
        return Queen(self.color, self.pos)

    def get_moves(self, board):
        moves = []
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        row = self.pos[0]
        col = self.pos[1]
        for dr, dc in directions:
            for i in range(1, 8):
                r, c = row + dr * i, col + dc * i
                if 0 <= r < 8 and 0 <= c < 8:
                    if board[r][c] == '.':
                        moves.append((r, c))
                    elif board[r][c].color != self.color:
                        moves.append((r, c))
                        break
                    else:
                        break
                else:
                    break
        return moves


class King(Piece):
    def __init__(self, color, pos):
        super().__init__(color, pos) 
        self.was_turn = False
    
    def Clone(self):
        result = King(self.color, self.pos)
        result.was_turn = self.was_turn
        return result

    def __str__(self):
        return 'kw' if self.color == 'white' else 'kb'
    
    def on_move(self, board):
        if not self.was_turn:
            if self.pos[1] == 1:
                board[self.pos[0]][2] = Rook(self.color, (self.pos[0], 2))
                board[self.pos[0]][0] = '.'
            elif self.pos[1] == 6:
                board[self.pos[0]][5] = Rook(self.color, (self.pos[0], 5))
                board[self.pos[0]][7] = '.'
            
        self.was_turn = True
        return board

    def get_moves(self, board):
        moves = []
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        row = self.pos[0]
        col = self.pos[1]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                if isinstance(board[r][c], Piece) and board[r][c].color != self.color:
                    moves.append((r, c))
                elif board[r][c] == '.':
                    moves.append((r, c))
        
        if not self.was_turn:
            can_right_castle = True
            for i in range(col+1, 7):
                can_right_castle &= (not isinstance(board[row][i], Piece))
            
            can_right_castle &= isinstance(board[row][7], Rook) and (not board[row][7].was_turn)
            if can_right_castle:
                moves.append((row, 6))

            can_laft_castle = True
            for i in range(col-1, 1, -1):
                can_laft_castle &= (not isinstance(board[row][i], Piece))
            
            can_laft_castle &= isinstance(board[row][0], Rook) and (not board[row][0].was_turn)
            if can_laft_castle:
                moves.append((row, 1))

        return moves

class ChessBot:
    def __init__(self):
        self.root = tk.Tk()
        self.canvas = tk.Canvas(self.root, width=400, height=400)
        self.canvas.pack()
        self.board = self.initialize_board()
        self.player_collor = 'white'
        self.bot_collor = 'black' if self.player_collor == 'white' else 'white'
        self.player_turn = True
        self.selected_piece = None
        self.images = {}
        self.load_images()
        self.canvas.bind("<Button-1>", self.on_board_click)
        
    def load_images(self):
        pieces = ['pw', 'pb', 'rw', 'rb', 'nw', 'nb', 'bw', 'bb', 'qw', 'qb', 'kw', 'kb']
        for piece in pieces:
            path = f"images/{piece}.png"
            self.images[piece] = ImageTk.PhotoImage(Image.open(path).resize((45, 45), Image.Resampling.LANCZOS))

    def initialize_board(self):
        board = [['.' for x in range(8)] for y in range(8)]
        board[0] = [Rook('black', (0, 0)), Knight('black', (0, 1)), Bishop('black', (0, 2)), Queen('black', (0, 3)), King('black', (0, 4)), Bishop('black', (0, 5)), Knight('black', (0, 6)), Rook('black', (0, 7))]
        board[1] = [Pawn('black', (1, i)) for i in range(8)]
        board[6] = [Pawn('white', (6, i)) for i in range(8)]
        board[7] = [Rook('white', (7, 0)), Knight('white', (7, 1)), Bishop('white', (7, 2)), Queen('white', (7, 3)), King('white', (7, 4)), Bishop('white', (7, 5)), Knight('white', (7, 6)), Rook('white', (7, 7))]
        return board

    def display_board(self):
        self.canvas.delete('all')
        for row in range(8):
            for col in range(8):
                x0, y0 = col * 50, row * 50
                x1, y1 = x0 + 50, y0 + 50
                color = "AntiqueWhite3" if (row + col) % 2 == 0 else "gray"
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color)
                piece = self.board[row][col]
                if piece != '.':
                    image = self.images[str(piece)]
                    self.canvas.create_image(x0 + 25, y0 + 25, image=image)

    def on_board_click(self, event):
        col = event.x // 50
        row = event.y // 50

        if self.selected_piece is None:
            piece = self.board[row][col]
            if piece != '.' and ((piece.color == 'white' and self.player_turn) or (piece.color == 'black' and not self.player_turn)):
                self.selected_piece = (row, col)
                self.highlight_cell(row, col)
                self.highlight_possible_moves(row, col)
        else:
            # avaliable_moves = self.get_available_moves(self.player_collor)
            selected_elem = self.board[self.selected_piece[0]][self.selected_piece[1]]
            tmp_elem = selected_elem.Clone()
            tmp_board = clone_board(self.board)
            tmp_board = tmp_elem.move(tmp_board, (row, col))
            pos_king = find_king_for_board(self.player_collor, tmp_board)

            if (row, col) in selected_elem.get_moves(self.board) and not is_check_by_pos(pos_king, tmp_board, self.player_collor):
                self.make_player_move(self.selected_piece, (row, col))
            else:
                print("Move is invalid")
            self.selected_piece = None
            self.display_board()

    def highlight_cell(self, row, col):
        x0, y0 = col * 50, row * 50
        x1, y1 = x0 + 50, y0 + 50
        self.canvas.create_rectangle(x0, y0, x1, y1, outline="green", width=4)

    def highlight_possible_cell(self, row, col, fill_color):
        cell_size = 50
        x0, y0 = col * cell_size, row * cell_size
        x1, y1 = x0 + cell_size, y0 + cell_size
        corner_size = 10

        self.canvas.create_polygon(x0, y0, x0 + corner_size, y0, x0, y0 + corner_size, outline="", fill=fill_color)
        self.canvas.create_polygon(x1, y0, x1 - corner_size, y0, x1, y0 + corner_size, outline="", fill=fill_color)
        self.canvas.create_polygon(x0, y1, x0 + corner_size, y1, x0, y1 - corner_size, outline="", fill=fill_color)
        self.canvas.create_polygon(x1, y1, x1 - corner_size, y1, x1, y1 - corner_size, outline="", fill=fill_color)

    def highlight_possible_moves(self, row, col):
        all_moves = self.board[row][col].get_moves(self.board)

        available_moves = []
        for (new_row, new_col) in all_moves:
            selected_elem = self.board[self.selected_piece[0]][self.selected_piece[1]]
            tmp_elem = selected_elem.Clone()
            tmp_board = [row[:] for row in self.board]
            tmp_board = tmp_elem.move(tmp_board, (new_row, new_col))
            pos_king = find_king_for_board(self.player_collor, tmp_board)
            if not is_check_by_pos(pos_king, tmp_board, self.player_collor):
                available_moves.append((new_row, new_col))

        print("Possible moves for the selected piece:")
        for move in available_moves:
            print(move)
            self.highlight_possible_cell(move[0], move[1], "green")

    def find_king(self, color):
        return find_king_for_board(color, self.board)

    def is_check(self, board, color):
        pos = self.find_king(color)
        return is_check_by_pos(pos, board, color)
    
    def is_player_win(self):
        return len(self.get_available_moves(self.bot_collor)) == 0
    
    def is_player_loose(self):
        return len(self.get_available_moves(self.player_collor)) == 0


    def make_player_move(self, start_pos, end_pos):
        piece = self.board[start_pos[0]][start_pos[1]].Clone()
        self.board = piece.move(self.board, end_pos)
        if self.is_player_win():
            print("YOU WIN!!!!!")
            exit(0)

        self.player_turn = False
        self.display_board()
        self.make_bot_move()

    def make_bot_move(self):
        available_moves = self.get_available_moves(self.bot_collor)
        if available_moves:
            move = self.best_of(available_moves)
            start_row, start_col, end_row, end_col = move
            self.make_move((start_row, start_col), (end_row, end_col))
            
            if self.is_player_loose():
                print("YOU LOSE!!!!!")
                exit(0)
            
            self.player_turn = True
            self.display_board()

    def best_of(self, available_moves):
        def try_move(board, move):
            start_row, start_col, end_row, end_col = move
            piece = board[start_row][start_col].Clone()
            piece.move(board, (end_row, end_col))

        """ def undo_move(board, move, captured_piece=None):
            start_row, start_col, end_row, end_col = move
            piece = board[end_row][end_col]
            board[end_row][end_col] = '.'  # Удаляем фигуру с конечной позиции
            board[start_row][start_col] = piece  # Возвращаем фигуру на начальную позицию
            if captured_piece:
                # Если была захвачена фигура, восстанавливаем её на место
                board[end_row][end_col] = captured_piece """

        def evaluate_board(board):
            # Функция оценки текущего состояния доски
            # Здесь можно использовать различные методы оценки
            piece_values = {'pw': 1, 'pb': 1, 'nw': 3.2, 'nb': 3.2, 'bw': 3.3, 'bb': 3.3, 'rw': 5.1, 'rb': 5.1, 'qw': 10, 'qb': 10, 'kw': 999, 'kb': 999}
            player_score = 0
            botscore = 0

            player_pos_king = find_king_for_board(self.player_collor, board)
            bot_pos_king = find_king_for_board(self.bot_collor, board)
            is_player_check = is_check_by_pos(player_pos_king, board, self.player_collor)
            is_bot_check = is_check_by_pos(bot_pos_king, board, self.bot_collor)

            # if is_bot_check:
            #     player_score += 2
            # 
            # if is_player_check:
            #     botscore += 2

            for row in board:
                for piece in row:
                    if isinstance(piece, Piece):
                        if piece.color == self.player_collor:
                            player_score += piece_values[str(piece)] + (7 - piece.pos[0]) * 1
                        else:
                            botscore += piece_values[str(piece)] + piece.pos[0]* 1

            return player_score - botscore

        def minimax(board, maximizing_player, depth, alpha, beta):

            check_hash = str(get_hash(board)) + str(maximizing_player)
            if (check_hash in minify_hashes):
                return minify_hashes[check_hash]

            if depth == 0:
                eval = evaluate_board(board)
                # print(f"Evaluation at depth {depth}: {eval}")
                return eval

            if maximizing_player:
                max_eval = float('-inf')
                
                for move in get_available_moves_for_board(board, self.player_collor):
                    temp_board = clone_board(board)  # Создаем копию доски
                    try_move(temp_board, move)
                    eval = minimax(temp_board, False, depth - 1, alpha, beta)
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
                #print(f"Max evaluation at depth {depth}: {max_eval}")
                minify_hashes[check_hash] = max_eval
                return max_eval
            else:
                min_eval = float('inf')
                for move in get_available_moves_for_board(board, self.bot_collor):
                    temp_board = clone_board(board)  # Создаем копию доски
                    try_move(temp_board, move)
                    eval = minimax(temp_board, True, depth - 1, alpha, beta)
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
                #print(f"Min evaluation at depth {depth}: {min_eval}")
                minify_hashes[check_hash] = min_eval
                return min_eval

        best_move = None
        best_value = float('inf')
        alpha = float('-inf')
        beta = float('inf')
        depth = 3

        
        for move in available_moves:
            temp_board = clone_board(self.board)  # Создаем копию доски
            try_move(temp_board, move)  # Выполняем временный ход
            eval = minimax(temp_board, False, depth, alpha, beta)
            if eval < best_value:
                best_move = move
                best_value = eval
                alpha = max(alpha, eval)

        return best_move

    def make_move(self, start_pos, end_pos):
        piece = self.board[start_pos[0]][start_pos[1]]
        self.board = piece.move(self.board, end_pos)
    
    def clone_board(self):
        tmp_board = []
        for row in range(8):
            tmp_board.append([])
            for col in range(8):
                tmp_board[row].append(self.board[row][col])
        return tmp_board

    def get_available_moves(self, color):
        available_moves = []

        for row in range(8):
            for col in range(8):
                elem = self.board[row][col]
                if isinstance(elem, Piece) and elem.color == color:
                    for new_pos in elem.get_moves(self.board):
                        tmp_elem = elem.Clone()
                        tmp_board = clone_board(self.board)
                        tmp_board = tmp_elem.move(tmp_board, new_pos)
                        pos_king = find_king_for_board(color, tmp_board)
                        if not is_check_by_pos(pos_king, tmp_board, color):
                            available_moves.append((row, col, new_pos[0], new_pos[1]))

        return available_moves
    

    def start_game(self):
        self.display_board()
        self.root.mainloop()

if __name__ == "__main__":
    bot = ChessBot()
    bot.start_game()
