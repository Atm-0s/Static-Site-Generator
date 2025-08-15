#!/usr/bin/env python3
import os
import sys
import shutil
from conversions import *


def main():
    if len(sys.argv) > 1:
        basepath = sys.argv[1]
    else:
        basepath = "/"
    source_directory = os.path.relpath("./static")
    target_directory = os.path.relpath("./docs")
    content_directory = os.path.relpath("./content")
    template_path = os.path.relpath("./template.html")
    if os.path.exists(target_directory):
        shutil.rmtree(target_directory)
    os.mkdir(target_directory)
    copy_files_recursion(source_directory, target_directory)
    generate_pages_recursion(content_directory, template_path, target_directory, basepath)




if __name__ == "__main__":
    main()