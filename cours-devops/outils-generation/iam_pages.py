"""Cours Keycloak et IAM (9 chapitres). Usage : python3 iam_pages.py <dossier>"""
import sys, runpy, pathlib
g = runpy.run_path(pathlib.Path(__file__).with_name('front_gen.py'), run_name='front'); ch, page = g['ch'], g['page']
def T(rows, head): return '<div class="tablewrap"><table><tr>' + ''.join(f'<th>{h}</th>' for h in head) + '</tr>' + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows) + '</table></div>'
DK = "Tout en conteneur : Keycloak, PostgreSQL et les applications tournent par Docker Compose ; l'outil d'administration <code>kcadm.sh</code> s'utilise avec <code>docker compose exec keycloak</code>."

IAM = [
ch("Fondamentaux de l'identité : authentifier, autoriser, fédérer", 'j',
 ["Identifier (qui dit être là), authentifier (le prouver), autoriser (décider ce qu'il peut faire) : trois questions distinctes, souvent confondues.", "OAuth 2 délègue un accès à une API par jeton ; OpenID Connect ajoute l'identité de l'utilisateur ; SAML fait la même chose en XML, encore très présent en entreprise.", "Un jeton d'accès sert à l'API, un jeton d'identité sert au client, un jeton de rafraîchissement renouvelle l'accès : chacun a son destinataire et sa durée de vie."],
 ["Distinguer authentification, autorisation et fédération", "Comparer OAuth 2, OpenID Connect et SAML", "Lire un JWT et savoir ce qu'il faut vérifier"],
 [("Les protocoles", T([
    ("OAuth 2 (2.1)", "déléguer l'accès à une API", "jeton d'accès", "API, applications, services"),
    ("OpenID Connect", "savoir qui est l'utilisateur", "jeton d'identité (JWT) + jeton d'accès", "connexion unique (SSO) moderne"),
    ("SAML 2.0", "connexion unique entre organisations", "assertion XML signée", "applications d'entreprise, administrations")], ("Protocole", "Sert à", "Produit", "Où on le trouve")), None),
  ("Lire un JWT", "Un JWT se compose d'un en-tête, d'un contenu et d'une signature, encodés en base64url : lisibles par tous, donc sans secret dedans. Le destinataire vérifie la signature avec la clé publique de l'émetteur, puis l'émetteur, l'audience, l'expiration et les droits.", """{ "alg": "RS256", "kid": "k1a9…" }                                   # en-tête : algorithme, identifiant de clé
{ "iss": "https://sso.crisis.fr/realms/crisis",                         # émetteur
  "aud": "incidents",                                                   # destinataire : cette API
  "sub": "8f2c…", "azp": "crisis-web",                                  # utilisateur, client
  "exp": 1790160000, "iat": 1790159700,                                 # expiration, émission (5 min)
  "scope": "openid incidents:lire incidents:escalader",
  "realm_access": { "roles": ["operateur"] } }
# décoder pour lire (jamais pour faire confiance) :
echo "$JETON" | cut -d. -f2 | tr '_-' '/+' | base64 -d 2>/dev/null"""),
  ("Durées de vie", "Un jeton d'accès vit quelques minutes, car il ne se révoque pas facilement ; le jeton de rafraîchissement vit plus longtemps, tourne à chaque usage et se révoque à la déconnexion ; la session de l'utilisateur est bornée par une durée maximale.", None)],
 [("Un développeur met le rôle « admin » dans le jeton d'identité et le vérifie côté navigateur pour afficher le menu d'administration. Où est le problème ?", "Afficher un menu selon le rôle est un confort ; la décision de sécurité doit être prise par l'API, qui vérifie le jeton d'accès qui lui est destiné. Le navigateur est sous le contrôle de l'utilisateur."),
  ("Question d'entretien : différence entre jeton d'identité et jeton d'accès ?", "Le jeton d'identité est destiné au client, pour savoir qui s'est connecté ; le jeton d'accès est destiné à l'API, pour autoriser un appel. On n'envoie jamais le jeton d'identité à une API comme preuve d'accès.")],
 ("Premiers jetons", ["Décoder trois jetons (identité, accès, rafraîchissement) obtenus depuis un Keycloak de test, et annoter chaque champ.", "Écrire la liste des vérifications qu'une API doit faire sur un jeton d'accès.", "Comparer une assertion SAML et un jeton d'identité OIDC pour le même utilisateur."],
  "Attendu : chaque champ est expliqué (iss, aud, sub, azp, exp, scope, rôles) ; la liste de vérifications contient signature, émetteur, audience, expiration, portées ; la comparaison montre qui signe quoi et pour qui.")),

ch("Keycloak : royaumes, clients, utilisateurs, rôles", 'j',
 ["Un royaume (realm) isole utilisateurs, clients et réglages ; le royaume master sert uniquement à administrer Keycloak.", "Un client représente une application : client public (navigateur, mobile) ou confidentiel (serveur, avec secret) ; ses adresses de redirection sont exactes, jamais génériques.", "Utilisateurs, groupes, rôles de royaume et de client, portées et mappeurs décident de ce qui figure dans les jetons ; la configuration se versionne comme du code."],
 ["Installer Keycloak en Docker, en mode développement puis production", "Configurer royaume, clients, rôles et mappeurs", "Gérer la configuration de Keycloak comme du code"],
 [("Keycloak en Docker", DK, """services:
  keycloak:
    image: quay.io/keycloak/keycloak:26.0
    command: [ "start", "--optimized", "--import-realm" ]         # en local : start-dev
    environment:
      KC_DB: postgres
      KC_DB_URL: jdbc:postgresql://kc-db:5432/keycloak
      KC_DB_USERNAME: keycloak
      KC_DB_PASSWORD: ${KC_DB_PASSWORD}
      KC_HOSTNAME: https://sso.crisis.fr
      KC_PROXY_HEADERS: xforwarded                                   # derrière un reverse proxy TLS
      KC_HEALTH_ENABLED: "true"
      KC_METRICS_ENABLED: "true"
      KC_BOOTSTRAP_ADMIN_USERNAME: admin-temporaire
      KC_BOOTSTRAP_ADMIN_PASSWORD: ${KC_ADMIN_PASSWORD}
    volumes: [ "./realms:/opt/keycloak/data/import:ro" ]
  kc-db: { image: postgres:16, environment: { POSTGRES_DB: keycloak, POSTGRES_USER: keycloak, POSTGRES_PASSWORD: "${KC_DB_PASSWORD}" } }"""),
  ("Royaume, clients et rôles", "Pour CrisisShield : un royaume crisis, un client public crisis-web (code d'autorisation avec PKCE), un client confidentiel pour chaque API, des rôles de royaume (operateur, coordinateur, admin) et des groupes par préfecture.", """docker compose exec keycloak /opt/keycloak/bin/kcadm.sh config credentials --server http://localhost:8080 --realm master --user admin-temporaire
docker compose exec keycloak /opt/keycloak/bin/kcadm.sh create realms -s realm=crisis -s enabled=true -s bruteForceProtected=true
docker compose exec keycloak /opt/keycloak/bin/kcadm.sh create clients -r crisis \\
  -s clientId=crisis-web -s publicClient=true -s standardFlowEnabled=true -s directAccessGrantsEnabled=false \\
  -s 'redirectUris=["https://crisis.fr/callback"]' -s 'webOrigins=["https://crisis.fr"]' \\
  -s 'attributes={"pkce.code.challenge.method":"S256"}'
docker compose exec keycloak /opt/keycloak/bin/kcadm.sh create roles -r crisis -s name=coordinateur"""),
  ("La configuration comme code", "Un royaume exporté en JSON s'importe au démarrage ; pour faire évoluer un royaume existant, keycloak-config-cli ou le fournisseur Terraform de Keycloak appliquent les changements depuis le dépôt, relus en MR.", """# Terraform (fournisseur keycloak/keycloak)
resource "keycloak_openid_client" "incidents_api" {
  realm_id                 = keycloak_realm.crisis.id
  client_id                = "incidents-api"
  access_type              = "CONFIDENTIAL"
  service_accounts_enabled = true
  standard_flow_enabled    = false
}
resource "keycloak_role" "coordinateur" { realm_id = keycloak_realm.crisis.id, name = "coordinateur" }""")],
 [("Un client a pour adresse de redirection « https://crisis.fr/* ». Quel risque ?", "Une redirection générique permet, avec une faille de redirection ouverte ailleurs sur le site, de détourner le code d'autorisation vers une page contrôlée par l'attaquant. Les adresses de redirection sont exactes, une par besoin."),
  ("Question d'entretien : à quoi sert le royaume master ?", "À administrer Keycloak lui-même ; les applications et leurs utilisateurs vivent dans leurs propres royaumes, et l'accès à master est réservé à quelques administrateurs, idéalement depuis un réseau d'administration.")],
 ("Keycloak pour CrisisShield", ["Keycloak et PostgreSQL en Compose, derrière un reverse proxy TLS.", "Royaume crisis : client public crisis-web avec PKCE, clients confidentiels des API, rôles, groupes par préfecture, mappeur de groupe.", "Toute la configuration en Terraform, appliquée par la CI ; recréer le royaume de zéro."],
  "Attendu : le royaume se recrée entièrement depuis le dépôt ; aucune adresse de redirection générique ; le jeton d'accès contient les rôles et le groupe de préfecture ; le royaume master n'a qu'un administrateur nominatif.")),

ch("Les flux OAuth 2 et OpenID Connect", 'c',
 ["Code d'autorisation avec PKCE pour tout ce qui a un utilisateur (web, mobile, SPA) ; identifiants client (client credentials) pour les services sans utilisateur.", "Les flux implicite et « mot de passe » sont abandonnés : ils exposent des jetons ou des mots de passe.", "Pour une application web moderne, un BFF garde les jetons côté serveur et ne donne au navigateur qu'un cookie de session HttpOnly."],
 ["Dérouler le flux code d'autorisation avec PKCE", "Choisir le bon flux pour chaque type de client", "Mettre en place un BFF pour une application monopage"],
 [("Code d'autorisation avec PKCE", "Le client génère un secret à usage unique, en envoie l'empreinte à Keycloak, puis le secret lui-même en échangeant le code : un code volé ne sert à rien sans ce secret. Les paramètres state et nonce protègent contre la falsification de requête et le rejeu.", """1. navigateur → /auth?response_type=code&client_id=crisis-web&redirect_uri=…&scope=openid
                   &state=ALEA1&nonce=ALEA2&code_challenge=SHA256(verif)&code_challenge_method=S256
2. l'utilisateur s'authentifie chez Keycloak (mot de passe, MFA, passkey)
3. Keycloak → redirect_uri?code=XYZ&state=ALEA1          (state vérifié par le client)
4. client → /token : grant_type=authorization_code, code=XYZ, code_verifier=verif
5. Keycloak → id_token (nonce vérifié), access_token (5 min), refresh_token (rotation)"""),
  ("Le bon flux pour chaque client", "", T([
    ("Application web avec serveur", "code d'autorisation + PKCE, client confidentiel", "jetons côté serveur"),
    ("Application monopage (Angular, React)", "code + PKCE via un BFF", "cookie HttpOnly, pas de jeton dans le navigateur"),
    ("Application mobile", "code + PKCE, client public", "navigateur système, pas de vue web intégrée"),
    ("Service sans utilisateur", "client credentials", "rôle minimal, secret ou clé privée"),
    ("Service au nom d'un utilisateur", "échange de jeton (RFC 8693)", "audience restreinte au service appelé"),
    ("Appareil sans clavier", "device authorization", "code affiché, validation sur un autre appareil")], ("Client", "Flux", "Point d'attention"))),
  ("Le BFF", "Le navigateur ne voit jamais de jeton : le BFF fait le flux OIDC, garde les jetons en session serveur, et relaie les appels à l'API en ajoutant le jeton. Une faille XSS ne peut plus voler de jeton, seulement agir pendant la session, et le cookie est protégé contre la falsification.", """# Spring Cloud Gateway en BFF : connexion OIDC, jeton relayé, cookie de session
spring.security.oauth2.client:
  registration.keycloak: { client-id: crisis-bff, client-secret: "${BFF_SECRET}", scope: openid,incidents:lire, authorization-grant-type: authorization_code }
  provider.keycloak.issuer-uri: https://sso.crisis.fr/realms/crisis
spring.cloud.gateway.routes: [ { id: api, uri: "http://incidents:8080", predicates: ["Path=/api/**"], filters: ["TokenRelay=", "StripPrefix=1"] } ]
server.servlet.session.cookie: { http-only: true, secure: true, same-site: strict }""")],
 [("Une application Angular stocke le jeton d'accès dans localStorage. Quel risque, et quelle alternative ?", "N'importe quel script injecté (XSS) lit et exfiltre le jeton. L'alternative est un BFF : le jeton reste côté serveur, le navigateur n'a qu'un cookie HttpOnly et SameSite, et les appels passent par le BFF."),
  ("Question d'entretien : à quoi sert PKCE si le client a déjà un code ?", "À prouver que celui qui échange le code est celui qui a démarré le flux : un code intercepté (application malveillante, journal, redirection) est inutilisable sans le vérificateur secret.")],
 ("Trois flux sur CrisisShield", ["Connexion de l'application Angular via un BFF (code + PKCE), jetons invisibles dans le navigateur.", "Traitement de nuit en client credentials avec un rôle minimal.", "Capturer les échanges et vérifier state, nonce, PKCE et rotation du jeton de rafraîchissement."],
  "Attendu : aucun jeton dans le stockage du navigateur ; un code rejoué est refusé ; un jeton de rafraîchissement déjà utilisé est refusé et révoque la session ; le traitement de nuit ne peut rien faire hors de son rôle.")),

ch("Intégrer des applications : Spring, front, services", 'c',
 ["Chaque API est un serveur de ressources : elle valide signature, émetteur, audience et expiration, puis transforme portées et rôles en autorisations.", "Le client (BFF, application serveur) utilise la bibliothèque OIDC de son framework : jamais de code de protocole écrit à la main.", "La correspondance entre rôles Keycloak et autorisations applicatives est explicite, testée, et documentée."],
 ["Configurer Spring Security en serveur de ressources et en client", "Transformer rôles et portées Keycloak en autorisations", "Tester l'autorisation d'une API"],
 [("Spring Security : serveur de ressources", "L'API récupère les clés publiques de Keycloak (JWKS), vérifie l'audience, et convertit les rôles du jeton en autorités Spring.", """spring.security.oauth2.resourceserver.jwt: { issuer-uri: "https://sso.crisis.fr/realms/crisis", audiences: [ incidents ] }
---
@Bean SecurityFilterChain api(HttpSecurity http) throws Exception {
  var conv = new JwtAuthenticationConverter();
  conv.setJwtGrantedAuthoritiesConverter(jwt -> {
    var roles = Optional.ofNullable(jwt.getClaimAsMap("realm_access")).map(m -> (List<String>) m.get("roles")).orElse(List.of());
    var scopes = Optional.ofNullable(jwt.getClaimAsString("scope")).map(s -> List.of(s.split(" "))).orElse(List.of());
    return Stream.concat(roles.stream().map(r -> "ROLE_" + r), scopes.stream().map(s -> "SCOPE_" + s))
                 .map(SimpleGrantedAuthority::new).collect(Collectors.toList());
  });
  return http.authorizeHttpRequests(a -> a
      .requestMatchers(HttpMethod.POST, "/v1/incidents/*/escalades").hasAuthority("SCOPE_incidents:escalader")
      .requestMatchers("/v1/admin/**").hasRole("admin")
      .anyRequest().authenticated())
    .oauth2ResourceServer(o -> o.jwt(j -> j.jwtAuthenticationConverter(conv))).build();
}"""),
  ("Côté interface et côté Node", "L'interface ne fait que refléter les droits (menus, boutons) à partir des informations fournies par le BFF ; un service Node vérifie les jetons avec une bibliothèque éprouvée, sur les mêmes critères.", """// Node : vérification d'un jeton d'accès avec la bibliothèque jose
import { createRemoteJWKSet, jwtVerify } from "jose";
const JWKS = createRemoteJWKSet(new URL("https://sso.crisis.fr/realms/crisis/protocol/openid-connect/certs"));
export async function verifier(jeton) {
  const { payload } = await jwtVerify(jeton, JWKS, { issuer: "https://sso.crisis.fr/realms/crisis", audience: "incidents", algorithms: ["RS256"] });
  return payload;          // puis : portées et rôles vérifiés pour l'action demandée
}"""),
  ("Tester l'autorisation", "Chaque règle d'accès a son test : un utilisateur sans la portée reçoit 403, sans jeton 401, avec un jeton destiné à une autre API 401. Spring fournit des jetons simulés pour les tests ; les tests d'intégration utilisent un Keycloak en conteneur.", """@Test void escalade_refusee_sans_portee() throws Exception {
  mvc.perform(post("/v1/incidents/42/escalades").with(jwt().authorities(new SimpleGrantedAuthority("SCOPE_incidents:lire"))))
     .andExpect(status().isForbidden());
}
@Test void escalade_autorisee() throws Exception {
  mvc.perform(post("/v1/incidents/42/escalades").with(jwt().authorities(new SimpleGrantedAuthority("SCOPE_incidents:escalader"))))
     .andExpect(status().isAccepted());
}
# intégration : dasniko/testcontainers-keycloak démarre un vrai Keycloak avec le royaume du dépôt""")],
 [("L'API accepte un jeton émis pour l'application « mobilisation ». Quelle vérification manque ?", "L'audience : l'API doit exiger que le jeton lui soit destiné (aud contient incidents). Sans cela, tout jeton valide du royaume ouvre toutes les API."),
  ("Question d'entretien : rôle ou portée pour autoriser une action ?", "La portée dit ce que le client a le droit de demander au nom de l'utilisateur ; le rôle dit ce que l'utilisateur a le droit de faire. Une action sensible vérifie souvent les deux : le client y est autorisé, et l'utilisateur aussi.")],
 ("Protéger les API de CrisisShield", ["Incidents et Mobilisation en serveurs de ressources Spring avec audience, rôles et portées.", "Un service Node qui vérifie les jetons avec jose selon les mêmes règles.", "Tests d'autorisation unitaires et tests d'intégration avec Keycloak en Testcontainers."],
  "Attendu : un jeton pour Mobilisation est refusé par Incidents ; chaque règle d'accès a un test qui échoue si on la supprime ; le service Node applique exactement les mêmes vérifications.")),

ch("Fédération : fournisseurs d'identité externes et annuaires", 's',
 ["Keycloak peut déléguer l'authentification à un autre fournisseur (Entra ID, Google, un fournisseur SAML d'une autre administration) : c'est le courtage d'identité.", "Il peut aussi lire les utilisateurs d'un annuaire LDAP ou Active Directory : c'est la fédération d'utilisateurs.", "Les attributs reçus sont traduits par des mappeurs ; le premier accès d'un utilisateur externe suit un flux dédié (création, liaison à un compte existant)."],
 ["Connecter un fournisseur d'identité OIDC ou SAML", "Fédérer un annuaire LDAP ou Active Directory", "Maîtriser les mappeurs et le premier accès"],
 [("Courtage d'identité", "Les agents d'une préfecture se connectent avec le fournisseur de leur organisation ; Keycloak reçoit l'assertion, applique les mappeurs, et émet ses propres jetons pour CrisisShield. L'application ne connaît qu'un seul émetteur.", """docker compose exec keycloak /opt/keycloak/bin/kcadm.sh create identity-provider/instances -r crisis \\
  -s alias=entra-prefecture -s providerId=oidc -s enabled=true \\
  -s 'config={"issuer":"https://login.microsoftonline.com/<tenant>/v2.0","clientId":"…","clientSecret":"${vault.entra_secret}",
              "defaultScope":"openid profile email","syncMode":"FORCE","validateSignature":"true","useJwksUrl":"true"}'
# mappeur : le groupe Entra « Cellule-de-crise » donne le rôle Keycloak coordinateur"""),
  ("Annuaire LDAP ou Active Directory", "La fédération d'utilisateurs lit les comptes dans l'annuaire (en lecture seule le plus souvent), importe ou non les utilisateurs, et associe les groupes de l'annuaire aux rôles. La connexion à l'annuaire est chiffrée et le compte de liaison a des droits minimaux.", T([
    ("Connexion", "ldaps:// ou StartTLS, certificat vérifié", "mot de passe en clair sur le réseau"),
    ("Mode", "lecture seule (READ_ONLY)", "écrire dans l'annuaire depuis Keycloak sans besoin"),
    ("Compte de liaison", "lecture des branches utiles seulement", "compte administrateur du domaine"),
    ("Groupes", "mappeur de groupes vers rôles", "rôles attribués à la main, un par un")], ("Réglage", "Recommandé", "À éviter"))),
  ("Le premier accès", "Quand un utilisateur externe arrive pour la première fois, Keycloak peut créer son compte, le lier à un compte existant de même adresse (après vérification), ou demander une confirmation. Lier automatiquement sur la seule adresse électronique est dangereux si le fournisseur externe ne la vérifie pas.", None)],
 [("Un utilisateur d'un fournisseur externe prend le contrôle d'un compte local en créant là-bas une adresse identique. Comment est-ce possible ?", "Le premier accès lie automatiquement les comptes sur l'adresse électronique sans exiger qu'elle soit vérifiée ni que l'utilisateur prouve détenir le compte local. On exige une adresse vérifiée par un fournisseur de confiance, ou une réauthentification avant liaison."),
  ("Question d'entretien : courtage d'identité ou fédération d'utilisateurs ?", "Le courtage délègue la connexion à un autre fournisseur d'identité (OIDC, SAML) ; la fédération d'utilisateurs lit les comptes d'un annuaire (LDAP, Active Directory) et Keycloak vérifie lui-même le mot de passe contre l'annuaire.")],
 ("Fédérer les préfectures", ["Un second Keycloak en Compose joue le fournisseur d'une préfecture ; le relier en OIDC au royaume crisis.", "Un annuaire OpenLDAP en conteneur, fédéré en lecture seule, groupes associés aux rôles.", "Tester le premier accès : création, liaison contrôlée, tentative de prise de compte par adresse identique."],
  "Attendu : un agent de la préfecture se connecte à CrisisShield avec son propre fournisseur et reçoit le bon rôle ; l'annuaire n'est jamais modifié ; la tentative de prise de compte échoue.")),

ch("Authentification forte, flux et sessions", 's',
 ["L'authentification multifacteur (code à usage unique, WebAuthn et passkeys) se configure par flux, et s'impose aux rôles sensibles.", "L'authentification renforcée à la demande (step-up) exige un niveau supérieur pour une action sensible, grâce aux niveaux d'assurance (ACR).", "Politiques de mot de passe, protection contre les attaques par force brute, durées de session et déconnexion complètent le dispositif."],
 ["Mettre en place MFA et passkeys", "Exiger une authentification renforcée pour une action sensible", "Régler sessions, force brute et politiques de mot de passe"],
 [("MFA et passkeys", "Les passkeys (WebAuthn) résistent à l'hameçonnage : la clé est liée au site. Le code à usage unique reste une solution de repli. Un flux dédié impose le second facteur aux coordinateurs et administrateurs.", """# politique du royaume
docker compose exec keycloak /opt/keycloak/bin/kcadm.sh update realms/crisis \\
  -s 'passwordPolicy="length(12) and notUsername and passwordHistory(5)"' \\
  -s bruteForceProtected=true -s failureFactor=5 -s waitIncrementSeconds=60 \\
  -s ssoSessionIdleTimeout=1800 -s ssoSessionMaxLifespan=36000
# flux de navigateur copié et modifié : « Conditional OTP / WebAuthn » requis si l'utilisateur a le rôle coordinateur
# action requise « webauthn-register » à la première connexion des administrateurs"""),
  ("Authentification renforcée à la demande", "Clore une crise ou supprimer des données exige un niveau d'assurance plus élevé : l'application demande ce niveau (acr_values), Keycloak exige alors le second facteur, et l'API vérifie la valeur acr du jeton avant d'agir.", """# côté client : demander le niveau 2 pour l'action sensible
/auth?…&acr_values=2&prompt=login
# côté Keycloak : correspondance niveau → étapes du flux (niveau 1 : mot de passe ; niveau 2 : mot de passe + WebAuthn)
# côté API : refuser si le niveau est insuffisant
if (!"2".equals(jwt.getClaimAsString("acr"))) throw new AccessDeniedException("authentification renforcée requise");"""),
  ("Sessions et déconnexion", "Des sessions courtes pour les rôles sensibles, une déconnexion qui révoque aussi le jeton de rafraîchissement, et la déconnexion par le canal serveur (back-channel) pour prévenir chaque application. On surveille les événements de connexion : échecs, nouveaux appareils, pays inhabituels.", None)],
 [("Les coordinateurs se font hameçonner malgré le code à usage unique : le faux site relaie le code en temps réel. Quelle parade ?", "Des passkeys (WebAuthn) : la signature est liée au nom de domaine du vrai site, un faux site ne peut pas l'obtenir. Le code à usage unique, lui, se relaie."),
  ("Question d'entretien : qu'est-ce que l'authentification renforcée à la demande ?", "Exiger un niveau d'authentification plus élevé seulement pour les actions sensibles : l'application demande un niveau d'assurance, le fournisseur d'identité fait passer l'étape manquante, et l'API vérifie ce niveau dans le jeton avant d'agir.")],
 ("Authentification forte sur CrisisShield", ["Passkeys obligatoires pour coordinateurs et administrateurs, code à usage unique en repli.", "Authentification renforcée pour « clore une crise » : l'API vérifie acr.", "Politique de mot de passe, protection force brute, sessions courtes, journal des événements de connexion vers Loki."],
  "Attendu : clore une crise sans second facteur récent est refusé par l'API ; cinq échecs bloquent temporairement le compte ; les événements de connexion sont visibles et alertent sur les échecs en rafale.")),

ch("Autorisation fine : RBAC, ABAC, ReBAC", 's',
 ["Les rôles (RBAC) suffisent pour les grandes catégories ; les attributs (ABAC) et les relations (ReBAC) servent quand la décision dépend de la ressource : « cet agent peut-il modifier cet incident de cette préfecture ? ».", "On sépare le point de décision (le moteur qui décide) du point d'application (l'API qui applique) ; la décision reste proche des données.", "OPA exprime des politiques par attributs ; OpenFGA, inspiré de Zanzibar, modélise des relations ; les deux se testent comme du code."],
 ["Choisir entre rôles, attributs et relations", "Écrire une politique OPA et un modèle OpenFGA", "Placer décision et application au bon endroit"],
 [("Trois modèles", "", T([
    ("RBAC (rôles)", "un rôle donne des droits", "« les coordinateurs escaladent »", "simple, vite limité"),
    ("ABAC (attributs)", "règles sur utilisateur, ressource, contexte", "« seulement les incidents de ma préfecture, en heures de crise »", "expressif, à tester"),
    ("ReBAC (relations)", "droits déduits de liens", "« membre de la cellule qui gère cet incident »", "adapté au partage et aux hiérarchies")], ("Modèle", "Principe", "Exemple CrisisShield", "Compromis"))),
  ("Une politique OPA", "L'API envoie à OPA l'utilisateur (tiré du jeton), l'action et la ressource ; OPA répond oui ou non selon la politique, versionnée et testée.", """package crisis.incidents
import rego.v1
default autorise := false
autorise if {
  input.action == "escalader"
  "coordinateur" in input.utilisateur.roles
  input.ressource.prefecture == input.utilisateur.prefecture
  input.ressource.statut == "OUVERT"
}
# test : docker run --rm -v "$PWD:/w" -w /w openpolicyagent/opa:0.69.0 test politiques/ -v"""),
  ("Un modèle OpenFGA", "OpenFGA stocke des relations (« Léa est membre de la préfecture N1 », « l'incident 42 appartient à N1 ») et répond à « Léa peut-elle modifier l'incident 42 ? » en suivant le modèle.", """model
  schema 1.1
type user
type prefecture
  relations
    define membre: [user]
    define coordinateur: [user]
type incident
  relations
    define prefecture: [prefecture]
    define lecteur: membre from prefecture
    define editeur: coordinateur from prefecture
# vérification : l'API demande check(user:lea, editeur, incident:42) avant d'agir""")],
 [("Les rôles se multiplient : coordinateur-N1, coordinateur-N2… 240 rôles. Que proposes-tu ?", "Passer à un modèle par attributs ou par relations : un rôle coordinateur, plus l'attribut ou la relation « préfecture », évalués par OPA ou OpenFGA ; les rôles restent peu nombreux et la règle devient lisible et testable."),
  ("Question d'entretien : où prendre la décision d'autorisation ?", "Dans un point de décision dédié (OPA, OpenFGA) ou dans le service qui possède la ressource, jamais seulement dans l'interface ou la passerelle : c'est là qu'on connaît l'état de la ressource. L'API applique la décision à chaque requête.")],
 ("Autorisation par préfecture", ["Politique OPA « escalader » avec tests unitaires, appelée par l'API Incidents.", "Modèle OpenFGA préfecture, incident, membre, coordinateur ; mêmes décisions que la politique OPA.", "Comparer les deux approches sur dix cas et documenter le choix dans une ADR."],
  "Attendu : un coordinateur de N2 ne peut pas escalader un incident de N1, quel que soit le modèle ; les politiques ont leurs tests en CI ; l'ADR explique pourquoi l'un ou l'autre est retenu.")),

ch("Exploiter et durcir Keycloak", 's',
 ["Keycloak en production : au moins deux instances en grappe, base PostgreSQL sauvegardée, derrière un reverse proxy TLS, avec métriques et journaux d'événements.", "Dans Kubernetes, l'opérateur Keycloak gère le déploiement, les mises à jour et la configuration.", "Durcissement : console d'administration séparée, royaume master verrouillé, rotation des clés de signature, montées de version régulières."],
 ["Déployer Keycloak en haute disponibilité", "Appliquer la liste de durcissement", "Superviser, sauvegarder et mettre à jour Keycloak"],
 [("Haute disponibilité et Kubernetes", "Plusieurs instances partagent la base et se synchronisent par un cache distribué ; l'opérateur Keycloak décrit l'installation dans une ressource Kubernetes, versionnée avec le reste.", """apiVersion: k8s.keycloak.org/v2alpha1
kind: Keycloak
metadata: { name: sso, namespace: identite }
spec:
  instances: 2
  db: { vendor: postgres, host: kc-db, usernameSecret: { name: kc-db, key: user }, passwordSecret: { name: kc-db, key: password } }
  hostname: { hostname: sso.crisis.fr, admin: admin-sso.interne.crisis.fr }     # console d'administration sur un nom interne
  http: { tlsSecret: sso-tls }
  proxy: { headers: xforwarded }"""),
  ("Liste de durcissement", "", T([
    ("Console d'administration", "nom interne, réseau d'administration seulement", "console exposée sur Internet"),
    ("Royaume master", "administrateurs nominatifs, MFA", "compte admin partagé"),
    ("Clients", "adresses de redirection exactes, flux inutiles désactivés", "joker dans les redirections, flux mot de passe actif"),
    ("Jetons", "accès 5 min, rafraîchissement avec rotation", "jetons d'accès d'une journée"),
    ("Clés", "rotation planifiée, ancienne clé gardée le temps de la transition", "même clé depuis l'installation"),
    ("Versions", "montée de version trimestrielle, notes de sécurité suivies", "version jamais mise à jour")], ("Point", "Recommandé", "À éviter"))),
  ("Superviser, sauvegarder, mettre à jour", "Les métriques (sur le port de gestion) alimentent Prometheus ; les événements de connexion et d'administration partent vers la supervision ; la base est sauvegardée et restaurée en test ; chaque montée de version est d'abord jouée sur une copie.", """# métriques et santé sur le port de gestion
curl -s http://keycloak:9000/health/ready
curl -s http://keycloak:9000/metrics | grep -E "keycloak_(logins|failed_login_attempts)"
# événements : activer les événements utilisateur et d'administration, les expédier vers Loki ou Elasticsearch
docker compose exec keycloak /opt/keycloak/bin/kcadm.sh update events/config -r crisis -s eventsEnabled=true -s adminEventsEnabled=true""")],
 [("La console d'administration de Keycloak est accessible depuis Internet avec le compte admin d'origine. Priorités ?", "Couper l'exposition de la console (nom interne, filtrage réseau), remplacer le compte d'origine par des administrateurs nominatifs avec MFA, vérifier les journaux d'administration pour une compromission passée, puis appliquer le reste de la liste."),
  ("Question d'entretien : comment fais-tu tourner les clés de signature sans casser les applications ?", "On ajoute une nouvelle clé active, on garde l'ancienne publiée dans le JWKS le temps que les jetons émis avec elle expirent, puis on la retire ; les applications qui lisent le JWKS dynamiquement suivent sans intervention.")],
 ("Keycloak de production", ["Deux instances derrière un reverse proxy TLS, console d'administration sur un nom séparé, base sauvegardée.", "Liste de durcissement appliquée et vérifiée point par point ; rotation d'une clé de signature sans interruption.", "Tableau de bord Grafana des connexions et échecs ; restauration de la base sur une copie ; montée de version testée."],
  "Attendu : l'arrêt d'une instance ne déconnecte personne ; la rotation de clé ne provoque aucune erreur 401 ; la console d'administration n'est pas joignable depuis l'extérieur ; la restauration fonctionne.")),

ch("Auditer un système d'identité, attaques et entretien", 'e',
 ["Un audit IAM passe en revue clients, flux, adresses de redirection, portées, durées de vie, stockage des jetons, validation côté API et journalisation.", "Les attaques classiques : redirection ouverte et vol de code, jeton dans le navigateur, audience non vérifiée, confusion d'algorithme, CSRF sans state, prise de compte par liaison automatique.", "En entretien, on raconte un audit ou un incident réel : ce qu'on a trouvé, comment on l'a prouvé, ce qu'on a corrigé, et comment on a évité la récidive."],
 ["Mener l'audit d'un royaume Keycloak et de ses applications", "Reconnaître et tester les attaques classiques", "Répondre aux questions d'entretien IAM"],
 [("La grille d'audit", "", T([
    ("Adresses de redirection", "joker, http, domaines tiers", "exactes, https, une par besoin"),
    ("Flux", "implicite ou mot de passe actifs", "code + PKCE, client credentials"),
    ("Jetons dans le navigateur", "localStorage, sessionStorage", "BFF, cookie HttpOnly"),
    ("Validation côté API", "pas d'audience, algorithme accepté sans liste", "émetteur, audience, algorithme, expiration"),
    ("Durées de vie", "accès longue durée, pas de rotation", "5 min, rotation du rafraîchissement"),
    ("Portées", "toutes accordées par défaut", "minimales, demandées explicitement"),
    ("Administration", "console exposée, compte partagé", "réseau interne, MFA, nominatif"),
    ("Journaux", "événements désactivés", "connexions et administration journalisées et alertées")], ("Point", "Constat à risque", "Attendu"))),
  ("Attaques à tester", "Chaque attaque se teste sur un environnement de recette : prouver le risque par un exemple reproductible est ce qui fait accepter une correction.", """1. Redirection ouverte + joker : redirect_uri=https://crisis.fr/../evil → le code part-il ailleurs ?
2. Code rejoué ou sans code_verifier : l'échange est-il refusé ?
3. Jeton d'une autre audience présenté à l'API : 401 attendu
4. Jeton modifié avec "alg":"none" ou signé HS256 avec la clé publique : 401 attendu
5. Réponse d'autorisation sans state ou avec un state d'une autre session : refus attendu
6. Liaison de compte par adresse identique depuis un fournisseur externe : refus ou réauthentification attendus
7. Jeton de rafraîchissement réutilisé après rotation : refus et révocation de la session attendus"""),
  ("Trente questions d'entretien", "", """1 Authentifier ou autoriser ? Prouver l'identité ; décider des droits. 2 OAuth ou OIDC ? Accès délégué ; identité en plus. 3 SAML ? SSO en XML, courant entre organisations. 4 Jeton d'identité ? Pour le client. 5 Jeton d'accès ? Pour l'API. 6 Rafraîchissement ? Renouveler sans reconnexion, avec rotation. 7 Vérifier un JWT ? Signature, émetteur, audience, expiration, algorithme. 8 PKCE ? Lier l'échange du code à celui qui l'a demandé. 9 state et nonce ? Contre la falsification et le rejeu. 10 Flux implicite ? Abandonné. 11 SPA ? BFF et cookie HttpOnly. 12 Service sans utilisateur ? Client credentials. 13 Au nom d'un utilisateur ? Échange de jeton. 14 Royaume master ? Administration seulement. 15 Client public ou confidentiel ? Sans ou avec secret. 16 Redirections ? Exactes. 17 Mappeur ? Ce qui entre dans le jeton. 18 Courtage ? Déléguer la connexion à un autre fournisseur. 19 Fédération LDAP ? Lire les comptes d'un annuaire. 20 Premier accès ? Création ou liaison contrôlée. 21 Passkeys ? Résistantes à l'hameçonnage. 22 Step-up ? Niveau plus élevé pour l'action sensible. 23 Force brute ? Blocage progressif. 24 RBAC, ABAC, ReBAC ? Rôles, attributs, relations. 25 OPA ? Politiques par attributs. 26 OpenFGA ? Relations, modèle Zanzibar. 27 Où décider ? Au plus près de la ressource, appliqué par l'API. 28 Haute disponibilité ? Deux instances, cache distribué, base sauvegardée. 29 Rotation de clés ? Nouvelle clé, ancienne gardée le temps de l'expiration. 30 Audit ? Redirections, flux, stockage, validation, durées, journaux.""")],
 [("En audit, tu trouves qu'une API accepte les jetons signés en HS256. Pourquoi est-ce grave ?", "Si l'API accepte HS256 alors que Keycloak signe en RS256, un attaquant peut signer un jeton avec la clé publique (connue de tous) utilisée comme secret HMAC : c'est la confusion d'algorithme. L'API doit imposer la liste des algorithmes attendus."),
  ("Question d'entretien : raconte un audit IAM.", "STAR : le périmètre, la grille, deux constats majeurs prouvés par un exemple reproductible (redirection générique, audience non vérifiée), la correction appliquée et vérifiée, et la règle ajoutée pour éviter la récidive (Terraform, test d'autorisation en CI).")],
 ("Audit complet d'un royaume", ["Un royaume volontairement mal configuré (fourni par un camarade ou construit exprès) : dérouler la grille d'audit.", "Prouver chacune des sept attaques sur la recette, puis corriger.", "Rapport d'audit de deux pages : constats classés par gravité, preuves, corrections, vérifications."],
  "Attendu : au moins six constats prouvés et corrigés ; chaque correction a un test qui empêche le retour du défaut ; le rapport est lisible par un responsable non technique en première page.")),
]

d = sys.argv[1]
page('cours-11-keycloak-et-iam.html', 'Keycloak et IAM — de zéro à expert', "Neuf chapitres pour maîtriser l'identité et les accès : OAuth 2, OpenID Connect et SAML, Keycloak (royaumes, clients, rôles, configuration comme code), les flux et le BFF, l'intégration Spring, front et Node, la fédération (fournisseurs externes, LDAP), l'authentification forte (passkeys, step-up), l'autorisation fine (OPA, OpenFGA), l'exploitation et le durcissement de Keycloak, et l'audit d'un système d'identité. Fil conducteur : l'accès des préfectures à CrisisShield, tout en Docker ; chaque chapitre a ses exercices corrigés et un travail pratique avec correction type.", "≈ 35 h de travail · prérequis : HTTP, Spring Boot, Docker ; complète le niveau 7 du parcours DevOps et le cours Microservices.", IAM, [('devops-07-securite-devsecops.html', 'DevOps niveau 7'), ('cours-10-ia-agentique.html', 'IA agentique'), ('cours-08-microservices.html', 'Microservices')])
