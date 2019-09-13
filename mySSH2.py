import paramiko
import time
import sys


def __init__(self):
    print ("function is running!")


def sshConnect(myAddress: str, myUsername: str, myPassword: str) -> paramiko.client:
    print("Connecting to server.")
    #   paramiko.util.log_to_file("Paramiko-util.log")
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(myAddress, username=myUsername, password=myPassword, allow_agent=False, timeout=30)
        return client
    except paramiko.ssh_exception:
        print("SSH Exception: Failed to establish connection", file=sys.stderr)
        sys.exit(50)


def sendCommand(client: paramiko.client, command: str) -> str:
    global mystring
    print ("sending " + command)
    stdin, stdout, stderr = client.exec_command(command + "\n", timeout=60)
    status = stdout.channel.exit_status_ready()
    stdin.flush()
    if status == 0:
        mystring = stdout.read(65535)
        print(mystring.decode('utf-8'))
        stdout.flush()
    # for line in stdout:
    #    print('... ' + line.strip('\n'))
    return mystring.decode('utf-8')


def shellInvoke(client: paramiko.client) -> paramiko.channel:
    print ("Starting Shell\n")
    cliChan = client.invoke_shell()
    return cliChan


def shellCommand(shellChan: paramiko.channel, command: str) -> str:
    print ("Sending Shell Command:  " + command + "\n")
    shellChan.send(command + "\r")
    #time.sleep(sleeptime)
    myOutput = shellChan.recv(131072)
    print (myOutput.decode("utf-8"))
    return myOutput.decode('utf-8')


def sshClose(client: paramiko.client) -> int:
    try:
        client.close()
        return 1
    except paramiko.SSHException:
        print ("failed to close ssh")
