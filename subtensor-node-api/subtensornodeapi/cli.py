import sys
import click

from interface import verify_binary_exists, run_sync_and_save

@click.command()
def test():
    """Test package"""
    verify_binary_exists()
    run_sync_and_save(sys.argv[1]) # pass file name


@click.group()
def subtensornodeapi():
    pass

googledrive.add_command(test)
