"""Place des images pédagogiques dans les pages du site, au bon endroit, sans doublon.
Principe : 00_… vue d'ensemble → en tête ; révision → section de révision ; sinon → chapitre dont le titre
ressemble le plus au nom de l'image (repli : ordre des images). Jeu principal en ligne, jeu secondaire en galerie.
Usage : python3 images_place.py <site> <racine des images> [--plan]"""
import sys, re, json, pathlib, unicodedata, shutil
from PIL import Image

SITE = pathlib.Path(sys.argv[1]); SRC = pathlib.Path(sys.argv[2]); PLAN_ONLY = '--plan' in sys.argv
# page → [(dossier, rôle, filtre facultatif sur les noms)]
JEUX = {
 'site-00-charte-graphique.html': [('00_Charte_Graphique_DevOps_Courses_Images_Pedagogiques', 'principal', None)],
 'devops-00-fondations.html': [('00_Fondations_Du_Poste_Vide_Au_Premier_Service_En_Ligne_Images_Pedagogiques', 'principal', None)],
 'devops-01-virtualisation-et-conteneurs.html': [('01_Virtualisation_Et_Conteneurs_Docker_En_Profondeur_Images_Pedagogiques', 'secondaire', None)],
 'devops-02-integration-et-livraison-continues.html': [('02_Integration_Et_Livraison_Continues_CI_CD_Images_Pedagogiques', 'secondaire', None), ('devops-03-infrastructure-as-code', 'secondaire-tete', None)],
 'devops-03-infrastructure-as-code.html': [('infrastructure_as_code_images_svg', 'principal', None)],
 'devops-04-cloud.html': [('devops-04-cloud', 'principal', None), ('04_Cloud_AWS_Azure_GCP_FinOps_Multicloud_Images_Pedagogiques', 'secondaire', None), ('HTML 5 KOTLIN', 'secondaire-tete', ['41-6', '44-9'])],
 'devops-05-kubernetes.html': [('05_Kubernetes_Architecture_Helm_ArgoCD_ServiceMesh_Autoscaling_Images_Pedagogiques', 'principal', None)],
 'devops-06-observabilite.html': [('06_Observabilite_Logs_Prometheus_OpenTelemetry_SLO_Incidents_Images_Pedagogiques', 'principal', None), ('devops_06_observabilite_images_png', 'secondaire', None)],
 'devops-07-securite-devsecops.html': [('07_Securite_DevSecOps_Vault_Kubernetes_Sigstore_ZeroTrust_Conformite_Images_Pedagogiques', 'principal', None), ('devops_07_securite_devsecops_images_png', 'secondaire', None)],
 'devops-08-sre-et-architecture.html': [('08_SRE_Architecture_Resilience_PRA_Performance_Microservices_Platform_Engineering_Images_Pedagogiques', 'principal', None), ('devops_08_sre_architecture_images_png', 'secondaire', None)],
 'devops-09-expert-et-leadership.html': [('09_Expert_Leadership_Plateformes_Migration_Gouvernance_DORA_Changement_IA_Images_Pedagogiques', 'principal', None), ('devops_09_expert_leadership_images_png', 'secondaire', None)],
 'devops-10-aide-memoire.html': [('10_Aide_Memoire_DevOps_Commandes_Bonnes_Pratiques_Images_Pedagogiques', 'principal', None), ('devops_10_aide_memoire_images_png', 'secondaire', None)],
 'devops-11-fiches-entretien.html': [('11_Fiches_Entretien_DevOps_TechLead_SRE_Leadership_Images_Pedagogiques', 'principal', None), ('devops_11_fiches_entretien_images_png', 'secondaire', None)],
 'cours-01-react.html': [('cours_01_react_images_png', 'principal', None)],
 'cours-02-angular.html': [('cours_02_angular_images_png', 'principal', None)],
 'cours-03-vue.html': [('cours_03_vue_images_png', 'principal', None)],
 'cours-11-struts-hibernate-jsp.html': [('cours_04_struts_hibernate_jsp_images_png', 'principal', None)],
 'cours-12-kotlin.html': [('html devlops 5', 'principal', None), ('cours_05_kotlin_images_png', 'secondaire', None), ('HTML 5 KOTLIN', 'secondaire-tete', ['37-1', '38-2', '39-3', '40-4', '41-5', '42-7', '43-8'])],
 'cours-13-java-pki-signature-electronique.html': [('cours_06_java_pki_signature_images_png', 'principal', None)],
 'cours-21-microservices.html': [('cours_21_microservices_images_png', 'principal', None)],
 'cours-31-ia-agentique.html': [('10_IA_Agentique_AI_Engineering_Zero_a_Expert_Images_Pedagogiques', 'principal', None), ('cours_31_ia_agentique_images_png', 'secondaire', None)],
 'cours-32-assistants-ia-copilot-claude-chatgpt.html': [('cours_32_assistants_ia_copilot_claude_chatgpt_images_png', 'principal', None)],
 'cours-41-keycloak-et-iam.html': [('cours_41_keycloak_et_iam_images_png', 'principal', None)],
 'cours-51-cloud.html': [('cours_51_cloud_images_png', 'principal', None)],
 'cours-52-aws.html': [('cours_52_aws_images_png', 'principal', None)],
 'cours-53-alibaba-cloud.html': [('cours_53_alibaba_cloud_images_png', 'principal', None)],
 'cours-61-data-platform-aws-talend.html': [('cours_61_data_platform_aws_talend_images_png', 'principal', None)],
 'cours-62-talend.html': [('cours_62_talend_images_png', 'principal', None)],
 'cours-63-monitoring.html': [('63_Monitoring_Prometheus_Grafana_ELK_Loki_Zero_a_Expert_Images_Pedagogiques', 'principal', None), ('cours_16_monitoring_images_png', 'secondaire', None)],
 'cours-91-savoir-etre-de-zero-a-expert.html': [('91_Savoir_Etre_Zero_a_Expert_Progression_Par_Paliers_Images_Pedagogiques', 'principal', None), ('cours_18_savoir_etre_images_png', 'secondaire', None)],
 'cours-92-savoir-etre-situations-et-attitudes.html': [('92_Savoir_Etre_Situations_Attitudes_Developpeur_TechLead_Manager_Directeur_Images_Pedagogiques', 'principal', None), ('cours_19_savoir_etre_situations_images_png', 'secondaire', None)],
}
# titres lus sur les images aux noms génériques
TITRES = {
 ('devops-04-cloud', '01-1'): ('20', 'Chapitre 20 — Concepts du cloud'), ('devops-04-cloud', '01-2'): ('21', 'Chapitre 21 — AWS en profondeur'),
 ('devops-04-cloud', '02-3'): ('22', 'Chapitre 22 — Azure et GCP : équivalences'), ('devops-04-cloud', '03-4'): ('23', 'Chapitre 23 — FinOps'),
 ('devops-04-cloud', '04-5'): ('24', 'Chapitre 24 — Multi-cloud et hybride'), ('devops-04-cloud', '05-6'): ('rev', 'Révision express du niveau 4'),
 ('devops-03-infrastructure-as-code', '20-1'): ('top', "Niveau 2 — vue d'ensemble de l'intégration et de la livraison continues (1)"),
 ('devops-03-infrastructure-as-code', '21-2'): ('top', "Niveau 2 — vue d'ensemble de l'intégration et de la livraison continues (2)"),
 ('HTML 5 KOTLIN', '41-6'): ('top', "Niveau 4 — vue d'ensemble du cloud (1)"), ('HTML 5 KOTLIN', '44-9'): ('top', "Niveau 4 — vue d'ensemble du cloud (2)"),
}
PREFIXE = lambda page: {'site-00-charte-graphique.html': 'charte', 'devops-10-aide-memoire.html': 'aide-memoire', 'devops-11-fiches-entretien.html': 'fiches-entretien'}.get(page) or (('niveau-' + page[7:9]) if page.startswith('devops-') else page[:8])
STOP = set('de la le les des du et en a au aux un une pour par sur avec sans dans vers ou the and of zero expert images png cours niveau chapitre vue ensemble fiche fiches'.split())
SYN = {'k8s': 'kubernetes', 'kube': 'kubernetes', 'iac': 'infrastructure', 'obs': 'observabilite', 'secu': 'securite', 'pg': 'postgresql', 'cicd': 'ci'}

def norm(t): return ''.join(c for c in unicodedata.normalize('NFD', t.lower()) if unicodedata.category(c) != 'Mn')
def jetons(t):
    return {SYN.get(w, w) for w in re.split(r'[^a-z0-9]+', norm(re.sub(r'<[^>]+>', ' ', t))) if len(w) >= 3 and w not in STOP and not w.isdigit()}
def proche(a, b): return a == b or (len(a) >= 5 and len(b) >= 5 and (a.startswith(b[:5]) or b.startswith(a[:5])))
def score(ji, jc): return sum(1 for a in ji if any(proche(a, b) for b in jc))

def legende(nom):
    t = re.sub(r'^\d+[_\- ]*', '', pathlib.Path(nom).stem).replace('_', ' ').replace('-', ' ').strip()
    for a, b in [('vue ensemble', "vue d'ensemble :"), ('ci cd', 'CI/CD'), (' iac', ' infrastructure as code'), ('star', 'STAR'), ('sbi', 'SBI'), ('n3', 'niveau 3'),
                 ('rto rpo', 'RTO et RPO'), ('rpo rto', 'RPO et RTO'), ('aws', 'AWS'), ('gcp', 'GCP'), ('sre', 'SRE'), ('dora', 'DORA'), ('slo', 'SLO'), ('llm', 'LLM'), ('mcp', 'MCP'), ('iam', 'IAM'), ('oidc', 'OIDC'), ('pki', 'PKI'), ('tls', 'TLS')]:
        t = re.sub(r'\b' + a.strip() + r'\b', b.strip(), t)
    t = re.sub(r"vue d'ensemble :\s*$", "vue d'ensemble", t)
    return 'Fiche visuelle : ' + (t[:1].upper() + t[1:])

def chapitres(s):
    out = []
    for m in re.finditer(r'<article(?P<attr>[^>]*)>', s):
        a = m.group('attr'); e = s.find('</article>', m.end()); body = s[m.end():e]
        i = re.search(r'id="([^"]+)"', a)
        titre = ' '.join(re.findall(r'<(?:h2|span class="chapnum")[^>]*>(.*?)</(?:h2|span)>', body, flags=re.S)[:2])
        h3 = ' '.join(re.findall(r'<h3[^>]*>(.*?)</h3>', body, flags=re.S))
        out.append({'id': i.group(1) if i else None, 'titre': re.sub(r'<[^>]+>', '', titre), 'jt': jetons(titre) | jetons(h3), 'jt2': jetons(titre)})
    return out

FORCER = {('cours_01_react_images_png', '05_react'): 'c10'}
def cible(page, dossier, nom, chs, rang, n_images, prec=-1):
    f = next((v for (d, k), v in FORCER.items() if d == dossier and k in nom), None)
    if f: return f
    cle = next((k for k in TITRES if k[0] == dossier and k[1] in nom), None)
    if cle:
        c, _ = TITRES[cle]
        if c in ('top', 'rev'): return c
        return next((x['id'] for x in chs if x['id'] == 'c' + c), 'top')
    st = pathlib.Path(nom).stem.lower()
    if 'vue_ensemble' in st or 'vue-ensemble' in st or (st.startswith('00_') and 'strategie' not in st): return 'top'
    if any(k in st for k in ('revision', 'express', 'synthese_questions')): return 'rev'
    m = re.match(r'^(\d{2})_', st)
    if m and int(m.group(1)) >= 11 and any(x['id'] == 'c' + str(int(m.group(1))) for x in chs): return 'c' + str(int(m.group(1)))
    ji = jetons(st)
    notes = [(score(ji, x['jt2']) * 2 + score(ji, x['jt']), -k, x) for k, x in enumerate(chs) if k >= max(0, prec)]   # ordre des chapitres respecté
    best = max(notes, key=lambda t: (t[0], t[1])) if notes else (0, 0, None)
    if best[0] > 0: return best[2]['id'] or ('#' + str(-best[1]))
    k = min(len(chs) - 1, max(0, round((rang - 1) * len(chs) / max(1, n_images - 1))))   # repli : ordre des images
    return chs[k]['id'] or ('#' + str(k))

def plan():
    P = []
    for page, jeux in JEUX.items():
        s = (SITE / page).read_text(); chs = chapitres(s)
        for dossier, role, filtre in jeux:
            imgs = sorted(p for p in (SRC / dossier).iterdir() if p.suffix.lower() in ('.png', '.jpg', '.svg') and (not filtre or any(f in p.name for f in filtre)))
            prec = -1
            for r, p in enumerate(imgs):
                c = cible(page, dossier, p.name, chs, r, len(imgs), prec)
                idx = next((k for k, x in enumerate(chs) if x['id'] == c or ('#' + str(k)) == c), None)
                if idx is not None: prec = idx
                cle = next((k for k in TITRES if k[0] == dossier and k[1] in p.name), None)
                cap = ('Fiche visuelle : ' + TITRES[cle][1]) if cle else legende(p.name)
                slug = PREFIXE(page) + '-' + re.sub(r'[^a-z0-9]+', '-', norm((TITRES[cle][1] if cle else re.sub(r'^\d+[_\- ]*', '', p.stem)))).strip('-')[:70]
                if role.startswith('secondaire'): slug += '-variante'
                P.append({'page': page, 'src': str(p), 'role': 'secondaire' if role.startswith('secondaire') else 'principal', 'cible': 'top' if role == 'secondaire-tete' else c, 'legende': cap, 'slug': slug})
    return P

def convertir(e):
    p = pathlib.Path(e['src']); dst_dir = SITE / 'images'
    if p.suffix.lower() == '.svg':
        dst = dst_dir / (e['slug'] + '.svg'); shutil.copy(p, dst); return dst.name
    dst = dst_dir / (e['slug'] + '.webp')
    if not dst.exists():
        im = Image.open(p).convert('RGB'); im.thumbnail((1500, 1500)); im.save(dst, 'WEBP', quality=72, method=6)
    return dst.name

FIG = lambda e, f: f'<figure class="fig zoomable" id="{e["slug"]}"><img src="images/{f}" alt="{e["legende"]}" loading="lazy" decoding="async"><figcaption>{e["legende"]}</figcaption></figure>'
def galerie(gid, figs): return f'<div class="gallery" id="{gid}"><strong>Autres fiches visuelles — clique pour agrandir</strong><div class="g-items">{"".join(figs)}</div></div>'

def appliquer(P):
    pages = {}
    for e in P: pages.setdefault(e['page'], []).append(e)
    bilan = {}
    for page, es in pages.items():
        path = SITE / page; s = path.read_text()
        # identifiants pour les articles qui n'en ont pas (fiches entretien)
        k = [0]
        def ident(m):
            k[0] += 1; return f'<article id="fiche-{k[0]}"' + m.group(1) + '>'
        s = re.sub(r'<article(?! id=)([^>]*)>', ident, s)
        chs = chapitres(s)
        for e in es:
            if e['cible'].startswith('#'): e['cible'] = chs[int(e['cible'][1:])]['id']
        groupes = {}
        for e in es:
            if f'id="{e["slug"]}"' in s: continue                        # déjà placée
            groupes.setdefault(e['cible'], []).append(e)
        n = 0
        for c, lot in groupes.items():
            prin = [e for e in lot if e['role'] == 'principal']; autres = [e for e in lot if e not in prin[:1]]
            inline = FIG(prin[0], convertir(prin[0])) if prin else ''
            figs = [FIG(e, convertir(e)) for e in autres]
            gid = 'gal-' + (c if c not in ('top', 'rev') else c + '-fiches')
            if c == 'top': pos = s.index('<article')
            elif c == 'rev':
                pos = s.find('<ol class="quiz">')
                if pos < 0:
                    last = [x for x in chapitres(s) if x['id']][-1]['id']; a = s.index(f'<article id="{last}"'); pos = s.index('</article>', a)
            else:
                a = s.index(f'<article id="{c}"'); fin = s.index('</article>', a); ex = s.find('<div class="exo"', a); pos = ex if 0 < ex < fin else fin
            bloc = ''
            if inline: bloc += '\n' + inline + '\n'
            if figs:
                if f'id="{gid}"' in s:                                     # galerie existante : on ajoute dedans
                    gi = s.index(f'id="{gid}"'); gp = s.index('<div class="g-items">', gi) + len('<div class="g-items">')
                    s = s[:gp] + ''.join(figs) + s[gp:]
                    if pos > gp: pos += len(''.join(figs))
                else: bloc += galerie(gid, figs) + '\n'
            s = s[:pos] + bloc + s[pos:]; n += len(lot)
        path.write_text(s); bilan[page] = n
    return bilan

if __name__ == '__main__':
    P = plan()
    json.dump(P, open('/tmp/plan_images.json', 'w'), ensure_ascii=False, indent=0)
    if PLAN_ONLY:
        import collections
        for page in JEUX:
            es = [e for e in P if e['page'] == page]
            c = collections.Counter(e['cible'] for e in es)
            print(f'{page[:44]:44} {len(es):3} images | ' + ' '.join(f'{k}:{v}' for k, v in sorted(c.items(), key=lambda x: (len(x[0]), x[0]))))
    else:
        print(appliquer(P))
