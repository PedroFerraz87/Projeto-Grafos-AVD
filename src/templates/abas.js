/* [IA] OpenAI Codex – abas locais com suporte a links diretos e setas do teclado. */
(() => {
  const lista = document.querySelector("[data-abas]");
  if (!lista) return;
  const abas = [...lista.querySelectorAll("[data-painel]")];
  const ir = (aba) => {
    for (const item of abas) {
      const ativa = item === aba;
      item.setAttribute("aria-selected", String(ativa));
      item.tabIndex = ativa ? 0 : -1;
      document.getElementById(item.dataset.painel).hidden = !ativa;
    }
  };
  const daAncora = (id) => abas.find(aba => {
    const painel = document.getElementById(aba.dataset.painel);
    return painel.id === id || [...painel.querySelectorAll("[id]")].some(elemento => elemento.id === id);
  });
  const guia = location.hash.slice(1);
  ir(daAncora(guia) || abas[0]);
  for (const aba of abas) {
    aba.addEventListener("click", () => ir(aba));
    aba.addEventListener("keydown", (evento) => {
      const pos = abas.indexOf(aba);
      const esquerda = (pos + abas.length - 1) % abas.length;
      const direita = (pos + 1) % abas.length;
      const alvos = {ArrowLeft:esquerda, ArrowRight:direita, Home:0, End:abas.length-1};
      if (!Object.hasOwn(alvos,evento.key)) return;
      evento.preventDefault();
      const alvo = abas[alvos[evento.key]];
      ir(alvo);
      alvo.focus();
    });
  }
  document.addEventListener("click", (evento) => {
    const link = evento.target.closest("a[href^='#']");
    const aba = link && daAncora(link.getAttribute("href").slice(1));
    if (aba) ir(aba);
  });
  window.addEventListener("hashchange", () => {
    const ativa = daAncora(location.hash.slice(1));
    if (ativa) ir(ativa);
  });
})();
