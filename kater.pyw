#!/usr/bin/env python3
import argparse
import sys
import zipfile
import os
from kater.main import kater


def katerCompress():
    pass


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-l', "--load",
                            type=str, help="kater file to open")
    arg_parser.add_argument("-gktr", "--gen-ktr", nargs=2,
                            help=f"generate a .ktr ('train reading') file from files in a folder and exit. \
#1 is the folder, #2 is an output file path")
    args = arg_parser.parse_args()

    if hasattr(args, "gen_ktr") and args.gen_ktr:  # Generate file with texts to read
        dir_in = args.gen_ktr[0]
        file_out = args.gen_ktr[1]

        _, file_extension = os.path.splitext(file_out)
        if file_extension != ".ktr":
            file_out += ".ktr"

        with zipfile.ZipFile(file_out, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
            for root, _, filenames in os.walk(dir_in):
                for name in filenames:
                    orig_name = name
                    name = os.path.join(root, name)
                    name = os.path.normpath(name)
                    zf.write(name, orig_name)
        sys.exit(0)
    elif hasattr(args, "load") and args.load:  # Start module
        kater(args.load)
    else:  # Dry run
        kater()


if __name__ == "__main__":
    main()
