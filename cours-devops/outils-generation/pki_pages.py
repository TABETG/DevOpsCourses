"""Cours Java PKI, X.509, signature électronique, eIDAS/RGS. Usage : python3 pki_pages.py <dossier>"""
import sys, runpy, pathlib
g = runpy.run_path(pathlib.Path(__file__).with_name('front_gen.py'), run_name='front'); ch, page = g['ch'], g['page']
OSSL = "Tout en conteneur : <code>alias ossl='docker run --rm -v \"$PWD:/w\" -w /w alpine/openssl'</code>, <code>alias jdk='docker run --rm -v \"$PWD:/w\" -w /w eclipse-temurin:21-jdk'</code> (keytool = <code>jdk keytool</code>)."

PKI = [
ch("Cryptographie appliquée : chiffrer, hacher, signer", 'j',
 ["Chiffrement symétrique (AES) : une clé partagée, rapide, pour les données ; asymétrique (RSA, ECC) : une paire publique/privée, lent, pour échanger des clés et signer.", "Un hash (SHA-256) résume un contenu de façon irréversible et sensible au moindre bit ; ce n'est ni un chiffrement ni une signature.", "Une signature = hash du document chiffré avec la clé privée ; quiconque a la clé publique vérifie : intégrité + authenticité + non-répudiation."],
 ["Expliquer à un architecte la différence entre chiffrer, hacher et signer", "Choisir RSA ou ECC, AES-GCM, SHA-256/512 et leurs tailles", "Reproduire chaque opération avec OpenSSL en conteneur"],
 [("Les trois opérations", "", """CHIFFRER (confidentialité)          HACHER (empreinte)                SIGNER (authenticité + intégrité)
clair --AES(k)--> chiffré           doc --SHA-256--> h (32 octets)    doc --SHA-256--> h --RSA(privée)--> sig
chiffré --AES(k)--> clair           irréversible, déterministe        vérif : RSA(publique, sig) == SHA-256(doc) ?
asymétrique : chiffre avec la       même doc = même h, 1 bit change   seule la clé privée signe ; tout le monde vérifie
PUBLIQUE, déchiffre avec la PRIVÉE  = h totalement différent          non-répudiation : seul le détenteur a pu signer"""),
  ("Algorithmes et tailles", "RSA : 2048 bits minimum, 3072/4096 pour une CA ; lent, clés grosses, universel. ECC (P-256, P-384, Ed25519) : 256 bits ≈ RSA 3072, rapide, petit, standard moderne (eIDAS, TLS 1.3). AES-128/256 en mode GCM (authentifié) ; jamais ECB. SHA-256 par défaut, SHA-384/512 pour les CA et le qualifié ; SHA-1 et MD5 interdits pour les signatures (collisions). Chiffrement hybride : RSA/ECDH échange une clé AES qui chiffre les données (TLS, PKCS#7, S/MIME).", None),
  ("En pratique avec OpenSSL", OSSL, """ossl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:3072 -out priv.pem && ossl pkey -in priv.pem -pubout -out pub.pem
ossl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -out ec.pem
echo "contrat" > doc.txt && ossl dgst -sha256 doc.txt                                  # empreinte
ossl dgst -sha256 -sign priv.pem -out doc.sig doc.txt && ossl dgst -sha256 -verify pub.pem -signature doc.sig doc.txt   # Verified OK
ossl enc -aes-256-gcm -pbkdf2 -in doc.txt -out doc.enc                                # symétrique (démo ; en prod la clé vient d'un KMS)
ossl pkeyutl -encrypt -pubin -inkey pub.pem -in cle-aes.bin -out cle.enc             # hybride : la clé AES chiffrée par RSA""")],
 [("Chiffrer avec la clé privée revient-il à signer ?", "Mathématiquement proche en RSA (raw), mais non : une signature applique un hash puis un padding (PSS ou PKCS#1 v1.5) et un algorithme précis ; « chiffrer avec la privée » sans hash ni padding est cassable. On signe avec <code>Signature</code>, on chiffre avec <code>Cipher</code>."),
  ("Question d'entretien : pourquoi hacher avant de signer ?", "RSA ne signe qu'un bloc de la taille de la clé et est lent ; le hash ramène tout document à 32 octets et lie la signature à l'intégrité du contenu entier.")],
 ("Kit cryptographique", ["Générer RSA 3072 et EC P-256 ; hacher, signer, vérifier un fichier ; modifier un octet et re-vérifier.", "Chiffrement hybride d'un fichier de 100 Mo : mesurer AES seul contre RSA direct (impossible au-delà de la taille de clé).", "Tableau : opération → algorithme → taille → usage → ce qui l'interdit."],
  "Après modification d'un octet : <code>Verification failure</code>. RSA direct sur 100 Mo : erreur <code>data too large for key size</code> : c'est la démonstration du chiffrement hybride. Le tableau cite SHA-1 « interdit depuis 2017 (SHAttered) » et RSA 1024 « interdit RGS/ANSSI ».")),

ch("PKI : autorités, certificats, chaîne et cycle de vie", 'j',
 ["Une PKI relie une identité à une clé publique par un certificat signé par une autorité (CA) ; la confiance descend d'une racine hors ligne vers des intermédiaires en ligne puis les certificats finaux.", "Le demandeur génère sa clé privée (jamais transmise) et une CSR (clé publique + identité) ; la RA vérifie l'identité ; la CA signe ; le certificat vit, se renouvelle, se révoque, expire.", "La chaîne se vérifie de la feuille à la racine : chaque certificat est signé par le suivant, et la racine est dans le magasin de confiance."],
 ["Dessiner et expliquer une PKI d'entreprise à un architecte", "Décrire CSR, RA, CA, chaîne, révocation et cycle de vie", "Savoir où sont les clés privées à chaque étape et pourquoi"],
 [("Schéma d'une PKI d'entreprise", "", """                 ┌──────────────────────────┐
                 │  ROOT CA (hors ligne)     │  clé en HSM, cérémonie, 20 ans, signe uniquement les intermédiaires
                 └────────────┬─────────────┘
        ┌─────────────────────┼──────────────────────┐
┌───────┴────────┐   ┌────────┴─────────┐   ┌────────┴────────┐
│ CA Serveurs TLS│   │ CA Personnes     │   │ CA Signature    │   intermédiaires en ligne, 5–10 ans, clés en HSM
└───────┬────────┘   └────────┬─────────┘   └────────┬────────┘
        │                     │                      │
   RA : vérifie          RA : vérifie             RA : vérifie          RA = enregistrement (identité) ; CA = signature
   le contrôle DNS       l'agent (badge, RH)      la personne morale
        │                     │                      │
   cert serveur         cert agent (auth,        cert cachet /
   (1 an, SAN)          signature, chiffrement)  signature (3 ans)
        │                     │                      │
   CRL + OCSP  ←──────── publiés par chaque CA ────────→  vérifiés par les clients (navigateur, Java, TrustyServer)"""),
  ("Cycle de vie et flux CSR", "", """1. génération de la clé privée par le demandeur (fichier chiffré, HSM, carte)      → la privée ne quitte JAMAIS son support
2. CSR = clé publique + Subject + SAN + usages, signée par la privée (preuve de possession)   openssl req -new
3. RA : vérification (DNS, pièce d'identité, Kbis) ; approbation                       → politique de certification (CP/CPS)
4. CA : signe la CSR avec sa clé privée → certificat X.509, numéro de série, validité    openssl ca / x509 -req
5. publication (LDAP, HTTP AIA), installation (keystore, serveur, carte)
6. usage ; surveillance de l'expiration (alerte 30 j) ; renouvellement = nouvelle clé + nouvelle CSR (rekey) ou même clé (renew)
7. révocation (compromission, départ, changement) → CRL et OCSP ; expiration → fin naturelle, archivage pour vérifier les vieilles signatures"""),
  ("Ce qu'un architecte veut entendre", "Pourquoi une racine hors ligne (compromission = tout reconstruire) ; pourquoi plusieurs intermédiaires (séparation des usages, révocation ciblée) ; où sont les clés (HSM pour les CA et les cachets, cartes pour les agents, fichiers chiffrés pour les serveurs avec rotation courte) ; comment on vérifie (chaîne + validité + usage + révocation) ; ce qui se passe à l'expiration d'une intermédiaire (renouvellement anticipé, double publication).", None)],
 [("Une CSR contient-elle la clé privée ?", "Non : la clé publique, l'identité demandée et une signature par la privée qui prouve qu'on la détient. Envoyer sa clé privée à une CA est une erreur classique et grave."),
  ("Question d'entretien : différence entre RA et CA ?", "La RA vérifie l'identité et approuve (processus, humains, contrôles) ; la CA signe techniquement. Séparer les deux limite l'impact d'une erreur ou d'un compromis.")],
 ("PKI trois niveaux avec OpenSSL", ["Root CA (RSA 4096, 20 ans, <code>pathlen:1</code>) hors ligne (conteneur <code>--network none</code>), intermédiaire (10 ans, <code>pathlen:0</code>), CSR et certificat serveur avec SAN.", "Chaîne <code>fullchain.pem</code> ; vérification <code>openssl verify -CAfile root.pem -untrusted int.pem serveur.pem</code>.", "Révocation d'un certificat et génération de la CRL ; vérification avec <code>-crl_check</code>."],
  "<code>openssl req -x509 -newkey rsa:4096 -days 7300 -subj '/CN=MI Root CA/O=Ministere' -addext 'basicConstraints=critical,CA:TRUE,pathlen:1' -addext 'keyUsage=critical,keyCertSign,cRLSign'</code> ; l'intermédiaire par <code>openssl ca</code> avec une configuration <code>[v3_intermediate_ca]</code> ; révocation : <code>openssl ca -revoke serveur.pem</code>, <code>openssl ca -gencrl</code>, puis <code>openssl verify -crl_check -CRLfile crl.pem …</code> → <code>certificate revoked</code>. Piège attendu : le serveur signé par la racine directement échoue le <code>pathlen</code> si on tente d'en faire une CA.")),

ch("X.509 en détail et formats de fichiers", 'j',
 ["Un certificat X.509 v3 = TBSCertificate (version, série, signature alg, issuer, validité, subject, clé publique, extensions) + algorithme + signature de la CA.", "Les extensions décident de l'usage : Basic Constraints (CA ?), Key Usage, Extended Key Usage, SAN (le seul nom vérifié), AKI/SKI (chaînage), CRL DP, AIA (OCSP, CA issuers).", "PEM (base64 avec en-têtes) et DER (binaire) encodent la même chose ; CRT/CER sont des extensions de fichier ; PKCS#12 emballe clé + certificats ; PKCS#8 est le format de clé privée."],
 ["Lire un certificat champ par champ avec OpenSSL et Java", "Identifier une erreur d'extension (SAN absent, EKU faux, pathlen) à la lecture", "Convertir entre PEM, DER, PKCS#12, PKCS#8, JKS"],
 [("Lecture commentée", "", """ossl x509 -in serveur.pem -text -noout
Certificate:
    Data:
        Version: 3 (0x2)                                   ← v3 = extensions possibles ; v1 sans extension est suspect
        Serial Number: 4f:2a:…                             ← unique par CA, ≥ 64 bits aléatoires (CA/B Forum) ; identifie dans la CRL
        Signature Algorithm: sha256WithRSAEncryption       ← ce que la CA a utilisé ; sha1 = à refuser
        Issuer: C=FR, O=Ministere, CN=MI CA Serveurs      ← doit être égal au Subject du certificat parent
        Validity: Not Before: Sep 22 2026 / Not After: Sep 22 2027   ← UTC ; 398 j max pour du TLS public
        Subject: C=FR, O=Ministere, CN=api.interieur.gouv.fr         ← le CN n'est PLUS utilisé pour TLS : seul le SAN compte
        Subject Public Key Info: RSA 3072 bit / id-ecPublicKey P-256 ← la clé publique du sujet
        X509v3 extensions:
            Basic Constraints: critical, CA:FALSE            ← feuille ; CA:TRUE + pathlen sur les CA
            Key Usage: critical, Digital Signature, Key Encipherment   ← nonRepudiation (contentCommitment) pour la signature de documents
            Extended Key Usage: TLS Web Server Authentication          ← serverAuth / clientAuth / codeSigning / emailProtection / timeStamping / OCSPSigning
            Subject Alternative Name: DNS:api.interieur.gouv.fr, DNS:api      ← noms vérifiés par le client ; IP: possible
            Subject Key Identifier / Authority Key Identifier             ← empreintes de clé qui relient enfant → parent
            CRL Distribution Points: URI:http://pki.interieur.gouv.fr/ca-serveurs.crl
            Authority Information Access: OCSP - URI:http://ocsp.interieur.gouv.fr ; CA Issuers - URI:…/ca-serveurs.cer   ← permet de reconstruire la chaîne
            Certificate Policies: 1.2.250.1.xxx (OID de la politique, ex. RGS **)
    Signature Algorithm: sha256WithRSAEncryption ; Signature Value: …   ← vérifiable avec la clé publique de l'Issuer"""),
  ("Formats", "", """| Format   | Contenu                                      | Encodage | Extension usuelle | Usage                                         |
| PEM      | cert, clé, CSR, CRL (« -----BEGIN … -----») | base64   | .pem .crt .cer .key| Linux, OpenSSL, nginx, Java (PemReader BC)    |
| DER      | idem, binaire ASN.1                          | binaire  | .der .cer .crt    | Windows, Java CertificateFactory, cartes      |
| CRT/CER  | un certificat (PEM ou DER selon le fichier)  | l'un ou l'autre | .crt .cer  | l'extension ne dit pas l'encodage : `file x` |
| PKCS#7   | un ou plusieurs certs (chaîne), pas de clé    | PEM/DER  | .p7b .p7c         | livraison de chaîne par les CA                |
| PKCS#8   | clé privée seule (chiffrée ou non)           | PEM/DER  | .key .pem .pk8    | Java PKCS8EncodedKeySpec, PostgreSQL JDBC     |
| PKCS#12  | clé privée + cert + chaîne, chiffré, mdp     | binaire  | .p12 .pfx         | keystore Java/.NET, import navigateur, cartes |
| JKS      | keystore propriétaire Java (déprécié)        | binaire  | .jks              | anciens Java ; migrer vers PKCS12             |
ossl x509 -in c.pem -outform DER -out c.der ; ossl x509 -inform DER -in c.der -out c.pem
ossl pkcs12 -export -inkey priv.pem -in serveur.pem -certfile chain.pem -name api -out api.p12   # PEM → P12
ossl pkcs12 -in api.p12 -nokeys -out certs.pem ; ossl pkcs12 -in api.p12 -nocerts -nodes | ossl pkcs8 -topk8 -nocrypt -out key.pk8
ossl pkcs7 -print_certs -in chain.p7b -out chain.pem""")],
 [("Le CN est <code>api.interieur.gouv.fr</code> mais il n'y a pas de SAN : le navigateur accepte-t-il ?", "Non (Chrome depuis 2017, Java depuis 8u181 avec <code>jdk.tls.disableCN</code>) : <code>hostname mismatch</code>. Le SAN est obligatoire."),
  ("Question d'entretien : à quoi servent AKI et SKI ?", "À retrouver le parent sans comparer des DN : l'AKI de l'enfant = le SKI du parent. Java et OpenSSL s'en servent pour construire la chaîne, surtout quand une CA a plusieurs clés (renouvellement).")],
 ("Anatomie et conversions", ["Lire les trois certificats du TP précédent et remplir un tableau champ → valeur → rôle.", "Produire chaque format depuis le certificat serveur, vérifier avec <code>file</code> et relire ; importer le P12 dans un keystore Java.", "Fabriquer un certificat sans SAN et un avec EKU clientAuth seulement : constater les refus (curl, Java)."],
  "curl : <code>SSL: no alternative certificate subject name matches</code> pour le sans-SAN ; Java : <code>No subject alternative DNS name matching</code> ; EKU clientAuth sur un serveur : <code>ExtendedKeyUsage does not permit use for TLS server</code>. Le tableau note que l'extension de fichier ne prouve rien : <code>file c.cer</code> dit PEM ou DER.")),

ch("Keystore, truststore et keytool ; utilisation dans Spring Boot", 'c',
 ["Un keystore contient ce que <em>je</em> suis (clé privée + certificat, <code>PrivateKeyEntry</code>) ; un truststore contient ceux en qui je crois (<code>TrustedCertificateEntry</code>, des CA). Même format, rôles opposés.", "PKCS12 est le format par défaut depuis Java 9 ; JKS est déprécié ; l'alias nomme l'entrée ; le mot de passe du keystore et celui de la clé peuvent différer.", "Spring Boot : <code>server.ssl.*</code> et <code>spring.ssl.bundle.*</code> (Boot 3.1+) pour serveur, client et mTLS, avec rechargement à chaud."],
 ["Créer, lister, importer, exporter avec keytool ; convertir JKS → PKCS12", "Distinguer keystore/truststore et le truststore par défaut de la JVM (<code>cacerts</code>)", "Configurer Spring Boot avec des SSL bundles"],
 [("keytool en conteneur", "", """jdk keytool -genkeypair -alias api -keyalg EC -groupname secp256r1 -sigalg SHA256withECDSA -validity 365 -dname "CN=api.interieur.gouv.fr,O=Ministere,C=FR" -ext "SAN=dns:api.interieur.gouv.fr" -keystore api.p12 -storetype PKCS12 -storepass changeit
jdk keytool -certreq -alias api -keystore api.p12 -storepass changeit -file api.csr           # CSR à faire signer par la CA
jdk keytool -importcert -alias ca-serveurs -file int.pem -keystore api.p12 -storepass changeit -noprompt   # chaîne d'abord
jdk keytool -importcert -alias api -file api-signe.pem -keystore api.p12 -storepass changeit               # remplace l'auto-signé par le signé (même alias)
jdk keytool -list -v -keystore api.p12 -storepass changeit | grep -E 'Alias|Entry type|Owner|Issuer|Valid'
jdk keytool -exportcert -alias api -keystore api.p12 -storepass changeit -rfc -file api.pem
jdk keytool -importcert -alias mi-root -file root.pem -keystore truststore.p12 -storetype PKCS12 -storepass changeit -noprompt   # truststore : seulement des CA
jdk keytool -importkeystore -srckeystore old.jks -srcstoretype JKS -destkeystore new.p12 -deststoretype PKCS12   # migration
jdk keytool -list -cacerts -storepass changeit | wc -l    # le truststore par défaut ($JAVA_HOME/lib/security/cacerts) : ~140 racines publiques"""),
  ("Spring Boot : bundles", "", """spring:
  ssl:
    bundle:
      pem:
        serveur: { keystore: { certificate: classpath:api-chain.pem, private-key: classpath:api.pk8 }, reload-on-update: true }   # PEM direct, rechargé à chaud
      jks:
        client-mi: { keystore: { location: file:/secrets/client.p12, password: ${KS_PW}, type: PKCS12 }, truststore: { location: file:/secrets/truststore.p12, password: ${TS_PW} } }
server:
  ssl: { bundle: serveur }                                     # HTTPS avec le bundle (ou server.ssl.key-store/… en configuration classique)
  port: 8443
// client : RestClient.builder().apply(sslBundles.getBundle("client-mi").applyTo? → RestClientSsl
@Bean RestClient trustyClient(RestClient.Builder b, RestClientSsl ssl) { return b.baseUrl("https://trustykey.mi").apply(ssl.fromBundle("client-mi")).build(); }
// à ne jamais faire : TrustManager qui accepte tout (« trust all »), HostnameVerifier à true ; c'est un MITM garanti""")],
 [("Le truststore contient le certificat du serveur lui-même plutôt que sa CA. Problème ?", "Ça marche jusqu'au renouvellement : le nouveau certificat n'est plus reconnu. On fait confiance à la CA (ou à la racine), pas à une feuille, sauf pinning délibéré."),
  ("Question d'entretien : différence keystore/truststore ?", "Même conteneur (PKCS12), rôle différent : keystore = mon identité (clé privée + chaîne) ; truststore = les autorités que j'accepte. Un serveur TLS a un keystore ; un client a un truststore ; en mTLS les deux ont les deux.")],
 ("Keystores de CrisisShield", ["Keystore serveur signé par la CA du TP 2, truststore avec la racine ; Spring Boot en HTTPS avec bundle PEM rechargé.", "Client Spring qui appelle le serveur avec le truststore ; test : sans truststore → <code>PKIX path building failed</code>.", "Migration d'un JKS existant vers PKCS12 et audit <code>keytool -list</code> des entrées."],
  "curl : <code>curl --cacert root.pem https://localhost:8443/actuator/health</code> → 200 ; sans <code>--cacert</code> : <code>unable to get local issuer certificate</code>. Le client Java sans bundle : <code>sun.security.provider.certpath.SunCertPathBuilderException</code>. Rechargement : remplacer le PEM, pas de redémarrage, nouvelle date <code>notAfter</code> vue par <code>openssl s_client</code>.")),

ch("TLS, HTTPS et mTLS avec X.509", 'c',
 ["Le handshake TLS 1.3 : ClientHello (versions, suites, key share) → ServerHello + certificat + preuve de possession (CertificateVerify) + Finished → le client vérifie chaîne, nom, validité, révocation → clé de session par ECDHE → trafic chiffré AES-GCM.", "mTLS ajoute une CertificateRequest : le client présente son certificat et signe le transcript ; le serveur vérifie contre son truststore et peut mapper le sujet à une identité.", "Ce que le certificat garantit : l'identité du serveur (SAN) et l'échange de clé authentifié ; ce qu'il ne garantit pas : que le serveur est honnête ou que l'application est sûre."],
 ["Décrire le handshake et où intervient chaque champ X.509", "Configurer Spring Boot en HTTPS puis en mTLS et extraire l'identité du certificat client", "Diagnostiquer un handshake avec <code>openssl s_client</code> et <code>-Djavax.net.debug</code>"],
 [("Le handshake, pas à pas", "", """client                                              serveur
  │ ClientHello : TLS1.3, suites, SNI=api.mi, key_share (ECDHE)     │
  │──────────────────────────────────────────────────────────────>│
  │ ServerHello (suite, key_share) ─ secrets dérivés des deux côtés (ECDHE) : à partir d'ici tout est chiffré
  │ EncryptedExtensions ; [CertificateRequest si mTLS]              │
  │ Certificate : chaîne serveur (feuille + intermédiaires, PAS la racine)
  │ CertificateVerify : signature du transcript avec la clé privée du serveur  ← preuve de possession
  │ Finished                                                        │
  │<──────────────────────────────────────────────────────────────│
  │ vérifie : chaîne → racine du truststore ; SAN = SNI ; dates ; KU/EKU serverAuth ; révocation (OCSP stapling / CRL) ; signature CertificateVerify avec la clé publique du cert
  │ [Certificate client + CertificateVerify si mTLS] ; Finished    │
  │──────────────────────────────────────────────────────────────>│
  │ données applicatives chiffrées AES-256-GCM, clé de session éphémère (PFS : une clé privée volée plus tard ne déchiffre pas le passé)"""),
  ("Spring Boot mTLS", "", """server:
  ssl: { bundle: serveur, client-auth: need }     # need = obligatoire ; want = optionnel (utile pour une migration)
spring.ssl.bundle.pem.serveur: { keystore: { certificate: classpath:api-chain.pem, private-key: classpath:api.pk8 }, truststore: { certificate: classpath:ca-personnes.pem } }   # truststore = la CA qui émet les certificats clients
// identité depuis le certificat : Spring Security X.509
http.x509(x -> x.subjectPrincipalRegex("CN=(.*?)(?:,|$)").userDetailsService(agents));   // CN → utilisateur ; mieux : SAN otherName / UPN ou le numéro de série + issuer
// derrière un reverse proxy qui termine TLS : le proxy passe le cert dans un en-tête (X-SSL-Client-Cert, base64 DER) — à n'accepter que depuis le proxy (réseau) et à vérifier à nouveau
ossl s_client -connect localhost:8443 -cert agent.pem -key agent.key -CAfile root.pem -servername api.mi < /dev/null 2>&1 | grep -E 'Verify return|subject=|Acceptable client certificate CA'""")],
 [("Pourquoi le serveur n'envoie-t-il pas la racine dans sa chaîne ?", "La racine doit déjà être dans le truststore du client : c'est ce qui fonde la confiance. L'envoyer ne sert à rien (le client ne la croirait pas parce qu'elle est envoyée) et alourdit le handshake."),
  ("Question d'entretien : mTLS ou jeton JWT pour authentifier un service ?", "mTLS authentifie la machine/le service au niveau transport, sans secret partagé, avec révocation par PKI ; le JWT porte une identité applicative et des droits. Souvent les deux : mTLS entre services (SPIFFE/mesh), JWT pour l'utilisateur.")],
 ("HTTPS puis mTLS sur CrisisShield", ["HTTPS avec la chaîne du TP 2 ; <code>s_client</code> montre <code>Verify return code: 0</code> avec la racine.", "mTLS <code>client-auth: need</code> avec la CA Personnes ; certificat agent avec EKU clientAuth ; Spring Security X.509 mappe le CN.", "Trois échecs analysés : certificat client d'une autre CA, certificat client expiré, EKU serverAuth seulement."],
  "Sans certificat client : <code>curl: (56) … alert bad certificate</code> ; autre CA : côté serveur <code>Received fatal alert: unknown_ca</code> ou <code>PKIX path building failed</code> dans les logs Tomcat avec <code>javax.net.debug=ssl:handshake</code> ; expiré : <code>certificate_expired</code> ; l'identité apparaît dans <code>SecurityContext</code> : <code>CN=Alice Dupont</code>.")),

ch("Signature électronique : niveaux, formats, horodatage", 'c',
 ["Signer = hacher le document, chiffrer le hash avec la clé privée, emballer avec le certificat du signataire, l'heure et les attributs signés dans un format standard ; vérifier = recalculer, déchiffrer, comparer, et valider le certificat à la date de signature.", "Trois niveaux eIDAS : simple (n'importe quelle donnée liée), avancée (liée de façon unique au signataire, sous son contrôle exclusif, détecte toute modification), qualifiée (avancée + certificat qualifié + dispositif qualifié : valeur d'une signature manuscrite).", "Formats : CAdES (CMS, tout fichier, .p7s), XAdES (XML, enveloppée/enveloppante/détachée), PAdES (PDF, signature visible et incrémentale) ; les profils B/T/LT/LTA ajoutent horodatage et preuves de validation pour la longue durée."],
 ["Expliquer le flux de signature et de vérification avec ses attributs signés", "Choisir le format et le niveau selon le document et l'exigence juridique", "Comprendre l'horodatage (RFC 3161) et la conservation longue durée"],
 [("Flux et attributs", "", """document ──SHA-256──> h ──┐
attributs signés : h, date, OID de politique, empreinte du certificat (ESS signing-certificate-v2) ──SHA-256──> h' ──RSA/ECDSA(privée)──> signature
conteneur (CMS/XAdES/PAdES) = signature + certificat(s) du signataire + attributs + [jeton d'horodatage TSA] + [OCSP/CRL au moment de la signature]
vérification : 1) recalculer h et h' 2) vérifier la signature avec la clé publique du cert inclus 3) valider le cert (chaîne, KU nonRepudiation, politique) À LA DATE prouvée par l'horodatage 4) contrôler la révocation à cette date"""),
  ("Formats et profils", "", """| Format | Support        | Où est la signature                 | Usage typique                                   |
| CAdES  | tout fichier   | .p7s détaché ou enveloppant (CMS)   | archives, échanges B2B, fichiers signés en lot   |
| XAdES  | XML            | enveloppée (dans le XML), enveloppante, détachée | flux administratifs, factures, SAML |
| PAdES  | PDF            | incrémentale dans le PDF, visible    | contrats, actes, documents pour les citoyens    |
| JAdES  | JSON (JWS)     | compact ou JSON                     | API, eIDAS 2 / wallet                           |
Profils : -B (baseline : signature + cert) ; -T (+ horodatage TSA) ; -LT (+ chaîne + OCSP/CRL incluses : vérifiable hors ligne) ; -LTA (+ horodatage d'archive périodique : vérifiable dans 30 ans malgré les algorithmes affaiblis)
Horodatage RFC 3161 : hash de la signature envoyé à une TSA → jeton signé (heure certaine) ; ossl ts -query -data sig.bin -sha256 | curl --data-binary @- -H 'Content-Type: application/timestamp-query' https://tsa… > ts.tsr"""),
  ("En pratique : DSS", "La bibliothèque de référence en Java est DSS (Digital Signature Service, Commission européenne) : elle produit et valide CAdES/XAdES/PAdES/JAdES à tous les niveaux, gère TSA, OCSP/CRL, la liste de confiance européenne (LOTL/TSL) et génère les rapports de validation (ETSI). TrustySign-type = un service qui encapsule DSS (ou équivalent) avec un HSM pour les clés de cachet.",
"""// DSS : signature PAdES-B-T
PAdESService service = new PAdESService(new CommonCertificateVerifier()); service.setTspSource(new OnlineTSPSource("https://tsa.example/tsr"));
PAdESSignatureParameters p = new PAdESSignatureParameters(); p.setSignatureLevel(SignatureLevel.PAdES_BASELINE_T); p.setDigestAlgorithm(DigestAlgorithm.SHA256); p.setSigningCertificate(token.getKeys().get(0).getCertificate()); p.setCertificateChain(...);
ToBeSigned tbs = service.getDataToSign(doc, p); SignatureValue sv = token.sign(tbs, DigestAlgorithm.SHA256, key);   // token = Pkcs12SignatureToken ou Pkcs11SignatureToken (HSM)
DSSDocument signed = service.signDocument(doc, p, sv);""")],
 [("Une signature valide aujourd'hui peut-elle devenir invalide ?", "Oui si on ne prouve pas la date : le certificat expire, l'algorithme s'affaiblit, la CRL n'est plus disponible. D'où -T (heure certaine), -LT (preuves incluses), -LTA (ré-horodatage). Une signature -B seule n'a pas d'avenir."),
  ("Question d'entretien : cachet contre signature ?", "Signature = personne physique (engagement) ; cachet = personne morale/serveur (origine et intégrité, automatisable). Même technique, certificats et effets juridiques différents.")],
 ("Signer et vérifier trois formats", ["CAdES détaché avec OpenSSL (<code>cms -sign</code>) puis vérification ; XAdES et PAdES avec DSS en Java (Docker), niveau -B puis -T avec une TSA de test.", "Modifier un octet du PDF signé et vérifier : rapport DSS « signature invalide » ; vérifier une signature dont le certificat est expiré depuis, avec et sans horodatage.", "Tableau : format → document → niveau eIDAS visé → profil → où sont les preuves."],
  "<code>ossl cms -sign -signer agent.pem -inkey agent.key -certfile int.pem -detached -outform DER -binary -in doc.pdf -out doc.p7s</code> ; <code>ossl cms -verify -CAfile root.pem -content doc.pdf -inform DER -in doc.p7s</code> → <code>Verification successful</code>. DSS : le rapport simple donne <code>TOTAL_PASSED</code> pour -T même après expiration du certificat (validation à la date du jeton), <code>INDETERMINATE / OUT_OF_BOUNDS_NO_POE</code> pour -B.")),

ch("Java : java.security, javax.crypto et Bouncy Castle", 'c',
 ["Le JDK fournit tout le nécessaire pour hacher, signer, vérifier, lire des certificats et des keystores (<code>MessageDigest</code>, <code>Signature</code>, <code>KeyFactory</code>, <code>CertificateFactory</code>, <code>KeyStore</code>, <code>Cipher</code>).", "Bouncy Castle ajoute ce que le JDK n'a pas : génération et signature de certificats, CSR (PKCS#10), lecture PEM, CMS/PKCS#7, OCSP, TSP, courbes et algorithmes supplémentaires.", "Règles : ne jamais réimplémenter un algorithme, nommer explicitement l'algorithme et le padding, utiliser <code>SecureRandom</code>, ne jamais logger une clé."],
 ["Écrire le code de base : clés, hash, signature, certificat, PKCS12", "Utiliser Bouncy Castle pour CSR, certificat signé, lecture PEM", "Connaître les pièges (Signature sans hash, PKCS#1 v1.5 contre PSS, charset)"],
 [("JDK : signer et vérifier", "", """// hash
byte[] h = MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(doc));           // toujours nommer l'algorithme ; SHA-1/MD5 jamais pour signer
// paire de clés
KeyPairGenerator kpg = KeyPairGenerator.getInstance("EC"); kpg.initialize(new ECGenParameterSpec("secp256r1"), SecureRandom.getInstanceStrong()); KeyPair kp = kpg.generateKeyPair();
// clé privée PKCS#8 depuis un fichier PEM (sans en-têtes) / DER
byte[] der = Base64.getMimeDecoder().decode(pemBody); PrivateKey pk = KeyFactory.getInstance("EC").generatePrivate(new PKCS8EncodedKeySpec(der));
// certificat X.509
X509Certificate cert = (X509Certificate) CertificateFactory.getInstance("X.509").generateCertificate(Files.newInputStream(pem));   // lit PEM ou DER
cert.checkValidity();                                                       // CertificateExpiredException / NotYetValid
// signature : l'algorithme inclut le hash et le padding
Signature s = Signature.getInstance("SHA256withECDSA"); s.initSign(pk); s.update(data); byte[] sig = s.sign();       // RSA : "SHA256withRSA" (PKCS#1 v1.5) ou "RSASSA-PSS" avec PSSParameterSpec (préféré)
Signature v = Signature.getInstance("SHA256withECDSA"); v.initVerify(cert.getPublicKey()); v.update(data); boolean ok = v.verify(sig);
// PKCS12
KeyStore ks = KeyStore.getInstance("PKCS12"); ks.load(Files.newInputStream(p12), pw);       // pw en char[], effacé après (Arrays.fill)
PrivateKey key = (PrivateKey) ks.getKey("api", pw); Certificate[] chain = ks.getCertificateChain("api");
// AES-GCM (si vraiment besoin de chiffrer soi-même) : Cipher c = Cipher.getInstance("AES/GCM/NoPadding"); c.init(ENCRYPT_MODE, k, new GCMParameterSpec(128, iv12octetsAleatoire)); … jamais réutiliser un IV"""),
  ("Bouncy Castle : CSR et certificat", "", """<dependency><groupId>org.bouncycastle</groupId><artifactId>bcpkix-jdk18on</artifactId><version>1.79</version></dependency>   <!-- bcprov (provider) + bcpkix (PKI) + bcutil -->
Security.addProvider(new BouncyCastleProvider());   // ou en tant que provider JCA dans java.security ; en mode FIPS : bc-fips
// CSR PKCS#10
PKCS10CertificationRequest csr = new JcaPKCS10CertificationRequestBuilder(new X500Name("CN=api.mi,O=Ministere,C=FR"), kp.getPublic())
  .addAttribute(PKCSObjectIdentifiers.pkcs_9_at_extensionRequest, new Extensions(new Extension(Extension.subjectAlternativeName, false, new GeneralNames(new GeneralName(GeneralName.dNSName, "api.mi")).getEncoded())))
  .build(new JcaContentSignerBuilder("SHA256withECDSA").build(kp.getPrivate()));
// certificat signé par une CA (clé caKey, cert caCert)
X509v3CertificateBuilder b = new JcaX509v3CertificateBuilder(caCert, new BigInteger(64, rnd), notBefore, notAfter, csr.getSubject(), csr.getSubjectPublicKeyInfo());
JcaX509ExtensionUtils u = new JcaX509ExtensionUtils();
b.addExtension(Extension.basicConstraints, true, new BasicConstraints(false)).addExtension(Extension.keyUsage, true, new KeyUsage(KeyUsage.digitalSignature | KeyUsage.keyEncipherment))
 .addExtension(Extension.extendedKeyUsage, false, new ExtendedKeyUsage(KeyPurposeId.id_kp_serverAuth)).addExtension(Extension.subjectAlternativeName, false, sanFromCsr)
 .addExtension(Extension.subjectKeyIdentifier, false, u.createSubjectKeyIdentifier(csr.getSubjectPublicKeyInfo())).addExtension(Extension.authorityKeyIdentifier, false, u.createAuthorityKeyIdentifier(caCert));
X509Certificate leaf = new JcaX509CertificateConverter().getCertificate(b.build(new JcaContentSignerBuilder("SHA256withRSA").build(caKey)));
// lecture PEM et CMS
Object o = new PEMParser(new FileReader("cert.pem")).readObject();   // X509CertificateHolder, PEMKeyPair, PrivateKeyInfo…
CMSSignedData cms = new CMSSignedDataGenerator()…;  // signature CAdES-like ; OCSP : OCSPReqBuilder ; TSP : TimeStampRequestGenerator""")],
 [("<code>Signature.getInstance(\"SHA256withRSA\")</code> ou <code>\"RSASSA-PSS\"</code> ?", "PSS est le padding probabiliste recommandé (RGS, eIDAS, TLS 1.3) ; PKCS#1 v1.5 reste répandu pour la compatibilité. Le choix doit être explicite et le même des deux côtés."),
  ("Question d'entretien : pourquoi Bouncy Castle si le JDK a JCA ?", "JCA sait utiliser des clés et certificats, pas en fabriquer (pas de CSR, pas d'émission, pas de CMS/OCSP/TSP dans l'API publique). BC comble ces trous et sert de provider alternatif (algorithmes, FIPS).")],
 ("Bibliothèque <code>crisis-crypto</code>", ["Module Java 21 (Maven en conteneur) : hash, signature RSA-PSS et ECDSA, lecture PKCS#8/X.509/PKCS12, tests JUnit avec des vecteurs.", "Mini CA en Bouncy Castle : racine, intermédiaire, émission depuis une CSR, export PEM/PKCS12 ; vérification croisée avec OpenSSL.", "Piège documenté : signature de <code>String</code> sans charset explicite, IV réutilisé, mot de passe en <code>String</code>."],
  "<code>docker run --rm -v \"$PWD:/w\" -w /w -v m2:/root/.m2 maven:3.9-eclipse-temurin-21 mvn -q verify</code>. Vérification croisée : le certificat émis par BC passe <code>openssl verify</code> et <code>openssl x509 -text</code> montre SKI/AKI cohérents ; la signature Java se vérifie avec <code>openssl dgst -verify</code> (PSS : <code>-sigopt rsa_padding_mode:pss</code>).")),

ch("Application Spring Boot : /sign, /verify, /certificate", 's',
 ["Architecture : Controller (HTTP, validation) → SignatureService (signer/vérifier) et CertificateService (charger, exposer, valider) → Configuration (keystore, provider, propriétés) ; le keystore vient d'un secret monté, jamais du classpath en production.", "La signature renvoyée est un conteneur (CMS ou JWS) avec le certificat, pas une signature brute : le vérificateur a besoin de tout.", "Journalisation d'audit : qui a signé quoi, quand, avec quel certificat (numéro de série), sans jamais logger le document ni la clé."],
 ["Structurer et coder l'application complète", "Exposer les informations d'un certificat en JSON et signer/vérifier en CMS", "Sécuriser les entrées et l'audit"],
 [("Configuration et services", "", """// application.yml
crisis.signature: { keystore: file:/secrets/signer.p12, keystore-password: ${SIGNER_KS_PW}, alias: cachet, truststore: file:/secrets/truststore.p12, truststore-password: ${TS_PW}, algorithm: SHA256withRSAandMGF1 }
@ConfigurationProperties("crisis.signature") public record SignatureProps(Resource keystore, char[] keystorePassword, String alias, Resource truststore, char[] truststorePassword, String algorithm) {}
@Configuration @EnableConfigurationProperties(SignatureProps.class) class CryptoConfig {
  @Bean KeyStore signerKeyStore(SignatureProps p) throws Exception { var ks = KeyStore.getInstance("PKCS12"); try (var in = p.keystore().getInputStream()) { ks.load(in, p.keystorePassword()); } return ks; }
  @Bean KeyStore trustStore(SignatureProps p) throws Exception { … }
  @Bean BouncyCastleProvider bc() { var bc = new BouncyCastleProvider(); Security.addProvider(bc); return bc; }
}
@Service public class CertificateService {
  private final X509Certificate cert; private final List<X509Certificate> chain; private final KeyStore trust;
  CertificateService(KeyStore ks, KeyStore trust, SignatureProps p) throws Exception { chain = Arrays.stream(ks.getCertificateChain(p.alias())).map(X509Certificate.class::cast).toList(); cert = chain.get(0); this.trust = trust; }
  public CertificateInfo info() { return new CertificateInfo(cert.getSubjectX500Principal().getName(), cert.getIssuerX500Principal().getName(), cert.getSerialNumber().toString(16), cert.getNotBefore(), cert.getNotAfter(), cert.getSigAlgName(), sans(cert), keyUsage(cert), Duration.between(Instant.now(), cert.getNotAfter().toInstant()).toDays()); }
  public void validate(X509Certificate c, Date at) throws GeneralSecurityException { /* chapitre suivant : PKIX + révocation */ }
}
@Service public class SignatureService {
  private final PrivateKey key; private final CertificateService certs; private final AuditLog audit;
  public byte[] sign(byte[] document, String principal) throws Exception {
    var gen = new CMSSignedDataGenerator();
    var signer = new JcaContentSignerBuilder("SHA256withRSAandMGF1").setProvider("BC").build(key);
    gen.addSignerInfoGenerator(new JcaSignerInfoGeneratorBuilder(new JcaDigestCalculatorProviderBuilder().build()).build(signer, certs.cert()));
    gen.addCertificates(new JcaCertStore(certs.chain()));
    byte[] cms = gen.generate(new CMSProcessableByteArray(document), false).getEncoded();    // false = détaché : le document n'est pas dans le conteneur
    audit.signed(principal, certs.cert().getSerialNumber(), sha256Hex(document)); return cms;
  }
  public VerifyResult verify(byte[] document, byte[] cms) throws Exception {
    var sd = new CMSSignedData(new CMSProcessableByteArray(document), cms);
    var certStore = sd.getCertificates();
    for (SignerInformation si : sd.getSignerInfos().getSigners()) {
      var holder = (X509CertificateHolder) certStore.getMatches(si.getSID()).iterator().next();
      var c = new JcaX509CertificateConverter().getCertificate(holder);
      boolean sigOk = si.verify(new JcaSimpleSignerInfoVerifierBuilder().setProvider("BC").build(c));   // vérifie hash + signature + attributs signés
      Date signingTime = signingTime(si).orElse(new Date());
      certs.validate(c, signingTime);                                                                    // chaîne, usage, révocation à la date
      return new VerifyResult(sigOk, c.getSubjectX500Principal().getName(), c.getSerialNumber().toString(16), signingTime);
    }
    throw new IllegalArgumentException("aucun signataire");
  }
}
@RestController @RequestMapping("/api") class SignatureController {
  @PostMapping(value = "/sign", consumes = MULTIPART_FORM_DATA_VALUE, produces = "application/pkcs7-signature") byte[] sign(@RequestParam MultipartFile document, Authentication auth) throws Exception { limit(document, 20_000_000); return signatureService.sign(document.getBytes(), auth.getName()); }
  @PostMapping(value = "/verify", consumes = MULTIPART_FORM_DATA_VALUE) VerifyResult verify(@RequestParam MultipartFile document, @RequestParam MultipartFile signature) throws Exception { return signatureService.verify(document.getBytes(), signature.getBytes()); }
  @GetMapping("/certificate") CertificateInfo certificate() { return certificateService.info(); }
  @ExceptionHandler({ CMSException.class, GeneralSecurityException.class }) ProblemDetail bad(Exception e) { return ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST, "signature ou certificat invalide"); }   // jamais la stack trace
}""")],
 [("Pourquoi une signature CMS détachée plutôt qu'un simple <code>byte[]</code> de signature ?", "Le CMS transporte le certificat, la chaîne, l'algorithme, l'heure et les attributs signés : le vérificateur n'a pas besoin de connaître le signataire à l'avance, et le format est interopérable (OpenSSL, DSS, Acrobat)."),
  ("Question d'entretien : que journaliser lors d'une signature ?", "L'identité appelante, l'empreinte du document, le numéro de série et l'issuer du certificat, l'heure, le résultat ; jamais le document ni la clé ni le mot de passe. Journal inaltérable (append-only, horodaté).")],
 ("Service de signature CrisisShield", ["Application complète (Controller/Service/Config), keystore monté par secret, audit en JSON, tests Testcontainers avec un keystore de test.", "Vérification croisée : signature vérifiée par <code>openssl cms -verify</code> ; signature OpenSSL vérifiée par l'API.", "Cas de test : document modifié, signature d'un certificat inconnu, certificat expiré (horloge simulée), clé absente au démarrage (échec rapide)."],
  "Attendu : <code>POST /sign</code> renvoie un <code>.p7s</code> vérifiable par OpenSSL ; <code>/verify</code> avec un document modifié → <code>valid: false</code> ; certificat hors truststore → 400 « chaîne non reconnue » ; au démarrage sans keystore, l'application refuse de démarrer (<code>Fail-fast</code>) plutôt que de servir des 500. <code>/certificate</code> renvoie <code>daysRemaining</code> alimentant une alerte.")),

ch("Valider un certificat : chaîne, dates, usages, CRL, OCSP", 's',
 ["Valider = construire une chaîne jusqu'à une ancre de confiance, vérifier chaque signature, les dates, les contraintes (BasicConstraints, pathlen, name constraints), les usages, les politiques, puis la révocation.", "CRL : liste signée périodique, complète mais lourde et en retard ; OCSP : question/réponse en ligne par numéro de série, à jour mais dépend d'un service (et fuit qui consulte quoi) ; OCSP stapling : le serveur joint une réponse fraîche.", "En Java : <code>CertPathValidator</code> PKIX avec <code>PKIXRevocationChecker</code> ; les propriétés <code>com.sun.security.enableCRLDP</code> et <code>ocsp.enable</code> ; savoir ce qui est vérifié et ce qui ne l'est pas par défaut."],
 ["Implémenter la validation complète en Java avec révocation", "Configurer et tester CRL et OCSP (répondeur OpenSSL) et le stapling", "Choisir une politique de révocation (soft-fail contre hard-fail) et la justifier"],
 [("Validation PKIX en Java", "", """public void validate(X509Certificate leaf, List<X509Certificate> intermediates, KeyStore trust, Date at) throws GeneralSecurityException {
  var cf = CertificateFactory.getInstance("X.509");
  var path = cf.generateCertPath(Stream.concat(Stream.of(leaf), intermediates.stream()).toList());          // feuille d'abord
  var params = new PKIXParameters(trust);                                                                     // ancres = truststore
  params.setDate(at);                                                                                         // validation à la date de signature (horodatage)
  var rc = (PKIXRevocationChecker) CertPathValidator.getInstance("PKIX").getRevocationChecker();
  rc.setOptions(EnumSet.of(PKIXRevocationChecker.Option.PREFER_CRLS));                                        // OCSP d'abord par défaut ; SOFT_FAIL pour tolérer un répondeur injoignable (à décider !)
  params.addCertPathChecker(rc); params.setRevocationEnabled(true);
  var result = (PKIXCertPathValidatorResult) CertPathValidator.getInstance("PKIX").validate(path, params);  // lève CertPathValidatorException avec reason : EXPIRED, REVOKED, NO_TRUST_ANCHOR, INVALID_SIGNATURE, UNDETERMINED_REVOCATION_STATUS…
  if (!leaf.getKeyUsage()[1]) throw new CertificateException("nonRepudiation requis pour signer");            // KU bit 1 = contentCommitment
  if (!Optional.ofNullable(leaf.getExtendedKeyUsage()).orElse(List.of()).contains("1.3.6.1.5.5.7.3.4")) …       // EKU attendu selon l'usage
}
// propriétés JVM utiles : -Dcom.sun.security.enableCRLDP=true -Docsp.enable=true -Dcom.sun.security.ocsp.timeout=5 ; Security.setProperty("ocsp.responderURL", …) pour forcer un répondeur"""),
  ("CRL, OCSP, stapling avec OpenSSL", "", """ossl ca -config ca.cnf -gencrl -out crl.pem ; ossl crl -in crl.pem -text -noout | head          # Next Update = date limite de validité de la CRL
ossl verify -CAfile root.pem -untrusted int.pem -crl_check -CRLfile crl.pem serveur.pem            # error 23 : certificate revoked
ossl ocsp -index index.txt -CA int.pem -rsigner ocsp.pem -rkey ocsp.key -port 2560 -text           # répondeur de test (cert avec EKU OCSPSigning)
ossl ocsp -issuer int.pem -cert serveur.pem -url http://localhost:2560 -CAfile root.pem            # Response verify OK ; serveur.pem: good | revoked (Reason: keyCompromise)
# stapling : nginx ssl_stapling on ; Spring Boot/Tomcat : jdk.tls.server.enableStatusRequestExtension=true ; vérifier : ossl s_client -status -connect … | grep -A3 'OCSP Response Status'"""),
  ("Politique de révocation", "Hard-fail (répondeur injoignable = refus) est correct pour la signature et les accès sensibles, coûteux en disponibilité ; soft-fail (injoignable = accepter, journaliser) est la pratique des navigateurs pour le TLS public. Entre les deux : OCSP stapling (le serveur porte la preuve), CRL en cache avec date de fraîcheur, court délai de vie des certificats (moins besoin de révoquer). Le choix est documenté dans la politique de validation et testé.", None)],
 [("Java vérifie-t-il la révocation par défaut ?", "Non : <code>PKIXParameters.setRevocationEnabled</code> vaut true mais sans <code>enableCRLDP</code> ni <code>ocsp.enable</code>, aucune source n'est consultée et la validation échoue (<code>UNDETERMINED_REVOCATION_STATUS</code>) ou, pour TLS (<code>SSLContext</code> par défaut), la révocation n'est simplement pas vérifiée. Il faut le configurer explicitement."),
  ("Question d'entretien : CRL ou OCSP ?", "CRL : hors ligne, cache, mais volumineuse et publiée toutes les X heures. OCSP : temps réel, léger, mais dépendance et vie privée. Stapling combine : réponse OCSP fraîche servie par le serveur. Les certificats courts (24 h–90 j) réduisent le besoin des deux.")],
 ("Validateur complet", ["<code>CertificateService.validate</code> avec PKIX, date, KU/EKU, et révocation CRL puis OCSP (répondeur OpenSSL en conteneur).", "Tests : expiré, révoqué (CRL), révoqué (OCSP), chaîne incomplète, ancre absente, répondeur coupé en hard-fail et soft-fail.", "Stapling activé sur le serveur HTTPS du TP 5 et vérifié avec <code>s_client -status</code>."],
  "Chaque cas produit une <code>CertPathValidatorException</code> avec une <code>reason</code> différente, mappée sur un code métier (<code>CERT_EXPIRED</code>, <code>CERT_REVOKED</code>, <code>CHAIN_INCOMPLETE</code>, <code>REVOCATION_UNKNOWN</code>) ; en soft-fail le répondeur coupé donne <code>valid</code> + avertissement journalisé ; en hard-fail : refus. Le stapling montre <code>OCSP Response Status: successful</code>.")),

ch("eIDAS, eIDAS 2, RGS : ce qu'un développeur doit savoir", 's',
 ["eIDAS (règlement 910/2014) : cadre européen des services de confiance ; trois niveaux de signature et de cachet ; horodatage qualifié ; certificats qualifiés délivrés par des QTSP audités et listés dans les listes de confiance nationales (TSL) agrégées (LOTL) ; effet juridique de la signature qualifiée = manuscrite dans toute l'UE.", "eIDAS 2 (2024) : portefeuille européen d'identité numérique (EUDI Wallet), attestations électroniques d'attributs, nouveaux services (archivage, registres), signature qualifiée à distance depuis le wallet ; formats JAdES/JWS, SD-JWT, OpenID4VP.", "RGS (Référentiel Général de Sécurité, ANSSI) : obligations des administrations françaises ; niveaux * / ** / *** pour authentification, signature, confidentialité, horodatage ; certificats RGS délivrés par des PSCE qualifiés ; convergence avec eIDAS (RGS ** ≈ avancée avec certificat qualifié, RGS *** ≈ qualifiée)."],
 ["Expliquer eIDAS et RGS en termes simples puis techniques", "Savoir ce que change eIDAS 2 pour une application", "Traduire une exigence réglementaire en choix techniques (certificat, format, niveau, TSA, validation)"],
 [("Ce que ça change dans le code", "", """| Exigence                       | Traduction technique                                                                      |
| signature avancée              | certificat personnel (KU nonRepudiation), clé sous contrôle exclusif (carte, HSM, wallet), format AdES, horodatage                    |
| signature qualifiée            | + certificat qualifié (QcStatements : id-etsi-qcs-QcCompliance, QcSSCD) + dispositif qualifié (QSCD) + QTSP dans la LOTL              |
| cachet (serveur)               | certificat de cachet (personne morale), clé en HSM, service automatisé (TrustySign-type), cachet qualifié pour les actes             |
| vérification                   | validation ETSI EN 319 102 (DSS) : LOTL/TSL pour reconnaître les QTSP, rapport de validation, conservation des preuves (-LT/-LTA)   |
| horodatage qualifié            | TSA qualifiée (RFC 3161), jeton conservé ; en France, prestataires qualifiés RGS/eIDAS                                              |
| RGS * / ** / ***               | politique de certification (OID), longueur de clés (RSA ≥ 2048/3072, ECC ≥ 256), SHA-256+, dispositif matériel à partir de **, face-à-face pour *** |
| authentification RGS           | certificat d'authentification (EKU clientAuth), mTLS ou signature de challenge ; interdiction des mots de passe seuls au niveau **   |
QcStatements dans un certificat : ossl x509 -in q.pem -text | grep -A5 'qcStatements' ; DSS : CertificateWrapper.isQualified() via la TSL"""),
  ("Dans une plateforme ministérielle", "L'application métier ne fait pas de cryptographie : elle appelle un service de signature (TrustySign-type) qui utilise les clés d'un HSM (TrustyKey-type) sous une CA interne ou un QTSP ; les documents pour les citoyens sont en PAdES-LTA avec cachet qualifié ; les échanges inter-administrations en XAdES ; les agents s'authentifient par carte (certificat RGS **) ; la validation passe par un service (TrustyServer-type) qui maintient les listes de confiance et journalise. Les exigences se lisent dans la PSSI, le RGS et le contrat de la CA (PC/DPC).", None)],
 [("Une signature avancée avec un certificat non qualifié a-t-elle une valeur juridique ?", "Oui : elle est recevable et sa validité s'apprécie au cas par cas (preuve à apporter). Seule la qualifiée a l'équivalence automatique avec la manuscrite. Pour un acte administratif engageant, on vise qualifiée ou avancée avec certificat qualifié (RGS **)."),
  ("Question d'entretien : comment savoir qu'un certificat est qualifié ?", "Il porte des QcStatements (QcCompliance, QcSSCD, QcType) et est émis par une CA listée comme qualifiée dans la TSL du pays (vérifiée via la LOTL). Le certificat seul ne suffit pas : la liste de confiance fait foi.")],
 ("Fiche réglementaire du service de signature", ["Pour trois cas d'usage (acte administratif au citoyen, échange inter-ministères, authentification d'un agent) : niveau eIDAS/RGS visé, type de certificat, dispositif, format, profil, TSA, validation.", "Lecture d'un certificat qualifié réel (téléchargé d'un QTSP) : QcStatements, politique, chaîne jusqu'à la TSL.", "Validation DSS d'une signature qualifiée d'exemple avec la LOTL : rapport ETSI et niveau reconnu."],
  "Le rapport DSS indique <code>QESig</code> (signature électronique qualifiée) ou <code>AdESig-QC</code> selon la TSL ; la fiche explique qu'un agent s'authentifie en RGS ** par carte + mTLS, que l'acte est un cachet qualifié PAdES-LTA, et que l'échange XAdES-T suffit en interne.")),

ch("Architecture réelle : application métier, TrustySign, TrustyKey, HSM, PKI", 'e',
 ["Séparer signer (service de signature : formats, politiques, horodatage, audit) de détenir les clés (service de clés : HSM, PKCS#11, contrôle d'accès, journal) de valider (service de validation : listes de confiance, révocation, rapports) : trois composants, trois surfaces d'attaque.", "Une clé privée de cachet ou de CA ne doit pas être un fichier : un HSM la génère, la garde, signe à l'intérieur, journalise, et ne l'exporte jamais ; Java y accède par PKCS#11 (SunPKCS11) ou l'API du fournisseur.", "Autour : API REST authentifiées (mTLS + jeton), base pour les métadonnées (jamais les clés), journal d'audit inaltérable, gestion du cycle de vie des certificats (inventaire, renouvellement, révocation) automatisée."],
 ["Décrire le rôle de chaque composant et les flux entre eux", "Expliquer PKCS#11 et l'accès Java à un HSM", "Concevoir la gestion du cycle de vie et l'audit à l'échelle d'un ministère"],
 [("Schéma et flux", "", """Application métier (Spring Boot)                  ┌────────────────┐
  │ POST /sign (doc, politique)  mTLS + JWT        │  Base métadonnées│ ← qui, quoi, quand, série, empreinte ; jamais les clés
  ▼                                                └────────────────┘
TrustySign  (service de signature)  ────── journal d'audit (append-only, horodaté, exporté SIEM)
  │ construit CAdES/XAdES/PAdES, attributs, appelle la TSA, assemble les preuves (-LT/-LTA)
  │ « signe ce hash avec la clé cachet-actes »  (mTLS, autorisation par politique)
  ▼
TrustyKey   (service de clés)       ────── contrôle d'accès par clé, quotas, journal, double approbation pour les opérations sensibles
  │ PKCS#11 (session, login, C_Sign)
  ▼
HSM (matériel, FIPS 140-3 / CC EAL4+ : Thales Luna, Entrust nShield, Utimaco ; cloud : CloudHSM, Key Vault HSM ; test : SoftHSM2)
  clés générées et utilisées à l'intérieur ; sauvegarde par cartes de quorum (k parmi n) ; réplication entre HSM
PKI / CA (EJBCA, Microsoft ADCS, CA d'un QTSP) : émet les certificats de cachet, d'agents, de serveurs ; publie CRL/OCSP ; TrustyServer-type valide (LOTL/TSL, révocation) et sert d'autorité de validation
Cycle de vie : inventaire (base + scan), alerte J-30, renouvellement automatisé (CSR générée dans le HSM, signée par la CA, nouveau cert déployé, ancien conservé pour vérifier), révocation en un appel (CA API) + propagation CRL/OCSP + invalidation des sessions"""),
  ("PKCS#11 en Java", "", """# pkcs11.cfg
name = LunaHSM
library = /usr/lib/libCryptoki2_64.so       # SoftHSM2 pour le labo : /usr/lib/softhsm/libsofthsm2.so
slot = 0
// chargement du provider
Provider p = Security.getProvider("SunPKCS11").configure("/etc/pkcs11.cfg"); Security.addProvider(p);
KeyStore ks = KeyStore.getInstance("PKCS11", p); ks.load(null, pin);                     // le « keystore » est le HSM ; la clé privée est une référence (handle), pas des octets
PrivateKey key = (PrivateKey) ks.getKey("cachet-actes", null);                          // key.getEncoded() == null : non exportable
Signature s = Signature.getInstance("SHA256withRSA", p); s.initSign(key); s.update(hash); byte[] sig = s.sign();   // la signature est calculée DANS le HSM
// SoftHSM2 en conteneur : docker run --rm -it -v "$PWD/tokens:/var/lib/softhsm/tokens" ghcr.io/…/softhsm2 sh -c 'softhsm2-util --init-token --slot 0 --label lab --pin 1234 --so-pin 0000 && pkcs11-tool --module /usr/lib/softhsm/libsofthsm2.so --login --pin 1234 --keypairgen --key-type rsa:3072 --label cachet-actes'
// DSS : new Pkcs11SignatureToken("/usr/lib/libCryptoki2_64.so", pinCallback, slot)"""),
  ("API, base, audit", "API : <code>/sign</code>, <code>/verify</code>, <code>/certificates</code> (inventaire, expiration), <code>/certificates/{id}/renew</code>, <code>/revoke</code> ; authentification mTLS service-à-service + jeton porteur de l'agent (Keycloak) ; autorisation par politique (quelle application peut utiliser quelle clé pour quel type de document). Base : transactions de signature (id, demandeur, empreinte, série du certificat, horodatage, résultat), certificats (série, issuer, sujet, dates, usage, emplacement, propriétaire, statut). Audit : journal signé/chaîné (hash du précédent), exporté vers le SIEM, conservé selon la durée légale ; rapports mensuels (signatures par application, certificats expirant, révocations).", None)],
 [("Pourquoi ne pas mettre la clé de cachet dans un PKCS12 sur le serveur de signature ?", "Un fichier se copie (sauvegarde, dump mémoire, administrateur) sans trace ; une compromission n'est pas détectable et oblige à révoquer sans savoir depuis quand. Le HSM rend l'exfiltration matériellement impossible et journalise chaque usage."),
  ("Question d'entretien : que se passe-t-il si le HSM tombe ?", "Plus de signature : c'est une brique à haute disponibilité (deux HSM en réplication, deux sites), avec SLO, supervision PKCS#11 (latence, erreurs), et procédure de restauration par cartes de quorum. Les vérifications, elles, continuent (clés publiques).")],
 ("Maquette de la plateforme", ["Trois services Spring Boot en Docker Compose : signature (CMS/PAdES via DSS), clés (SoftHSM2 par PKCS#11), validation (PKIX + CRL/OCSP + inventaire) ; PostgreSQL pour les métadonnées ; mTLS entre services ; Keycloak pour les agents.", "Flux complet : l'application métier signe un PDF (cachet), le vérifie, l'inventaire alerte à J-30, renouvellement automatisé, révocation propagée.", "Dossier d'architecture : rôle de chaque composant, flux, données, audit, cycle de vie, plan de continuité (HSM secondaire)."],
  "Preuve : <code>key.getEncoded()</code> renvoie null (clé non exportable) ; la signature PAdES-T est validée par DSS et Acrobat ; le journal d'audit contient une ligne par signature avec le hash chaîné ; la révocation d'un certificat de cachet fait échouer <code>/verify</code> dans la minute (OCSP) ; le dossier tient en 8 pages avec le schéma ci-dessus adapté.")),

ch("Sécurité, attaques et débogage PKI", 'e',
 ["Chaque risque se décrit attaque → impact → protection : vol de clé (fichier copié → usurpation → HSM, rotation, courte durée), MITM (trust-all, CA pirate → interception → validation stricte, pinning ciblé, CT), mauvaise chaîne (intermédiaire manquant → refus ou acceptation d'un faux → fullchain, AIA, tests), algorithmes faibles (SHA-1, RSA 1024 → forgeage → politique d'algorithmes, <code>jdk.certpath.disabledAlgorithms</code>), secrets (mot de passe en clair → accès → secret manager, char[], rotation).", "<code>PKIX path building failed</code> signifie que Java n'a pas pu relier le certificat reçu à une ancre de son truststore : chaîne incomplète côté serveur, CA absente côté client, ou mauvais truststore utilisé.", "Le diagnostic est une séquence : qui parle à qui, ce que le serveur envoie (<code>s_client -showcerts</code>), ce que le client accepte (<code>keytool -list</code>, <code>javax.net.debug</code>), dates, noms, algorithmes."],
 ["Dérouler la grille attaque → impact → protection en entretien", "Diagnostiquer les erreurs TLS/PKI les plus fréquentes avec openssl et keytool", "Lire un <code>javax.net.debug</code> et une stack <code>SSLHandshakeException</code>"],
 [("Grille des risques", "", """| Risque                     | Attaque                                        | Impact                          | Protection                                                                 |
| vol de clé privée          | copie du .p12/.key, dump mémoire, sauvegarde   | usurpation, signatures frauduleuses | HSM, clés non exportables, courte durée, rotation, révocation, détection d'usage anormal |
| certificat expiré          | rien à attaquer : panne                        | service indisponible, signatures refusées | inventaire, alertes J-30/J-7, renouvellement automatisé (ACME, API CA), tests |
| certificat révoqué accepté | client sans vérification de révocation        | clé compromise toujours utilisable | CRL/OCSP activés, stapling, hard-fail sur la signature, certificats courts |
| mauvaise validation chaîne | trust-all, CN au lieu du SAN, pas d'ancre     | MITM, faux serveur accepté       | PKIX complet, SAN, truststore minimal, tests négatifs en CI               |
| MITM                       | CA pirate dans le truststore, proxy TLS        | lecture/modification du trafic   | truststore contrôlé (pas cacerts par défaut pour l'interne), pinning ciblé, Certificate Transparency, mTLS |
| configuration TLS faible   | TLS 1.0/1.1, RC4, 3DES, renégociation          | déchiffrement, downgrade         | TLS 1.2+ (1.3 préféré), suites AEAD, HSTS, testssl.sh en CI                |
| algorithme faible / SHA-1  | collision (SHAttered), RSA 1024 factorisable   | certificat ou signature forgés   | SHA-256+, RSA ≥ 3072 / ECC P-256+, jdk.certpath.disabledAlgorithms, politique de la CA |
| secrets mal gérés          | mot de passe keystore dans Git, logs, env      | accès aux clés                   | Vault/Secrets Manager, char[] effacés, pas de log, revue, gitleaks       |
| horloge                    | dérive NTP                                     | « not yet valid », OCSP rejeté   | NTP supervisé, tolérance documentée                                        |"""),
  ("Commandes de diagnostic", "", """ossl s_client -connect host:443 -servername host -showcerts < /dev/null 2>&1 | grep -E 'depth|verify|s:|i:|Verify return'   # ce que le serveur envoie et où la vérification casse
ossl s_client … 2>/dev/null | ossl x509 -noout -dates -subject -ext subjectAltName                                       # dates et SAN de la feuille
ossl verify -CAfile root.pem -untrusted int.pem leaf.pem ; ossl verify -show_chain …                                       # chaîne hors ligne
ossl x509 -in c.pem -noout -text | grep -E 'Signature Algorithm|Public-Key|Not After'                                     # algorithmes, taille, expiration
ossl crl -in crl.pem -noout -nextupdate ; ossl ocsp -issuer int.pem -cert c.pem -url … -CAfile root.pem                     # révocation
jdk keytool -list -v -keystore ts.p12 -storepass x | grep -E 'Alias|Owner|Valid' ; jdk keytool -printcert -file c.pem      # ce que Java accepte
jdk keytool -printcert -sslserver host:443                                                                                 # la chaîne vue par Java
java -Djavax.net.debug=ssl:handshake:verbose -jar app.jar 2>&1 | grep -E 'Found trusted|Certificate chain|alert|Exception' # décision de la JVM
docker run --rm drwetter/testssl.sh --severity LOW https://host                                                            # protocoles, suites, HSTS, stapling"""),
  ("Lire les erreurs", "", """PKIX path building failed: unable to find valid certification path to requested target
  → la chaîne reçue n'atteint aucune ancre : (a) le serveur n'envoie pas l'intermédiaire → -showcerts n'affiche qu'un cert ; corriger fullchain ; (b) la CA interne n'est pas dans le truststore utilisé → keytool -list ; ajouter la RACINE ; (c) l'application utilise cacerts au lieu du truststore fourni → -Djavax.net.ssl.trustStore ou bundle
PKIX path validation failed: … validity check failed / CertificateExpiredException        → expiré ou horloge ; -dates
No subject alternative DNS name matching host found                                       → SAN absent ou nom différent (SNI, alias DNS)
Certificates do not conform to algorithm constraints                                      → SHA-1/RSA1024/MD5 ; jdk.certpath.disabledAlgorithms
Received fatal alert: handshake_failure / protocol_version                                → suites ou versions incompatibles ; testssl
Received fatal alert: bad_certificate / unknown_ca / certificate_required                 → mTLS : cert client absent, d'une autre CA, ou EKU faux
SSLHandshakeException: Remote host terminated the handshake                               → souvent un proxy/LB qui coupe ; tester en direct
Unable to load keystore / keystore password was incorrect / Tag number over 30            → mauvais mot de passe ou mauvais format (JKS lu en PKCS12, PEM lu en binaire)""")],
 [("Le serveur envoie une chaîne correcte, <code>openssl verify</code> passe, mais Java échoue en PKIX. Pistes ?", "L'application n'utilise pas le truststore qu'on croit (cacerts par défaut, bundle mal nommé, variable d'environnement absente en prod), ou une politique d'algorithmes refuse un maillon (SHA-1 intermédiaire), ou la date de la JVM diffère. <code>javax.net.debug</code> montre le truststore chargé et la raison."),
  ("Question d'entretien : pinning ou pas ?", "Pinning d'une clé/CA interne pour des liaisons critiques service-à-service oui (avec plan de rotation) ; pinning de certificats publics non (renouvellements cassent tout). Le mTLS avec une CA interne donne le même bénéfice de façon gérable.")],
 ("Salle de crise PKI", ["Reproduire dix pannes sur la maquette (expiré, intermédiaire manquant, mauvais truststore, SHA-1, SAN absent, révoqué, horloge +2 h, mot de passe faux, TLS 1.0 seul, EKU faux) et documenter pour chacune : symptôme exact, commande qui la révèle, correction.", "testssl.sh en CI sur le serveur de signature avec échec sur note < A.", "Runbook <code>docs/runbooks/tls-pki.md</code> en 12 entrées, utilisé pour le support N3."],
  "Le runbook est vérifié en le faisant suivre par un pair sans contexte : chaque panne est diagnostiquée en < 5 minutes avec les commandes données. testssl : A+ après HSTS et suppression de TLS 1.1 et CBC.")),

ch("Questions d'entretien Java PKI (40) et fiche de révision", 'e',
 ["Une réponse d'entretien tient en deux phrases, puis on détaille si on est relancé ; l'exemple concret vaut plus que la définition.", "Les vingt concepts, vingt commandes et acronymes ci-dessous sont à savoir de mémoire.", "Les schémas à retenir : les trois opérations, la PKI trois niveaux, le handshake TLS, le flux de signature, l'architecture métier → signature → clés → HSM → CA."],
 ["Répondre aux 40 questions les plus probables", "Réciter la fiche condensée", "Redessiner les cinq schémas de tête"],
 [("Quarante questions", "", """1 Keystore vs truststore ? Mon identité (clé privée + chaîne) vs les CA que j'accepte ; même format PKCS12. Ex : serveur = keystore, client = truststore, mTLS = les deux.
2 Chaîne de certification ? Feuille signée par une intermédiaire signée par une racine du truststore ; vérifiée de bas en haut (signature, dates, contraintes). Ex : fullchain.pem = feuille + intermédiaires.
3 Comment Java valide un certificat ? CertPathValidator PKIX : construit la chaîne (AKI/SKI, AIA), vérifie signatures, dates, BasicConstraints, KU/EKU, politiques, puis révocation si activée. Ex : chapitre 9.
4 CRL vs OCSP ? Liste signée périodique vs réponse en ligne par série ; stapling = le serveur joint la réponse OCSP. Ex : navigateur = OCSP soft-fail ; signature = hard-fail.
5 Qu'est-ce qu'un X.509 ? Structure ASN.1 liant identité, clé publique, validité, usages (extensions), signée par une CA. Ex : openssl x509 -text.
6 Signature numérique ? Hash du document chiffré avec la clé privée, vérifié avec la publique : intégrité, authenticité, non-répudiation. Ex : SHA256withRSA sur un PDF.
7 Pourquoi un HSM ? Clé non exportable, opérations dedans, journal, certification ; un fichier se copie sans trace. Ex : clé de cachet, clé de CA.
8 Signature vs chiffrement ? Signer = privée puis vérifier avec la publique (authenticité) ; chiffrer = publique puis déchiffrer avec la privée (confidentialité). Ex : PDF signé lisible par tous.
9 eIDAS ? Règlement UE des services de confiance : niveaux simple/avancée/qualifiée, QTSP, TSL, effet juridique. Ex : signature qualifiée = manuscrite.
10 RGS ? Référentiel ANSSI pour les administrations françaises : niveaux */**/***, certificats RGS, exigences d'authentification et de signature. Ex : carte agent RGS **.
11 Symétrique vs asymétrique ? Une clé partagée rapide (AES) vs paire publique/privée lente (RSA/ECC) ; hybride en pratique. Ex : TLS.
12 RSA vs ECC ? Sécurité équivalente avec des clés bien plus petites en ECC (P-256 ≈ RSA 3072), plus rapide ; RSA universel. Ex : TLS 1.3 en ECDSA.
13 Pourquoi hacher avant de signer ? Taille fixe, rapidité, intégrité du document entier. Ex : SHA-256 → 32 octets.
14 SHA-1 ? Collisions démontrées (2017) : interdit pour signer et certifier. Ex : jdk.certpath.disabledAlgorithms.
15 CSR ? Demande signée contenant clé publique + identité + extensions ; la privée reste chez le demandeur. Ex : openssl req -new.
16 Root CA hors ligne, pourquoi ? Sa compromission détruit toute la confiance ; elle ne signe que les intermédiaires, en cérémonie. Ex : HSM sous scellés.
17 SAN vs CN ? Seul le SAN est vérifié pour TLS ; le CN est informatif. Ex : hostname mismatch sans SAN.
18 Key Usage vs Extended Key Usage ? KU = opérations cryptographiques (signature, chiffrement de clé, signature de certificat) ; EKU = finalités applicatives (serverAuth, clientAuth, codeSigning, timeStamping). Ex : nonRepudiation pour signer des documents.
19 Basic Constraints ? CA ou pas, et profondeur de chaîne autorisée (pathlen). Ex : pathlen:0 sur l'intermédiaire.
20 PEM vs DER ? Même contenu, base64 avec en-têtes vs binaire. Ex : openssl x509 -inform DER.
21 PKCS#12 ? Conteneur chiffré de clé privée + certificats ; keystore Java par défaut. Ex : .p12 pour Spring Boot.
22 PKCS#8 ? Format de clé privée (chiffrée ou non). Ex : PKCS8EncodedKeySpec.
23 PKCS#11 ? API standard des HSM et cartes ; SunPKCS11 en Java. Ex : C_Sign dans le HSM.
24 PKCS#7 / CMS ? Conteneur de données signées/chiffrées avec certificats ; base de CAdES. Ex : .p7s détaché.
25 Handshake TLS 1.3 ? ClientHello/ServerHello (ECDHE), certificat + CertificateVerify, Finished ; le client valide la chaîne et le SAN ; PFS. Ex : s_client.
26 mTLS ? Le client présente aussi un certificat ; le serveur le valide et mappe l'identité. Ex : services d'un ministère.
27 PKIX path building failed ? Aucune ancre atteinte : intermédiaire manquant, CA absente du truststore, mauvais truststore. Ex : -showcerts + keytool -list.
28 Signature avancée vs qualifiée ? Avancée = lien unique, contrôle exclusif, intégrité ; qualifiée = + certificat qualifié + QSCD → équivalence manuscrite. Ex : QcStatements.
29 CAdES/XAdES/PAdES ? CMS pour tout fichier / XML / PDF ; profils B, T, LT, LTA. Ex : PAdES-LTA pour l'archivage.
30 Horodatage ? Jeton RFC 3161 d'une TSA prouvant l'existence à une date ; rend une signature vérifiable après expiration. Ex : -T.
31 Cachet vs signature ? Personne morale automatisée vs personne physique. Ex : cachet d'un acte généré.
32 QTSP ? Prestataire qualifié audité, listé dans la TSL. Ex : validation via la LOTL.
33 Comment renouveler un certificat sans coupure ? Nouvelle clé + CSR, nouveau cert déployé avant l'expiration, rechargement à chaud, ancien conservé pour vérifier les vieilles signatures. Ex : reload-on-update.
34 Que faire d'une clé compromise ? Révoquer immédiatement (CRL/OCSP), réémettre, chercher depuis quand, invalider ce qui a été signé après la date estimée, post-mortem. Ex : OCSP reason keyCompromise.
35 Trust-all TrustManager ? Accepte tout certificat : MITM garanti ; interdit, même en dev (utiliser une CA de dev). Ex : revue de code.
36 Certificate Transparency ? Journaux publics des certificats émis ; détecte une émission frauduleuse. Ex : crt.sh.
37 PSS vs PKCS#1 v1.5 ? Padding probabiliste prouvé vs déterministe historique ; PSS recommandé. Ex : RSASSA-PSS.
38 AES-GCM ? Chiffrement authentifié ; IV unique obligatoire. Ex : 96 bits aléatoires.
39 Que contient un certificat qualifié en plus ? QcStatements, politique qualifiée, CA dans la TSL, souvent délivré face à face. Ex : carte d'agent.
40 Comment tester une PKI en CI ? CA de test générée à chaque pipeline, certificats volontairement expirés/révoqués/sans SAN, tests négatifs, testssl. Ex : chapitre 11."""),
  ("Fiche condensée", "", """CONCEPTS (20) : symétrique/asymétrique · hash · signature · chiffrement hybride · PKI · Root/Intermediate CA · RA · CSR · X.509 v3 · SAN · KU/EKU · Basic Constraints · chaîne · CRL/OCSP/stapling · keystore/truststore · PKCS#8/#12/#11/#7 · TLS 1.3/mTLS · CAdES/XAdES/PAdES · profils B/T/LT/LTA · eIDAS/RGS/QTSP/HSM
COMMANDES (20) : openssl genpkey · req -new · x509 -req/-text · ca · verify · s_client -showcerts · pkcs12 -export/-in · pkcs8 · dgst -sign/-verify · cms -sign/-verify · crl · ocsp · ts · keytool -genkeypair · -certreq · -importcert · -exportcert · -list -v · -printcert -sslserver · java -Djavax.net.debug=ssl:handshake
ACRONYMES : CA RA CSR CRL OCSP AIA CDP SAN KU EKU AKI SKI PEM DER PKCS CMS TSA TSL LOTL QTSP QSCD QES AdES PAdES XAdES CAdES eIDAS RGS ANSSI HSM PKCS#11 FIPS PFS SNI HSTS CT
SCHÉMAS : les trois opérations (ch. 1) · PKI trois niveaux (ch. 2) · handshake TLS/mTLS (ch. 5) · flux de signature et vérification (ch. 6) · métier → signature → clés → HSM → CA (ch. 10)
RÉFLEXES : SAN pas CN · PKCS12 pas JKS · SHA-256+ · RSA ≥ 3072 ou P-256 · révocation configurée explicitement · jamais trust-all · clé de cachet en HSM · signature avec horodatage · certificats courts et renouvellement automatisé · tests négatifs en CI""")],
 [("Comment répondre à une question dont on ne connaît pas le détail ?", "Donner le principe (deux phrases), l'exemple qu'on a pratiqué, et dire ce qu'on vérifierait (« je regarderais la sortie de s_client »). Un raisonnement de diagnostic vaut plus qu'une définition récitée."),
  ("Quelle histoire personnelle préparer ?", "Une panne TLS réelle diagnostiquée (PKIX, expiration) racontée en STAR avec la commande décisive et ce qu'on a automatisé ensuite (alerte J-30, test en CI).")],
 ("Simulation d'entretien", ["Répondre à voix haute aux 40 questions, chronométré (30 s chacune), s'enregistrer, noter les hésitations.", "Redessiner les cinq schémas de mémoire et les comparer aux originaux.", "Refaire le TP complet (chapitres 2 → 9) en moins de deux heures sans relire le cours."],
  "Objectif : 36/40 réponses en moins de 30 s, les cinq schémas exacts sur les points clés (racine hors ligne, CertificateVerify, attributs signés, HSM non exportable), le TP en < 2 h avec la vérification OpenSSL/Java croisée à chaque étape.")),
]

d = sys.argv[1]
page('cours-06-java-pki-signature-electronique.html', 'Java, PKI et signature électronique — de zéro à expert', "Treize chapitres orientés mission et entretien : cryptographie appliquée, PKI et X.509, formats, keystores et Spring Boot, TLS/mTLS, signature électronique (CAdES/XAdES/PAdES, horodatage), Java et Bouncy Castle, application Spring Boot de signature, validation et révocation, eIDAS et RGS, architecture avec HSM, sécurité et débogage, 40 questions d'entretien et fiche de révision. Tout en Docker (OpenSSL, JDK, Maven, SoftHSM2), chaque chapitre a ses exercices corrigés et un travail pratique avec correction type.", "≈ 40 h de travail · prérequis : Java/Spring Boot confirmé, Docker Desktop · complète le niveau 7 du parcours DevOps (PKI 41.9, Vault PKI, cert-manager).", PKI, [('cours-07-cloud.html', 'Cloud'), ('devops-07-securite-devsecops.html', 'DevOps niveau 7')])
