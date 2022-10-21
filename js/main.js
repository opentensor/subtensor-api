const { ApiPromise } = require("@polkadot/api/promise/Api");
const { WsProvider } = require("@polkadot/rpc-provider/ws");
const path = require('path');
const fs = require('fs');
const os = require("os");

function get_provider_from_url(url) {
    const provider = new WsProvider(url);
    return provider;
}

function get_api_from_url(url) {
    const provider = get_provider_from_url(url);
    const api = new ApiPromise({
        provider
    });
    return api;
}

async function sync(url, get_api_from_url, parseNeuronData, blockHash=undefined) {
    let api = get_api_from_url(url);

    // Wait for the API to be connected to the node
    try {
        await api.isReady;
    } catch (err) {
        console.log(err);
        return;
    }

    if (!!!blockHash) {
        try {
            blockHash = await api.rpc.chain.getBlockHash();
        } catch (err) {
            console.log(err);
            return;
        }
    }
    api = await api.at(blockHash);
    
    const neurons = await refreshMeta(api, parseNeuronData);
    return neurons;
}

async function getNeurons(api, page, pageSize) {
    return new Promise((resolve, reject) => {
      const indexStart = page * pageSize;
      (api.query.subtensorModule.neurons.multi(
        Array.from(new Array(pageSize), (_, i) => i + indexStart)
      ))
      .then(resolve)
      .catch(err => {
        console.log(err)
        reject(err);
      });
    })
};

function parseNeuronData(result) {
    let neurons = result.map((result, j) => {
        const indexStart = page * pageSize;
        const neuron = result.value;
        console.log(indexStart + j);
        return {
            hotkey: (neuron.hotkey).toString(),
            coldkey: (neuron.coldkey).toString(),
            stake: BigInt(neuron.stake).toString(),
            dividends: BigInt(neuron.dividends).toString(),
            emission: BigInt(neuron.emission).toString(),
            incentive: BigInt(neuron.incentive).toString(),
            trust: BigInt(neuron.trust).toString(),
            rank: BigInt(neuron.rank).toString(),
            consensus: BigInt(neuron.consensus).toString(),
            last_update: BigInt(neuron.lastUpdate).toString(),
            priority: BigInt(neuron.priority).toString(),
            version: (neuron.version).toNumber(),
            modality: (neuron.modality).toNumber(),
            active: (neuron.active).toNumber(),
            ip: (neuron.ip).toString(),
            ip_type: (neuron.ipType).toNumber(),
            port: (neuron.port).toNumber(),
            uid: j + indexStart,
            bonds: neuron.bonds.map(bond => {
                return [
                    (bond[0]).toNumber(),
                    BigInt(bond[1]).toString()
                ]
            }),
            weights: neuron.weights.map(weight => {
                return [
                    (weight[0]).toNumber(),
                    (weight[1]).toNumber()
                ]
            })
        };
    });
    return neurons;
}

async function refreshMeta(api, parseNeuronData) {
    const numNeurons = ((await api.query.subtensorModule.n())).words[0];

    let _neurons = [];
    const numPages = 16;
    let pageSize = Math.ceil(numNeurons / numPages);
    const last_page_length = numNeurons % pageSize;
    for (let page = 0; page < numPages; page++) {
        if (page === numPages - 1) {
            // if last page, use the last_page_length
            if (last_page_length > 0) {
                // if last_page_length is 0, then the last page is a full page
                pageSize = last_page_length; 
            }
        }
        const result = await getNeurons(api, page, pageSize)
    let neurons_ = parseNeuronData(result);
    
    _neurons = _neurons.concat(neurons_);
    }
    return _neurons;
}

async function sync_and_save(url, filename, blockHash=undefined) {
    const neurons = await sync(url, get_api_from_url, parseNeuronData, blockHash);
    const neurons_json = JSON.stringify(neurons);
    
    fs.writeFileSync(path.resolve(filename.replace('~', os.homedir())), neurons_json);
    return neurons;
}

async function blockAtRegistration(api, page, pageSize) {
    return new Promise((resolve, reject) => {
        const indexStart = page * pageSize;
        (api.query.subtensorModule.blockAtRegistration.multi(
          Array.from(new Array(pageSize), (_, i) => i + indexStart)
        ))
        .then(resolve)
        .catch(err => {
          console.log(err)
          reject(err);
        });
      })
}

async function get_block_at_registration(api) {
    const numNeurons = ((await api.query.subtensorModule.n())).words[0];

    let _blockAtRegistrationAll = [];
    const numPages = 16;
    let pageSize = Math.ceil(numNeurons / numPages);
    const last_page_length = numNeurons % pageSize;
    for (let page = 0; page < numPages; page++) {
        if (page === numPages - 1) {
            // if last page, use the last_page_length
            if (last_page_length > 0) {
                // if last_page_length is 0, then the last page is a full page
                pageSize = last_page_length; 
            }
        }
        const result = await blockAtRegistration(api, page, pageSize)
    let blockAtRegistrationAll_ = result.map((result, j) => {
        return BigInt(result).toString(); // block number are u64 so we need to convert to string for JSON
    });
    _blockAtRegistrationAll = _blockAtRegistrationAll.concat(blockAtRegistrationAll_);
    }
    return _blockAtRegistrationAll;
}

async function get_block_at_registration_for_all(url, get_api_from_url, blockHash=undefined) {
    let api = get_api_from_url(url);

    // Wait for the API to be connected to the node
    try {
        await api.isReady;
    } catch (err) {
        console.log(err);
        return;
    }

    if (!!!blockHash) {
        try {
            blockHash = await api.rpc.chain.getBlockHash();
        } catch (err) {
            console.log(err);
            return;
        }
    }
    api = await api.at(blockHash);
    
    const block_at_registration_all = await get_block_at_registration(api);
    return block_at_registration_all;
}

async function get_block_at_registration_for_all_and_save(url, filename, blockHash=undefined) {
    const block_at_registration_all = await get_block_at_registration_for_all(url, get_api_from_url, blockHash);
    const block_at_registration_json = JSON.stringify(block_at_registration_all);
    
    fs.writeFileSync(path.resolve(filename.replace('~', os.homedir())), block_at_registration_json);
    return block_at_registration_all;
}

module.exports = {
    // for cli
    sync_and_save, get_block_at_registration_for_all_and_save,
    // for testing
    getNeurons,
    blockAtRegistration,
    get_block_at_registration_for_all,
    sync,
};
