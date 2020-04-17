# File Transfer Utility

A simple application to transfer files from a client computer to a server computer (currently only supports one file at a time).

## How to use:
### 1. Installation

    $ git clone https://github.com/DarkCeptor44/file-transfer.git && cd file-transfer
    $ pip install -r requirements.txt

### 2. Start server

    $ python main.py server
Or

    $ server.bat

When a file is received it's gonna ask where to save it, simply choose a name and the original extension.
    
### 3. Start client

    $ python main.py client --host SERVER_IP
Or

    $ client.bat SERVER_IP
    
When running it's gonna ask you for a file to send, simply choose it and wait.