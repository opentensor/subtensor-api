const { ApiPromise } = require("@polkadot/api/promise/Api");
const { WsProvider } = require("@polkadot/rpc-provider/ws");
const path = require('path');
const fs = require('fs');
const os = require("os");

function get_provider_from_url(url) {
    const provider = new WsProvider(url, false); // false means no auto reconnect
    return provider;
}

function get_api_from_url(url) {
    const provider = get_provider_from_url(url);
    const api = new ApiPromise({
        provider
    });
    return api;
}

async function sync_historical(url, get_api_from_url, parseNeuronData, blockNumbers=[undefined], uids=[]) {
    // get neuron info at each block for one or more uids
    let api = get_api_from_url(url);

    // Wait for the API to be connected to the node
    try {
        await api.connect();
        await api.isReady;
    } catch (err) {
        console.log(err);
        return;
    }

    const historical_metagraph  = {
        
    }
    for (let i = 0; i < blockNumbers.length; i++) {
        let blockNumber = blockNumbers[i];
        let blockHash;
        if (!!!blockNumber || blockNumber === "latest") {
            try {
                const block = await api.rpc.chain.getBlock(); // latest block
                blockHash = block.block.header.hash;
                blockNumber = block.block.header.number;
            } catch (err) {
                console.log(err);
                return;
            }
        } else {
            blockHash = await api.rpc.chain.getBlockHash(blockNumber);
        }

        const api_at_block = await api.at(blockHash);
        
        let uids_to_query = uids;

        if (uids.length === 0) {
            // get all uids
            const n = (await api_at_block.query.subtensorModule.n()).words[0];
            uids_to_query = Array.from(Array(n).keys());
        }
    
        const neurons = await api_at_block.query.subtensorModule.neurons.multi(uids_to_query)
        const parsedNeurons = parseNeuronData(neurons.map(neuron => neuron.value));
        historical_metagraph[blockNumber] = Object.fromEntries(parsedNeurons.map(neuron => [neuron.uid, neuron]));
    }

    return historical_metagraph;
}

async function sync(url, get_api_from_url, parseNeuronData, blockHash=undefined) {
    let api = get_api_from_url(url);

    // Wait for the API to be connected to the node
    try {
        await api.connect();
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
    
    const neurons_unordered = await refreshMeta(api, parseNeuronData);
    const neurons = neurons_unordered.sort((a, b) => a.uid - b.uid);
    return neurons;
}

function parseNeuronData( neuron_data ) {
    let neurons = neuron_data.map((neuron, j) => {
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
            uid: (neuron.uid).toNumber(),
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
    const neuron_entries = await api.query.subtensorModule.neurons.entries();
    const neurons_unordered = parseNeuronData(neuron_entries.map(entry => entry[1].value));
    return neurons_unordered;
}

async function difficulty_historical(url, get_api_from_url, blockNumbers=[undefined]) {
    let api = get_api_from_url(url);

    // Wait for the API to be connected to the node
    try {
        await api.connect();
        await api.isReady;
    } catch (err) {
        console.log(err);
        return;
    }

    const historical_difficulty  = {
        
    }

    for (let i = 0; i < blockNumbers.length; i++) {
        let blockNumber = blockNumbers[i];
        let blockHash;
        if (!!!blockNumber || blockNumber === "latest") {
            try {
                const block = await api.rpc.chain.getBlock(); // latest block
                blockHash = block.block.header.hash;
                blockNumber = block.block.header.number;
            } catch (err) {
                console.log(err);
                return;
            }
        } else {
            blockHash = await api.rpc.chain.getBlockHash(blockNumber);
        }

        const api_at_block = await api.at(blockHash);

        const difficulty = BigInt(await api_at_block.query.subtensorModule.difficulty()).toString();
        historical_difficulty[blockNumber] = difficulty;
    }

    return historical_difficulty;
}

async function sync_and_save_historical_difficulty(url, filename, blockNumbers=[undefined], fd=undefined) {
    console.time("difficulty_historical");
    const neurons = await difficulty_historical(url, get_api_from_url, blockNumbers);
    const neurons_json = JSON.stringify(neurons);
    console.timeEnd("difficulty_historical");

    if (!!fd) {
        fs.writeFileSync(fd, neurons_json);
    } else {
        fs.writeFileSync(path.resolve(filename.replace('~', os.homedir())), neurons_json);
    }
    return neurons;
}

async function sync_and_save(url, filename, blockHash=undefined, fd=undefined) {
    console.time("sync");
    const neurons = await sync(url, get_api_from_url, parseNeuronData, blockHash);
    const neurons_json = JSON.stringify(neurons);
    console.timeEnd("sync");

    if (fd) {
        fs.writeFileSync(fd, neurons_json);
    } else {
        fs.writeFileSync(path.resolve(filename.replace('~', os.homedir())), neurons_json);
    }
    return neurons;
}

async function sync_and_save_historical(url, filename, blockNumbers=[undefined], uids=[], fd=undefined) {
    console.time("sync_historical");
    const neurons = await sync_historical(url, get_api_from_url, parseNeuronData, blockNumbers, uids);
    const neurons_json = JSON.stringify(neurons);
    console.timeEnd("sync_historical");

    if (!!fd) {
        fs.writeFileSync(fd, neurons_json);
    } else {
        fs.writeFileSync(path.resolve(filename.replace('~', os.homedir())), neurons_json);
    }
    return neurons;
}

async function get_block_at_registration(api) {
    const n = (await api.query.subtensorModule.n()).words[0];
    const result = await api.query.subtensorModule.blockAtRegistration.multi(Array.from(Array(n).keys()))
    const blockAtRegistrationAll_parsed = result.map((result, j) => {
        try {
            return BigInt(result).toString();  // block number are u64 so we need to convert to string for JSON
        } catch (err) {
            console.log("Error parsing blockAtRegistration for neuron " + j);
            throw err;
        }
    });
    return blockAtRegistrationAll_parsed;
}

async function get_block_at_registration_for_all(url, get_api_from_url, blockHash=undefined) {
    let api = get_api_from_url(url);

    // Wait for the API to be connected to the node
    try {
        await api.connect();
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

async function get_block_at_registration_for_all_and_save(url, filename, blockHash=undefined, fd=undefined) {
    const block_at_registration_all = await get_block_at_registration_for_all(url, get_api_from_url, blockHash);
    const block_at_registration_json = JSON.stringify(block_at_registration_all);
    
    if (!!fd) {
        fs.writeFileSync(fd, block_at_registration_json);
    } else {
        fs.writeFileSync(path.resolve(filename.replace('~', os.homedir())), block_at_registration_json);
    }
    return block_at_registration_all;
}

module.exports = {
    // for cli
    sync_and_save, get_block_at_registration_for_all_and_save, sync_and_save_historical, sync_and_save_historical_difficulty,
    // for testing
    get_block_at_registration_for_all,
    sync,
};
