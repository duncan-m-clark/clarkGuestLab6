import socket
import sys
import time
from dataclasses import dataclass

@dataclass
class Maze: #used for the maze created
    width: int
    height: int
    cells: bytes


players = [] # GLOBAL VARIABLES
max_players = 0
player_num = 0


def testing(): # used for teting the server side of the protocol
    s = socket.socket()
    s.bind(("localhost", 8008))
    s.listen(1)
    c, a = s.accept()
    cmd = ""

    while(cmd != "exit"):
        cmd = input("enter hex")
        cmd = bytes.fromhex(cmd)
        print(cmd)
        c.send(cmd) #must be in bb'00' form
    c.close()
    s.close()



def print_maze(maze):
    #print(maze.cells)
    global max_players
    global players

    for y in range(maze.height): # printing in grid layout for reference
        for x in range(maze.width):

            print(f'{maze.cells[x + (y*maze.width)] &0xf :04b}', end = '')
            for i in range(max_players):
                #print(players[i], " ", y, x)
                if players[i]["row"] == y and players[i]["col"] == x and players[i]["in_use"]:
                    print(f"P{i+1}", end="") # show locations

            print(end = " ") #formatting for troubleshooting

        print('\n')


def check_jumps(col, row, direction, maze): # helper function to choose_move. Returns amount of jumps for certain move. Recurses to find total jumps
    global max_players
    global players

    if(col < maze.width and row < maze.height):
        for i in range(max_players):
            if players[i]["row"] == row and players[i]["col"] == col and players[i]["in_use"]: # any active player in that position
                if direction == "down" and row+1 < maze.height: # check for boundary
                    return check_jumps(col, row+1, "down", maze) + 1 #recurse to see multiple jumps
                elif direction == "right" and col+1 < maze.width: #check boundary
                    return check_jumps(col+1, row, "right", maze) + 1 # recurse right
    return 0 #root case. either hit a boundary or there is no player

def check_move(col, row, direction, maze, jump): # makes sure its a valid move. Returns True if move is valid. jump is bool for if the move is a jump
    if(col < maze.width and row < maze.height):
        for i in range(max_players):
            if players[i]["row"] == row and players[i]["col"] == col and players[i]["in_use"]: # any active player in that position

                if(jump == False): #moving into another player cannot happen
                    return False

                if direction == "down" and jump and row+1 < maze.height: # check for boundary if its a jump
                    return check_move(col, row+1, "down", maze, jump)#recurse to see multiple jumps
                elif direction == "right" and jump and col+1 < maze.width: #check boundary if its a jump
                    return check_move(col+1, row, "right", maze, jump) # recurse right
                
                
                
        
        return True # move ends on the map

    else: # move takes you off the map
        return False



def choose_move(maze):# The idea is to find the move down or right that jumps the most squares. If not, then just move 

    global players #getting global variables to find positions of players
    global player_num


    row = players[player_num]["row"]
    col = players[player_num]["col"]

    current_cell = maze.cells[col + row * maze.width] #getting the value at the index of the player
    bottom_open = current_cell & 0x08 # gets the value of the bit in the 4th position x000 = bottom wall
    right_open = current_cell &0x01 #gets value of rightmost bit 000x = right wall

    right_jump = check_jumps(col+1, row, "right", maze) # checking right jump for jumps over players
    down_jump = check_jumps(col, row+1, "down", maze) # checking down jump for jumps over players
    

    #print("R D: ", right_jump,  " ", down_jump)
    if(right_jump >= down_jump and check_move(col+1, row, "right", maze, True)): # jump right if its better than bottom jump. Default right jump on ==
        if (right_jump == 0 and right_open == 0) or right_jump > 0: #no players to the right but there is a wall or there is a tie > 0
            return 0x13 #return hex for jump right

        else: 
            return 0xf # move right since there is no wall. Already know it stays on the map due to check_move above
    
    elif(down_jump >= right_jump and check_move(col, row+1, "down", maze, True)): # jump down if it jump more than a right jump. = in case right jump is not valid on tie
        if(down_jump == 0 and bottom_open == 0) or down_jump > 0:
            return 0x16 #return hex for down jump.
        
        else:
            return 0x12 # move down if there is no wall
    
    else: #No hopping found and down is not valid. We now just move down. NOTE This may lose your turn if there is a player in front of you but there is no valid move to bring you closer to the exit
        if(bottom_open): #if there is no wall
            #print("MD")
            return 0x12 # move down
        else:
            #print("JD")
            return 0x16 #jump wall




def client(address): #handles client side receives and inputs
    global max_players
    global player_num
    global players
    # setup connection
    s = socket.socket()
    try:
        s.connect((address, 8008))

    except socket.error as e:
        print("Unable to connect to server", e)
    
    while(True): #using break statements to get out
    
        msg_code = s.recv(1, socket.MSG_WAITALL).hex() # just receive the first byte. this flag is used in the client given and will be useful later
        print(msg_code)
        

        if msg_code == '00': #Welcome message
            player_num = int.from_bytes(s.recv(1, socket.MSG_WAITALL))
            max_players = int.from_bytes(s.recv(1, socket.MSG_WAITALL))

            players = [None] * max_players
            print(f"Welcome Player {player_num+1} of {max_players}\n")

            for i in range(max_players): # initialize the player array
                players[i] = {"in_use": False, "col": 0, "row": 0} #in_use is if they joined
        
        elif msg_code == '01': # receive maze uncompressed
            maze_size = int.from_bytes(s.recv(2, socket.MSG_WAITALL), 'little') # little is needed for multiple bytes
            width = int.from_bytes(s.recv(1, socket.MSG_WAITALL))
            height = int.from_bytes(s.recv(1, socket.MSG_WAITALL))
            cells = s.recv(maze_size-2, socket.MSG_WAITALL)#-2 since we alrady got two bytes|

            maze = Maze(width, height, cells) # setting maze object values
            print('Received uncompressed maze')

        elif msg_code == '02': # receive compressed maze. TODO if time
            print("not supported")
            s.recv(102, soket.MSG_WAITALL) # get rid of the next 102 bytes which are the maze 

        elif msg_code == '05': # Illegal move
            print("Illegal Move")
            time.sleep(10) # debugging

        elif msg_code == '06': # not your turn
            print("it is not your turn")

        elif msg_code == '07': # 07 - get location
            player_id = int.from_bytes(s.recv(1, socket.MSG_WAITALL)) # get player to change position
            col = int.from_bytes(s.recv(1, socket.MSG_WAITALL))# get column first
            row = int.from_bytes(s.recv(1, socket.MSG_WAITALL))# get row second

            players[player_id]["col"] = col
            players[player_id]["row"] = row
            players[player_id]["in_use"] = True # in case the player joined before you did
            print(f"Player {player_id+1}'s position updated to {col},{row}")

        elif msg_code == '08': # 08 - someone's turn
            
            player_id = int.from_bytes(s.recv(1, socket.MSG_WAITALL)) # get id whose turn

            #print_maze(maze) # for testing

            if player_id == player_num: # its your turn
                print("Its your turn")
                time.sleep(.2)
                move = choose_move(maze)
                print(hex(move))
                if move == "exit": #L was given and we are leaving the game loop
                    break
                else:
                    s.send(move.to_bytes())# send the move to the server
            else:
                print(f"Its player {player_id+1}'s turn.")
            
            
        elif msg_code == '09': # 09 - too many players
            print("There are too many players. Goodbye")
            break # break loop to exit games

        elif msg_code == '0a': # 0a - a player joins
            player_id = int.from_bytes(s.recv(1, socket.MSG_WAITALL)) # get id of who joined
            players[player_id]["in_use"] = True #change status to in_use
            print(f"Player {player_id+1} has joined")

        elif msg_code == '0b': #0b - a player left
            player_id = int.from_bytes(s.recv(1, socket.MSG_WAITALL)) # get id of who left
            players[player_id]["in_use"] = False #change status to in_use
            print(f"Player {player_id+1} has left.")
        
        elif msg_code == '0c': #0c - a player wins
            player_id = int.from_bytes(s.recv(1, socket.MSG_WAITALL)) # get id of who won
            print(f"Player {player_id + 1} Won!")
            if(player_id == player_num):
                print("Great Job! you won!")
            else:
                print("Better luck next time :(")
        
        elif msg_code == '0d': #0d - starting new game
            print("Starting a new game") 
        
        elif msg_code == '0e': # Server terminated
            print("The server has closed.")
            break # get out of loop
        else:
            print("Unrecognized message: ", msg_code)

            try:
                print("send")
                s.send(b'') #send empty bit to test connection, 
            except (BrokenPipeError, ConnectionResetError, OSError) as e:
                print("Connection to the server has been lost. Please try restarting.")
                break
    
    print("Closing connection")
    s.close() # close connection



if __name__ == "__main__":

    if len(sys.argv) > 1: # for testing. Sends one bit at a time and acts as server
        if sys.argv[1] == "server":
            testing()
        else:
            client(sys.argv[1]) # pass in the server address
    else:
        print("Please include the server address or \"server\" for testing")
