import sys
import click

from subtensornodeapi.interface import verify_binary_exists, run_sync_and_save

@click.command()
@click.argument('path')
def test(path):
    """Test package"""
    verify_binary_exists()
    run_sync_and_save(path) # pass file name


@click.group()
def subtensornodeapi():
    pass

subtensornodeapi.add_command(test)
