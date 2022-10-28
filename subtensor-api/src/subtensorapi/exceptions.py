class FastSyncException(Exception):
    """"Exception raised during fast sync of neurons"""
    pass

class FastSyncOSNotSupportedException(FastSyncException):
    """"Exception raised when the OS is not supported by fast sync"""
    pass

class FastSyncNotFoundException(FastSyncException):
    """"Exception raised when the fast sync binary is not found"""
    pass

class FastSyncFormatException(FastSyncException):
    """"Exception raised when the downloaded metagraph file is not formatted correctly"""
    pass

class FastSyncFileException(FastSyncException):
    """"Exception raised when the metagraph file cannot be read"""
    pass

class FastSyncRuntimeException(FastSyncException):
    """"Exception raised when the fast sync binary fails to run"""
    pass
