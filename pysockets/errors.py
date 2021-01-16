import traceback

# TODO
class AbruptCloseError(Exception):
    pass

# Raised when no function was found with the name that the SocketServer was calling.
class FunctionNotFoundError(Exception):
    pass

# Raised when the connection to the Server failed.
class ConnectionFailedError(Exception):
    pass

# Raised when the data recieved is empty.
class NullRecieveError(Exception):
    pass

# Raised if the bytes length was not castable into an integer.
class NonCastableLengthError(Exception):
    pass
