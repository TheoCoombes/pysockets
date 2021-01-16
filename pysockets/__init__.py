from . import utils, errors
import socket
from time import sleep # See line 73

class SocketServer:
    # Setup variables
    def __init__(self, show_messages=True, encoding="utf-8"):
        self.recieves = {}
        self.on_recieve_list = []
        self.on_close_list = []
        self.show_messages = show_messages
        self.data_recieve_size = 4096
        self.encoding = encoding
        self.closed = False
        self.sock = None
        self.conn = None
        self.client_ip = None

    # Adds a function to the event dictionary.
    def event(self, function):
        self.recieves[function.__name__] = function

    # Adds a function to the on_recieve list.
    def on_recieve(self, function):
        self.on_recieve_list.append(function)

    # Adds a function to the on_close list.
    def on_close(self, function):
        self.on_close_list.append(function)

    # Sends a message on the socket connection.
    def send(self, function : str, *args, **kwargs):
        if self.closed:
            return
        args = args + (kwargs,)
        print(args)
        nargs, splits = utils.encode_args(args, encoding=self.encoding)
        splits.insert(0, function)
        data = str(splits).encode(self.encoding) + nargs
        self.conn.sendall(str(len(data)).encode(self.encoding))
        self.conn.sendall(data)

    # Creates the socket.
    def create(self, port, host=None, wait_for_client=True):
        self.closed = False
        if host is None:
            host = socket.gethostbyname(socket.gethostname())
        self.port = port
        self.host = host
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((host, port))
        if self.show_messages:
            print(f"[PySockets] Server Binded @ {self.host}:{self.port}")
        if wait_for_client:
            self.wait_for_client()
        
    # Close the socket server. When safe is true it'll wait for a confirmation.
    def close(self, outbound=True):
        if outbound:
            self.send("|CLOSE|")
        self.closed = True
        self.sock = None
        self.conn = None
        self.client_ip = None
        if self.show_messages:
            print("[PySockets] Socket Closed")
        for function in self.on_close_list:
            function()

    def wait_for_client(self):
        if self.show_messages:
            print("[PySockets] Waiting for Client Connection...")
        self.sock.listen()
        self.conn, self.client_ip = self.sock.accept()
        sleep(0.1) # TODO FIX (when no sleep, length data fails to send, instead only body data sends)
        if self.show_messages:
            print("[PySockets] Client Connected")

    # Listens for incoming data into the Socket Server indefinitely.
    def listen(self):
        with self.conn:
            while not self.closed:
                try:
                    length = int(self.conn.recv(25).decode(self.encoding))
                except TypeError:
                    raise errors.NullRecieveError("The length data recieved was empty")
                except ValueError:
                     raise errors.NonCastableLengthError("The length data recieved was not castable into an int")
                data = self.conn.recv(length)
                if not data:
                    raise errors.NullRecieveError("The data recieved was empty.")
                ndata, splits = utils.decode_splits_data(data, self.encoding)
                function = splits[0]
                if function == "|CLOSE|":
                    self.close(outbound=False)
                    break
                splits.pop(0)
                nargs = utils.decode_args(ndata, splits, self.encoding)
                kwargs = nargs[-1]
                nargs = nargs[:-1]
                for fnctn in self.on_recieve_list:
                    fnctn(function, *nargs, **kwargs)
                f = self.recieves.get(function, None)
                if f is not None:
                    f(*nargs, **kwargs)
                else:
                    raise errors.FunctionNotFoundError(f"The function \"{function}\" was not found")

    # Listens for incoming data into the Socket Server once.
    def listen_once(self):
        with self.conn:
            try:
                length = int(self.conn.recv(25).decode(self.encoding))
            except TypeError:
                raise errors.NullRecieveError("The length data recieved was empty")
            except ValueError:
                raise errors.NonCastableLengthError("The length data recieved was not castable into an int")
            data = self.conn.recv(length)
            if not data:
                raise errors.NullRecieveError("The data recieved was empty.")
            ndata, splits = utils.decode_splits_data(data, self.encoding)
            function = splits[0]
            if function == "|CLOSE|":
                self.close(outbound=False)
                return
            splits.pop(0)
            nargs = utils.decode_args(ndata, splits, self.encoding)
            kwargs = nargs[-1]
            nargs = nargs[:-1]
            for fnctn in self.on_recieve_list:
                fnctn(function, *nargs, **kwargs)
            f = self.recieves.get(function, None)
            if f is not None:
                f(*nargs, **kwargs)
            else:
                raise errors.FunctionNotFoundError(f"The function \"{function}\" was not found")

class SocketClient:
    # Setup variables
    def __init__(self, show_messages=True, encoding="utf-8"):
        self.recieves = {}
        self.on_recieve_list = []
        self.on_close_list = []
        self.show_messages = show_messages
        self.data_recieve_size = 4096
        self.encoding = encoding
        self.closed = False
        self.sock = None

    # Adds a function to the event list.
    def event(self, function):
        self.recieves[function.__name__] = function
    
    # Adds a function to the on_recieve list.
    def on_recieve(self, function):
        self.on_recieve_list.append(function)

    # Adds a function to the on_close list.
    def on_close(self, function):
        self.on_close_list.append(function)

    # Sends a message on the socket connection.
    def send(self, function : str, *args, **kwargs):
        if self.closed:
            return
        args = args + (kwargs,)
        print(args)
        nargs, splits = utils.encode_args(args, encoding=self.encoding)
        splits.insert(0, function)
        data = str(splits).encode(self.encoding) + nargs
        self.sock.sendall(str(len(data)).encode(self.encoding))
        self.sock.sendall(data)

    # Creates the socket.
    def connect(self, port, host=None):
        self.closed = False
        if host is None:
            host = socket.gethostbyname(socket.gethostname())
        self.port = port
        self.host = host
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((host, port))
        except Exception as e:
            raise errors.ConnectionFailedError(f"Failed to connect to {self.host}:{self.port}\n\n{e}")
        if self.show_messages:
            print(f"[PySockets] Server Connected @ {self.host}:{self.port}")
        
    # Close the connection to the socket server.
    def close(self, outbound=True):
        if outbound:
            self.send("|CLOSE|")
        self.closed = True
        self.sock = None
        if self.show_messages:
            print("[PySockets] Socket Connection Closed")
        for function in self.on_close_list:
            function()

    # Listens for incoming data into the Socket Server indefinitely.
    def listen(self):
        while not self.closed:
            try:
                length = int(self.sock.recv(25).decode(self.encoding))
            except TypeError:
                raise errors.NullRecieveError("The length data recieved was empty")
            except ValueError:
                raise errors.NonCastableLengthError("The length data recieved was not castable into an int")
            data = self.sock.recv(length)
            if not data:
                raise errors.NullRecieveError("The data recieved was empty.")
            ndata, splits = utils.decode_splits_data(data, self.encoding)
            function = splits[0]
            if function == "|CLOSE|":
                self.close(outbound=False)
                break
            splits.pop(0)
            nargs = utils.decode_args(ndata, splits, self.encoding)
            kwargs = nargs[-1]
            nargs = nargs[:-1]
            for fnctn in self.on_recieve_list:
                fnctn(function, *nargs, **kwargs)
            f = self.recieves.get(function, None)
            if f is not None:
                f(*nargs, **kwargs)
            else:
                raise errors.FunctionNotFoundError(f"The function \"{function}\" was not found")

    # Listens for incoming data into the Socket Server once.
    def listen_once(self):
        try:
            length = int(self.sock.recv(25).decode(self.encoding))
        except TypeError:
            raise errors.NullRecieveError("The length data recieved was empty")
        except ValueError:
            raise errors.NonCastableLengthError("The length data recieved was not castable into an int")
        data = self.sock.recv(length)
        if not data:
            raise errors.NullRecieveError("The data recieved was empty.")
        ndata, splits = utils.decode_splits_data(data, self.encoding)
        function = splits[0]
        if function == "|CLOSE|":
            self.close(outbound=False)
            return
        splits.pop(0)
        nargs = utils.decode_args(ndata, splits, self.encoding)
        kwargs = nargs[-1]
        nargs = nargs[:-1]
        for fnctn in self.on_recieve_list:
            fnctn(function, *nargs, **kwargs)
        f = self.recieves.get(function, None)
        if f is not None:
            f(*nargs, **kwargs)
        else:
            raise errors.FunctionNotFoundError(f"The function \"{function}\" was not found")
