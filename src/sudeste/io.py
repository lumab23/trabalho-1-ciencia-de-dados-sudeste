"""Inspeção por assinatura e leitura sem perder códigos ou marcadores originais."""
import csv
import hashlib
import io
import json
import lzma
import zipfile
from pathlib import Path

import pandas as pd


def salvar_json(caminho: Path, objeto):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(objeto, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def ler_fonte(caminho: Path, config: dict) -> tuple[pd.DataFrame, dict]:
    if not caminho.is_file():
        raise FileNotFoundError(f"Fonte ausente: {caminho}. Execute o download ou coloque o arquivo do professor neste caminho; consulte data/raw/README.md.")
    original = caminho.read_bytes()
    resumo = {"arquivo": config.get("arquivo", caminho.name), "bytes": len(original),
              "sha256": hashlib.sha256(original).hexdigest(), "nome_original": config.get("nome_original"),
              "ano_metadados": config.get("ano"), "evidencia_ano": config.get("evidencia_ano")}
    if config.get("sha256") and resumo["sha256"] != config["sha256"]:
        raise ValueError(f"{caminho.name}: SHA256 diferente do arquivo inspecionado. Revise conteúdo, esquema e ano antes de atualizar config.json.")
    compactacao = "xz" if original.startswith(b"\xfd7zXZ\x00") else None
    dados = lzma.decompress(original) if compactacao else original
    resumo["compactacao"] = compactacao
    excel = dados.startswith(b"\xd0\xcf\x11\xe0")
    if dados.startswith(b"PK"):
        with zipfile.ZipFile(io.BytesIO(dados)) as arquivo_zip:
            excel = "xl/workbook.xml" in arquivo_zip.namelist()
        if not excel:
            raise ValueError("ZIP não é XLSX. Inspecione e selecione o arquivo interno explicitamente.")
    if excel:
        engine = "openpyxl" if dados.startswith(b"PK") else "xlrd"
        livro = pd.ExcelFile(io.BytesIO(dados), engine=engine)
        aba = config.get("aba", livro.sheet_names[0] if len(livro.sheet_names) == 1 else None)
        if aba is None:
            raise ValueError(f"Escolha uma aba em config.json: {livro.sheet_names}")
        df = pd.read_excel(livro, sheet_name=aba, header=config.get("cabecalho", 0), dtype="string", keep_default_na=False)
        resumo.update(formato=engine, abas=livro.sheet_names, aba_selecionada=aba, encoding="não se aplica")
    else:
        encoding = config.get("encoding")
        if not encoding:
            try:
                dados.decode("utf-8-sig")
                encoding = "utf-8-sig"
            except UnicodeDecodeError:
                from charset_normalizer import from_bytes
                candidato = from_bytes(dados).best()
                if candidato is None:
                    raise ValueError("Codificação não identificada; configure encoding.")
                encoding = candidato.encoding
        texto = dados.decode(encoding, errors="strict")
        sep = config.get("separador") or csv.Sniffer().sniff(texto[:8192], delimiters=",;\t|").delimiter
        df = pd.read_csv(io.StringIO(texto), sep=sep, header=config.get("cabecalho", 0), dtype="string", keep_default_na=False)
        resumo.update(formato="csv", encoding=encoding, separador=sep, abas=[], linhas_iniciais=texto.splitlines()[:4])
    resumo.update(cabecalho=config.get("cabecalho", 0), registros=len(df), colunas=list(df.columns),
                  tipos_leitura={c: str(t) for c, t in df.dtypes.items()},
                  tipos_inferidos={c: str(t) for c, t in df.apply(lambda s: pd.to_numeric(s, errors="coerce") if pd.to_numeric(s, errors="coerce").notna().all() else s).dtypes.items()},
                  vazios={c: int(df[c].str.strip().eq("").sum()) for c in df},
                  duplicatas_exatas=int(df.duplicated().sum()))
    return df, resumo


def carregar_fontes(raiz: Path, config: dict):
    bases, inventario = {}, {}
    erros = []
    for nome, especificacao in config["fontes"].items():
        try:
            bases[nome], inventario[nome] = ler_fonte(raiz / especificacao["arquivo"], especificacao)
        except Exception as erro:
            inventario[nome] = {"erro": str(erro), "tipo": type(erro).__name__}
            erros.append(f"{nome}: {erro}")
    salvar_json(raiz / "outputs/reports/inventario_fontes.json", inventario)
    if erros:
        raise ValueError("Falha ao carregar fontes:\n" + "\n".join(erros))
    return bases, inventario
