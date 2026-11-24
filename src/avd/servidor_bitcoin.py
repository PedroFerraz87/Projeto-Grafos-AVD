# [IA] OpenAI Codex – serviço local para executar a bancada no dataset original.
"""Sirva a demonstração em loopback e envie um resultado por algoritmo."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from threading import Lock
from urllib.parse import parse_qs, urlsplit

from .experimentos import ALGORITMOS, RAIZ, SAIDAS, RedeBitcoin, pares_publicados
from ..viz import gerar_pagina_bitcoin


def _criar_handler(rede, pares, pagina):
    fila = Lock()
    fila_mapas = Lock()
    rotas = {
        "/": pagina,
        "/bitcoin_alpha.html": pagina,
        "/labirinto_interativo.html": RAIZ / "out/parte1/labirinto_interativo.html",
        "/algoritmos_em_acao.html": RAIZ / "out/parte1/algoritmos_em_acao.html",
        "/parte2/parte2_report.json": SAIDAS / "parte2_report.json",
        "/parte2/dados_comparacao_algoritmos/comparacao_caminhos.csv":
            SAIDAS / "dados_comparacao_algoritmos/comparacao_caminhos.csv",
    }

    class Painel(BaseHTTPRequestHandler):
        def do_GET(self):
            arquivo = rotas.get(urlsplit(self.path).path)
            if arquivo is None or not arquivo.is_file():
                self.send_error(404)
                return
            conteudo = arquivo.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", (mimetypes.guess_type(arquivo)[0] or "text/plain") + "; charset=utf-8")
            self.send_header("Content-Length", str(len(conteudo)))
            self.end_headers()
            self.wfile.write(conteudo)

        def do_POST(self):
            destino = urlsplit(self.path)
            if destino.path not in {"/api/execucao", "/api/labirintos"}:
                self.send_error(404)
                return
            porta = self.server.server_port
            hosts = {f"127.0.0.1:{porta}", f"localhost:{porta}"}
            origem = self.headers.get("Origin")
            if self.headers.get("Host") not in hosts or (origem and origem not in {f"http://{h}" for h in hosts}):
                self.send_error(403)
                return
            if destino.path == "/api/labirintos":
                self._analisar_envio()
                return
            try:
                fonte = int(parse_qs(destino.query).get("fonte", [""])[0])
                destinos = pares[fonte]
            except (ValueError, KeyError):
                self.send_error(400, "Fonte ausente ou indisponível")
                return
            if not fila.acquire(blocking=False):
                self.send_error(429, "Há outra execução em andamento")
                return
            try:
                self.send_response(200)
                self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                resultados = []
                for algoritmo in ALGORITMOS:
                    resultado = rede.executar(algoritmo, fonte, destinos)
                    resultados.append(resultado)
                    self._enviar({"resultado": resultado})
                self._enviar({"grafo": rede.amostra(fonte, destinos, resultados)})
            except (BrokenPipeError, ConnectionResetError):
                pass
            finally:
                fila.release()

        def _enviar(self, mensagem):
            linha = json.dumps(mensagem, ensure_ascii=False, separators=(",", ":")) + "\n"
            self.wfile.write(linha.encode("utf-8"))
            self.wfile.flush()

        # [IA] OpenAI Codex – análise em arquivo temporário, isolada da execução do benchmark.
        def _analisar_envio(self):
            def responder(status, dados):
                resposta = json.dumps(dados, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(resposta)))
                self.send_header("Cache-Control", "no-store")
                try:
                    self.end_headers()
                    self.wfile.write(resposta)
                except (BrokenPipeError, ConnectionResetError):
                    pass

            try:
                tamanho = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                tamanho = 0
            if not 0 < tamanho <= 32 * 1024:
                responder(400, {"erro": "Envie um mapa .txt com até 32 KB."})
                return
            if not fila_mapas.acquire(blocking=False):
                responder(429, {"erro": "Há um mapa sendo analisado. Tente novamente quando ele terminar."})
                return
            try:
                self.connection.settimeout(10)
                conteudo = self.rfile.read(tamanho)
                if len(conteudo) != tamanho:
                    responder(400, {"erro": "O envio do mapa chegou incompleto."})
                    return
                with TemporaryDirectory(prefix="labirinto-envio-") as pasta:
                    caminho = Path(pasta) / "mapa.txt"
                    caminho.write_bytes(conteudo)
                    processo = subprocess.run(
                        [sys.executable, "-m", "src.avd.mapa_ao_vivo", str(caminho)],
                        cwd=RAIZ, capture_output=True, timeout=20, check=True,
                    )
                dados = json.loads(processo.stdout)
                responder(422 if "erro" in dados else 200, dados)
            except subprocess.TimeoutExpired:
                responder(422, {"erro": "A análise passou de 20 segundos. Tente um mapa menor ou com menos bônus."})
            except TimeoutError:
                responder(408, {"erro": "O envio do arquivo demorou muito."})
            except (subprocess.CalledProcessError, OSError, ValueError):
                responder(500, {"erro": "Não foi possível analisar o mapa."})
            finally:
                fila_mapas.release()

    return Painel


def main():
    parser = argparse.ArgumentParser(description="Abre o painel Bitcoin Alpha e executa os algoritmos em localhost.")
    parser.add_argument("--porta", type=int, default=8765)
    args = parser.parse_args()
    rede = RedeBitcoin()
    with TemporaryDirectory(prefix="bitcoin-painel-") as pasta:
        pagina = gerar_pagina_bitcoin(SAIDAS, Path(pasta) / "bitcoin_alpha.html")
        with ThreadingHTTPServer(("127.0.0.1", args.porta), _criar_handler(rede, pares_publicados(), pagina)) as servidor:
            print(f"Bitcoin Alpha: http://127.0.0.1:{servidor.server_port}/bitcoin_alpha.html", flush=True)
            print(f"Enviar labirinto: http://127.0.0.1:{servidor.server_port}/labirinto_interativo.html#enviar-mapa", flush=True)
            try:
                servidor.serve_forever()
            except KeyboardInterrupt:
                pass


if __name__ == "__main__":
    main()
