# subtensor-node-api

To build executables for linux and macos, run `yarn run build`  

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
      
