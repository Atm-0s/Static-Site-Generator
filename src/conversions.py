from textnode import TextType, TextNode
from htmlnode import LeafNode, ParentNode, HTMLNode
from blocktype import BlockType
import re
import os
import shutil

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

def markdown_to_html_node(markdown):
    block_list = markdown_to_blocks(markdown)

    def block_to_block_type_dict(block_list):
        block_type_dict = {}
        for block in block_list:
            block_type_dict[block] = block_to_block_type(block)
        return block_type_dict

    def create_child_list(block):
        text_nodes = text_to_textnodes(block)
        html_child_list = []
        for text_node in text_nodes:
            html_node = text_node_to_html_node(text_node)
            html_child_list.append(html_node)
        return html_child_list

    def create_para_parent(html_child_list):
        node = ParentNode("p", html_child_list)
        return node

    def create_heading_parent(html_child_list, level):
        node = ParentNode(f"h{level}", html_child_list)
        return node

    def create_code_parent(html_leaf_node):
        code_parent = ParentNode("code", [html_leaf_node])
        pre_parent = ParentNode("pre", [code_parent])
        return pre_parent

    def create_ordered_parent(list_items):
        li_nodes = []
        for item_text in list_items:
            item_children = create_child_list(item_text)
            li_node = ParentNode("li", item_children)
            li_nodes.append(li_node)
        ol_node = ParentNode("ol", li_nodes)
        return ol_node

    def create_unordered_parent(list_items):
        li_nodes = []
        for item_text in list_items:
            item_children = create_child_list(item_text)
            li_node = ParentNode("li", item_children)
            li_nodes.append(li_node)
        ul_node = ParentNode("ul", li_nodes)
        return ul_node

    def create_quote_parent(html_child_list):
        node = ParentNode("blockquote", html_child_list)
        return node

    def listify(block):
        lines = block.split("\n")
        list_lines = []
        for line in lines:
            if line.startswith("-"):
                list_lines.append(line[2:])
            else:
                parts = line.split(". ", 1)
                list_lines.append(parts[1])
        return list_lines

    html_node_blocks=[]



    block_type_dict = block_to_block_type_dict(block_list)
    for block, block_type in block_type_dict.items():
        if block_type == BlockType.CODE:
            code_content = block[4:-3]
            node = TextNode(code_content, TextType.TEXT)
            html_node = text_node_to_html_node(node)
            html_node_blocks.append(create_code_parent(html_node))

        elif block_type == BlockType.HEADING:
            if block.startswith("#"):
                count = 0
                for char in block:
                    if char == "#":
                        count += 1
                    else:
                        break
                heading_text = block[count:].strip()
                heading_children = create_child_list(heading_text)
                heading_node = create_heading_parent(heading_children, count)
                html_node_blocks.append(heading_node)

        elif block_type == BlockType.PARAGRAPH:
            lines = block.split("\n")
            paragraph = " ".join(lines)
            para_children = create_child_list(paragraph)
            para_node = create_para_parent(para_children)
            html_node_blocks.append(para_node)

        elif block_type == BlockType.QUOTE:
            lines = block.split("\n")
            quote_lines = []
            for line in lines:
                quote_lines.append(line[2:])
            quote_content = "\n".join(quote_lines)
            quote_children = create_child_list(quote_content)
            quote_node = create_quote_parent(quote_children)
            html_node_blocks.append(quote_node)

        elif block_type == BlockType.ORDERED_LIST:
            list_items = listify(block)
            ol_node = create_ordered_parent(list_items)
            html_node_blocks.append(ol_node)

        elif block_type == BlockType.UNORDERED_LIST:
            list_items = listify(block)
            ul_node = create_unordered_parent(list_items)
            html_node_blocks.append(ul_node)

    div_node = ParentNode("div", html_node_blocks)
    return div_node

def copy_files_recursion(source_directory, target_directory):
    source_list = os.listdir(source_directory)
    for item in source_list:
        from_path = os.path.join(source_directory, item)
        dest_path = os.path.join(target_directory, item)
        if os.path.isfile(from_path):
            shutil.copy(from_path, dest_path)
            print(f"Copying {from_path} to {dest_path}")
        if os.path.isdir(from_path):
            if not os.path.isdir(dest_path):
                os.mkdir(dest_path)
                print(f"Creating directory {dest_path}")
            copy_files_recursion(from_path, dest_path)

def extract_title(markdown):
    md_lines = markdown.split("\n")
    for line in md_lines:
        if line.startswith("# "):
            header = line.strip("# ")
            return header
    raise ValueError("No title was found.")

def generate_page(from_path, template_path, dest_path, basepath):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    with open(from_path, "r") as f:
        from_f = f.read()
    with open(template_path, "r") as f:
        temp_f = f.read()
    from_html = markdown_to_html_node(from_f).to_html()
    title = extract_title(from_f)
    temp_f = temp_f.replace("{{ Title }}", title)
    temp_f = temp_f.replace("{{ Content }}", from_html)
    temp_f = temp_f.replace('href="/', f'href="{basepath}')
    temp_f = temp_f.replace('src="/', f'src="{basepath}')
    dest_dir = os.path.dirname(dest_path)
    os.makedirs(dest_dir, exist_ok=True)
    with open(dest_path, "w") as f:
        f.write(temp_f)

def generate_pages_recursion(source_directory, template_path, target_directory, basepath):
    source_list = os.listdir(source_directory)
    for item in source_list:
        from_path = os.path.join(source_directory, item)
        dest_path = os.path.join(target_directory, item).replace(".md", ".html")
        if os.path.isfile(from_path):
            if not from_path.endswith(".md"):
                continue
            generate_page(from_path, template_path, dest_path, basepath)
            print(f"Generating {from_path} to {dest_path}")
        if os.path.isdir(from_path):
            if not os.path.isdir(dest_path):
                os.mkdir(dest_path)
                print(f"Creating directory {dest_path}")
            generate_pages_recursion(from_path, template_path, dest_path, basepath)