board = [' '] * 9

def display():
    print(board[0], '|', board[1], '|', board[2])
    print('--+---+--')
    print(board[3], '|', board[4], '|', board[5])
    print('--+---+--')
    print(board[6], '|', board[7], '|', board[8])

def check_win(player):
    wins = [
        (0,1,2), (3,4,5), (6,7,8),
        (0,3,6), (1,4,7), (2,5,8),
        (0,4,8), (2,4,6)
    ]

    for a, b, c in wins:
        if board[a] == board[b] == board[c] == player:
            return True
    return False

player = 'X'

for i in range(9):
    display()
    pos = int(input("Enter position (1-9): ")) - 1

    if board[pos] == ' ':
        board[pos] = player

        if check_win(player):
            display()
            print(player, "wins!")
            break

        player = 'O' if player == 'X' else 'X'
    else:
        print("Position already occupied!")

else:
    display()
    print("Draw!")