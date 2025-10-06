import tkinter as tk
import random
import time

# -------------------------------
# Game Configuration
# -------------------------------
GAME_WIDTH = 600
GAME_HEIGHT = 400
APPLE_SIZE = 40
SWORD_LENGTH = 80
BACKGROUND_COLOR = "#1b1b1b"
APPLE_COLOR = "#ff3b3b"
SWORD_COLOR = "#00ffcc"
SPEED = 30  # smaller = faster animation

score = 0
running = True
apples = []

# -------------------------------
# Window Setup
# -------------------------------
window = tk.Tk()
window.title("🍎 Apple Cutting Game")
window.resizable(False, False)

score_label = tk.Label(window, text=f"Score: {score}", font=("Arial", 16), bg="#222", fg="white")
score_label.pack(fill="x")

canvas = tk.Canvas(window, bg=BACKGROUND_COLOR, width=GAME_WIDTH, height=GAME_HEIGHT)
canvas.pack()

window.update()

# -------------------------------
# Sword (controlled by mouse)
# -------------------------------
sword = canvas.create_line(0, 0, 0, 0, fill=SWORD_COLOR, width=4)

def move_sword(event):
    x, y = event.x, event.y
    canvas.coords(sword, x - SWORD_LENGTH//2, y, x + SWORD_LENGTH//2, y)

canvas.bind("<Motion>", move_sword)

# -------------------------------
# Apple Class
# -------------------------------
class Apple:
    def __init__(self):
        self.x = random.randint(20, GAME_WIDTH - 20)
        self.y = -APPLE_SIZE
        self.apple = canvas.create_oval(
            self.x, self.y, self.x + APPLE_SIZE, self.y + APPLE_SIZE, fill=APPLE_COLOR
        )
        self.speed = random.randint(3, 7)

    def move(self):
        canvas.move(self.apple, 0, self.speed)
        self.y += self.speed
        if self.y > GAME_HEIGHT:
            canvas.delete(self.apple)
            return False
        return True

# -------------------------------
# Game Logic
# -------------------------------
def spawn_apple():
    if running:
        apple = Apple()
        apples.append(apple)
        window.after(1000, spawn_apple)  # spawn every 1 sec

def check_collision():
    global score
    sword_coords = canvas.coords(sword)
    if not sword_coords:
        return
    x1, y1, x2, y2 = sword_coords
    for apple in apples[:]:
        apple_coords = canvas.coords(apple.apple)
        ax1, ay1, ax2, ay2 = apple_coords
        # Simple overlap check
        if x1 < ax2 and x2 > ax1 and y1 < ay2 and y2 > ay1:
            canvas.delete(apple.apple)
            apples.remove(apple)
            score += 1
            score_label.config(text=f"Score: {score}")

def update_game():
    global running
    if not running:
        return
    for apple in apples[:]:
        if not apple.move():
            apples.remove(apple)
    check_collision()
    window.after(SPEED, update_game)

# -------------------------------
# Game Over Handling
# -------------------------------
def game_over():
    global running
    running = False
    canvas.delete("all")
    canvas.create_text(
        GAME_WIDTH/2, GAME_HEIGHT/2,
        text=f"Game Over!\nFinal Score: {score}",
        fill="red",
        font=("Arial", 24, "bold")
    )

def stop_game(event):
    game_over()

window.bind("<Escape>", stop_game)

# -------------------------------
# Start Game
# -------------------------------
spawn_apple()
update_game()
window.mainloop()
