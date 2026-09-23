import re, pathlib

out = pathlib.Path('/mnt/user-data/outputs')

def insert_before_niche(s, ch, niche_tech, block):
    key = f'Pour sortir du lot — {niche_tech}'
    i = s.index(key); j = s.rfind('<div class="niche">', 0, i)
    assert j > s.index(f'<span class="chapnum">Chapitre {ch}</span>')
    return s[:j] + block + s[j:]

# =====================================================================
# 37.7 — Sécurité applicative dans le code
# =====================================================================
APPSEC = r'''<h3>37.7 Sécurité applicative dans le code : OWASP Top 10 et les corrections Spring Boot<span class="badge tag-coeur">Par cœur</span></h3>
<p>Le pipeline détecte ; c'est le code qui protège. Pour chaque catégorie de l'OWASP Top 10 (2021, la révision 2025 garde la même logique), le motif vulnérable tel qu'on le voit en revue, la correction Spring Boot, et le test qui l'empêche de revenir.</p>
<div class="tablewrap"><table>
<tr><th>Catégorie</th><th>Motif vulnérable</th><th>Correction Spring Boot</th><th>Test</th></tr>
<tr><td>A01 Contrôle d'accès défaillant</td><td><code>GET /incidents/{id}</code> qui renvoie l'incident sans vérifier l'organisation de l'utilisateur (IDOR) ; rôles vérifiés côté front seulement</td><td><code>@PreAuthorize("@access.canRead(#id, authentication)")</code> avec vérification en base ; requêtes filtrées par organisation ; refus par défaut (<code>anyRequest().authenticated()</code>)</td><td>Test MockMvc : utilisateur de l'organisation B sur l'incident de A → 403 ou 404</td></tr>
<tr><td>A02 Défaillances cryptographiques</td><td>MD5/SHA-1 pour les mots de passe, AES en mode ECB, clés dans le code, TLS 1.0 accepté</td><td><code>Argon2PasswordEncoder</code> ou <code>BCryptPasswordEncoder</code> ; AES-GCM via Vault Transit ; clés hors du code ; TLS 1.2+ avec suites modernes</td><td>Test qui refuse un hash qui n'est pas Argon2/bcrypt ; scan TLS (testssl)</td></tr>
<tr><td>A03 Injection</td><td><code>"SELECT * FROM incidents WHERE zone='" + zone + "'"</code> ; JPQL concaténé ; commandes système avec entrée utilisateur ; LDAP</td><td>Paramètres nommés (<code>:zone</code>), Spring Data, <code>Criteria</code> ; jamais <code>Runtime.exec</code> avec une entrée ; validation stricte des entrées (<code>@Valid</code>, <code>@Pattern</code>)</td><td>Règle Semgrep (chapitre 37) ; test avec <code>' OR 1=1 --</code> qui doit renvoyer 400</td></tr>
<tr><td>A04 Conception non sécurisée</td><td>Récupération de mot de passe par question secrète ; pas de limite sur les tentatives ; logique métier contournable (prix côté client)</td><td>Modélisation des menaces (37.1) avant de coder ; règles métier côté serveur ; limitation de débit (Bucket4j) ; validation des invariants dans le domaine</td><td>Tests de règles métier avec valeurs manipulées ; test de limite de débit</td></tr>
<tr><td>A05 Mauvaise configuration</td><td>Actuator exposé sans authentification, <code>server.error.include-stacktrace=always</code>, CORS <code>*</code>, CSRF désactivé sur une application à session, en-têtes de sécurité absents</td><td>Actuator restreint (<code>management.endpoints.web.exposure.include</code> minimal, port séparé), erreurs génériques, CORS explicite, CSRF conservé pour les sessions, en-têtes via Spring Security (<code>headers()</code> : HSTS, CSP, frame options)</td><td>DAST ZAP en CI ; test des en-têtes ; test 401 sur <code>/actuator/env</code></td></tr>
<tr><td>A06 Composants vulnérables</td><td>Dépendances obsolètes, transitive vulnérable, Spring Boot en fin de support</td><td>Renovate, SCA bloquant, BOM à jour, suppression des dépendances inutiles</td><td>Dependency-Check / Trivy fs avec seuil</td></tr>
<tr><td>A07 Authentification défaillante</td><td>JWT non vérifié (audience, algorithme), sessions sans expiration, mots de passe faibles acceptés</td><td>Serveur de ressources OAuth2 avec <code>issuer-uri</code> et <code>audiences</code> (chapitre 41), politique de mots de passe, MFA via l'IdP, rotation des refresh tokens</td><td>Les dix tests négatifs du TP 41 (alg none, audience, expiré, IDOR…)</td></tr>
<tr><td>A08 Intégrité des logiciels et données</td><td>Désérialisation Java d'objets non fiables, plugins ou dépendances non vérifiés, pipeline sans signature</td><td>Jamais <code>ObjectInputStream</code> sur une entrée externe ; Jackson sans typage polymorphe par défaut ; signatures et SLSA (chapitre 40)</td><td>Règle SAST sur la désérialisation ; vérification Cosign à l'admission</td></tr>
<tr><td>A09 Journalisation et surveillance insuffisantes</td><td>Échecs d'authentification non journalisés, logs avec données personnelles ou secrets, pas d'alerte</td><td>Événements de sécurité structurés (chapitre 32), masquage, alertes sur taux d'échec de connexion et accès refusés (chapitre 35)</td><td>Test que l'échec de connexion produit un log sans le mot de passe ; alerte testée</td></tr>
<tr><td>A10 Falsification de requête côté serveur (SSRF)</td><td>Endpoint qui télécharge une URL fournie par l'utilisateur (webhook, import, aperçu)</td><td>Liste d'autorisation de domaines, résolution DNS vérifiée, blocage des adresses privées et de l'IMDS (169.254.169.254), pas de redirections suivies, egress réseau restreint (NetworkPolicy)</td><td>Test avec <code>http://169.254.169.254/</code> et <code>http://localhost</code> → refusés</td></tr>
</table></div>
<pre><code>// Trois corrections qui reviennent dans toutes les revues Java
// 1. Contrôle d'accès par objet, en base, pas dans le contrôleur
@Component("access")
public class AccessPolicy {
    public boolean canRead(String incidentId, Authentication auth) {
        String org = ((Jwt) auth.getPrincipal()).getClaimAsString("org");
        return incidents.existsByIdAndOrganisation(incidentId, org);
    }
}
// 2. Validation d'entrée déclarative : le contrôleur refuse avant le métier
public record CreateIncident(@NotBlank @Size(max = 200) String title,
                             @Pattern(regexp = "^[A-Za-z-]{2,40}$") String zone,
                             @NotNull Priority priority) {}
// 3. En-têtes de sécurité et session
http.headers(h -> h
    .httpStrictTransportSecurity(hsts -> hsts.includeSubDomains(true).maxAgeInSeconds(31536000))
    .contentSecurityPolicy(csp -> csp.policyDirectives("default-src 'self'; frame-ancestors 'none'"))
    .frameOptions(f -> f.deny()));</code></pre>
<p><strong>Checklist de revue sécurité</strong> (à mettre dans le template de merge request) : autorisation vérifiée par objet ; entrées validées et bornées ; requêtes paramétrées ; pas de secret, d'URL de prod ni de donnée personnelle dans le code, les tests ou les logs ; erreurs génériques vers le client ; nouvelle dépendance justifiée et scannée ; nouvel endpoint couvert par un test négatif (401, 403, 400) ; appel sortant avec timeout et liste d'autorisation. Huit lignes, deux minutes par revue, la majorité des failles évitée.</p>
'''
APPSEC_EXO = r'''<div class="exo"><span class="tag">Exercice 37.3</span>
<p>Ce contrôleur est-il sûr ? <code>@GetMapping("/incidents/{id}") public Incident get(@PathVariable String id, @RequestParam(defaultValue = "false") boolean full) { return repo.findById(id).orElseThrow(); }</code></p>
<details><summary>Corrigé</summary><div class="sol">Non : A01, tout utilisateur authentifié lit n'importe quel incident (IDOR) ; il faut filtrer par organisation ou vérifier une politique d'accès par objet, et renvoyer 404 (pas 403, pour ne pas confirmer l'existence). Secondairement : <code>full</code> laisse penser qu'un mode renvoie plus de données, à contrôler par rôle ; et l'entité JPA renvoyée directement expose des champs internes (préférer un DTO).</div></details></div>

'''
APPSEC_TP = '<li>Sécurité dans le code : passe CrisisShield au crible des dix catégories de la section 37.7, corrige au moins cinq motifs réels trouvés (IDOR, validation, en-têtes, Actuator, SSRF sur l\'import), ajoute le test négatif correspondant à chacun, et mets la checklist de revue dans le template de merge request.</li>'

# =====================================================================
# 41.9 — PKI en pratique
# =====================================================================
PKI = r'''<h3>41.9 PKI en pratique : certificats, validation, révocation, exploitation<span class="badge tag-coeur">Par cœur</span></h3>
<p>Ce que 41.2 décrit en architecture, ici en gestes quotidiens. C'est ta spécialité : cette section doit être récitable.</p>
<h4>Anatomie d'un certificat X.509</h4>
<div class="tablewrap"><table>
<tr><th>Champ</th><th>Rôle</th><th>Piège courant</th></tr>
<tr><td>Subject et Subject Alternative Names</td><td>Qui est certifié : les SAN font foi (le CN est ignoré par les navigateurs modernes)</td><td>Certificat sans le SAN utilisé → « hostname mismatch »</td></tr>
<tr><td>Issuer</td><td>Qui a signé : doit correspondre au Subject de l'autorité suivante dans la chaîne</td><td>Chaîne incomplète : le serveur n'envoie pas l'intermédiaire</td></tr>
<tr><td>Validité (notBefore, notAfter)</td><td>Fenêtre d'usage ; les certificats publics sont limités à 398 jours, tendance vers 47 jours d'ici 2029</td><td>Expiration non surveillée ; horloge de la machine fausse</td></tr>
<tr><td>Key Usage et Extended Key Usage</td><td>Ce que la clé a le droit de faire : signature, chiffrement, serverAuth, clientAuth, codeSigning</td><td>Certificat serveur utilisé comme client (mTLS) sans clientAuth → refusé</td></tr>
<tr><td>Basic Constraints (CA:TRUE, pathlen)</td><td>Le certificat peut-il signer d'autres certificats, et jusqu'à quelle profondeur</td><td>Intermédiaire sans CA:TRUE ; pathlen trop court</td></tr>
<tr><td>CRL Distribution Points, AIA (OCSP)</td><td>Où vérifier la révocation et récupérer l'émetteur</td><td>URL interne inaccessible depuis les clients → validation lente ou échec</td></tr>
<tr><td>Algorithme et taille de clé</td><td>RSA 2048 minimum (3072 recommandé), ECDSA P-256 (plus rapide, clés courtes), Ed25519 hors navigateurs</td><td>SHA-1 refusé partout ; RSA 1024 interdit</td></tr>
</table></div>
<pre><code># Lire, vérifier, convertir : le kit openssl
openssl x509 -in srv.crt -noout -text                      # tout le certificat
openssl x509 -in srv.crt -noout -subject -issuer -dates -ext subjectAltName
openssl s_client -connect api.example:443 -servername api.example -showcerts &lt;/dev/null   # chaîne envoyée par le serveur (SNI !)
openssl verify -CAfile chain.pem srv.crt                    # validation locale de la chaîne
openssl x509 -in srv.crt -noout -ocsp_uri ; openssl ocsp -issuer int.pem -cert srv.crt -url URL   # révocation
openssl req -in srv.csr -noout -text                        # relire une demande avant de la signer
openssl pkey -in srv.key -noout -check                      # la clé privée est-elle valide
openssl x509 -noout -modulus -in srv.crt | openssl md5 ; openssl rsa -noout -modulus -in srv.key | openssl md5   # clé et certificat correspondent ?
openssl pkcs12 -export -in srv.crt -inkey srv.key -certfile chain.pem -out srv.p12   # PEM → PKCS#12 (Java, Windows)
openssl pkcs12 -in srv.p12 -nokeys -out srv.pem             # PKCS#12 → PEM
openssl x509 -in srv.der -inform DER -out srv.pem           # DER → PEM
# Java : magasins de clés et de confiance
keytool -list -v -keystore truststore.p12 -storetype PKCS12
keytool -importcert -alias racine-interne -file root.crt -keystore truststore.p12 -storetype PKCS12
keytool -importkeystore -srckeystore srv.p12 -srcstoretype PKCS12 -destkeystore keystore.jks
# Spring Boot : server.ssl.bundle / spring.ssl.bundle.pem.* pour charger PEM directement, sans JKS (Boot 3.1+)</code></pre>
<h4>Validation et révocation</h4>
<ul>
<li><strong>Validation par le client</strong> : chaîne jusqu'à une racine de confiance du magasin (système, navigateur, JVM <code>cacerts</code>, ou magasin applicatif), dates, nom (SAN), usages, révocation. Le serveur doit envoyer le certificat feuille <em>et</em> les intermédiaires ; jamais la racine (elle est déjà chez le client).</li>
<li><strong>Révocation</strong> : CRL (liste signée, téléchargée, lourde), OCSP (requête par certificat, fuite de vie privée, dépendance), <strong>OCSP stapling</strong> (le serveur joint la réponse OCSP : à activer), et la solution moderne : <strong>certificats courts</strong> (heures ou jours) renouvelés automatiquement, où la révocation devient inutile. C'est le choix du mesh, de Vault PKI et de cert-manager en interne.</li>
<li><strong>Épinglage</strong> (pinning) : à éviter sauf cas précis (mobile vers sa propre API) car il casse la rotation ; préférer la validation de la chaîne et Certificate Transparency pour les certificats publics.</li>
</ul>
<h4>Erreurs fréquentes et leur cause</h4>
<div class="tablewrap"><table>
<tr><th>Message</th><th>Cause</th><th>Remède</th></tr>
<tr><td><code>unable to get local issuer certificate</code></td><td>Intermédiaire manquant côté serveur, ou racine absente du magasin client</td><td>Envoyer la chaîne complète ; ajouter la racine interne au truststore (trust-manager en Kubernetes, image de base)</td></tr>
<tr><td><code>certificate has expired</code></td><td>Expiration, ou horloge de la machine fausse</td><td>Renouveler ; NTP ; alerte à 30 et 14 jours</td></tr>
<tr><td><code>hostname mismatch</code>, <code>No subject alternative DNS name matching</code></td><td>Le SAN ne contient pas le nom appelé (IP, nom court de service)</td><td>Émettre avec tous les noms (<code>api</code>, <code>api.crisisshield.svc</code>, <code>api.crisisshield.svc.cluster.local</code>)</td></tr>
<tr><td><code>PKIX path building failed</code> (Java)</td><td>La JVM ne connaît pas la racine ; magasin <code>cacerts</code> non mis à jour dans l'image</td><td>Truststore applicatif ou <code>cacerts</code> enrichi au build ; jamais désactiver la vérification</td></tr>
<tr><td><code>handshake failure</code></td><td>Suites ou versions TLS incompatibles, certificat client exigé et absent (mTLS), EKU incorrect</td><td><code>openssl s_client</code> avec <code>-tls1_2</code> / <code>-cert</code> pour isoler</td></tr>
<tr><td>Ça marche avec curl, pas avec l'application</td><td>Magasins de confiance différents (système contre JVM), SNI absent, proxy d'entreprise qui réécrit les certificats</td><td>Comparer les magasins, forcer le <code>servername</code>, ajouter la racine du proxy</td></tr>
<tr><td>Le certificat est renouvelé mais le service sert encore l'ancien</td><td>Application qui ne recharge pas le fichier</td><td>Redémarrage ou rechargement (Spring SSL bundles rechargeables, <code>reloader</code> Kubernetes, hook cert-manager)</td></tr>
</table></div>
<h4>Exploiter une PKI</h4>
<ul>
<li><strong>Inventaire</strong> : tout certificat est connu (émetteur, propriétaire, expiration, où il est déployé) ; sans inventaire, l'expiration est un incident garanti. cert-manager et Vault donnent l'inventaire interne ; pour l'externe, scan et Certificate Transparency.</li>
<li><strong>Automatisation</strong> : ACME (Let's Encrypt, ou une CA interne qui parle ACME comme step-ca ou Vault), cert-manager, renouvellement bien avant expiration, rechargement sans coupure.</li>
<li><strong>Cérémonie de clés</strong> pour la racine : machine hors ligne, plusieurs témoins, procédure écrite, clé dans un HSM ou chiffrée et partagée (Shamir), certificat racine publié, journal signé ; la racine ne signe que des intermédiaires, une ou deux fois par décennie.</li>
<li><strong>HSM et KMS</strong> : clés critiques (racine, signature de code, signature de jetons) dans un HSM (PKCS#11, certification FIPS 140-3 ou Critères Communs) ou un KMS cloud ; la clé ne sort jamais, les opérations sont journalisées ; les exigences RGS, eIDAS, PCI l'imposent.</li>
<li><strong>Signature de code et d'artefacts</strong> : la PKI signe aussi les jars, images, paquets (chapitre 40) et les jetons (JWT, chapitre 41.5) ; la rotation des clés de signature de l'IdP se fait par JWKS avec plusieurs clés actives.</li>
<li><strong>Cadres</strong> : RGS en France pour l'administration, eIDAS pour la signature électronique, les Baseline Requirements du CA/Browser Forum pour les certificats publics, le durcissement TLS de l'ANSSI comme référence de configuration.</li>
</ul>
'''
PKI_EXO = r'''<div class="exo"><span class="tag">Exercice 41.5</span>
<p>Un client Java refuse de se connecter à ton API avec <code>PKIX path building failed</code>, alors que curl depuis la même machine fonctionne. Quatre hypothèses, dans l'ordre où tu les vérifies.</p>
<details><summary>Corrigé</summary><div class="sol">1) La JVM utilise son propre <code>cacerts</code> qui ne contient pas la racine interne (curl utilise le magasin système) : <code>keytool -list</code> et ajouter la racine, ou un truststore applicatif. 2) Le serveur n'envoie pas l'intermédiaire et curl a la chaîne en cache ou dans son magasin : <code>openssl s_client -showcerts</code>. 3) Un proxy d'entreprise réécrit les certificats et sa racine n'est que dans le magasin système. 4) Version de Java ancienne qui refuse l'algorithme ou la taille de clé. Jamais de <code>TrustManager</code> qui accepte tout « pour tester ».</div></details></div>

'''
PKI_TP = '<li>PKI au quotidien : sur ta PKI du TP 41, émets un certificat de service avec tous les SAN nécessaires, vérifie la chaîne avec <code>openssl verify</code>, active l\'OCSP stapling sur l\'Ingress, convertis en PKCS#12 pour un client Java et charge-le par SSL bundle Spring ; reproduis et corrige les cinq erreurs du tableau 41.9 ; construis l\'inventaire des certificats du cluster (cert-manager + un scan des endpoints) avec une alerte à 30 et 14 jours ; rédige et exécute la cérémonie de la racine hors ligne avec un journal signé.</li>'

# =====================================================================
# 54.8 — Application LLM en production
# =====================================================================
LLM = r'''<h3>54.8 Construire une application LLM en production : RAG, agents, évaluation, coût<span class="badge tag-important">Important</span></h3>
<pre><code>Utilisateur ─► Application (Spring Boot / Quarkus + LangChain4j ou Spring AI)
                 │  1. garde-fous d'entrée (taille, injection, données sensibles masquées)
                 │  2. récupération : recherche hybride (vecteurs pgvector + BM25) filtrée par droits, reranking
                 │  3. prompt = instructions + contexte récupéré + question ; format de sortie contraint (JSON schema)
                 ▼
             Passerelle LLM (auth, quotas, journal, coût, cache, routage petit/gros modèle)
                 ▼
             Fournisseur (API Claude, ou modèle auto-hébergé vLLM)
                 ▼
             Validation de sortie (schéma, citations présentes, filtre) ─► réponse + sources ─► trace OTel, eval hors ligne</code></pre>
<ul>
<li><strong>RAG</strong> : découpage des documents par sections sémantiques (300 à 800 tokens, chevauchement), métadonnées (source, date, droits d'accès), embeddings versionnés, recherche hybride et reranking ; le contrôle d'accès s'applique à la récupération (un utilisateur ne récupère que ce qu'il a le droit de lire) ; fraîcheur par réindexation événementielle ; toujours renvoyer les sources.</li>
<li><strong>Agents</strong> : outils déclarés avec schéma strict et moindre privilège, boucle bornée (nombre d'étapes, budget de tokens), confirmation humaine pour les actions d'écriture ou externes, journalisation de chaque appel d'outil, isolation d'exécution ; patrons : routeur, planificateur-exécutant, revue par un second modèle. MCP pour standardiser les outils, avec authentification et audit comme pour une API.</li>
<li><strong>Sorties structurées</strong> : demander du JSON conforme à un schéma et le valider ; retenter avec l'erreur ; ne jamais exécuter ou afficher une sortie sans validation (LLM05).</li>
<li><strong>Évaluation</strong> : un jeu de cas versionné (questions, réponses attendues, sources attendues, pièges, injections) exécuté en CI à chaque changement de prompt, de modèle ou d'index ; métriques de RAG (pertinence des passages, fidélité de la réponse aux sources, exactitude), juge LLM calibré sur un échantillon relu par des humains ; seuil bloquant.</li>
<li><strong>Observabilité et coût</strong> : traces OpenTelemetry par requête (récupération, prompt, appel, validation) avec tokens et coût, tableau de bord par fonctionnalité et par tenant, cache sémantique, modèle petit par défaut et escalade, quotas par utilisateur ; coût par requête suivi comme une métrique de fiabilité.</li>
<li><strong>Stack Java</strong> : LangChain4j (Quarkus ou Spring) ou Spring AI pour les appels, outils, RAG et sorties structurées ; pgvector dans PostgreSQL pour les vecteurs (pas de nouvelle base tant que ça tient) ; Testcontainers pour les tests d'intégration ; la passerelle du TP 54 devant tout.</li>
<li><strong>Cycle de vie</strong> : prompts et schémas versionnés, environnements, canary sur un pourcentage d'utilisateurs, retour arrière de prompt aussi simple qu'un rollback de code, revue humaine échantillonnée en continu, et la fiche AI Act pour chaque usage.</li>
</ul>
'''
LLM_EXO = r'''<div class="exo"><span class="tag">Exercice 54.5</span>
<p>Ton assistant RAG répond à un opérateur avec des informations d'un incident d'une autre organisation. Où est la faille, et quelles sont les deux corrections ?</p>
<details><summary>Corrigé</summary><div class="sol">Le contrôle d'accès n'est pas appliqué à la récupération : l'index est commun et la recherche renvoie des passages que l'utilisateur ne devrait pas voir (LLM02, LLM08). Corrections : filtrer la recherche par organisation et droits avant le classement (métadonnées et clause de filtre, jamais après coup par le modèle), et partitionner l'index par tenant ; ajouter un test d'évaluation qui vérifie qu'aucune source d'une autre organisation n'apparaît.</div></details></div>

'''
LLM_TP = '<li><strong>Application LLM complète</strong> : un assistant « aide à la décision » pour CrisisShield en LangChain4j ou Spring AI derrière ta passerelle : RAG sur les fiches d\'incidents et les runbooks (pgvector, recherche hybride, filtre par organisation), sorties structurées validées, deux outils en lecture seule, un jeu de 30 cas d\'évaluation en CI avec seuil, traces et coût par requête dans Grafana, canary sur un groupe d\'utilisateurs Keycloak, fiche AI Act et threat model. C\'est le second volet de ton projet vitrine.</li>'

# =====================================================================
# Application
# =====================================================================
p = out/'devops-niveau-7-securite-devsecops.html'; s = p.read_text()
assert '37.7 Sécurité applicative' not in s
s = insert_before_niche(s, 37, 'Bearer CLI', APPSEC)
s = s.replace('<div class="tp"><span class="tag">Travail pratique 37', APPSEC_EXO + '<div class="tp"><span class="tag">Travail pratique 37', 1)
i = s.index('<div class="tp"><span class="tag">Travail pratique 37'); j = s.index('</ol>', i); s = s[:j] + APPSEC_TP + s[j:]
s = insert_before_niche(s, 41, 'OpenZiti', PKI)
s = s.replace('<div class="tp"><span class="tag">Travail pratique 41', PKI_EXO + '<div class="tp"><span class="tag">Travail pratique 41', 1)
i = s.index('<div class="tp"><span class="tag">Travail pratique 41'); j = s.index('</ol>', i); s = s[:j] + PKI_TP + s[j:]
s = s.replace('<li>Construire un programme de sécurité applicative mesurable</li>',
              '<li>Construire un programme de sécurité applicative mesurable</li><li>Corriger dans le code Spring Boot chaque catégorie de l\'OWASP Top 10 et tenir une checklist de revue sécurité</li>', 1)
s = s.replace('<li>Authentifier services, partenaires et webhooks sans compte partagé</li>',
              '<li>Authentifier services, partenaires et webhooks sans compte partagé</li><li>Lire, valider, convertir et exploiter des certificats X.509 ; diagnostiquer les erreurs TLS ; conduire une cérémonie de clés et justifier un HSM</li>', 1)
s = s.replace('<li>SBOM à chaque build ; prioriser par EPSS, KEV et reachability ; VEX pour documenter le non-exploitable.</li>',
              '<li>SBOM à chaque build ; prioriser par EPSS, KEV et reachability ; VEX pour documenter le non-exploitable.</li><li>Dans le code : autorisation par objet, entrées validées, requêtes paramétrées, en-têtes, pas de désérialisation d\'entrée, SSRF bloqué ; huit lignes de checklist en revue.</li>', 1)
s = s.replace('<li>PKI : racine hors ligne, intermédiaire en ligne (Vault), certificats courts renouvelés par cert-manager.</li>',
              '<li>PKI : racine hors ligne, intermédiaire en ligne (Vault), certificats courts renouvelés par cert-manager ; les SAN font foi, la chaîne sans la racine, OCSP stapling ou durée courte, inventaire et alerte d\'expiration.</li>', 1)
s = s.replace('<li>Les quinze questions DevSecOps de la section 42.5.</li>',
              '<li>Les quinze questions DevSecOps de la section 42.5.</li><li>OWASP Top 10 : pour chaque catégorie, le motif vulnérable, la correction Spring et le test.</li><li>X.509 : les sept champs et leurs pièges ; validation et révocation ; les sept erreurs TLS fréquentes ; cérémonie de clés et HSM.</li>', 1)
p.write_text(s); print('niveau 7 :', re.findall(r'<h3>(37\.\d|41\.\d) ', s))

p = out/'devops-niveau-9-expert-leadership.html'; s = p.read_text()
assert '54.8 Construire' not in s
s = insert_before_niche(s, 54, 'Signature de modèles et ML-BOM', LLM)
s = s.replace('<div class="tp"><span class="tag">Travail pratique 54', LLM_EXO + '<div class="tp"><span class="tag">Travail pratique 54', 1)
old = '<li>Rédige la fiche produit et l\'architecture de la passerelle comme livrable de mission'
assert old in s; s = s.replace(old, LLM_TP + '\n' + old, 1)
s = s.replace('<li>Exploiter des systèmes d\'IA en production : LLMOps, coût, évaluation, observabilité</li>',
              '<li>Exploiter des systèmes d\'IA en production : LLMOps, coût, évaluation, observabilité</li><li>Construire une application LLM complète (RAG avec contrôle d\'accès, agents bornés, sorties structurées, évaluation en CI) avec la stack Java</li>', 1)
s = s.replace('<li>Copilot : le contexte dans le dépôt vaut plus que les prompts',
              '<li>Application LLM : le contrôle d\'accès s\'applique à la récupération, les sorties sont validées, les prompts sont versionnés et évalués en CI, le coût est une métrique.</li><li>Copilot : le contexte dans le dépôt vaut plus que les prompts', 1)
s = s.replace('<li>Copilot : offres et facturation aux crédits,',
              '<li>Architecture d\'une application LLM en production : les huit briques, et ce que RAG, agents et évaluation exigent.</li><li>Copilot : offres et facturation aux crédits,', 1)
p.write_text(s); print('niveau 9 :', re.findall(r'<h3>(54\.\d) ', s))

# =====================================================================
# Carte des compétences sur la page d'accueil
# =====================================================================
ip = out/'devops-parcours-complet.html'; t = ip.read_text()
if 'Carte des compétences' not in t:
    L = {0:"devops-niveau-0-fondations.html",1:"devops-niveau-1-conteneurs.html",2:"devops-niveau-2-ci-cd.html",3:"devops-niveau-3-infrastructure-as-code.html",4:"devops-niveau-4-cloud.html",5:"devops-niveau-5-kubernetes.html",6:"devops-niveau-6-observabilite.html",7:"devops-niveau-7-securite-devsecops.html",8:"devops-niveau-8-sre-architecture.html",9:"devops-niveau-9-expert-leadership.html"}
    def a(lvl, ch, txt): return f'<a href="{L[lvl]}#c{ch}">{txt}</a>'
    rows = [
     ("DevSecOps", "Niveau 7 entier : " + ", ".join([a(7,37,"analyses et SBOM (37)"), a(7,38,"secrets (38)"), a(7,39,"Kubernetes (39)"), a(7,40,"supply chain (40)"), a(7,41,"zero trust (41)"), a(7,42,"conformité et 15 questions (42)")]) + " ; " + a(2,13,"quality gates (13)") + ", " + a(1,10,"scan et signature d'images (10)")),
     ("Cybersécurité applicative", a(7,37,"threat modeling, SAST/DAST/SCA, OWASP Top 10 dans le code Spring (37.7)") + ", " + a(7,41,"authentification, OAuth 2.1, Spring Security (41.4 à 41.7)") + ", " + a(2,13,"tests de sécurité en pipeline (13)")),
     ("PKI, TLS, HSM", a(0,3,"TLS et certificats (3.6)") + ", " + a(7,38,"Vault PKI et Transit (38)") + ", " + a(7,41,"PKI interne, SPIFFE, PKI en pratique : X.509, révocation, erreurs, cérémonie, HSM (41.2, 41.3, 41.9)") + ", " + a(4,21,"KMS et Nitro Enclaves (21)")),
     ("LLM et IA", a(9,54,"agents, AIOps, LLMOps, OWASP LLM Top 10, application LLM en production (54.1 à 54.4, 54.8)") + ", " + a(9,54,"passerelle IA sécurisée (TP 54)")),
     ("GitHub Copilot et IA générative", a(9,54,"usage développeur (54.5), Enterprise (54.6), prompts, sécurité et adoption (54.7)")),
     ("Terraform", a(3,16,"chapitre 16 : modèle, modules, state, CI, langage avancé, débogage (16.1 à 16.8)") + ", " + a(4,21,"AWS en Terraform (21)") + ", " + a(9,49,"landing zone (49)")),
     ("Ansible", a(3,17,"chapitre 17 : playbooks, rôles, Vault, Molecule, flux et stratégies, performance (17.1 à 17.8)") + ", " + a(3,18,"Packer (18)")),
     ("Kubernetes", "Niveau 5 entier : " + a(5,25,"architecture, kubectl expert, administration (25)") + ", " + a(5,26,"objets, manifests avancés, 20 questions (26)") + ", " + a(5,27,"stockage et opérateurs (27)") + ", " + a(5,28,"Helm et Kustomize (28)") + ", " + a(5,29,"ArgoCD (29)") + ", " + a(5,30,"mesh (30)") + ", " + a(5,31,"autoscaling (31)") + " ; " + a(7,39,"sécurité (39)")),
     ("Docker et CI/CD", a(1,8,"Docker (8)") + ", " + a(1,9,"Compose (9)") + ", " + a(2,12,"GitLab CI, GitHub Actions, Jenkins (12)") + ", " + a(2,15,"stratégies de déploiement (15)")),
     ("Cloud AWS et FinOps", a(4,21,"AWS en profondeur (21)") + ", " + a(4,22,"Azure et GCP (22)") + ", " + a(4,23,"FinOps (23)")),
     ("Observabilité et SRE", a(6,32,"logs (32)") + ", " + a(6,33,"métriques (33)") + ", " + a(6,34,"traces (34)") + ", " + a(6,35,"SLO et alerting (35)") + ", " + a(6,36,"incidents (36)") + ", " + a(8,43,"modèle SRE, Tech Lead SRE, SRE de plateforme, 15 questions (43)") + ", " + a(8,44,"PRA (44)")),
     ("Architecture et données", a(8,45,"performance (45)") + ", " + a(8,46,"microservices et Kafka (46)") + ", " + a(8,47,"PostgreSQL en production (47)") + ", " + a(8,48,"platform engineering (48)")),
     ("Tech Lead et leadership", a(9,51,"gouvernance (51)") + ", " + a(9,52,"DORA et audit (52)") + ", " + a(9,53,"conduite du changement, coaching, 30 questions Tech Lead (53)") + ", " + a(9,50,"migration legacy (50)")),
    ]
    table = '<h2>Carte des compétences</h2>\n<p>Pour retrouver un sujet de fiche de poste ou de mission : où il est traité, et à quel niveau de profondeur.</p>\n<div class="tablewrap"><table><tr><th>Compétence</th><th>Où dans le parcours</th></tr>' + ''.join(f'<tr><td><strong>{k}</strong></td><td>{v}</td></tr>' for k, v in rows) + '</table></div>\n'
    t = t.replace('<h2>Comment travailler ce parcours</h2>', table + '<h2>Comment travailler ce parcours</h2>', 1)
    ip.write_text(t); print('carte des compétences ok')
