# Captura de prints reais (estilo `prints`)

Os prints são as telas REAIS do app (repositório privado `lucas5342648/viralsafeai`), abertas
localmente com `npx vite` e com o Supabase simulado: todo pedido do app ao banco é respondido com
os dados que o conector "Optimizze mcp bot" devolveu. Nada toca o site nem o banco de verdade.

## Passo a passo (rotina)
1. `add_repo` lucas5342648/viralsafeai (access read) e clonar em `~/viralsafeai`.
   `cd ~/viralsafeai && npm ci --no-audit --no-fund` (1–2 min).
2. Subir o app (em segundo plano, `run_in_background`):
   `cd ~/viralsafeai && VITE_SUPABASE_URL=https://mock.supabase.co VITE_SUPABASE_PUBLISHABLE_KEY=anon npx vite --port 5179 --host 127.0.0.1`
   Conferir: `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5179/` = 200.
3. Conector: `listar_em_alta` (tipo video, limite 20) → salve a resposta INTEIRA, como veio, em
   `/tmp/cap/em_alta.json` (Write). Escolha 3 vídeos de produtos/nichos diferentes, com `capa` (não null).
4. Para cada vídeo: `criar_variacoes` → 1 a 3 min → `ver_projeto` (status completed) → salve a resposta
   em `/tmp/cap/proj_<slug>.json`. Pode encurtar: V1 e V3 só com as 3 primeiras cenas; V2 inteira;
   guias só version 0 e 2 (é o que aparece nos prints).
5. Montar dados + baixar capas: `python3 captura/montar_dados.py /tmp/cap/em_alta.json /tmp/cap/proj_<slug>.json <video_id> /tmp/cap/<slug>`
   (precisa do domínio wjhoedvxmkjvryqsbdto.supabase.co liberado; se aparecer "sem imagem" pra capa do
   vídeo escolhido, troque de vídeo).
6. Capturar (de dentro de ~/viralsafeai, que tem o playwright):
   `node <repo-carrosseis>/captura/capturar.js /tmp/cap/<slug>/dados.json /tmp/cap/<slug>/dados_um.json <video_id> <project_id> /tmp/cap/<slug>/cap`
7. Compor os fundos: `python3 captura/compor.py /tmp/cap/<slug>/cap assets/prints/AAAA-MM-DD_<slug>`
8. Spec + render: copie a estrutura de `specs/2026-11-12_F_prints_bermuda.json` e rode
   `python3 motor/prints.py <spec> carrosseis/<pasta> <LETRA>`. Prévia em grade e OLHAR antes de publicar:
   @ e marca borrados, card da capa só com o vídeo e as métricas, legendas sem cortar.

## O que cada print mostra
- s1: card do vídeo escolhido (capa + vendas 7d, faturamento, views, postado), sem o botão.
- s2: lista "Vídeos em alta" (com os outros vídeos).
- s3: tela "Produto" (mesmo produto do vídeo).
- s4: resultado V1, roteiro cena a cena (fala/ação/tom).
- s5: resultado V3 (outro gancho).
- s6: fim da V2 + Dicas de Gravação.
