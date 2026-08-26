def alpha_beta(depth, node, alpha, beta, maximizing):

    if depth == 3:
        return node

    if maximizing:
        best = -999

        for value in [node + 1, node + 2]:
            best = max(best, alpha_beta(depth + 1, value,
                                        alpha, beta, False))
            alpha = max(alpha, best)

            if beta <= alpha:
                break

        return best

    else:
        best = 999

        for value in [node + 1, node + 2]:
            best = min(best, alpha_beta(depth + 1, value,
                                        alpha, beta, True))
            beta = min(beta, best)

            if beta <= alpha:
                break

        return best


result = alpha_beta(0, 0, -999, 999, True)

print("Best value using Alpha-Beta Pruning:", result)