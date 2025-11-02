import socket
import sys


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
        c.send(cmd) #must be in b'\x00' form
    c.close()
    s.close()


def client(address): #handles 
    # setup connection
    s = socket.socket()
    try:
        s.connect((address, 8008))

    except socket.error as e:
        print("Unable to connect to server", e)
    
    while(True):
        receive = s.recv(1, MSG_WAITALL) # just receive the first byte. this flag is used in the client given and will be useful later

            print(receive)

        match receive:

            case '\0': #Welcome message

            case '\x01': # receive maze uncompressed

            case '\x02': # receive compressed maze. TODO if time

            case '\x05': # Illegal move

            case '\x06': # not your turn

            case '\a': # 07 - get location

            case '\b': # 08 - your turn
            
            case '\t': # 09 - too many players

            case '\n': # 0a - a player joins

            case '\v': #0b - a player left

            case '\f': #0c - a player wins

            case '\r': #0d - starting new game

            case '\x0e': # Server terminated



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
