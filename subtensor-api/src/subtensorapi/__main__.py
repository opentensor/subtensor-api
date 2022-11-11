import argparse
import sys
from typing import List, Optional

from . import cli, __version__


def main(args: Optional[List[str]] = sys.argv[1:]) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="version", version=__version__)

    cmd_parsers = parser.add_subparsers(dest="command")

    sync_and_save = cmd_parsers.add_parser("sync_and_save")
    cli.add_args_sync_and_save(sync_and_save)

    blockAtRegistration_for_all_and_save = cmd_parsers.add_parser(
        "blockAtReg_and_save"
    )
    cli.add_args_blockAtRegistration_for_all_and_save(
        blockAtRegistration_for_all_and_save
    )

    sync_and_save_historical = cmd_parsers.add_parser(
        "sync_and_save_historical"
    )
    cli.add_args_sync_and_save_historical(
        sync_and_save_historical
    )

    parsed_args = parser.parse_args(args)

    if parsed_args.command == "sync_and_save":
        cli.sync_and_save(parsed_args)
    elif parsed_args.command == "blockAtReg_and_save":
        cli.blockAtRegistration_for_all_and_save(parsed_args)
    elif parsed_args.command == "sync_and_save_historical":
        cli.sync_and_save_historical(parsed_args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main(sys.argv[1:])
