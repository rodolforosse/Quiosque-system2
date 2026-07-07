// JS do Caixa (separado do template)
// Este arquivo é carregado por app/templates/site/caixa.html no bloco extra_js

(function () {
  function formatMoneyBR(value) {
    return 'R$ ' + value.toFixed(2).replace('.', ',');
  }

  function mapMetodoLabel(m) {
    const mapa = {
      'dinheiro': 'Dinheiro',
      'pix': 'PIX',
      'cartao_debito': 'Cartão de Débito',
      'cartao_credito': 'Cartão de Crédito',
      'cheque': 'Cheque'
    };
    return mapa[m] || (m ? String(m).replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase()) : 'Desconhecido');
  }

  async function carregarMovimentacoesCaixa() {
    const btn = document.getElementById('btn-carregar-movimentacoes');
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Carregando...';
    }

    try {
      const resp = await fetch('/caixa/movimentacoes.json', { credentials: 'same-origin' });
      if (!resp.ok) throw new Error('Resposta HTTP ' + resp.status);
      const data = await resp.json();
      if (!data.success) throw new Error(data.error || 'Erro ao obter movimentações');

      const body = document.getElementById('tabela-movimentacoes-body');
      body.innerHTML = '';

      let totalEntradas = 0, totalSaidas = 0;
      const porForma = {};

      if (!data.movimentacoes || data.movimentacoes.length === 0) {
        body.innerHTML = '<tr><td colspan="5" class="text-center text-muted py-5">Nenhuma movimentação encontrada para este caixa.</td></tr>';
      } else {
        data.movimentacoes.forEach(m => {
          const tr = document.createElement('tr');

          const dt = new Date(m.date);
          const hora = dt.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'});
          const dataStr = hora + ' ' + dt.toLocaleDateString();

          const entradaText = (m.entrada && m.entrada > 0) ? formatMoneyBR(Number(m.entrada)) : '-';
          const saidaText = (m.saida && m.saida > 0) ? formatMoneyBR(Number(m.saida)) : '-';

          tr.innerHTML = `
            <td class="small">${dataStr}</td>
            <td class="small">${m.description || ''}</td>
            <td class="text-end small text-success">${entradaText}</td>
            <td class="text-end small text-danger">${saidaText}</td>
            <td class="small">${mapMetodoLabel(m.metodo_pagamento)}</td>
          `;

          body.appendChild(tr);

          totalEntradas += Number(m.entrada || 0);
          totalSaidas += Number(m.saida || 0);
          const forma = m.metodo_pagamento || 'dinheiro';
          porForma[forma] = (porForma[forma] || 0) + Number(m.entrada || 0) - Number(m.saida || 0);
        });
      }

      // Atualiza painel lateral
      const painel = document.getElementById('relatorio-caixa-body');
      const saldoInicial = (typeof window.caixa !== 'undefined' && window.caixa.valor_inicial) ? Number(window.caixa.valor_inicial) : 0.0;
      const saldoFinal = saldoInicial + totalEntradas - totalSaidas;

      let formasHtml = '';
      Object.keys(porForma).forEach(f => {
        formasHtml += `<div class="d-flex justify-content-between"><small>${mapMetodoLabel(f)}</small><strong>${formatMoneyBR(porForma[f])}</strong></div>`;
      });

      painel.innerHTML = `
        <div class="d-flex justify-content-between"><small>Total entradas</small><strong>${formatMoneyBR(totalEntradas)}</strong></div>
        <div class="d-flex justify-content-between"><small>Total saídas</small><strong>${formatMoneyBR(totalSaidas)}</strong></div>
        <div class="d-flex justify-content-between text-danger"><small>Total itens cancelados</small><strong>R$ 0,00</strong></div>
        <hr>
        <div class="d-flex justify-content-between"><small>Saldo inicial</small><strong>${formatMoneyBR(saldoInicial)}</strong></div>
        <div class="d-flex justify-content-between"><small>Saldo final</small><strong>${formatMoneyBR(saldoFinal)}</strong></div>
        <hr>
        ${formasHtml || '<p class="text-muted small">Nenhuma forma de pagamento registrada.</p>'}
        <hr>
        <div class="d-flex justify-content-between"><strong>TOTAL</strong><strong>${formatMoneyBR(saldoFinal)}</strong></div>
      `;

    } catch (err) {
      console.error('Erro ao carregar movimentos do caixa', err);
      alert('Erro ao carregar movimentações do caixa: ' + err.message);
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-list me-2"></i>Mostrar Movimentações';
      }
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    const btn = document.getElementById('btn-carregar-movimentacoes');
    if (btn) btn.addEventListener('click', carregarMovimentacoesCaixa);

    // Opcional: carregar automaticamente ao abrir a página se houver caixa
    const shouldAutoLoad = false; // ajuste se quiser auto-load
    if (shouldAutoLoad && btn && !btn.disabled) {
      btn.click();
    }
  });

  // Expor função no escopo global para facilitar testes manuais
  window.carregarMovimentacoesCaixa = carregarMovimentacoesCaixa;
})();
