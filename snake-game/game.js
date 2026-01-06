// Game constants
const GRID_X_SIZE = 20;
const GRID_Y_SIZE = 30;
const CELL_SIZE = 20;
const INITIAL_SPEED = 150;
const SPEED_INCREMENT = 5;

// Game state
let canvas, ctx;
let snake = [];
let direction = { x: 1, y: 0 };
let nextDirection = { x: 1, y: 0 };
let food = { x: 0, y: 0 };
let score = 0;
let highScore = 0;
let gameLoop = null;
let isPaused = false;
let gameStarted = false;
let speed = INITIAL_SPEED;

// Initialize game
document.addEventListener('DOMContentLoaded', () => {
    canvas = document.getElementById('gameCanvas');
    ctx = canvas.getContext('2d');

    // Load high score from localStorage
    highScore = localStorage.getItem('snakeHighScore') || 0;
    document.getElementById('highScore').textContent = highScore;

    // Event listeners
    document.getElementById('startBtn').addEventListener('click', startGame);
    document.getElementById('pauseBtn').addEventListener('click', togglePause);
    document.getElementById('resetBtn').addEventListener('click', resetGame);
    document.getElementById('playAgainBtn').addEventListener('click', playAgain);
    document.addEventListener('keydown', handleKeyPress);

    // Initialize game without starting
    initGame();
    drawGame();
});

function initGame() {
    // Initialize snake in the middle
    snake = [
        { x: 10, y: 10 },
        { x: 9, y: 10 },
        { x: 8, y: 10 }
    ];
    direction = { x: 1, y: 0 };
    nextDirection = { x: 1, y: 0 };
    score = 0;
    speed = INITIAL_SPEED;
    document.getElementById('score').textContent = score;
    spawnFood();
}

function startGame() {
    if (!gameStarted) {
        gameStarted = true;
        isPaused = false;
        document.getElementById('startBtn').disabled = true;
        document.getElementById('pauseBtn').disabled = false;
        gameLoop = setInterval(update, speed);
    }
}

function togglePause() {
    if (!gameStarted) return;

    isPaused = !isPaused;
    const pauseBtn = document.getElementById('pauseBtn');

    if (isPaused) {
        clearInterval(gameLoop);
        pauseBtn.textContent = 'Resume';
    } else {
        gameLoop = setInterval(update, speed);
        pauseBtn.textContent = 'Pause';
    }
}

function resetGame() {
    clearInterval(gameLoop);
    gameStarted = false;
    isPaused = false;
    document.getElementById('startBtn').disabled = false;
    document.getElementById('pauseBtn').disabled = true;
    document.getElementById('pauseBtn').textContent = 'Pause';
    document.getElementById('gameOver').classList.add('hidden');
    initGame();
    drawGame();
}

function playAgain() {
    resetGame();
    startGame();
}

function handleKeyPress(e) {
    if (!gameStarted) {
        if (e.key === ' ' || e.key === 'Enter') {
            startGame();
        }
        return;
    }

    // Prevent default arrow key behavior (scrolling)
    if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
        e.preventDefault();
    }

    // Handle direction changes (can't reverse)
    switch(e.key) {
        case 'ArrowUp':
        case 'w':
        case 'W':
            if (direction.y === 0) nextDirection = { x: 0, y: -1 };
            break;
        case 'ArrowDown':
        case 's':
        case 'S':
            if (direction.y === 0) nextDirection = { x: 0, y: 1 };
            break;
        case 'ArrowLeft':
        case 'a':
        case 'A':
            if (direction.x === 0) nextDirection = { x: -1, y: 0 };
            break;
        case 'ArrowRight':
        case 'd':
        case 'D':
            if (direction.x === 0) nextDirection = { x: 1, y: 0 };
            break;
        case ' ':
            togglePause();
            break;
    }
}

function update() {
    // Update direction
    direction = { ...nextDirection };

    // Calculate new head position
    const head = { ...snake[0] };
    head.x += direction.x;
    head.y += direction.y;

    // Check collision with walls
    if (head.x < 0 || head.x >= GRID_X_SIZE || head.y < 0 || head.y >= GRID_Y_SIZE) {
        gameOver();
        return;
    }

    // Check collision with self
    if (snake.some(segment => segment.x === head.x && segment.y === head.y)) {
        gameOver();
        return;
    }

    // Add new head
    snake.unshift(head);

    // Check if food is eaten
    if (head.x === food.x && head.y === food.y) {
        score += 10;
        document.getElementById('score').textContent = score;

        // Update high score
        if (score > highScore) {
            highScore = score;
            document.getElementById('highScore').textContent = highScore;
            localStorage.setItem('snakeHighScore', highScore);
        }

        // Spawn new food
        spawnFood();

        // Increase speed slightly
        if (score % 50 === 0 && speed > 50) {
            speed -= SPEED_INCREMENT;
            clearInterval(gameLoop);
            gameLoop = setInterval(update, speed);
        }
    } else {
        // Remove tail if no food eaten
        snake.pop();
    }

    drawGame();
}

function spawnFood() {
    // Generate random position
    do {
        food.x = Math.floor(Math.random() * GRID_X_SIZE);
        food.y = Math.floor(Math.random() * GRID_Y_SIZE);
    } while (snake.some(segment => segment.x === food.x && segment.y === food.y));
}

function drawGame() {
    // Clear canvas
    ctx.fillStyle = '#f8f9fa';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw grid
    ctx.strokeStyle = '#e0e0e0';
    ctx.lineWidth = 1;
    for (let i = 0; i <= GRID_X_SIZE; i++) {
        ctx.beginPath();
        ctx.moveTo(i * CELL_SIZE, 0);
        ctx.lineTo(i * CELL_SIZE, canvas.height);
        ctx.stroke();
    }
    for (let i = 0; i <= GRID_Y_SIZE; i++) {
        ctx.beginPath();
        ctx.moveTo(0, i * CELL_SIZE);
        ctx.lineTo(canvas.width, i * CELL_SIZE);
        ctx.stroke();
    }

    // Draw snake
    snake.forEach((segment, index) => {
        if (index === 0) {
            // Head
            ctx.fillStyle = '#28a745';
            ctx.fillRect(
                segment.x * CELL_SIZE + 1,
                segment.y * CELL_SIZE + 1,
                CELL_SIZE - 2,
                CELL_SIZE - 2
            );

            // Eyes
            ctx.fillStyle = 'white';
            const eyeSize = 4;
            const eyeOffset = 6;
            if (direction.x === 1) { // Right
                ctx.fillRect(segment.x * CELL_SIZE + eyeOffset + 6, segment.y * CELL_SIZE + 4, eyeSize, eyeSize);
                ctx.fillRect(segment.x * CELL_SIZE + eyeOffset + 6, segment.y * CELL_SIZE + 12, eyeSize, eyeSize);
            } else if (direction.x === -1) { // Left
                ctx.fillRect(segment.x * CELL_SIZE + 4, segment.y * CELL_SIZE + 4, eyeSize, eyeSize);
                ctx.fillRect(segment.x * CELL_SIZE + 4, segment.y * CELL_SIZE + 12, eyeSize, eyeSize);
            } else if (direction.y === -1) { // Up
                ctx.fillRect(segment.x * CELL_SIZE + 4, segment.y * CELL_SIZE + 4, eyeSize, eyeSize);
                ctx.fillRect(segment.x * CELL_SIZE + 12, segment.y * CELL_SIZE + 4, eyeSize, eyeSize);
            } else { // Down
                ctx.fillRect(segment.x * CELL_SIZE + 4, segment.y * CELL_SIZE + 12, eyeSize, eyeSize);
                ctx.fillRect(segment.x * CELL_SIZE + 12, segment.y * CELL_SIZE + 12, eyeSize, eyeSize);
            }
        } else {
            // Body
            ctx.fillStyle = '#4caf50';
            ctx.fillRect(
                segment.x * CELL_SIZE + 1,
                segment.y * CELL_SIZE + 1,
                CELL_SIZE - 2,
                CELL_SIZE - 2
            );
        }
    });

    // Draw food
    ctx.fillStyle = '#dc3545';
    ctx.beginPath();
    ctx.arc(
        food.x * CELL_SIZE + CELL_SIZE / 2,
        food.y * CELL_SIZE + CELL_SIZE / 2,
        CELL_SIZE / 2 - 2,
        0,
        2 * Math.PI
    );
    ctx.fill();

    // Draw small highlight on food
    ctx.fillStyle = '#ff6b7a';
    ctx.beginPath();
    ctx.arc(
        food.x * CELL_SIZE + CELL_SIZE / 2 - 3,
        food.y * CELL_SIZE + CELL_SIZE / 2 - 3,
        3,
        0,
        2 * Math.PI
    );
    ctx.fill();
}

function gameOver() {
    clearInterval(gameLoop);
    gameStarted = false;

    // Show game over screen
    document.getElementById('finalScore').textContent = score;
    document.getElementById('gameOver').classList.remove('hidden');

    // Reset buttons
    document.getElementById('startBtn').disabled = false;
    document.getElementById('pauseBtn').disabled = true;
    document.getElementById('pauseBtn').textContent = 'Pause';
}
