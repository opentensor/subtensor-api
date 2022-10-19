 const {sync_and_save, get_block_at_registration_for_all_and_save} = require('./main.js');

require('yargs')
  .scriptName("subtensor-api")
  .usage('$0 <cmd> [args]')
  .command('sync_and_save', 'Subtensor API Wrapper v1.1.0', (yargs) => {
    yargs.options({
      'filename': {
        alias: 'f',
        type: 'string',
        default: '~/.bittensor/metagraph.json',
        describe: 'the filename to save the metagraph to',
        demandOption: false,
      },
      'url': {
        alias: 'u',
        type: 'string',
        default: 'ws://AtreusLB-2c6154f73e6429a9.elb.us-east-2.amazonaws.com:9944',
        describe: 'the url of the substrate node to sync from',
        demandOption: false,
      },
      'blockHash': {
        alias: 'b',
        type: 'string',
        default: 'latest',
        describe: 'the block hash to sync at',
        demandOption: false,
      },
    })
  }, function (argv) {
    return sync_and_save(
      argv.url,
      argv.filename,
      argv.blockHash === 'latest' ? undefined : argv.blockHash, // If latest, then call using undefined.
      ).then(() => {
      console.log(`Done metagraph sync for Block:${argv.blockHash}, wrote to file: ${argv.filename}`);
      process.exit(0);
    }).catch(err => {
      console.log(err);
      process.exit(1);
    });
  })
  .command('get_block_at_registration_for_all_and_save', 'Subtensor API Wrapper v1.1.0', (yargs) => {
    yargs.options({
      'filename': {
        alias: 'f',
        type: 'string',
        default: '~/.bittensor/blockAtRegistration_all.json',
        describe: 'the filename to save the data to',
        demandOption: false,
      },
      'url': {
        alias: 'u',
        type: 'string',
        default: 'ws://AtreusLB-2c6154f73e6429a9.elb.us-east-2.amazonaws.com:9944',
        describe: 'the url of the substrate node to sync from',
        demandOption: false,
      },
      'blockHash': {
        alias: 'b',
        type: 'string',
        default: 'latest',
        describe: 'the block hash to sync at',
        demandOption: false,
      },
    })
  }, function (argv) {
    return get_block_at_registration_for_all_and_save(
      argv.url,
      argv.filename,
      argv.blockHash === 'latest' ? undefined : argv.blockHash, // If latest, then call using undefined.
      ).then(() => {
      console.log(`Done blockAtRegistration for all for Block:${argv.blockHash}, wrote to file: ${argv.filename}`);
      process.exit(0);
    }).catch(err => {
      console.log(err);
      process.exit(1);
    });
  })
  .help()
  .argv