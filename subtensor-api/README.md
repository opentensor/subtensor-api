# Subtensor API Python package
A python wrapper around the `@polkadot/api` node library to query the bittensor chain.
# Install from pypi
`pip install subtensorapi==0.1.2`  
# Running the CLI
## Usage
View usage  
`python3 -m subtensorapi --help`   
   
Specify chain endpoint url  
`python3 -m subtensorapi [sync_and_save|blockAtReg_and_save] --endpoint_url ENDPOINT_URL`     
Specify filename to save to
`python3 -m subtensorapi [sync_and_save|blockAtReg_and_save] --filename FILENAME.json`  
Specify blockhash to sync the chain at
`python3 -m subtensorapi [sync_and_save|blockAtReg_and_save] --block_hash BLOCK_HASH`  
### Sync And Save Metagraph
Pulls the `neurons` storage map and saves it to a JSON file.  
View usage  
`python3 -m subtensorapi sync_and_save --help`     
Run sync of metagraph and save to JSON file  
`python3 -m subtensorapi sync_and_save`      

### Grab blockAtRegistration
Pulls the storage map of `blockAtRegistration` and saves it to a JSON file  
View usage
`python3 -m subtensorapi blockAtReg_and_save --help`