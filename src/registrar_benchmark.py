
# T26: Victor

import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path


def registrar_benchmark(
    caminho_csv="out/parte2/benchmark.csv",
    caminho_json="out/parte2/parte2_report.json"
):
    caminho_csv = Path(caminho_csv)
    caminho_json = Path(caminho_json)

    # Lê as medições que já foram realizadas.
    with caminho_csv.open(encoding="utf-8", newline="") as arquivo:
        medicoes = list(csv.DictReader(arquivo))

    # Agrupa os tempos por algoritmo, recorte e fonte.
    grupos = defaultdict(list)

    for medicao in medicoes:
        chave = (
            medicao["algoritmo"],
            int(medicao["recorte"]),
            int(medicao["fonte"])
        )
        grupos[chave].append(float(medicao["tempo_ms"]))

    # Verifica se cada grupo possui cinco execuções.
    for chave, tempos in grupos.items():
        if len(tempos) != 5:
            raise ValueError(
                f"O grupo {chave} possui {len(tempos)} execuções."
            )

    resumo = []

    for (algoritmo, recorte, fonte), tempos in sorted(grupos.items()):
        resumo.append({
            "algoritmo": algoritmo,
            "recorte": recorte,
            "fonte": fonte,
            "execucoes": len(tempos),
            "tempo_medio_ms": statistics.mean(tempos),
            "tempo_desvio_ms": statistics.stdev(tempos)
        })

    # Preserva as informações da T25.
    with caminho_json.open(encoding="utf-8") as arquivo:
        relatorio = json.load(arquivo)

    relatorio["benchmark"] = {
        "arquivo_csv": caminho_csv.as_posix(),
        "total_medicoes": len(medicoes),
        "unidade_tempo": "ms",
        "resumo": resumo
    }

    # Salva uma cópia de segurança do relatório anterior.
    backup = caminho_json.with_suffix(".backup.json")
    backup.write_text(
        caminho_json.read_text(encoding="utf-8"),
        encoding="utf-8"
    )

    caminho_json.write_text(
        json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )

    print(f"Total de medições: {len(medicoes)}")
    print(f"Grupos analisados: {len(resumo)}")
    print(f"Relatório atualizado: {caminho_json}")
    print(f"Cópia de segurança: {backup}")


if __name__ == "__main__":
    registrar_benchmark()
