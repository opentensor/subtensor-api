import os
import sys
import subprocess


def verify_binary_exists() -> None:
    """
    Verifies that the fast sync binary exists
    """
    path_to_bin = get_path_to_fast_sync()
    if not os.path.exists(path_to_bin) or not os.path.isfile(path_to_bin):
        raise Exception("Could not find fast sync binary at {}.".format(path_to_bin))

def get_path_to_fast_sync() -> str:
    """Returns the path to the fast sync binary"""
    os_name: str = "linux"
    path_to_bin = os.path.join(os.path.dirname(__file__), f"../../../bin/subtensor-node-api-{os_name}")
    return path_to_bin

def run_sync_and_save(filename: str) -> None:
    path_to_bin = get_path_to_fast_sync()
    sync_neurons(filename, path_to_bin)


def sync_neurons(filename: str, path_to_bin: str) -> None:
    """Runs the fast sync binary to sync all neurons at a given block hash"""
    
    print("Using subtensor-node-api for neuron retrieval...")
    # will write to ~/.bittensor/metagraph.json by default
    try:
        subprocess.run([path_to_bin, "sync_and_save", '-f', filename], check=True, stdout=subprocess.PIPE)
    except subprocess.SubprocessError as e:
        raise Exception("Error running fast sync binary: {}".format(e))


if __name__ == '__main__':
    verify_binary_exists()
    run_sync_and_save(sys.argv[1]) # pass file name