"""Executa do início ao fim com o Python atual e salva evidência da execução."""
import argparse
from pathlib import Path
import sys
import os

import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager, KernelSpec


class KernelDoAmbiente(KernelSpecManager):
    def get_kernel_spec(self, kernel_name):
        return KernelSpec(argv=[sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
                          display_name="Python do ambiente T326", language="python")


def executar_notebook(raiz, caminho):
    # Caches e runtime ficam no projeto; não instala kernels no perfil pessoal.
    for variavel, subpasta in (("IPYTHONDIR", "ipython"), ("JUPYTER_RUNTIME_DIR", "jupyter")):
        destino = raiz / ".runtime" / subpasta
        destino.mkdir(parents=True, exist_ok=True)
        os.environ[variavel] = str(destino)
    origem = raiz / caminho
    notebook = nbformat.read(origem, as_version=4)
    nbformat.validate(notebook)
    kernel = KernelManager(kernel_spec_manager=KernelDoAmbiente())
    cliente = NotebookClient(notebook, km=kernel, timeout=180, resources={"metadata": {"path": str(raiz)}})
    try:
        cliente.execute()
    finally:
        # O KernelManager é fornecido por nós, portanto também o encerramos.
        if kernel.has_kernel:
            kernel.shutdown_kernel(now=True)
    destino = origem.with_name(origem.stem + "_executado.ipynb")
    nbformat.write(notebook, destino)
    from nbconvert import HTMLExporter
    html, _ = HTMLExporter().from_notebook_node(notebook)
    (raiz / "outputs/reports" / f"{origem.stem}.html").write_text(html, encoding="utf-8")
    return destino


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("arquivo", nargs="?", default="notebooks/01_preparacao_dados.ipynb")
    args = parser.parse_args()
    print(executar_notebook(Path.cwd(), args.arquivo))
