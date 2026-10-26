# Rotina diária: carrosséis TikTok da Optimizze AI

Este repositório gera, publica (como rascunho) e otimiza carrosséis de TikTok que divulgam a
**Optimizze AI** (SaaS para afiliados do TikTok Shop). Dono: Lucas. Conta TikTok: **@silvaa.bnss**.
Tudo em português do Brasil, fuso America/Sao_Paulo.

## IDs fixos
- Zernio account (TikTok): `6add0b0455ea8ab9cbf6f9d4`
- Zernio profile: `6add09dda7307722fa8314be`
- Automação de comentário "TTS" (resposta pública apontando pro link da bio): `6add19e6b29a00ca1771edee` — já ativa, NÃO recriar.
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
4. **Decidir os 3 carrosséis do dia** (regra 2+1):
   - 2 carrosséis "explorar o que funciona": estilo/ângulo/gancho do melhor desempenho recente.
   - 1 carrossel "teste": um ângulo ou gancho novo do `banco_angulos.md` (ou outro estilo).
   - Nunca repetir um gancho de capa usado nos últimos 14 dias (ver `historico.csv`).
5. **Gerar**: escreva um spec em `specs/AAAA-MM-DD_<letra>_<slug>.json` e renderize:
   - Estilo **nativo** (padrão, performa melhor): `python3 motor/nativo.py <spec> carrosseis/<pasta> <PREFIXO>`
     usa os prints reais de `assets/base/` (ver `assets/base/base.json` pro papel de cada imagem).
   - Estilo **escuro** (só como teste): `python3 motor/render.py <spec> carrosseis/<pasta>` (formato dos specs em `carrosseis/lote01_*`).
   Monte uma prévia em grade (PIL) e OLHE com a ferramenta Read: texto cortado, caixa desalinhada ou
   legenda antiga aparecendo = corrigir antes de publicar.
6. **Publicar**: `git add/commit/push` (o push precisa acontecer ANTES de agendar). Depois agende no Zernio
   com `posts_create_post` (via `call_tool`), um por horário: **12:00, 19:00 e 21:00** (America/Sao_Paulo),
   com `timezone: America/Sao_Paulo`, `tags: ["carrossel", "<estilo>"]`, `metadata: {"carrossel": "<pasta>"}` e:
   ```
   tiktok_settings: {draft: true, mediaType: "photo", photoCoverIndex: 0, privacyLevel: "PUBLIC_TO_EVERYONE",
     allowComment: true, commercialContentType: "brand_organic", contentPreviewConfirmed: true,
     expressConsentGiven: true, description: "<legenda completa com hashtags>"}
   content: "<título curto, até 90 caracteres, sem hashtags>"
   ```
   Se um horário do dia já passou, pule pro próximo horário livre (nunca agende no passado).
   `draft: true` = chega como notificação na Caixa de entrada do TikTok; o Lucas escolhe a música viral e posta.
   Limite do TikTok: 5 rascunhos pendentes por 24h. Se o Zernio recusar por esse limite, NÃO insista:
   avise o Lucas que ele precisa finalizar os rascunhos pendentes.
7. **Registrar**: acrescente uma linha por carrossel em `historico.csv`, commit e push.
8. **Avisar o Lucas** (SendUserMessage, curto): o que foi agendado e quando, o top e o pior post recente
   com números, e o aprendizado do dia em 1 linha.

## Regras de conteúdo (não negociáveis)
- Estrutura: "passo a passo" pra fazer vídeo pro TikTok Shop com IA, com a Optimizze entrando
  **naturalmente** como a ferramenta de um dos passos (nunca como anúncio).
- CTA: "Comenta TTS e acessa a Optimizze pelo link da minha bio". Nunca prometer link por DM
  (o TikTok não permite DM automática).
- Honestidade: números só se estiverem num print real (ex.: R$ 185 mil da Kalodata) ou marcados
  como "exemplo". Não inventar depoimentos, resultados ou recursos que a Optimizze não tem.
- Recursos reais da Optimizze: Remix Inteligente (envia vídeo que já vendeu; devolve V1 Otimizada e Fiel,
  V2 Variação de Contexto, V3 Variação Criativa), Resumo da otimização (Hook, Estrutura da Copy, CTA),
  Modo Gravação (cenas com FALA/AÇÃO/TOM), Prompts de vídeo por cena, plano mensal R$29,90 e anual R$197.
- Sem emoji dentro dos slides (não há fonte de emoji); emojis só na legenda.
- Hashtags que performaram: `#tiktokshop #tiktokshopbr #ia #afiliados #afiliadosiniciantes`.
- Textos curtos por slide (máx. ~12 palavras), linguagem de afiliado brasileiro, direta.

## Quando pedir ajuda ao Lucas
- Faltam prints/fotos novos (os 8 de `assets/base/` cansam rápido): peça prints SEM legenda.
- Erro de conexão do Zernio/GitHub, ou métricas zeradas por mais de 2 dias.
