const {getNeurons, sync, blockAtRegistration, get_block_at_registration_for_all} = require("../main");
const {expect} = require("chai");

describe("Test Neurons are pulled", function() {
        const mock_n = 1024;

        const get_mock_api = (n_neurons) => {
            return {
                query: {
                    subtensorModule: {
                        neurons: {
                            multi: function(params) {
                                return new Promise(function(resolve, reject) {
                                    resolve(params); // needs to return an array of the same length. Just return params
                                });
                            }
                        },
                        n: function() {
                            return new Promise(function(resolve, reject) {
                                resolve({words: [n_neurons]}); // needs to return a number
                            });
                        }
                    }
                },
                isReady: new Promise(function(resolve, reject) {
                    resolve(true);
                }),
                rpc: {
                    chain: {
                        getBlockHash: function() {
                            return new Promise(function(resolve, reject) {
                                resolve("0x1631466c080fe9ca1e093b080352bd287b727505c5f15572aaae1e82cea2970a");
                            });
                        }
                    }
                },
                at: function(blockHash) {
                    return new Promise(function(resolve, reject) {
                        resolve(get_mock_api(n_neurons));
                    });
                }
            }
        }

        const mock_get_api_from_url = (url) => {
            return get_mock_api(mock_n);
        }

        const mock_parse_neuron_data = (result, page, pageSize) => {
            return result.map(
                (result, j) => {
                    return j;
                }
            )
        };

        it("should pull all neurons in page", async function() {
            const neurons = await getNeurons(get_mock_api(mock_n), 0, 10);
            expect(neurons).to.have.lengthOf(10);
        });

        it("should pull all n neurons", async function() {
            const neurons = await sync("wss://mock_url:9944", mock_get_api_from_url, mock_parse_neuron_data)
            expect(neurons).to.have.lengthOf(mock_n);
        });

        it("should pull all n neurons when n is not evenly divisible", async function() {
            const mock_get_api_from_url_ = (url) => {
                return get_mock_api(mock_n + 1);
            }
            const neurons = await sync("wss://mock_url:9944", mock_get_api_from_url_, mock_parse_neuron_data)
            expect(neurons).to.have.lengthOf(mock_n + 1);
        });
    }
)

describe("Test blockAtRegistration are pulled", function() {
    const mock_n = 1024;

    const get_mock_api = (n_neurons) => {
        return {
            query: {
                subtensorModule: {
                    blockAtRegistration: {
                        multi: function(params) {
                            return new Promise(function(resolve, reject) {
                                resolve(params); // needs to return an array of the same length. Just return params
                            });
                        }
                    },
                    n: function() {
                        return new Promise(function(resolve, reject) {
                            resolve({words: [n_neurons]}); // needs to return a number
                        });
                    }
                }
            },
            isReady: new Promise(function(resolve, reject) {
                resolve(true);
            }),
            rpc: {
                chain: {
                    getBlockHash: function() {
                        return new Promise(function(resolve, reject) {
                            resolve("0x1631466c080fe9ca1e093b080352bd287b727505c5f15572aaae1e82cea2970a");
                        });
                    }
                }
            },
            at: function(blockHash) {
                return new Promise(function(resolve, reject) {
                    resolve(get_mock_api(n_neurons));
                });
            }
        }
    }

    const mock_get_api_from_url = (url) => {
        return get_mock_api(mock_n);
    }

    it("should pull all storageValues in page", async function() {
        const blockAtRegistration_ = await blockAtRegistration(get_mock_api(mock_n), 0, 10);
        expect(blockAtRegistration_).to.have.lengthOf(10);
    });

    it("should pull all n blockAtRegistration", async function() {
        const blockAtRegistration_ = await get_block_at_registration_for_all("wss://mock_url:9944", mock_get_api_from_url)
        expect(blockAtRegistration_).to.have.lengthOf(mock_n);
    });

    it("should pull all n blockAtRegistration when n is not evenly divisible", async function() {
        let mock_get_api_from_url_ = (url) => {
            return get_mock_api(mock_n + 1);
        }
        const blockAtRegistration_ = await get_block_at_registration_for_all("wss://mock_url:9944", mock_get_api_from_url_)
        expect(blockAtRegistration_).to.have.lengthOf(mock_n + 1);
    });
}
)