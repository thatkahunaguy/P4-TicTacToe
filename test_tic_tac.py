"""quick tests"""

# from tic_tac_toe import text_board_to_array


def text_board_to_array(board):
    board_array = [[0, 0, 0] for i in range(3)]
    print "board_array=", board_array
    for i in range(0, 3):
        print "i=", i
        index = 3*i
        print "index=", index
        snippet = board[index:index+3]
        print "snippet=", snippet
        for j in range(0, 3):
            print "j=", j
            char = snippet[j]
            # skip if the space is 0/blank
            if not(char == "0"):
                if char == "X":
                    board_array[i][j] = 1
                else:
                    board_array[i][j] = -1
    return board_array


def game_over(array):
    board_array = text_board_to_array(array)
    print board_array
    # check row & column of the move & diagonols
    # assume the move was 0, 0 for test
    row = col = diag1 = diag2 = 0
    for i in range(0, 3):
        row += board_array[0][i]
        col += board_array[i][0]
        diag1 += board_array[i][i]
        diag2 += board_array[i][abs(2-i)]
    print "row=", row
    print "col=", col
    print "diag1=", diag1
    print "diag2=", diag2
    if abs(row) == 3 or abs(col) == 3 or abs(diag1) == 3 or abs(diag2) == 3:
        return True
    else:
        return False

again = True
while again:
    string = raw_input("Enter the board:")
    print string
    # array = text_board_to_array(string)
    # print array
    if game_over(string):
        print "Game Over"
    else:
        print "Keep Going"
    a = raw_input("Enter 0 to continue:")
    if a == "0":
        again = True
    else:
        again = False
