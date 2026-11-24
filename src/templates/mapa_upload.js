/* [IA] OpenAI Codex – envio local de mapa, reaproveitado pelas vistas do site. */
(() => {
  const modoLocal = location.protocol === "http:" && ["127.0.0.1", "localhost"].includes(location.hostname);
  const chave = "grafos-mapa-enviado-v1";
  const tipo = document.body.dataset.vistaMapa;
  const dados = document.getElementById("dados");
  const form = document.getElementById("enviar-mapa");
  const mostrar = (texto) => {
    const status = document.getElementById("upload-status");
    if (status) status.textContent = texto;
  };
  if (location.hash === "#enviar-mapa" && form) {
    window.addEventListener("load", () => form.scrollIntoView(), {once: true});
  }

  if (modoLocal) {
    try {
      const salvo = JSON.parse(sessionStorage.getItem(chave));
      if (salvo?.[tipo]?.mapas?.mapa_enviado) {
        const base = JSON.parse(dados.textContent);
        base.mapas.mapa_enviado = salvo[tipo].mapas.mapa_enviado;
        base.mapa_inicial = "mapa_enviado";
        dados.textContent = JSON.stringify(base);
        mostrar("Mapa carregado: " + salvo.nome);
        const link = document.getElementById("upload-quatro");
        if (link) link.hidden = false;
      }
    } catch {
      mostrar("O mapa anterior não pôde ser recuperado. Você pode enviá-lo novamente.");
    }
  }

  if (!form) return;
  const input = document.getElementById("upload-arquivo");
  const botao = form.querySelector("button");
  if (!modoLocal) {
    input.disabled = botao.disabled = true;
    const link = document.getElementById("upload-abrir-local");
    link.href = "http://127.0.0.1:8765/labirinto_interativo.html#enviar-mapa";
    link.hidden = false;
    mostrar("Abra o painel local para enviar um labirinto e calcular os resultados.");
    return;
  }

  form.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    const arquivo = input.files[0];
    if (!arquivo) return;
    input.disabled = botao.disabled = true;
    mostrar("Validando o mapa e executando os quatro algoritmos…");
    try {
      const resposta = await fetch("/api/labirintos", {method: "POST", body: arquivo});
      if (!resposta.headers.get("content-type")?.includes("application/json")) {
        throw new Error("O serviço de mapas está indisponível. Confira se o servidor local está atualizado.");
      }
      const resultado = await resposta.json();
      if (!resposta.ok) throw new Error(resultado.erro || "Não foi possível analisar o mapa.");
      try {
        sessionStorage.setItem(chave, JSON.stringify({...resultado, nome: arquivo.name}));
      } catch {
        throw new Error("O navegador não conseguiu guardar a análise nesta aba. Experimente um mapa menor.");
      }
      history.replaceState(null, "", "#mapa_enviado/BFS/0");
      location.reload();
    } catch (erro) {
      mostrar(erro.message);
    } finally {
      input.disabled = botao.disabled = false;
    }
  });
})();
