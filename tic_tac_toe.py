import tkinter as tk 
from tkinter import messagebox 
import random

# --- Game Logic ---
class TicTacToeGame():
    def __init__(self):
        self.state = '         '
        self.player = 'X'
        self.winner = None

    def allowed_moves(self):
        return [self.state[:i] + self.player + self.state[i+1:]
                for i in range(9) if self.state[i] == ' ']

    def make_move(self, next_state):
        if self.winner:
            raise(Exception("Game already completed."))
        if not self.__valid_move(next_state):
            raise(Exception(f"Invalid move: {self.state} -> {next_state}"))

        self.state = next_state
        self.winner = self.predict_winner(self.state)
        if not self.winner:
            self.player = 'O' if self.player == 'X' else 'X'
        else:
            self.player = None

    def playable(self):
        return not self.winner and ' ' in self.state

    def predict_winner(self, state):
        wins = [(0,1,2), (3,4,5), (6,7,8),
                (0,3,6), (1,4,7), (2,5,8),
                (0,4,8), (2,4,6)]
        for a, b, c in wins:
            if state[a] == state[b] == state[c] != ' ':
                return state[a]
        return None
    def __valid_move(self, next_state):
        return next_state in self.allowed_moves()

    def print_board(self):
        s = self.state
        print(f'     {s[0]} | {s[1]} | {s[2]} ')
        print('    -----------')
        print(f'     {s[3]} | {s[4]} | {s[5]} ')
        print('    -----------')
        print(f'     {s[6]} | {s[7]} | {s[8]} ')

# --- Agent ---
class Agent():
    def __init__(self, game_class, epsilon=0.1, alpha=0.5, value_player='X'):
        self.V = {}
        self.NewGame = game_class
        self.epsilon = epsilon
        self.alpha = alpha
        self.value_player = value_player

    def state_value(self, state):
        return self.V.get(state, 0.0)

    def learn_game(self, num_episodes=1000):
        for _ in range(num_episodes):
            self.learn_from_episode()

    def learn_from_episode(self):
        game = self.NewGame()
        _, move = self.learn_select_move(game)
        while move:
            move = self.learn_from_move(game, move)

    def learn_from_move(self, game, move):
        game.make_move(move)
        r = self.__reward(game)
        td_target = r
        next_val = 0.0
        selected_next = None
        if game.playable():
            best_next, selected_next = self.learn_select_move(game)
            next_val = self.state_value(best_next)
        current_val = self.state_value(move)
        self.V[move] = current_val + self.alpha * (r + next_val - current_val)
        return selected_next

    def learn_select_move(self, game):
        state_vals = self.__state_values(game.allowed_moves())
        if game.player == self.value_player:
            best = self.__argmax_V(state_vals)
        else:
            best = self.__argmin_V(state_vals)
        selected = best if random.random() > self.epsilon else self.__random_V(state_vals)
        return best, selected

    def play_select_move(self, game):
        state_vals = self.__state_values(game.allowed_moves())
        if game.player == self.value_player:
            return self.__argmax_V(state_vals)
        else:
            return self.__random_V(state_vals)

    def demo_game(self, verbose=False):
        game = self.NewGame()
        t = 0
        while game.playable():
            if verbose:
                print(f"\nTurn {t}")
                game.print_board()
            move = self.play_select_move(game)
            game.make_move(move)
            t += 1
        if verbose:
            print(f"\nTurn {t}")
            game.print_board()
        return game.winner if game.winner else '-'

    def __state_values(self, states):
        return {s: self.state_value(s) for s in states}

    def __argmax_V(self, state_vals):
        max_val = max(state_vals.values())
        return random.choice([s for s, v in state_vals.items() if v == max_val])

    def __argmin_V(self, state_vals):
        min_val = min(state_vals.values())
        return random.choice([s for s, v in state_vals.items() if v == min_val])

    def __random_V(self, state_vals):
        return random.choice(list(state_vals.keys()))

    def __reward(self, game):
        if game.winner == self.value_player:
            return 1.0
        elif game.winner:
            return -1.0
        return 0.0

# --- Statistics printer ---
def print_game_stats(agent, n=1000):
    results = [agent.demo_game() for _ in range(n)]
    print("Game stats:")
    for k in ['X', 'O', '-']:
        print(f"  {k}: {results.count(k)/n:.2%}")

# --- GUI ---
class TicTacToeGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TicTacToe Game")
        self.geometry("300x350")
        self.resizable(False, False)

        self.agent = None
        self.game = None
        self.human_player = None
        self.agent_player = None

        # Symbol selection frame
        self.symbol_frame = tk.Frame(self)
        self.symbol_frame.pack(pady=50)

        label = tk.Label(self.symbol_frame, text="Choose your symbol:", font=("Arial", 14))
        label.pack(pady=10)

        btn_x = tk.Button(self.symbol_frame, text="X", width=5, font=("Arial", 14), command=lambda: self.start_game('X'))
        btn_o = tk.Button(self.symbol_frame, text="O", width=5, font=("Arial", 14), command=lambda: self.start_game('O'))
        btn_x.pack(side='left', padx=20)
        btn_o.pack(side='right', padx=20)

        # Game board (hidden at first)
        self.board_frame = tk.Frame(self)
        self.buttons = []
        for i in range(9):
            b = tk.Button(self.board_frame, text=' ', font=('Arial', 24), width=3, height=1,
                          command=lambda i=i: self.player_move(i))
            self.buttons.append(b)
        for i, b in enumerate(self.buttons):
            b.grid(row=i//3, column=i%3, padx=5, pady=5)

        self.status_label = tk.Label(self, text="", font=("Arial", 12))
        self.status_label.pack(pady=10)

    def start_game(self, human_symbol):
        self.human_player = human_symbol
        self.agent_player = 'O' if human_symbol == 'X' else 'X'
        self.symbol_frame.pack_forget()

        self.game = TicTacToeGame()
        self.game.player = 'X'
        self.agent = Agent(TicTacToeGame, epsilon=0.1, alpha=0.5, value_player=self.agent_player)

        # Print stats before training
        print("\n--- Avant apprentissage ---")
        print_game_stats(self.agent, 1000)

        self.status_label.config(text="Training AI, please wait...")
        self.update()
        self.agent.learn_game(10000)

        # Print stats after training
        print("\n--- Après apprentissage ---")
        print_game_stats(self.agent, 1000)

        self.board_frame.pack()
        self.status_label.config(text=f"Your symbol: {self.human_player}. {'Your turn!' if self.game.player == self.human_player else 'AI\'s turn...'}")

        if self.game.player == self.agent_player:
            self.after(500, self.ai_move)

    def player_move(self, idx):
        if not self.game.playable() or self.game.player != self.human_player or self.game.state[idx] != ' ':
            return

        new_state = self.game.state[:idx] + self.human_player + self.game.state[idx+1:]
        try:
            self.game.make_move(new_state)
        except Exception as e:
            messagebox.showerror("Invalid Move", str(e))
            return

        self.update_board()
        if self.check_end(): return

        self.status_label.config(text="AI's turn...")
        self.after(500, self.ai_move)

    def ai_move(self):
        if not self.game.playable() or self.game.player != self.agent_player:
            return

        move_state = self.agent.play_select_move(self.game)
        try:
            self.game.make_move(move_state)
        except Exception as e:
            messagebox.showerror("AI Error", str(e))
            return

        self.update_board()
        if not self.check_end():
            self.status_label.config(text="Your turn!")

    def update_board(self):
        for i, b in enumerate(self.buttons):
            b.config(text=self.game.state[i])

    def check_end(self):
        if self.game.winner:
            self.end_game(f"Player {self.game.winner} wins!")
            return True
        elif not self.game.playable():
            self.end_game("It's a draw!")
            return True
        return False

    def end_game(self, message):
        self.status_label.config(text=message)
        messagebox.showinfo("Game Over", message)
        for b in self.buttons:
            b.config(state=tk.DISABLED)

# --- Run the game ---
if __name__ == "__main__":
    app = TicTacToeGUI()
    app.mainloop()
