# The MIT License (MIT)
# Copyright © 2022 Opentensor Foundation

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated 
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, 
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of 
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION 
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.

__version__ = "1.1.0"

import enum
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Dict, List, Optional, Union
import multiprocessing as mp

from .exceptions import *

RAOPERTAO: int = 1e9
U64MAX: int = 18_446_744_073_709_551_615
U32MAX: int = 4_294_967_295


class OS_NAME(enum.Enum):
    """Enum for OS_NAME"""
    LINUX = "linux"
    MAC = "macos"
    WINDOWS = "windows"

@dataclass
class NeuronData:
    """
    Dataclass for NeuronData
    From JSON of the form
    {
        "hotkey": str,
        "coldkey": str,
        "uid": int,
        "active": int,
        "ip": str,
        "ip_type": int,
        "port": int,
        "stake": str(int),
        "rank": str(int),
        "emission": str(int),
        "incentive": str(int),
        "consensus": str(int),
        "trust": str(int),
        "dividends": str(int),
        "modality": int,
        "last_update": str(int),
        "version": int,
        "priority": str(int),
        "weights": [
            [int, int],
        ],
        "bonds": [
            [int, str(int)],
        ],
    }
    """
    hotkey: str
    coldkey: str
    uid: int
    active: int
    ip: str
    ip_type: int
    port: int
    stake: int
    rank: int
    emission: int
    incentive: int
    consensus: int
    trust: int
    dividends: int
    modality: int
    last_update: int
    version: int
    priority: int
    weights: List[List[int]]
    bonds: List[List[int]]

class FastSync:
    endpoint_url: str

    def __init__(self, endpoint_url: str) -> None:
        self.endpoint_url = endpoint_url

    @classmethod
    def get_platform(cls) -> str:
        return sys.platform

    @classmethod
    def get_os(cls) -> OS_NAME:
        """Returns the OS enum for the current OS"""
        platform = cls.get_platform()
        if platform == "linux" or platform == "linux2":
            return OS_NAME.LINUX
        elif platform == "darwin":
            return OS_NAME.MAC
        elif platform == "win32":
            return OS_NAME.WINDOWS
        else:
            raise Exception("Not sure what OS this is")

    @classmethod
    def verify_fast_sync_support(cls) -> None:
        """
        Verifies that the current system is supported by fast sync

        Raises:
            FastSyncOSNotSupportedException: If the current OS is not supported
            FastSyncNotFoundException: If the fast sync binary is not found
        """
        cls.verify_os_support()
        cls.verify_binary_exists()

    @classmethod
    def verify_os_support(cls) -> None:
        """
        Verifies that the current OS is supported by fast sync

        Raises:
            FastSyncOSNotSupportedException: If the current OS is not supported
        """

        try:
            OS = cls.get_os()
        except Exception as e:
            raise FastSyncOSNotSupportedException("OS not supported by fast sync: {}".format(e))
        
        if OS != OS.LINUX and OS != OS.MAC:
            raise FastSyncOSNotSupportedException("OS not supported for fast sync")
    
    @classmethod
    def verify_binary_exists(cls) -> None:
        """
        Verifies that the fast sync binary exists

        Raises:
            FastSyncNotFoundException: If the fast sync binary is not found
        """
        path_to_bin = cls.get_path_to_fast_sync()
        if not os.path.exists(path_to_bin) or not os.path.isfile(path_to_bin):
            raise FastSyncNotFoundException("Could not find fast sync binary at {}.".format(path_to_bin))

    @classmethod
    def get_path_to_fast_sync(cls) -> str:
        """Returns the path to the fast sync binary"""
        os_name: OS_NAME = cls.get_os()
        path_to_bin = os.path.join(os.path.dirname(__file__), f"./bin/subtensor-node-api-{os_name.value}")
        return path_to_bin

    @classmethod
    def __call_binary(cls, args: List[str]) -> None:
        """
        Calls the fast sync binary with the given args

        Args:
            args: List of arguments to pass to the fast
                sync binary

        Raises:
            FastSyncRuntimeException: If the fast sync binary fails
        """
        cls.verify_fast_sync_support()
        path_to_bin = cls.get_path_to_fast_sync()
        args = [path_to_bin] + args
        try:
            subprocess.run(args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.decode(sys.getfilesystemencoding())
            raise FastSyncRuntimeException("Error running fast sync binary: {}\nSTDERR={}".format(e, stderr))


    @classmethod
    def __call_binary_and_get_file(cls, args: List[str], init_read_timeout: Optional[int] = 30) -> bytes:
        """
        Calls the fast sync binary with the given args and returns the file_data

        Args:
            args: List of arguments to pass to the fast
                sync binary
            init_read_timeout (optional): 
                Timeout for the initial read of the file
                in seconds. Defaults to 30 seconds.
                None means no timeout.

        Raises:
            FastSyncRuntimeException: If the fast sync binary fails
        """
        READ_BUFFER_SIZE: int = 3 * 1024 * 1024
        cls.verify_fast_sync_support()
        path_to_bin = cls.get_path_to_fast_sync()

        # create pipe to get file from nodejs
        conn = mp.Pipe()
        conn1, conn2 = conn
        in_fd, out_fd = conn1.fileno(), conn2.fileno()
        
        args = [path_to_bin] + args + ['-p', str(out_fd)] # pass write end of pipe to nodejs
        std_out, std_err = None, None

        try:
            with subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, pass_fds=[out_fd]) as proc:
                file_data = b''
                conn1.poll(init_read_timeout) # wait for first data to be written to pipe
                while conn1.poll(0.1): 
                    data = os.read(in_fd, READ_BUFFER_SIZE)
                    file_data += data

                try:
                    std_out, std_err = proc.communicate(None, timeout=0.2)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    std_out, std_err = proc.communicate(None, timeout=0.2)

            conn1.close()
            conn2.close()
            
            # with env should close the read end of the pipe

            # check for errors
            if proc.returncode != 0:
                # read stderr from nodejs
                stderr = std_err.decode(sys.getfilesystemencoding()) if std_err else ''
                raise FastSyncRuntimeException("Error running fast sync binary: {}\nSTDERR={}".format(proc.returncode, stderr))

            if file_data == b'':
                raise FastSyncRuntimeException("Error running fast sync binary: No data returned from nodejs within timeout {}s".format(init_read_timeout))
            
            return file_data
        
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.decode(sys.getfilesystemencoding())
            raise FastSyncRuntimeException("Error running fast sync binary: {}\nSTDERR={}".format(e, stderr))

    def sync_and_save(self, block_hash: str, filename: Optional[str] = None) -> None:
        """Runs the fast sync binary to sync all neurons at a given block hash"""
        self.verify_fast_sync_support()
        args = ["sync_and_save", "-u", self.endpoint_url, '-b', block_hash]
        if filename is not None:
            args.extend(['-f', filename])
        # will write to ~/.bittensor/metagraph.json by default
        self.__call_binary(args)

    def sync_fd(self, block_hash: str, init_read_timeout: int = 30) -> List[SimpleNamespace]:
        """Runs the fast sync binary to sync all neurons at a given block hash"""
        self.verify_fast_sync_support()
        args = ["sync_and_save", "-u", self.endpoint_url, '-b', block_hash]

        file_data = self.__call_binary_and_get_file(args, init_read_timeout=init_read_timeout)

        return self._load_neurons_from_metragraph_file_data(file_data)

    def sync_and_save_historical(self, block_numbers: List[Union[int, str]] = ["latest"], uids: List[int] = [], filename: Optional[str] = None) -> None:
        """Runs the fast sync binary to sync all uids at each block number"""
        self.verify_fast_sync_support()
        args = (
            ["sync_and_save_historical", "-u", self.endpoint_url] +
            (['-b'] + [str(bn) for bn in block_numbers]) +
            ((['-i'] + [str(uid) for uid in uids]) if len(uids) > 0 else []) + # uids are optional, default to all
            (['-f', filename] if filename is not None else []) # will write to ~/.bittensor/metagraph_historical.json by default
        )

        self.__call_binary(args)

    def sync_historical_fd(self, block_numbers: List[Union[int, str]] = ["latest"], uids: List[int] = [], init_read_timeout: int = 30) -> Dict[str, Dict[str, SimpleNamespace]]:
        """Runs the fast sync binary to sync all uids at each block number"""
        self.verify_fast_sync_support()
        args = (
            ["sync_and_save_historical", "-u", self.endpoint_url] +
            (['-b'] + [str(bn) for bn in block_numbers]) +
            ((['-i'] + [str(uid) for uid in uids]) if len(uids) > 0 else []) # uids are optional, default to all
        )

        file_data = self.__call_binary_and_get_file(args, init_read_timeout=init_read_timeout)

        return self._load_neurons_from_historical_metragraph_file_data(file_data)

    def sync_and_save_historical_difficulty(self, block_numbers: List[Union[int, str]] = ["latest"], filename: Optional[str] = None) -> None:
        """Runs the fast sync binary to sync difficulty at each block number"""
        self.verify_fast_sync_support()
        args = (
            ["sync_and_save_historical_difficulty", "-u", self.endpoint_url] +
            (['-b'] + [str(bn) for bn in block_numbers]) +
            (['-f', filename] if filename is not None else []) # will write to ~/.bittensor/metagraph_historical.json by default
        )

        self.__call_binary(args)

    def sync_historical_difficulty_fd(self, block_numbers: List[Union[int, str]] = ["latest"], init_read_timeout: int = 30) -> Dict[str, Dict[str, SimpleNamespace]]:
        """Runs the fast sync binary to sync difficulty at each block number"""
        self.verify_fast_sync_support()
        args = (
            ["sync_and_save_historical_difficulty", "-u", self.endpoint_url] +
            (['-b'] + [str(bn) for bn in block_numbers])
        )

        file_data = self.__call_binary_and_get_file(args, init_read_timeout=init_read_timeout)

        return self._load_historical_difficulty_file_data(file_data)

    def get_blockAtRegistration_for_all_and_save(self, block_hash: str, filename: Optional[str] = None) -> None:
        """Runs the fast sync binary to get blockAtRegistration for all neurons at a given block hash"""
        self.verify_fast_sync_support()
        args = ["block_at_reg_and_save", "-u", self.endpoint_url, '-b', block_hash]
        if filename is not None:
            args.extend(['-f', filename])
        # will write to ~/.bittensor/blockAtRegistration_all.json by default
        self.__call_binary(args)

    def get_blockAtRegistration_for_all_fd(self, block_hash: str) -> List[int]:
        """Runs the fast sync binary to get blockAtRegistration for all neurons at a given block hash"""
        self.verify_fast_sync_support()
        args = ["block_at_reg_and_save", "-u", self.endpoint_url, '-b', block_hash]

        file_data = self.__call_binary_and_get_file(args)

        return self._load_neurons_from_blockAtRegistration_all_file_data(file_data)

    @classmethod
    def load_blockAtRegistration_for_all(cls, json_file_location: Optional[str] = '~/.bittensor/blockAtRegistration_all.json') -> List[int]:
        """
        Loads neurons from the blockAtRegistration JSON file
        See: https://github.com/opentensor/subtensor-api/tree/main/js#blockatregistration-structure

        Args:
            json_file_location (str, optional): The location of the blockAtRegistration JSON file. Defaults to '~/.bittensor/blockAtRegistration_all.json'.
        
        Raises:
            FastSyncFileException: If the JSON file could not be read
            FastSyncFormatException: If the JSON file is not in the correct format
        
        Returns:
            List[int]
                a list of the blockAtRegistration numbers
        """
        try:
            with open(os.path.join(os.path.expanduser(json_file_location))) as f:
                file_data = f.read()
            return cls._load_neurons_from_blockAtRegistration_all_file_data(file_data)
        except FileNotFoundError:
            raise FastSyncFileException('{} not found. Try calling fast_sync_neurons() first.', json_file_location)
        except OSError:
            raise FastSyncFileException('Could not read {}', json_file_location)

    @classmethod
    def _load_neurons_from_blockAtRegistration_all_file_data(cls, file_data: str) -> List[int]:
        """
        Loads neurons from the blockAtRegistration_all JSON file data
        
        Raises: FastSyncFormatException if the file is not in the correct format

        Returns: List[int]
            a list of the blockAtRegistration numbers
        """
        try:
            data = json.loads(file_data)
        except json.JSONDecodeError:
            raise FastSyncFormatException('Could not parse blockAtRegistration JSON file data as json')

        # all the large ints are strings
        if not isinstance(data, list):
            raise FastSyncFormatException('Expected a JSON array at the top level')
        
        try:
            # validate the blockAtRegistration data
            blockAtRegistration_all: List[int] = [
                int(blockAtRegistration) for blockAtRegistration in data
            ]
        except Exception as e:
            raise FastSyncFormatException('Could not parse blockAtRegistration JSON file data: {}'.format(e))
            
        return blockAtRegistration_all

    @classmethod
    def _load_neurons_from_metragraph_file_data(cls, file_data: str) -> List[SimpleNamespace]:
        """
        Loads neurons from the metagraph file data
        See: https://github.com/opentensor/subtensor-api/tree/main/js#neuron-structure
        
        Raises: FastSyncFormatException if the file is not in the correct format

        Returns: List[SimpleNamespace]
            a list of the Neurons
        """
        try:
            data = json.loads(file_data)
        except json.JSONDecodeError:
            raise FastSyncFormatException('Could not parse metagraph file data as json')

        # the top level is a list
        if not isinstance(data, list):
            raise FastSyncFormatException('Expected a JSON array at the top level')
        
        neurons: List[SimpleNamespace] = []
        try:
            # loop over the JSON array and parse the neuron data to correct types
            for neuron_data in data:
                # add all fields to the namespace as-is
                # only modify the fields that need to be cast and/or adjusted
                neuron = SimpleNamespace( **neuron_data )
                # hotkey and coldkey are strings
                # uid is an int
                # active is an int
                # ip is a string
                # ip_type is an int
                # port is an int
                neuron.stake = int(neuron.stake) / RAOPERTAO
                neuron.rank = int(neuron.rank) / U64MAX
                neuron.emission = int(neuron.emission) / RAOPERTAO
                neuron.incentive = int(neuron.incentive) / U64MAX
                neuron.consensus = int(neuron.consensus) / U64MAX
                neuron.trust = int(neuron.trust) / U64MAX
                neuron.dividends = int(neuron.dividends) / U64MAX
                # modality is an int
                neuron.last_update = int(neuron.last_update)
                # version is an int
                neuron.priority = int(neuron.priority)
                # weights are already ints
                neuron.bonds = [[bond[0], int(bond[1])] for bond in neuron.bonds]

                neuron.is_null = False
                neurons.append( neuron )

        except Exception as e:
            raise FastSyncFormatException('Could not parse metagraph file data: {}'.format(e))
            
        return neurons

    @classmethod
    def _load_neurons_from_historical_metragraph_file_data(cls, file_data: str) -> Dict[str, Dict[str, SimpleNamespace]]:
        """
        Loads neurons from the historical metagraph file data
        See: https://github.com/opentensor/subtensor-api/tree/main/js#neuron-structure
        See: https://github.com/opentensor/subtensor-api/tree/main/js#historical-structure
        
        Raises: FastSyncFormatException if the file is not in the correct format

        Returns: Dict[str(int), Dict[str(int), SimpleNamespace]]
            a Dict of blockNumber to Dict of uid to neuron data
        """
        try:
            data = json.loads(file_data)
        except json.JSONDecodeError:
            raise FastSyncFormatException('Could not parse metagraph file data as json')

        # the top level is a dict
        if not isinstance(data, dict):
            raise FastSyncFormatException('Expected a JSON object at the top level')
        
        historical: Dict[int, Dict[int, SimpleNamespace]] = {}
        try:
            # loop over the JSON object and parse the neuron data to correct types
            for blockNumber, block_data in data.items():
                historical[blockNumber] = {}
                for uid, neuron_data in block_data.items():
                    # add all fields to the namespace as-is
                    # only modify the fields that need to be cast and/or adjusted
                    neuron = SimpleNamespace( **neuron_data )
                    # hotkey and coldkey are strings
                    # uid is an int
                    # active is an int
                    # ip is a string
                    # ip_type is an int
                    # port is an int
                    neuron.stake = int(neuron.stake) / RAOPERTAO
                    neuron.rank = int(neuron.rank) / U64MAX
                    neuron.emission = int(neuron.emission) / RAOPERTAO
                    neuron.incentive = int(neuron.incentive) / U64MAX
                    neuron.consensus = int(neuron.consensus) / U64MAX
                    neuron.trust = int(neuron.trust) / U64MAX
                    neuron.dividends = int(neuron.dividends) / U64MAX
                    # modality is an int
                    neuron.last_update = int(neuron.last_update)
                    # version is an int
                    neuron.priority = int(neuron.priority)
                    # weights are already ints
                    neuron.bonds = [[bond[0], int(bond[1])] for bond in neuron.bonds]

                    neuron.is_null = False
                    
                    historical[blockNumber][uid] = neuron

        except Exception as e:
            raise FastSyncFormatException('Could not parse metagraph file data: {}'.format(e))
            
        return historical

    @classmethod
    def _load_historical_difficulty_file_data(cls, file_data: str) -> Dict[str, Dict[str, SimpleNamespace]]:
        """
        Loads neurons from the historical difficulty file data
        See: https://github.com/opentensor/subtensor-api/tree/main/js#historical-difficulty-structure
        
        Raises: FastSyncFormatException if the file is not in the correct format

        Returns: Dict[str(int), int]
            a Dict of blockNumber to difficulty
        """
        try:
            data = json.loads(file_data)
        except json.JSONDecodeError:
            raise FastSyncFormatException('Could not parse historical difficulty file data as json')

        # the top level is a dict
        if not isinstance(data, dict):
            raise FastSyncFormatException('Expected a JSON object at the top level')
        
        historical: Dict[str(int), int] = {}
        try:
            # loop over the JSON object and parse data
            for blockNumber, difficulty_str in data.items():
                historical[blockNumber] = int(difficulty_str)

        except Exception as e:
            raise FastSyncFormatException('Could not parse historical difficulty file data: {}'.format(e))
            
        return historical

    @classmethod
    def load_historical_difficulty(cls, difficulty_location: Optional[str] = '~/.bittensor/difficulty_historical.json') -> Dict[str, int]:
        """
        Loads neurons from the historical difficulty file

        Args:
            hdifficultylocation (str, optional): The location of the metagraph file. Defaults to '~/.bittensor/difficulty_historical.json'.
        
        Raises:
            FastSyncFileException: If the difficulty file could not be read
            FastSyncFormatException: If the difficulty file is not in the correct format
        
        Returns:
            Dict[str(int), int]:
                a Dict of blockNumber to difficulty
        """
        try:
            with open(os.path.join(os.path.expanduser(difficulty_location))) as f:
                file_data = f.read()
            return cls._load_historical_difficulty_file_data(file_data)
        except FileNotFoundError:
            raise FastSyncFileException('{} not found. Try calling sync_and_save_historical_difficulty() first.', difficulty_location)
        except OSError:
            raise FastSyncFileException('Could not read {}', difficulty_location)

    @classmethod
    def load_historical_neurons(cls, metagraph_location: Optional[str] = '~/.bittensor/metagraph_historical.json') -> Dict[str, Dict[str, SimpleNamespace]]:
        """
        Loads neurons from the historical metagraph file

        Args:
            metagraph_location (str, optional): The location of the metagraph file. Defaults to '~/.bittensor/metagraph_historical.json'.
        
        Raises:
            FastSyncFileException: If the metagraph file could not be read
            FastSyncFormatException: If the metagraph file is not in the correct format
        
        Returns:
            Dict[str(int), Dict[str(int), SimpleNamespace]]:
                a Dict of blockNumber to Dict of uid to neuron data
        """
        try:
            with open(os.path.join(os.path.expanduser(metagraph_location))) as f:
                file_data = f.read()
            return cls._load_neurons_from_historical_metragraph_file_data(file_data)
        except FileNotFoundError:
            raise FastSyncFileException('{} not found. Try calling sync_and_save_historical() first.', metagraph_location)
        except OSError:
            raise FastSyncFileException('Could not read {}', metagraph_location)

    @classmethod
    def load_neurons(cls, metagraph_location: Optional[str] = '~/.bittensor/metagraph.json') -> List[SimpleNamespace]:
        """
        Loads neurons from the metagraph file

        Args:
            metagraph_location (str, optional): The location of the metagraph file. Defaults to '~/.bittensor/metagraph.json'.
        
        Raises:
            FastSyncFileException: If the metagraph file could not be read
            FastSyncFormatException: If the metagraph file is not in the correct format
        
        Returns:
            List[SimpleNamespace]
                a list of the Neurons
        """
        try:
            with open(os.path.join(os.path.expanduser(metagraph_location))) as f:
                file_data = f.read()
            return cls._load_neurons_from_metragraph_file_data(file_data)
        except FileNotFoundError:
            raise FastSyncFileException('{} not found. Try calling sync_and_save() first.', metagraph_location)
        except OSError:
            raise FastSyncFileException('Could not read {}', metagraph_location)
