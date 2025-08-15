#!/usr/bin/env python3
import os
import shutil
from conversions import *


def main():
    source_directory = os.path.relpath("./static")
    target_directory = os.path.relpath("./public")
    content_directory = os.path.relpath("./content")
    template_path = os.path.relpath("./template.html")
    if os.path.exists(target_directory):
        shutil.rmtree(target_directory)
    os.mkdir(target_directory)
    copy_files_recursion(source_directory, target_directory)
    generate_pages_recursion(content_directory, template_path, target_directory)




if __name__ == "__main__":
    main()