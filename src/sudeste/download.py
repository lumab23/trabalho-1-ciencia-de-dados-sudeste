"""Baixa somente os IDs do enunciado; preserva originais e registra falhas."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from datetime import datetime, timezone

FONTES = {
    "pib": "1GQVxYHY9ouZvh_Jkbzt3sjnWHslxGqnX",
    "populacao": "1OLg85S7vAr4MQomc_wcaQhRo6SLciSu0",
    "dtb": "1G3Ll5LsIhsvpodjnKg6JE0KXbc_D-BSP",
}


def baixar(raiz: Path) -> dict:
    import gdown
    import requests
    pasta = raiz / "data/raw"
    pasta.mkdir(parents=True, exist_ok=True)
    manifesto = {}
    for nome, identificador in FONTES.items():
        # Nome sem extensão: o leitor identificará o formato pelo conteúdo real.
        destino = pasta / f"{nome}_original"
        item = {"id": identificador, "url": f"https://drive.google.com/file/d/{identificador}/view",
                "arquivo": str(destino.relative_to(raiz)),
                "verificado_em_utc": datetime.now(timezone.utc).isoformat()}
        try:
            # A falha de metadados não invalida um original local já disponível.
            try:
                with requests.get(f"https://drive.google.com/uc?id={identificador}", stream=True, timeout=30) as resposta:
                    resposta.raise_for_status()
                    item["content_type"] = resposta.headers.get("Content-Type")
                    item["content_disposition"] = resposta.headers.get("Content-Disposition")
                pagina = requests.get(item["url"], timeout=30)
                pagina.raise_for_status()
                titulo = re.search(r"<title>(.*?)</title>", pagina.text, re.S)
                item["titulo_drive"] = titulo.group(1) if titulo else None
            except requests.RequestException as erro:
                item["erro_metadados"] = f"{type(erro).__name__}: {erro}"
            if not destino.exists():
                temporario = pasta / f"{nome}_download.part"
                resultado = gdown.download(id=identificador, output=str(temporario), quiet=False)
                if resultado is None:
                    raise RuntimeError("gdown não retornou um arquivo")
                temporario.rename(destino)
                item["origem"] = "download_gdown"
            else:
                item["origem"] = "arquivo_existente_preservado"
            if destino.stat().st_size == 0:
                raise ValueError("Arquivo vazio; obtenha uma cópia íntegra do mesmo ID.")
            item.update(status="disponivel", bytes=destino.stat().st_size,
                        sha256=hashlib.sha256(destino.read_bytes()).hexdigest())
        except Exception as erro:
            item.update(status="falha", erro=f"{type(erro).__name__}: {erro}",
                        acao=f"Baixe o mesmo ID pelo navegador e copie para {destino.relative_to(raiz)}; ou configure o caminho em config.json.")
        manifesto[nome] = item
        print(f"{nome}: {item['status']}")
    # Mantém o histórico de tentativas, inclusive mensagens de erro.
    with (pasta / "downloads.jsonl").open("a", encoding="utf-8") as arquivo:
        arquivo.write(json.dumps(manifesto, ensure_ascii=False) + "\n")
    return manifesto


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    resultado = baixar(args.root)
    raise SystemExit(1 if any(x["status"] == "falha" for x in resultado.values()) else 0)
