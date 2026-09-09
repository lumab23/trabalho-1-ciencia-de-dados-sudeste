"""Fixtures artificiais apenas para testar regras; não são dados do trabalho."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from sudeste.io import ler_fonte
from sudeste.preparacao import (codigo_municipio, calcular_pib_per_capita, cruzar,
                               filtrar_sudeste, padronizar_colunas, padronizar_fonte,
                               selecionar_ano)
from sudeste.pipeline import executar


@pytest.mark.parametrize("entrada,esperado", [("3106200", "3106200"), (3106200, "3106200"),
    (3106200.0, "3106200"), (" 3106200.00 ", "3106200"), ("0012345", "0012345")])
def test_codigo_preserva_sete_digitos(entrada, esperado):
    assert codigo_municipio(entrada) == esperado


@pytest.mark.parametrize("entrada", [None, pd.NA, np.nan, "", "310620", "31062001", "3106200.5", "3.1062e6", "31A6200"])
def test_codigo_invalido_nao_completa_nem_inventa(entrada):
    assert pd.isna(codigo_municipio(entrada))


def test_colunas_colisao():
    with pytest.raises(ValueError, match="colidem"):
        padronizar_colunas(pd.DataFrame(columns=["Município", "Municipio"]))


def test_dtb_usa_codigo_completo_e_preserva_codigo_local():
    dados = pd.DataFrame({"UF": ["31"], "Nome_UF": ["Minas Gerais"], "Município": ["06200"],
                          "Código Município Completo": ["3106200"], "Nome_Município": ["Belo Horizonte"]})
    base = padronizar_fonte(dados, "dtb", {})
    assert base.loc[0, "codigo_municipio"] == "3106200"
    assert base.loc[0, "codigo_municipio_local"] == "06200"
    assert base.loc[0, "municipio"] == "Belo Horizonte"


def test_filtro_usa_uf_dtb():
    dtb = pd.DataFrame({"codigo_municipio": ["3106200", "3205309", "3304557", "3550308", "2304400"],
                        "codigo_uf": ["31", "32", "33", "35", "23"],
                        "estado": ["Minas Gerais", "Espírito Santo", "Rio de Janeiro", "São Paulo", "Ceará"]})
    resultado = filtrar_sudeste(dtb)
    assert set(resultado.uf) == {"ES", "MG", "RJ", "SP"}
    assert len(resultado) == 4
    assert resultado.regiao.eq("Sudeste").all()


def test_filtro_rejeita_nome_estado_inconsistente():
    with pytest.raises(ValueError, match="contradiz"):
        filtrar_sudeste(pd.DataFrame({"codigo_municipio": ["3106200"], "codigo_uf": ["31"], "estado": ["Ceará"]}))


def test_conversao_mil_reais_antes_da_divisao():
    bruto = pd.DataFrame({"Cód.": ["3106200"], "Município": ["Belo Horizonte (MG)"], "PIB (Mil Reais)": ["1234.5"]})
    base = padronizar_fonte(bruto, "pib", {"ano": 2020, "evidencia_ano": "fixture de teste", "unidade_monetaria": "mil_reais"})
    base["populacao"] = 100
    assert calcular_pib_per_capita(base).loc[0, "pib_per_capita_reais"] == 12345


def test_unidade_contraditoria_interrompe():
    bruto = pd.DataFrame({"Cód.": ["3106200"], "Município": ["BH"], "PIB (Mil Reais)": ["100"]})
    with pytest.raises(ValueError, match="mil_reais"):
        padronizar_fonte(bruto, "pib", {"ano": 2020, "evidencia_ano": "teste", "unidade_monetaria": "reais"})


@pytest.mark.parametrize("pib,pop", [(10, 0), (10, -1), (10, None), (-10, 2), (None, 2),
                                     (np.inf, 2), (10, np.inf), (10, 2.5), ("X", 10)])
def test_calculo_invalido_nao_inventa_valor(pib, pop):
    resultado = calcular_pib_per_capita(pd.DataFrame({"pib_total_reais": [pib], "populacao": [pop]}))
    assert pd.isna(resultado.loc[0, "pib_per_capita_reais"])
    assert not resultado.loc[0, "apto_pib_per_capita"]


def test_pib_zero_valido():
    resultado = calcular_pib_per_capita(pd.DataFrame({"pib_total_reais": [0.0], "populacao": [10]}))
    assert resultado.loc[0, "pib_per_capita_reais"] == 0


def test_ano_mais_recente_comum_e_configuravel():
    pib = pd.DataFrame({"ano": [2019, 2020, 2021]})
    pop = pd.DataFrame({"ano": [2019, 2020, 2022]})
    assert selecionar_ano(pib, pop) == (2020, [2019, 2020])
    assert selecionar_ano(pib, pop, 2019)[0] == 2019
    with pytest.raises(ValueError, match="indisponível"):
        selecionar_ano(pib, pop, 2021)


def test_sem_anos_comuns():
    with pytest.raises(ValueError, match="não têm anos comuns"):
        selecionar_ano(pd.DataFrame({"ano": [2020]}), pd.DataFrame({"ano": [2021]}))


def test_sem_ano_evidenciado():
    bruto = pd.DataFrame({"Cód.": ["3106200"], "Município": ["BH"], "População (Pessoas)": ["10"]})
    with pytest.raises(ValueError, match="evidencia_ano"):
        padronizar_fonte(bruto, "populacao", {"unidade_populacao": "pessoas"})


@pytest.fixture
def fontes_cruzamento():
    dtb = pd.DataFrame({"codigo_municipio": ["3106200", "3550308"], "municipio": ["BH", "SP"],
                       "codigo_uf": ["31", "35"], "uf": ["MG", "SP"], "estado": ["Minas Gerais", "São Paulo"], "regiao": ["Sudeste", "Sudeste"]})
    pib = pd.DataFrame({"codigo_municipio": ["3106200"], "ano": [2020], "municipio_pib": ["BH"], "pib_total_reais": [100.0]})
    pop = pd.DataFrame({"codigo_municipio": ["3106200", "3550308"], "ano": [2020, 2020], "municipio_populacao": ["BH", "SP"], "populacao": [10, 20]})
    return dtb, pib, pop


def test_cruzamento_preserva_ausencia_para_auditoria(fontes_cruzamento):
    resultado = cruzar(*fontes_cruzamento)
    assert len(resultado) == 2
    assert resultado.loc[1, "vinculo_pib"] == "left_only"
    assert pd.isna(resultado.loc[1, "pib_total_reais"])


def test_cruzamento_rejeita_muitos_para_muitos(fontes_cruzamento):
    dtb, pib, pop = fontes_cruzamento
    with pytest.raises(ValueError, match="duplicada"):
        cruzar(dtb, pd.concat([pib, pib]), pop)


def test_cruzamento_rejeita_anos_distintos(fontes_cruzamento):
    dtb, pib, pop = fontes_cruzamento
    pop["ano"] = 2021
    with pytest.raises(ValueError, match="anos diferentes"):
        cruzar(dtb, pib, pop)


def test_fonte_ausente_informa_recuperacao(tmp_path):
    with pytest.raises(FileNotFoundError, match="arquivo do professor"):
        ler_fonte(tmp_path / "inexistente", {})


def test_hash_incompativel_nao_herda_ano(tmp_path):
    arquivo = tmp_path / "alterado.csv"
    arquivo.write_text("codigo,valor\n3106200,1\n")
    with pytest.raises(ValueError, match="SHA256"):
        ler_fonte(arquivo, {"sha256": "hash_diferente", "ano": 2020})


def test_pipeline_real_reconcilia_dtb_e_unidades(tmp_path):
    raiz = Path(__file__).resolve().parents[1]
    config = json.loads((raiz / "config.json").read_text())
    for fonte in config["fontes"].values():
        caminho = raiz / fonte["arquivo"]
        if not caminho.exists():
            pytest.skip("Arquivos reais ainda não disponíveis; teste não executado.")
        fonte["arquivo"] = str(caminho)
    (tmp_path / "config.json").write_text(json.dumps(config))
    base, relatorio = executar(tmp_path)
    # A quantidade vem da DTB real, sem número de municípios fixado no teste.
    assert len(base) == relatorio["etapas"]["dtb_sudeste"] - relatorio["perdas_e_recortes"]["excluidos_calculo_invalido"]
    assert relatorio["releitura"] == {"csv": "aprovada", "parquet": "aprovada"}
    assert not base.duplicated(["codigo_municipio", "ano"]).any()
    bruto, _ = ler_fonte(Path(config["fontes"]["pib"]["arquivo"]), config["fontes"]["pib"])
    comparacao = base.merge(bruto, left_on="codigo_municipio", right_on="Cód.", validate="one_to_one")
    np.testing.assert_allclose(comparacao.pib_total_reais.to_numpy(dtype=float), pd.to_numeric(comparacao["PIB (Mil Reais)"]).to_numpy() * 1000)
    for original, destino in [("Impostos (Mil Reais)", "impostos_reais"), ("VA da agropecuária (Mil Reais)", "va_agropecuaria_reais"),
                              ("VA da indústria (Mil Reais)", "va_industria_reais"), ("VA dos serviços (Mil Reais)", "va_servicos_reais"),
                              ("VA da administração pública (Mil Reais)", "va_administracao_publica_reais")]:
        np.testing.assert_allclose(comparacao[destino].to_numpy(dtype=float), pd.to_numeric(comparacao[original]).to_numpy() * 1000)
