import re, pathlib, html

out = pathlib.Path('/mnt/user-data/outputs')

# ---------------- 7.4 Hyperviseurs en entreprise ----------------
SEC = r'''<h3>7.4 Hyperviseurs en entreprise : VMware, Proxmox, Nutanix<span class="badge tag-coeur">Par cœur</span></h3>
<p>En mission, les conteneurs tournent sur des VM, et ces VM tournent sur l'un de ces trois. Depuis le rachat de VMware par Broadcom (2023) et ses hausses de licences, la « sortie de VMware » est l'un des programmes les plus fréquents des DSI françaises ; Proxmox et Nutanix en sont les deux destinations principales, avec le cloud public.</p>
<div class="tablewrap"><table>
<tr><th></th><th>VMware vSphere</th><th>Proxmox VE</th><th>Nutanix</th></tr>
<tr><td>Hyperviseur</td><td>ESXi (type 1, propriétaire)</td><td>KVM (type 1, Linux Debian) + conteneurs LXC</td><td>AHV (type 1, KVM durci et intégré)</td></tr>
<tr><td>Plan de contrôle</td><td>vCenter</td><td>Interface web sur chaque nœud, cluster sans serveur central (corosync)</td><td>Prism Element (cluster) et Prism Central (multi-clusters)</td></tr>
<tr><td>Stockage</td><td>vSAN, baies SAN/NAS</td><td>ZFS, LVM, Ceph intégré (hyperconvergé), NFS, iSCSI</td><td>AOS : stockage distribué hyperconvergé natif (CVM sur chaque nœud)</td></tr>
<tr><td>Haute disponibilité</td><td>HA, DRS, vMotion</td><td>HA, migration à chaud, pas d'équilibrage automatique natif (scripts, ProxLB)</td><td>HA, migration à chaud, équilibrage automatique</td></tr>
<tr><td>Sauvegarde</td><td>Veeam et écosystème</td><td>Proxmox Backup Server (incrémental, déduplication, chiffrement), Veeam depuis 2024</td><td>Snapshots et réplication natifs, Mine, Veeam, HYCU</td></tr>
<tr><td>Kubernetes</td><td>Tanzu</td><td>Rien de natif : Talos, RKE2, kubeadm sur des VM ; opérateur Proxmox pour Cluster API</td><td>NKP (Nutanix Kubernetes Platform, ex Karbon, issu de D2iQ)</td></tr>
<tr><td>Réseau</td><td>NSX</td><td>Linux bridge, VLAN, SDN (VXLAN, EVPN) depuis la 8.x</td><td>Flow (microsegmentation), Flow Virtual Networking</td></tr>
<tr><td>Infrastructure as Code</td><td>Provider vsphere, Packer, PowerCLI</td><td>Provider Terraform <code>bpg/proxmox</code>, collection Ansible <code>community.general.proxmox_*</code>, API REST, Packer builder</td><td>Provider Terraform <code>nutanix/nutanix</code>, collection <code>nutanix.ncp</code>, API v4, Calm (self-service)</td></tr>
<tr><td>Licence et coût</td><td>Abonnement par cœur, cher, bundles imposés</td><td>Open source (AGPL) gratuit ; support par abonnement par socket, prix bas</td><td>Abonnement par cœur, appliances certifiées ou matériel validé, prix élevé, support fort</td></tr>
<tr><td>Quand</td><td>Existant à maintenir, écosystème et compétences en place</td><td>PME, collectivités, laboratoires, edge, budgets contraints, équipes Linux à l'aise</td><td>Grandes organisations qui veulent l'hyperconvergence clé en main, le support et l'intégration cloud (NC2 sur AWS/Azure)</td></tr>
</table></div>

<h4>Proxmox VE en pratique</h4>
<pre><code># Sur un nœud Proxmox (ou via l'API : tout ce qui suit existe en REST)
pveversion ; pvecm status ; pvecm nodes                 # version ; état du cluster corosync ; nœuds
qm list ; qm config 100 ; qm start 100 ; qm shutdown 100 ; qm migrate 100 node2 --online   # VM (QEMU/KVM)
pct list ; pct enter 200 ; pct exec 200 -- apt update    # conteneurs LXC
qm create 9000 --name ubuntu-tpl --memory 2048 --net0 virtio,bridge=vmbr0 --scsihw virtio-scsi-pci
qm importdisk 9000 noble-server-cloudimg-amd64.img local-lvm ; qm set 9000 --ide2 local-lvm:cloudinit --boot order=scsi0 ; qm template 9000   # template cloud-init
qm clone 9000 101 --name web1 --full ; qm set 101 --ipconfig0 ip=10.0.1.11/24,gw=10.0.1.1 --sshkeys ~/.ssh/id_ed25519.pub
pvesm status ; pvesm list local-lvm                      # stockages
vzdump 101 --storage pbs --mode snapshot                  # sauvegarde (vers Proxmox Backup Server)
ha-manager add vm:101 --state started ; ha-manager status # haute disponibilité
pveum user add ci@pve ; pveum aclmod / -user ci@pve -role PVEVMAdmin ; pveum user token add ci@pve terraform   # compte et token pour l'IaC
journalctl -u pve-cluster -u corosync -f                  # quand le cluster tousse</code></pre>
<pre><code># Terraform : une VM depuis le template cloud-init (provider bpg/proxmox)
provider "proxmox" { endpoint = "https://pve.lab:8006/", api_token = var.pve_token, insecure = false }
resource "proxmox_virtual_environment_vm" "web" {
  name = "web1" ; node_name = "pve1"
  clone { vm_id = 9000 }
  cpu { cores = 2 } ; memory { dedicated = 2048 }
  initialization {
    ip_config { ipv4 { address = "10.0.1.11/24", gateway = "10.0.1.1" } }
    user_account { username = "deploy", keys = [var.ssh_pub] }
  }
}
# Ansible : inventaire dynamique des VM Proxmox (plugin community.general.proxmox) puis les rôles du chapitre 17</code></pre>
<ul>
<li><strong>Cluster</strong> : trois nœuds minimum (quorum corosync ; deux nœuds + QDevice sinon), réseau dédié à corosync et un autre à Ceph, horloges synchronisées. Un nœud isolé du quorum fence ses VM HA : c'est voulu.</li>
<li><strong>Stockage</strong> : ZFS local pour la simplicité et les snapshots ; Ceph pour le partagé et la HA (trois nœuds, disques NVMe, réseau 10 Gbit minimum) ; NFS pour les ISO et sauvegardes.</li>
<li><strong>Sauvegarde</strong> : Proxmox Backup Server sur une machine distincte, vérification des sauvegardes planifiée, restauration testée ; 3-2-1 comme au chapitre 44.</li>
<li><strong>Sécurité</strong> : pare-feu intégré par datacenter, nœud et VM ; utilisateurs avec rôles minimaux et tokens d'API (jamais root@pam pour l'IaC) ; MFA (TOTP, WebAuthn) ; certificats ACME intégrés ; mises à jour de l'hôte Debian.</li>
<li><strong>Kubernetes dessus</strong> : Talos Linux (chapitre 18) ou RKE2 sur des VM clonées par Terraform ; le stockage persistant par Ceph CSI ou Longhorn ; MetalLB pour les Services LoadBalancer.</li>
</ul>

<h4>Nutanix en pratique</h4>
<pre><code># Depuis une CVM (Controller VM) ou Prism ; l'API v4 et Terraform couvrent tout
ncli cluster info ; ncli host list ; ncli vm list          # cluster, hôtes, VM (interface historique)
acli vm.list ; acli vm.create web1 memory=2G num_vcpus=2 ; acli vm.disk_create web1 clone_from_image=ubuntu-24.04 ; acli vm.on web1   # AHV
acli vm.snapshot_create web1 snapshot_name=avant-migration ; acli vm.clone web2 clone_from_vm=web1
acli net.list ; acli image.list                              # réseaux, catalogue d'images
nutanix_cluster_check ; ncc health_checks run_all            # NCC : vérifications de santé
cluster status ; allssh "date"                               # état et commande sur tous les nœuds
# Prism Central : catégories (étiquettes) → politiques Flow (microsegmentation), protection (snapshots, réplication), Calm (blueprints self-service), NKP (clusters Kubernetes)</code></pre>
<pre><code># Terraform : VM sur AHV (provider nutanix/nutanix)
provider "nutanix" { username = var.user, password = var.password, endpoint = "prism-central.lab", insecure = false }
resource "nutanix_virtual_machine" "web" {
  name = "web1" ; cluster_uuid = data.nutanix_cluster.c.id
  num_vcpus_per_socket = 2 ; memory_size_mib = 2048
  disk_list { data_source_reference = { kind = "image", uuid = data.nutanix_image.ubuntu.id } }
  nic_list { subnet_uuid = data.nutanix_subnet.app.id }
  guest_customization_cloud_init_user_data = base64encode(file("cloud-init.yaml"))
  categories { name = "Environment", value = "prod" }     # pilote Flow et les politiques de protection
}
# Ansible : collection nutanix.ncp (ntnx_vms, ntnx_images, inventaire dynamique)</code></pre>
<ul>
<li><strong>Hyperconvergence</strong> : chaque nœud apporte calcul et stockage ; la CVM de chaque nœud forme le stockage distribué AOS (réplication RF2 ou RF3, localité des données). Ajouter un nœud ajoute les deux ; c'est simple à exploiter et à faire grandir, et c'est ce qu'on paie.</li>
<li><strong>Catégories</strong> : le mécanisme central ; elles pilotent la microsegmentation Flow (politiques par catégorie, pas par IP), la protection des données (calendriers de snapshots et réplication vers un autre site : le PRA du chapitre 44), le placement et les quotas.</li>
<li><strong>Exploitation</strong> : mises à jour orchestrées par LCM (firmware, AOS, AHV, sans coupure), NCC pour la santé, Prism Central pour la vue multi-clusters, l'analyse de capacité et le coût ; support Nutanix comme argument principal.</li>
<li><strong>Migration</strong> : Nutanix Move migre des VM depuis VMware, Hyper-V ou AWS avec réplication continue puis bascule courte ; c'est l'outil de la sortie de VMware. NC2 permet d'étendre le cluster sur AWS ou Azure (hybride, chapitre 24).</li>
<li><strong>Kubernetes</strong> : NKP fournit des clusters conformes gérés depuis Prism, avec CSI Nutanix pour les volumes ; sinon Talos ou RKE2 comme sur Proxmox.</li>
</ul>

<h4>Ce que le DevOps y fait</h4>
<p>Il ne clique pas dans Prism ni dans l'interface Proxmox : il décrit les VM en Terraform à partir de templates cloud-init construits par Packer, les configure par Ansible avec un inventaire dynamique, y déploie Kubernetes par Cluster API ou Talos, branche la sauvegarde et le monitoring (exporters Proxmox et Nutanix pour Prometheus), et traite la plateforme de virtualisation comme une ressource de la landing zone (chapitre 49) avec ses SLO (chapitre 43). Une sortie de VMware est un projet de migration classique (chapitre 50) : inventaire, dépendances, vagues, Move ou export OVF, tests, décommissionnement.</p>
'''
EXOS = r'''<div class="exo"><span class="tag">Exercice 7.3</span>
<p>Une collectivité de 40 VM, deux administrateurs Linux, budget en baisse, doit quitter VMware. Proxmox ou Nutanix ? Argumente, puis indique ce qui te ferait changer d'avis.</p>
<details><summary>Corrigé</summary><div class="sol">Proxmox : coût de licence nul (support par socket abordable), KVM et Debian que les administrateurs connaissent, ZFS ou Ceph selon le nombre de nœuds, Proxmox Backup Server, IaC par Terraform et Ansible. Changerait la décision : exigence de support éditeur contractuel fort, équipe sans compétence Linux, besoin d'hyperconvergence à grande échelle avec LCM et réplication multi-sites clé en main, ou un existant Nutanix ailleurs dans l'organisation ; alors Nutanix, malgré le coût.</div></details></div>

<div class="exo"><span class="tag">Exercice 7.4</span>
<p>Un cluster Proxmox à deux nœuds redémarre spontanément ses VM HA quand le lien réseau entre les nœuds tombe. Explique et corrige.</p>
<details><summary>Corrigé</summary><div class="sol">Sans quorum (deux nœuds = pas de majorité possible en cas de coupure), chaque nœud se croit isolé ; le fencing HA arrête ses VM pour éviter une double exécution. Correction : un troisième vote (QDevice sur une petite machine, ou un troisième nœud), un réseau corosync dédié et redondant, et ne mettre en HA que ce qui doit l'être.</div></details></div>

'''
TP = ('<li>Hyperviseurs d\'entreprise : sans installer d\'hyperviseur sur ton poste (interdit), écris et valide (<code>terraform validate</code>) un module Terraform Proxmox (provider bpg) et un module Nutanix créant la même VM CrisisShield depuis un template cloud-init, plus le playbook Ansible d\'inventaire dynamique correspondant ; documente les commandes <code>qm</code>, <code>pct</code>, <code>vzdump</code>, <code>acli</code> et <code>ncc</code> que tu utiliserais le premier jour. Si tu disposes d\'une machine de labo ou d\'un compte Nutanix Community Edition, exécute-les et note les différences avec le cours.</li>')

p = out/'devops-niveau-1-conteneurs.html'; s = p.read_text()
assert '7.4 Hyperviseurs' not in s
key = 'Pour sortir du lot — Firecracker'; i = s.index(key); j = s.rfind('<div class="niche">', 0, i)
s = s[:j] + SEC + s[j:]
s = s.replace('<div class="tp"><span class="tag">Travail pratique 7', EXOS + '<div class="tp"><span class="tag">Travail pratique 7', 1)
i = s.index('<div class="tp"><span class="tag">Travail pratique 7'); j = s.index('</ol>', i); s = s[:j] + TP + s[j:]
s = s.replace('<li>Choisir entre VM et conteneur selon le besoin</li>',
              '<li>Choisir entre VM et conteneur selon le besoin</li><li>Comparer VMware, Proxmox et Nutanix, piloter chacun en ligne de commande et en Terraform, et cadrer une sortie de VMware</li>', 1)
s = s.replace('<li>Sous Windows, Docker tourne dans une VM WSL 2 : chemins, performances et fins de ligne en découlent.</li>',
              '<li>Sous Windows, Docker tourne dans une VM WSL 2 : chemins, performances et fins de ligne en découlent.</li><li>En entreprise, les VM tournent sur VMware, Proxmox (KVM, open source) ou Nutanix (AHV, hyperconvergé) ; la sortie de VMware est un programme fréquent, piloté en Terraform et Ansible.</li>', 1)
s = s.replace('<li>Ce que Docker Desktop fait sous Windows ; deux pièges de Git Bash.</li>',
              '<li>Ce que Docker Desktop fait sous Windows ; deux pièges de Git Bash.</li><li>VMware, Proxmox, Nutanix : hyperviseur, plan de contrôle, stockage, HA, sauvegarde, IaC, quand ; les commandes qm/pct/vzdump et acli/ncc ; le quorum.</li>', 1)
s = s.replace('Machines virtuelles et hyperviseurs</h2>', 'Machines virtuelles et hyperviseurs : VMware, Proxmox, Nutanix</h2>', 1)
p.write_text(s); print('7 :', re.findall(r'<h3>(7\.\d) ', s))

# ---------------- chapitre 50 : cas de sortie de VMware ----------------
p = out/'devops-niveau-9-expert-leadership.html'; s = p.read_text()
if 'Sortie de VMware' not in s:
    add = r'''<h4>Cas fréquent : la sortie de VMware</h4>
<p>Après le rachat par Broadcom, beaucoup d'organisations quittent vSphere. C'est une migration de plateforme (« relocate » ou « replatform ») qui suit le même programme : inventaire des VM et de leurs dépendances (vCenter, RVTools, CMDB), choix de la cible par lot (Proxmox, Nutanix, cloud public, ou conteneurisation directe pour ce qui s'y prête : chapitre 7.4), fondations d'abord (réseau, stockage, sauvegarde, IaC sur la nouvelle plateforme), migration outillée (Nutanix Move, export OVF/OVA et <code>qm importovf</code> sur Proxmox, agents de réplication), vagues par criticité avec tests et retour arrière, puis décommissionnement de vSphere et fin des licences. Pièges : les VM à licences liées au matériel, les appliances propriétaires, les dépendances réseau (VLAN, NSX), les sauvegardes Veeam à reconfigurer, et les compétences de l'équipe.</p>
'''
    s = s.replace('<h3>50.3 Les données', add + '<h3>50.3 Les données', 1)
    s = s.replace('<li>Les 7 R avec une répartition réaliste : beaucoup de replatform, peu de refactor, du retire.</li>',
                  '<li>Les 7 R avec une répartition réaliste : beaucoup de replatform, peu de refactor, du retire ; la sortie de VMware est un programme type.</li>', 1)
    p.write_text(s); print('50 : cas VMware ajouté')

# ---------------- aide-mémoire ----------------
p = out/'devops-aide-memoire.html'; s = p.read_text()
if 'id="virt"' not in s:
    def esc(t): return html.escape(t)
    cmds = [("pvecm status ; pvecm nodes ; qm list ; pct list","cluster Proxmox ; VM ; conteneurs LXC"),("qm start|shutdown|migrate 100 node2 --online","cycle de vie et migration à chaud"),
            ("qm clone 9000 101 --full ; qm set 101 --ipconfig0 ip=…","VM depuis un template cloud-init"),("vzdump 101 --storage pbs --mode snapshot","sauvegarde vers Proxmox Backup Server"),
            ("ha-manager add vm:101 --state started ; ha-manager status","haute disponibilité"),("pveum user token add ci@pve terraform","token d'API pour l'IaC"),
            ("acli vm.list ; acli vm.create … ; acli vm.on web1","Nutanix AHV"),("acli vm.snapshot_create web1 snapshot_name=x","snapshot"),("ncli cluster info ; cluster status ; ncc health_checks run_all","état et santé Nutanix"),
            ("terraform : providers bpg/proxmox et nutanix/nutanix","VM en code"),("ansible : community.general.proxmox_* et nutanix.ncp","configuration et inventaire dynamique")]
    bps = ["Jamais de clic dans Prism ni Proxmox : templates Packer/cloud-init, Terraform, Ansible avec inventaire dynamique ; comptes et tokens d'API à droits minimaux.",
           "Proxmox : trois nœuds ou QDevice pour le quorum, réseaux dédiés corosync et Ceph, Proxmox Backup Server séparé, MFA, mises à jour Debian.",
           "Nutanix : tout passe par les catégories (Flow, protection, placement), LCM pour les mises à jour, NCC avant toute opération, Move pour migrer depuis VMware.",
           "Traiter la plateforme comme un service : SLO, sauvegardes testées, monitoring par exporters, PRA par réplication entre sites.",
           "Sortie de VMware = projet de migration (chapitre 50) : inventaire, dépendances, vagues, retour arrière, décommissionnement effectif."]
    art = ('<article id="virt"><div class="chaphead"><span class="chapnum">Niveau 1, chapitre 7</span></div><h2>Proxmox et Nutanix</h2>'
           '<div class="tablewrap"><table class="cmd"><tr><th>Commande</th><th>Ce qu\'elle fait</th></tr>' + ''.join(f'<tr><td>{esc(c)}</td><td>{esc(d)}</td></tr>' for c,d in cmds) + '</table></div>'
           '<div class="bp"><strong>Bonnes pratiques</strong><ol>' + ''.join(f'<li>{esc(b)}</li>' for b in bps) + '</ol></div></article>\n')
    s = s.replace('<article id="compose">', art + '<article id="compose">', 1)
    s = s.replace('<a href="#compose">Docker Compose</a>', '<a href="#virt">Proxmox et Nutanix</a><a href="#compose">Docker Compose</a>', 1)
    p.write_text(s); print('aide-mémoire : section virtualisation ajoutée')

# ---------------- carte des compétences ----------------
p = out/'devops-parcours-complet.html'; s = p.read_text()
if 'Proxmox' not in s:
    s = s.replace('<tr><td><strong>Docker et CI/CD</strong></td>',
                  '<tr><td><strong>Virtualisation : VMware, Proxmox, Nutanix</strong></td><td><a href="devops-niveau-1-conteneurs.html#c7">hyperviseurs en entreprise, commandes, IaC, HA, sauvegarde (7.4)</a>, <a href="devops-niveau-9-expert-leadership.html#c50">sortie de VMware (50)</a>, <a href="devops-niveau-3-infrastructure-as-code.html#c18">Packer et Talos (18)</a></td></tr>\n<tr><td><strong>Docker et CI/CD</strong></td>', 1)
    p.write_text(s); print('carte ok')
