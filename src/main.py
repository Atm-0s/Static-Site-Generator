#!/usr/bin/env python3

from textnode import TextNode, TextType

def main():
    textnode = TextNode("Dummy text", TextType.PLAIN)
    print(textnode)

if __name__ == "__main__":
    main()