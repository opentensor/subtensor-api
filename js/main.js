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
    
    const neurons = await refreshMeta(api, parseNeuronData);
    return neurons;
}

function parseNeuronData( neuron_data ) {
    let neurons = neuron_data.map((result, j) => {
        const neuron = result[1].value;
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
            uid: j,
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
    const neurons = parseNeuronData(neuron_entries);
    return neurons
}

async function sync_and_save(url, filename, blockHash=undefined) {
    console.time("sync");
    const neurons = await sync(url, get_api_from_url, parseNeuronData, blockHash);
    const neurons_json = JSON.stringify(neurons);
    console.timeEnd("sync");
    
    fs.writeFileSync(path.resolve(filename.replace('~', os.homedir())), neurons_json);
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
    get_block_at_registration_for_all,
    sync,
};
