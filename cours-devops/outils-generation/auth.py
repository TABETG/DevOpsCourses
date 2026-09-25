import re, pathlib, html

p = pathlib.Path('/mnt/user-data/outputs/devops-07-securite-devsecops.html')
s = p.read_text()
assert '41.6 Mise en œuvre' not in s, 'déjà fait'

# ---- schéma : Authorization Code + PKCE ----
def fig_pkce():
    m = "ahpkce"
    b = ''
    def box(x,y,w,h,lines,cls,fs=13,sub=None):
        out = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" class="{cls}"/>'
        n = len(lines)+(1 if sub else 0); lh=fs+4; y0 = y+h/2-(n-1)*lh/2+fs*0.35
        for i,t in enumerate(lines): out += f'<text x="{x+w/2}" y="{y0+i*lh:.1f}" text-anchor="middle" font-size="{fs}" font-weight="700">{html.escape(t)}</text>'
        if sub: out += f'<text x="{x+w/2}" y="{y0+len(lines)*lh:.1f}" text-anchor="middle" class="lbl">{html.escape(sub)}</text>'
        return out
    def ar(x1,y1,x2,y2,label=None,dx=0,dy=-6,dashed=False):
        o = f'<path d="M{x1},{y1} L{x2},{y2}" class="arrow{" dashed" if dashed else ""}" marker-end="url(#{m})"/>'
        if label: o += f'<text x="{(x1+x2)/2+dx}" y="{(y1+y2)/2+dy}" text-anchor="middle" class="lbl">{html.escape(label)}</text>'
        return o
    b += box(10,20,120,50,["Navigateur","(SPA ou BFF)"],"green",12)
    b += box(180,20,120,50,["Keycloak"],"purple",13,"serveur d'autorisation")
    b += box(350,20,120,50,["API"],"soft",13,"serveur de ressources")
    b += ar(130,35,180,35,"1. redirection + code_challenge",0,-9)
    b += ar(180,55,130,55,"2. code (après login, MFA)",0,14)
    b += ar(70,70,70,110) + box(10,110,120,40,["3. échange code"],"box",11,"+ code_verifier")
    b += ar(130,130,180,130) + box(180,110,120,40,["4. jetons"],"box",11,"access, id, refresh")
    b += ar(300,130,350,130,"5. Bearer",0,-9) + box(350,110,120,40,["6. vérifie JWT"],"box",11,"iss, aud, exp, alg, JWKS")
    b += ar(410,110,240,70,"JWKS (clés publiques)",60,-6,True)
    return (f'<figure class="fig"><svg viewBox="0 0 480 165" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Flux Authorization Code avec PKCE">'
            f'<defs><marker id="{m}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="ahead"/></marker></defs>{b}</svg>'
            f'<figcaption>Authorization Code + PKCE : le seul flux à utiliser pour toute application avec un utilisateur. Le code_verifier prouve que celui qui échange le code est celui qui a lancé la demande ; l\'API ne parle jamais à Keycloak pour valider un jeton, elle vérifie la signature avec les clés publiques (JWKS).</figcaption></figure>')

NEW = r'''<h3>41.4 Authentification des humains<span class="badge tag-coeur">Par cœur</span></h3>
<p>L'authentification est la première ligne de tout ce qui précède : un IdP mal configuré annule le mesh, la PKI et Vault. Ce que le DevSecOps exige d'un système d'authentification, quel que soit le produit :</p>
<ul>
<li><strong>Mots de passe</strong> : stockés avec Argon2id (ou bcrypt), jamais réversibles ; politique NIST SP 800-63B : longueur (12 caractères et plus) plutôt que complexité imposée, pas d'expiration périodique, refus des mots de passe compromis (liste Have I Been Pwned), pas d'indices ni de questions secrètes.</li>
<li><strong>MFA</strong> : obligatoire pour tout accès sensible et tout administrateur. Du plus faible au plus fort : SMS (interceptable), TOTP (application), notification push avec appariement de numéro, <strong>FIDO2 / passkeys</strong> (résistant au phishing : la clé est liée au domaine, un faux site n'obtient rien). Les passkeys sont le standard à recommander en 2026.</li>
<li><strong>SSO</strong> : une identité, un endroit où la désactiver. OpenID Connect pour tout ce qui est moderne, SAML 2.0 pour les applications d'entreprise legacy ; l'IdP (Keycloak, Entra ID, Okta) fédère les annuaires (LDAP, Active Directory) et les fournisseurs sociaux ou partenaires (identity brokering).</li>
<li><strong>Sessions</strong> : cookie <code>HttpOnly</code>, <code>Secure</code>, <code>SameSite=Lax</code> ou <code>Strict</code>, identifiant régénéré après connexion (fixation), durée absolue et durée d'inactivité, révocation côté serveur, déconnexion propagée (back-channel logout OIDC).</li>
<li><strong>Attaques à traiter</strong> : force brute et credential stuffing (limitation par compte et par IP, verrouillage progressif, détection d'anomalie), énumération de comptes (messages identiques que le compte existe ou non), phishing (passkeys, pas de lien de connexion magique sans second facteur), et surtout la <strong>récupération de compte</strong>, maillon faible de tout système : elle doit être aussi forte que la connexion.</li>
<li><strong>Keycloak en pratique</strong> : un realm par domaine de confiance, des clients par application avec le flux strictement nécessaire, des flows d'authentification personnalisés (MFA conditionnelle par rôle ou par risque), la détection de force brute activée, les événements exportés vers le SIEM, la configuration en code (export du realm, <code>keycloak-config-cli</code>, opérateur), la haute disponibilité (cluster, base PostgreSQL managée) et un suivi rigoureux des versions : Keycloak publie régulièrement des correctifs de sécurité.</li>
</ul>

<h3>41.5 OAuth 2.1 et OpenID Connect en détail<span class="badge tag-coeur">Par cœur</span></h3>
<p><strong>OAuth 2.1</strong> est un cadre de <em>délégation d'autorisation</em> : une application obtient un jeton pour appeler une API au nom d'un utilisateur, sans jamais voir son mot de passe. <strong>OpenID Connect</strong> ajoute l'<em>authentification</em> par-dessus : un jeton d'identité (<code>id_token</code>) signé qui dit qui s'est connecté, quand, et comment. Quatre rôles : le propriétaire de la ressource (l'utilisateur), le client (l'application), le serveur d'autorisation (Keycloak), le serveur de ressources (l'API).</p>
''' + fig_pkce() + r'''
<div class="tablewrap"><table>
<tr><th>Flux</th><th>Pour</th><th>Statut en OAuth 2.1</th></tr>
<tr><td>Authorization Code + PKCE</td><td>Toute application avec un utilisateur : web, SPA, mobile, CLI avec navigateur</td><td>Le flux par défaut ; PKCE obligatoire pour tous les clients, publics ou confidentiels</td></tr>
<tr><td>Client Credentials</td><td>Machine à machine sans utilisateur (batch, service)</td><td>Autorisé ; préférer mTLS ou SPIFFE quand c'est possible</td></tr>
<tr><td>Device Authorization</td><td>Appareils sans navigateur, CLI, TV</td><td>Autorisé</td></tr>
<tr><td>Token Exchange (RFC 8693)</td><td>Un service appelle un autre service au nom de l'utilisateur, avec un jeton à portée réduite</td><td>Autorisé ; la bonne façon de propager l'identité dans une chaîne de services</td></tr>
<tr><td>Implicit</td><td>Anciennes SPA</td><td>Supprimé (jeton dans l'URL, fuite)</td></tr>
<tr><td>Resource Owner Password</td><td>Formulaire maison qui envoie le mot de passe à l'API</td><td>Supprimé (le client voit le mot de passe, pas de MFA, pas de SSO)</td></tr>
</table></div>
<p>Les trois jetons et ce qu'on en fait :</p>
<ul>
<li><strong>Access token</strong> : pour appeler l'API ; courte durée (5 à 15 minutes) ; audience (<code>aud</code>) = l'API visée, scopes minimaux ; JWT signé ou jeton opaque vérifié par introspection. Le client ne le lit pas, il le transmet.</li>
<li><strong>ID token</strong> : pour le client, jamais envoyé à une API ; contient <code>sub</code>, <code>auth_time</code>, <code>acr</code> (niveau d'authentification), <code>nonce</code> (anti-rejeu).</li>
<li><strong>Refresh token</strong> : pour obtenir un nouvel access token sans réauthentifier ; longue durée mais <strong>rotation à chaque usage</strong> avec détection de réutilisation (un refresh token volé et rejoué révoque toute la famille) ; lié au client ; côté navigateur uniquement via un BFF, jamais dans le localStorage.</li>
</ul>
<pre><code>// Valider un JWT côté serveur de ressources : la liste complète, sans exception
1. alg dans une liste blanche (RS256 ou ES256) ; refuser "none" et HS256 avec un secret partagé
2. signature vérifiée avec la clé publique désignée par kid, obtenue via le JWKS de l'émetteur (cache, rotation)
3. iss = exactement l'URL attendue (https://auth.crisisshield.example/realms/crisis)
4. aud contient l'identifiant de cette API (sinon un jeton émis pour une autre API est réutilisable ici)
5. exp et nbf avec une tolérance d'horloge de quelques secondes
6. typ / scope / rôles : le jeton a le droit de faire cette opération
7. Contrôle d'accès par objet : cet utilisateur a-t-il le droit sur CET incident (IDOR) — le jeton ne le dit pas, le code doit le vérifier</code></pre>
<p>Compléments quand le risque le justifie : jetons liés au client (<strong>DPoP</strong> : preuve de possession d'une clé, ou mTLS-bound) pour qu'un jeton volé soit inutilisable ; <strong>PAR</strong> (Pushed Authorization Requests) et JAR pour ne pas exposer les paramètres d'autorisation dans l'URL ; <strong>FAPI 2.0</strong> comme profil de référence pour la finance et la santé. Découverte automatique via <code>/.well-known/openid-configuration</code> : ne jamais coder en dur les URL des points de terminaison.</p>

<h3>41.6 Mise en œuvre : Spring Security, Quarkus, React avec Keycloak<span class="badge tag-important">Important</span></h3>
<pre><code># Spring Boot 3 : l'API comme serveur de ressources (aucun secret, seulement l'émetteur)
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: https://auth.crisisshield.example/realms/crisis
          audiences: [crisisshield-api]        # rejette les jetons émis pour d'autres API</code></pre>
<pre><code>@Configuration
@EnableMethodSecurity
class SecurityConfig {
    @Bean
    SecurityFilterChain api(HttpSecurity http) throws Exception {
        return http
            .csrf(c -> c.disable())                       // API sans session ni cookie : pas de CSRF
            .sessionManagement(sm -> sm.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(a -> a
                .requestMatchers("/actuator/health/**").permitAll()
                .requestMatchers(HttpMethod.GET, "/api/incidents/**").hasAuthority("ROLE_operator")
                .anyRequest().authenticated())
            .oauth2ResourceServer(o -> o.jwt(j -> j.jwtAuthenticationConverter(keycloakRoles())))
            .build();
    }
    // Les rôles Keycloak sont dans realm_access.roles : les convertir en autorités Spring
    JwtAuthenticationConverter keycloakRoles() {
        var conv = new JwtAuthenticationConverter();
        conv.setJwtGrantedAuthoritiesConverter(jwt -> {
            var realm = (Map&lt;String, Object&gt;) jwt.getClaims().getOrDefault("realm_access", Map.of());
            var roles = (Collection&lt;String&gt;) realm.getOrDefault("roles", List.of());
            return roles.stream().map(r -> new SimpleGrantedAuthority("ROLE_" + r)).collect(toList());
        });
        return conv;
    }
}
// Contrôle par objet : le service vérifie l'organisation de l'utilisateur, pas seulement le rôle
@PreAuthorize("@incidentAccess.canRead(#id, authentication)")
public Incident get(String id) { ... }</code></pre>
<pre><code># Quarkus : même chose en trois lignes
quarkus.oidc.auth-server-url=https://auth.crisisshield.example/realms/crisis
quarkus.oidc.client-id=crisisshield-api
quarkus.oidc.token.audience=crisisshield-api
# puis @RolesAllowed("operator") sur les ressources, et SecurityIdentity injecté</code></pre>
<p>Côté <strong>front React</strong>, deux architectures acceptables :</p>
<ul>
<li><strong>BFF (recommandée)</strong> : un composant serveur (Spring Cloud Gateway avec <code>TokenRelay</code>, ou une petite application Spring Boot <code>oauth2-client</code>) fait le flux OIDC, garde les jetons côté serveur, et donne au navigateur un cookie de session <code>HttpOnly</code>. Le JavaScript ne voit jamais de jeton ; XSS ne peut rien voler. CSRF à gérer sur le BFF (SameSite + jeton).</li>
<li><strong>SPA directe</strong> : bibliothèque conforme (<code>oidc-client-ts</code>, <code>keycloak-js</code>) en Authorization Code + PKCE, access token en mémoire seulement, refresh par rotation et durée courte, politique CSP stricte. Acceptable pour des applications à risque modéré.</li>
</ul>
<p><strong>Tests</strong> : Spring Security Test avec <code>jwt().authorities(...)</code> pour les tests unitaires de contrôleurs, Testcontainers Keycloak (image officielle et un realm importé) pour les tests d'intégration qui obtiennent de vrais jetons, et des tests négatifs systématiques : jeton expiré, <code>alg: none</code>, audience d'une autre API, rôle insuffisant, accès à l'objet d'une autre organisation. Ces tests sont ceux que le TP 41 exige.</p>

<h3>41.7 Authentification entre services et pour les API<span class="badge tag-important">Important</span></h3>
<div class="tablewrap"><table>
<tr><th>Mécanisme</th><th>Quand</th><th>Exigences</th></tr>
<tr><td>mTLS / SPIFFE</td><td>Service à service dans la plateforme</td><td>Certificats courts émis automatiquement, autorisation par identité (mesh, AuthorizationPolicy)</td></tr>
<tr><td>Client Credentials OAuth</td><td>Service à service via l'IdP, batchs</td><td>Secret client dans Vault ou, mieux, assertion JWT signée par une clé privée (<code>private_key_jwt</code>) ; jetons de 5 minutes</td></tr>
<tr><td>Token Exchange</td><td>Propager l'identité de l'utilisateur à travers une chaîne de services</td><td>Jeton échangé contre un jeton à audience et portée réduites ; jamais de relais du jeton d'origine à tout le monde</td></tr>
<tr><td>Clés d'API</td><td>Partenaires externes, intégrations simples</td><td>Stockées hachées, préfixées (identifiables dans les fuites), à portée et quota, tournées, révocables, journalisées ; jamais dans une URL</td></tr>
<tr><td>Signature HMAC de requête / webhooks</td><td>Webhooks entrants et sortants</td><td>Signature sur le corps avec horodatage, fenêtre de validité, rejet des rejeux</td></tr>
<tr><td>Identité cloud (rôle IAM, Workload Identity)</td><td>Appels aux services du fournisseur</td><td>Aucun secret ; le rôle est l'identité (chapitres 21, 38)</td></tr>
</table></div>
<p>Règles transverses : chaque appelant a une identité propre (jamais un compte technique partagé), toute autorisation se fait au serveur, les jetons sont courts, la limitation de débit est par identité, et tout est journalisé avec l'identité de l'appelant pour l'audit. Une passerelle d'API (chapitre 46) centralise validation de jetons, quotas et journalisation ; elle ne remplace pas le contrôle d'accès par objet dans le service.</p>

<h3>41.8 IAM avancé dans le cloud<span class="badge tag-important">Important</span></h3>'''

# remplacer l'ancienne section 41.4 (jusqu'au titre 41.5 IAM avancé inclus)
start = s.index('<h3>41.4 OAuth 2.1, OpenID Connect, jetons')
end_marker = re.search(r'<h3>41\.5 IAM avancé dans le cloud<span class="badge[^<]*</span></h3>', s)
assert end_marker and end_marker.start() > start
s = s[:start] + NEW + s[end_marker.end():]

# objectifs du chapitre 41
s = s.replace('<li>Maîtriser OAuth 2.1, OpenID Connect et les jetons dans une architecture de services</li>',
              '<li>Concevoir l\'authentification des humains : mots de passe, MFA et passkeys, SSO, sessions, récupération de compte</li><li>Maîtriser OAuth 2.1 et OpenID Connect : flux, jetons, validation complète d\'un JWT, BFF</li><li>Implémenter avec Spring Security, Quarkus et React sur Keycloak, tests négatifs compris</li><li>Authentifier services, partenaires et webhooks sans compte partagé</li>', 1)

# résumé en 30 secondes du chapitre 41
s = s.replace('<li>OAuth 2.1 : code + PKCE, jetons courts, refresh rotation, BFF ; IDOR est la faille numéro un des API.</li>',
              '<li>Authentification : Argon2id, MFA par passkeys, SSO OIDC, sessions durcies, récupération de compte aussi forte que la connexion.</li><li>OAuth 2.1 : code + PKCE partout, jetons courts avec audience, refresh rotation, BFF pour le navigateur, validation JWT en sept points ; IDOR est la faille numéro un des API.</li>', 1)

# exercices supplémentaires avant le TP 41
EXOS = r'''<div class="exo"><span class="tag">Exercice 41.3</span>
<p>Une API accepte tout JWT dont la signature est valide auprès du JWKS de Keycloak. Trouve trois attaques que cette validation laisse passer et la ligne de configuration ou de code qui ferme chacune.</p>
<details><summary>Corrigé</summary><div class="sol">Un jeton émis pour une autre API du même realm (pas de vérification d'audience → <code>audiences</code> / <code>token.audience</code>) ; un jeton d'un autre realm ou d'un autre émetteur qui publie aussi un JWKS (pas de vérification d'<code>iss</code> → <code>issuer-uri</code> exact) ; un id_token utilisé comme access token (vérifier <code>typ</code>/<code>azp</code> et l'audience) ; et, si l'algorithme n'est pas restreint, un jeton <code>alg: none</code> ou HS256 signé avec la clé publique comme secret (liste blanche d'algorithmes). Enfin, la signature ne dit rien du droit sur l'objet : IDOR reste à traiter dans le code.</div></details></div>

<div class="exo"><span class="tag">Exercice 41.4</span>
<p>Le service Incidents doit appeler le service Notification « au nom de » l'opérateur connecté. Compare trois options : relayer l'access token reçu, utiliser Client Credentials, utiliser Token Exchange.</p>
<details><summary>Corrigé</summary><div class="sol">Relayer le jeton : simple mais l'audience ne correspond pas (rejet, ou pire, acceptation laxiste) et Notification reçoit un jeton trop puissant. Client Credentials : Notification sait qu'Incidents appelle, mais perd l'identité de l'opérateur (audit et autorisation impossibles). Token Exchange : Incidents échange le jeton contre un jeton d'audience <code>notification</code> à portée réduite, qui porte l'utilisateur d'origine et le service intermédiaire (<code>act</code>) ; c'est la solution correcte, complétée par mTLS/SPIFFE entre les deux services.</div></details></div>

'''
s = s.replace('<div class="tp"><span class="tag">Travail pratique 41', EXOS + '<div class="tp"><span class="tag">Travail pratique 41', 1)

# étapes de TP : remplacer l'étape « Application » par un bloc plus complet
old_tp = s[s.index('<li>Application : audite le flux OAuth de CrisisShield'):]
old_tp = old_tp[:old_tp.index('</li>')+5]
new_tp = ('<li>Authentification des humains : realm Keycloak <code>crisis</code> en code (export JSON versionné, appliqué par <code>keycloak-config-cli</code>), politique de mots de passe NIST avec vérification des mots de passe compromis, passkeys (WebAuthn) obligatoires pour le groupe <code>admin</code> et proposées aux opérateurs, détection de force brute activée, flow de récupération de compte revu (second facteur exigé), événements exportés vers Loki, brokering vers un fournisseur externe (Google ou Entra ID de test).</li>'
          '<li>Application : passe l\'API en serveur de ressources Spring Security (émetteur et audience vérifiés, conversion des rôles, contrôle d\'accès par objet), le front React derrière un BFF Spring Cloud Gateway avec cookie de session <code>HttpOnly</code> (variante : SPA directe avec <code>oidc-client-ts</code> et PKCE, à comparer). Refresh rotation et back-channel logout configurés et testés. Le service Notification (Quarkus) authentifie Incidents par Token Exchange et mTLS.</li>'
          '<li>Tests de sécurité automatisés, tous en CI : jeton expiré, <code>alg: none</code>, HS256 avec clé publique, mauvais émetteur, mauvaise audience, id_token utilisé comme access token, rôle insuffisant, IDOR entre organisations, refresh token rejoué après rotation, clé d\'API révoquée. Chaque cas attend 401 ou 403 et un événement journalisé. Testcontainers Keycloak pour les tests d\'intégration.</li>'
          '<li>Partenaires : une clé d\'API hachée, préfixée et à quota pour un partenaire fictif, un webhook sortant signé HMAC avec horodatage, et la vérification côté récepteur.</li>')
s = s.replace(old_tp, new_tp, 1)

# révision
s = s.replace('<li>OAuth 2.1 et OIDC : flux autorisés, jetons, BFF, IDOR.</li>',
              '<li>Authentification des humains : mots de passe (Argon2id, NIST), MFA et passkeys, SSO, sessions, récupération de compte.</li><li>OAuth 2.1 et OIDC : rôles, flux autorisés et supprimés, les trois jetons, les sept points de validation d\'un JWT, BFF, Token Exchange, IDOR.</li>', 1)

# accroche du niveau
s = s.replace('zero trust et PKI, puis les référentiels de conformité', 'zero trust, authentification (OAuth 2.1, OpenID Connect, Keycloak) et PKI, puis les référentiels de conformité', 1)
p.write_text(s)
print('chapitre 41 enrichi :', s.count('<h3>41.'), 'sections')

# page d'accueil : description du niveau 7
ip = pathlib.Path('/mnt/user-data/outputs/devops-parcours-complet.html'); t = ip.read_text()
t = t.replace('supply chain Sigstore et SLSA, zero trust et PKI, conformité.', 'supply chain Sigstore et SLSA, zero trust, authentification (OAuth 2.1, OpenID Connect, Keycloak) et PKI, conformité.', 1)
ip.write_text(t); print('index ok')
