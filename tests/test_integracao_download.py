"""Testa entrega futura e recuperação sem depender de rede ou de colegas."""
import json
import nbformat
import pytest
import requests

from sudeste.download import baixar, FONTES
from sudeste.integracao import consolidar


def test_integracao_aguarda_contribuicao_real(tmp_path):
    (tmp_path / "integracao.json").write_text(json.dumps({"contribuicoes": [{"autor": "estatística descritiva", "arquivo": "ausente.ipynb"}], "saida": "final.ipynb"}))
    with pytest.raises(FileNotFoundError, match="contribuições reais"):
        consolidar(tmp_path)
    assert not (tmp_path / "final.ipynb").exists()


def test_integracao_preserva_origem_limpa_saidas_e_nao_sobrescreve(tmp_path):
    # Notebook mínimo artificial para testar a consolidação, sem análise econômica.
    celula = nbformat.v4.new_code_cell("x = 1", execution_count=1,
        outputs=[nbformat.v4.new_output("stream", name="stdout", text="saida antiga")])
    origem = tmp_path / "teste.ipynb"
    nbformat.write(nbformat.v4.new_notebook(cells=[celula]), origem)
    conteudo_original = origem.read_bytes()
    (tmp_path / "integracao.json").write_text(json.dumps({"contribuicoes": [{"autor": "Teste", "arquivo": "teste.ipynb"}], "saida": "final.ipynb"}))
    destino = consolidar(tmp_path)
    resultado = nbformat.read(destino, as_version=4)
    assert resultado.cells[1].outputs == []
    assert resultado.cells[1].execution_count is None
    assert resultado.cells[1].metadata.autor == "Teste"
    assert origem.read_bytes() == conteudo_original
    with pytest.raises(FileExistsError):
        consolidar(tmp_path)


def test_download_preserva_manual_quando_metadados_offline(tmp_path, monkeypatch):
    pasta = tmp_path / "data/raw"
    pasta.mkdir(parents=True)
    for nome in FONTES:
        (pasta / f"{nome}_original").write_bytes(b"arquivo de teste,sem resultados reais\n")
    def offline(*args, **kwargs):
        raise requests.ConnectionError("rede indisponível no teste")
    monkeypatch.setattr(requests, "get", offline)
    manifesto = baixar(tmp_path)
    assert all(item["status"] == "disponivel" for item in manifesto.values())
    assert all(item["origem"] == "arquivo_existente_preservado" for item in manifesto.values())
    assert all("erro_metadados" in item for item in manifesto.values())


def test_download_falha_documenta_recuperacao(tmp_path, monkeypatch):
    import gdown
    def offline(*args, **kwargs):
        raise requests.ConnectionError("rede indisponível no teste")
    monkeypatch.setattr(requests, "get", offline)
    monkeypatch.setattr(gdown, "download", offline)
    manifesto = baixar(tmp_path)
    assert all(item["status"] == "falha" and "acao" in item for item in manifesto.values())
    assert (tmp_path / "data/raw/downloads.jsonl").is_file()
