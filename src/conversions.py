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