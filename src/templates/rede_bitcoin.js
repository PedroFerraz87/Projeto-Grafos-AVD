/* [IA] OpenAI Codex – exploração visual da topologia real do Bitcoin Alpha. */
class RedeBitCoin {
  constructor(rede, canvas, resumo, inspecao) {
    this.rede = rede;
    this.canvas = canvas;
    this.resumo = resumo;
    this.inspecao = inspecao;
    this.fundo = document.createElement("canvas");
    this.zoom = 1;
    this.dx = this.dy = 0;
    this.arcosPorUsuario = new Map(rede.vertices.map(id=>[id,[]]));
    for (const arco of rede.arcos) {
      this.arcosPorUsuario.get(arco[0]).push(arco);
      if (arco[1] !== arco[0]) this.arcosPorUsuario.get(arco[1]).push(arco);
    }
    canvas.addEventListener("pointerdown", e => {
      this.arraste = {x:e.clientX, y:e.clientY, dx:this.dx, dy:this.dy};
      canvas.setPointerCapture(e.pointerId);
      canvas.classList.add("arrastando");
    });
    canvas.addEventListener("pointermove", e => {
      if (!this.arraste) return;
      this.dx = this.arraste.dx + e.clientX - this.arraste.x;
      this.dy = this.arraste.dy + e.clientY - this.arraste.y;
      this.atualizarFundo();
    });
    const soltar = (e) => {
      const inicio = this.arraste;
      this.arraste = null;
      canvas.classList.remove("arrastando");
      if (!inicio || e.type !== "pointerup" || Math.hypot(e.clientX-inicio.x,e.clientY-inicio.y) > 4) return;
      const caixa = canvas.getBoundingClientRect();
      const x = e.clientX - caixa.left, y = e.clientY - caixa.top;
      let escolhido, distancia = 10;
      for (const [id,[p,q]] of this.posicoes ?? []) {
        const d = Math.hypot(x-p,y-q);
        if (d < distancia) {distancia=d;escolhido=id;}
      }
      if (escolhido !== undefined) this.localizar(escolhido,false);
    };
    canvas.addEventListener("pointerup", soltar);
    canvas.addEventListener("pointercancel", soltar);
    canvas.addEventListener("wheel", e => {
      if (!e.ctrlKey && !e.metaKey) return;
      e.preventDefault();
      this.mudarZoom(e.deltaY<0 ? 1.2 : 1/1.2);
    }, {passive:false});
    new ResizeObserver(()=>this.atualizarFundo()).observe(canvas);
  }

  preparar(fonte) {
    if (fonte === this.fonte) return;
    this.fonte = fonte;
    const niveis = this.rede.niveis[fonte] ?? {};
    const maiorNivel = Math.max(1,...Object.values(niveis));
    const grupos = new Map();
    for (const id of this.rede.vertices) {
      const nivel = niveis[id] ?? (maiorNivel+1);
      if (!grupos.has(nivel)) grupos.set(nivel, []);
      grupos.get(nivel).push(id);
    }
    this.origem = new Map();
    for (const [nivel,grupo] of grupos) {
      grupo.forEach((id,i)=>{
        const angulo = i*2.399963229728653+0.6*nivel;
        const raio = nivel ? (nivel-.6+Math.sqrt((i+1)/grupo.length))/(maiorNivel+1.5) : 0;
        this.origem.set(id,[raio*Math.cos(angulo),raio*Math.sin(angulo)]);
      });
    }
    this.enquadrar();
  }

  atualizarFundo() {
    if (!this.origem) return;
    this.fundoSujo = true;
    if (this.quadroPendente) return;
    this.quadroPendente = requestAnimationFrame(() => {
      this.quadroPendente = undefined;
      this.desenhar();
    });
  }

  refazerFundo(largura,altura,scale) {
    this.fundo.width = Math.round(largura*scale);
    this.fundo.height = Math.round(altura*scale);
    this.canvas.width = this.fundo.width;
    this.canvas.height = this.fundo.height;
    const ctx = this.fundo.getContext("2d");
    ctx.setTransform(scale,0,0,scale,0,0);
    this.posicoes = new Map();
    for (const [id,[x,y]] of this.origem) {
      this.posicoes.set(id,[largura/2+this.dx+x*largura*.46*this.zoom,
                           altura/2+this.dy+y*altura*.46*this.zoom]);
    }
    ctx.beginPath();
    for (const [a,b] of this.rede.arcos) {
      const [x,y] = this.posicoes.get(a), [u,v] = this.posicoes.get(b);
      ctx.moveTo(x,y);
      ctx.lineTo(u,v);
    }
    ctx.strokeStyle = "#67789517";
    ctx.lineWidth = .66;
    ctx.stroke();
    ctx.fillStyle = "#465874a2";
    for (const [x,y] of this.posicoes.values()) ctx.fillRect(x-1,y-1,2,2);
    this.fundoSujo = false;
  }

  exibir({fonte,destino,resultado,indice,cor}) {
    this.dados = {fonte,destino,resultado,indice,cor};
    this.preparar(fonte);
    this.desenhar();
  }

  desenhar() {
    if (!this.origem || !this.dados) return;
    const {width,height} = this.canvas.getBoundingClientRect();
    if (!width || !height) return;
    const scale = Math.min(devicePixelRatio || 1, 2);
    if (this.fundoSujo || this.canvas.width!==Math.round(width*scale) || this.canvas.height!==Math.round(height*scale)) {
      this.refazerFundo(width,height,scale);
    }
    const {fonte,destino,resultado,indice,cor} = this.dados;
    const ctx = this.canvas.getContext("2d");
    ctx.setTransform(1,0,0,1,0,0);
    ctx.clearRect(0,0,this.canvas.width,this.canvas.height);
    ctx.drawImage(this.fundo,0,0);
    ctx.setTransform(scale,0,0,scale,0,0);
    const eventos = resultado?.eventos ?? [];
    const contagem = Math.min(indice,eventos.length);
    const visitados = new Map();
    for (let i=0;i<contagem;i++) visitados.set(...eventos[i]);
    for (const [id,fase] of visitados) {
      const [x,y] = this.posicoes.get(id);
      ctx.fillStyle = cor;
      ctx.globalAlpha = fase===1 ? .42 : .9;
      ctx.fillRect(x-1.55,y-1.55,3.1,3.1);
    }
    ctx.globalAlpha = 1;
    const arco = (a,b,tinta,espessura) => {
      const [x,y] = this.posicoes.get(a), [u,v] = this.posicoes.get(b);
      const t = Math.atan2(v-y,u-x);
      ctx.strokeStyle = tinta; ctx.lineWidth = espessura; ctx.beginPath();
      ctx.moveTo(x,y); ctx.lineTo(u-3*Math.cos(t),v-3*Math.sin(t));
      ctx.lineTo(u-8*Math.cos(t-.42),v-8*Math.sin(t-.42));
      ctx.moveTo(u-3*Math.cos(t),v-3*Math.sin(t));
      ctx.lineTo(u-8*Math.cos(t+.42),v-8*Math.sin(t+.42));
      ctx.stroke();
    };
    const caminho = resultado?.destinos[destino]?.caminho ?? [];
    caminho.forEach((id,i) => {
      if (i && visitados.has(id) && visitados.has(caminho[i-1])) arco(caminho[i-1],id,cor,1.6);
    });
    for (const [a,b] of resultado?.ciclo ?? []) arco(a,b,"#a92533",2.2);
    for (const [a,b,peso] of this.arcosPorUsuario.get(this.selecionado) ?? []) {
      arco(a,b,peso<0 ? "#a925336e" : "#224caa66",1);
    }
    const atual = contagem ? eventos[contagem-1][0] : fonte;
    for (const [id,tinta] of new Map([[fonte,"#243953"],[destino,"#974015"],[atual,cor],[this.selecionado,"#123eaa"]])) {
      if (id === undefined) continue;
      const [x,y]=this.posicoes.get(id);
      ctx.beginPath();ctx.arc(x,y,5,0,2*Math.PI);
      ctx.fillStyle=tinta;ctx.fill();
      ctx.strokeStyle="#fffdf4";ctx.lineWidth=1.4;ctx.stroke();
      ctx.font="bold 12px Consolas,monospace";ctx.textAlign="center";
      ctx.lineWidth=3;ctx.strokeText(id,x,y-9);
      ctx.fillStyle="#1e2b3a";ctx.fillText(id,x,y-9);
    }
    this.resumo.textContent = this.rede.vertices.length.toLocaleString("pt-BR")+" usuários · "+
      this.rede.arcos.length.toLocaleString("pt-BR")+" avaliações · usuário atual "+atual+" · "+
      contagem.toLocaleString("pt-BR")+"/"+eventos.length.toLocaleString("pt-BR")+" eventos";
  }

  localizar(id,centrar=true) {
    if (!this.origem?.has(id)) {
      this.inspecao.textContent = "Usuário não encontrado na rede.";
      return;
    }
    this.selecionado = id;
    if (centrar) {
      const [x,y] = this.origem.get(id);
      this.dx = -x*this.canvas.clientWidth*.46*this.zoom;
      this.dy = -y*this.canvas.clientHeight*.46*this.zoom;
    }
    let entrada = 0, saida = 0;
    for (const [a,b] of this.arcosPorUsuario.get(id)) {
      if (a===id) saida++;
      if (b===id) entrada++;
    }
    this.inspecao.textContent = "Usuário "+id+" · "+entrada+" avaliações recebidas · "+saida+" avaliações enviadas.";
    this.atualizarFundo();
  }

  mudarZoom(fator) {
    const proximo = Math.max(.7,Math.min(8,this.zoom*fator));
    this.dx *= proximo/this.zoom;
    this.dy *= proximo/this.zoom;
    this.zoom = proximo;
    this.atualizarFundo();
  }

  enquadrar() {
    this.zoom = 1;
    this.dx = this.dy = 0;
    this.atualizarFundo();
  }
}
