from textnode import TextType, TextNode
from htmlnode import LeafNode
from blocktype import BlockType
import re

def text_node_to_html_node(text_node: TextNode):
    def simple_leaf(tag=None):
        return lambda node: LeafNode(tag, node.text)

    text_type_dict = {
        TextType.TEXT: simple_leaf(),
        TextType.BOLD: simple_leaf("b"),
        TextType.ITALIC: simple_leaf("i"),
        TextType.CODE: simple_leaf("code"),
        TextType.LINK: lambda node: LeafNode("a", node.text, {"href": node.url}),
        TextType.IMAGE: lambda node: LeafNode("img", "", {"src": node.url, "alt": node.text})
    }

    if text_node.text_type in text_type_dict:
        return text_type_dict[text_node.text_type](text_node)
    else:
         raise ValueError(f"{text_node.text_type} is not a valid TextType")

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
        else:
            split = node.text.split(delimiter)
            if len(split) % 2 == 0:
                raise ValueError(f"Invalid markdown: unmatched delimiter '{delimiter}'")

            for i, text in enumerate(split):
                if text != "":
                    if i % 2 == 0:
                        new_node = TextNode(text, TextType.TEXT)
                        new_nodes.append(new_node)
                    else:
                        new_node = TextNode(text, text_type)
                        new_nodes.append(new_node)
    return new_nodes

def extract_markdown_images(text):
    matches = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches

def extract_markdown_links(text):
    matches = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches

def split_nodes_image(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
        else:
            images = extract_markdown_images(node.text)
            if not images:
                new_nodes.append(node)
            else:
                current_text = node.text
                for alt_text, url in images:
                    sections = current_text.split(f"![{alt_text}]({url})", 1)
                    if sections[0]:
                        new_nodes.append(TextNode(sections[0], TextType.TEXT))
                    image_node = TextNode(alt_text, TextType.IMAGE, url)
                    new_nodes.append(image_node)
                    current_text = sections[1]
                if current_text:
                    new_nodes.append(TextNode(current_text, TextType.TEXT))
    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
        else:
            links = extract_markdown_links(node.text)
            if not links:
                new_nodes.append(node)
            else:
                current_text = node.text
                for alt_text, url in links:
                    sections = current_text.split(f"[{alt_text}]({url})", 1)
                    if sections[0]:
                        new_nodes.append(TextNode(sections[0], TextType.TEXT))
                    link_node = TextNode(alt_text, TextType.LINK, url)
                    new_nodes.append(link_node)
                    current_text = sections[1]
                if current_text:
                    new_nodes.append(TextNode(current_text, TextType.TEXT))
    return new_nodes

def text_to_textnodes(text):
    new_nodes = [TextNode(text, TextType.TEXT)]
    new_nodes = split_nodes_delimiter(new_nodes, "**", TextType.BOLD)
    new_nodes = split_nodes_delimiter(new_nodes, "_", TextType.ITALIC)
    new_nodes = split_nodes_delimiter(new_nodes, "`", TextType.CODE)
    new_nodes = split_nodes_image(new_nodes)
    new_nodes = split_nodes_link(new_nodes)
    return new_nodes

def markdown_to_blocks(markdown):
    block_list = markdown.split("\n\n")
    processed_blocks = []
    for block in block_list:
        stripped_block = block.strip()
        if stripped_block != "":
            processed_blocks.append(stripped_block)

    return processed_blocks

def block_to_block_type(block):
    if block.startswith(("# ", "## ", "### ", "#### ", "##### ", "###### ")):
        return BlockType.HEADING

    if block.startswith("```") and block.endswith("```"):
        return BlockType.CODE

    split_by_line = block.split("\n")

    boolean_list = []
    for line in split_by_line:
        if line.startswith(">"):
            boolean_list.append(True)
        else:
            boolean_list.append(False)
    if all(boolean_list):
        return BlockType.QUOTE

    boolean_list = []
    for line in split_by_line:
        if line.startswith("- "):
            boolean_list.append(True)
        else:
            boolean_list.append(False)
    if all(boolean_list):
        return BlockType.UNORDERED_LIST

    boolean_list = []
    for i, line in enumerate(split_by_line):
        if line.startswith(f"{i+1}. "):
            boolean_list.append(True)
        else:
            boolean_list.append(False)
    if all(boolean_list):
        return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH
