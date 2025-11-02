import socket
import sys
import time


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


def client(address): #handles client side receives and inputs
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
            cells = int.from_bytes(s.recv(maze_size-2, socket.MSG_WAITALL), 'little')#-2 since we alrady got two bytes
            print('Received uncompressed maze')

        elif msg_code == '02': # receive compressed maze. TODO if time
            print("not supported\n")

        elif msg_code == '05': # Illegal move
            print("Illegal Move\n")

        elif msg_code == '06': # not your turn
            print("it is not your turn\n")

        elif msg_code == '07': # 07 - get location
            player_id = int.from_bytes(s.recv(1, socket.MSG_WAITALL)) # get player to change position
            col = int.from_bytes(s.recv(1, socket.MSG_WAITALL))# get column first
            row = int.from_bytes(s.recv(1, socket.MSG_WAITALL))# get row second

            players[player_id]["col"] = col
            players[player_id]["row"] = row
            players[player_id]["in_use"] = True # in case the player joined before you did
            print(f"Player {player_id+1}'s position updated")

        elif msg_code == '08': # 08 - someone's turn
            player_id = int.from_bytes(s.recv(1, socket.MSG_WAITALL)) # get id whose turn
            if player_id == player_num: # its your turn
                print("Its your turn\n")
            
        elif msg_code == '09': # 09 - too many players
            print("There are too many players. Goodbye.\n")
            break # break loop to exit games

        elif msg_code == '0a': # 0a - a player joins
            player_id = int.from_bytes(s.recv(1, socket.MSG_WAITALL)) # get id of who joined
            players[player_id]["in_use"] = True #change status to in_use
            print(f"Player {player_id+1} has joined\n")

        elif msg_code == '0b': #0b - a player left
            player_id = int.from_bytes(s.recv(1, socket.MSG_WAITALL)) # get id of who left
            players[player_id]["in_use"] = False #change status to in_use
            print(f"Player {player_id+1} has left.\n")
        
        elif msg_code == '0c': #0c - a player wins
            player_id = int.from_bytes(s.recv(1, socket.MSG_WAITALL)) # get id of who won
            print(f"Player {player_id + 1} Won!\n")
            if(player_id == player_num):
                print("Great Job! you won!")
            else:
                print("Better luck next time :(")
        
        elif msg_code == '0d': #0d - starting new game
            print("Starting a new game\n") 
        
        elif msg_code == '0e': # Server terminated
            print("The server has closed. Closing connection.\n")
            break # get out of loop
        else:
            print("Unrecognized message: ", msg_code, "\n")
    
    
    s.close() # close connection



    # receive opcode
    # switch statements
    # take in the appropriate amount of bytes for the opcode
    return


if __name__ == "__main__":

    if len(sys.argv) > 1: # for testing. Sends one bit at a time and acts as server
        if sys.argv[1] == "server":
            testing()
        else:
            client(sys.argv[1]) # pass in the server address
    else:
        print("Please include the server address or \"server\" for testing")
