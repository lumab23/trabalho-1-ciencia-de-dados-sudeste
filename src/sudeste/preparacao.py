"""Transformações puras: códigos, unidades, anos e cruzamentos validados."""
import re
import unicodedata

import numpy as np
import pandas as pd

# Fonte: https://www.ibge.gov.br/explica/codigos-dos-municipios.php
# A associação municipal vem da DTB; esta tabela apenas traduz seus códigos de UF.
SUDESTE = {"31": ("MG", "Minas Gerais"), "32": ("ES", "Espírito Santo"),
           "33": ("RJ", "Rio de Janeiro"), "35": ("SP", "São Paulo")}
MONETARIAS = {
    "pib_mil_reais": "pib_total_reais",
    "impostos_mil_reais": "impostos_reais",
    "va_da_agropecuaria_mil_reais": "va_agropecuaria_reais",
    "va_da_industria_mil_reais": "va_industria_reais",
    "va_dos_servicos_mil_reais": "va_servicos_reais",
    "va_da_administracao_publica_mil_reais": "va_administracao_publica_reais",
}


def nome_padrao(valor) -> str:
    texto = unicodedata.normalize("NFKD", str(valor)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "_", texto).strip("_")


def padronizar_colunas(df):
    resultado = df.copy()
    nomes = [nome_padrao(c) for c in df.columns]
    if len(nomes) != len(set(nomes)):
        raise ValueError("Colunas distintas colidem após a padronização.")
    resultado.columns = nomes
    return resultado


def codigo_municipio(valor):
    """Aceita sete dígitos e sufixo decimal .0; nunca inventa dígito verificador."""
    if pd.isna(valor):
        return pd.NA
    texto = re.sub(r"\.0+$", "", str(valor).strip())
    return texto if re.fullmatch(r"[0-9]{7}", texto) else pd.NA


def numerico(serie, decimal="."):
    # Marcadores SIDRA (.., ..., -, X), vazios e textos tornam-se ausentes;
    # o chamador preserva e registra os registros afetados, sem imputar zero.
    texto = serie.astype("string").str.strip()
    if decimal == ",":
        texto = texto.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    elif decimal != ".":
        raise ValueError("Separador decimal deve ser '.' ou ','.")
    return pd.to_numeric(texto, errors="coerce").astype("Float64")


def exigir_colunas(df, colunas):
    faltantes = sorted(set(colunas) - set(df.columns))
    if faltantes:
        raise ValueError(f"Esquema não reconhecido. Colunas ausentes: {faltantes}; disponíveis: {list(df.columns)}")


def padronizar_fonte(df, nome, config):
    base = padronizar_colunas(df)
    codigo = "codigo_municipio_completo" if nome == "dtb" else "cod"
    exigir_colunas(base, [codigo])
    base["codigo_original"] = base[codigo]
    base["codigo_municipio"] = base[codigo].map(codigo_municipio).astype("string")
    if nome == "dtb":
        exigir_colunas(base, ["uf", "nome_uf", "nome_municipio"])
        base = base.rename(columns={"municipio": "codigo_municipio_local", "uf": "codigo_uf", "nome_uf": "estado", "nome_municipio": "municipio"})
        base["codigo_uf"] = base["codigo_uf"].astype("string").str.strip().str.replace(r"\.0+$", "", regex=True)
    else:
        exigir_colunas(base, ["municipio"])
        base = base.rename(columns={"municipio": f"municipio_{nome}"})
        if "ano" in base:
            anos = numerico(base["ano"])
            if (anos.isna() | ~np.isfinite(anos) | anos.mod(1).ne(0) | ~anos.between(1900, 2100)).any():
                raise ValueError(f"{nome}: ano ausente ou inválido; corrija a fonte.")
            base["ano"] = anos.astype("Int64")
        else:
            ano = config.get("ano")
            if not isinstance(ano, int) or isinstance(ano, bool) or not 1900 <= ano <= 2100 or not config.get("evidencia_ano"):
                raise ValueError(f"{nome}: não há coluna de ano. Informe ano e evidencia_ano comprovados em config.json.")
            base["ano"] = pd.Series(ano, index=base.index, dtype="Int64")
        if nome == "pib":
            exigir_colunas(base, ["pib_mil_reais"])
            if config.get("unidade_monetaria") != "mil_reais":
                raise ValueError("Cabeçalho PIB (Mil Reais) exige unidade_monetaria=mil_reais.")
            for origem, destino in MONETARIAS.items():
                if origem in base:
                    base[destino] = numerico(base[origem], config.get("decimal", ".")) * 1000
        elif nome == "populacao":
            exigir_colunas(base, ["populacao_pessoas"])
            if config.get("unidade_populacao") != "pessoas":
                raise ValueError("População deve estar em pessoas, conforme o cabeçalho.")
            base["populacao"] = numerico(base["populacao_pessoas"], config.get("decimal", "."))
        else:
            raise ValueError(f"Fonte desconhecida: {nome}")
    return base


def selecionar_ano(pib, populacao, ano=None):
    comuns = sorted(set(pib["ano"].dropna().astype(int)) & set(populacao["ano"].dropna().astype(int)))
    if not comuns:
        raise ValueError("PIB e população não têm anos comuns; mistura temporal não permitida.")
    selecionado = max(comuns) if ano is None else ano
    if selecionado not in comuns:
        raise ValueError(f"Ano solicitado {selecionado} indisponível em ambas as fontes. Comuns: {comuns}")
    return selecionado, comuns


def exigir_chave_unica(df, chaves):
    if df[chaves].isna().any().any() or df.duplicated(chaves).any():
        raise ValueError(f"Chave ausente ou duplicada: {chaves}. Consulte os relatórios de auditoria.")


def filtrar_sudeste(dtb):
    exigir_chave_unica(dtb, ["codigo_municipio"])
    base = dtb.loc[dtb["codigo_uf"].isin(SUDESTE)].copy()
    base["uf"] = base["codigo_uf"].map({c: v[0] for c, v in SUDESTE.items()}).astype("string")
    base["regiao"] = "Sudeste"
    estados = base["codigo_uf"].map({c: v[1] for c, v in SUDESTE.items()})
    if base["estado"].map(nome_padrao).ne(estados.map(nome_padrao)).any():
        raise ValueError("Nome do estado na DTB contradiz seu código de UF.")
    return base


def cruzar(dtb_sudeste, pib, populacao):
    exigir_chave_unica(dtb_sudeste, ["codigo_municipio"])
    for df in (pib, populacao):
        exigir_chave_unica(df, ["codigo_municipio", "ano"])
        if df["ano"].nunique() != 1:
            raise ValueError("Selecione um único ano antes do cruzamento.")
    if set(pib["ano"]) != set(populacao["ano"]):
        raise ValueError("Não é permitido cruzar anos diferentes.")
    base = dtb_sudeste[["codigo_municipio", "municipio", "codigo_uf", "uf", "estado", "regiao"]].copy()
    base["ano"] = int(pib["ano"].iloc[0])
    economicas = [c for c in MONETARIAS.values() if c in pib]
    base = base.merge(pib[["codigo_municipio", "ano", "municipio_pib", *economicas]],
                      on=["codigo_municipio", "ano"], how="left", validate="one_to_one", indicator="vinculo_pib")
    base = base.merge(populacao[["codigo_municipio", "ano", "municipio_populacao", "populacao"]],
                      on=["codigo_municipio", "ano"], how="left", validate="one_to_one", indicator="vinculo_populacao")
    return base


def calcular_pib_per_capita(base):
    resultado = base.copy()
    pib = pd.to_numeric(resultado["pib_total_reais"], errors="coerce").astype("Float64")
    pop = pd.to_numeric(resultado["populacao"], errors="coerce").astype("Float64")
    valido = (np.isfinite(pib) & pib.ge(0) & np.isfinite(pop) & pop.gt(0) & pop.mod(1).eq(0)).fillna(False)
    resultado["pib_per_capita_reais"] = (pib / pop.where(valido)).where(valido).astype("Float64")
    resultado["apto_pib_per_capita"] = valido
    return resultado


def motivos_invalidos(base):
    motivos = pd.Series("", index=base.index, dtype="string")
    def marcar(mascara, motivo):
        motivos.loc[mascara.fillna(False)] += motivo + ";"
    for nome in ("pib", "populacao"):
        marcar(base[f"vinculo_{nome}"].ne("both"), f"sem_{nome}")
    marcar(base["pib_total_reais"].isna(), "pib_ausente_ou_nao_numerico")
    marcar(base["pib_total_reais"].lt(0) | ~np.isfinite(base["pib_total_reais"]), "pib_negativo_ou_nao_finito")
    marcar(base["populacao"].isna(), "populacao_ausente_ou_nao_numerica")
    marcar(base["populacao"].le(0) | ~np.isfinite(base["populacao"]), "populacao_nao_positiva_ou_nao_finita")
    marcar(base["populacao"].mod(1).ne(0), "populacao_fracionaria")
    return motivos.str.rstrip(";")
