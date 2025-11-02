import socket
import sys


def testing():
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


def client():
    # setup connection
    # receive opcode
    # switch statements
    # take in the appropriate amount of bytes for the opcode
    return


if __name__ == "__main__":

    if len(sys.argv) > 1 and sys.argv[1] == "server": # for testing. Sends one bit at a time and acts as server
        testing()
    else:
        client()
