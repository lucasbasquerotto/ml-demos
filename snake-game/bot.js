/**
 * Snake Game Bot - AI player using pathfinding algorithms
 */

class SnakeBot {
    constructor(gridXSize, gridYSize) {
        this.gridXSize = gridXSize;
        this.gridYSize = gridYSize;
        this.enabled = false;
        this.path = [];
    }

    enable() {
        this.enabled = true;
        this.path = [];
    }

    disable() {
        this.enabled = false;
        this.path = [];
    }

    toggle() {
        if (this.enabled) {
            this.disable();
        } else {
            this.enable();
        }
        return this.enabled;
    }

    /**
     * Get next direction for the snake to move
     * Uses A* pathfinding to find path to food
     */
    getNextDirection(snake, food, currentDirection) {
        if (!this.enabled) return null;

        const head = snake[0];

        // Debug: log current state
        console.log('Bot - Head:', head, 'Food:', food, 'Direction:', currentDirection);

        // Always try to find a fresh path to food
        this.path = this.findPathToFood(snake, food);

        console.log('Bot - Path found:', this.path);

        // If we can't find a path to food, try to find a safe move
        if (this.path.length === 0) {
            console.log('Bot - No path to food, finding safe direction');
            const safeDir = this.findSafeDirection(snake, currentDirection);
            console.log('Bot - Safe direction:', safeDir);
            return safeDir;
        }

        // Follow the path - get the FIRST position in the path
        const nextPos = this.path[0];
        console.log('Bot - Next position from path:', nextPos);

        const direction = this.getDirectionToPosition(head, nextPos);
        console.log('Bot - Direction to next position:', direction);

        return direction;
    }

    /**
     * A* pathfinding algorithm to find path to food
     */
    findPathToFood(snake, food) {
        const start = snake[0];
        const goal = food;

        console.log('A* - Starting pathfinding from', start, 'to', goal);

        const openSet = [start];
        const cameFrom = new Map();
        const gScore = new Map();
        const fScore = new Map();

        const startKey = this.positionKey(start);
        gScore.set(startKey, 0);
        fScore.set(startKey, this.heuristic(start, goal));

        let iterations = 0;
        const maxIterations = 1000;

        while (openSet.length > 0 && iterations < maxIterations) {
            iterations++;

            // Get node with lowest fScore
            let current = openSet[0];
            let currentIndex = 0;
            const currentFScore = fScore.get(this.positionKey(current));
            let lowestF = currentFScore !== undefined ? currentFScore : Infinity;

            for (let i = 1; i < openSet.length; i++) {
                const posKey = this.positionKey(openSet[i]);
                const fValue = fScore.get(posKey);
                const f = fValue !== undefined ? fValue : Infinity;
                if (f < lowestF) {
                    lowestF = f;
                    current = openSet[i];
                    currentIndex = i;
                }
            }

            // Check if we reached the goal
            if (current.x === goal.x && current.y === goal.y) {
                console.log('A* - Found path after', iterations, 'iterations');
                const path = this.reconstructPath(cameFrom, current);
                console.log('A* - Reconstructed path:', path);
                return path;
            }

            openSet.splice(currentIndex, 1);

            // Check all neighbors
            const neighbors = this.getNeighbors(current);
            console.log('A* - Exploring', neighbors.length, 'neighbors from', current);
            console.log('A* - Current key:', this.positionKey(current), 'gScore:', gScore.get(this.positionKey(current)));

            for (const neighbor of neighbors) {
                const neighborKey = this.positionKey(neighbor);
                console.log('A* - Checking neighbor', neighbor);

                // Skip if position is occupied by snake body (except tail which will move)
                if (this.isOccupiedBySnake(neighbor, snake, true)) {
                    console.log('A* - Neighbor occupied by snake, skipping');
                    continue;
                }

                console.log('A* - Neighbor is free, adding to consideration');

                // DEBUGGING: Store currentKey outside the calculation
                const savedCurrentKey = this.positionKey(current);
                console.log('A* - savedCurrentKey:', savedCurrentKey, 'gScore has it:', gScore.has(savedCurrentKey), 'value:', gScore.get(savedCurrentKey));

                const currentGScoreValue = gScore.get(savedCurrentKey);
                const tentativeGScore = (currentGScoreValue !== undefined ? currentGScoreValue : Infinity) + 1;
                const existingGScore = gScore.get(neighborKey);
                const existingGScoreValue = existingGScore !== undefined ? existingGScore : Infinity;

                console.log('A* - tentativeGScore:', tentativeGScore, 'existingGScore:', existingGScoreValue, 'will update:', tentativeGScore < existingGScoreValue);

                if (tentativeGScore < existingGScoreValue) {
                    cameFrom.set(neighborKey, current);
                    gScore.set(neighborKey, tentativeGScore);
                    fScore.set(neighborKey, tentativeGScore + this.heuristic(neighbor, goal));

                    if (!openSet.some(pos => pos.x === neighbor.x && pos.y === neighbor.y)) {
                        openSet.push(neighbor);
                        console.log('A* - Added to openSet. Size:', openSet.length);
                    } else {
                        console.log('A* - Neighbor already in openSet');
                    }
                }
            }
        }

        console.log('A* - No path found after', iterations, 'iterations. OpenSet final size:', openSet.length);
        return []; // No path found
    }

    /**
     * Check if bot can survive after eating food (won't trap itself)
     */
    canSurviveAfterEating(snake, pathToFood) {
        // Simulate eating food
        const newSnake = [...snake];

        // Follow path to food
        for (const pos of pathToFood) {
            const head = { ...pos };
            newSnake.unshift(head);
            // Don't remove tail since we're eating
        }

        // Check if there's still space to move (can reach tail)
        const head = newSnake[0];
        const tail = newSnake[newSnake.length - 1];

        // Try to find path to tail area
        const openSpace = this.countReachableSpace(head, newSnake);

        // Need at least as much space as snake length
        return openSpace >= newSnake.length;
    }

    /**
     * Count reachable empty spaces from a position
     */
    countReachableSpace(start, snake) {
        const visited = new Set();
        const queue = [start];
        visited.add(this.positionKey(start));
        let count = 0;

        while (queue.length > 0) {
            const current = queue.shift();
            count++;

            const neighbors = this.getNeighbors(current);
            for (const neighbor of neighbors) {
                const key = this.positionKey(neighbor);
                if (!visited.has(key) && !this.isOccupiedBySnake(neighbor, snake, false)) {
                    visited.add(key);
                    queue.push(neighbor);
                }
            }
        }

        return count;
    }

    /**
     * Find a safe direction when no path to food exists
     */
    findSafeDirection(snake, currentDirection) {
        const head = snake[0];
        const possibleDirections = [
            { x: 0, y: -1, name: 'up' },
            { x: 0, y: 1, name: 'down' },
            { x: -1, y: 0, name: 'left' },
            { x: 1, y: 0, name: 'right' }
        ];

        // Filter out reverse direction
        const validDirections = possibleDirections.filter(dir => {
            // Can't reverse
            if (currentDirection.x !== 0 && dir.x === -currentDirection.x) return false;
            if (currentDirection.y !== 0 && dir.y === -currentDirection.y) return false;
            return true;
        });

        // Score each direction
        let bestDirection = null;
        let bestScore = -Infinity;

        for (const dir of validDirections) {
            const newPos = { x: head.x + dir.x, y: head.y + dir.y };

            // Skip if out of bounds or hitting snake
            if (this.isOutOfBounds(newPos) || this.isOccupiedBySnake(newPos, snake, true)) {
                continue;
            }

            // Score based on reachable space
            const space = this.countReachableSpace(newPos, snake);

            if (space > bestScore) {
                bestScore = space;
                bestDirection = dir.name;
            }
        }

        return bestDirection;
    }

    /**
     * Check if a position is out of bounds
     */
    isOutOfBounds(pos) {
        return pos.x < 0 || pos.x >= this.gridXSize || pos.y < 0 || pos.y >= this.gridYSize;
    }

    /**
     * Check if a position is occupied by snake
     */
    isOccupiedBySnake(pos, snake, ignoreTail) {
        const length = ignoreTail ? snake.length - 1 : snake.length;
        for (let i = 0; i < length; i++) {
            if (snake[i].x === pos.x && snake[i].y === pos.y) {
                return true;
            }
        }
        return false;
    }

    /**
     * Get valid neighboring positions
     */
    getNeighbors(pos) {
        const neighbors = [
            { x: pos.x, y: pos.y - 1 }, // up
            { x: pos.x, y: pos.y + 1 }, // down
            { x: pos.x - 1, y: pos.y }, // left
            { x: pos.x + 1, y: pos.y }  // right
        ];

        return neighbors.filter(n => !this.isOutOfBounds(n));
    }

    /**
     * Manhattan distance heuristic
     */
    heuristic(pos1, pos2) {
        return Math.abs(pos1.x - pos2.x) + Math.abs(pos1.y - pos2.y);
    }

    /**
     * Create a unique key for a position
     */
    positionKey(pos) {
        return `${pos.x},${pos.y}`;
    }

    /**
     * Reconstruct path from A* algorithm
     */
    reconstructPath(cameFrom, current) {
        const path = [current];
        let currentKey = this.positionKey(current);

        while (cameFrom.has(currentKey)) {
            current = cameFrom.get(currentKey);
            path.unshift(current);
            currentKey = this.positionKey(current);
        }

        // Remove the starting position (current head position)
        path.shift();
        return path;
    }

    /**
     * Check if the current path is still valid
     */
    isPathValid(snake, path) {
        if (path.length === 0) return false;

        const head = snake[0];
        const nextPos = path[0];

        // Check if next position is adjacent to head
        const dx = Math.abs(nextPos.x - head.x);
        const dy = Math.abs(nextPos.y - head.y);
        if ((dx === 1 && dy === 0) || (dx === 0 && dy === 1)) {
            // Check if next position is not occupied by snake
            return !this.isOccupiedBySnake(nextPos, snake, true);
        }

        return false;
    }

    /**
     * Get direction string from current position to target position
     */
    getDirectionToPosition(from, to) {
        if (to.x > from.x) return 'right';
        if (to.x < from.x) return 'left';
        if (to.y > from.y) return 'down';
        if (to.y < from.y) return 'up';
        return null;
    }
}

// Export for use in main game
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SnakeBot };
}
