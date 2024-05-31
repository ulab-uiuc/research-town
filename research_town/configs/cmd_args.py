import argparse


def parse_args() -> argparse.Namespace:
    r"""Parses the command line arguments."""
    parser = argparse.ArgumentParser(description='Research Town')

    parser.add_argument('--cfg',
                        dest='cfg_file',
                        type=str,
                        required=True,
                        help='The configuration file path.')

    return parser.parse_args()