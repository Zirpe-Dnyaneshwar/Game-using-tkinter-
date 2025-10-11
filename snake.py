"""
Snake — polished Tkinter single-file game.
Features:
- Arrow key controls and WASD
- Pause/Resume (Space)
- Food, growing snake, score and high-score persisted to `snake_highscore.txt`
- Multiple levels with increasing speed and optional obstacles
- Smooth grid-based movement, responsive input buffering
- Restart and Quit buttons, and overlay messages

Save as snake_game.py and run with: python snake_game.py
"""

import tkinter as tk
from tkinter import messagebox
import random
import os

# --- Configuration ---
GRID_SIZE = 20  # pixels per cell
ROWS = 24
COLS = 30
WINDOW_WIDTH = COLS * GRID_SIZE
WINDOW_HEIGHT = ROWS * GRID_SIZE
INITIAL_SPEED = 120  # ms per move
SPEED_INCREMENT = 8   # ms decrease per level (faster)
LEVEL_UP_SCORE = 5    # score needed to level up
HIGH_SCORE_FILE = 'snake_highscore.txt'

# Colors
BG_COLOR = '#0f1724'
SNAKE_COLOR = '#00ff7f'
HEAD_COLOR = '#00b36b'
FOOD_COLOR = '#ff4757'
OBSTACLE_COLOR = '#8b5cf6'
GRID_COLOR = '#0b1220'
TEXT_COLOR = '#e2e8f0'


class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title('Snake — Tkinter')
        self.canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack()

        # UI
        self.frame = tk.Frame(root, bg=BG_COLOR)
        self.frame.pack(fill='x')
        self.score_label = tk.Label(self.frame, text='Score: 0', fg=TEXT_COLOR, bg=BG_COLOR, font=('Consolas', 12))
        self.score_label.pack(side='left', padx=8)
        self.level_label = tk.Label(self.frame, text='Level: 1', fg=TEXT_COLOR, bg=BG_COLOR, font=('Consolas', 12))
        self.level_label.pack(side='left', padx=8)
        self.high_label = tk.Label(self.frame, text='High: 0', fg=TEXT_COLOR, bg=BG_COLOR, font=('Consolas', 12))
        self.high_label.pack(side='left', padx=8)
        self.pause_btn = tk.Button(self.frame, text='Pause', command=self.toggle_pause)
        self.pause_btn.pack(side='right', padx=8)
        self.restart_btn = tk.Button(self.frame, text='Restart', command=self.restart_game)
        self.restart_btn.pack(side='right')

        # Ensure highscore is loaded before UI uses it
        self.highscore = 0
        self.load_highscore()

        # Game state
        self.reset_state()
        self.draw_grid_lines()
        self.bind_events()
        self.running = True
        # Start loop using current speed
        self.root.after(self.speed, self.game_loop)

    def reset_state(self):
        self.speed = INITIAL_SPEED
        self.score = 0
        self.level = 1
        self.direction = (1, 0)  # moving right initially
        start_x = COLS // 3
        start_y = ROWS // 2
        self.snake = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
        self.next_direction = self.direction
        self.food = None
        self.obstacles = set()
        self.place_food()
        self.game_over = False
        self.paused = False
        self.input_buffer = []
        # don't call update_ui until highscore is known (it is loaded in __init__)
        self.canvas.delete('snake')
        self.canvas.delete('food')
        self.canvas.delete('obstacle')
        self.update_ui()

    def bind_events(self):
        # single key handler for arrows and letters
        self.root.bind('<Key>', self.on_key)
        # also allow explicit lower-case binds (some environments)
        self.root.bind('w', lambda e: self.enqueue_direction((0, -1)))
        self.root.bind('s', lambda e: self.enqueue_direction((0, 1)))
        self.root.bind('a', lambda e: self.enqueue_direction((-1, 0)))
        self.root.bind('d', lambda e: self.enqueue_direction((1, 0)))

    def on_key(self, event):
        key = event.keysym
        if key in ('Up', 'w', 'W'):
            self.enqueue_direction((0, -1))
        elif key in ('Down', 's', 'S'):
            self.enqueue_direction((0, 1))
        elif key in ('Left', 'a', 'A'):
            self.enqueue_direction((-1, 0))
        elif key in ('Right', 'd', 'D'):
            self.enqueue_direction((1, 0))
        elif key == 'space':
            self.toggle_pause()
        elif key in ('r', 'R'):
            self.restart_game()

    def enqueue_direction(self, dir):
        # Prevent reversing directly
        if (dir[0] == -self.direction[0] and dir[1] == -self.direction[1]) or dir == self.direction:
            return
        # keep buffer small
        if len(self.input_buffer) < 3:
            self.input_buffer.append(dir)

    def draw_grid_lines(self):
        # subtle grid
        for c in range(COLS + 1):
            x = c * GRID_SIZE
            self.canvas.create_line(x, 0, x, WINDOW_HEIGHT, fill=GRID_COLOR)
        for r in range(ROWS + 1):
            y = r * GRID_SIZE
            self.canvas.create_line(0, y, WINDOW_WIDTH, y, fill=GRID_COLOR)

    def place_food(self):
        attempts = 0
        while True:
            attempts += 1
            x = random.randint(0, COLS - 1)
            y = random.randint(0, ROWS - 1)
            if (x, y) not in self.snake and (x, y) not in self.obstacles:
                self.food = (x, y)
                break
            if attempts > 1000:
                # fallback to avoid infinite loop
                self.food = None
                break

    def place_obstacles_for_level(self):
        # Add some obstacles as levels increase
        self.obstacles.clear()
        obs_count = max(0, self.level - 1) * 3
        for _ in range(obs_count):
            attempts = 0
            while True:
                attempts += 1
                x = random.randint(2, COLS - 3)
                y = random.randint(2, ROWS - 3)
                if (x, y) not in self.snake and (x, y) != self.food:
                    self.obstacles.add((x, y))
                    break
                if attempts > 500:
                    break

    def draw_snake(self):
        self.canvas.delete('snake')
        for i, (x, y) in enumerate(self.snake):
            px = x * GRID_SIZE
            py = y * GRID_SIZE
            r = GRID_SIZE * 0.9
            if i == 0:
                self.canvas.create_rectangle(px + 2, py + 2, px + r - 2, py + r - 2, fill=HEAD_COLOR, outline='', tags='snake')
            else:
                self.canvas.create_rectangle(px + 4, py + 4, px + r - 4, py + r - 4, fill=SNAKE_COLOR, outline='', tags='snake')

    def draw_food(self):
        self.canvas.delete('food')
        if not self.food:
            return
        x, y = self.food
        px = x * GRID_SIZE
        py = y * GRID_SIZE
        r = GRID_SIZE * 0.7
        self.canvas.create_oval(px + (GRID_SIZE - r) / 2, py + (GRID_SIZE - r) / 2,
                                px + (GRID_SIZE + r) / 2, py + (GRID_SIZE + r) / 2,
                                fill=FOOD_COLOR, outline='', tags='food')

    def draw_obstacles(self):
        self.canvas.delete('obstacle')
        for (x, y) in self.obstacles:
            px = x * GRID_SIZE
            py = y * GRID_SIZE
            r = GRID_SIZE * 0.9
            self.canvas.create_rectangle(px + 2, py + 2, px + r - 2, py + r - 2, fill=OBSTACLE_COLOR, outline='', tags='obstacle')

    def update_ui(self):
        # ensure attributes exist
        if not hasattr(self, 'score'):
            self.score = 0
        if not hasattr(self, 'level'):
            self.level = 1
        if not hasattr(self, 'highscore'):
            self.highscore = 0
        self.score_label.config(text=f'Score: {self.score}')
        self.level_label.config(text=f'Level: {self.level}')
        self.high_label.config(text=f'High: {self.highscore}')

    def load_highscore(self):
        try:
            if os.path.exists(HIGH_SCORE_FILE):
                with open(HIGH_SCORE_FILE, 'r') as f:
                    content = f.read().strip()
                    self.highscore = int(content) if content.isdigit() else 0
            else:
                self.highscore = 0
        except:
            self.highscore = 0

    def save_highscore(self):
        try:
            with open(HIGH_SCORE_FILE, 'w') as f:
                f.write(str(self.highscore))
        except:
            pass

    def game_loop(self):
        if not getattr(self, 'running', True):
            return
        if getattr(self, 'paused', False) or getattr(self, 'game_over', False):
            self.root.after(100, self.game_loop)
            return

        # handle input buffer
        if self.input_buffer:
            nd = self.input_buffer.pop(0)
            # prevent reverse
            if not (nd[0] == -self.direction[0] and nd[1] == -self.direction[1]):
                self.direction = nd

        # compute next head
        hx, hy = self.snake[0]
        nx = (hx + self.direction[0])
        ny = (hy + self.direction[1])
        # wrap-around behavior
        nx = nx % COLS
        ny = ny % ROWS
        next_head = (nx, ny)

        # collision checks
        if next_head in self.snake:
            self.end_game('You collided with yourself!')
            return
        if next_head in self.obstacles:
            self.end_game('You hit an obstacle!')
            return

        # move snake
        self.snake.insert(0, next_head)
        if next_head == self.food:
            self.score += 1
            # level up check
            if self.score % LEVEL_UP_SCORE == 0:
                self.level += 1
                self.speed = max(30, self.speed - SPEED_INCREMENT)
                self.place_obstacles_for_level()
            self.place_food()
        else:
            self.snake.pop()

        # redraw
        self.draw_snake()
        self.draw_food()
        self.draw_obstacles()
        self.update_ui()
        self.root.after(self.speed, self.game_loop)

    def end_game(self, reason):
        self.game_over = True
        msg = f'Game Over! {reason}\nYour score: {self.score}'
        if self.score > self.highscore:
            self.highscore = self.score
            self.save_highscore()
            msg += '\nNew High Score!'
        messagebox.showinfo('Game Over', msg)

    def toggle_pause(self):
        if getattr(self, 'game_over', False):
            return
        self.paused = not self.paused
        self.pause_btn.config(text='Resume' if self.paused else 'Pause')

    def restart_game(self):
        if messagebox.askyesno('Restart', 'Restart the game?'):
            self.reset_state()
            self.load_highscore()
            self.update_ui()


# --- Run ---
if __name__ == '__main__':
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()
