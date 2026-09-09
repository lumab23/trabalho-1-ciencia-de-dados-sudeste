"""Reúne contribuições reais em ordem explícita; não cria seções fictícias."""
import argparse
from pathlib import Path
import json
import uuid
import nbformat


def consolidar(raiz: Path, manifesto="integracao.json"):
    config = json.loads((raiz / manifesto).read_text(encoding="utf-8"))
    faltantes = [c["arquivo"] for c in config["contribuicoes"] if not (raiz / c["arquivo"]).is_file()]
    if faltantes:
        raise FileNotFoundError("Consolidação aguarda contribuições reais: " + ", ".join(faltantes))
    destino = raiz / config["saida"]
    if destino.exists():
        raise FileExistsError(f"{destino} já existe. Configure outro nome de saída para preservar o arquivo anterior.")
    celulas = []
    for contribuicao in config["contribuicoes"]:
        notebook = nbformat.read(raiz / contribuicao["arquivo"], as_version=4)
        nbformat.validate(notebook)
        celulas.append(nbformat.v4.new_markdown_cell(f"## Contribuição de {contribuicao['autor']}\n\nOrigem: `{contribuicao['arquivo']}`"))
        for celula in notebook.cells:
            celula["id"] = uuid.uuid4().hex[:8]
            celula.metadata["autor"] = contribuicao["autor"]
            celula.metadata["arquivo_origem"] = contribuicao["arquivo"]
            if celula.cell_type == "code":
                celula.outputs = []
                celula.execution_count = None
            celulas.append(celula)
    resultado = nbformat.v4.new_notebook(cells=celulas)
    resultado.metadata["kernelspec"] = {"display_name": "Python (T326 Sudeste)", "language": "python", "name": "t326-sudeste"}
    nbformat.validate(resultado)
    nbformat.write(resultado, destino)
    return destino


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--manifesto", default="integracao.json")
    args = parser.parse_args()
    print(consolidar(args.root, args.manifesto))
