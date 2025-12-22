import collections

def reveal_cells(board, row, col):
	rows, cols = len(board), len(board[0])
	revealed = set()
	queue = collections.deque()
	queue.append((row, col))
	while queue:
		r, c = queue.popleft()
		if (r, c) in revealed:
			continue
		revealed.add((r, c))
		if board[r][c] == 0:
			for dr in [-1, 0, 1]:
				for dc in [-1, 0, 1]:
					nr, nc = r + dr, c + dc
					if 0 <= nr < rows and 0 <= nc < cols:
						if (nr, nc) not in revealed and board[nr][nc] != 'M':
							queue.append((nr, nc))
	return revealed
