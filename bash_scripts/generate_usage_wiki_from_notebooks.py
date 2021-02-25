import nbformat
import os
from traitlets.config import Config
from nbconvert import MarkdownExporter


notebooks_dir = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), 'notebooks')
wiki_dir = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), 'genet.wiki')

md_exporter = MarkdownExporter()

for notebook in [f for f in os.listdir(notebooks_dir) if f.endswith('.ipynb')]:
    with open(os.path.join(notebooks_dir, notebook)) as f:
        nb = nbformat.read(f, as_version=4)
        (body, resources) = md_exporter.from_notebook_node(nb)
    with open(os.path.join(wiki_dir, f'Usage:-{notebook[:-6]}.md'.replace(' ', '-')), 'w') as f:
        f.write(body)
