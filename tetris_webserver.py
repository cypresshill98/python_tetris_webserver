from flask import Flask, render_template, send_from_directory, request, jsonify
import pygame
import random
import io
from PIL import Image, ImageOps, ImageDraw
import csv
from datetime import datetime

app = Flask(__name__)

# Screen dimensions
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

COLORS = [BLACK, RED, GREEN, BLUE, CYAN, MAGENTA, YELLOW, ORANGE]

# Shapes
SHAPES = [
    [[1, 1, 1],
     [0, 1, 0]],

    [[0, 2, 2],
     [2, 2, 0]],

    [[3, 3, 0],
     [0, 3, 3]],

    [[4, 4],
     [4, 4]],

    [[0, 0, 5],
     [5, 5, 5]],

    [[6, 0, 0],
     [6, 6, 6]],

    [[0, 7, 0],
     [7, 7, 7]]
]

# Initialize pygame
pygame.init()
screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

# Create grid
def create_grid():
    return [[0 for _ in range(SCREEN_WIDTH // BLOCK_SIZE)] for _ in range(SCREEN_HEIGHT // BLOCK_SIZE)]

# Draw grid
def draw_grid(grid):
    for y, row in enumerate(grid):
        for x, value in enumerate(row):
            if value != 0:
                pygame.draw.rect(screen, COLORS[value], (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.line(screen, WHITE, (x * BLOCK_SIZE, 0), (x * BLOCK_SIZE, SCREEN_HEIGHT))
        pygame.draw.line(screen, WHITE, (0, y * BLOCK_SIZE), (SCREEN_WIDTH, y * BLOCK_SIZE))

# Add a global variable to track the pause state
is_paused = False

# Add a global variable to track the game over state
game_over = False

def render_game():
    global is_paused, game_over

    if is_paused:
        # Display a paused screen
        paused_image = Image.new('RGBA', (SCREEN_WIDTH, SCREEN_HEIGHT), (0, 0, 0, 255))
        draw = ImageDraw.Draw(paused_image)
        draw.rectangle([(0, 0), (SCREEN_WIDTH, SCREEN_HEIGHT)], fill=(0, 0, 0, 128))
        draw.text((SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 10), "Game Paused", fill="white")
        return paused_image

    if game_over:
        # Display a game over screen
        game_over_image = Image.new('RGBA', (SCREEN_WIDTH, SCREEN_HEIGHT), (0, 0, 0, 255))
        draw = ImageDraw.Draw(game_over_image)
        draw.text((SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 10), "Game Over", fill="white")
        return game_over_image

    grid = create_grid()
    current_shape = random.choice(SHAPES)
    shape_pos = [0, SCREEN_WIDTH // BLOCK_SIZE // 2 - len(current_shape[0]) // 2]

    # Draw the current shape
    for y, row in enumerate(current_shape):
        for x, value in enumerate(row):
            if value != 0:
                grid[y + shape_pos[0]][x + shape_pos[1]] = value

    # Draw the grid
    draw_grid(grid)

    # Convert the pygame surface to an image
    image = pygame.surfarray.array3d(screen)
    image = Image.fromarray(image.transpose((1, 0, 2))).convert('RGBA')

    return image

# Serve static files
@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('images', filename)

# Serve audio files
@app.route('/audio/<path:filename>')
def serve_audio(filename):
    return send_from_directory('audio', filename)

@app.route('/')
def index():
    return render_template('tetris.html')

# Update the handle_input function to properly handle the ESC key event
@app.route('/handle_input', methods=['POST'])
def handle_input():
    global is_paused
    data = request.get_json()
    if data and 'key' in data:
        if data['key'] == 'ESC':
            is_paused = not is_paused
    return '', 204

@app.route('/save_score', methods=['POST'])
def save_score():
    data = request.get_json()
    if data and 'name' in data and 'score' in data and 'time' in data:
        with open('scores.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([data['name'], data['score'], data['time'], datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    return '', 204

# Add a route to set the game over state
@app.route('/set_game_over', methods=['POST'])
def set_game_over():
    global game_over
    game_over = True

    # Refresh the score table after game over
    get_scores_json()

    return '', 204

@app.route('/scores')
def show_scores():
    scores = []
    try:
        with open('scores.csv', 'r') as csvfile:
            reader = csv.reader(csvfile)
            scores = sorted(list(reader), key=lambda x: int(x[1]), reverse=True)
    except FileNotFoundError:
        scores = []

    return render_template('scores.html', scores=scores)

@app.route('/scores.json')
def get_scores_json():
    scores = []
    try:
        with open('scores.csv', 'r') as csvfile:
            reader = csv.reader(csvfile)
            scores = sorted(list(reader), key=lambda x: int(x[1]), reverse=True)
    except FileNotFoundError:
        scores = []

    return jsonify(scores)

if __name__ == '__main__':
    app.run(debug=True)