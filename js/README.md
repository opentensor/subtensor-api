# subtensor-node-api

To build executables for linux and macos, run `yarn run build`  

## Usage
First you build the binary with `yarn build`  
Then, you can run using the binary (replace `{}` with your OS)  
`./subtensor-node-api-{macos,linux} [sync_and_save|get_block_at_registration_for_all_and_save]`  
### sync_and_save
`./subtensor-node-api-{macos,linux} sync_and_save`  
This will pull the latest metagraph/neuron data from the chain and write it to a JSON file  
(default: `~/.bittensor/metagraph.json`) in the [below format](#neuron-structure).  

You can specify the output filename like so:  
`./subtensor-node-api-{macos,linux} sync_and_save --filename <foo.json>`    

You can specify the subtensor endpoint like so:  
`./subtensor-node-api-{macos,linux} sync_and_save --url <wss://examplendpoint:9944>`   

You can specify the blockhash to sync at like so:  
`./subtensor-node-api-{macos,linux} sync_and_save --blockHash <0xsomeblockhash>`     
### get_block_at_registration_for_all_and_save
`./subtensor-node-api-{macos,linux} get_block_at_registration_for_all_and_save`  
This will pull the latest storage map for `blockAtRegistration` for all UIDs from the chain and write it to a JSON file  
(default: `~/.bittensor/blockAtRegistration_all.json`) in the [below format](#blockatregistration-structure).    

You can specify the output filename like so:   
`./subtensor-node-api-{macos,linux} get_block_at_registration_for_all_and_save --filename <foo.json>`    

You can specify the subtensor endpoint like so:  
`./subtensor-node-api-{macos,linux} get_block_at_registration_for_all_and_save -url <wss://examplendpoint:9944>`     

You can specify the blockhash to sync at like so:   
`./subtensor-node-api-{macos,linux} sync_and_save --blockHash <0xsomeblockhash>`      

## Neuron Structure
The NeuronData from `sync_and_save` will be saved into the JSON file as an array with the following types:
     
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
      
## blockAtRegistration Structure
The blockAtRegistration data saved to the JSON file will be a JSON array of integers represented as strings, in the order of their UIDs:  
  
    [
       str(int),
       str(int),
       ...,
       str(int)
    ]
