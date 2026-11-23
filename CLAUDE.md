# Rotina diária: carrosséis TikTok da Optimizze AI

Este repositório gera, publica (direto, automático) e otimiza carrosséis de TikTok que divulgam a
**Optimizze AI** (SaaS para afiliados do TikTok Shop). Dono: Lucas. Conta TikTok: **@silvaa.bnss**.
Tudo em português do Brasil, fuso America/Sao_Paulo.

## IDs fixos
- Zernio account (TikTok): `6add0b0455ea8ab9cbf6f9d4`
- Zernio profile: `6add09dda7307722fa8314be`
- Automação de comentário "TTS" (resposta pública apontando pro link da bio): `6add19e6b29a00ca1771edee` — já ativa, NÃO recriar.
  Desde 11/11 também responde "link", "aplicativo", "app" e "ferramenta", e as respostas não citam o nome da marca.
- Imagens públicas: `https://raw.githubusercontent.com/lucas5342648/optimizze-carrosseis/main/<caminho>`

## A rotina (roda todo dia de manhã)
1. **Preparar**: o repo já deve estar clonado; se não, `add_repo` (lucas5342648/optimizze-carrosseis, push) e clonar.
   `git pull`. Conferir `python3 -c "import PIL, playwright"`.
2. **Ler métricas** (Zernio `analytics_get_analytics`, account_id acima, from_date = 30 dias atrás, limit 30).
   A resposta é grande: ela é salva em arquivo; processe com python (ast.literal_eval do campo result).
   Para cada post do `historico.csv` publicado há mais de 24h, atualize views, likes, comments, shares,
   saves, follows, completionRate. O match é pelo `latePostId` (id do post Zernio) ou pela data/legenda.
   Posts antigos do Lucas (externos) servem de referência de estilo: média ~800 views no estilo nativo.
3. **Aprender**: atualize `aprendizados.md` com 2–4 linhas novas e concretas (o que subiu/caiu e a hipótese).
   Métrica principal: views e saves; secundária: comments (TTS = intenção de clique) e follows.
4. **Modo VIRAL (verificar antes de tudo):** um post é "viral" se tiver **3x ou mais a mediana de views**
   dos últimos 10 posts, ou **2.000+ views**, ou saves/comments muito acima do normal.
   Se houver um post viral nos últimos 7 dias, os 3 carrosséis do dia seguem o estilo dele:
   - 2 carrosséis **quase iguais** ao viral: mesmo estilo visual, mesmo ângulo e mesma estrutura de slides,
     mudando só a redação do gancho, a ordem/escolha dos prints ou o exemplo.
   - 1 carrossel **variação controlada**: mantém o que deu certo e muda UMA coisa só (gancho, CTA,
     nº de slides ou horário), para descobrir o que exatamente fez viralizar.
   - Registre em `aprendizados.md` qual post viralizou, os números e o que está sendo testado.
   - Saia do modo viral quando 3 posts seguidos no estilo dele ficarem abaixo da mediana.
   Sem post viral, use a regra normal abaixo.
5. **Decidir os 3 carrosséis do dia** — desde 20/11 os 3 são no estilo **`premium` (FigCraft)**, aprovado
   pelo Lucas em 19/11, cada um com um vídeo/produto DIFERENTE da biblioteca (variar nichos: moda, beleza,
   casa, ferramentas, utilidades). Os prints continuam vindo da captura de sempre; muda só o design.
   A regra 2+1 abaixo vale dentro do premium: 2 repetem a estrutura do melhor post premium recente; 1 muda
   UMA coisa (texto da capa, texto do slide-lista, um passo a menos, texto do CTA).
   (De 13/11 a 19/11 o padrão foi o estilo `prints`: mediana de 60 views. Ele vira o plano B do premium.)
   Regra normal 2+1 (e o modo viral acima, que tem prioridade):
   - 2 carrosséis "explorar o que funciona": estilo/ângulo/gancho do melhor desempenho recente.
   - 1 carrossel "teste": um ângulo ou gancho novo do `banco_angulos.md` (ou outro estilo).
   - Nunca repetir um gancho de capa usado nos últimos 14 dias (ver `historico.csv`).
   - **Fila**: se existir algum spec em `specs/fila/`, o mais antigo É o carrossel "teste" do dia
     (formatos adaptados de posts virais pesquisados). Renderize com o motor do campo `estilo`
     e depois mova o spec para `specs/` com a data do dia no nome.
     Fora do modo viral, o estilo `tablet` também pode ser usado nos 2 de "explorar" se performar bem.
6. **Gerar**: escreva um spec em `specs/AAAA-MM-DD_<letra>_<slug>.json` e renderize:
   - Estilo **premium** (PADRÃO desde 20/11): ver a seção "Estilo premium (FigCraft)" no fim deste arquivo.
   - Estilo **prints** (padrão de 13/11 a 19/11; plano B se o FigCraft falhar): prints REAIS das telas do app com dados reais da biblioteca
     (conector Optimizze). Passo a passo completo em `captura/README.md`; motor `motor/prints.py`.
     Exemplos: `specs/2026-11-12_F_prints_bermuda.json` (Passo 1..5) e `specs/2026-11-12_G_prints_parafusadeira.json` (1. 2. 3.).
   - Estilo **nativo** (antigo padrão; usar se a captura falhar): `python3 motor/nativo.py <spec> carrosseis/<pasta> <PREFIXO>`
     usa os prints reais de `assets/base/` (ver `assets/base/base.json` pro papel de cada imagem).
   - Estilo **tablet** (formato do viral do nicho): `python3 motor/tablet.py <spec> carrosseis/<pasta> <PREFIXO>`;
     legenda em 2 camadas (branco + vermelho), slide 2 pedindo pra salvar, passos numerados,
     slide "Quer o acesso à ferramenta? Comenta TTS". Exemplo: `specs/fila/E_tablet_passo_a_passo.json`.
   - Estilo **escuro** (só como teste): `python3 motor/render.py <spec> carrosseis/<pasta>` (formato dos specs em `carrosseis/lote01_*`).
   Monte uma prévia em grade (PIL) e OLHE com a ferramenta Read: texto cortado, caixa desalinhada ou
   legenda antiga aparecendo = corrigir antes de publicar.
7. **Publicar**: `git add/commit/push` (o push precisa acontecer ANTES de agendar). Depois agende no Zernio
   com `posts_create_post` (via `call_tool`), um por horário: **12:00, 19:00 e 21:00** (America/Sao_Paulo),
   com `timezone: America/Sao_Paulo`, `tags: ["carrossel", "<estilo>"]`, `metadata: {"carrossel": "<pasta>"}` e:
   ```
   tiktok_settings: {draft: false, autoAddMusic: true, mediaType: "photo", photoCoverIndex: 0,
     privacyLevel: "PUBLIC_TO_EVERYONE", allowComment: true, commercialContentType: "brand_organic",
     contentPreviewConfirmed: true, expressConsentGiven: true, description: "<legenda completa com hashtags>"}
   content: "<título curto, até 90 caracteres, sem hashtags>"
   ```
   Se um horário do dia já passou, pule pro próximo horário livre (nunca agende no passado).
   **Antes de agendar**, liste os posts já agendados pra hoje na conta (`posts_list_posts`): se já houver
   carrossel agendado num horário, NÃO agende outro por cima (não duplicar) e avise o Lucas no resumo.
   **PUBLICAÇÃO DIRETA (desde 29/10)**: `draft: false` + `autoAddMusic: true` = o Zernio publica sozinho
   no horário e o TikTok escolhe a música. NUNCA use `draft: true`: os rascunhos da Caixa de entrada
   chegavam com atraso de horas/dias e um falhou ("could not process as inbox draft"). O Lucas NÃO
   quer postar manualmente.
   Depois do horário, confira com `posts_get`/`posts_list_posts` se o status virou `published`;
   se `failed`, leia `errorMessage`, corrija (ex.: reduzir slides) e reagende; se for erro de limite
   diário do TikTok, avise o Lucas em vez de insistir.
   Se o Zernio responder 409 (conteúdo duplicado), mude levemente o `content` (título) e tente de novo.
   **POSTAGEM PELO LUCAS, COM MÚSICA VIRAL (desde 24/11, pedido dele em 23/11) — VALE ACIMA DA PUBLICAÇÃO DIRETA:**
   a rotina PRODUZ tudo (ele não quer produzir nada), mas quem POSTA é o Lucas, pra escolher a música em alta
   (no automático o TikTok só libera a biblioteca comercial). Então os 3 posts do dia vão como RASCUNHO, criados
   logo de manhã: `draft: true`, `autoAddMusic: false`, scheduled_for = agora + 5 min (um a cada 5 min),
   tags `["carrossel", "<formato>", "manual"]` e `metadata: {"carrossel": "<pasta>", "horario": "12:00"}` (ou 19:00/21:00).
   Eles chegam na Caixa de entrada do TikTok dele; os lembretes das 11:50, 18:50 e 20:50 mandam a legenda
   pronta e os links das imagens (plano B se o rascunho não chegar). No historico.csv, horário "12:00 (manual)" etc.
   Na mensagem da manhã, diga que os 3 estão na Caixa de entrada e qual vai em cada horário.
   **TESTE "MÚSICA DO LUCAS" (20/11 a 24/11, aprovado por ele em 19/11):** a análise de 19/11 mostrou
   que os posts que o Lucas publicou à mão têm cerca de 5x mais views que os automáticos (mediana de 312 × 66).
   Durante o teste, só o carrossel das **19:00** vira RASCUNHO: crie o post logo de manhã (scheduled_for
   = agora + 5 min, `draft: true`, `autoAddMusic: false`, tags `["carrossel", "<estilo>", "manual-teste"]`),
   pra chegar na Caixa de entrada do TikTok com folga. O Lucas coloca uma música em alta e posta às 19h
   (o lembrete das 18:50 avisa ele). O de 19h usa a MESMA estrutura do de 12h (os dois "explorar"), pra
   comparar só o jeito de postar. 12:00 e 21:00 continuam com publicação direta, como acima.
   No historico.csv, o de 19h leva `19:00 (manual)` no horário. Em **25/11**, compare as views, saves e
   completion dos 5 manuais com os 10 automáticos do mesmo período, registre em aprendizados.md e mande
   o resultado ao Lucas perguntando se continua. Até ele responder, volte a publicar os 3 direto.
   **Máximo 9 slides por carrossel.** O único de 10 (27/10 C, tablet) falhou no TikTok. Até haver
   prova do contrário, nunca passe de 9 (corte/junte slides do spec, inclusive os da fila).
8. **Registrar**: acrescente uma linha por carrossel em `historico.csv`, commit e push.
9. **Avisar o Lucas** (SendUserMessage, curto): o que foi agendado e quando, o top e o pior post recente
   com números, e o aprendizado do dia em 1 linha.

## Regras de conteúdo (não negociáveis)
- Estrutura: "passo a passo" pra fazer vídeo pro TikTok Shop com IA, com a Optimizze entrando
  **naturalmente** como a ferramenta de um dos passos (nunca como anúncio).
- CTA (slides e legenda): "Comenta TTS pra receber o acesso à ferramenta" (ou variação curta com
  "Comenta TTS"). NUNCA falar "link na bio" nos slides nem na legenda: o link da bio só aparece na
  RESPOSTA AUTOMÁTICA a quem comenta TTS (automação já ativa). Nunca prometer link por DM.
- PROIBIDO convidar a pedir ajuda ou contato: nada de "que eu te ajudo", "me chama", "qualquer dúvida
  me chama", "manda DM", "fala comigo". O Lucas NÃO quer pedidos de ajuda na DM. O CTA é só
  "Comenta TTS"; quem entrega o link da bio é a resposta automática nos comentários.
- Área segura: todo slide passa por `motor/seguro.py::enquadrar` (já embutido em nativo.py e tablet.py),
  que centraliza o conteúdo porque o TikTok corta as bordas de carrossel. Não remova isso. No estilo
  escuro (render.py), aplique `enquadrar` nas imagens antes de publicar.
- Honestidade: números só se estiverem num print real (ex.: R$ 185 mil da Kalodata), vierem da
  biblioteca da Optimizze (conector, ver abaixo) ou marcados como "exemplo". Não inventar depoimentos, resultados ou recursos que a Optimizze não tem.
- Recursos reais da Optimizze: Remix Inteligente (envia vídeo que já vendeu; devolve V1 Otimizada e Fiel,
  V2 Variação de Contexto, V3 Variação Criativa), Resumo da otimização (Hook, Estrutura da Copy, CTA),
  Modo Gravação (cenas com FALA/AÇÃO/TOM), Prompts de vídeo por cena, plano mensal R$29,90 e anual R$197.
- **Nome da marca (desde 11/11):** NÃO citar "Optimizze" nos slides nem na legenda (ainda não se sabe
  se o nome pode ser usado). Falar "a ferramenta" / "a IA". Nos prints reais, o logo fica borrado.
- **Como descrever o recurso:** nunca "a IA gera roteiros". O certo: gera **variações** baseadas na
  **estrutura validada** de vídeos que já venderam (V1/V2/V3 com cenas fala/ação/tom).
- **Gancho que conecta com o afiliado (desde 12/11):** o carrossel NUNCA começa direto no passo a passo.
  Slide 1 = HEADLINE grande no topo falando com o afiliado e dizendo o que o post vai mostrar
  (ex.: "Afiliado: para de gravar vídeo que não vende", "Não sabe o que gravar hoje?") + subtítulo na caixa
  com a prova real (vendas do vídeo) + card do vídeo. Slide 2 = dor/promessa ou "salva esse passo a passo"
  (ex.: "O segredo não é o produto" / "É a estrutura do vídeo. Te mostro como usar a de quem já vende").
  Só depois vêm os passos. Ver specs/2026-11-12_F_prints_bermuda.json e _G_prints_parafusadeira.json.
- **Vídeo citado = só ele na tela:** quando o slide fala de um vídeo específico, o print mostra só
  aquele vídeo (sem a grade de outros vídeos), e o @ do criador sempre borrado.
- Sem emoji dentro dos slides (não há fonte de emoji); emojis só na legenda.
- Hashtags que performaram: `#tiktokshop #tiktokshopbr #ia #afiliados #afiliadosiniciantes`.
- Textos curtos por slide (máx. ~12 palavras), linguagem de afiliado brasileiro, direta.
- **Sem promessa de resultado (desde 17/11):** nada de "vê qual vende mais", "vai vender", "garantido".
  Use "vê qual traz mais resultado" / "testa e vê qual funciona melhor".
- **CTA só promete o acesso (desde 17/11):** "Comenta TTS e receba o acesso à ferramenta". Não prometer
  brinde, "estrutura validada", roteiro, material extra nem nada além do link do site (que vem na resposta automática).
- **Slide 1 mostra o faturamento:** se a capa mostra/cita um vídeo, o card dele aparece COM as métricas
  (vendas, faturamento, views) e o faturamento de 7 dias em destaque (ex.: selo "R$ 109 mil em 7 dias"), como estimado.
- **"TikTok Shop" escrito nos primeiros slides (desde 22/11, pedido do Lucas):** a capa e o slide 2 citam
  "TikTok Shop" DE FORMA NATURAL, dentro da frase, pra atrair o afiliado sem parecer forçado. Capa: "Afiliado" no título,
  em roxo ("[[Afiliado]], pegue a"), e "TikTok Shop" em roxo/negrito no subtítulo ("em 7 dias no [[TikTok Shop]] (estimado)"),
  os dois bem visíveis (pedido do Lucas em 22/11: "achei meio pequeno"). Slide 2: no título ("De 1 vídeo que já vende no TikTok Shop você tira
  3 vídeos novos"). Legenda: "...que fez R$ X mil em 7 dias no TikTok Shop". Nada de etiqueta/pílula "AFILIADO DO
  TIKTOK SHOP" nem de repetir a palavra à força (o Lucas achou forçado). Vale também pra variação do dia.
- **"Pegar", nunca "roubar" (desde 22/11, pedido do Lucas):** nada de "roube", "rouba", "roubar" em slide,
  título ou legenda. Use "pegue a estrutura" / "pega a estrutura".
- **Todo post apresenta a ferramenta de forma natural (desde 23/11, pedido do Lucas):** qualquer formato
  (ranking, raio-X, erros, dicas...) tem 1 slide em que a ferramenta entra como a fonte ou o atalho do que o post
  mostrou ("Tiro esse ranking da ferramenta que eu uso", "Essa análise sai da ferramenta que eu uso"), com um
  print real, sem cara de anúncio, + o slide de CTA "Comenta TTS". O nome "Optimizze" continua proibido.
- **Vídeo com IA (breve):** em um dos passos, mencionar que também dá pra fazer o vídeo com IA
  (a ferramenta gera os prompts de cada cena), sem virar o foco do carrossel.

## Biblioteca da Optimizze (conector "Optimizze mcp bot", desde 11/11)
Conector MCP com a biblioteca de vídeos e produtos mais vendidos do TikTok Shop da Optimizze.
Ferramentas: `listar_em_alta` (tipo video|produto), `ver_video`, `criar_variacoes`, `ver_projeto`,
`listar_meus_projetos`, `exportar_imagens`, `uso_de_hoje`.
- **Em uso diário desde 13/11** (o Lucas aprovou o estilo prints em 12/11).
- Uso: trocar os "exemplos" inventados por dados reais. Para cada carrossel:
  escolha um vídeo de `listar_em_alta` (tipo video, só com `tem_fala`, produtos variados entre os 3,
  de preferência nichos de afiliado: beleza, casa, moda, utilidades), rode `criar_variacoes` e, 1 a 3 min
  depois, `ver_projeto`. Use o resultado REAL nos slides: produto, Resumo da otimização (`improvements`
  da V1), hooks de V1/V2/V3 (`scenes_data[0].fala`), uma cena do Modo Gravação (FALA/AÇÃO/TOM).
- Mantém o estilo e a estrutura decididos pelas regras acima (modo viral ou 2+1): a biblioteca muda
  o EXEMPLO, não o formato. No estilo escuro, os blocos "Exemplo:" passam a ter o conteúdo real
  (pode tirar o "Exemplo" e escrever "Gerado pela Optimizze" ou nada).
- Passo novo e real que pode virar slide: "Acha um vídeo que já vende" (biblioteca, ranking com vendas
  de 7 dias) e "Cria variações na estrutura que já vendeu". Sem citar o nome da marca.
- **Estilo `prints` (motor/prints.py, desde 11/11):** prints REAIS das telas do app (abertas a partir do
  código do repositório viralsafeai com os dados do conector) + legenda em caixa branca. Exemplo:
  specs/2026-11-11_E_prints_protetor.json. A rotina faz a captura sozinha (ver `captura/README.md`).
- Números reais da biblioteca podem ir no slide (vendas e faturamento de 7 dias, views), sempre
  como "estimado" e sem citar o nome/@ do criador do vídeo original. Nunca usar capa ou trecho do
  vídeo de outro criador como se fosse do Lucas.
- Limite: 6 variações por dia (`uso_de_hoje`). A rotina usa no máximo 3.
- `exportar_imagens` só funciona se o Lucas configurar o token do GitHub; se responder "desligado",
  siga sem imagens da biblioteca (motores de sempre).
- Se o conector ou a captura falharem, a rotina segue com o estilo nativo/escuro e exemplos marcados como
  "exemplo", e avisa o Lucas no resumo do dia. Nunca trave os 3 carrosséis do dia por causa disso.

## Quando pedir ajuda ao Lucas
- Faltam prints/fotos novos (os 8 de `assets/base/` cansam rápido): peça prints SEM legenda.
- Erro de conexão do Zernio/GitHub, ou métricas zeradas por mais de 2 dias.

## Estilo premium (FigCraft) — PADRÃO desde 20/11 (aprovado pelo Lucas em 19/11)
Visual escuro/roxo modelado nos carrosséis virais "Roube meu Prompt", 1080x1350, feito no FigCraft headless.
- Instalar (uma vez por sessão): `CLI=$(bash figcraft/instalar.sh)`. Ele baixa o release linux do
  github.com/storytold/figcraft e instala as fontes de `assets/fonts/`. A Inter já vem no sistema.
- Fluxo por carrossel: captura de sempre (`captura/README.md` até o `compor.py`, que gera s1..s6 em
  `assets/prints/AAAA-MM-DD_<slug>/`) → spec premium → `python3 figcraft/premium.py <spec> carrosseis/<pasta> <PREFIXO> --cli $CLI`
  → prévia em grade → OLHAR. Não precisa do `motor/prints.py`.
- Spec: copie `specs/exemplo_premium_nicho.json` e troque produto, números (do conector, "estimado"),
  caminhos `assets/prints/...` e a legenda. Recortes de partida: s2 `y` 770, s3 440, s4 640, s5 640, s6
  `y` 1112 + `x` 60 + `larg` 740 (s6 tem 1528 de altura). Ajuste olhando a prévia, porque cada vídeo muda a altura das telas.
- Capa: `l1` "[[Afiliado]], pegue a", `l2` "Estrutura", `l3` "de um vídeo que fez R$ X mil", `l4` "em 7 dias no [[TikTok Shop]] (estimado)"
  (`[[...]]` = roxo e negrito; o `l4` sai em 48 px),
  `selo` "R$ X mil em 7 dias". Não usar `kicker` (a pílula existe no motor, mas o Lucas achou forçada). Slide 2 (`lista`):
  `pilula` "Salva esse post" e `titulo` "De **1 vídeo que já vende no TikTok Shop** você tira **3 vídeos novos**:". Exemplo: `specs/exemplo_premium_nicho.json`. Na variação do dia, pode trocar `l1`/`l2`/`l3` por outro gancho curto.
- Slides: capa (card do vídeo com métricas + selo do faturamento + tela da V1) → lista "salva esse post"
  → Passo 1..5 (print real + texto) → CTA (mesma vitrine + "COMENTA TTS E RECEBA O / Acesso à ferramenta").
- NÃO desenhar linhas/"teias" ligando as telas (é recurso da ferramenta de outra pessoa).
- Os prints vêm da captura de sempre (`captura/`); o spec usa `print` + `y` (e `x`/`larg` pra dar zoom)
  pra escolher o recorte de cada passo. Conferir a prévia: nada de card cortado no topo do recorte.
- Se a instalação ou a renderização do FigCraft falhar, faça os 3 no estilo `prints` (motor/prints.py, com os
  mesmos s1..s6) e avise o Lucas no resumo.

## Rodízio de formatos (desde 23/11, pedido do Lucas: "testar mais formatos")
De 12/11 a 22/11 todo post foi o mesmo "passo a passo da ferramenta" e ficou entre 20 e 140 views (mediana ~55).
O que muda agora é o ASSUNTO/formato do post, não só o visual. Todos usam o motor `figcraft/premium.py`
(mesmo visual escuro/roxo) e seguem TODAS as regras de conteúdo (Afiliado/TikTok Shop na capa, "pegue",
números reais "estimado", sem nome da marca, ferramenta natural, CTA "Comenta TTS").
- **Agenda:** 24/11: 12h e 19h premium, 21h **raio-X** (os 3 como rascunho pro Lucas postar, ver "POSTAGEM PELO LUCAS"). A partir de 25/11: **12h = premium
  (controle)**; **19h e 21h = formatos do banco abaixo**, em rodízio (nunca o mesmo formato 2 dias seguidos no mesmo horário).
- **Como decidir:** cada formato roda pelo menos 2 vezes (produtos/temas diferentes). Se fizer **2x a mediana de
  views dos últimos 10 posts** (ou o dobro de saves), entra no rodízio fixo e ganha variações; se ficar abaixo da
  mediana 2 vezes, sai. Registre em `aprendizados.md` (formato, views, saves) e na coluna `estilo` do historico.csv
  use o nome do formato (`ranking`, `raiox`, `erros`, `antes_depois`, `dicas`).
- **Banco de formatos** (tipos de slide do premium.py: `rank_capa`, `produto`, `capa_texto`, `texto`, `passo` com
  `pilula`, `cta` com `print`):
  1. **ranking**: "Afiliado, esses são os 5 produtos que mais faturaram essa semana no TikTok Shop".
     Dados: `listar_em_alta` tipo **produto** (pular produto repetido/variação do mesmo); fotos baixadas pra
     `assets/produtos/<id>.jpg` (webp → jpg). Contagem regressiva 5→1, slide "De onde eu tiro isso" (print da
     biblioteca, s2) e CTA com print. Variações: por categoria (beleza, casa, moda...). Exemplo: `specs/2026-11-23_C_ranking_semana.json`.
  2. **raiox**: "Afiliado, o raio-X do vídeo que fez R$ X mil". Dados REAIS: `ver_video` (fala original → o gancho)
     e `ver_projeto` → `analise` (structure_analysis, retention_analysis, triggers). Slides: capa (vitrine) →
     1. O gancho (citação da fala original) → 2. A estrutura → 3. Os gatilhos → "Como eu fiz essa análise"
     (ferramenta, print da V1) → CTA. Exemplo: `specs/exemplo_raiox.json`. Evite produtos com promessa de
     saúde/estética exagerada no vídeo original (ex.: "clareou em 3 dias").
  3. **erros**: `capa_texto` "3 erros que fazem seu vídeo não vender no TikTok Shop" → 1 slide `texto` por erro
     (o erro + o que fazer) → ferramenta como o atalho pra corrigir (ex.: gancho → variações com gancho novo) → CTA.
     Os erros vêm do que a `analise`/`improvements` da biblioteca apontam com frequência (ganchos genéricos,
     repetição na abertura, CTA fraco), nada inventado sobre números.
  4. **antes_depois**: "O mesmo vídeo, 2 ganchos": `texto` com a fala ORIGINAL (antes) e `texto` com o gancho da
     V1/V2/V3 (depois) + o porquê (`improvements`), sem prometer que o "depois" vende mais.
  5. **dicas**: `capa_texto` "O que eu olho antes de escolher um produto pra divulgar" → itens práticos baseados
     nos dados da biblioteca (vendas 7d, faturamento, nº de vídeos vendendo) → ferramenta → CTA.
     Sem depoimento ou resultado pessoal inventado.
  6. **vídeo curto** (MP4 com zoom nos prints): ainda não existe o motor; só depois de o Lucas aprovar.
