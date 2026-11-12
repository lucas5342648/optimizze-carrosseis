"""Monta os dados simulados do app a partir das respostas do conector.

Uso: python3 captura/montar_dados.py <em_alta.json> <projeto.json> <video_id> <pasta>
- em_alta.json: resposta de listar_em_alta (tipo video), copiada como veio.
- projeto.json: resposta de ver_projeto (status completed), copiada como veio.
Gera <pasta>/dados.json, <pasta>/dados_um.json (lista só com o vídeo escolhido) e baixa capas/fotos
para <pasta>/storage (precisa do domínio do Supabase liberado).
"""
import json, os, subprocess, sys
PREF = "https://wjhoedvxmkjvryqsbdto.supabase.co/storage/v1/object/public/biblioteca/"
UID = "00000000-0000-4000-8000-000000000001"
em_alta, projeto, vid, pasta = json.load(open(sys.argv[1])), json.load(open(sys.argv[2])), sys.argv[3], sys.argv[4]
os.makedirs(pasta, exist_ok=True)
# fala de exemplo só pra tela saber que o vídeo tem fala (o texto em si não aparece nos prints)
FALA = " ".join(s.get("fala", "") for v in projeto["versoes"][:1] for s in v.get("scenes_data", []))[:600] or "vídeo com fala guardada pela biblioteca"
cam = lambda u: u[len(PREF):] if u and u.startswith(PREF) else u
itens = em_alta["itens"]; dia = em_alta["dia"]
alta, videos, prods = [], [], {}
for it in itens:
    p = it.get("produto") or {}
    cat = p.get("categoria_id")
    alta.append(dict(dia=dia, tipo="video", item_id=it["video_id"], posicao=it["posicao"], vendas_7d=it["vendas_7d"],
                     faturamento_7d=it["faturamento_7d_brl"], views=it["views"], categoria_id=cat, postado_em=it["postado_em"], tem_transcricao=it["tem_fala"]))
    videos.append(dict(video_id=it["video_id"], criador=it["criador"], legenda=it["legenda"], duracao_s=it["duracao_s"], postado_em=it["postado_em"],
                       feito_por_ia=it["feito_por_ia"], categoria_id=cat, produto_id=p.get("produto_id"), capa=cam(it["capa"]), situacao="ativo",
                       transcricao=FALA, transcricao_tentativas=1))
    if p: prods[p["produto_id"]] = dict(produto_id=p["produto_id"], nome=p["nome"], categoria_id=cat, comissao=p["comissao"],
                                        fotos=[cam(f) for f in p["fotos"]], preco_brl=p["preco_brl"], preco_original_brl=p["preco_original_brl"], nota=None, avaliacoes=None)
escolhido = next(it for it in itens if it["video_id"] == vid)
P = projeto["project_id"]; agora = projeto.get("criado_em", "2026-01-01T00:00:00Z")
scripts = [dict(id=f"s{v['version']}", project_id=P, version=v["version"], created_at=agora, script_text=v.get("script_text", ""),
                reading_text=v.get("reading_text", ""), scenes_data=v.get("scenes_data", []), improvements=v.get("improvements", []),
                checagem_riscos=None, video_ia=None) for v in projeto["versoes"]]
guias = [dict(id=f"g{g['version']}", project_id=P, version=g["version"], created_at=agora, guide_content=g["guide_content"]) for g in projeto.get("guias_de_gravacao", [])]
a = projeto.get("analise") or {}
analise = dict(id="a1", project_id=P, created_at=agora, hook_score=a.get("hook_score"), risk_level="low", risk_notes=None, risk_suggestions=None,
               video_dna=None, structure_analysis=a.get("structure_analysis"), retention_analysis=a.get("retention_analysis"), triggers=a.get("triggers"))
proj = dict(id=P, user_id=UID, status="completed", content_type="remix", remix_mode="recreate_same_product", product_name=projeto.get("produto"),
            target_audience=None, product_description=None, product_images=None, transcription="", video_characteristics=None,
            biblioteca_video_id=vid, created_at=agora, updated_at=agora, title=None)
dados = dict(rpc=dict(check_subscription_active=True, touch_last_seen=None),
             funcoes={"biblioteca:acesso": dict(ligada=True, sem_requisicoes=False), "checar-roteiros": dict(ligada=False),
                      "biblioteca:analisar": dict(ligada=True, transcription=FALA, video_characteristics=""),
                      "biblioteca:produto": dict(ligada=True, produto=dict(nome=projeto.get("produto"), preco_brl=None, descricao="", fotos=[]))},
             tabelas=dict(emails_pagantes=[dict(id="e", email="afiliado@exemplo.com", assinatura_ativa=True, data_expiracao="2099-12-31", plano="yearly")],
                          projects=[proj], analyses=[analise], scripts=scripts, execution_guides=guias, profiles=[dict(id=UID, feedback_dismissed=True)],
                          biblioteca_em_alta=alta, biblioteca_videos=videos, biblioteca_produtos=list(prods.values()), biblioteca_salvos=[]))
json.dump(dados, open(f"{pasta}/dados.json", "w"), ensure_ascii=False)
um = json.loads(json.dumps(dados)); um["tabelas"]["biblioteca_em_alta"] = [r for r in alta if r["item_id"] == vid]
json.dump(um, open(f"{pasta}/dados_um.json", "w"), ensure_ascii=False)
caminhos = [v["capa"] for v in videos if v["capa"]] + [f for p in prods.values() for f in p["fotos"][:1]]
for c in caminhos:
    dest = f"{pasta}/storage/{c}"; os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.exists(dest): continue
    r = subprocess.run(["curl", "-s", "-o", dest, "-w", "%{http_code}", "--max-time", "20", PREF + c], capture_output=True, text=True)
    if r.stdout != "200":
        print("sem imagem:", c, r.stdout); os.path.exists(dest) and os.remove(dest)
print("ok", pasta, "| vídeo", vid, "posição", escolhido["posicao"])
