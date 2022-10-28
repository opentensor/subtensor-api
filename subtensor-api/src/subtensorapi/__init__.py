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

__version__ = "0.1.2"

import enum
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from types import SimpleNamespace
from typing import List, Optional
from .exceptions import *

from tqdm import tqdm
from rich.console import Console

RAOPERTAO: int = 10e9
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

    def sync_and_save(self, console: Console, block_hash: str, filename: Optional[str] = None) -> None:
        """Runs the fast sync binary to sync all neurons at a given block hash"""
        FastSync.verify_fast_sync_support()
        path_to_bin = FastSync.get_path_to_fast_sync()
        console.print("Using subtensor-node-api for neuron retrieval...")
        args = [path_to_bin, "sync_and_save", "-u", self.endpoint_url, '-b', block_hash]
        if filename is not None:
            args.extend(['-f', filename])
        # will write to ~/.bittensor/metagraph.json by default
        try:
            subprocess.run(args, check=True, stdout=subprocess.PIPE)
        except subprocess.SubprocessError as e:
            raise FastSyncRuntimeException("Error running fast sync binary: {}".format(e))

    def get_blockAtRegistration_for_all_and_save(self, console: Console, block_hash: str, filename: Optional[str] = None) -> None:
        """Runs the fast sync binary to get blockAtRegistration for all neurons at a given block hash"""
        FastSync.verify_fast_sync_support()
        path_to_bin = FastSync.get_path_to_fast_sync()
        console.print("Using subtensor-node-api for blockAtRegistration storage retrieval...")
        args = [path_to_bin, "block_at_reg_and_save", "-u", self.endpoint_url, '-b', block_hash]
        if filename is not None:
            args.extend(['-f', filename])
        # will write to ~/.bittensor/blockAtRegistration_all.json by default
        try:
            subprocess.run(args, check=True, stdout=subprocess.PIPE)
        except subprocess.SubprocessError as e:
            raise FastSyncRuntimeException("Error running fast sync binary: {}".format(e))

    @classmethod
    def load_blockAtRegistration_for_all(cls, json_file_location: Optional[str] = '~/.bittensor/blockAtRegistration_all.json') -> List[int]:
        """
        Loads neurons from the blockAtRegistration JSON file

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
                int(blockAtRegistration) for blockAtRegistration in tqdm(data, "Parsing blockAtRegistration_all data")
            ]
        except Exception as e:
            raise FastSyncFormatException('Could not parse blockAtRegistration JSON file data: {}'.format(e))
            
        return blockAtRegistration_all

    @classmethod
    def _load_neurons_from_metragraph_file_data(cls, file_data: str) -> List[SimpleNamespace]:
        """
        Loads neurons from the metagraph file data
        See: https://github.com/opentensor/subtensor-api#neuron-structure
        
        Raises: FastSyncFormatException if the file is not in the correct format

        Returns: List[SimpleNamespace]
            a list of the Neurons
        """
        try:
            data = json.loads(file_data)
        except json.JSONDecodeError:
            raise FastSyncFormatException('Could not parse metagraph file data as json')

        # all the large ints are strings
        if not isinstance(data, list):
            raise FastSyncFormatException('Expected a JSON array at the top level')
        
        neurons: List[SimpleNamespace] = []
        try:
            # loop over the JSON array and parse the neuron data to correct types
            for neuron_data in tqdm(data, "Parsing Neuron Data"):
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
            raise FastSyncFileException('{} not found. Try calling fast_sync_neurons() first.', metagraph_location)
        except OSError:
            raise FastSyncFileException('Could not read {}', metagraph_location)
