"""
Jump Game - Tkinter Version
Author: ChatGPT
Features:
- Player jumps over moving obstacles
- Score system
- Game over and restart
- Smooth animations with gravity and jump physics
"""

import tkinter as tk
import random

# Window setup
WIDTH = 800
HEIGHT = 400
root = tk.Tk()
root.title("Jump Game - Tkinter")
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="skyblue")
canvas.pack()

# Ground and game objects
ground = canvas.create_rectangle(0, HEIGHT - 50, WIDTH, HEIGHT, fill="green")
player = canvas.create_rectangle(80, HEIGHT - 100, 120, HEIGHT - 50, fill="red")

# Variables
jumping = False
velocity = 0
gravity = 1
obstacles = []
score = 0
game_running = True

# Text
score_text = canvas.create_text(70, 30, text="Score: 0", fill="white", font=("Arial", 16))
game_over_text = None

# Functions
def jump(event=None):
    global jumping, velocity
    if not game_running:
        return
    if not jumping:
        jumping = True
        velocity = -17  # Jump power

def create_obstacle():
    if not game_running:
        return
    height = random.randint(40, 80)
    obstacle = canvas.create_rectangle(WIDTH, HEIGHT - 50 - height, WIDTH + 40, HEIGHT - 50, fill="black")
    obstacles.append(obstacle)
    root.after(random.randint(1500, 2500), create_obstacle)

def move_obstacles():
    global score, game_running
    for obstacle in obstacles[:]:
        canvas.move(obstacle, -10, 0)
        x1, y1, x2, y2 = canvas.coords(obstacle)
        if x2 < 0:
            canvas.delete(obstacle)
            obstacles.remove(obstacle)
            score += 1
            canvas.itemconfig(score_text, text=f"Score: {score}")
        else:
            # Collision detection
            px1, py1, px2, py2 = canvas.coords(player)
            if px2 > x1 and px1 < x2 and py2 > y1:
                game_over()
    if game_running:
        root.after(50, move_obstacles)

def update_player():
    global jumping, velocity
    if jumping:
        canvas.move(player, 0, velocity)
        velocity += gravity
        x1, y1, x2, y2 = canvas.coords(player)
        if y2 >= HEIGHT - 50:
            jumping = False
            canvas.coords(player, 80, HEIGHT - 100, 120, HEIGHT - 50)
    if game_running:
        root.after(30, update_player)

def game_over():
    global game_running, game_over_text
    game_running = False
    canvas.create_text(WIDTH // 2, HEIGHT // 2 - 20, fill="white", font=("Arial", 30, "bold"), text="GAME OVER")
    game_over_text = canvas.create_text(WIDTH // 2, HEIGHT // 2 + 20, fill="yellow", font=("Arial", 16), text="Press 'R' to Restart")

def restart(event=None):
    global game_running, score, obstacles, jumping, velocity
    game_running = True
    score = 0
    jumping = False
    velocity = 0
    for obs in obstacles:
        canvas.delete(obs)
    obstacles.clear()
    canvas.itemconfig(score_text, text=f"Score: {score}")
    canvas.coords(player, 80, HEIGHT - 100, 120, HEIGHT - 50)
    canvas.delete("all")
    # Recreate base UI
    recreate_ui()
    create_obstacle()
    update_player()
    move_obstacles()

def recreate_ui():
    global ground, player, score_text
    ground = canvas.create_rectangle(0, HEIGHT - 50, WIDTH, HEIGHT, fill="green")
    player = canvas.create_rectangle(80, HEIGHT - 100, 120, HEIGHT - 50, fill="red")
    score_text = canvas.create_text(70, 30, text="Score: 0", fill="white", font=("Arial", 16))

# Key bindings
root.bind("<space>", jump)
root.bind("r", restart)

# Start game
create_obstacle()
update_player()
move_obstacles()

root.mainloop()
