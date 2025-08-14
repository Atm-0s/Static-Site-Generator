#!/usr/bin/env python3
import os
import shutil
from conversions import *


def main():
    source_directory = os.path.relpath("./static")
    target_directory = os.path.relpath("./public")
    if os.path.exists(target_directory):
        shutil.rmtree("./public")
    os.mkdir("./public")
    return copy_files_recursion(source_directory, target_directory)



if __name__ == "__main__":
    main()