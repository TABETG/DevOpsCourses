import re, pathlib, json, html as H

out = pathlib.Path('/mnt/user-data/outputs')
src = pathlib.Path('/home/claude/pipes2.py').read_text()
ns = {}
exec(src.split('L = {1:')[0].replace("src = pathlib.Path('/home/claude/pipes.py').read_text()", "src = pathlib.Path('/home/claude/pipes.py').read_text()"), ns)
pipe, st = ns['pipe'], ns['st']
BLOG = "https://blog.stephane-robert.info/docs/homelab/"

SEC = r'''<h3>7.5 Construire un homelab DevSecOps, « security-first »<span class="badge tag-important">Important</span></h3>
<p>Un homelab est le seul endroit où tu peux casser un pare-feu, planter un cluster et le reconstruire à 23 h sans conséquence : c'est ce qui transforme ce parcours en compétence réelle, et ce qu'un recruteur ne peut pas obtenir d'une IA. Cette section s'appuie sur le parcours <a href="''' + BLOG + r'''" rel="noopener">HomeLab DevSecOps de Stéphane Robert</a>, une référence francophone, et le relie aux chapitres de ce cours.</p>
<div class="note">Ce parcours impose « tout en Docker, rien en local » pour les TP : le homelab est l'exception assumée, c'est du matériel dédié (ou une VM cloud avec virtualisation imbriquée), jamais ton poste de travail. Sans matériel, la variante « homelab virtuel » ci-dessous couvre 80 % de l'apprentissage.</div>

<h4>Le piège du homelab classique, et l'ordre inverse</h4>
<p>La trajectoire habituelle : Proxmox sur un mini-PC, quelques VM, un K3s, un reverse proxy, des secrets en clair dans des YAML, « je sécuriserai plus tard ». Résultat : chaque service a ses propres identifiants, les mots de passe traînent dans l'historique Git, l'accès admin n'a pas d'authentification centrale. L'approche security-first inverse l'ordre : <strong>réseau → identité → secrets → charges de travail</strong>. Chaque nouveau service hérite alors du SSO, des secrets dynamiques, des certificats et des journaux, sans effort. C'est exactement la logique de la plateforme du chapitre 48, et celle des règles de plateforme du chapitre 43.3 (pas de dépendance circulaire).</p>

<h4>Trois couches</h4>
<div class="tablewrap"><table>
<tr><th>Couche</th><th>Composants</th><th>Rôle</th><th>Dans ce cours</th></tr>
<tr><td>Réseau</td><td>OPNsense (pare-feu, routeur, DNS local, IDS Suricata), switch manageable, Tailscale ou WireGuard</td><td>Segmenter en VLAN (MGMT 10.0.10.0/24, SERVERS 10.0.20.0/24, IOT 10.0.30.0/24 totalement isolé), contrôler les flux, accès distant sans port exposé</td><td>Chapitre 3 (réseau), 41.3 (zero trust)</td></tr>
<tr><td>Confiance (nœud admin Proxmox, hors cluster)</td><td>Fournisseur d'identité (authentik, ou Keycloak que tu connais), OpenBao (fork libre de Vault), step-ca (PKI interne, ACME)</td><td>Qui es-tu, quel secret as-tu le droit de lire, ce certificat est-il légitime</td><td>Chapitres 38 (secrets), 41 (authentification, PKI)</td></tr>
<tr><td>Exécution (cluster applicatif)</td><td>Talos Linux (ou K3s pour débuter), ArgoCD, Traefik, External Secrets, Prometheus + Grafana, puis Loki, Tempo, Longhorn</td><td>Consommer les services de confiance : OIDC partout, secrets injectés, certificats émis par la PKI</td><td>Niveaux 5 et 6, chapitre 18 (Talos)</td></tr>
</table></div>
<p><strong>Pourquoi la couche de confiance vit hors du cluster</strong> : si l'IdP tourne dans le cluster et que le cluster a un problème d'authentification, tu ne peux plus te connecter pour le réparer. Identité, secrets et PKI doivent survivre à la destruction du cluster pour permettre de le reconstruire. Même règle en entreprise : l'IdP de l'astreinte, l'outil d'incident et la documentation ne dépendent pas de la plateforme qu'ils servent.</p>

<h4>Quatre phases, dans l'ordre, avec une porte de sortie chacune</h4>
<div class="tablewrap"><table>
<tr><th>Phase</th><th>Ce que tu obtiens</th><th>Tu passes à la suivante quand</th></tr>
<tr><td>1. Fondations réseau (1 à 2 jours)</td><td>OPNsense installé, LAN propre, DNS local, accès distant Tailscale, Proxmox admin joignable</td><td>Tu as coupé le Wi-Fi local et tu joins encore OPNsense par Tailscale ; le plan de VLAN est écrit</td></tr>
<tr><td>2. Nœud admin de confiance</td><td>IdP avec MFA sur le compte admin, OpenBao initialisé, DNS enrichi (auth.lab.local, vault.lab.local), sauvegardes configurées</td><td>Les clés de descellement d'OpenBao sont stockées hors site ; ton compte personnel existe dans l'IdP</td></tr>
<tr><td>3. Cluster applicatif</td><td>Talos (kubectl get nodes), ArgoCD derrière l'IdP, Traefik avec wildcard *.apps.lab.local, External Secrets relié à OpenBao, Prometheus + Grafana</td><td>Une application réelle a été déployée par ArgoCD ET un secret a transité depuis OpenBao ; avant, tu as un cluster, pas une chaîne de livraison</td></tr>
<tr><td>4. Industrialisation et chaîne d'approvisionnement (continue)</td><td>Golden images Packer + Ansible, registre privé (Harbor ou Zot), pipeline qui construit, scanne et signe (Cosign), SBOM stockés avec les images, Kyverno</td><td>La politique « images signées obligatoires » est passée en audit sur un namespace de test, puis en refus ; sinon elle bloque tout et tu la désactives en urgence</td></tr>
</table></div>
<p>Si tu dois arbitrer, sacrifie la phase 4 avant la phase 1 : un pare-feu mal posé se paie sur toutes les couches, un SBOM manquant ne casse aucun service. Et documente ton installation dès le premier jour : dans six mois, c'est ton futur toi qui reconstruit.</p>

<h4>Matériel, et variante sans matériel</h4>
<ul>
<li><strong>Matériel</strong> : un mini-PC à deux interfaces réseau pour OPNsense (Intel N100 suffit), un mini-PC pour le nœud admin, un ou trois mini-PC (N100, Ryzen) pour le cluster, un switch manageable pour les VLAN, un SSD par nœud ; budget de 500 à 1 000 € pour un ensemble complet, silencieux et sobre. Pas de serveur rack : bruit, consommation, et rien de plus à apprendre.</li>
<li><strong>Homelab virtuel</strong> : une seule machine (ou une VM cloud avec virtualisation imbriquée, comme un serveur Hetzner à quelques euros par mois) qui fait tourner Proxmox, avec OPNsense, le nœud admin et Talos en VM à l'intérieur. Tu perds la vraie segmentation physique et le switch, tu gardes tout le reste : VLAN virtuels, IdP, OpenBao, PKI, cluster, GitOps, chaîne d'approvisionnement. C'est la version compatible avec ta règle « rien sur le poste ».</li>
<li><strong>Ce que ce cours te fait déjà faire en Docker</strong> (kind, Vault, Keycloak, ArgoCD, Prometheus) est la phase 3 et 4 en miniature ; le homelab ajoute le réseau, la virtualisation et l'exploitation dans la durée : sauvegardes, mises à jour, pannes réelles.</li>
</ul>

<h4>Du homelab à la preuve de compétence</h4>
<div class="tablewrap"><table>
<tr><th>Pratiqué dans le homelab</th><th>Compétence</th><th>Validation</th><th>Chapitres</th></tr>
<tr><td>OPNsense, VLAN, pare-feu, IDS</td><td>Sécurité réseau</td><td>projet vitrine, LFCS</td><td>3, 41</td></tr>
<tr><td>Proxmox, templates, sauvegardes</td><td>Virtualisation, administration</td><td>LFCS, RHCSA</td><td>2, 7</td></tr>
<tr><td>Ansible, Packer, Terraform</td><td>Automatisation, IaC</td><td>RHCE, Terraform Associate</td><td>16 à 18</td></tr>
<tr><td>Talos, ArgoCD, External Secrets</td><td>Kubernetes, GitOps</td><td>CKA, CKAD</td><td>25 à 31</td></tr>
<tr><td>Prometheus, Grafana, Loki</td><td>Observabilité</td><td>projet vitrine</td><td>32 à 36</td></tr>
<tr><td>Cosign, Kyverno, Harbor, SBOM</td><td>Chaîne d'approvisionnement</td><td>CKS</td><td>39, 40</td></tr>
</table></div>
<div class="entretien"><strong>En entretien</strong> — « Vous avez un homelab ? » est une vraie question de recruteur DevSecOps. La bonne réponse décrit une architecture, pas une liste de VM : « réseau segmenté par OPNsense, identité et secrets hors cluster pour éviter la dépendance circulaire, Talos piloté en GitOps, images signées vérifiées à l'admission ». Puis une panne que tu as réparée toi-même, et ce que tu en as changé.</div>
'''

PIPE = pipe("pipe-homelab", "Dans quel ordre construire le homelab pour ne pas tout refaire ?",
 ["matériel", "phase 1 : réseau", "phase 2 : confiance", "phase 3 : cluster", "phase 4 : chaîne d'approvisionnement", "exploitation"],
 [st("matériel", ["mini-PC 2 ports réseau → OPNsense", "mini-PC admin → Proxmox (IdP, OpenBao, PKI)", "3 mini-PC → cluster Talos", "switch manageable, 1 SSD par nœud", "budget ≈ 800 €, silencieux"], "Le matériel se choisit pour l'architecture, pas l'inverse : deux ports réseau pour le pare-feu, un nœud dédié à la confiance."),
  st("réseau", ["OPNsense : routage, filtrage, DNS local", "VLAN MGMT 10.0.10.0/24, SERVERS 10.0.20.0/24, IOT 10.0.30.0/24 (isolé)", "Tailscale : accès distant sans port ouvert", "test : Wi-Fi coupé, OPNsense joignable ? oui"], "Rien d'autre ne démarre tant que le réseau n'est pas stable et joignable à distance : c'est la seule phase « immédiate »."),
  st("confiance", ["Proxmox admin, hors du futur cluster", "IdP : compte admin avec MFA, ton compte perso", "OpenBao initialisé, clés de descellement hors site", "step-ca : PKI interne, ACME", "DNS : auth.lab.local, vault.lab.local"], "Identité, secrets et certificats existent avant les applications ; s'ils vivaient dans le cluster, une panne du cluster empêcherait de le réparer."),
  st("cluster", ["Talos : 1 control plane, 2 workers (kubectl get nodes)", "ArgoCD, connecté à l'IdP (OIDC)", "Traefik, wildcard *.apps.lab.local, certificats step-ca", "External Secrets ← OpenBao", "Prometheus + Grafana", "→ 1 application déployée par ArgoCD, 1 secret synchronisé"], "Le cluster ne fait que consommer la couche de confiance ; la porte de sortie est une application réelle livrée par GitOps avec un secret venu d'OpenBao."),
  st("chaîne", ["Packer + Ansible : golden images Debian", "Harbor : registre privé", "CI : build, scan Trivy, SBOM Syft, signature Cosign", "Kyverno : images signées obligatoires (audit → refus)"], "Chaque maillon ne vaut que si le précédent est là : signer sans admission ne bloque rien ; un SBOM sans registre est introuvable le jour de la CVE."),
  st("exploitation", ["sauvegardes Proxmox Backup Server, restauration testée", "mises à jour mensuelles : OPNsense, Proxmox, Talos", "Longhorn, Loki, Tempo, Velero quand le besoin arrive", "journal de bord : ce qui a cassé, ce que tu as changé"], "Le homelab n'est jamais fini : c'est l'exploitation dans la durée, pannes comprises, qui construit la compétence que les recruteurs cherchent.", ["journal de bord : ce qui a cassé, ce que tu as changé"])],
 "4 phases, chacune avec une porte de sortie, puis l'exploitation continue",
 "D'après la roadmap HomeLab DevSecOps de Stéphane Robert : réseau, confiance, cluster, chaîne d'approvisionnement, dans cet ordre et pas autrement. Sacrifier la phase 4 avant la phase 1.", sep=' → ')

EXO = r'''<div class="exo"><span class="tag">Exercice 7.5</span>
<p>Ton homelab tourne : Keycloak et Vault sont déployés dans le cluster Talos, comme le reste. Un soir, une mise à jour de Talos casse le CNI ; plus aucun Pod ne communique. Que se passe-t-il quand tu veux te connecter à ArgoCD pour revenir en arrière, et comment l'architecture security-first l'évite ?</p>
<details><summary>Corrigé</summary><div class="sol">ArgoCD délègue son authentification à Keycloak, qui tourne dans le cluster cassé : impossible de se connecter, et External Secrets ne peut plus lire Vault, lui aussi dans le cluster. C'est la dépendance circulaire. Avec l'IdP, le coffre et la PKI sur le nœud admin hors cluster, tu te connectes encore (Tailscale, IdP vivant), tu reconstruis le cluster depuis Git, External Secrets resynchronise les secrets et tout revient. Même principe qu'en entreprise pour l'IdP de l'astreinte et l'outil d'incident.</div></details></div>

'''
TP = ('<li>Homelab : rédige ton plan en une page (matériel ou variante virtuelle, plan d\'adressage et VLAN, ce qui va sur le nœud admin, distribution Kubernetes, les quatre phases avec leurs portes de sortie), commité dans <code>docs/homelab.md</code>. Si tu as le matériel ou une VM cloud à virtualisation imbriquée : phase 1 (OPNsense + Tailscale) et phase 2 (Proxmox admin avec Keycloak ou authentik, OpenBao, step-ca) ce mois-ci, en suivant les guides de Stéphane Robert ; phase 3 avec Talos au niveau 5 ; phase 4 au niveau 7. Tiens un journal de bord des pannes.</li>')

p = out/'devops-niveau-1-conteneurs.html'; s = p.read_text()
assert '7.5 Construire un homelab' not in s
key = 'Pour sortir du lot — Firecracker'; i = s.index(key); j = s.rfind('<div class="niche">', 0, i)
s = s[:j] + SEC + '\n' + PIPE + '\n' + s[j:]
s = s.replace('<div class="tp"><span class="tag">Travail pratique 7', EXO + '<div class="tp"><span class="tag">Travail pratique 7', 1)
i = s.index('<div class="tp"><span class="tag">Travail pratique 7'); j = s.index('</ol>', i); s = s[:j] + TP + s[j:]
s = s.replace('<li>Comparer VMware, Proxmox et Nutanix, piloter chacun en ligne de commande et en Terraform, et cadrer une sortie de VMware</li>',
              '<li>Comparer VMware, Proxmox et Nutanix, piloter chacun en ligne de commande et en Terraform, et cadrer une sortie de VMware</li><li>Concevoir un homelab DevSecOps security-first : réseau, confiance hors cluster, cluster, chaîne d\'approvisionnement</li>', 1)
s = s.replace('<li>En entreprise, les VM tournent sur VMware, Proxmox (KVM, open source) ou Nutanix (AHV, hyperconvergé) ; la sortie de VMware est un programme fréquent, piloté en Terraform et Ansible.</li>',
              '<li>En entreprise, les VM tournent sur VMware, Proxmox (KVM, open source) ou Nutanix (AHV, hyperconvergé) ; la sortie de VMware est un programme fréquent, piloté en Terraform et Ansible.</li><li>Homelab security-first : réseau, puis identité et secrets hors cluster, puis le cluster, puis la chaîne d\'approvisionnement ; jamais l\'inverse.</li>', 1)
s = s.replace('<li>VMware, Proxmox, Nutanix : hyperviseur, plan de contrôle, stockage, HA, sauvegarde, IaC, quand ; les commandes qm/pct/vzdump et acli/ncc ; le quorum.</li>',
              '<li>VMware, Proxmox, Nutanix : hyperviseur, plan de contrôle, stockage, HA, sauvegarde, IaC, quand ; les commandes qm/pct/vzdump et acli/ncc ; le quorum.</li><li>Homelab : les trois couches, les quatre phases et leurs portes de sortie, pourquoi la couche de confiance vit hors du cluster.</li>', 1)
p.write_text(s); print('7 :', re.findall(r'<h3>(7\.\d) ', s))

# renvois depuis 43.3 (plateforme) et 18 (Talos)
p = out/'devops-niveau-8-sre-architecture.html'; s = p.read_text()
if 'homelab' not in s:
    s = s.replace("l'IdP de l'astreinte, la documentation et l'outil d'incident vivent ailleurs)", "l'IdP de l'astreinte, la documentation et l'outil d'incident vivent ailleurs ; c'est aussi le principe du nœud admin de confiance du homelab, chapitre 7.5)", 1); p.write_text(s); print('43 ok')
p = out/'devops-niveau-3-infrastructure-as-code.html'; s = p.read_text()
if 'chapitre 7.5' not in s:
    s = s.replace('Talos Linux', 'Talos Linux (la distribution retenue pour le cluster du homelab, chapitre 7.5)', 1); p.write_text(s); print('18 ok')

# page d'accueil : ressources externes
ip = out/'devops-parcours-complet.html'; t = ip.read_text()
if 'Ressources externes' not in t:
    t = t.replace('<h2>Aide-mémoire</h2>',
        '<h2>Ressources externes</h2>\n<ul>\n<li><a href="' + BLOG + '" rel="noopener">HomeLab DevSecOps, Stéphane Robert</a> : le parcours de référence en français pour construire un laboratoire personnel security-first (matériel, OPNsense et Tailscale, nœud admin Proxmox avec authentik et OpenBao, roadmap en quatre phases). Le chapitre 7.5 de ce cours s\'en inspire et le relie aux chapitres concernés ; le reste du blog (formations OPNsense, Proxmox, Talos, supply chain, examens blancs) est un complément utile à chaque niveau.</li>\n</ul>\n<h2>Aide-mémoire</h2>', 1)
    t = t.replace('<td><strong>Virtualisation : VMware, Proxmox, Nutanix</strong></td><td><a href="devops-niveau-1-conteneurs.html#c7">hyperviseurs en entreprise, commandes, IaC, HA, sauvegarde (7.4)</a>',
                  '<td><strong>Virtualisation et homelab</strong></td><td><a href="devops-niveau-1-conteneurs.html#c7">hyperviseurs en entreprise, commandes, IaC, HA, sauvegarde (7.4), homelab security-first (7.5)</a>', 1)
    ip.write_text(t); print('index ok')
