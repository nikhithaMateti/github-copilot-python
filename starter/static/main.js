// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const SCOREBOARD_STORAGE_KEY = 'sudokuTopScores';
const MAX_SCOREBOARD_ENTRIES = 10;

let puzzle = [];
let timerIntervalId = null;
let timerStartTime = null;
let hintsUsed = 0;
let isGameSolved = false;
let currentDifficulty = 'medium';

function getBoardElement() {
  return document.getElementById('sudoku-board');
}

function getSelectedDifficulty() {
  const difficultySelect = document.getElementById('difficulty');
  return difficultySelect ? difficultySelect.value : 'medium';
}

function getPlayerName() {
  const playerNameInput = document.getElementById('player-name');
  if (!playerNameInput) {
    return 'Player';
  }

  const trimmedName = playerNameInput.value.trim();
  return trimmedName || 'Player';
}

function toFlatCellIndex(row, col) {
  return row * SIZE + col;
}

function getSubgridClass(row, col) {
  const subgridRow = Math.floor(row / 3);
  const subgridCol = Math.floor(col / 3);
  const isEvenSubgrid = (subgridRow + subgridCol) % 2 === 0;
  return isEvenSubgrid ? 'subgrid-a' : 'subgrid-b';
}

function buildCellBaseClass(row, col) {
  return `sudoku-cell ${getSubgridClass(row, col)}`;
}

function lockCell(inputs, row, col, value) {
  const flatIndex = toFlatCellIndex(row, col);
  const inputCell = inputs[flatIndex];
  inputCell.value = value;
  inputCell.disabled = true;
  inputCell.className = `${buildCellBaseClass(row, col)} prefilled`;
}

function sanitizeCellInput(event) {
  const sanitizedValue = event.target.value.replace(/[^1-9]/g, '');
  event.target.value = sanitizedValue;
}

function setMessage(text, color) {
  const messageElement = document.getElementById('message');
  messageElement.style.color = color;
  messageElement.innerText = text;
}

function getTimerElement() {
  return document.getElementById('timer');
}

function formatElapsedMilliseconds(elapsedMilliseconds) {
  const totalSeconds = Math.floor(elapsedMilliseconds / 1000);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

function renderTimer(elapsedMilliseconds) {
  const timerElement = getTimerElement();
  if (!timerElement) {
    return;
  }

  timerElement.innerText = formatElapsedMilliseconds(elapsedMilliseconds);
}

function elapsedTimeMilliseconds() {
  if (!timerStartTime) {
    return 0;
  }

  return Math.max(0, Date.now() - timerStartTime);
}

function stopTimer() {
  if (timerIntervalId) {
    clearInterval(timerIntervalId);
    timerIntervalId = null;
  }
}

function startTimer() {
  stopTimer();
  timerStartTime = Date.now();
  renderTimer(0);

  timerIntervalId = setInterval(() => {
    renderTimer(elapsedTimeMilliseconds());
  }, 250);
}

function normalizeScore(score) {
  if (!score || typeof score !== 'object') {
    return null;
  }

  const elapsedMilliseconds = Number(score.elapsedMilliseconds);
  if (!Number.isFinite(elapsedMilliseconds) || elapsedMilliseconds < 0) {
    return null;
  }

  return {
    playerName: typeof score.playerName === 'string' && score.playerName.trim() ? score.playerName.trim() : 'Player',
    elapsedMilliseconds,
    difficulty: typeof score.difficulty === 'string' && score.difficulty ? score.difficulty : 'medium',
    hintsUsed: Number.isInteger(score.hintsUsed) && score.hintsUsed >= 0 ? score.hintsUsed : 0
  };
}

function loadScores() {
  try {
    const raw = localStorage.getItem(SCOREBOARD_STORAGE_KEY);
    if (!raw) {
      return [];
    }

    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) {
      return [];
    }

    return parsed.map(normalizeScore).filter(Boolean);
  } catch {
    return [];
  }
}

function saveScores(scores) {
  const normalizedScores = scores.map(normalizeScore).filter(Boolean);
  const fastestScores = sortAndTrimScores(normalizedScores);
  localStorage.setItem(SCOREBOARD_STORAGE_KEY, JSON.stringify(fastestScores));
}

function sortAndTrimScores(scores) {
  const sorted = [...scores].sort((left, right) => left.elapsedMilliseconds - right.elapsedMilliseconds);
  return sorted.slice(0, MAX_SCOREBOARD_ENTRIES);
}

function formatDifficulty(difficulty) {
  if (!difficulty) {
    return 'Medium';
  }

  return difficulty.charAt(0).toUpperCase() + difficulty.slice(1).toLowerCase();
}

function renderScoreboard() {
  const scoreboardList = document.getElementById('scoreboard-list');
  if (!scoreboardList) {
    return;
  }

  scoreboardList.innerHTML = '';
  const scores = sortAndTrimScores(loadScores());

  if (scores.length === 0) {
    const emptyItem = document.createElement('li');
    emptyItem.innerText = 'No scores yet.';
    scoreboardList.appendChild(emptyItem);
    return;
  }

  for (const score of scores) {
    const scoreItem = document.createElement('li');
    const formattedTime = formatElapsedMilliseconds(score.elapsedMilliseconds);
    const formattedDifficulty = formatDifficulty(score.difficulty);
    scoreItem.innerText = `${score.playerName} - ${formattedTime} (${formattedDifficulty}, hints: ${score.hintsUsed})`;
    scoreboardList.appendChild(scoreItem);
  }
}

function saveCompletedGameScore() {
  const newScore = {
    playerName: getPlayerName(),
    elapsedMilliseconds: elapsedTimeMilliseconds(),
    difficulty: currentDifficulty,
    hintsUsed
  };

  const scores = loadScores();
  scores.push(newScore);
  saveScores(sortAndTrimScores(scores));
  renderScoreboard();
}

function createBoardElement() {
  const boardElement = getBoardElement();
  boardElement.innerHTML = '';

  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';

    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = buildCellBaseClass(i, j);
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', sanitizeCellInput);
      rowDiv.appendChild(input);
    }

    boardElement.appendChild(rowDiv);
  }
}

function renderPuzzle(nextPuzzle) {
  puzzle = nextPuzzle;
  createBoardElement();

  const boardElement = getBoardElement();
  const inputs = boardElement.getElementsByTagName('input');

  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const flatIndex = toFlatCellIndex(i, j);
      const cellValue = puzzle[i][j];
      const inputCell = inputs[flatIndex];

      if (cellValue !== 0) {
        inputCell.value = cellValue;
        inputCell.disabled = true;
        inputCell.className += ' prefilled';
      } else {
        inputCell.value = '';
        inputCell.disabled = false;
      }
    }
  }
}

async function newGame() {
  currentDifficulty = getSelectedDifficulty();
  const encodedDifficulty = encodeURIComponent(currentDifficulty);
  const response = await fetch(`/new?difficulty=${encodedDifficulty}`);
  const data = await response.json();
  renderPuzzle(data.puzzle);
  hintsUsed = 0;
  isGameSolved = false;
  startTimer();
  document.getElementById('message').innerText = '';
}

function readBoardFromInputs(inputs) {
  const board = [];

  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const flatIndex = toFlatCellIndex(i, j);
      const value = inputs[flatIndex].value;
      board[i][j] = value ? parseInt(value, 10) : 0;
    }
  }

  return board;
}

function highlightIncorrectCells(inputs, incorrectCells) {
  for (let index = 0; index < inputs.length; index++) {
    const inputCell = inputs[index];
    if (inputCell.disabled) {
      continue;
    }

    const row = Math.floor(index / SIZE);
    const col = index % SIZE;
    inputCell.className = buildCellBaseClass(row, col);

    if (incorrectCells.has(index)) {
      inputCell.className += ' incorrect';
    }
  }
}

async function checkSolution() {
  const boardElement = getBoardElement();
  const inputs = boardElement.getElementsByTagName('input');
  const board = readBoardFromInputs(inputs);

  const response = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });

  const data = await response.json();

  if (data.error) {
    setMessage(data.error, '#d32f2f');
    return;
  }

  const incorrectCells = new Set(
    data.incorrect.map(cell => toFlatCellIndex(cell[0], cell[1]))
  );

  highlightIncorrectCells(inputs, incorrectCells);

  // Check whether the board still contains empty cells
  const hasEmptyCells = board.some(row => row.includes(0));

  if (hasEmptyCells) {
    setMessage('Please complete the Sudoku before checking.', '#d32f2f');
    return;
  }

  if (incorrectCells.size === 0) {
    if (!isGameSolved) {
      saveCompletedGameScore();
      stopTimer();
      isGameSolved = true;
    }

    setMessage('Congratulations! You solved it!', '#388e3c');
  } else {
    setMessage('Some cells are incorrect.', '#d32f2f');
  }
}

async function requestHint() {
 const boardElement = getBoardElement();
const inputs = boardElement.getElementsByTagName('input');
const board = readBoardFromInputs(inputs);

const response = await fetch('/hint', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({ board })
});

  const data = await response.json();
  if (data.error) {
    setMessage(data.error, '#d32f2f');
    return;
  }

  if (!data.hint) {
    setMessage('No empty cells available.', '#1976d2');
    return;
  }

  
  const {row, col, value} = data.hint;
  lockCell(inputs, row, col, value);
  puzzle[row][col] = value;
  hintsUsed += 1;
  setMessage('Added one hint.', '#1976d2');
}

// Wire buttons
function toggleTheme() {
    document.documentElement.classList.toggle('dark-mode');

    const button = document.getElementById('theme-toggle');

    if (document.documentElement.classList.contains('dark-mode')) {
        button.textContent = '☀️ Light Mode';
        localStorage.setItem('theme', 'dark');
    } else {
        button.textContent = '🌙 Dark Mode';
        localStorage.setItem('theme', 'light');
    }
}

function loadTheme() {
    const savedTheme = localStorage.getItem('theme');

    if (savedTheme === 'dark') {
        document.documentElement.classList.add('dark-mode');
        document.getElementById('theme-toggle').textContent = '☀️ Light Mode';
    }
}
window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('hint').addEventListener('click', requestHint);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
  loadTheme();
  renderScoreboard();
  // initialize
  newGame();
});