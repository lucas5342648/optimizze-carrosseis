// Tira os 6 prints padrão do carrossel "prints" abrindo a interface REAL do app
// (repositório viralsafeai rodando localmente com `npx vite`) com o Supabase simulado:
// todo pedido ao Supabase é respondido com os dados do conector (dados.json).
// Uso: node captura/capturar.js <dados.json> <dados_um.json> <video_id> <project_id> <pasta_saida> [porta]
// Saída: s1_card.png (só o card do vídeo, sem o botão), s2.png (lista), s3.png (criar),
//        s4.png (V1), s5.png (V3), s6.png (dicas de gravação). @ e marca borrados.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const [, , arqDados, arqUm, videoId, projectId, saida, porta = '5179'] = process.argv;
const BASE = `http://127.0.0.1:${porta}`;
const STORAGE = path.join(path.dirname(arqDados), 'storage');
const USER = { id: '00000000-0000-4000-8000-000000000001', email: 'afiliado@exemplo.com', aud: 'authenticated', role: 'authenticated', app_metadata: {}, user_metadata: {}, created_at: '2026-01-01T00:00:00Z' };
const b64 = (o) => Buffer.from(JSON.stringify(o)).toString('base64url');
const JWT = `${b64({ alg: 'HS256', typ: 'JWT' })}.${b64({ sub: USER.id, email: USER.email, role: 'authenticated', exp: 4102444800 })}.x`;

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

async function abrir(browser, dados, rota, opc = {}) {
  const page = await browser.newPage({ viewport: { width: 430, height: opc.altura || 764 }, deviceScaleFactor: 2 });
  await page.addInitScript(([jwt, user]) => {
    localStorage.setItem('sb-mock-auth-token', JSON.stringify({ access_token: jwt, refresh_token: 'r', token_type: 'bearer', expires_in: 3600000, expires_at: 4102444800, user }));
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
      const nome = p.split('/').pop(); let ped = {}; try { ped = JSON.parse(req.postData() || '{}'); } catch {}
      body = dados.funcoes?.[`${nome}:${ped.acao ?? ''}`] ?? dados.funcoes?.[nome] ?? {};
    } else if (p.startsWith('/rest/v1/')) {
      body = filtrar(dados.tabelas?.[p.split('/').pop()] ?? [], u.searchParams, req.headers()['range']);
      if ((req.headers()['accept'] || '').includes('vnd.pgrst.object')) body = Array.isArray(body) ? (body[0] ?? null) : body;
    }
    await route.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*', 'content-range': '0-0/*' }, body: JSON.stringify(body) });
  });
  await page.goto(BASE + rota, { waitUntil: 'networkidle' });
  await page.waitForTimeout(opc.espera || 4000);
  for (const t of opc.cliques || []) { await page.getByText(t, { exact: false }).first().click().catch(() => console.log('sem clique:', t)); await page.waitForTimeout(800); }
  if (opc.rolarAte) {
    await page.getByText(opc.rolarAte, { exact: false }).first().evaluate((el) => el.scrollIntoView({ block: 'start' })).catch(() => console.log('sem rolar:', opc.rolarAte));
    await page.evaluate(() => window.scrollBy(0, -120)); await page.waitForTimeout(500);
  }
  // borra @ dos criadores e a marca
  await page.evaluate(() => {
    for (const el of document.querySelectorAll('body *')) {
      const t = el.textContent || '';
      if (el.children.length === 0 && (/(^|\s)@\w/.test(t) || /Optimizze/i.test(t) || /^\s*AI\s*$/.test(t))) el.style.filter = 'blur(9px)';
    }
  });
  return page;
}

(async () => {
  fs.mkdirSync(saida, { recursive: true });
  const dados = JSON.parse(fs.readFileSync(arqDados, 'utf8'));
  const um = JSON.parse(fs.readFileSync(arqUm, 'utf8'));
  const browser = await chromium.launch();
  // 1. Card do vídeo (só ele, sem o botão de criar variações)
  let page = await abrir(browser, um, '/biblioteca/videos', { altura: 1400 });
  const badge = page.locator('text=/^#\\d+$/').first();
  const card = badge.locator('xpath=ancestor::*[.//button][1]');
  const cb = await card.boundingBox();
  const bb = await card.locator('button').first().boundingBox();
  const fim = bb ? bb.y - 6 : cb.y + cb.height;
  // tira também a linha do @ (borrada) logo acima do botão, se houver
  const arroba = await card.locator('text=/^@/').first().boundingBox().catch(() => null);
  const corte = arroba && arroba.y > cb.y + cb.height * 0.5 ? arroba.y - 4 : fim;
  await page.screenshot({ path: path.join(saida, 's1_card.png'), clip: { x: cb.x, y: cb.y, width: cb.width, height: corte - cb.y } });
  await page.close();
  // 2. Lista completa
  page = await abrir(browser, dados, '/biblioteca/videos'); await page.screenshot({ path: path.join(saida, 's2.png') }); await page.close();
  // 3. Criar variações (mesmo produto)
  page = await abrir(browser, dados, `/biblioteca/criar/${videoId}`, { cliques: ['Vender o produto do vídeo'] }); await page.screenshot({ path: path.join(saida, 's3.png') }); await page.close();
  // 4-6. Resultado
  page = await abrir(browser, dados, `/projects/${projectId}`, { espera: 2500 }); await page.screenshot({ path: path.join(saida, 's4.png') }); await page.close();
  page = await abrir(browser, dados, `/projects/${projectId}`, { espera: 2500, cliques: ['Variação Criativa'] }); await page.screenshot({ path: path.join(saida, 's5.png') }); await page.close();
  page = await abrir(browser, dados, `/projects/${projectId}`, { espera: 2500, cliques: ['Variação de Contexto'], rolarAte: 'Dicas de Grava' }); await page.screenshot({ path: path.join(saida, 's6.png') }); await page.close();
  await browser.close();
  console.log('ok', saida);
})();
