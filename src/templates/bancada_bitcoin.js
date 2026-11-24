/* [IA] OpenAI Codex – renderização do grafo e reprodução dos eventos registrados. */
(() => {
  const caixa = $("exec-par"), rodar = $("exec-rodar"), replay = $("exec-replay"), passo = $("exec-passo");
  const mensagem = $("exec-mensagem");
  const modoLocal = location.protocol === "http:" && ["127.0.0.1", "localhost"].includes(location.hostname);
  const vistaRede = new RedeBitCoin(dados.rede, $("rede-canvas"), $("rede-resumo"), $("rede-inspecao"));
  const seletorAlgoritmo = $("rede-algoritmo");
  const recentes = new Map();
  const paineis = Object.entries(rotulos).map(([id, nome]) => {
    const elemento = document.createElement("article");
    elemento.className = "exec-panel";
    elemento.dataset.algoritmo = id;
    elemento.innerHTML = '<header><h3></h3><output></output></header><canvas role="img"></canvas><p class="fatos"></p><p class="nota"></p>';
    elemento.querySelector("h3").textContent = nome;
    $("exec-paineis").append(elemento);
    return {id, nome, elemento, canvas:elemento.querySelector("canvas"), marcas:new Map(), aplicado:0};
  });
  let grafo, indice = 0, relogio, ocupado = false;
  for (const [id,nome] of Object.entries(rotulos)) seletorAlgoritmo.add(new Option(nome,id));
  for (const [i, par] of dados.comparacao_caminhos.entries()) {
    caixa.add(new Option(par.origem + " → " + par.destino, i));
  }
  if (!modoLocal) rodar.textContent = "Rodar demonstração";

  function atual() {return dados.comparacao_caminhos[Number(caixa.value)];}

  function exibirRede() {
    const {origem,destino} = atual();
    const id = seletorAlgoritmo.value;
    const painel = paineis.find(p=>p.id===id);
    vistaRede.exibir({fonte:origem,destino,resultado:painel?.resultado,indice,cor:tintas[id]});
    const fatos = painel?.elemento.querySelector(".fatos").textContent;
    $("rede-execucao").textContent = fatos ? rotulos[id]+" · "+fatos+" · "+formatar(painel.resultado.tempo_ms)+" ms" : "";
  }

  function modoCompleto(ativo) {
    $("rede-inteira").hidden = !ativo;
    $("rede-controles").hidden = !ativo;
    $("rede-comparacao").hidden = ativo;
    $("ver-rede").setAttribute("aria-pressed",String(ativo));
    $("ver-quatro").setAttribute("aria-pressed",String(!ativo));
    mostrar(indice);
  }

  function desenhar(painel, destino, fonte) {
    const {canvas, resultado} = painel;
    const {width, height} = canvas.getBoundingClientRect();
    if (!width || !height) return;
    const ratio = Math.min(devicePixelRatio || 1, 2);
    const w = Math.round(width*ratio), h = Math.round(height*ratio);
    if (canvas.width !== w || canvas.height !== h) {canvas.width=w;canvas.height=h;}
    const ctx = canvas.getContext("2d");
    ctx.setTransform(ratio,0,0,ratio,0,0);
    ctx.clearRect(0,0,width,height);
    canvas.setAttribute("aria-label", painel.nome+" no grafo, de "+fonte+" para "+destino);
    if (!grafo) return;
    const {vertices, arcos} = grafo;
    const cor = tintas[painel.id];
    const xy = new Map(vertices.map((id, i) => {
      const theta = i * 2.399963229728653;
      const raio = Math.sqrt(i/Math.max(1,vertices.length-1));
      return [id, [width/2 + Math.cos(theta)*raio*width*.43,
                   height/2 + Math.sin(theta)*raio*height*.39]];
    }));
    xy.set(fonte, [width*.09,height*.49]);
    xy.set(destino, [width*.92,height*.49]);
    painel.coordenadas = xy;
    const n = Math.min(indice,resultado?.eventos.length ?? 0);
    while (painel.aplicado < n) {
      const [id,fase] = resultado.eventos[painel.aplicado++];
      if (xy.has(id)) painel.marcas.set(id,fase);
    }
    const noAtual = n ? resultado.eventos[n-1][0] : fonte;
    const percurso = resultado?.destinos[destino]?.caminho ?? [];
    const ligar = (a,b) => a+":"+b;
    const caminho = new Set(percurso.slice(1).map((v,i)=>ligar(percurso[i],v)));
    const ciclo = new Set((resultado?.ciclo ?? []).map(([a,b])=>ligar(a,b)));
    for (const [origem, alvo] of arcos) {
      const [x,y] = xy.get(origem), [u,v] = xy.get(alvo);
      const temCiclo = ciclo.has(ligar(origem,alvo));
      const temCaminho = caminho.has(ligar(origem,alvo)) && painel.marcas.has(origem) && painel.marcas.has(alvo);
      const angulo = Math.atan2(v-y,u-x);
      ctx.strokeStyle = temCiclo ? "#b3242a" : temCaminho ? cor : "#606a773b";
      ctx.lineWidth = temCiclo ? 2.2 : temCaminho ? 1.6 : .75;
      ctx.beginPath();
      ctx.moveTo(x,y);
      ctx.lineTo(u-3*Math.cos(angulo),v-3*Math.sin(angulo));
      if (temCiclo || temCaminho) {
        ctx.lineTo(u-7*Math.cos(angulo-.38),v-7*Math.sin(angulo-.38));
        ctx.moveTo(u-3*Math.cos(angulo),v-3*Math.sin(angulo));
        ctx.lineTo(u-7*Math.cos(angulo+.38),v-7*Math.sin(angulo+.38));
      }
      ctx.stroke();
    }
    for (const [id,[x,y]] of xy) {
      const marcado = painel.marcas.get(id);
      const especial = id===fonte || id===destino || id===noAtual;
      ctx.fillStyle = id===noAtual ? cor : marcado===1 ? "#9a81ab" : marcado===0 ? cor : "#596476";
      ctx.beginPath();
      ctx.arc(x,y,especial ? 4.8 : 2.85,0,2*Math.PI);
      ctx.fill();
      if (especial) {
        ctx.font = "bold 10px Consolas,monospace";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.strokeStyle = "#f3f1e7";
        ctx.lineWidth = 3;
        ctx.strokeText(id,x,y-10);
        ctx.fillStyle = "#1b2630";
        ctx.fillText(id,x,y-10);
      }
    }
  }

  function mostrar(p) {
    if (p<indice) paineis.forEach(painel=>{painel.aplicado=0;painel.marcas.clear();});
    indice = p;
    passo.value = String(indice);
    $("exec-progresso").textContent = indice+" / "+passo.max+" eventos";
    const {origem,destino} = atual();
    for (const painel of paineis) {
      const resultado = painel.resultado;
      const caso = resultado?.destinos[destino];
      const fase = resultado?.eventos[Math.min(indice,resultado.eventos.length)-1];
      painel.elemento.querySelector("header output").textContent = resultado ? formatar(resultado.tempo_ms)+" ms" : "Aguardando";
      let resumo = "";
      if (caso?.status === "CICLO_NEGATIVO") {
        resumo = "Ciclo de custo "+resultado.ciclo.reduce((t,a)=>t+a[2],0)+" · destino afetado";
      } else if (caso?.status === "INALCANCAVEL") {
        resumo = "Destino inalcançável";
      } else if (caso?.status === "ARVORE_DFS") {
        resumo = caso.passos+" arcos na árvore DFS";
      } else if (caso) {
        resumo = caso.passos+" arcos · custo "+caso.custo;
      }
      painel.elemento.querySelector(".fatos").textContent = resumo;
      painel.elemento.querySelector(".nota").textContent = resultado
        ? inteiro.format(resultado.alcancados)+" usuários alcançados"+(fase ? " · "+(fase[1]===1?"finalizou ":"visitou ")+fase[0] : "")
        : "";
      desenhar(painel,destino,origem);
    }
    exibirRede();
  }

  function carregar(experimento) {
    grafo = experimento?.grafo;
    for (const painel of paineis) {
      painel.resultado = experimento?.resultados.find(r=>r.algoritmo===painel.id);
      painel.aplicado = 0;
      painel.marcas.clear();
    }
    passo.max = Math.max(0,...paineis.map(p=>p.resultado?.eventos.length ?? 0));
    passo.disabled = Number(passo.max)===0;
    replay.disabled = passo.disabled || ocupado;
    mostrar(0);
    $("usuarios-grafo").textContent = grafo ? "Desenho: "+grafo.vertices.length+" usuários e "+grafo.arcos.length+" avaliações reais." : "";
  }

  function pausar() {
    clearInterval(relogio);
    relogio = undefined;
    replay.textContent = "Reproduzir";
  }

  function reproduzir() {
    if (relogio) {pausar();return;}
    if (indice >= Number(passo.max)) mostrar(0);
    replay.textContent = "Pausar";
    const salto = Math.max(1,Math.ceil(Number(passo.max)/135));
    relogio = setInterval(()=>{
      mostrar(Math.min(indice+salto,Number(passo.max)));
      if (indice===Number(passo.max)) pausar();
    },75);
  }

  function preparar() {
    pausar();
    const {origem} = atual();
    carregar(recentes.get(origem) || dados.experimentos?.[origem]);
    mensagem.textContent = modoLocal
      ? "Clique em Rodar os quatro para calcular novamente na máquina local."
      : "Modo offline. A demonstração reproduz execuções registradas no dataset completo.";
    rodar.disabled = !modoLocal && !grafo;
  }

  async function executar() {
    if (!modoLocal) {if (relogio) pausar(); mostrar(0); reproduzir();return;}
    pausar();
    rodar.disabled = caixa.disabled = ocupado = true;
    const {origem} = atual();
    const experimento = {resultados: [], grafo:dados.experimentos?.[origem]?.grafo};
    carregar(experimento);
    try {
      mensagem.textContent = "Executando BFS, DFS, Dijkstra e Bellman-Ford em sequência. Bellman-Ford pode levar mais tempo.";
      const resposta = await fetch("/api/execucao?fonte="+origem,{method:"POST"});
      if (!resposta.ok || !resposta.headers.get("content-type")?.includes("ndjson")) {
        throw new Error("Servidor indisponível ou ocupado. Use python -m src.avd.servidor_bitcoin.");
      }
      const leitor = resposta.body.pipeThrough(new TextDecoderStream()).getReader();
      let buffer = "";
      for (;;) {
        const leitura = await leitor.read();
        if (leitura.done) break;
        buffer += leitura.value;
        const linhas = buffer.split("\n");
        buffer = linhas.pop();
        for (const linha of linhas) {
          const comando = JSON.parse(linha);
          if (comando.grafo) experimento.grafo = comando.grafo;
          if (comando.resultado) {
            experimento.resultados.push(comando.resultado);
            mensagem.textContent = experimento.resultados.length+"/4 concluídos. Último: "+rotulos[comando.resultado.algoritmo]+".";
          }
          carregar(experimento);
        }
      }
      if (experimento.resultados.length!==4 || !experimento.grafo) throw new Error("A execução foi interrompida.");
      recentes.set(origem,experimento);
      mensagem.textContent = "Quatro execuções concluídas nesta máquina. Reproduzindo os eventos registrados.";
      reproduzir();
    } catch (erro) {
      carregar(recentes.get(origem) || dados.experimentos?.[origem]);
      mensagem.textContent = erro.message;
    } finally {
      rodar.disabled = caixa.disabled = ocupado = false;
      replay.disabled = Number(passo.max)===0;
    }
  }

  rodar.addEventListener("click",executar);
  replay.addEventListener("click",reproduzir);
  passo.addEventListener("input",()=>{pausar();mostrar(Number(passo.value));});
  caixa.addEventListener("change",preparar);
  seletorAlgoritmo.addEventListener("change",exibirRede);
  $("ver-rede").addEventListener("click",()=>modoCompleto(true));
  $("ver-quatro").addEventListener("click",()=>modoCompleto(false));
  $("rede-controles").addEventListener("submit",evento=>{
    evento.preventDefault();
    vistaRede.localizar(Number($("rede-usuario").value));
  });
  $("rede-reduzir").addEventListener("click",()=>vistaRede.mudarZoom(1/1.3));
  $("rede-ampliar").addEventListener("click",()=>vistaRede.mudarZoom(1.3));
  $("rede-enquadrar").addEventListener("click",()=>vistaRede.enquadrar());
  const observador = new ResizeObserver(()=>{
    const {origem,destino} = atual();
    paineis.forEach(p=>desenhar(p,destino,origem));
  });
  for (const painel of paineis) {
    observador.observe(painel.canvas);
    painel.canvas.addEventListener("click",evento=>{
      const {left,top} = painel.canvas.getBoundingClientRect();
      const vizinho = [...(painel.coordenadas ?? [])].find(([, [x,y]])=>
        Math.hypot(evento.clientX-left-x,evento.clientY-top-y)<7);
      if (vizinho) {
        const id = vizinho[0];
        const saindo = grafo.arcos.filter(([a])=>a===id).length;
        $("usuarios-grafo").textContent = "Usuário "+id+" · "+saindo+" avaliações de saída entre os usuários desenhados.";
      }
    });
  }
  preparar();
})();
