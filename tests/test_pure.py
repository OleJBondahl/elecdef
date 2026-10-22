"""Family gate wrappers."""

import ast

import family


def test_f2_pure():
    family.gate_f2()


def float_sites(tree: ast.Module) -> list[int]:
    """The line of each float literal, `float` name or `.float` attribute in a syntax tree."""
    return [
        node.lineno
        for node in ast.walk(tree)
        if (isinstance(node, ast.Constant) and isinstance(node.value, float))
        or (isinstance(node, ast.Name) and node.id == "float")
        or (isinstance(node, ast.Attribute) and node.attr == "float")
    ]


def test_e2_checker_can_fail():
    assert float_sites(ast.parse("a = 1.5")) == [1]
    assert float_sites(ast.parse("def f(a: float): ...")) == [1]


def test_e2_no_float_in_src():
    assert [
        (str(path), float_sites(tree)) for path, tree in family.src_trees() if float_sites(tree)
    ] == []
