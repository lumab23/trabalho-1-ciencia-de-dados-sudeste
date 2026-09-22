"""Orquestração auditável; nenhuma análise econômica dos demais integrantes."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .io import carregar_fontes, salvar_json
from .preparacao import (MONETARIAS, SUDESTE, calcular_pib_per_capita, cruzar,
                        exigir_chave_unica, filtrar_sudeste, motivos_invalidos,
                        nome_padrao, padronizar_fonte, selecionar_ano)


def auditar(raiz, nome, df):
    destino = raiz / "outputs/reports" / f"{nome}.csv"
    destino.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(destino, index=False, encoding="utf-8")


def normalizar(bases, config, raiz):
    tratadas = {}
    problemas = []
    for nome, df in bases.items():
        base = padronizar_fonte(df, nome, config["fontes"][nome])
        chaves = ["codigo_municipio"] + ([] if nome == "dtb" else ["ano"])
        invalidos = base["codigo_municipio"].isna()
        duplicados = base.duplicated(chaves, keep=False)
        auditar(raiz, f"{nome}_codigos_invalidos", base.loc[invalidos])
        auditar(raiz, f"{nome}_duplicados", base.loc[duplicados])
        if invalidos.any() or duplicados.any():
            problemas.append(f"{nome}: {int(invalidos.sum())} códigos inválidos e {int(duplicados.sum())} linhas com chave duplicada")
        if nome == "dtb":
            inconsistente = (base["codigo_municipio"].str[:2].ne(base["codigo_uf"]) |
                             base["codigo_uf"].isna() | base["municipio"].str.strip().eq("") |
                             base["estado"].str.strip().eq("")).fillna(True)
            auditar(raiz, "dtb_inconsistencias", base.loc[inconsistente])
            if inconsistente.any():
                problemas.append("DTB: códigos de UF, nomes ou prefixos municipais inconsistentes")
        tratadas[nome] = base
    if problemas:
        raise ValueError("; ".join(problemas) + ". Nenhuma duplicata foi removida arbitrariamente.")
    return tratadas


def integrar(tratadas, config, raiz, inventario):
    pib, pop, dtb = (tratadas[c] for c in ("pib", "populacao", "dtb"))
    ano, comuns = selecionar_ano(pib, pop, config.get("ano"))
    pib_ano = pib.loc[pib["ano"].eq(ano)].copy()
    pop_ano = pop.loc[pop["ano"].eq(ano)].copy()
    territorio = filtrar_sudeste(dtb)
    if territorio.empty:
        raise ValueError("A DTB não contém municípios do Sudeste.")
    etapas = {"pib_bruto": len(pib), "populacao_bruta": len(pop), "dtb_bruta": len(dtb),
              "pib_ano_selecionado": len(pib_ano), "populacao_ano_selecionado": len(pop_ano),
              "dtb_sudeste": len(territorio)}
    perdas = {"pib_outros_anos": len(pib) - len(pib_ano), "populacao_outros_anos": len(pop) - len(pop_ano),
              "dtb_fora_sudeste": len(dtb) - len(territorio)}
    correspondencias = {}
    for nome, fonte in (("pib", pib_ano), ("populacao", pop_ano)):
        # Outer join nacional revela chaves ausentes em qualquer lado, sem as ocultar pelo filtro.
        cobertura = dtb[["codigo_municipio", "estado"]].merge(fonte[["codigo_municipio"]],
                      on="codigo_municipio", how="outer", validate="one_to_one", indicator=True)
        auditar(raiz, f"{nome}_cobertura_dtb", cobertura.loc[cobertura["_merge"].ne("both")])
        correspondencias[nome] = {str(k): int(v) for k, v in cobertura["_merge"].value_counts().items()}
        perdas[f"{nome}_sem_dtb"] = int(cobertura["_merge"].eq("right_only").sum())
        perdas[f"{nome}_fora_sudeste_com_dtb"] = int((fonte["codigo_municipio"].isin(dtb["codigo_municipio"]) & ~fonte["codigo_municipio"].isin(territorio["codigo_municipio"])).sum())
        etapas[f"{nome}_sudeste"] = int(fonte["codigo_municipio"].isin(territorio["codigo_municipio"]).sum())
    cruzada = cruzar(territorio, pib_ano, pop_ano)
    etapas["apos_cruzar_pib"] = len(cruzada)  # Ambos os joins são left 1:1, ancorados na DTB.
    etapas["apos_cruzar_populacao"] = len(cruzada)
    cruzada = calcular_pib_per_capita(cruzada)
    cruzada["motivo_exclusao"] = motivos_invalidos(cruzada)
    for nome in ("pib", "populacao"):
        mascara = cruzada[f"vinculo_{nome}"].ne("both")
        auditar(raiz, f"sudeste_sem_{nome}", cruzada.loc[mascara])
        perdas[f"dtb_sudeste_sem_{nome}"] = int(mascara.sum())
    # Divergências de grafia são auditadas; nome oficial da DTB prevalece.
    divergencias = []
    for nome in ("pib", "populacao"):
        coluna = f"municipio_{nome}"
        limpo = cruzada[coluna].astype("string").str.replace(r"\s*\([A-Z]{2}\)$", "", regex=True)
        diferente = limpo.notna() & limpo.map(nome_padrao).ne(cruzada["municipio"].map(nome_padrao))
        parte = cruzada.loc[diferente, ["codigo_municipio", "municipio", coluna]].copy()
        parte["fonte"] = nome
        parte = parte.rename(columns={coluna: "nome_na_fonte"})
        divergencias.append(parte)
    divergencias = pd.concat(divergencias, ignore_index=True)
    auditar(raiz, "nomes_divergentes", divergencias)
    rejeitados = cruzada.loc[~cruzada["apto_pib_per_capita"]].copy()
    auditar(raiz, "registros_excluidos", rejeitados)
    # Colunas auxiliares não entram na base de consumo; permanecem na auditoria.
    colunas = ["codigo_municipio", "municipio", "codigo_uf", "uf", "estado", "regiao", "ano",
               "pib_total_reais", "populacao", "pib_per_capita_reais"]
    colunas += [c for c in MONETARIAS.values() if c != "pib_total_reais" and c in cruzada]
    final = cruzada.loc[cruzada["apto_pib_per_capita"], colunas].copy()
    problemas_economicos = []
    for c in colunas[10:]:
        # Não se presume que todo VA negativo seja erro. Preserva-o e sinaliza-o.
        invalido = final[c].isna() | ~np.isfinite(final[c])
        alerta = invalido | final[c].lt(0)
        if alerta.any():
            parte = final.loc[alerta, ["codigo_municipio", "ano", c]].rename(columns={c: "valor"})
            parte["variavel"] = c
            problemas_economicos.append(parte)
        final.loc[invalido, c] = pd.NA
    auditar(raiz, "alertas_variaveis_economicas", pd.concat(problemas_economicos, ignore_index=True) if problemas_economicos else pd.DataFrame(columns=["codigo_municipio", "ano", "valor", "variavel"]))
    for c in ("codigo_municipio", "codigo_uf", "municipio", "uf", "estado", "regiao"):
        final[c] = final[c].astype("string")
    final["ano"] = final["ano"].astype("Int64")
    final["populacao"] = final["populacao"].astype("Int64")
    final = final.sort_values(["uf", "codigo_municipio"]).reset_index(drop=True)
    etapas["base_final"] = len(final)
    perdas["excluidos_calculo_invalido"] = len(rejeitados)
    relatorio = {
        "status": "processado", "executado_em_utc": datetime.now(timezone.utc).isoformat(),
        "ano_selecionado": int(ano), "anos_comuns": comuns,
        "anos_disponiveis": {n: sorted(tratadas[n]["ano"].unique().tolist()) for n in ("pib", "populacao")},
        "fontes": inventario, "etapas": etapas, "perdas_e_recortes": perdas,
        "correspondencias_nacionais": correspondencias,
        "registros_por_uf_dtb": territorio.groupby("uf").size().to_dict(),
        "registros_por_uf_final": final.groupby("uf").size().to_dict(),
        "ausentes_final": final.isna().sum().to_dict(),
        "ausentes_antes_exclusao": cruzada[colunas].isna().sum().to_dict(),
        "duplicatas_chave_final": int(final.duplicated(["codigo_municipio", "ano"]).sum()),
        "divergencias_nomes": len(divergencias),
        "unidades": {"monetarias_entrada": "mil reais", "fator_conversao": 1000,
                     "monetarias_saida": "reais correntes de 2020" if ano == 2020 else f"reais correntes de {ano}",
                     "populacao": "pessoas", "pib_per_capita": "reais por pessoa"},
        "decisoes": [
            "Ano dos arquivos originais identificado por Content-Disposition e título no Drive; não há coluna de ano nos CSVs fornecidos.",
            "Escolha automática do maior ano comum; config.ano permite selecionar outro ano comum, nunca anos distintos.",
            "DTB sem edição identificada: correspondência de códigos e nomes não comprova equivalência histórica de limites territoriais.",
            "Código municipal completo tem sete dígitos. Código local de cinco dígitos da DTB não é usado como chave.",
            "Região Sudeste derivada dos códigos de UF da DTB (31,32,33,35); regiões imediatas/intermediárias não são macrorregiões.",
            "Códigos ausentes e chaves duplicadas interrompem o pipeline após registrar as linhas; não há deduplicação arbitrária.",
            "PIB ausente, negativo ou não finito e população ausente, não positiva, não inteira ou não finita: exclusão auditada da base de consumo, sem imputação.",
            "VA e impostos: ausentes/não numéricos/não finitos ficam nulos; negativos são preservados e sinalizados para revisão.",
            "Nomes divergentes são relatados, sem cruzamento aproximado por nome; prevalece o nome da DTB.",
            "PIB per capita é PIB dividido pela estimativa populacional do mesmo ano; não representa renda individual nem distribuição de renda.",
            "VA dos serviços e VA da administração pública preservam os rótulos do arquivo; consultar os metadados SIDRA antes de agregar setores.",
            "Nenhuma quantidade de municípios foi imposta; cobertura final é reconciliada com a DTB fornecida.",
        ]}
    validar_final(final, relatorio)
    return final, relatorio


def validar_final(base, relatorio):
    exigir_chave_unica(base, ["codigo_municipio", "ano"])
    if base.empty or not set(base["uf"]).issubset({v[0] for v in SUDESTE.values()}):
        raise ValueError("Base vazia ou com UF fora do Sudeste.")
    if not base["regiao"].eq("Sudeste").all() or not base["ano"].eq(relatorio["ano_selecionado"]).all():
        raise ValueError("Região ou ano inconsistente.")
    if not base["codigo_municipio"].str.fullmatch(r"[0-9]{7}").all():
        raise ValueError("Código final não tem sete dígitos.")
    if not base["codigo_municipio"].str[:2].eq(base["codigo_uf"]).all():
        raise ValueError("UF incompatível com o código municipal.")
    if not (base["populacao"].gt(0) & base["populacao"].mod(1).eq(0) & base["pib_total_reais"].ge(0)).all():
        raise ValueError("Valores centrais inválidos na base final.")
    if not np.isfinite(base[["pib_total_reais", "populacao", "pib_per_capita_reais"]].to_numpy(dtype=float)).all():
        raise ValueError("Valor central ausente ou não finito na base final.")
    if not np.allclose(base["pib_per_capita_reais"].to_numpy(dtype=float),
                       (base["pib_total_reais"] / base["populacao"]).to_numpy(dtype=float), rtol=1e-12, atol=1e-8):
        raise ValueError("PIB per capita não corresponde à fórmula.")
    if relatorio["etapas"]["dtb_sudeste"] != len(base) + relatorio["perdas_e_recortes"]["excluidos_calculo_invalido"]:
        raise ValueError("Perdas não reconciliadas com a DTB.")
    if relatorio["unidades"]["fator_conversao"] != 1000 or relatorio["unidades"]["populacao"] != "pessoas":
        raise ValueError("Unidades diferentes do contrato.")


def exportar(base, relatorio, raiz):
    pasta = raiz / "data/processed"
    pasta.mkdir(parents=True, exist_ok=True)
    csv = pasta / "sudeste_municipios.csv"
    parquet = pasta / "sudeste_municipios.parquet"
    base.to_csv(csv, index=False, encoding="utf-8", float_format="%.17g")
    base.to_parquet(parquet, index=False)
    relida = pd.read_csv(csv, dtype={c: str(t) for c, t in base.dtypes.items()})
    pd.testing.assert_frame_equal(base, relida, check_exact=False, rtol=1e-12, atol=1e-8)
    pd.testing.assert_frame_equal(base, pd.read_parquet(parquet))
    validar_final(relida, relatorio)
    relatorio["releitura"] = {"csv": "aprovada", "parquet": "aprovada"}
    relatorio["tipos_final"] = {c: str(t) for c, t in base.dtypes.items()}
    salvar_json(raiz / "outputs/reports/qualidade.json", relatorio)
    linhas = ["# Relatório de qualidade — T326", "", f"Ano: {relatorio['ano_selecionado']}. Anos comuns: {relatorio['anos_comuns']}.",
              "", "## Registros por etapa", "", "| Etapa | Registros |", "|---|---:|"]
    linhas += [f"| {k} | {v} |" for k, v in relatorio["etapas"].items()]
    linhas += ["", "## Cobertura do Sudeste", "", "| UF | DTB fornecida | Base final |", "|---|---:|---:|"]
    linhas += [f"| {uf} | {q} | {relatorio['registros_por_uf_final'].get(uf, 0)} |" for uf, q in sorted(relatorio["registros_por_uf_dtb"].items())]
    linhas += ["", "## Perdas e recortes", "", "Contagens abaixo podem se sobrepor (por exemplo, ausência simultânea de PIB e população). A exclusão final é contada uma única vez.", ""]
    linhas += [f"- {k}: {v}" for k, v in relatorio["perdas_e_recortes"].items()]
    linhas += ["", "## Validações", "", f"Duplicatas município/ano: {relatorio['duplicatas_chave_final']}. Divergências de nomes: {relatorio['divergencias_nomes']}.",
               "Releitura de CSV e Parquet aprovada; cálculo validado por comparação numérica. Valores econômicos em reais correntes, população em pessoas e PIB per capita em reais/pessoa.",
               "", "Ausentes por coluna na base final:", ""]
    linhas += [f"- {k}: {v}" for k, v in relatorio["ausentes_final"].items()]
    linhas += ["", "## Fontes e decisões", ""]
    linhas += [f"- {n}: {i.get('nome_original')}; {i.get('registros')} linhas; {i.get('formato')}; {i.get('encoding')}; compressão {i.get('compactacao')}. SHA256: `{i.get('sha256')}`." for n, i in relatorio["fontes"].items()]
    linhas += [""] + [f"- {d}" for d in relatorio["decisoes"]]
    linhas += ["", "Detalhes de esquema: inventario_fontes.json. Auditorias de chaves, cobertura, nomes e exclusões: CSVs nesta pasta. Os originais preservam os valores anteriores à conversão."]
    (raiz / "outputs/reports/qualidade.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    salvar_json(pasta / "metadados.json", {k: relatorio[k] for k in ("ano_selecionado", "unidades", "tipos_final", "fontes", "decisoes")})
    return csv, parquet


def executar(raiz, config_path="config.json", ano=None):
    try:
        config = json.loads((raiz / config_path).read_text(encoding="utf-8"))
        if ano is not None:
            config["ano"] = ano
        bases, inventario = carregar_fontes(raiz, config)
        tratadas = normalizar(bases, config, raiz)
        base, relatorio = integrar(tratadas, config, raiz, inventario)
        exportar(base, relatorio, raiz)
        salvar_json(raiz / "outputs/reports/ultima_execucao.json", {"status": "sucesso", "ano": relatorio["ano_selecionado"], "registros": len(base), "utc": datetime.now(timezone.utc).isoformat()})
        return base, relatorio
    except Exception as erro:
        salvar_json(raiz / "outputs/reports/ultima_execucao.json", {"status": "falha", "erro": str(erro), "utc": datetime.now(timezone.utc).isoformat(), "observacao": "Saídas anteriores, se existirem, foram preservadas e não validam esta execução."})
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--config", default="config.json")
    parser.add_argument("--ano", type=int)
    args = parser.parse_args()
    base, relatorio = executar(args.root.resolve(), args.config, args.ano)
    print(f"Ano {relatorio['ano_selecionado']}: {len(base)} registros.\n{base.groupby('uf').size().to_string()}")


if __name__ == "__main__":
    main()
