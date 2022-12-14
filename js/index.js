const {sync_and_save, get_block_at_registration_for_all_and_save, sync_and_save_historical, sync_and_save_historical_difficulty} = require('./main.js');

const VERSION = 'v1.7.0'

require('yargs')
  .scriptName("subtensor-api")
  .usage('$0 <cmd> [args]')
  .command('sync_and_save', `Subtensor API Wrapper ${VERSION}`, (yargs) => {
    yargs.options({
      'filename': {
        alias: 'f',
        type: 'string',
        default: '~/.bittensor/metagraph.json',
        describe: 'the filename to save the metagraph to',
        demandOption: false,
      },
      'fd': {
        alias: 'p',
        type: 'number',
        default: undefined,
        describe: 'the fd to pipe the metagraph to',
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
      argv.fd,
      ).then(() => {
      console.log(`Done metagraph sync for Block:${argv.blockHash}, wrote to file: ${argv.filename}`);
      process.exit(0);
    }).catch(err => {
      console.log(err);
      process.exit(1);
    });
  })
  .command('sync_and_save_historical', `Subtensor API Wrapper ${VERSION}`, (yargs) => {
    yargs.options({
      'filename': {
        alias: 'f',
        type: 'string',
        default: '~/.bittensor/metagraph_historical.json',
        describe: 'the filename to save the metagraph to',
        demandOption: false,
      },
      'fd': {
        alias: 'p',
        type: 'number',
        default: undefined,
        describe: 'the fd to pipe the metagraph to',
        demandOption: false,
      },
      'url': {
        alias: 'u',
        type: 'string',
        default: 'ws://AtreusLB-2c6154f73e6429a9.elb.us-east-2.amazonaws.com:9944',
        describe: 'the url of the substrate node to sync from',
        demandOption: false,
      },
      'blockNumbers': {
        alias: 'b',
        type: 'array',
        default: ['latest'],
        describe: 'the block number(s) to sync at',
        demandOption: false,
      },
      'uids': {
        alias: 'i',
        type: 'array',
        default: [],
        describe: 'the uid(s) to sync',
        demandOption: false,
      },
    })
  }, function (argv) {
    return sync_and_save_historical(
      argv.url,
      argv.filename,
      argv.blockNumbers,
      argv.uids,
      argv.fd,
      ).then(() => {
      if (argv.fd) {
        console.log(`Done metagraph sync for Block(s):${argv.blockNumbers} and UID(s):${argv.uids}, wrote to fd: ${argv.fd}`);
      } else {
        console.log(`Done metagraph sync for Block(s):${argv.blockNumbers} and UID(s):${argv.uids}, wrote to file: ${argv.filename}`);
      }
      process.exit(0);
    }).catch(err => {
      console.log(err);
      process.exit(1);
    });
  })
  .command('sync_and_save_historical_difficulty', `Subtensor API Wrapper ${VERSION}`, (yargs) => {
    yargs.options({
      'filename': {
        alias: 'f',
        type: 'string',
        default: '~/.bittensor/difficulty_historical.json',
        describe: 'the filename to save the difficulty data to',
        demandOption: false,
      },
      'fd': {
        alias: 'p',
        type: 'number',
        default: undefined,
        describe: 'the fd to pipe the difficulty data to',
        demandOption: false,
      },
      'url': {
        alias: 'u',
        type: 'string',
        default: 'ws://AtreusLB-2c6154f73e6429a9.elb.us-east-2.amazonaws.com:9944',
        describe: 'the url of the substrate node to sync from',
        demandOption: false,
      },
      'blockNumbers': {
        alias: 'b',
        type: 'array',
        default: ['latest'],
        describe: 'the block number(s) to sync at',
        demandOption: false,
      },
    })
  }, function (argv) {
    return sync_and_save_historical_difficulty(
      argv.url,
      argv.filename,
      argv.blockNumbers,
      argv.fd,
      ).then(() => {
      if (argv.fd) {
        console.log(`Done difficulty sync for Block(s):${argv.blockNumbers}, wrote to fd: ${argv.fd}`);
      } else {
        console.log(`Done difficulty sync for Block(s):${argv.blockNumbers}, wrote to file: ${argv.filename}`);
      }
      process.exit(0);
    }).catch(err => {
      console.log(err);
      process.exit(1);
    });
  })
  .command('block_at_reg_and_save', `Subtensor API Wrapper ${VERSION}`, (yargs) => {
    yargs.options({
      'filename': {
        alias: 'f',
        type: 'string',
        default: '~/.bittensor/blockAtRegistration_all.json',
        describe: 'the filename to save the data to',
        demandOption: false,
      },
      'fd': {
        alias: 'p',
        type: 'number',
        default: undefined,
        describe: 'the fd to pipe the metagraph to',
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
      argv.fd,
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