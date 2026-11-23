/* [IA] OpenAI Codex – visualização sincronizada dos percursos e projeção em relevo. */
(() => {
  const mesa = document.getElementById("mesa-de-rotas");
  if (!mesa) return;

  const leitura = document.getElementById("dados");
  if (!leitura) return;
  const dados = JSON.parse(leitura.textContent);
  const nomesDosMapas = Object.keys(dados.mapas);
  const algoritmos = dados.algoritmos.filter((nome) => nomesDosMapas.some((id) => dados.mapas[id].percursos[nome]));
  if (!nomesDosMapas.length || !algoritmos.length) {
    mesa.hidden = true;
    return;
  }

  const rotulos = { BFS: "BFS", DIJKSTRA: "Dijkstra", BELLMAN_FORD: "Bellman-Ford" };
  const estados = {
    OK: "Percurso encontrado",
    RECUSA: "Recusa de peso negativo",
    CICLO_NEGATIVO: "Ciclo negativo",
    SEM_SOLUCAO: "Sem solução",
  };
  const notas = {
    RECUSA: "Este mapa tem uma aresta com peso negativo.",
    CICLO_NEGATIVO: "Um ciclo de custo negativo pode alcançar a saída.",
    SEM_SOLUCAO: "A saída é inalcançável.",
    INDISPONIVEL: "O relatório não inclui este algoritmo para o mapa.",
  };
  const terrenos = {
    ".": "#192a35", ",": "#44382d", "~": "#1f4257",
    S: "#355144", G: "#58622e", "+": "#513d36", "*": "#493347",
  };
  const simbolos = { ">": "→", "<": "←", "^": "↑", v: "↓" };

  const porId = (id) => document.getElementById(id);
  const seletorMapa = porId("mesa-mapa");
  const botaoRelevo = porId("mesa-relevo");
  const botaoPlanta = porId("mesa-planta");
  const tempo = porId("mesa-tempo");
  const indicador = porId("mesa-passo");
  const resumo = porId("mesa-resumo");
  const reproduzir = porId("mesa-reproduzir");
  const reiniciar = porId("mesa-reiniciar");
  const anterior = porId("mesa-anterior");
  const proximo = porId("mesa-proximo");
  const canais = ["a", "b"].map((lado) => {
    const caixa = mesa.querySelector('[data-mesa-canal="' + lado + '"]');
    return {
      seletor: porId("mesa-algoritmo-" + lado),
      quadro: porId("mesa-quadro-" + lado),
      cor: getComputedStyle(caixa).getPropertyValue("--mesa-sinal").trim(),
      status: caixa.querySelector("[data-mesa-status]"),
      passos: caixa.querySelector("[data-mesa-passos]"),
      custo: caixa.querySelector("[data-mesa-custo]"),
      acumulado: caixa.querySelector("[data-mesa-acumulado]"),
      nota: caixa.querySelector("[data-mesa-nota]"),
      percurso: null,
      desenho: null,
    };
  });

  const opcoesDoLaboratorio = document.getElementById("mapa")?.options ?? [];
  const nomesAmigaveis = new Map(Array.from(opcoesDoLaboratorio, (opcao) => [opcao.value, opcao.text]));
  nomesDosMapas.forEach((id) => {
    seletorMapa.add(new Option(nomesAmigaveis.get(id) ?? id.replaceAll("_", " "), id));
  });
  seletorMapa.value = nomesDosMapas.includes(dados.mapa_inicial) ? dados.mapa_inicial : nomesDosMapas[0];
  canais.forEach(({ seletor }, index) => {
    algoritmos.forEach((nome) => seletor.add(new Option(rotulos[nome] ?? nome, nome)));
    seletor.selectedIndex = Math.min(index, algoritmos.length - 1);
  });

  let mapa;
  let girarEmRelevo = true;
  let passo = 0;
  let limite = 0;
  let animacao = null;

  function parar() {
    if (animacao !== null) clearInterval(animacao);
    animacao = null;
    reproduzir.textContent = "Reproduzir";
  }

  function poligono(ctx, vertices, preenchimento, borda) {
    ctx.beginPath();
    vertices.forEach(([x, y], i) => {
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.closePath();
    ctx.fillStyle = preenchimento;
    ctx.fill();
    if (borda) {
      ctx.strokeStyle = borda;
      ctx.lineWidth = .65;
      ctx.stroke();
    }
  }

  function projecao(largura, altura, linhas, colunas) {
    const margem = Math.min(35, largura * .075, altura * .11);
    if (!girarEmRelevo) {
      const unidade = Math.min((largura - 2 * margem) / colunas, (altura - 2 * margem) / linhas);
      const x = (largura - colunas * unidade) / 2;
      const y = (altura - linhas * unidade) / 2;
      return { unidade, parede: 0, ponto: (c, l) => [x + c * unidade, y + l * unidade] };
    }
    const eixo = linhas + colunas;
    const unidade = Math.min((largura - 2 * margem) / (eixo * .93), (altura - 2 * margem) / (eixo * .43 + .83));
    const horizontal = unidade * .93;
    const diagonal = unidade * .43;
    const parede = unidade * .83;
    const x = (largura - eixo * horizontal) / 2 + linhas * horizontal;
    const y = (altura - eixo * diagonal + parede) / 2;
    return { unidade, parede, ponto: (c, l, z = 0) => [x + (c - l) * horizontal, y + (c + l) * diagonal - z] };
  }

  function quadrante(ponto, c, l, z) {
    return [ponto(c, l, z), ponto(c + 1, l, z), ponto(c + 1, l + 1, z), ponto(c, l + 1, z)];
  }

  function corDoPiso(simbolo) {
    if (terrenos[simbolo]) return terrenos[simbolo];
    if ("abcd".includes(simbolo)) return "#50462f";
    if ("ABCD".includes(simbolo)) return "#344652";
    if (simbolos[simbolo]) return "#243947";
    return "#192a35";
  }

  function pintarPiso(ctx, grade, plano) {
    const { ponto, unidade } = plano;
    const linhas = grade.length;
    const colunas = grade[0].length;
    poligono(ctx, [ponto(0, 0), ponto(colunas, 0), ponto(colunas, linhas), ponto(0, linhas)], "#121f2a", "#59798a");
    grade.forEach((linha, l) => {
      Array.from(linha).forEach((simbolo, c) => {
        if (simbolo === "#") return;
        poligono(ctx, quadrante(ponto, c, l), corDoPiso(simbolo), "#314651");
        if (simbolo === "." || simbolo === "," || unidade < 8) return;
        const [x, y] = ponto(c + .5, l + .5);
        ctx.font = "650 " + Math.round(Math.min(12, unidade * .5)) + "px system-ui, sans-serif";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillStyle = "abcd".includes(simbolo) ? "#ffe5a3" : "#d4e4ee";
        ctx.fillText(simbolos[simbolo] ?? simbolo, x, y);
      });
    });
  }

  function pintarParedes(ctx, grade, plano) {
    const { ponto, parede } = plano;
    const paredes = [];
    grade.forEach((linha, l) => {
      Array.from(linha).forEach((simbolo, c) => {
        if (simbolo === "#") paredes.push([c, l]);
      });
    });
    paredes.sort(([c1, l1], [c2, l2]) => c1 + l1 - c2 - l2);
    paredes.forEach(([c, l]) => {
      const topo = quadrante(ponto, c, l, parede);
      if (parede) {
        const base = quadrante(ponto, c, l, 0);
        poligono(ctx, [topo[3], topo[2], base[2], base[3]], "#293f50", "#182a37");
        poligono(ctx, [topo[1], topo[2], base[2], base[1]], "#1f303d", "#182a37");
      }
      poligono(ctx, topo, parede ? "#4f687b" : "#364c5d", parede ? "#738ea0" : "#486171");
    });
  }

  function camada(largura, altura, pixel) {
    const papel = document.createElement("canvas");
    papel.width = Math.ceil(largura * pixel);
    papel.height = Math.ceil(altura * pixel);
    const contexto = papel.getContext("2d");
    contexto.setTransform(pixel, 0, 0, pixel, 0, 0);
    return { papel, contexto };
  }

  function prepararQuadro(canal) {
    const { width: largura, height: altura } = canal.quadro.getBoundingClientRect();
    if (!largura || !altura) return;
    const pixel = Math.min(window.devicePixelRatio || 1, 2);
    const plano = projecao(largura, altura, mapa.grade.length, mapa.grade[0].length);
    canal.quadro.width = Math.ceil(largura * pixel);
    canal.quadro.height = Math.ceil(altura * pixel);
    const ctx = canal.quadro.getContext("2d");
    if (!ctx) return;
    ctx.setTransform(pixel, 0, 0, pixel, 0, 0);
    const piso = camada(largura, altura, pixel);
    const paredes = camada(largura, altura, pixel);
    pintarPiso(piso.contexto, mapa.grade, plano);
    pintarParedes(paredes.contexto, mapa.grade, plano);
    canal.desenho = { ctx, largura, altura, plano, piso: piso.papel, paredes: paredes.papel };
  }

  function pintarTrilha(ctx, trajeto, trecho, plano, cor, sobreposto = false) {
    ctx.save();
    ctx.strokeStyle = cor;
    ctx.lineWidth = Math.max(1.5, plano.unidade * .19);
    ctx.lineJoin = "round";
    ctx.lineCap = "round";
    if (sobreposto) {
      // O tracejado mantém legíveis os trechos que passam atrás de paredes altas.
      ctx.globalAlpha = .52;
      ctx.lineWidth *= .58;
      ctx.setLineDash([Math.max(2, plano.unidade * .24), Math.max(2, plano.unidade * .23)]);
    } else {
      ctx.shadowColor = cor;
      ctx.shadowBlur = Math.min(8, plano.unidade * .35);
    }
    ctx.beginPath();
    for (let i = 0; i <= trecho; i++) {
      const { linha, coluna } = trajeto[i];
      const [x, y] = plano.ponto(coluna + .5, linha + .5);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
    ctx.restore();
  }

  function pintarPosicao(ctx, item, plano, cor) {
    const { ponto, parede, unidade } = plano;
    const c = item.coluna + .5;
    const l = item.linha + .5;
    const [x, y] = ponto(c, l, parede * 1.35);
    const [, piso] = ponto(c, l);
    ctx.save();
    ctx.strokeStyle = cor;
    ctx.fillStyle = cor;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(x, piso);
    ctx.stroke();
    ctx.shadowColor = cor;
    ctx.shadowBlur = 9;
    ctx.beginPath();
    ctx.arc(x, y, Math.max(2.5, unidade * .18), 0, Math.PI * 2);
    ctx.fill();
    ctx.shadowBlur = 0;
    ctx.strokeStyle = "#f7f9fb";
    ctx.stroke();
    ctx.restore();
  }

  function pintarCanal(canal) {
    const trajeto = canal.percurso?.percurso ?? [];
    const trecho = Math.min(passo, trajeto.length - 1);
    const item = trajeto[trecho];
    canal.acumulado.textContent = item?.custo_acumulado ?? "—";
    const nome = rotulos[canal.seletor.value] ?? canal.seletor.value;
    const descricao = item ? "Passo " + trecho + " de " + canal.percurso.passos : canal.status.textContent;
    canal.quadro.setAttribute("aria-label", nome + ". " + descricao + ".");
    if (!canal.desenho) return;
    const { ctx, largura, altura, plano, piso, paredes } = canal.desenho;
    ctx.clearRect(0, 0, largura, altura);
    ctx.drawImage(piso, 0, 0, largura, altura);
    if (item) pintarTrilha(ctx, trajeto, trecho, plano, canal.cor);
    ctx.drawImage(paredes, 0, 0, largura, altura);
    if (item && plano.parede) pintarTrilha(ctx, trajeto, trecho, plano, canal.cor, true);
    if (item) pintarPosicao(ctx, item, plano, canal.cor);
  }

  function atualizarTempo(destino) {
    passo = Math.max(0, Math.min(limite, destino));
    tempo.value = passo;
    indicador.textContent = "Passo " + passo + " de " + limite;
    reiniciar.disabled = passo === 0;
    anterior.disabled = passo === 0;
    proximo.disabled = passo === limite;
    canais.forEach(pintarCanal);
  }

  function formatarDiferenca(valor, unidade) {
    if (valor === 0) return "mesmo " + unidade;
    const absoluto = Math.abs(valor);
    return absoluto + " " + unidade + (unidade === "passo" && absoluto !== 1 ? "s" : "") + (valor > 0 ? " a mais" : " a menos");
  }

  function atualizarComparacao() {
    parar();
    mapa = dados.mapas[seletorMapa.value];
    canais.forEach((canal) => {
      canal.percurso = mapa.percursos[canal.seletor.value];
      const estado = canal.percurso?.status ?? "INDISPONIVEL";
      canal.status.dataset.status = estado;
      canal.status.textContent = estados[estado] ?? "Sem dados";
      canal.passos.textContent = canal.percurso?.passos ?? "—";
      canal.custo.textContent = canal.percurso?.custo ?? "—";
      canal.nota.textContent = notas[estado] ?? canal.percurso?.observacao ?? "";
      prepararQuadro(canal);
    });
    const [a, b] = canais.map(({ percurso }) => percurso);
    limite = Math.max(0, ...canais.map(({ percurso }) => (percurso?.percurso?.length ?? 0) - 1));
    tempo.max = limite;
    tempo.disabled = limite === 0;
    reproduzir.disabled = limite === 0;
    const nomes = canais.map(({ seletor }) => rotulos[seletor.value] ?? seletor.value);
    if (a?.status === "OK" && b?.status === "OK") {
      const passos = formatarDiferenca(b.passos - a.passos, "passo");
      const diferenca = b.custo - a.custo;
      const custo = diferenca === 0 ? "mesmo custo" : "custo " + Math.abs(diferenca) + (diferenca > 0 ? " maior" : " menor");
      resumo.textContent = nomes[1] + " em relação a " + nomes[0] + ": " + passos + " e " + custo + ".";
    } else if (limite > 0) {
      resumo.textContent = "A linha do tempo acompanha o percurso disponível.";
    } else {
      resumo.textContent = "Escolha outro mapa ou algoritmo para ver um percurso.";
    }
    atualizarTempo(0);
  }

  function mudarVista(relevo) {
    girarEmRelevo = relevo;
    mesa.dataset.vista = relevo ? "relevo" : "planta";
    botaoRelevo.setAttribute("aria-pressed", relevo);
    botaoPlanta.setAttribute("aria-pressed", !relevo);
    canais.forEach(prepararQuadro);
    atualizarTempo(passo);
  }

  seletorMapa.addEventListener("change", atualizarComparacao);
  canais.forEach(({ seletor }) => seletor.addEventListener("change", atualizarComparacao));
  botaoRelevo.addEventListener("click", () => mudarVista(true));
  botaoPlanta.addEventListener("click", () => mudarVista(false));
  tempo.addEventListener("input", () => {
    parar();
    atualizarTempo(Number(tempo.value));
  });
  [[reiniciar, () => 0], [anterior, () => passo - 1], [proximo, () => passo + 1]].forEach(([botao, destino]) => {
    botao.addEventListener("click", () => {
      parar();
      atualizarTempo(destino());
    });
  });
  reproduzir.addEventListener("click", () => {
    if (animacao !== null) {
      parar();
      return;
    }
    if (passo === limite) atualizarTempo(0);
    reproduzir.textContent = "Pausar";
    animacao = setInterval(() => {
      atualizarTempo(passo + 1);
      if (passo === limite) parar();
    }, 275);
  });
  const observador = new ResizeObserver(() => {
    canais.forEach(prepararQuadro);
    atualizarTempo(passo);
  });
  canais.forEach(({ quadro }) => observador.observe(quadro));
  mesa.dataset.vista = "relevo";
  atualizarComparacao();
})();
