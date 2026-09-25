"""Cours Monitoring de zéro à expert (13 chapitres) : Prometheus, Grafana, Alertmanager, ELK, Loki, OpenTelemetry. Usage : python3 monitoring_pages.py <dossier>"""
import sys, runpy, pathlib
g = runpy.run_path(pathlib.Path(__file__).with_name('front_gen.py'), run_name='front'); ch, page = g['ch'], g['page']
def T(rows, head): return '<div class="tablewrap"><table><tr>' + ''.join(f'<th>{h}</th>' for h in head) + '</tr>' + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows) + '</table></div>'
DK = "Tout en conteneur : chaque outil tourne par Docker Compose, rien n'est installé sur le poste ; les commandes d'outillage passent par <code>docker run</code> ou <code>docker compose exec</code>."

MO = [
ch("Fondamentaux : quoi surveiller, et avec quelle pile", 'j',
 ["Surveiller, c'est savoir si le service rend ce qu'il promet ; observer, c'est pouvoir expliquer pourquoi quand il ne le fait pas.", "Quatre signaux d'or pour un service (latence, trafic, erreurs, saturation), la méthode RED pour les requêtes, la méthode USE pour les ressources.", "Une pile a quatre étages : collecter, stocker, visualiser, alerter ; Prometheus et Grafana pour les métriques, ELK ou Loki pour les journaux, Tempo ou Jaeger pour les traces."],
 ["Choisir quoi mesurer avec les quatre signaux d'or, RED et USE", "Distinguer tirer et pousser, boîte blanche et boîte noire", "Monter une première pile Prometheus, Grafana et Loki en Docker"],
 [("Quoi mesurer", T([
    ("Quatre signaux d'or", "un service", "latence, trafic, erreurs, saturation", "p95 de POST /incidents, requêtes par seconde, taux de 5xx, pool de connexions"),
    ("RED", "chaque point d'entrée", "débit (Rate), erreurs (Errors), durée (Duration)", "par route de l'API et par consommateur Kafka"),
    ("USE", "chaque ressource", "utilisation, saturation, erreurs", "CPU, mémoire, disque, réseau, connexions de base")], ("Méthode", "Pour", "Ce qu'on mesure", "Exemple CrisisShield")), None),
  ("Tirer, pousser, boîte blanche, boîte noire", "Prometheus tire les métriques : il interroge chaque cible sur /metrics et sait immédiatement si elle ne répond plus. On ne pousse que pour les traitements trop courts pour être interrogés. La boîte blanche mesure de l'intérieur (instrumentation) ; la boîte noire sonde de l'extérieur comme un utilisateur : les deux se complètent.", None),
  ("Une première pile en Docker", DK, """# compose.yaml : première pile de supervision
services:
  prometheus: { image: prom/prometheus:v2.54.1, ports: ["9090:9090"], volumes: ["./prometheus.yml:/etc/prometheus/prometheus.yml:ro"] }
  grafana:    { image: grafana/grafana:11.2.0, ports: ["3000:3000"], volumes: ["./grafana/provisioning:/etc/grafana/provisioning:ro"] }
  loki:       { image: grafana/loki:3.2.0, ports: ["3100:3100"] }
  node-exporter: { image: prom/node-exporter:v1.8.2, pid: host, volumes: ["/:/host:ro,rslave"], command: ["--path.rootfs=/host"] }
  incidents:  { image: crisisshield/incidents:1.4.2, environment: { MANAGEMENT_ENDPOINTS_WEB_EXPOSURE_INCLUDE: "health,prometheus" } }
# prometheus.yml
global: { scrape_interval: 15s, evaluation_interval: 15s }
scrape_configs:
  - job_name: incidents
    metrics_path: /actuator/prometheus
    static_configs: [ { targets: ["incidents:8080"] } ]
  - job_name: node
    static_configs: [ { targets: ["node-exporter:9100"] } ]""")],
 [("Tout est vert dans Grafana (CPU à 30 %, mémoire à 50 %) mais les utilisateurs se plaignent. Qu'as-tu oublié de mesurer ?", "Ce que vit l'utilisateur : le taux d'erreurs et la latence des requêtes (RED), mesurés à l'entrée et par une sonde externe. Des ressources saines ne disent rien d'un service qui renvoie des 500 ou répond en huit secondes."),
  ("Question d'entretien : monitoring ou observabilité ?", "Le monitoring surveille des indicateurs connus et alerte quand ils dérivent ; l'observabilité permet d'explorer des questions imprévues grâce à des données riches et corrélées. On a besoin des deux : l'un prévient, l'autre explique.")],
 ("Première pile de supervision", ["Compose : Prometheus, Grafana, Loki, node-exporter et CrisisShield qui expose /actuator/prometheus.", "Un tableau de bord RED pour le service, USE pour la machine.", "Une sonde externe (blackbox) sur la page d'accueil de CrisisShield."],
  "Attendu : les deux cibles sont « up » dans Prometheus ; le tableau de bord montre débit, erreurs et p95 par route ; arrêter CrisisShield fait passer la sonde à 0 en moins d'une minute.")),

ch("Prometheus : modèle de données, instrumentation, collecte", 'c',
 ["Prometheus interroge ses cibles à intervalle régulier et stocke des séries temporelles, identifiées par un nom de métrique et des labels.", "Quatre types : le compteur ne fait que monter, la jauge monte et descend, l'histogramme répartit les valeurs par tranches, le résumé calcule ses quantiles côté client.", "La découverte de services (Kubernetes, fichiers, DNS) trouve les cibles ; les exporters traduisent ce qui ne parle pas Prometheus."],
 ["Lire le format d'exposition et choisir le bon type", "Instrumenter une application Spring avec Micrometer", "Configurer collecte, découverte, réécriture de labels et exporters"],
 [("Le modèle de données", "Une série, c'est un nom et une combinaison de labels ; chaque combinaison nouvelle crée une série de plus. Les noms suivent une convention : unité en suffixe (_seconds, _bytes) et _total pour les compteurs.", """# format d'exposition (extrait de /actuator/prometheus)
# TYPE incidents_declares_total counter
incidents_declares_total{zone="N1",gravite="P1"} 42
# TYPE jdbc_connections_active gauge
jdbc_connections_active{pool="HikariPool-1"} 7
# TYPE http_server_requests_seconds histogram
http_server_requests_seconds_bucket{uri="/v1/incidents",method="POST",status="201",le="0.1"} 812
http_server_requests_seconds_bucket{uri="/v1/incidents",method="POST",status="201",le="0.5"} 990
http_server_requests_seconds_bucket{uri="/v1/incidents",method="POST",status="201",le="+Inf"} 1000
http_server_requests_seconds_sum{uri="/v1/incidents",method="POST",status="201"} 61.3
http_server_requests_seconds_count{uri="/v1/incidents",method="POST",status="201"} 1000"""),
  ("Instrumenter avec Micrometer", "Spring Boot expose déjà HTTP, JVM, pool de connexions et Kafka. On ajoute les métriques métier, avec des labels bornés (zone, gravité), jamais un identifiant.", """# application.yml
management:
  endpoints.web.exposure.include: health,prometheus
  metrics.distribution:
    percentiles-histogram.http.server.requests: true          # histogramme agrégeable
    slo.http.server.requests: 100ms,300ms,1s                  # tranches alignées sur les SLO
  metrics.tags: { application: incidents }
---
@Service class IncidentService {
  private final Counter declares; private final Timer escalade;
  IncidentService(MeterRegistry r) {
    declares = Counter.builder("incidents.declares").tag("canal", "api").register(r);        // → incidents_declares_total
    escalade = Timer.builder("incidents.escalade").publishPercentileHistogram().register(r);
  }
  public void declarer(Incident i) { declares.increment(); /* … */ }
}"""),
  ("Collecter, découvrir, réécrire", "Dans Kubernetes, Prometheus découvre les Pods et on filtre par annotation ou label ; hors Kubernetes, un fichier de cibles suffit. La réécriture de labels choisit les cibles et nettoie les labels avant stockage.", """scrape_configs:
  - job_name: pods
    kubernetes_sd_configs: [ { role: pod } ]
    relabel_configs:
      - { source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape], action: keep, regex: "true" }
      - { source_labels: [__meta_kubernetes_namespace], target_label: namespace }
      - { source_labels: [__meta_kubernetes_pod_label_app], target_label: service }
    metric_relabel_configs:
      - { source_labels: [__name__], regex: "jvm_gc_.*_seconds_max", action: drop }     # séries inutiles supprimées
  - job_name: fichiers
    file_sd_configs: [ { files: ["/etc/prometheus/cibles/*.yml"], refresh_interval: 1m } ]
# exporters courants : node (machine), blackbox (sondes), postgres, kafka, redis, nginx""")],
 [("Pourquoi un histogramme plutôt qu'un résumé pour la latence d'une API répartie sur trois Pods ?", "Les histogrammes s'agrègent : on additionne les tranches des trois Pods puis on calcule le quantile. Les quantiles d'un résumé sont calculés dans chaque Pod et ne s'additionnent pas : leur moyenne n'est pas le p95 du service."),
  ("Question d'entretien : pourquoi Prometheus tire-t-il les métriques ?", "Tirer donne l'état de chaque cible (up), centralise la configuration et empêche un client d'inonder le serveur ; le push reste pour les traitements éphémères, via la Pushgateway, avec la limite qu'elle garde la dernière valeur même si le traitement a disparu.")],
 ("Instrumenter CrisisShield", ["Métriques métier : incidents_declares_total par zone et gravité, histogramme de la durée d'escalade.", "Collecte par fichier de cibles, exporters PostgreSQL et node ; réécriture des labels service et environnement.", "Supprimer à la collecte deux familles de séries inutiles et mesurer le gain."],
  "Attendu : toutes les cibles sont « up » ; les métriques métier apparaissent avec des labels bornés ; prometheus_tsdb_head_series baisse après la suppression des séries inutiles.")),

ch("PromQL : interroger sans se tromper", 'c',
 ["PromQL enchaîne un sélecteur, des fonctions et des agrégations ; un vecteur instantané donne une valeur par série, un vecteur de plage une fenêtre de valeurs.", "rate() s'applique à un compteur, jamais à une jauge ; on calcule rate avant d'agréger avec sum, sinon les redémarrages faussent tout.", "histogram_quantile se calcule sur des tranches agrégées ; les règles d'enregistrement précalculent les requêtes coûteuses des tableaux de bord et des alertes."],
 ["Écrire des requêtes de débit, d'erreurs et de latence justes", "Éviter les pièges classiques de rate, sum et des quantiles", "Écrire des règles d'enregistrement et les tester"],
 [("Sélecteurs et fonctions", "On filtre par labels (égalité, différence, expression régulière), on choisit une fenêtre adaptée à l'intervalle de collecte (au moins quatre fois), et on compare avec le passé grâce à offset.", """up{job="incidents"}                                            # la cible répond-elle ?
http_server_requests_seconds_count{uri="/v1/incidents", status=~"5.."}
rate(http_server_requests_seconds_count{job="incidents"}[5m])    # requêtes par seconde
increase(incidents_declares_total[1h])                          # incidents déclarés sur une heure
avg_over_time(jdbc_connections_active[10m])                     # moyenne d'une jauge
rate(http_server_requests_seconds_count[5m]) / rate(http_server_requests_seconds_count[5m] offset 1w)   # comparé à la semaine dernière"""),
  ("Agréger correctement", "Débit, taux d'erreurs et latence du service : on agrège après rate, en gardant les labels utiles avec by. Le quantile se calcule sur la somme des tranches, en conservant le label le.", """# débit par service
sum by (service) (rate(http_server_requests_seconds_count[5m]))
# taux d'erreurs du service (ratio, entre 0 et 1)
sum by (service) (rate(http_server_requests_seconds_count{status=~"5.."}[5m]))
  / sum by (service) (rate(http_server_requests_seconds_count[5m]))
# p95 de latence par service
histogram_quantile(0.95, sum by (le, service) (rate(http_server_requests_seconds_bucket[5m])))
# pièges : rate(sum(x)[5m]) est faux (redémarrages) ; rate() sur une jauge n'a pas de sens ; moyenne de p95 ≠ p95"""),
  ("Règles d'enregistrement", "Une requête lourde recalculée par vingt tableaux de bord coûte cher : une règle d'enregistrement la calcule une fois par intervalle et la stocke sous un nom qui dit son niveau, sa métrique et ses opérations.", """groups:
  - name: incidents-red
    interval: 30s
    rules:
      - record: service:http_requests:rate5m
        expr: sum by (service) (rate(http_server_requests_seconds_count[5m]))
      - record: service:http_errors:ratio_rate5m
        expr: sum by (service) (rate(http_server_requests_seconds_count{status=~"5.."}[5m])) / sum by (service) (rate(http_server_requests_seconds_count[5m]))
      - record: service:http_latency_seconds:p95_5m
        expr: histogram_quantile(0.95, sum by (le, service) (rate(http_server_requests_seconds_bucket[5m])))
# vérifier : docker run --rm -v "$PWD:/w" -w /w --entrypoint promtool prom/prometheus:v2.54.1 check rules regles.yml""")],
 [("Un collègue calcule le p95 du service avec avg(http_latency_p95) sur ses trois Pods. Qu'en penses-tu ?", "C'est faux : une moyenne de quantiles n'est pas un quantile. Il faut agréger les tranches de l'histogramme (sum by (le)) puis calculer histogram_quantile sur la somme."),
  ("Question d'entretien : différence entre rate et irate ?", "rate donne le débit moyen sur la fenêtre, lissé et adapté aux alertes et aux tendances ; irate n'utilise que les deux derniers points, très réactif mais bruité, réservé aux graphiques de détail.")],
 ("Dix requêtes et leurs tests", ["Écrire les dix requêtes utiles de CrisisShield : débit, erreurs, p95 et p99 par route, saturation du pool, incidents par zone.", "Transformer les plus lourdes en règles d'enregistrement.", "Écrire des tests unitaires de règles (promtool test rules) avec des séries simulées."],
  "Attendu : les tableaux de bord utilisent les règles et s'affichent en moins d'une seconde ; promtool test rules passe en CI ; un test échoue si l'on remplace sum(rate()) par rate(sum()).")),

ch("Alerter : règles, Alertmanager, fatigue", 'c',
 ["On alerte sur les symptômes vus par l'utilisateur (erreurs, latence, budget d'erreur) ; les causes (CPU, disque) servent au diagnostic ou deviennent des tickets.", "Alertmanager regroupe, route, inhibe et met en silence : une panne doit donner une page, pas deux cents.", "Chaque alerte a un propriétaire, une gravité, un runbook ; une alerte que personne ne traite est supprimée."],
 ["Écrire des règles d'alerte actionnables", "Configurer routage, regroupement et inhibition dans Alertmanager", "Réduire la fatigue d'alerte avec des mesures"],
 [("Des règles d'alerte utiles", "Une bonne alerte dit ce que vit l'utilisateur, depuis combien de temps, et quoi faire. La condition for évite de réveiller quelqu'un pour un pic de trente secondes ; le runbook donne les premiers gestes.", """groups:
  - name: incidents-alertes
    rules:
      - alert: IncidentsErreursElevees
        expr: service:http_errors:ratio_rate5m{service="incidents"} > 0.05
        for: 5m
        labels: { severity: page, equipe: crise }
        annotations:
          summary: "Incidents : {{ $value | humanizePercentage }} d'erreurs depuis 5 minutes"
          runbook_url: "https://runbooks.crisis.fr/incidents/erreurs"
      - alert: IncidentsBudgetErreurRapide         # consommation rapide du budget d'erreur (SLO 99,9 %)
        expr: service:http_errors:ratio_rate1h{service="incidents"} > (14.4 * 0.001) and service:http_errors:ratio_rate5m{service="incidents"} > (14.4 * 0.001)
        labels: { severity: page, equipe: crise }"""),
  ("Alertmanager", "Le routage envoie chaque alerte à la bonne équipe selon ses labels ; le regroupement fusionne les alertes d'une même panne ; l'inhibition fait taire les alertes secondaires quand une alerte principale est active ; le silence couvre une maintenance.", """route:
  receiver: tickets
  group_by: [alertname, service, namespace]
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  routes:
    - matchers: [ 'severity="page"', 'equipe="crise"' ]
      receiver: astreinte-crise
inhibit_rules:
  - source_matchers: [ 'alertname="NoeudIndisponible"' ]
    target_matchers: [ 'severity=~"page|ticket"' ]
    equal: [ node ]                                   # le nœud est tombé : on tait ses Pods
receivers:
  - name: astreinte-crise
    webhook_configs: [ { url: "http://pager-bridge:8080/alertes" } ]
  - name: tickets
    email_configs: [ { to: "crise-tickets@crisis.fr" } ]"""),
  ("Contre la fatigue d'alerte", "On mesure : nombre de pages par semaine d'astreinte, part des pages suivies d'une action, alertes jamais traitées. Objectif courant : moins de deux pages par nuit, chacune utile ; le reste devient ticket ou disparaît.", """# silence pour une maintenance planifiée (deux heures)
docker compose exec alertmanager amtool silence add service=incidents --duration=2h --comment="migration base V12"
# revue hebdomadaire : alertes les plus bruyantes
topk(10, sum by (alertname) (changes(ALERTS_FOR_STATE[7d])))""")],
 [("Une panne réseau d'un nœud déclenche 180 alertes et 180 pages. Que corriger ?", "Le regroupement (group_by sur service et nœud), une inhibition des alertes des Pods quand le nœud est indisponible, et le passage en ticket des alertes de cause ; la panne ne doit produire qu'une page, avec le bon runbook."),
  ("Question d'entretien : alerter sur le CPU à 80 % ?", "En page, non : un CPU à 80 % ne dit pas que l'utilisateur souffre. On alerte sur les erreurs, la latence ou le budget d'erreur ; le CPU sert au diagnostic, ou à un ticket de capacité s'il reste haut plusieurs jours.")],
 ("Alertes et astreinte de CrisisShield", ["Six règles : erreurs, latence p95, budget d'erreur rapide et lent, cible indisponible, sonde externe en échec.", "Alertmanager : routage par équipe, regroupement, inhibition par nœud, silence de maintenance.", "Simuler une panne de nœud et une montée d'erreurs ; compter les notifications reçues."],
  "Attendu : la panne de nœud produit une seule page ; la montée d'erreurs déclenche l'alerte en cinq minutes avec son runbook ; le silence de maintenance supprime toute notification pendant la fenêtre.")),

ch("Grafana : des tableaux de bord qui répondent à une question", 'c',
 ["Un tableau de bord répond à une question précise (« le service va-t-il bien ? », « où est le goulot ? ») ; une page de 80 graphiques ne répond à rien.", "En haut l'état et le SLO, puis RED du service, puis USE des ressources ; des variables pour changer de service ou d'environnement, des liens vers les journaux et les traces.", "Les tableaux de bord et les sources de données sont du code : provisionnés, relus en MR, versionnés."],
 ["Concevoir un tableau de bord lisible en dix secondes", "Utiliser variables et liens vers journaux et traces", "Provisionner Grafana entièrement par le code"],
 [("Une question par tableau de bord", "Le tableau de bord d'un service tient sur un écran : une ligne d'état (SLO, budget restant, alertes actives), une ligne RED, une ligne USE. Chaque panneau a une unité, un seuil coloré et un titre qui dit ce qu'il montre.", """Tableau de bord « Service Incidents » (au plus 12 panneaux)
ligne 1 : disponibilité sur 30 jours · budget d'erreur restant · alertes actives
ligne 2 : débit par route · taux d'erreurs par route · p95 et p99 par route
ligne 3 : CPU et mémoire des Pods · pool de connexions · retard des consommateurs Kafka
liens : journaux du service (Loki), traces lentes (Tempo), runbook"""),
  ("Variables et liens", "Une variable remplit une liste à partir des labels ; $__rate_interval choisit une fenêtre adaptée au zoom. Un lien de données ouvre les journaux ou les traces du même service sur la même période.", """# variable « service »
label_values(up{namespace="$namespace"}, service)
# panneau p95, fenêtre adaptée au zoom
histogram_quantile(0.95, sum by (le, uri) (rate(http_server_requests_seconds_bucket{service="$service"}[$__rate_interval])))
# lien de données vers les journaux du même service et de la même période
/explore?left={"datasource":"loki","queries":[{"expr":"{service=\\"$service\\"} |= \\"ERROR\\""}],"range":{"from":"${__from}","to":"${__to}"}}"""),
  ("Tout en code", "Les sources de données et les tableaux de bord sont provisionnés au démarrage à partir de fichiers ; une modification passe par une MR relue. Terraform ou Grafonnet génèrent le JSON pour éviter les copier-coller.", """# grafana/provisioning/datasources/sources.yaml
apiVersion: 1
datasources:
  - { name: Prometheus, type: prometheus, url: http://prometheus:9090, isDefault: true }
  - { name: Loki, type: loki, url: http://loki:3100 }
  - { name: Tempo, type: tempo, url: http://tempo:3200 }
# grafana/provisioning/dashboards/fournisseur.yaml
apiVersion: 1
providers: [ { name: crisis, folder: CrisisShield, type: file, options: { path: /etc/grafana/dashboards } } ]
# Terraform : resource "grafana_dashboard" "incidents" { config_json = file("dashboards/incidents.json") }""")],
 [("Le tableau de bord principal a 80 panneaux et personne ne s'en sert pendant les incidents. Que proposes-tu ?", "Le découper par question : un tableau de bord par service (état, RED, USE, sur un écran), un tableau de bord de parcours utilisateur, et des vues de détail reliées par des liens ; supprimer les panneaux que personne n'a ouverts depuis trois mois."),
  ("Question d'entretien : pourquoi provisionner Grafana par le code ?", "Pour que les tableaux de bord soient relus, versionnés, reproductibles entre environnements et restaurables ; un tableau de bord modifié à la main en production se perd au premier redéploiement.")],
 ("Tableaux de bord de CrisisShield en code", ["Provisionner Prometheus, Loki et Tempo comme sources de données.", "Tableau de bord « service » à variables (espace de noms, service), avec liens vers journaux et traces.", "Stocker le JSON dans le dépôt, le déployer par la CI, et vérifier qu'une modification manuelle est écrasée."],
  "Attendu : le même tableau de bord sert pour les cinq services grâce aux variables ; un clic sur un pic d'erreurs ouvre les journaux de la même période ; la CI redéploie le tableau de bord depuis le dépôt.")),

ch("Prometheus à l'échelle : cardinalité, haute disponibilité, long terme", 's',
 ["La mémoire et le coût de Prometheus suivent le nombre de séries actives : un label non borné (identifiant, URL brute) peut le faire tomber.", "La haute disponibilité se fait par paires identiques, dédoublonnées à la lecture ; Prometheus seul garde quelques semaines, pas des années.", "Pour le long terme et la vue globale : remote_write vers Mimir, Thanos ou VictoriaMetrics, avec sous-échantillonnage."],
 ["Mesurer et réduire la cardinalité", "Monter une paire de Prometheus avec dédoublonnage", "Envoyer les métriques vers un stockage long terme"],
 [("Maîtriser la cardinalité", "On cherche les métriques qui ont le plus de séries, puis les labels responsables ; on les supprime à la collecte ou on corrige l'instrumentation. Une alerte sur le nombre de séries prévient avant la panne.", """# les dix métriques qui ont le plus de séries
topk(10, count by (__name__) ({__name__=~".+"}))
# séries en mémoire, et leur croissance
prometheus_tsdb_head_series
deriv(prometheus_tsdb_head_series[1h])
# à la collecte : supprimer un label non borné
metric_relabel_configs:
  - { regex: "request_id|session_id", action: labeldrop }"""),
  ("Haute disponibilité et long terme", "Deux Prometheus identiques collectent les mêmes cibles, chacun avec un label de réplica ; la couche de requête dédoublonne. remote_write envoie les séries vers un stockage durable sur objet (S3), interrogeable sur des mois.", """global:
  external_labels: { cluster: prod-paris, replica: "$(POD_NAME)" }
remote_write:
  - url: http://mimir:9009/api/v1/push
    queue_config: { max_samples_per_send: 5000, capacity: 20000 }
    write_relabel_configs:
      - { source_labels: [__name__], regex: "go_.*|process_.*", action: drop }   # rien d'inutile en long terme
# Mimir ou Thanos : blocs dans S3, rétention 13 mois, sous-échantillonnage à 5 min puis 1 h"""),
  ("Fédération et coûts", "La fédération fait remonter des agrégats (règles d'enregistrement) d'un Prometheus de site vers un Prometheus global, jamais toutes les séries. Le coût se pilote : séries actives, octets par échantillon, rétention, et la question « qui regarde cette métrique ? ».", None)],
 [("Prometheus redémarre en boucle, OOMKilled, depuis la dernière mise en production. Démarche ?", "Regarder prometheus_tsdb_head_series et topk par métrique : une métrique nouvelle a probablement un label non borné (identifiant, URL avec paramètres). La supprimer à la collecte tout de suite, corriger l'instrumentation, et ajouter une alerte sur la croissance des séries."),
  ("Question d'entretien : Thanos, Mimir ou VictoriaMetrics ?", "Tous trois offrent stockage long terme, vue globale et haute disponibilité. Thanos s'ajoute à côté de Prometheus (sidecar), Mimir reçoit en remote_write avec une architecture multi-locataire, VictoriaMetrics mise sur la simplicité et la compacité ; le choix dépend de l'échelle et de l'équipe.")],
 ("Supervision durable", ["Injecter volontairement un label non borné, observer la croissance des séries, puis le supprimer à la collecte.", "Paire de Prometheus avec labels de réplica, remote_write vers Mimir (stockage MinIO en conteneur).", "Grafana sur Mimir : requête sur trente jours, dédoublonnage vérifié en arrêtant un réplica."],
  "Attendu : l'alerte de croissance des séries se déclenche avant l'OOM ; l'arrêt d'un réplica ne crée ni trou ni doublon dans les graphiques ; les requêtes sur trente jours répondent en quelques secondes.")),

ch("Superviser Kubernetes", 's',
 ["kube-prometheus-stack installe l'opérateur Prometheus, Alertmanager, Grafana, node-exporter et kube-state-metrics, avec des règles et des tableaux de bord prêts.", "Les applications se déclarent par ServiceMonitor ou PodMonitor ; les règles par PrometheusRule : tout est versionné avec l'application.", "kube-state-metrics dit l'état des objets (réplicas, redémarrages, Jobs), cAdvisor la consommation des conteneurs, node-exporter la machine."],
 ["Installer et régler kube-prometheus-stack", "Déclarer la collecte d'une application par ServiceMonitor", "Connaître les alertes Kubernetes essentielles"],
 [("kube-prometheus-stack", "L'installation se fait par Helm, avec des valeurs versionnées ; on règle la rétention, le stockage persistant, les sélecteurs de ServiceMonitor et l'Alertmanager de l'équipe.", """docker run --rm -v "$HOME/.kube:/root/.kube" -v "$PWD:/w" -w /w alpine/helm:3.16.2 \\
  upgrade --install supervision oci://ghcr.io/prometheus-community/charts/kube-prometheus-stack \\
  -n supervision --create-namespace -f valeurs-supervision.yaml
# valeurs-supervision.yaml (extrait)
prometheus:
  prometheusSpec:
    retention: 15d
    serviceMonitorSelectorNilUsesHelmValues: false        # prendre les ServiceMonitor de tous les espaces de noms
    storageSpec: { volumeClaimTemplate: { spec: { resources: { requests: { storage: 50Gi } } } } }"""),
  ("ServiceMonitor et PrometheusRule", "L'équipe de l'application livre, dans son propre dépôt, la façon de collecter ses métriques et ses règles d'alerte ; l'opérateur les prend en compte sans redémarrage.", """apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata: { name: incidents, namespace: crise, labels: { equipe: crise } }
spec:
  selector: { matchLabels: { app: incidents } }
  endpoints: [ { port: http, path: /actuator/prometheus, interval: 15s } ]
---
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata: { name: incidents, namespace: crise }
spec:
  groups: [ { name: incidents, rules: [ { alert: IncidentsErreursElevees, expr: 'service:http_errors:ratio_rate5m{service="incidents"} > 0.05', for: 5m, labels: { severity: page } } ] } ]"""),
  ("Les alertes essentielles", "", T([
    ("KubePodCrashLooping", "increase(kube_pod_container_status_restarts_total[15m]) > 3", "un conteneur redémarre en boucle"),
    ("KubeDeploymentReplicasMismatch", "kube_deployment_spec_replicas != kube_deployment_status_replicas_available", "des réplicas manquent depuis 15 min"),
    ("NodeFilesystemAlmostOutOfSpace", "node_filesystem_avail_bytes / node_filesystem_size_bytes < 0.1", "disque de nœud presque plein"),
    ("CPUThrottlingHigh", "rate(container_cpu_cfs_throttled_periods_total[5m]) / rate(container_cpu_cfs_periods_total[5m]) > 0.25", "limite CPU trop basse"),
    ("KubeJobFailed", "kube_job_status_failed > 0", "un Job a échoué"),
    ("KubePersistentVolumeFillingUp", "kubelet_volume_stats_available_bytes / kubelet_volume_stats_capacity_bytes < 0.1", "volume persistant presque plein")], ("Alerte", "Expression (simplifiée)", "Ce qu'elle signale")))],
 [("Un nouveau service tourne depuis deux semaines mais n'apparaît dans aucun tableau de bord. Pourquoi ?", "Personne n'a livré son ServiceMonitor, ou ses labels ne correspondent pas au sélecteur de Prometheus. On l'ajoute au modèle de service, et une alerte « service déployé sans cible collectée » (kube_deployment sans up correspondant) évite les services invisibles."),
  ("Question d'entretien : kube-state-metrics ou metrics-server ?", "metrics-server fournit la consommation instantanée pour kubectl top et l'autoscaler ; kube-state-metrics expose l'état des objets Kubernetes (réplicas, statuts, redémarrages) à Prometheus pour l'historique et les alertes.")],
 ("Supervision du cluster kind", ["Installer kube-prometheus-stack dans kind avec des valeurs versionnées.", "ServiceMonitor et PrometheusRule livrés avec CrisisShield.", "Provoquer un CrashLoop, un disque plein simulé et une limite CPU trop basse ; vérifier chaque alerte."],
  "Attendu : les trois pannes déclenchent leur alerte avec le bon espace de noms et le bon service ; les tableaux de bord Kubernetes fournis affichent les Pods de CrisisShield ; tout est réinstallable depuis le dépôt.")),

ch("La pile ELK : Elasticsearch, Logstash, Beats, Kibana", 'c',
 ["Elasticsearch stocke et indexe des documents JSON, avec une recherche plein texte rapide ; Kibana les explore et les met en tableaux de bord.", "La collecte passe par Filebeat ou Elastic Agent ; Logstash ou les ingest pipelines transforment (analyse, enrichissement, masquage).", "Des journaux structurés en JSON dès l'application évitent l'essentiel des expressions grok fragiles."],
 ["Monter la pile Elastic en Docker, sécurité activée", "Collecter les journaux des conteneurs et les transformer", "Chercher et visualiser avec KQL et Kibana"],
 [("La pile en Docker", DK, """services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.15.2
    environment: { discovery.type: single-node, ELASTIC_PASSWORD: "${ELASTIC_PASSWORD}", xpack.security.enabled: "true", ES_JAVA_OPTS: "-Xms1g -Xmx1g" }
    volumes: [ "es-data:/usr/share/elasticsearch/data" ]
  kibana:
    image: docker.elastic.co/kibana/kibana:8.15.2
    environment: { ELASTICSEARCH_HOSTS: "https://elasticsearch:9200", ELASTICSEARCH_USERNAME: kibana_system, ELASTICSEARCH_PASSWORD: "${KIBANA_PASSWORD}" }
    ports: [ "5601:5601" ]
  filebeat:
    image: docker.elastic.co/beats/filebeat:8.15.2
    user: root
    volumes: [ "./filebeat.yml:/usr/share/filebeat/filebeat.yml:ro", "/var/lib/docker/containers:/var/lib/docker/containers:ro", "/var/run/docker.sock:/var/run/docker.sock:ro" ]
volumes: { es-data: {} }
# le socket Docker est monté en lecture seule, pour ce seul conteneur de collecte, dans un labo"""),
  ("Collecter et transformer", "Filebeat lit les journaux des conteneurs, décode le JSON et ajoute les métadonnées Docker ; Logstash intervient pour les formats hérités (grok), l'enrichissement ou le masquage de données personnelles.", """# filebeat.yml
filebeat.inputs:
  - type: filestream
    id: conteneurs
    paths: [ /var/lib/docker/containers/*/*.log ]
    parsers: [ { container: { stream: all } }, { ndjson: { target: "", overwrite_keys: true } } ]
processors: [ { add_docker_metadata: ~ } ]
output.elasticsearch: { hosts: ["https://elasticsearch:9200"], username: filebeat_writer, password: "${FILEBEAT_PASSWORD}", ssl.certificate_authorities: ["/certs/ca.crt"] }
# logstash (format hérité) : analyse, date, masquage
filter {
  grok { match => { "message" => "%{TIMESTAMP_ISO8601:horodatage} %{LOGLEVEL:niveau} %{GREEDYDATA:texte}" } }
  date { match => [ "horodatage", "ISO8601" ] }
  mutate { gsub => [ "texte", "[0-9]{16}", "[carte masquée]" ] }
}"""),
  ("Explorer avec Kibana", "Dans Discover, KQL filtre par champ et par texte ; Lens construit des visualisations sans code ; un tableau de bord Kibana réunit les vues d'un service. Une recherche enregistrée devient une règle d'alerte.", """service.name : "incidents" and log.level : "ERROR"
http.response.status_code >= 500 and not url.path : "/actuator/*"
message : "timeout" and trace.id : *
event.duration > 2000000000                 # plus de deux secondes (nanosecondes)""")],
 [("Les journaux arrivent dans Elasticsearch mais on ne peut pas filtrer par niveau : tout est dans le champ message. Pourquoi ?", "Les journaux ne sont pas structurés, ou le JSON n'est pas décodé à la collecte. On fait écrire l'application en JSON (niveau, service, traceId) et on active le décodage ndjson dans Filebeat, au lieu d'empiler des expressions grok."),
  ("Question d'entretien : à quoi sert Logstash si Filebeat envoie directement à Elasticsearch ?", "À transformer ce que Filebeat et les ingest pipelines ne font pas bien : formats hérités complexes, enrichissements, routage vers plusieurs destinations, tampon de charge. Sans ces besoins, Filebeat et un ingest pipeline suffisent.")],
 ("Journaux de CrisisShield dans Elastic", ["Pile Elastic en Compose avec sécurité et comptes dédiés (collecte, lecture).", "Journaux JSON de CrisisShield collectés par Filebeat ; un format hérité traité par Logstash avec masquage.", "Tableau de bord Kibana du service et une règle d'alerte sur les erreurs."],
  "Attendu : filtrer par service, niveau et traceId fonctionne sans grok pour les journaux JSON ; aucune donnée de carte n'apparaît en clair ; le compte de collecte ne peut qu'écrire dans ses index.")),

ch("Elasticsearch en production", 's',
 ["Un shard de 10 à 50 Go, pas des milliers de petits : les data streams et le cycle de vie (ILM) basculent sur un nouvel index par taille ou par âge.", "Un mapping explicite évite l'explosion du nombre de champs et les types devinés à tort ; keyword pour filtrer, text pour chercher.", "Sécurité (TLS, rôles, clés d'API), instantanés vers un stockage objet, et surveillance de la santé du cluster."],
 ["Configurer data streams et cycle de vie des index", "Écrire des mappings sûrs et maîtriser le nombre de champs", "Sécuriser, sauvegarder et surveiller le cluster"],
 [("Data streams et cycle de vie", "Les journaux vont dans un data stream ; la politique ILM crée un nouvel index à 50 Go ou un jour, déplace les anciens vers des nœuds moins chers, puis les supprime à trente jours.", """PUT _ilm/policy/journaux-30j
{ "policy": { "phases": {
  "hot":    { "actions": { "rollover": { "max_primary_shard_size": "50gb", "max_age": "1d" } } },
  "warm":   { "min_age": "3d",  "actions": { "shrink": { "number_of_shards": 1 }, "forcemerge": { "max_num_segments": 1 } } },
  "delete": { "min_age": "30d", "actions": { "delete": {} } } } } }
PUT _index_template/journaux
{ "index_patterns": ["logs-crisis-*"], "data_stream": {},
  "template": { "settings": { "index.lifecycle.name": "journaux-30j", "number_of_shards": 1 } } }"""),
  ("Des mappings sans explosion", "Avec le mapping dynamique, chaque clé inconnue d'un JSON devient un champ : des données utilisateur arbitraires peuvent créer des milliers de champs et ralentir tout le cluster. On déclare les champs connus, on refuse ou on ignore le reste.", """PUT _index_template/journaux
{ "index_patterns": ["logs-crisis-*"], "data_stream": {},
  "template": {
    "settings": { "index.mapping.total_fields.limit": 500 },
    "mappings": { "dynamic": "false",
      "properties": {
        "@timestamp": { "type": "date" }, "service.name": { "type": "keyword" }, "log.level": { "type": "keyword" },
        "trace.id": { "type": "keyword" }, "message": { "type": "text" },
        "http": { "properties": { "response": { "properties": { "status_code": { "type": "short" } } } } } } } } }
# dynamic: false → les champs inconnus restent dans _source mais ne sont pas indexés"""),
  ("Sécurité, sauvegardes, santé", "Chaque outil a son compte ou sa clé d'API avec le moindre privilège ; les instantanés partent chaque nuit vers S3 et se restaurent en test ; on surveille l'état du cluster, les shards non attribués et la pression mémoire. OpenSearch suit les mêmes principes.", """POST _security/api_key { "name": "filebeat-crise", "role_descriptors": { "ecriture": { "index": [ { "names": ["logs-crisis-*"], "privileges": ["create_doc", "auto_configure"] } ] } } }
PUT _snapshot/s3-nuit { "type": "s3", "settings": { "bucket": "crisis-es-snapshots" } }
PUT _slm/policy/nuit { "schedule": "0 30 1 * * ?", "name": "<nuit-{now/d}>", "repository": "s3-nuit", "retention": { "expire_after": "30d" } }
GET _cluster/health            # green / yellow / red
GET _cat/shards?v&h=index,shard,prirep,state,unassigned.reason&s=state""")],
 [("Le cluster passe en jaune puis en rouge après l'ajout de journaux d'un nouveau service qui envoie des charges utiles JSON variables. Hypothèse ?", "Une explosion de mapping : chaque clé nouvelle crée un champ, la limite est atteinte ou la mémoire du nœud maître sature. On passe le mapping en dynamic false ou strict, on déclare les champs utiles, et on limite total_fields."),
  ("Question d'entretien : combien de shards pour un index ?", "Assez pour que chacun reste entre 10 et 50 Go ; trop de petits shards coûtent en mémoire et en gestion. Avec les data streams et le rollover par taille, on ne choisit plus au jugé : le cycle de vie crée un nouvel index quand le précédent est plein.")],
 ("Cluster Elastic prêt pour la production", ["Data stream des journaux avec politique ILM (rollover, warm, suppression à 30 jours).", "Mapping explicite avec dynamic false ; envoyer un journal aux champs inattendus et vérifier le comportement.", "Clés d'API au moindre privilège, instantanés nocturnes vers MinIO, restauration testée, alerte sur l'état du cluster."],
  "Attendu : le rollover se déclenche à la taille configurée ; le journal aux clés inattendues est stocké sans créer de champ ; la restauration d'un instantané fonctionne sur un cluster vide ; l'état rouge déclenche une alerte.")),

ch("Journaux avec Loki, et le collecteur OpenTelemetry", 's',
 ["Loki n'indexe que les labels (service, niveau, espace de noms) et stocke le texte compressé sur objet : moins cher qu'Elasticsearch, moins puissant en recherche plein texte.", "LogQL filtre par labels, puis par texte ou JSON, et calcule des métriques à partir des journaux.", "Le collecteur OpenTelemetry reçoit journaux, métriques et traces, les transforme (masquage, lots) et les envoie vers chaque destination."],
 ["Collecter vers Loki avec des labels bornés", "Écrire des requêtes LogQL et des alertes sur journaux", "Router tous les signaux avec le collecteur OpenTelemetry"],
 [("Loki : des labels, pas un index plein texte", "Chaque combinaison de labels crée un flux : les labels restent peu nombreux et bornés ; le reste se filtre à la requête. Grafana Alloy ou Promtail collectent les journaux des conteneurs.", """# requêtes LogQL
{service="incidents", niveau="error"}                                          # un flux
{service="incidents"} |= "timeout" | json | duree_ms > 2000                     # filtre texte puis JSON
sum by (service) (rate({namespace="crise"} |= "ERROR" [5m]))                    # métrique issue des journaux
{service="incidents"} | json | line_format "{{.traceId}} {{.message}}"
# à éviter : un label par requête (request_id) → des millions de flux"""),
  ("ELK ou Loki ?", "", T([
    ("Recherche plein texte", "excellente (index inversé)", "par filtre à la lecture, plus lente"),
    ("Coût de stockage", "élevé (index)", "faible (objet compressé)"),
    ("Exploitation", "cluster à dimensionner, shards, ILM", "simple, stockage objet"),
    ("Cas d'usage", "sécurité (SIEM), analyses riches, recherches libres", "journaux d'exploitation liés aux métriques et traces"),
    ("Écosystème", "Kibana, Elastic APM, Elastic Security", "Grafana, Tempo, Mimir")], ("Critère", "ELK / OpenSearch", "Loki"))),
  ("Le collecteur OpenTelemetry", "Un seul agent par nœud ou par service reçoit tout en OTLP, limite sa mémoire, groupe en lots, retire les attributs sensibles et exporte vers Prometheus, Loki, Elasticsearch ou Tempo : changer de destination ne touche pas les applications.", """receivers:
  otlp: { protocols: { grpc: {}, http: {} } }
  filelog: { include: [ /var/log/pods/*/*/*.log ], operators: [ { type: container } ] }
processors:
  memory_limiter: { check_interval: 1s, limit_percentage: 80 }
  attributes/pii: { actions: [ { key: user.email, action: delete }, { key: http.request.header.authorization, action: delete } ] }
  batch: {}
exporters:
  prometheusremotewrite: { endpoint: http://mimir:9009/api/v1/push }
  otlphttp/loki: { endpoint: http://loki:3100/otlp }
  otlp/tempo: { endpoint: tempo:4317, tls: { insecure: true } }
service:
  pipelines:
    metrics: { receivers: [otlp], processors: [memory_limiter, batch], exporters: [prometheusremotewrite] }
    logs:    { receivers: [otlp, filelog], processors: [memory_limiter, attributes/pii, batch], exporters: [otlphttp/loki] }
    traces:  { receivers: [otlp], processors: [memory_limiter, attributes/pii, batch], exporters: [otlp/tempo] }""")],
 [("Loki devient lent et la facture de stockage explose après l'ajout d'un label request_id. Pourquoi ?", "Chaque valeur crée un flux : des millions de flux minuscules, un index énorme et des requêtes lentes. On retire le label, on garde request_id dans le texte ou le JSON, et on le filtre à la requête avec | json | request_id=\"…\"."),
  ("Question d'entretien : pourquoi un collecteur OpenTelemetry plutôt que l'envoi direct ?", "Il découple les applications des outils : on change de destination, on masque des données sensibles, on groupe et on limite la mémoire en un seul endroit ; les applications ne parlent qu'OTLP.")],
 ("Journaux et signaux par le collecteur", ["Grafana Alloy vers Loki avec trois labels bornés ; requêtes LogQL et une alerte sur le taux d'erreurs des journaux.", "Collecteur OpenTelemetry : journaux, métriques et traces de CrisisShield, suppression des en-têtes d'autorisation.", "Basculer l'export des journaux de Loki vers Elasticsearch sans toucher aux applications."],
  "Attendu : moins de cinquante flux Loki pour tout CrisisShield ; aucun en-tête Authorization dans les journaux stockés ; la bascule vers Elasticsearch ne demande qu'une modification du collecteur.")),

ch("Traces et APM", 's',
 ["Une trace montre le chemin et la durée d'une requête à travers les services ; l'APM y ajoute erreurs, dépendances et profils par service.", "Tout garder coûte cher : l'échantillonnage en tête garde un pourcentage, l'échantillonnage en queue garde les traces utiles (erreurs, lenteurs).", "Les exemplars relient un point de métrique à une trace ; l'identifiant de trace relie journaux et traces."],
 ["Monter Tempo, Jaeger ou Elastic APM", "Configurer un échantillonnage qui garde l'essentiel", "Relier métriques, journaux et traces dans Grafana"],
 [("Tempo, Jaeger, Elastic APM", "Tempo stocke les traces sur objet à faible coût et s'intègre à Grafana ; Jaeger offre sa propre interface ; Elastic APM s'intègre à Kibana. L'instrumentation reste OpenTelemetry, quelle que soit la destination.", """tempo:
  image: grafana/tempo:2.6.0
  command: [ "-config.file=/etc/tempo.yaml" ]
  volumes: [ "./tempo.yaml:/etc/tempo.yaml:ro" ]
incidents:
  environment:
    JAVA_TOOL_OPTIONS: "-javaagent:/otel/opentelemetry-javaagent.jar"
    OTEL_SERVICE_NAME: incidents
    OTEL_EXPORTER_OTLP_ENDPOINT: http://otel-collector:4317
    OTEL_TRACES_SAMPLER: parentbased_always_on           # la décision finale est prise au collecteur (queue)"""),
  ("Échantillonner sans perdre l'essentiel", "L'échantillonnage en queue attend la fin de la trace pour décider : on garde toutes les erreurs, toutes les traces lentes, et un petit pourcentage du reste pour la référence.", """processors:
  tail_sampling:
    decision_wait: 10s
    policies:
      - { name: erreurs, type: status_code, status_code: { status_codes: [ERROR] } }
      - { name: lentes,  type: latency, latency: { threshold_ms: 1000 } }
      - { name: echantillon, type: probabilistic, probabilistic: { sampling_percentage: 5 } }
# attention : toutes les parties d'une trace doivent arriver au même collecteur (répartition par traceId)"""),
  ("Relier les trois signaux", "Un exemplar attache un identifiant de trace à un point d'histogramme : du pic de latence on saute à une trace lente réelle. Dans Grafana, un champ dérivé transforme le traceId d'un journal Loki en lien vers Tempo, et Tempo renvoie aux journaux de la trace.", """# Micrometer : exemplars exposés avec l'histogramme (Prometheus avec --enable-feature=exemplar-storage)
management.prometheus.metrics.export.enabled: true
# Grafana, source Loki : champ dérivé vers Tempo
derivedFields: [ { name: traceId, matcherRegex: '"traceId":"(\\w+)"', url: '$${__value.raw}', datasourceUid: tempo } ]""")],
 [("La facture de stockage des traces a triplé et 99 % des traces conservées sont des requêtes rapides sans erreur. Que changer ?", "Passer à un échantillonnage en queue : garder toutes les erreurs et les traces lentes, et seulement quelques pourcents des requêtes normales ; les métriques gardent la vue complète du trafic."),
  ("Question d'entretien : échantillonnage en tête ou en queue ?", "En tête, la décision est prise au début, simple et bon marché, mais on perd des erreurs au hasard ; en queue, on décide une fois la trace complète, ce qui garde les traces utiles au prix d'un collecteur qui les met en attente.")],
 ("Traces utiles et reliées", ["Tempo et collecteur OpenTelemetry en Compose ; traces de la passerelle jusqu'aux notifications.", "Échantillonnage en queue : erreurs, lenteurs au-delà d'une seconde, 5 % du reste.", "Exemplars sur la latence et liens journaux vers traces dans Grafana."],
  "Attendu : toutes les requêtes en erreur ont leur trace, les requêtes normales sont échantillonnées ; du pic de p99 on ouvre une trace lente en un clic ; le volume stocké baisse de plus de 80 %.")),

ch("Sondes, bases de données, middleware et SLO outillés", 's',
 ["Une sonde externe (blackbox) vérifie ce que voit l'utilisateur : disponibilité, temps de réponse, validité du certificat.", "Chaque composant a ses indicateurs clés : connexions et réplication pour PostgreSQL, retard des consommateurs pour Kafka, mémoire et pauses pour la JVM.", "Les SLO se déclarent dans un fichier ; un générateur (Sloth, Pyrra) produit règles d'enregistrement et alertes de burn rate."],
 ["Sonder un service de l'extérieur, certificat compris", "Superviser PostgreSQL, Kafka et la JVM avec les bons indicateurs", "Générer SLO et alertes à partir d'une déclaration"],
 [("Sonder de l'extérieur", "Le blackbox exporter interroge les URL publiques comme un navigateur ; Prometheus lui passe la cible par réécriture de labels. On alerte sur l'échec de la sonde et sur l'expiration prochaine du certificat.", """# prometheus.yml
- job_name: sondes-http
  metrics_path: /probe
  params: { module: [http_2xx] }
  static_configs: [ { targets: ["https://crisis.fr", "https://api.crisis.fr/actuator/health"] } ]
  relabel_configs:
    - { source_labels: [__address__], target_label: __param_target }
    - { source_labels: [__param_target], target_label: instance }
    - { target_label: __address__, replacement: "blackbox:9115" }
# alertes
probe_success == 0                                               # le site ne répond plus (pendant 2 min)
probe_ssl_earliest_cert_expiry - time() < 21 * 86400             # certificat qui expire dans moins de 21 jours"""),
  ("Bases de données et middleware", "", T([
    ("PostgreSQL", "pg_stat_activity_count, pg_replication_lag, pg_stat_database_deadlocks", "connexions proches du maximum, retard de réplique, verrous mortels"),
    ("Kafka", "kafka_consumergroup_lag, kafka_topic_partition_under_replicated_partition", "consommateur bloqué, partitions non répliquées"),
    ("JVM", "jvm_memory_used_bytes{area=\"heap\"}, jvm_gc_pause_seconds, jvm_threads_states_threads", "mémoire saturée, pauses longues, fils bloqués"),
    ("Pool de connexions", "hikaricp_connections_pending, hikaricp_connections_timeout_total", "requêtes qui attendent une connexion")], ("Composant", "Métriques clés", "Ce qu'elles révèlent"))),
  ("Des SLO générés", "On déclare l'objectif et la mesure ; Sloth produit les règles d'enregistrement sur plusieurs fenêtres et les alertes de burn rate rapide et lent, identiques pour tous les services.", """# slo-incidents.yaml (Sloth)
version: prometheus/v1
service: incidents
slos:
  - name: requetes-reussies
    objective: 99.9
    sli:
      events:
        error_query: sum(rate(http_server_requests_seconds_count{service="incidents",status=~"5.."}[{{.window}}]))
        total_query: sum(rate(http_server_requests_seconds_count{service="incidents"}[{{.window}}]))
    alerting: { name: IncidentsSLO, page_alert: { labels: { severity: page } }, ticket_alert: { labels: { severity: ticket } } }
# docker run --rm -v "$PWD:/w" -w /w ghcr.io/slok/sloth generate -i slo-incidents.yaml -o regles-slo.yaml""")],
 [("Un consommateur Kafka est resté bloqué six heures sans aucune alerte. Qu'a-t-il manqué ?", "Une alerte sur le retard du groupe de consommateurs (kafka_consumergroup_lag qui croît, ou retard en temps), avec un seuil lié au besoin métier ; l'application était « up », seul le retard révélait le problème."),
  ("Question d'entretien : pourquoi une sonde externe si l'on a déjà les métriques internes ?", "Parce que les métriques internes ne voient pas ce qui se passe avant l'application : DNS, certificat, équilibreur de charge, réseau. La sonde mesure ce que vit l'utilisateur, et elle fonctionne même quand l'application ne publie plus rien.")],
 ("Sondes et composants de CrisisShield", ["Blackbox exporter sur les URL publiques ; alertes d'indisponibilité et d'expiration de certificat.", "Exporters PostgreSQL et Kafka ; tableau de bord et alertes sur connexions, réplication et retard des consommateurs.", "SLO de disponibilité et de latence déclarés avec Sloth ; règles générées en CI."],
  "Attendu : arrêter un consommateur fait monter le retard et déclenche l'alerte ; un certificat de test à 20 jours déclenche l'alerte d'expiration ; les règles de SLO générées passent promtool et sont identiques pour chaque service.")),

ch("Exploiter la supervision : surveiller le surveillant, code, sécurité, entretien", 'e',
 ["La supervision peut tomber en silence : une alerte toujours active (watchdog), relayée vers un service externe, prévient quand plus rien n'arrive.", "La supervision est du code testé en CI : configurations, règles, tableaux de bord et modèles d'index passent par une MR et des vérifications automatiques.", "Elle a ses risques : données personnelles dans les journaux, accès trop larges, coût qui dérive ; on les traite comme pour n'importe quel système de production."],
 ["Mettre en place la surveillance de la supervision", "Tester la supervision en CI", "Répondre aux questions d'entretien sur Prometheus, ELK et l'alerte"],
 [("Qui surveille le surveillant ?", "Une alerte Watchdog est toujours active ; Alertmanager l'envoie toutes les minutes à un service externe de battement de cœur, qui prévient l'astreinte par un autre canal s'il ne reçoit plus rien. On surveille aussi les échecs d'évaluation de règles et de notification.", """- alert: Watchdog
  expr: vector(1)
  labels: { severity: none }
  annotations: { summary: "Battement de cœur de la chaîne d'alerte" }
# Alertmanager : route dédiée vers le service externe (répétition chaque minute)
- matchers: [ 'alertname="Watchdog"' ]
  receiver: battement-externe
  repeat_interval: 1m
# méta-supervision
rate(prometheus_rule_evaluation_failures_total[5m]) > 0
rate(alertmanager_notifications_failed_total[5m]) > 0
elasticsearch_cluster_health_status{color="red"} == 1"""),
  ("La supervision comme code, testée", "Chaque MR de supervision passe les mêmes contrôles : syntaxe, tests unitaires de règles, configuration d'Alertmanager, qualité des tableaux de bord et modèles d'index validés sur un cluster de test.", """# .gitlab-ci.yml (extrait)
verifier-supervision:
  image: prom/prometheus:v2.54.1
  script:
    - promtool check config prometheus.yml
    - promtool check rules regles/*.yml
    - promtool test rules tests/*.yml
verifier-alertmanager:
  image: prom/alertmanager:v0.27.0
  script: [ amtool check-config alertmanager.yml ]
verifier-tableaux-de-bord:
  image: grafana/dashboard-linter:latest
  script: [ for f in dashboards/*.json; do dashboard-linter lint --strict "$f"; done ]"""),
  ("Trente questions d'entretien", "", """1 Monitoring ou observabilité ? Surveiller le connu, explorer l'imprévu. 2 Quatre signaux d'or ? Latence, trafic, erreurs, saturation. 3 RED et USE ? Requêtes : débit, erreurs, durée ; ressources : utilisation, saturation, erreurs. 4 Pourquoi Prometheus tire ? État des cibles, configuration centrale. 5 Types de métriques ? Compteur, jauge, histogramme, résumé. 6 Histogramme ou résumé ? Histogramme, agrégeable. 7 Cardinalité ? Nombre de séries ; labels bornés. 8 rate ou irate ? Lissé pour alerter, instantané pour zoomer. 9 sum puis rate ? Non : rate puis sum. 10 Quantile d'un service ? histogram_quantile sur sum by (le). 11 Règle d'enregistrement ? Précalculer une requête coûteuse. 12 Bonne alerte ? Symptôme, durée, gravité, runbook, propriétaire. 13 Alertmanager ? Regrouper, router, inhiber, mettre en silence. 14 Fatigue d'alerte ? Mesurer les pages, supprimer l'inutile. 15 Burn rate ? Vitesse de consommation du budget d'erreur. 16 Haute disponibilité Prometheus ? Paire + dédoublonnage. 17 Long terme ? remote_write vers Mimir, Thanos, VictoriaMetrics. 18 Fédération ? Remonter des agrégats, pas tout. 19 ServiceMonitor ? Déclaration de collecte avec l'application. 20 kube-state-metrics ? État des objets Kubernetes. 21 ELK ? Stocker et chercher, collecter, transformer, explorer. 22 Logstash utile quand ? Formats hérités, enrichissement, routage. 23 Taille de shard ? 10 à 50 Go, rollover par taille. 24 ILM ? Cycle de vie : hot, warm, suppression. 25 Explosion de mapping ? Champs dynamiques ; mapping explicite. 26 Loki ou ELK ? Coût et simplicité contre recherche plein texte. 27 Collecteur OpenTelemetry ? Découpler applications et outils. 28 Échantillonnage en queue ? Garder erreurs et lenteurs. 29 Exemplar ? Lien d'une métrique vers une trace. 30 Surveiller la supervision ? Watchdog et battement de cœur externe.""")],
 [("Pendant une panne de nuit, aucune alerte n'est arrivée : Prometheus était tombé une heure avant. Qu'est-ce qui l'aurait signalé ?", "Le Watchdog relayé à un service externe de battement de cœur : faute de signal, ce service aurait prévenu l'astreinte par un autre canal. Avec une paire de Prometheus, la collecte aurait aussi continué."),
  ("Question d'entretien : quelles données ne doivent jamais arriver dans la supervision ?", "Mots de passe, jetons, en-têtes d'autorisation, données de paiement, données personnelles inutiles : on les supprime à la source (journaux structurés sans ces champs) et dans le collecteur (processeur de masquage), et l'accès aux journaux se limite par rôle.")],
 ("Une supervision elle-même fiable", ["Watchdog relayé vers un service de battement de cœur en conteneur ; arrêter Prometheus et vérifier l'alerte par l'autre canal.", "Pipeline de CI de la supervision : promtool, amtool, lint des tableaux de bord, modèles d'index testés.", "Revue de sécurité et de coût : données sensibles, rôles, rétentions, séries et volumes par équipe."],
  "Attendu : l'arrêt de Prometheus est signalé en moins de trois minutes par le canal externe ; une règle cassée fait échouer la CI ; la revue produit une liste de trois actions datées (masquage, rôle, rétention).")),
]

d = sys.argv[1]
page('cours-16-monitoring.html', 'Monitoring — de zéro à expert : Prometheus, Grafana, ELK, Loki', "Treize chapitres pour superviser un système de bout en bout : quoi mesurer (signaux d'or, RED, USE), Prometheus et son modèle de données, PromQL, alertes et Alertmanager, tableaux de bord Grafana en code, Prometheus à l'échelle (cardinalité, haute disponibilité, Mimir, Thanos), Kubernetes, la pile ELK et Elasticsearch en production, Loki et le collecteur OpenTelemetry, traces et APM, sondes et SLO outillés, et la supervision de la supervision. Fil conducteur : CrisisShield, tout en Docker ; chaque chapitre a ses exercices corrigés et un travail pratique avec correction type.", "≈ 50 h de travail · prérequis : Docker, bases de Linux ; approfondit le niveau 6 du parcours DevOps.", MO, [('devops-06-observabilite.html', 'DevOps niveau 6'), ('cours-08-microservices.html', 'Microservices'), ('cours-15-data-platform-aws-talend.html', 'Data Platform')])
