from mwie.parsing.markdown_generator import MarkdownGenerator


def test_markdown_conversion():
    html = """
    <h1>Main Title</h1>
    <p>This is an introductory paragraph with meaningful details.</p>
    <h2>Subheading 1</h2>
    <ul>
        <li>First point</li>
        <li>Second point</li>
    </ul>
    <table>
        <tr><th>Col A</th><th>Col B</th></tr>
        <tr><td>Val 1</td><td>Val 2</td></tr>
    </table>
    <blockquote>A deep insight on web engines.</blockquote>
    """
    gen = MarkdownGenerator(html)
    md = gen.generate()

    assert "# Main Title" in md
    assert "## Subheading 1" in md
    assert "- First point" in md
    assert "- Second point" in md
    assert "| Col A | Col B |" in md
    assert "| Val 1 | Val 2 |" in md
    assert "> A deep insight on web engines." in md
