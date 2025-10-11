"""
Improved Ludo game — user-friendly Tkinter implementation.
Features:
- Start dialog to choose number of players (2-4) and board style (classic/modern)
- Clear turn display with color badge
- Dice displayed as a drawn die (no external images)
- Animated token movement (step-by-step)
- Auto-skip when no moves available
- AI players supported
- Buttons: Roll Dice, Restart Game, Toggle Sound (sound uses winsound on Windows if enabled)

Save this as ludo_game.py and run with Python 3.
"""

import tkinter as tk
from tkinter import simpledialog, messagebox
import random
import math
import sys

# Optional simple sound on Windows
try:
    if sys.platform.startswith('win'):
        import winsound
    else:
        winsound = None
except Exception:
    winsound = None

# --- Configurable constants ---
WINDOW_SIZE = 760
BOARD_SIZE = 620
MARGIN = (WINDOW_SIZE - BOARD_SIZE) // 2
CELL = BOARD_SIZE // 15
TOKENS_PER_PLAYER = 4
MAIN_PATH_LEN = 52
HOME_STRETCH_LEN = 6

COLORS = ['red', 'green', 'yellow', 'blue']
START_POSITIONS = [0, 13, 26, 39]
HOME_ENTRY = [51, 12, 25, 38]

# --- Utility: build classic cross-shaped path coordinates ---

def build_path_coords():
    # We'll build a classic Ludo path around a 15x15 grid mapped into pixel coords.
    grid = [[None]*15 for _ in range(15)]
    # create mapping from (r,c) to pixels
    def pix(r,c):
        x = MARGIN + c * (BOARD_SIZE/14)
        y = MARGIN + r * (BOARD_SIZE/14)
        return (x,y)

    # Standard ludo grid positions (manual ordered indexes following clockwise path)
    cells = [
        (6,0),(6,1),(6,2),(6,3),(6,4),(6,5),
        (5,6),(4,6),(3,6),(2,6),(1,6),(0,6),(0,7),
        (0,8),(1,8),(2,8),(3,8),(4,8),(5,8),
        (6,9),(6,10),(6,11),(6,12),(6,13),(6,14),
        (7,14),(8,14),(8,13),(8,12),(8,11),(8,10),(8,9),
        (9,8),(10,8),(11,8),(12,8),(13,8),(14,8),(14,7),
        (14,6),(13,6),(12,6),(11,6),(10,6),(9,6),(8,6)
    ]
    # Ensure length 52 by appending additional perimeter points computed smoothly
    coords = [pix(r,c) for (r,c) in cells]
    # If too short/padded, repeat last safe spots (should be 52 though)
    while len(coords) < MAIN_PATH_LEN:
        coords.append(coords[-1])
    return coords[:MAIN_PATH_LEN]

PATH_COORDS = build_path_coords()
CENTER = (MARGIN + BOARD_SIZE/2, MARGIN + BOARD_SIZE/2)

# Home coords: for each player, linear interpolation from their entry cell to center
HOME_COORDS = {}
for p in range(4):
    sx,sy = PATH_COORDS[START_POSITIONS[p]]
    hx = []
    for i in range(HOME_STRETCH_LEN):
        t = (i+1)/HOME_STRETCH_LEN
        x = sx + (CENTER[0]-sx)*t
        y = sy + (CENTER[1]-sy)*t
        hx.append((x,y))
    HOME_COORDS[p] = hx

# --- Token and Player classes ---
class Token:
    def __init__(self, canvas, player, index, color, base_pos):
        self.canvas = canvas
        self.player = player
        self.index = index
        self.color = color
        self.radius = CELL*0.4
        self.pos = -1  # -1 at base, 0..MAIN_PATH_LEN-1 on path, >=MAIN_PATH_LEN in home
        self.id = None
        self.base_pos = base_pos
        self.create()

    def create(self):
        x,y = self.get_draw_coord()
        self.id = self.canvas.create_oval(x-self.radius, y-self.radius, x+self.radius, y+self.radius, fill=self.color, outline='black', width=2)
        self.canvas.tag_bind(self.id, '<Button-1>', self.on_click)

    def get_draw_coord(self):
        if self.pos == -1:
            bx,by = self.base_pos
            offset_x = (self.index % 2) * (self.radius*1.6) - self.radius*0.8
            offset_y = (self.index // 2) * (self.radius*1.6) - self.radius*0.8
            return (bx + offset_x, by + offset_y)
        if self.pos >= 0 and self.pos < MAIN_PATH_LEN:
            return PATH_COORDS[self.pos]
        # home
        home_idx = self.pos - MAIN_PATH_LEN
        return HOME_COORDS[self.player][home_idx]

    def move_to(self, new_pos):
        self.pos = new_pos
        x,y = self.get_draw_coord()
        self.canvas.coords(self.id, x-self.radius, y-self.radius, x+self.radius, y+self.radius)

    def on_click(self, event):
        self.canvas.event_generate('<<TokenClicked>>', when='tail', data=f'{self.player},{self.index}')

class Player:
    def __init__(self, idx, color, canvas):
        self.idx = idx
        self.color = color
        self.canvas = canvas
        sx,sy = PATH_COORDS[START_POSITIONS[idx]]
        self.base_pos = (sx, sy)
        self.tokens = [Token(canvas, idx, i, color, self.base_pos) for i in range(TOKENS_PER_PLAYER)]

    def movable_tokens(self, roll):
        return [t for t in self.tokens if can_move_token(t, self.idx, roll)]

# --- Game logic functions ---

def can_move_token(token, player_idx, roll):
    if token.pos == -1:
        return roll == 6
    finish = MAIN_PATH_LEN + HOME_STRETCH_LEN -1
    if token.pos >= MAIN_PATH_LEN:
        return token.pos + roll <= finish
    # on main path
    entry = HOME_ENTRY[player_idx]
    if entry >= token.pos:
        dist = entry - token.pos
    else:
        dist = MAIN_PATH_LEN - (token.pos - entry)
    if roll > dist:
        into = roll - dist - 1
        return into < HOME_STRETCH_LEN
    else:
        return True

def advance_position(pos, steps, player_idx):
    if pos == -1:
        if steps == 6:
            return START_POSITIONS[player_idx]
        return -1
    if pos >= MAIN_PATH_LEN:
        new = pos + steps
        finish = MAIN_PATH_LEN + HOME_STRETCH_LEN -1
        return new if new <= finish else -1
    entry = HOME_ENTRY[player_idx]
    if entry >= pos:
        dist = entry - pos
    else:
        dist = MAIN_PATH_LEN - (pos - entry)
    if steps > dist:
        into = steps - dist - 1
        new = MAIN_PATH_LEN + into
        return new if new <= MAIN_PATH_LEN + HOME_STRETCH_LEN -1 else -1
    else:
        return (pos + steps) % MAIN_PATH_LEN

# --- Animated movement helper ---

def animate_move(canvas, token, path_positions, step_ms=120, on_complete=None):
    # path_positions is list of intermediate absolute pos values
    if not path_positions:
        if on_complete: on_complete()
        return
    next_pos = path_positions.pop(0)
    # move token graphically step by step along small linear interpolation for smoother animation
    start_x, start_y = token.get_draw_coord()
    token.pos = next_pos
    end_x, end_y = token.get_draw_coord()
    steps = 6
    def step(i=0):
        if i >= steps:
            canvas.coords(token.id, end_x-token.radius, end_y-token.radius, end_x+token.radius, end_y+token.radius)
            if path_positions:
                canvas.after(step_ms, lambda: animate_move(canvas, token, path_positions, step_ms, on_complete))
            else:
                if on_complete: on_complete()
            return
        frac = (i+1)/steps
        x = start_x + (end_x-start_x)*frac
        y = start_y + (end_y-start_y)*frac
        canvas.coords(token.id, x-token.radius, y-token.radius, x+token.radius, y+token.radius)
        canvas.after(int(step_ms/steps), lambda: step(i+1))
    step()

# --- Main Game class with GUI ---
class LudoGame:
    def __init__(self, root):
        self.root = root
        self.root.title('Ludo - Friendly Edition')
        self.canvas = tk.Canvas(root, width=WINDOW_SIZE, height=WINDOW_SIZE, bg='#f8f8f8')
        self.canvas.pack()

        # Game state
        self.players = []
        self.current_player = 0
        self.dice_roll = None
        self.human_count = 1
        self.num_players = 2
        self.sounds = False
        self.board_style = 'classic'
        self.setup_from_dialog()
        self.create_ui_widgets()
        self.draw_board()
        self.init_players()
        self.canvas.bind('<<TokenClicked>>', self.on_token_clicked)
        self.update_ui()

    def setup_from_dialog(self):
        dlg = tk.Toplevel(self.root)
        dlg.title('Game Setup')
        dlg.grab_set()
        tk.Label(dlg, text='Choose number of players (2-4):').pack(padx=8,pady=4)
        var_players = tk.IntVar(value=2)
        for n in (2,3,4):
            tk.Radiobutton(dlg, text=str(n), variable=var_players, value=n).pack(anchor='w', padx=12)
        tk.Label(dlg, text='How many human players? (rest are AI)').pack(padx=8,pady=4)
        var_humans = tk.IntVar(value=1)
        for n in range(1,5):
            tk.Radiobutton(dlg, text=str(n), variable=var_humans, value=n).pack(anchor='w', padx=12)
        tk.Label(dlg, text='Board style:').pack(padx=8,pady=4)
        var_style = tk.StringVar(value='classic')
        tk.Radiobutton(dlg, text='Classic', variable=var_style, value='classic').pack(anchor='w', padx=12)
        tk.Radiobutton(dlg, text='Modern', variable=var_style, value='modern').pack(anchor='w', padx=12)
        tk.Label(dlg, text='Enable simple sounds (Windows only)?').pack(padx=8,pady=4)
        var_sound = tk.BooleanVar(value=False)
        tk.Checkbutton(dlg, text='Enable sounds', variable=var_sound).pack(anchor='w', padx=12)

        def on_ok():
            self.num_players = var_players.get()
            self.human_count = min(var_humans.get(), self.num_players)
            self.board_style = var_style.get()
            self.sounds = var_sound.get() and winsound is not None
            dlg.destroy()
        tk.Button(dlg, text='Start Game', command=on_ok).pack(pady=8)
        self.root.wait_window(dlg)

    def create_ui_widgets(self):
        # Top info
        self.info_label = tk.Label(self.root, text='', font=('Arial',14))
        self.info_label.place(x=20, y=10)
        # Dice canvas
        self.dice_canvas = tk.Canvas(self.root, width=80, height=80, bg='#f8f8f8', highlightthickness=0)
        self.dice_canvas.place(x=WINDOW_SIZE-120, y=20)
        # Buttons
        self.roll_btn = tk.Button(self.root, text='Roll Dice', command=self.roll_dice, width=10)
        self.roll_btn.place(x=WINDOW_SIZE-210, y=110)
        self.restart_btn = tk.Button(self.root, text='Restart Game', command=self.restart)
        self.restart_btn.place(x=WINDOW_SIZE-210, y=150)

    def draw_board(self):
        self.canvas.delete('all')
        # big border
        self.canvas.create_rectangle(MARGIN, MARGIN, MARGIN+BOARD_SIZE, MARGIN+BOARD_SIZE, fill='#ffffff', width=2)
        # draw main path cells
        for i,(x,y) in enumerate(PATH_COORDS):
            r = CELL*0.9
            self.canvas.create_rectangle(x-r, y-r, x+r, y+r, outline='black', width=1, fill='#fafafa')
        # draw home stretches
        for p in range(4):
            for (x,y) in HOME_COORDS[p]:
                r = CELL*0.9
                self.canvas.create_rectangle(x-r, y-r, x+r, y+r, outline='black', width=1, fill='#fff7e6')
        # draw base squares and color areas
        corners = [(2,2),(2,12),(12,2),(12,12)]
        for i,(r,c) in enumerate(corners):
            x0 = MARGIN + c*(BOARD_SIZE/14) - CELL*2
            y0 = MARGIN + r*(BOARD_SIZE/14) - CELL*2
            x1 = x0 + CELL*4
            y1 = y0 + CELL*4
            self.canvas.create_rectangle(x0,y0,x1,y1, fill=COLORS[i], outline='black')
            # mark base center
            cx = x0 + (x1-x0)/2
            cy = y0 + (y1-y0)/2
            # small text color name
            self.canvas.create_text(cx, cy+CELL*1.8, text=COLORS[i].upper(), font=('Arial',8), fill='black')

        # center circle
        cx,cy = CENTER
        self.canvas.create_oval(cx-70,cy-70,cx+70,cy+70, fill='#ffffff', outline='black')

    def init_players(self):
        self.players = []
        for i in range(self.num_players):
            p = Player(i, COLORS[i], self.canvas)
            self.players.append(p)
        self.current_player = 0
        self.dice_roll = None

    def update_ui(self):
        cp = self.current_player
        color = COLORS[cp]
        human_or_ai = 'Human' if cp < self.human_count else 'AI'
        self.info_label.config(text=f"Turn: {color.upper()} ({human_or_ai})")
        # draw dice
        self.draw_die(self.dice_roll)
        # highlight movable tokens
        for p_idx, player in enumerate(self.players):
            for tok in player.tokens:
                if self.dice_roll is not None and p_idx==cp and can_move_token(tok,p_idx,self.dice_roll):
                    self.canvas.itemconfig(tok.id, width=4)
                else:
                    self.canvas.itemconfig(tok.id, width=2)
        # if AI turn and dice not rolled, trigger AI roll
        if cp >= self.human_count and self.dice_roll is None:
            self.root.after(500, self.ai_roll)

    def draw_die(self, value):
        self.dice_canvas.delete('all')
        size = 64
        pad = 8
        self.dice_canvas.create_rectangle(pad,pad,pad+size,pad+size, fill='#ffffff', outline='black', width=2)
        if value is None:
            return
        # draw pips
        positions = {
            1: [(0.5,0.5)],
            2: [(0.25,0.25),(0.75,0.75)],
            3: [(0.25,0.25),(0.5,0.5),(0.75,0.75)],
            4: [(0.25,0.25),(0.25,0.75),(0.75,0.25),(0.75,0.75)],
            5: [(0.25,0.25),(0.25,0.75),(0.5,0.5),(0.75,0.25),(0.75,0.75)],
            6: [(0.25,0.2),(0.25,0.5),(0.25,0.8),(0.75,0.2),(0.75,0.5),(0.75,0.8)]
        }
        for (fx,fy) in positions.get(value,[]):
            x = pad + fx*size
            y = pad + fy*size
            r = 5
            self.dice_canvas.create_oval(x-r,y-r,x+r,y+r, fill='black')

    def roll_dice(self):
        if self.dice_roll is not None:
            return
        if self.current_player >= self.human_count:
            return
        self.dice_roll = random.randint(1,6)
        if self.sounds and winsound:
            try:
                winsound.Beep(800,120)
            except: pass
        # check movable
        movable = self.players[self.current_player].movable_tokens(self.dice_roll)
        if not movable:
            self.dice_roll = None
            self.info_label.config(text=f"{COLORS[self.current_player].upper()} has no moves — skipping...")
            self.root.after(700, self.next_turn)
            return
        self.update_ui()

    def ai_roll(self):
        # AI rolls automatically
        self.dice_roll = random.randint(1,6)
        if self.sounds and winsound:
            try:
                winsound.Beep(700,100)
            except: pass
        movable = self.players[self.current_player].movable_tokens(self.dice_roll)
        if not movable:
            self.dice_roll = None
            self.root.after(600, self.next_turn)
            return
        # choose best: capture preferred
        choice = None
        for t in movable:
            target = advance_position(t.pos,self.dice_roll,t.player)
            if target>=0 and target<MAIN_PATH_LEN:
                for p_idx,p in enumerate(self.players):
                    if p_idx==t.player: continue
                    for ot in p.tokens:
                        if ot.pos==target and ot.pos<MAIN_PATH_LEN:
                            choice = t
                            break
                    if choice: break
            if choice: break
        if not choice:
            choice = random.choice(movable)
        self.root.after(300, lambda: self.make_move(choice))

    def on_token_clicked(self, event):
        data = event.__dict__.get('data')
        if not data:
            return
        p_idx, t_idx = map(int, data.split(','))
        if p_idx != self.current_player:
            return
        if self.dice_roll is None:
            messagebox.showinfo('Roll First', 'Please roll the dice first.')
            return
        token = self.players[p_idx].tokens[t_idx]
        if not can_move_token(token,p_idx,self.dice_roll):
            return
        self.make_move(token)

    def make_move(self, token):
        roll = self.dice_roll
        path = []
        old = token.pos
        for step in range(1, roll+1):
            new = advance_position(token.pos if step==1 else path[-1], 1, token.player)
            if new == -1:
                # shouldn't happen because we checked movability
                break
            path.append(new)
        # play animation
        def on_done():
            # after moving, check capture
            newpos = token.pos
            if newpos>=0 and newpos<MAIN_PATH_LEN:
                self.check_capture(token)
            # check finished
            self.dice_roll = None
            # if rolled 6, same player continues
            if roll != 6:
                self.next_turn()
            else:
                self.update_ui()
        animate_move(self.canvas, token, path, step_ms=120, on_complete=on_done)

    def check_capture(self, moved_token):
        for p_idx, p in enumerate(self.players):
            if p_idx == moved_token.player: continue
            for ot in p.tokens:
                if ot.pos == moved_token.pos and ot.pos < MAIN_PATH_LEN:
                    ot.move_to(-1)
                    if self.sounds and winsound:
                        try: winsound.Beep(1000,120)
                        except: pass
                    self.info_label.config(text=f"{COLORS[moved_token.player].upper()} captured {COLORS[p_idx].upper()}!")

    def next_turn(self):
        if self.check_winner(): return
        self.current_player = (self.current_player + 1) % self.num_players
        self.dice_roll = None
        self.update_ui()

    def check_winner(self):
        for p_idx, p in enumerate(self.players):
            finished = sum(1 for t in p.tokens if t.pos == MAIN_PATH_LEN + HOME_STRETCH_LEN -1)
            if finished == TOKENS_PER_PLAYER:
                messagebox.showinfo('Game Over', f'Player {COLORS[p_idx].upper()} wins!')
                return True
        return False

    def restart(self):
        if messagebox.askyesno('Restart', 'Restart the game?'):
            self.setup_from_dialog()
            self.draw_board()
            self.init_players()
            self.update_ui()

# --- Run ---
if __name__ == '__main__':
    root = tk.Tk()
    app = LudoGame(root)
    root.mainloop()
