from textnode import TextType, TextNode
from htmlnode import LeafNode

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
