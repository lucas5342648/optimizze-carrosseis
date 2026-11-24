// Grava a TELA do app (viralsafeai rodando local com o Supabase simulado, igual ao capturar.js)
// fazendo o passo a passo, em trechos curtos de vídeo (webm), pro formato "video_tela".
// Uso: node captura/gravar.js <dados.json> <dados_um.json> <video_id> <project_id> <pasta_saida> [porta]
// Saída: pastas t1_lista..t6_dicas e t7_prompts com os quadros (jpg 860x1528, 30 por segundo de vídeo) + cortes.json.
// @ dos criadores e a marca ficam borrados o tempo todo (o borrão é reaplicado a cada 200 ms).
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const [, , arqDados, arqUm, videoId, projectId, saida, porta = '5179'] = process.argv;
const BASE = `http://127.0.0.1:${porta}`;
const STORAGE = path.join(path.dirname(arqDados), 'storage');
const USER = { id: '00000000-0000-4000-8000-000000000001', email: 'afiliado@exemplo.com', aud: 'authenticated', role: 'authenticated', app_metadata: {}, user_metadata: {}, created_at: '2026-01-01T00:00:00Z' };
const b64 = (o) => Buffer.from(JSON.stringify(o)).toString('base64url');
const JWT = `${b64({ alg: 'HS256', typ: 'JWT' })}.${b64({ sub: USER.id, email: USER.email, role: 'authenticated', exp: 4102444800 })}.x`;
const W = 430, H = 764, FPS = 30;

function filtrar(linhas, q, range) {
  if (!Array.isArray(linhas)) return linhas;
  let r = linhas.slice();
  for (const [k, v] of q.entries()) {
    if (['select', 'order', 'limit', 'offset'].includes(k)) continue;
    if (v.startsWith('eq.')) r = r.filter((x) => String(x[k]) === decodeURIComponent(v.slice(3)));
    else if (v.startsWith('in.(')) { const s = new Set(v.slice(4, -1).split(',').map((x) => x.replace(/"/g, ''))); r = r.filter((x) => s.has(String(x[k]))); }
  }
  const ord = q.get('order');
  if (ord) { const [col, sentido] = ord.split(',')[0].split('.'); r.sort((a, b) => (a[col] > b[col] ? 1 : a[col] < b[col] ? -1 : 0) * (sentido === 'desc' ? -1 : 1)); }
  let ini = Number(q.get('offset') || 0), lim = q.get('limit') ? Number(q.get('limit')) : Infinity;
  if (range) { const [a, b] = range.split('-').map(Number); ini = a; lim = b - a + 1; }
  return r.slice(ini, ini + lim);
}

async function trecho(browser, dados, rota, nome, acoes, espera = 3500) {
  // Grava com o screencast do Chrome (CDP) em resolução de celular retina (860x1528),
  // só depois que a tela carregou: não precisa cortar o carregamento.
  const ctx = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  await page.addInitScript(([jwt, user]) => {
    localStorage.setItem('sb-mock-auth-token', JSON.stringify({ access_token: jwt, refresh_token: 'r', token_type: 'bearer', expires_in: 3600000, expires_at: 4102444800, user }));
    const borrar = () => {
      for (const el of document.querySelectorAll('body *')) {
        const t = el.textContent || '';
        if (el.children.length === 0 && (/(^|\s)@\w/.test(t) || /Optimizze/i.test(t) || /^\s*AI\s*$/.test(t))) el.style.filter = 'blur(9px)';
      }
    };
    setInterval(borrar, 200);
    document.addEventListener('DOMContentLoaded', borrar);
  }, [JWT, USER]);
  await page.route('https://mock.supabase.co/**', async (route) => {
    const req = route.request(); const u = new URL(req.url()); const p = u.pathname;
    if (p.startsWith('/storage/')) {
      const local = path.join(STORAGE, decodeURIComponent(p.replace('/storage/v1/object/public/biblioteca/', '')));
      if (!fs.existsSync(local)) return route.fulfill({ status: 404, body: '' });
      const tipo = local.endsWith('.webp') ? 'image/webp' : local.endsWith('.png') ? 'image/png' : 'image/jpeg';
      return route.fulfill({ status: 200, contentType: tipo, headers: { 'access-control-allow-origin': '*' }, body: fs.readFileSync(local) });
    }
    let body = [];
    if (p.startsWith('/auth/v1/user')) body = USER;
    else if (p.startsWith('/rest/v1/rpc/')) body = dados.rpc?.[p.split('/').pop()] ?? true;
    else if (p.startsWith('/functions/v1/')) {
      const nm = p.split('/').pop(); let ped = {}; try { ped = JSON.parse(req.postData() || '{}'); } catch {}
      body = dados.funcoes?.[`${nm}:${ped.acao ?? ''}`] ?? dados.funcoes?.[nm] ?? {};
    } else if (p.startsWith('/rest/v1/')) {
      body = filtrar(dados.tabelas?.[p.split('/').pop()] ?? [], u.searchParams, req.headers()['range']);
      if ((req.headers()['accept'] || '').includes('vnd.pgrst.object')) body = Array.isArray(body) ? (body[0] ?? null) : body;
    }
    await route.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*', 'content-range': '0-0/*' }, body: JSON.stringify(body) });
  });
  await page.goto(BASE + rota, { waitUntil: 'networkidle' });
  await page.waitForTimeout(espera);
  const dir = path.join(saida, nome); fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
  // Gravação quadro a quadro (30 qps "virtuais"): cada passo mexe a tela um pouquinho e tira um print 2x.
  // Fica liso mesmo com o print levando ~80 ms, e nítido (860x1528).
  const cdp = await ctx.newCDPSession(page);
  let n = 0;
  const foto = async () => {
    const m = await cdp.send('Page.getLayoutMetrics');
    const v = m.cssVisualViewport || m.visualViewport;
    const r = await cdp.send('Page.captureScreenshot', { format: 'jpeg', quality: 90, clip: { x: v.pageX, y: v.pageY, width: W, height: H, scale: 2 } });
    const arq = path.join(dir, `q${String(n++).padStart(5, '0')}.jpg`);
    fs.writeFileSync(arq, Buffer.from(r.data, 'base64'));
    return arq;
  };
  const ctl = {
    page,
    async parar(seg) { const a = await foto(); for (let i = 1; i < Math.round(seg * FPS); i++) fs.copyFileSync(a, path.join(dir, `q${String(n++).padStart(5, '0')}.jpg`)); },
    async rolar(px, seg) {
      const k = Math.max(1, Math.round(seg * FPS));
      for (let i = 0; i < k; i++) {
        // easing suave (começa e termina devagar)
        const f = (x) => 0.5 - 0.5 * Math.cos(Math.PI * x);
        const d = px * (f((i + 1) / k) - f(i / k));
        await page.evaluate((dy) => {
          let alvo = document.scrollingElement; let maior = alvo.scrollHeight - alvo.clientHeight;
          for (const el of document.querySelectorAll('main, div')) {
            const st = getComputedStyle(el);
            if ((st.overflowY === 'auto' || st.overflowY === 'scroll') && el.scrollHeight - el.clientHeight > maior) { alvo = el; maior = el.scrollHeight - el.clientHeight; }
          }
          alvo.scrollTop += dy;
        }, d);
        await foto();
      }
    },
    async clicar(texto, seg = 0.8) {
      const el = page.getByText(texto, { exact: false }).first();
      await el.click().catch(() => console.log('sem clique:', texto));
      const fim = Date.now() + seg * 1000;
      while (Date.now() < fim) { const a = await foto(); fs.copyFileSync(a, path.join(dir, `q${String(n++).padStart(5, '0')}.jpg`)); }
    },
    async mostrar(texto, seg = 0.6) {
      await page.getByText(texto, { exact: false }).first().evaluate((el) => el.scrollIntoView({ block: 'center' })).catch(() => console.log('sem achar:', texto));
      await page.waitForTimeout(250); await this.parar(seg);
    },
  };
  await acoes(ctl);
  await ctx.close();
  return { nome, dir, quadros: n, dur: n / FPS };
}

(async () => {
  fs.mkdirSync(saida, { recursive: true });
  const dados = JSON.parse(fs.readFileSync(arqDados, 'utf8'));
  const um = JSON.parse(fs.readFileSync(arqUm, 'utf8'));
  const browser = await chromium.launch();
  const out = [];
  // 1. Lista dos vídeos que mais vendem (rola devagar)
  out.push(await trecho(browser, dados, '/biblioteca/videos', 't1_lista', async (c) => { await c.parar(0.8); await c.rolar(900, 3.0); await c.parar(0.6); }));
  // 2. O vídeo escolhido, com vendas e faturamento
  out.push(await trecho(browser, um, '/biblioteca/videos', 't2_card', async (c) => { await c.rolar(160, 0.8); await c.parar(2.2); }));
  // 3. Pede as variações no mesmo produto
  out.push(await trecho(browser, dados, `/biblioteca/criar/${videoId}`, 't3_criar', async (c) => { await c.parar(1.2); await c.clicar('Vender o produto do vídeo', 1.2); }));
  // 4. V1 cena por cena (rola devagar pelas cenas)
  out.push(await trecho(browser, dados, `/projects/${projectId}`, 't4_v1', async (c) => { await c.parar(1.0); await c.rolar(1500, 5.0); await c.parar(0.6); }, 2500));
  // 5. V3 (outro gancho)
  out.push(await trecho(browser, dados, `/projects/${projectId}`, 't5_v3', async (c) => { await c.parar(0.4); await c.clicar('Variação Criativa', 1.0); await c.rolar(450, 1.8); await c.parar(0.6); }, 2500));
  // 6. Dicas de gravação
  out.push(await trecho(browser, dados, `/projects/${projectId}`, 't6_dicas', async (c) => { await c.clicar('Variação de Contexto', 0.5); await c.mostrar('Dicas de Grava', 2.4); }, 2500));
  // 7. Vídeo de IA: prompts de cada cena (pedido do Lucas em 23/11). O app só mostra essa seção depois que o
  // vídeo é enviado ao projeto; aqui o projeto aparece como "já enviado" (sem biblioteca_video_id), e os
  // prompts são os que o próprio app monta com as cenas reais da V1 (sem DNA visual: base 9:16 genérica).
  const ia = JSON.parse(JSON.stringify(dados));
  ia.tabelas.projects = (ia.tabelas.projects || []).map((p) => ({ ...p, biblioteca_video_id: null }));
  ia.funcoes = { ...(ia.funcoes || {}), 'video-ia-curto': { ativo: false } };
  out.push(await trecho(browser, ia, `/projects/${projectId}`, 't7_prompts', async (c) => { await c.mostrar('Prompts de Vídeo por Cena', 1.0); await c.rolar(650, 2.6); await c.parar(0.6); }, 2500));
  await browser.close();
  fs.writeFileSync(path.join(saida, 'cortes.json'), JSON.stringify(out, null, 1));
  console.log('ok', out.map((o) => `${o.nome} ${o.quadros}q ${o.dur.toFixed(1)}s`).join(' | '));
})();
