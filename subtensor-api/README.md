# Subtensor API Python package
A python wrapper around the `@polkadot/api` node library to query the bittensor chain.
# Install from pypi
`pip install subtensorapi==1.0.0`  
# Running the CLI
## Usage
View usage  
`python3 -m subtensorapi --help`   
   
Specify chain endpoint url  
`python3 -m subtensorapi [sync_and_save|blockAtReg_and_save] --endpoint_url ENDPOINT_URL`     
Specify filename to save to
`python3 -m subtensorapi [sync_and_save|blockAtReg_and_save] --filename FILENAME.json`  
Specify blockhash to sync the chain at, default "latest"
`python3 -m subtensorapi [sync_and_save|blockAtReg_and_save] --block_hash BLOCK_HASH`  
### Sync And Save Metagraph
Pulls the `neurons` storage map and saves it to a JSON file.  
View usage  
`python3 -m subtensorapi sync_and_save --help`     
Run sync of metagraph and save to JSON file  
`python3 -m subtensorapi sync_and_save`      

### Grab blockAtRegistration
Pulls the `blockAtRegistration` storage map and saves it to a JSON file.  
View usage
`python3 -m subtensorapi blockAtReg_and_save --help`

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