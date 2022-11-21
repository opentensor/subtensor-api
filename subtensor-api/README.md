# Subtensor API Python package
A python wrapper around the `@polkadot/api` node library to query the bittensor chain.
# Install from pypi
`pip install subtensorapi==1.1.0`  
# Running the CLI
## Usage
View usage  
`python3 -m subtensorapi --help`   
   
Specify chain endpoint url  
`python3 -m subtensorapi [sync_and_save|blockAtReg_and_save|sync_and_save_historical|sync_and_save_historical_difficulty] --endpoint_url ENDPOINT_URL`     
Specify filename to save to
`python3 -m subtensorapi [sync_and_save|blockAtReg_and_save|sync_and_save_historical|sync_and_save_historical_difficulty] --filename FILENAME.json`  
Specify blockhash to sync the chain at, default "latest"
`python3 -m subtensorapi [sync_and_save|blockAtReg_and_save|sync_and_save_historical|sync_and_save_historical_difficulty] --block_hash BLOCK_HASH`  
### Sync And Save Metagraph
Pulls the `neurons` storage map and saves it to a JSON file.  
View usage  
`python3 -m subtensorapi sync_and_save --help`     
Run sync of metagraph and save to JSON file  
`python3 -m subtensorapi sync_and_save -f metagraph.json`      

### Sync And Save Neurons from Metagraph at historical blocks
Pulls the `neurons` storage map at each block for each UID and saves it to a JSON file.  
View usage  
`python3 -m subtensorapi sync_and_save_historical --help`     
Run sync of metagraph at blocks `2706651 2706652 2706653` and UIDs `1 2 3` and save to JSON file    
`python3 -m subtensorapi sync_and_save_historical -i 1 2 3 -b 2706651 2706652 2706653 -f history.json`      

### Grab blockAtRegistration
Pulls the `blockAtRegistration` storage map and saves it to a JSON file.  
View usage
`python3 -m subtensorapi blockAtReg_and_save --help`

### Sync And Save Difficulty at historical blocks
Pulls the `difficulty` storage value at each block and saves it to a JSON file.  
View usage  
`python3 -m subtensorapi sync_and_save_historical_difficulty --help`     
Run sync of metagraph at blocks `2706651 2706652 2706653` and save to JSON file    
`python3 -m subtensorapi sync_and_save_historical_difficulty -b 2706651 2706652 2706653 -f history_diff.json`    

# Using the library
## FastSync class
Setup of a FastSync instance
```python
from subtensorapi import FastSync

# check if fast sync is available on the platform
FastSync.verify_fast_sync_support() 

# specify the chain endpoint_url  
fast_sync: FastSync = FastSync(endpoint_url)
```  
### Run the metagraph sync  
Pulls the `neurons` storage map.  
```python
# specify block_hash to sync at. Default is "latest"
block_hash = "0xb2fa081[...]"
# run the sync command and save to JSON file at block_hash
fast_sync.sync_and_save(block_hash)
# load neurons in from JSON file
neurons = fast_sync.load_neurons()
```

### Run the historical metagraph sync 
Pulls the `neurons` storage map for each block and each UID
```python
# specify blockNumbers to sync at. Default is "latest"
blockNumbers = ["latest", 2706652]
# specify UIDs to sync
UIDs = [1, 2, 3, 4095]
# run the sync command and save to JSON file at block_hash
fast_sync.sync_and_save_historical(blockNumbers, UIDs)
# load neurons in from JSON file
historical_neurons = fast_sync.load_historical_neurons()
```

### Run the historical difficulty sync 
Pulls the `difficulty` storage value for each block
```python
# specify blockNumbers to sync at. Default is "latest"
blockNumbers = ["latest", 2706652]
# run the sync command and save to JSON file at block_hash
fast_sync.sync_and_save_historical_difficulty(blockNumbers)
# load neurons in from JSON file
historical_diff = fast_sync.load_historical_difficulty()
```

### Run blockAtRegistration pull
Pulls the `blockAtRegistration` storage map.  
```python
# specify block_hash to sync at. Default is "latest"
block_hash = "0xb2fa081[...]"
# run the pull command and save to JSON file at block_hash
fast_sync.get_blockAtRegistration_for_all_and_save(block_hash)
# load blockAtRegistration_all from JSON file
blockAtRegistration_all = fast_sync.load_blockAtRegistration_for_all()
```

## Using the FastSync class without writing to a file
You can redirect the file writing to a pipe instead of a file.  
This removes the need to write to disk and provides a speedup.  

Example: 
```python
# all neurons
all_neurons: List[SimpleNamespace] = fast_sync.sync_fd(block_hash)
# historical neurons
historical_neurons: Dict[str, Dict[str, SimpleNamespace]] = fast_sync.sync_historical_fd(blockNumbers, UIDs)
# blockAtRegistration_all
blockAtRegistration_all: List[int] = fast_sync.get_blockAtRegistration_for_all_fd(block_hash)
# historical difficulty
historical_diff: Dict[str, int] = fast_sync.sync_historical_difficulty_fd(blockNumbers)
```