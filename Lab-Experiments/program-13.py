def minimax(depth, node, maximizing):
    if depth == 3:
        return node

    if maximizing:
        return max(
            minimax(depth + 1, node + 1, False),
            minimax(depth + 1, node + 2, False)
        )
    else:
        return min(
            minimax(depth + 1, node + 1, True),
            minimax(depth + 1, node + 2, True)
        )

result = minimax(0, 0, True)

print("Best value using Minimax:", result)