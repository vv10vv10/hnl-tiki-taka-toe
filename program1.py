# Football Tic-Tac-Toe (terminal version)

board = [[" " for _ in range(3)] for _ in range(3)]

rows = ["Barcelona", "Real Madrid", "Manchester United"]
cols = ["Brazil", "France", "Argentina"]

current_player = "X"

while True:
    print("\n      ", end="")
    for c in cols:
        print(f"{c:^15}", end="")
    print()

    for i in range(3):
        print(f"{rows[i]:<15}", end="")
        for j in range(3):
            print(f"{board[i][j]:^15}", end="")
        print()

    r = int(input(f"\nIgrač {current_player}, odaberi red (0-2): "))
    c = int(input("Odaberi stupac (0-2): "))

    if board[r][c] != " ":
        print("Polje je zauzeto!")
        continue

    player_name = input(
        f"Upiši nogometaša koji je igrao za " f"{rows[r]} i predstavljao {cols[c]}: "
    )

    # Ovdje bi inače išla provjera preko baze podataka/API-ja.
    print(f"Unio si: {player_name}")

    board[r][c] = current_player

    # Provjera pobjede
    for i in range(3):
        if all(board[i][j] == current_player for j in range(3)):
            print(f"\nPobjednik je igrač {current_player}!")
            exit()

        if all(board[j][i] == current_player for j in range(3)):
            print(f"\nPobjednik je igrač {current_player}!")
            exit()

    if all(board[i][i] == current_player for i in range(3)) or all(
        board[i][2 - i] == current_player for i in range(3)
    ):
        print(f"\nPobjednik je igrač {current_player}!")
        exit()

    # Neriješeno
    if all(board[i][j] != " " for i in range(3) for j in range(3)):
        print("\nNeriješeno!")
        exit()

    current_player = "O" if current_player == "X" else "X"
