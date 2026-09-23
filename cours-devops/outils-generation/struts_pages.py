"""Cours Java web classique : Servlets/JSP, Struts (2/6 et 1 legacy), Hibernate. Usage : python3 struts_pages.py <dossier>"""
import sys, runpy, pathlib
g = runpy.run_path(pathlib.Path(__file__).with_name('front_gen.py'), run_name='front'); ch, page = g['ch'], g['page']
MVN = "Tout en conteneur : <code>alias mvn='docker run --rm -v \"$PWD:/app\" -w /app -v m2:/root/.m2 maven:3.9-eclipse-temurin-17 mvn'</code> et l'application déployée dans <code>tomcat:10.1-jdk17</code> par Compose."

SH = [
ch("Servlets et JSP : le socle du web Java", 'j',
 ["Un conteneur de servlets (Tomcat) reçoit la requête HTTP, la transforme en <code>HttpServletRequest</code>, appelle une servlet ou une JSP, et renvoie la réponse ; une JSP est compilée en servlet au premier appel.", "Le pattern MVC modèle 2 : la servlet (contrôleur) traite, met des attributs dans la requête, et forward vers une JSP (vue) qui ne fait qu'afficher avec EL et JSTL ; jamais de Java dans la JSP (scriptlets interdits).", "Quatre portées (page, request, session, application) et leur coût : la session est un état serveur à limiter ; les filtres et listeners encadrent le cycle."],
 ["Écrire une servlet, un filtre, un listener, et comprendre le cycle de vie", "Écrire une JSP propre avec EL, JSTL et tags de formatage", "Choisir la portée d'un attribut et éviter les fuites de session"],
 [("Cycle et MVC modèle 2", "", """navigateur → Tomcat (Connector) → FilterChain (encodage, sécurité, journalisation) → Servlet (doGet/doPost) → req.setAttribute("incidents", list) → RequestDispatcher.forward("/WEB-INF/vues/incidents.jsp") → JSP → HTML
// IncidentServlet.java (Jakarta EE 10 : jakarta.servlet.*)
@WebServlet("/incidents")
public class IncidentServlet extends HttpServlet {
  private IncidentService service;                                  // injecté par le listener ou obtenu du ServletContext
  @Override public void init() { service = (IncidentService) getServletContext().getAttribute("incidentService"); }
  @Override protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
    String zone = req.getParameter("zone");                          // toujours valider/normaliser
    req.setAttribute("incidents", service.list(zone));
    req.getRequestDispatcher("/WEB-INF/vues/incidents.jsp").forward(req, resp);   // sous WEB-INF : la JSP n'est pas appelable directement
  }
  @Override protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws IOException {
    service.create(req.getParameter("titre"), req.getParameter("priorite"));
    resp.sendRedirect(req.getContextPath() + "/incidents");            // PRG : Post-Redirect-Get, jamais forward après un POST
  }
}
@WebFilter("/*") public class EncodingFilter implements Filter { public void doFilter(ServletRequest q, ServletResponse s, FilterChain c) throws IOException, ServletException { q.setCharacterEncoding("UTF-8"); s.setContentType("text/html;charset=UTF-8"); c.doFilter(q, s); } }
@WebListener public class AppListener implements ServletContextListener { public void contextInitialized(ServletContextEvent e) { e.getServletContext().setAttribute("incidentService", new IncidentService(DataSources.fromJndi())); } }"""),
  ("JSP, EL, JSTL", "", """<%@ page contentType="text/html;charset=UTF-8" pageEncoding="UTF-8" %>
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
<%@ taglib prefix="fmt" uri="jakarta.tags.fmt" %>
<%@ taglib prefix="fn" uri="jakarta.tags.functions" %>
<c:set var="titre" value="Incidents" scope="request"/>
<h1><c:out value="${titre}"/></h1>                                           <!-- c:out échappe le HTML : anti-XSS ; ${x} brut n'échappe PAS -->
<c:choose><c:when test="${empty incidents}"><p>Aucun incident.</p></c:when>
<c:otherwise><table>
<c:forEach var="i" items="${incidents}" varStatus="st">
  <tr class="${st.index % 2 == 0 ? 'pair' : 'impair'}"><td>${i.id}</td><td><c:out value="${i.titre}"/></td>
  <td><fmt:formatDate value="${i.creeLe}" pattern="dd/MM/yyyy HH:mm"/></td><td>${fn:toUpperCase(i.priorite)}</td></tr>
</c:forEach></table></c:otherwise></c:choose>
<form method="post" action="${pageContext.request.contextPath}/incidents"><input name="titre" required><select name="priorite"><option>P1</option><option>P2</option></select><button>Créer</button></form>
<c:url var="lien" value="/incidents"><c:param name="zone" value="${param.zone}"/></c:url><a href="${lien}">Filtrer</a>   <!-- c:url encode et ajoute jsessionid si besoin -->
EL : ${sessionScope.utilisateur.nom}, ${param.zone}, ${header['User-Agent']}, ${cookie.theme.value}, ${initParam.version} ; opérateurs empty, ?:, ==, div, mod
web.xml / jsp-config : <scripting-invalid>true</scripting-invalid> (interdit les scriptlets), <el-ignored>false</el-ignored>, <page-encoding>UTF-8</page-encoding>"""),
  ("Le poste", MVN, """# compose.yaml
services:
  web: { image: tomcat:10.1-jdk17, ports: ["8080:8080"], volumes: ["./target/crisis.war:/usr/local/tomcat/webapps/ROOT.war"], environment: { JAVA_OPTS: "-Dfile.encoding=UTF-8" }, depends_on: [db] }
  db:  { image: postgres:16, environment: { POSTGRES_PASSWORD: crisis, POSTGRES_DB: crisis }, volumes: ["pg:/var/lib/postgresql/data"] }
volumes: { pg: {} }
# mvn -q package && docker compose up -d ; http://localhost:8080/incidents""")],
 [("Pourquoi les JSP sous <code>/WEB-INF/</code> ?", "Tout ce qui est sous WEB-INF n'est pas servi directement : la JSP ne peut être atteinte que par un forward du contrôleur, donc jamais sans les attributs qu'elle attend, jamais sans passer par la sécurité."),
  ("Question d'entretien : différence entre forward et redirect ?", "Forward : même requête, côté serveur, URL inchangée, attributs conservés. Redirect : réponse 302, nouvelle requête du navigateur, attributs de requête perdus, URL changée ; indispensable après un POST (PRG) pour éviter la re-soumission.")],
 ("Mini CrisisShield en servlets et JSP", ["Servlet liste/création d'incidents, filtre d'encodage, listener qui prépare le service ; JSP avec JSTL, formulaire, PRG.", "JSP sous WEB-INF, scriptlets interdits, sortie échappée ; test d'un XSS (<code>&lt;script&gt;</code> dans le titre) avant/après <code>c:out</code>.", "Déploiement dans Tomcat par Compose ; logs Tomcat lus avec <code>docker compose logs</code>."],
  "Preuve : le titre <code>&lt;script&gt;alert(1)&lt;/script&gt;</code> s'affiche littéralement avec <code>c:out</code> et s'exécute avec <code>${i.titre}</code> ; un rafraîchissement après création ne recrée pas l'incident (PRG) ; <code>curl /WEB-INF/vues/incidents.jsp</code> → 404.")),

ch("JSP avancé : tags personnalisés, layouts, i18n, sécurité", 'c',
 ["Un tag file (<code>.tag</code>) ou une classe <code>SimpleTagSupport</code> factorise le HTML répété ; <code>jsp:include</code> et <code>c:import</code> composent ; Tiles ou SiteMesh gèrent le layout global.", "i18n : <code>fmt:setLocale</code>, <code>fmt:bundle</code>, <code>fmt:message</code> avec des fichiers properties par locale ; formats de dates et nombres par locale.", "Sécurité : XSS (échapper partout, attributs et JavaScript inclus), CSRF (jeton par session vérifié en POST), en-têtes de sécurité par filtre, sessions (HttpOnly, Secure, rotation à la connexion), jamais d'EL évaluant une entrée utilisateur."],
 ["Écrire un tag file et un tag Java, et composer des pages avec Tiles", "Internationaliser une application JSP", "Sécuriser les vues (XSS, CSRF, sessions, en-têtes)"],
 [("Tags et layout", "", """<%-- WEB-INF/tags/badge.tag --%>
<%@ tag body-content="empty" %><%@ attribute name="priorite" required="true" %><%@ taglib prefix="c" uri="jakarta.tags.core" %>
<span class="badge badge-${fn:toLowerCase(priorite)}"><c:out value="${priorite}"/></span>
<%-- usage --%> <%@ taglib prefix="cs" tagdir="/WEB-INF/tags" %> <cs:badge priorite="${i.priorite}"/>
// tag Java : public class TruncateTag extends SimpleTagSupport { private String value; private int max = 40; public void doTag() throws IOException { getJsonContext().getOut().print(StringEscapeUtils.escapeHtml4(value.length() > max ? value.substring(0, max) + "…" : value)); } … setters … }  + TLD sous WEB-INF/tlds/
<!-- Tiles 3 : tiles.xml -->
<definition name="layout" template="/WEB-INF/layout/page.jsp"><put-attribute name="header" value="/WEB-INF/layout/header.jsp"/><put-attribute name="body" value=""/></definition>
<definition name="incidents" extends="layout"><put-attribute name="titre" value="Incidents"/><put-attribute name="body" value="/WEB-INF/vues/incidents.jsp"/></definition>
<!-- page.jsp --> <tiles:insertAttribute name="header"/><main><tiles:insertAttribute name="body"/></main>"""),
  ("i18n et sécurité", "", """<fmt:setLocale value="${sessionScope.locale != null ? sessionScope.locale : pageContext.request.locale}"/><fmt:setBundle basename="messages"/>
<h1><fmt:message key="incidents.titre"/></h1> <fmt:message key="incidents.compte"><fmt:param value="${fn:length(incidents)}"/></fmt:message>   <!-- messages_fr.properties : incidents.compte=Vous avez {0} incidents -->
<fmt:formatNumber value="${montant}" type="currency" currencyCode="EUR"/>
// CSRF : filtre qui pose un jeton en session et le vérifie sur POST/PUT/DELETE ; dans le formulaire : <input type="hidden" name="_csrf" value="${sessionScope._csrf}">
// XSS dans un attribut ou du JS : <a title="${fn:escapeXml(i.titre)}"> ; <script>var t = "${fn:escapeXml(i.titre)}";</script> → mieux : passer par un data-attribute et lire côté JS ; jamais d'HTML construit depuis une entrée
// sessions : <session-config><cookie-config><http-only>true</http-only><secure>true</secure></cookie-config><tracking-mode>COOKIE</tracking-mode><session-timeout>30</session-timeout></session-config> ; request.changeSessionId() à la connexion
// en-têtes par filtre : X-Content-Type-Options nosniff, Content-Security-Policy, X-Frame-Options DENY ; erreurs : <error-page><exception-type>java.lang.Throwable</exception-type><location>/WEB-INF/vues/erreur.jsp</location></error-page> (pas de stack trace)""")],
 [("<code>${param.q}</code> affiché dans une page de résultats : problème ?", "XSS réfléchi : l'EL n'échappe pas. <code>c:out</code> ou <code>fn:escapeXml</code>, dans le HTML comme dans les attributs et le JavaScript."),
  ("Question d'entretien : Tiles ou include ?", "<code>jsp:include</code> compose des fragments à la main dans chaque page ; Tiles définit un layout central et des définitions héritées : une seule page maîtresse, des vues qui ne connaissent que leur corps.")],
 ("Vues industrialisées", ["Tag file <code>badge</code>, tag Java <code>truncate</code> avec TLD, layout Tiles avec header/footer/menu.", "Messages fr/en avec sélecteur de langue en session ; dates et montants formatés.", "Filtre CSRF, filtre d'en-têtes, page d'erreur générique ; tests : POST sans jeton → 403, stack trace jamais affichée."],
  "Preuve : la page bascule en anglais par <code>?lang=en</code> et garde le choix ; un POST sans <code>_csrf</code> renvoie 403 ; une exception volontaire affiche la page d'erreur propre et la trace est dans les logs Tomcat seulement.")),

ch("Struts 2 (Struts 6) : architecture, actions, résultats, intercepteurs", 'c',
 ["Struts 2 (renommé Struts 6 depuis la 6.0, Jakarta depuis 6.4) : un filtre unique (<code>StrutsPrepareAndExecuteFilter</code>) reçoit tout, un <code>ActionMapper</code> choisit l'action, une pile d'intercepteurs (params, validation, i18n, fileUpload, exception…) s'exécute avant et après l'action, l'action est un POJO qui renvoie un nom de résultat, le résultat rend la vue (JSP, redirect, stream, JSON).", "La ValueStack et OGNL relient la vue à l'action : <code>&lt;s:property value=\"incident.titre\"/&gt;</code> lit un getter de l'action ; les paramètres HTTP sont convertis et injectés dans les setters.", "Configuration par <code>struts.xml</code> (packages, namespaces, actions, results, interceptor-stacks) ou par conventions/annotations (plugin Convention)."],
 ["Décrire le cycle d'une requête Struts 2 et le rôle de chaque intercepteur", "Écrire des actions, des résultats et des vues avec les tags Struts", "Configurer packages, namespaces et piles d'intercepteurs"],
 [("Cycle et configuration", "", """HTTP → StrutsPrepareAndExecuteFilter → ActionMapper (/incidents/lister.action) → ActionProxy → ActionInvocation : [exception → alias → servletConfig → i18n → prepare → chain → scopedModelDriven → modelDriven → fileUpload → checkbox → datetime → multiselect → staticParams → actionMappingParams → params → conversionError → validation → workflow → debugging] → Action.execute() → "success" → Result (dispatcher JSP) → intercepteurs (après) → réponse
<!-- pom : org.apache.struts:struts2-core:6.4.0 (classifier jakarta pour Tomcat 10), struts2-convention-plugin, struts2-json-plugin, struts2-tiles-plugin, struts2-spring-plugin -->
<!-- struts.xml -->
<struts>
  <constant name="struts.devMode" value="false"/>                         <!-- jamais true en production : expose la ValueStack -->
  <constant name="struts.action.extension" value="action,"/>
  <constant name="struts.ognl.allowStaticMethodAccess" value="false"/>
  <package name="incidents" namespace="/incidents" extends="struts-default">
    <interceptors><interceptor name="audit" class="fr.crisis.web.AuditInterceptor"/>
      <interceptor-stack name="crisisStack"><interceptor-ref name="audit"/><interceptor-ref name="defaultStack"><param name="params.excludeParams">dojo\\..*,^struts\\..*,^session\\..*,^request\\..*,^application\\..*,^servlet(Request|Response)\\..*,parameters\\...*,^action:.*,^method:.*,^class\\..*</param></interceptor-ref></interceptor-stack></interceptors>
    <default-interceptor-ref name="crisisStack"/>
    <global-results><result name="error">/WEB-INF/vues/erreur.jsp</result><result name="login" type="redirectAction"><param name="actionName">connexion</param><param name="namespace">/</param></result></global-results>
    <global-exception-mappings><exception-mapping exception="java.lang.Exception" result="error"/></global-exception-mappings>
    <action name="lister" class="fr.crisis.web.IncidentAction" method="lister"><result>/WEB-INF/vues/incidents.jsp</result></action>
    <action name="creer" class="fr.crisis.web.IncidentAction" method="creer"><result name="input">/WEB-INF/vues/incidents.jsp</result><result type="redirectAction"><param name="actionName">lister</param></result></action>
  </package>
</struts>"""),
  ("Action et vue", "", """public class IncidentAction extends ActionSupport implements Preparable {   // ActionSupport : messages, erreurs, i18n
  private IncidentService service;                       // injecté par Spring (struts2-spring-plugin) : setter
  private Incident incident = new Incident();            // modèle rempli par l'intercepteur params : incident.titre, incident.priorite
  private List<Incident> incidents; private String zone;
  public void prepare() { }                              // avant params : charger des listes de référence
  public String lister() { incidents = service.list(zone); return SUCCESS; }
  public String creer() { service.create(incident); addActionMessage(getText("incident.cree")); return SUCCESS; }
  // getters/setters : ce sont les seules portes d'entrée d'OGNL ; ne pas exposer de setter dangereux
}
<%@ taglib prefix="s" uri="/struts-tags" %>
<s:actionmessage/><s:actionerror/>
<s:form action="creer" method="post"><s:textfield name="incident.titre" label="%{getText('incident.titre')}"/><s:select name="incident.priorite" list="#{'P1':'Critique','P2':'Haute'}"/><s:token/><s:submit key="bouton.creer"/></s:form>
<s:iterator value="incidents" var="i" status="st"><tr><td><s:property value="#i.id"/></td><td><s:property value="#i.titre"/></td></tr></s:iterator>   <!-- s:property échappe par défaut (escapeHtml=true) -->
<s:url var="u" action="lister"><s:param name="zone" value="%{zone}"/></s:url><s:a href="%{#u}">Filtrer</s:a>""")],
 [("Pourquoi <code>excludeParams</code> et <code>allowStaticMethodAccess=false</code> ?", "L'intercepteur params évalue les noms de paramètres en OGNL : sans liste d'exclusion et sans restriction, un nom de paramètre malicieux peut atteindre le contexte (S2-005, S2-032, S2-045). C'est la première ligne de défense avec la mise à jour de version."),
  ("Question d'entretien : que fait l'intercepteur workflow ?", "Après validation, s'il y a des erreurs de champ ou d'action, il renvoie <code>input</code> sans exécuter l'action : c'est lui qui réaffiche le formulaire avec les messages.")],
 ("CrisisShield en Struts 6", ["Projet Maven struts2-core jakarta + Tomcat 10 en Compose ; actions lister/créer/détail avec struts.xml, résultats et redirectAction (PRG).", "Intercepteur <code>audit</code> maison (qui, quelle action, durée) dans une pile personnalisée ; global results et exception mapping.", "Vue JSP avec tags Struts, messages i18n, jeton <code>s:token</code> + intercepteur <code>token</code> contre la double soumission."],
  "Preuve : la double soumission d'un formulaire renvoie <code>invalid.token</code> ; <code>?debug=xml</code> ne fonctionne pas (devMode false) ; l'intercepteur audit journalise <code>lister 12 ms</code> ; un paramètre <code>class.classLoader.x=1</code> est ignoré (excludeParams).")),

ch("Struts 2 : formulaires, validation, conversion, uploads, OGNL", 'c',
 ["Validation par XML (<code>IncidentAction-validation.xml</code>), annotations (<code>@RequiredStringValidator</code>…) ou <code>validate()</code>/<code>validateCreer()</code> ; les erreurs de champ remontent dans <code>fieldErrors</code> et la vue les affiche par champ.", "Conversion de types automatique (nombres, dates, listes, énumérations) avec convertisseurs personnalisés (<code>StrutsTypeConverter</code>) ; les erreurs de conversion deviennent des erreurs de champ.", "OGNL : langage d'expression de la ValueStack (<code>%{}</code>, <code>#var</code>, <code>#session</code>, <code>#request</code>, <code>#parameters</code>) ; puissant, donc à ne jamais laisser évaluer une entrée utilisateur."],
 ["Valider un formulaire des trois façons et afficher les erreurs", "Écrire un convertisseur et gérer un upload de fichier", "Lire et écrire OGNL sans ouvrir de faille"],
 [("Validation", "", """<!-- IncidentAction-creer-validation.xml (à côté de la classe) -->
<validators>
  <field name="incident.titre"><field-validator type="requiredstring"><message key="erreur.titre.requis"/></field-validator><field-validator type="stringlength"><param name="minLength">3</param><param name="maxLength">200</param><message>Entre ${minLength} et ${maxLength} caractères</message></field-validator></field>
  <field name="incident.zone"><field-validator type="regex"><param name="regexExpression"><![CDATA[^[A-Z][0-9]$]]></param><message>Format A1</message></field-validator></field>
  <validator type="expression"><param name="expression">!(incident.priorite == 'P1' &amp;&amp; incident.zone == null)</param><message>Zone obligatoire en P1</message></validator>
</validators>
// ou : @Validations(requiredStrings = { @RequiredStringValidator(fieldName = "incident.titre", key = "erreur.titre.requis") }) public String creer() { … }
// ou programmatique : public void validateCreer() { if (service.existe(incident.getTitre())) addFieldError("incident.titre", getText("erreur.titre.doublon")); }
<s:textfield name="incident.titre"/> affiche l'erreur du champ automatiquement (thème xhtml) ; <s:fielderror fieldName="incident.titre"/> pour le thème simple"""),
  ("Conversion et upload", "", """// PriorityConverter extends StrutsTypeConverter : convertFromString(context, values, toClass) → Priority.valueOf(values[0]) ; convertToString(context, o) → o.toString()
// enregistrement : IncidentAction-conversion.properties : incident.priorite=fr.crisis.web.PriorityConverter (ou xwork-conversion.properties global)
// dates : struts.date.format=dd/MM/yyyy ; listes : incident.contacts[0].email ; Map : prefs['theme']
// upload : <s:form enctype="multipart/form-data"><s:file name="piece"/></s:form> ; action : private File piece; private String pieceFileName, pieceContentType;
// intercepteur fileUpload : <param name="fileUpload.maximumSize">5242880</param><param name="fileUpload.allowedTypes">application/pdf,image/png</param> ; struts.multipart.maxSize ; ne jamais faire confiance à pieceFileName (chemin) : renommer, vérifier le contenu (Tika)
OGNL : %{incident.titre} (valeur) ; #session.utilisateur ; #parameters.zone[0] ; incidents.{? #this.priorite == 'P1'} (sélection) ; incidents.{titre} (projection) ; @fr.crisis.Util@constante (statique : désactivé)
Règles : jamais %{} sur une valeur venant de l'utilisateur ; struts.ognl.expressionMaxLength ; struts.excludedClasses/Packages ; mise à jour Struts à chaque avis de sécurité (S2-045 : en-tête Content-Type évalué en OGNL → RCE ; S2-066 : upload et traversée de chemin)""")],
 [("Le formulaire réaffiché a perdu les listes déroulantes : pourquoi ?", "Le résultat <code>input</code> n'exécute pas la méthode qui les chargeait. Charger les listes de référence dans <code>prepare()</code> (intercepteur prepare, exécuté aussi pour input) ou dans un getter paresseux."),
  ("Question d'entretien : qu'est-ce que la ValueStack ?", "Une pile d'objets (action en haut, puis modèle, contexte) sur laquelle OGNL résout les expressions : <code>titre</code> cherche un getter dans l'action, puis dans les objets suivants. Elle est recréée à chaque requête.")],
 ("Formulaire complet", ["Validation XML + annotation + programmatique ; règle croisée P1/zone ; messages i18n par champ.", "Convertisseur d'énumération, dates au format français, tableau de contacts ; upload PDF limité et renommé.", "Tests : requête avec nom de paramètre OGNL malicieux journalisé et ignoré ; upload d'un .exe renommé .pdf refusé (contenu vérifié)."],
  "Preuve : trois validations rouges affichées sous les champs concernés ; <code>incident.contacts[2].email</code> crée bien le troisième contact ; l'upload de 6 Mo est refusé avec le message de taille ; le pseudo-PDF est refusé par la détection de type réel.")),

ch("Struts 2 avancé : intercepteurs, plugins, Spring, REST/JSON, sécurité", 's',
 ["Un intercepteur maison encapsule une préoccupation transverse (audit, autorisation, transaction, rate limiting) ; il voit l'invocation avant et après et peut court-circuiter (renvoyer un résultat sans exécuter l'action).", "Plugins : Convention (zéro XML, actions par nom de package), JSON (résultat json pour les API et AJAX), REST (contrôleurs RESTful), Tiles, Spring (injection), Bean Validation ; ils s'empilent par le classpath.", "Sécurité Struts : suivre les avis (S2-xxx), ne jamais activer devMode/dynamicMethodInvocation en prod, restreindre OGNL, sécuriser les uploads, et tester avec un scanner (les CVE Struts sont dans tous les outils)."],
 ["Écrire des intercepteurs (autorisation, transaction) et les ordonner", "Utiliser Convention, JSON, REST et l'intégration Spring", "Appliquer la checklist de sécurité Struts et la vérifier"],
 [("Intercepteurs maison", "", """public class AuthorizationInterceptor extends AbstractInterceptor {
  @Override public String intercept(ActionInvocation inv) throws Exception {
    Object action = inv.getAction(); Map<String, Object> session = inv.getInvocationContext().getSession();
    if (action instanceof RequiresRole r && !roles(session).contains(r.role())) return "login";      // court-circuit : l'action n'est pas exécutée
    return inv.invoke();                                                                              // continue la pile
  }
}
public class TransactionInterceptor extends AbstractInterceptor {   // ouvre/commit une transaction Hibernate autour de l'action (ou laisser Spring @Transactional sur le service : préférable)
  @Override public String intercept(ActionInvocation inv) throws Exception { Transaction tx = session().beginTransaction(); try { String r = inv.invoke(); tx.commit(); return r; } catch (Exception e) { tx.rollback(); throw e; } }
}
// ordre : l'intercepteur déclaré en premier s'exécute en premier avant l'action, et en dernier après ; les résultats aussi passent par les intercepteurs après (PreResultListener pour agir avant le rendu)"""),
  ("Plugins et intégration", "", """// Convention : classe fr.crisis.actions.incidents.ListerAction → /incidents/lister ; résultat : /WEB-INF/content/incidents/lister.jsp ; @Action, @Result, @Namespace pour les exceptions à la règle ; @ParentPackage("crisis-default")
// JSON : <result type="json"><param name="root">incidents</param><param name="excludeNullProperties">true</param></result> ; @JSON(serialize=false) sur un getter à masquer ; entrée : <interceptor-ref name="json"/> pour désérialiser un corps JSON dans l'action
// REST : struts2-rest-plugin : IncidentsController { index() GET /incidents, show() GET /incidents/42, create() POST, update() PUT, destroy() DELETE } ; extensions .json/.xml
// Spring : struts2-spring-plugin + ContextLoaderListener ; les actions sont des beans prototype ; les services @Transactional injectés par setter ; struts.objectFactory = spring
// Bean Validation : struts2-bean-validation-plugin : @NotBlank @Size sur le modèle, mêmes annotations que Hibernate Validator
Checklist sécurité : version à jour (6.x) ; devMode=false ; struts.enable.DynamicMethodInvocation=false ; struts.ognl.allowStaticMethodAccess=false ; excludeParams et excludedClasses par défaut conservés ; struts.multipart.maxSize ; uploads renommés et types vérifiés ; s:token sur les formulaires ; escapeHtml sur s:property (défaut) ; pas de s:include avec un chemin utilisateur ; headers de sécurité par filtre ; scan OWASP ZAP + dependency-check en CI""")],
 [("Pourquoi le plugin REST plutôt que des actions classiques pour une API ?", "Il mappe les verbes HTTP sur des méthodes et gère la négociation de contenu ; mais pour une nouvelle API, Spring MVC/Boot ou JAX-RS sont plus standards : Struts REST sert surtout à exposer une API depuis une application Struts existante."),
  ("Question d'entretien : comment s'est propagée la faille S2-045 (Equifax) ?", "Le multipart parser Jakarta construisait un message d'erreur avec l'en-tête Content-Type, message ensuite évalué en OGNL : une requête avec un Content-Type contenant une expression exécutait du code. Leçon : mise à jour rapide, aucune évaluation d'entrée, WAF en attendant.")],
 ("Application Struts industrialisée", ["Intercepteurs autorisation et audit ; actions par Convention ; services Spring @Transactional injectés ; résultat JSON pour la liste (AJAX) et contrôleur REST.", "Checklist sécurité appliquée point par point ; OWASP ZAP en conteneur contre l'application ; dependency-check bloquant sur une CVE Struts.", "Tests d'action avec <code>StrutsJUnit4TestCase</code> : exécution d'une action avec paramètres, vérification du résultat et des erreurs."],
  "Preuve : un utilisateur sans rôle admin est redirigé vers <code>login</code> sans exécuter <code>supprimer</code> (journal audit vide) ; ZAP ne remonte aucune alerte High ; dependency-check fait échouer le build si on rétrograde struts2-core en 2.3.x ; les tests d'action passent en < 5 s.")),

ch("Struts 1 legacy et migration", 's',
 ["Struts 1 (fin de vie depuis 2013, CVE non corrigées) : <code>ActionServlet</code>, <code>struts-config.xml</code>, <code>Action.execute(mapping, form, req, resp)</code>, <code>ActionForm</code>/<code>DynaActionForm</code>, <code>ActionForward</code>, tags <code>html:</code>/<code>bean:</code>/<code>logic:</code>, validator-rules.xml, Tiles 1.", "Beaucoup d'applications d'entreprise tournent encore dessus : savoir les lire, les corriger, les sécuriser (filtre de paramètres, WAF) et planifier la sortie.", "Migration : par strangler (nouvelles fonctionnalités en Spring MVC/Boot derrière le même contexte ou un reverse proxy), page par page, avec tests de caractérisation ; Struts 2 n'est une cible que si l'équipe y est déjà."],
 ["Lire et modifier une application Struts 1 en sécurité", "Cartographier un legacy Struts 1 (actions, forms, forwards, tiles)", "Planifier et exécuter une migration progressive vers Spring"],
 [("Struts 1 : les pièces", "", """<!-- struts-config.xml -->
<form-beans><form-bean name="incidentForm" type="org.apache.struts.validator.DynaValidatorForm"><form-property name="titre" type="java.lang.String"/><form-property name="priorite" type="java.lang.String"/></form-bean></form-beans>
<action-mappings><action path="/incidents" type="fr.crisis.web.IncidentAction" name="incidentForm" scope="request" validate="true" input="/WEB-INF/vues/incidents.jsp" parameter="method"><forward name="success" path="/WEB-INF/vues/incidents.jsp"/><forward name="liste" path="/incidents.do?method=lister" redirect="true"/></action></action-mappings>
public class IncidentAction extends DispatchAction {   // parameter="method" → ?method=lister
  public ActionForward lister(ActionMapping m, ActionForm f, HttpServletRequest req, HttpServletResponse resp) { req.setAttribute("incidents", service.list()); return m.findForward("success"); }
  public ActionForward creer(ActionMapping m, ActionForm f, HttpServletRequest req, HttpServletResponse resp) { DynaValidatorForm form = (DynaValidatorForm) f; service.create((String) form.get("titre"), (String) form.get("priorite")); return m.findForward("liste"); }
}
<html:form action="/incidents?method=creer"><html:text property="titre"/><html:errors property="titre"/><html:submit/></html:form> <logic:iterate id="i" name="incidents"><bean:write name="i" property="titre" filter="true"/></logic:iterate>
Pièges : ActionForm en scope session qui garde l'état ; bean:write sans filter (XSS) ; ActionServlet singleton non thread-safe si champs d'instance ; CVE-2014-0114 (ClassLoader via BeanUtils : filtre excluant class.*), CVE-2008-2025 (XSS), Struts 1 non maintenu → WAF, filtre de paramètres, isolation réseau"""),
  ("Cartographie et migration", "", """# inventaire automatique : parser struts-config.xml et tiles-defs.xml → tableau action → classe → forms → forwards → JSP ; grep des scriptlets ; grep bean:write sans filter ; graphe des dépendances entre actions (xmllint / script Python)
# tests de caractérisation : parcours HTTP enregistrés (HtmlUnit/Playwright) avec captures des pages → rejoués contre chaque étape
# strangler : Spring Boot déployé à côté (même Tomcat ou reverse proxy) ; session partagée via Spring Session (Redis) ou cookie de jeton ; les nouvelles pages en Thymeleaf/Spring MVC ; les anciennes redirigées une par une ; les services métier extraits d'abord (ils sont réutilisables tels quels)
# ordre : 1) sécuriser (filtre, WAF, mise à jour des libs) 2) extraire les services et les tester 3) remplacer les écrans les plus modifiés 4) supprimer Struts 1 quand plus aucune action ne reste ; budget par écran : ½ à 2 jours ; jamais de big bang""")],
 [("Pourquoi ne pas migrer Struts 1 vers Struts 2 ?", "Le modèle diffère (POJO, intercepteurs, OGNL) : c'est une réécriture, pas une mise à niveau ; autant viser Spring MVC, mieux maintenu, plus recruté, et déjà présent si Spring est dans le projet. Struts 2 n'a de sens que si l'équipe le maîtrise et qu'un plugin de compatibilité réduit l'effort."),
  ("Question d'entretien : un client refuse tout budget de migration mais Struts 1 est exposé sur Internet. Que fais-tu ?", "Réduire le risque immédiat : filtre de paramètres (class.*), WAF avec règles Struts, mise à jour de Tomcat/JDK, isolation réseau, revue XSS des JSP, tests de sécurité ; documenter la dette avec le coût d'un incident ; proposer le strangler écran par écran, chiffré.")],
 ("Legacy Struts 1 : sécuriser puis migrer", ["Reconstruire une mini application Struts 1 (DispatchAction, DynaValidatorForm, Tiles) dans Tomcat 9 en Docker.", "Script d'inventaire (actions, forms, forwards, JSP, scriptlets, XSS) ; filtre de paramètres et test de la CVE-2014-0114 avant/après.", "Migration strangler de l'écran liste vers Spring Boot (Thymeleaf) derrière un reverse proxy nginx, tests de caractérisation identiques avant/après."],
  "Preuve : la requête <code>?class.classLoader.resources.dirContext.docBase=/</code> est bloquée par le filtre (400) ; l'inventaire liste 6 actions, 3 forms, 9 forwards, 2 JSP avec scriptlets ; après migration de <code>/incidents</code>, Playwright rejoue les mêmes parcours avec les mêmes captures, et Struts 1 ne sert plus que l'écran de création.")),

ch("Hibernate : fondations, mapping, cycle de vie des entités", 'c',
 ["Hibernate est l'implémentation de référence de Jakarta Persistence (JPA) : <code>SessionFactory</code>/<code>EntityManagerFactory</code> (une par application, coûteuse), <code>Session</code>/<code>EntityManager</code> (une par unité de travail, légère, non thread-safe), transactions.", "Une entité est une classe mappée sur une table (<code>@Entity</code>, <code>@Id</code>, <code>@Column</code>, <code>@Table</code>, types, énumérations, dates, conversions) ; le mapping XML (hbm.xml) existe encore dans le legacy.", "Cycle de vie : transient (nouvel objet) → persistent/managed (attaché à une session : ses changements sont détectés et écrits au flush) → detached (session fermée) → removed ; comprendre ce cycle explique 80 % des bugs Hibernate."],
 ["Configurer Hibernate (JPA) et écrire des entités correctement mappées", "Expliquer et manipuler les états d'une entité (persist, merge, detach, flush)", "Choisir identifiants, types et stratégies de génération"],
 [("Configuration et entité", "", """<!-- META-INF/persistence.xml (JPA) ; ou hibernate.cfg.xml en Hibernate natif -->
<persistence-unit name="crisis"><provider>org.hibernate.jpa.HibernatePersistenceProvider</provider>
  <properties><property name="jakarta.persistence.jdbc.url" value="jdbc:postgresql://db:5432/crisis"/><property name="jakarta.persistence.jdbc.user" value="crisis"/><property name="jakarta.persistence.jdbc.password" value="${DB_PASSWORD}"/>
    <property name="hibernate.hbm2ddl.auto" value="validate"/>            <!-- jamais update/create en production : Flyway -->
    <property name="hibernate.show_sql" value="false"/><property name="hibernate.format_sql" value="true"/><property name="hibernate.jdbc.batch_size" value="50"/><property name="hibernate.order_inserts" value="true"/>
    <property name="hibernate.connection.provider_class" value="com.zaxxer.hikari.hibernate.HikariConnectionProvider"/></properties></persistence-unit>
@Entity @Table(name = "incident", indexes = @Index(name = "idx_incident_zone_cree", columnList = "zone, cree_le"))
public class Incident {
  @Id @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "incident_seq") @SequenceGenerator(name = "incident_seq", sequenceName = "incident_seq", allocationSize = 50) private Long id;   // SEQUENCE : batching possible ; IDENTITY empêche le batch d'insertion
  @Column(nullable = false, length = 200) private String titre;
  @Enumerated(EnumType.STRING) @Column(nullable = false, length = 3) private Priorite priorite;   // STRING, jamais ORDINAL (réordonner l'enum casse les données)
  @Column(name = "cree_le", nullable = false, updatable = false) private Instant creeLe = Instant.now();
  @Version private int version;                                                                  // verrou optimiste (chapitre 10)
  @Convert(converter = ZoneConverter.class) private Zone zone;                                  // AttributeConverter pour un type maison
  @Embedded private Localisation localisation;                                                   // @Embeddable : colonnes lat/lon dans la même table
  protected Incident() {}                                                                        // constructeur sans argument requis (proxy) ; equals/hashCode sur l'identifiant métier ou stable, jamais sur l'id auto-généré seul
}"""),
  ("Cycle de vie", "", """EntityManager em = emf.createEntityManager(); em.getTransaction().begin();
Incident i = new Incident("Fuite", Priorite.P1);   // transient : Hibernate l'ignore
em.persist(i);                                      // managed : l'INSERT est différé au flush ; l'id SEQUENCE est attribué tout de suite
i.setTitre("Fuite gaz");                            // dirty checking : l'UPDATE partira au flush, sans appel explicite
em.flush();                                         // synchronise avec la base (INSERT, UPDATE) sans commit ; auto avant une requête et au commit
em.getTransaction().commit(); em.close();           // i devient detached
i.setTitre("Autre");                                // aucune écriture : détaché
EntityManager em2 = …; Incident m = em2.merge(i);   // merge : copie l'état dans une instance managed (m), i reste detached ; retour à utiliser
em2.remove(m);                                      // removed : DELETE au flush
em.find(Incident.class, 42L)      // cache de session (1er niveau) : deux find dans la même session = une requête
em.getReference(Incident.class, 42L)   // proxy paresseux : pas de requête tant qu'on ne lit qu'un champ autre que l'id ; LazyInitializationException si la session est fermée
Erreurs classiques : LazyInitializationException (accès hors session) ; detached entity passed to persist (utiliser merge) ; NonUniqueObjectException (deux instances du même id dans la session) ; TransientPropertyValueException (association vers un objet non persisté sans cascade)""")],
 [("Pourquoi <code>hbm2ddl.auto=update</code> est-il interdit en production ?", "Il ne fait que des ajouts approximatifs (jamais de suppression, types parfois faux), sans versionnage ni revue ; un schéma de production se migre avec Flyway/Liquibase et Hibernate se contente de <code>validate</code>."),
  ("Question d'entretien : différence entre <code>persist</code> et <code>merge</code> ?", "<code>persist</code> attache une instance nouvelle (transient) et la rend managed ; <code>merge</code> copie l'état d'une instance (détachée ou nouvelle) dans une instance managed qu'il renvoie. Après merge, on travaille sur la valeur retournée.")],
 ("Modèle CrisisShield en Hibernate", ["persistence.xml avec Hikari, Flyway pour le schéma, <code>validate</code> ; entités Incident, Zone (convertisseur), Localisation (embeddable), énumérations en STRING.", "Test JUnit avec Testcontainers PostgreSQL qui parcourt chaque transition d'état et provoque chaque exception classique, puis la corrige.", "Journal SQL activé le temps du test pour compter les requêtes (p6spy ou datasource-proxy)."],
  "Preuve : le test montre 1 INSERT différé au flush, 1 UPDATE par dirty checking, 0 requête au second <code>find</code>, une <code>LazyInitializationException</code> reproduite puis corrigée en chargeant dans la transaction ; Flyway V1 crée la séquence avec <code>INCREMENT 50</code> cohérent avec <code>allocationSize</code>.")),

ch("Associations, héritage et chargement (lazy, fetch, N+1)", 's',
 ["Associations : <code>@ManyToOne</code> (côté propriétaire, clé étrangère), <code>@OneToMany(mappedBy)</code> (côté inverse), <code>@OneToOne</code>, <code>@ManyToMany</code> (table de jointure, à remplacer par une entité de liaison dès qu'il y a des attributs) ; cascade et orphanRemoval décident du sort des enfants.", "Chargement : LAZY partout par défaut (y compris <code>@ManyToOne</code>), puis chargement explicite par cas d'usage (JOIN FETCH, EntityGraph, batch fetching) ; EAGER global est la source des jointures cartésiennes et des lenteurs.", "Héritage : SINGLE_TABLE (rapide, colonnes nullables), JOINED (normalisé, jointures), TABLE_PER_CLASS (à éviter) ; <code>@MappedSuperclass</code> pour partager des champs sans polymorphisme."],
 ["Mapper des associations bidirectionnelles sans piège (propriétaire, equals, helpers)", "Diagnostiquer et corriger un N+1 par fetch join, EntityGraph ou batch", "Choisir une stratégie d'héritage"],
 [("Associations", "", """@Entity public class Incident {
  @ManyToOne(fetch = FetchType.LAZY, optional = false) @JoinColumn(name = "zone_id") private Zone zone;          // LAZY explicite : le défaut de @ManyToOne est EAGER !
  @OneToMany(mappedBy = "incident", cascade = CascadeType.ALL, orphanRemoval = true) private List<Evenement> evenements = new ArrayList<>();
  public void ajouter(Evenement e) { evenements.add(e); e.setIncident(this); }                                  // helper : maintient les deux côtés
  public void retirer(Evenement e) { evenements.remove(e); e.setIncident(null); }                                // orphanRemoval → DELETE
}
@Entity public class Evenement { @Id @GeneratedValue Long id; @ManyToOne(fetch = FetchType.LAZY) @JoinColumn(name = "incident_id") private Incident incident; … }
// ManyToMany avec attributs → entité de liaison : @Entity class Affectation { @EmbeddedId AffectationId id; @ManyToOne @MapsId("incidentId") Incident incident; @ManyToOne @MapsId("equipeId") Equipe equipe; Instant depuis; }
// Set plutôt que List pour les collections non ordonnées (List + @OrderColumn si l'ordre compte ; un List sans ordre = « bag » : suppression coûteuse)
// héritage : @Inheritance(strategy = InheritanceType.SINGLE_TABLE) @DiscriminatorColumn(name = "type") sur Notification ; sous-classes Sms, Email avec @DiscriminatorValue"""),
  ("N+1 et chargement", "", """List<Incident> xs = em.createQuery("select i from Incident i", Incident.class).getResultList();   // 1 requête
for (Incident i : xs) System.out.println(i.getZone().getNom());                                    // N requêtes : N+1
// 1) JOIN FETCH : select distinct i from Incident i join fetch i.zone left join fetch i.evenements where i.priorite = :p   (une seule collection fetchée par requête : sinon produit cartésien / MultipleBagFetchException)
// 2) EntityGraph : @NamedEntityGraph(name = "Incident.avecZone", attributeNodes = @NamedAttributeNode("zone")) ; em.find(Incident.class, id, Map.of("jakarta.persistence.fetchgraph", em.getEntityGraph("Incident.avecZone")))
// 3) batch fetching : @BatchSize(size = 50) sur la collection ou hibernate.default_batch_fetch_size=50 : N+1 devient N/50+1 avec IN (...)
// 4) subselect : @Fetch(FetchMode.SUBSELECT) : la collection de tous les incidents de la requête en une sous-requête
// 5) projection DTO quand on n'a pas besoin de l'entité : select new fr.crisis.dto.IncidentLigne(i.id, i.titre, z.nom) from Incident i join i.zone z
// détecter : hibernate.generate_statistics + Statistics.getPrepareStatementCount() dans un test ; ou log SQL + compteur ; règle : un test d'intégration par écran qui borne le nombre de requêtes""")],
 [("Une liste de 200 incidents affiche 401 requêtes SQL : d'où ça vient ?", "1 pour la liste + 200 pour <code>zone</code> (ManyToOne) + 200 pour <code>evenements</code> (collection) : deux N+1. JOIN FETCH sur zone, batch ou subselect sur evenements, ou un DTO."),
  ("Question d'entretien : pourquoi <code>select distinct</code> avec un fetch de collection ?", "La jointure duplique la ligne parent pour chaque enfant ; <code>distinct</code> (ou Hibernate 6 qui dédoublonne automatiquement) garantit une instance parent par entité. Et une seule collection par fetch, sinon produit cartésien.")],
 ("Modèle complet et chasse au N+1", ["Zone, Incident, Evenement, Affectation (liaison), Notification (héritage SINGLE_TABLE) avec helpers, Set/List justifiés, equals/hashCode corrects.", "Test qui compte les requêtes pour trois écrans (liste, détail, tableau de bord) : version naïve puis corrigée (fetch join, EntityGraph, batch, DTO).", "Tableau : écran → requêtes avant → technique → requêtes après → temps."],
  "Résultat typique : liste 401 → 2 requêtes (fetch zone + subselect événements) ; détail 12 → 1 (EntityGraph) ; tableau de bord 1 200 → 1 (DTO agrégé) ; temps 3 800 ms → 60 ms sur 5 000 incidents en Testcontainers.")),

ch("Requêtes : JPQL/HQL, Criteria, natives, pagination, projections", 's',
 ["JPQL/HQL parlent en entités et propriétés, pas en tables : jointures par association, fonctions, sous-requêtes, agrégats, <code>new</code> pour projeter en DTO ; requêtes nommées compilées au démarrage.", "Criteria API (JPA) et le métamodèle statique (<code>Incident_</code>) construisent des requêtes dynamiques typées (filtres optionnels) ; les spécifications Spring Data les rendent composables.", "SQL natif pour ce que JPQL ne sait pas (fonctions spécifiques, CTE, fenêtres, PostGIS) avec mapping vers entités ou DTO ; pagination par <code>setFirstResult/setMaxResults</code> (avec ordre stable) ou keyset pour les gros volumes."],
 ["Écrire des requêtes JPQL efficaces avec paramètres, projections et agrégats", "Construire des filtres dynamiques en Criteria typée", "Paginer et utiliser le SQL natif à bon escient"],
 [("JPQL", "", """@NamedQuery(name = "Incident.ouvertsParZone", query = "select i from Incident i join fetch i.zone z where z.code = :zone and i.statut = fr.crisis.Statut.OUVERT order by i.creeLe desc")
List<Incident> xs = em.createNamedQuery("Incident.ouvertsParZone", Incident.class).setParameter("zone", "N1").setFirstResult(0).setMaxResults(20).getResultList();   // paramètres nommés : jamais de concaténation (injection JPQL)
// agrégats et DTO : select new fr.crisis.dto.StatZone(z.code, count(i), avg(i.dureeMinutes)) from Incident i join i.zone z where i.creeLe >= :depuis group by z.code having count(i) > 5
// sous-requête : select i from Incident i where i.id in (select e.incident.id from Evenement e where e.type = 'ESCALADE')
// exists : where exists (select 1 from Affectation a where a.incident = i and a.equipe.nom = :equipe)
// mise à jour en masse (contourne le cache de session : clear après) : update Incident i set i.statut = :ferme where i.creeLe < :limite
// Hibernate 6 : fonctions standard portables (year(), left(), etc.), tuples, fetch en pagination avec avertissement « HHH90003004 firstResult/maxResults specified with collection fetch; applying in memory » → ne jamais paginer un fetch de collection : deux requêtes (ids paginés puis fetch par in)"""),
  ("Criteria, natif, pagination", "", """CriteriaBuilder cb = em.getCriteriaBuilder(); CriteriaQuery<Incident> q = cb.createQuery(Incident.class); Root<Incident> i = q.from(Incident.class);
List<Predicate> p = new ArrayList<>();
if (f.zone() != null) p.add(cb.equal(i.get(Incident_.zone).get(Zone_.code), f.zone()));
if (f.priorite() != null) p.add(cb.equal(i.get(Incident_.priorite), f.priorite()));
if (f.texte() != null) p.add(cb.like(cb.lower(i.get(Incident_.titre)), "%" + f.texte().toLowerCase() + "%"));
q.select(i).where(p.toArray(Predicate[]::new)).orderBy(cb.desc(i.get(Incident_.creeLe)), cb.desc(i.get(Incident_.id)));   // ordre stable pour paginer
TypedQuery<Incident> tq = em.createQuery(q).setFirstResult(page * 20).setMaxResults(20);
// count séparé pour le total : CriteriaQuery<Long> c = cb.createQuery(Long.class); c.select(cb.count(c.from(Incident.class))).where(…)
// keyset (gros volumes) : where (i.creeLe, i.id) < (:creeLe, :id) order by i.creeLe desc, i.id desc limit 20 → pas d'OFFSET coûteux
// natif : em.createNativeQuery("select z.code, count(*) from incident i join zone z on z.id = i.zone_id where i.geom && ST_MakeEnvelope(:x1,:y1,:x2,:y2,4326) group by z.code", Tuple.class)
// natif vers entité : createNativeQuery(sql, Incident.class) (colonnes = mapping) ; vers DTO : @SqlResultSetMapping + @ConstructorResult
// pièges : select * natif avec entité et colonnes manquantes ; N+1 après une requête native ; cache de session non invalidé par une requête native de modification (em.clear())""")],
 [("Pourquoi JPQL n'est-il pas sensible à l'injection si on utilise des paramètres, mais l'est avec la concaténation ?", "Les paramètres sont liés par JDBC (PreparedStatement) après compilation ; une valeur concaténée fait partie de la requête et peut en changer la structure, comme en SQL."),
  ("Question d'entretien : OFFSET 100000 est lent, que faire ?", "Pagination par keyset : filtrer sur la dernière valeur vue (colonne triée + id), index couvrant ; l'OFFSET oblige la base à parcourir et jeter les lignes précédentes.")],
 ("Couche de requêtes", ["Requêtes nommées pour les écrans, DTO de statistiques, mise à jour en masse avec clear ; filtres dynamiques en Criteria avec métamodèle généré (hibernate-jpamodelgen).", "Pagination classique + count et pagination keyset ; comparaison EXPLAIN à la page 1 et à la page 5 000.", "Requête native PostGIS mappée en DTO ; test qui vérifie qu'aucune requête n'est construite par concaténation (grep en CI)."],
  "Preuve : keyset page 5 000 : 3 ms contre 420 ms en OFFSET ; le métamodèle rend une faute de frappe de propriété impossible (erreur de compilation) ; la native PostGIS renvoie les incidents d'une zone en 5 ms avec l'index GIST du cours PostgreSQL.")),

ch("Transactions, verrouillage, caches et performance", 'e',
 ["Une transaction encadre l'unité de travail : <code>@Transactional</code> (Spring) ou <code>em.getTransaction()</code> ; propagation (REQUIRED, REQUIRES_NEW), isolation, readOnly (optimisations : pas de dirty checking, flush manuel), rollback sur exception runtime.", "Concurrence : verrou optimiste (<code>@Version</code>, <code>OptimisticLockException</code> à gérer par retry ou message) par défaut ; verrou pessimiste (<code>LockModeType.PESSIMISTIC_WRITE</code> = SELECT … FOR UPDATE) pour les sections critiques courtes ; jamais de verrou pessimiste long.", "Caches : 1er niveau (session, toujours), 2e niveau (Ehcache/Infinispan/Redis : entités de référence rarement modifiées, avec stratégie et TTL), cache de requêtes (rarement utile) ; performance : batch d'inserts/updates, StatelessSession pour les imports, fetch size, statistiques, index, et la question à poser toujours : « combien de requêtes ? »."],
 ["Configurer transactions, isolation et readOnly correctement", "Gérer la concurrence par verrou optimiste et pessimiste", "Mettre en place le cache de second niveau et les traitements en masse"],
 [("Transactions et verrous", "", """@Service public class IncidentService {
  @Transactional public void escalader(Long id) { Incident i = em.find(Incident.class, id); i.escalader(); }                   // commit au retour ; rollback sur RuntimeException ; réessai à prévoir sur OptimisticLockException
  @Transactional(readOnly = true) public List<IncidentLigne> liste(Filtre f) { … }                                             // flush désactivé, connexion en lecture seule (réplica possible)
  @Transactional(propagation = Propagation.REQUIRES_NEW) public void journaliser(String msg) { … }                             // commité même si l'appelant échoue (audit)
  @Retryable(retryFor = OptimisticLockException.class, maxAttempts = 3) @Transactional public void cloturer(Long id, int versionVue) { Incident i = em.find(Incident.class, id); if (i.getVersion() != versionVue) throw new OptimisticLockException("modifié entre-temps"); i.cloturer(); }   // version transportée par le formulaire : détection de mise à jour perdue
  @Transactional public void reserverEquipe(Long equipeId, Long incidentId) { Equipe e = em.find(Equipe.class, equipeId, LockModeType.PESSIMISTIC_WRITE); if (e.disponible()) e.affecter(incidentId); }   // SELECT … FOR UPDATE, court ; jakarta.persistence.lock.timeout pour ne pas attendre indéfiniment
}
// pièges : @Transactional sur une méthode privée ou appelée depuis la même classe (proxy ignoré) ; exception checked qui ne rollback pas (rollbackFor) ; transaction ouverte pendant un appel HTTP externe (verrous et connexions tenus) ; Open Session In View activé (spring.jpa.open-in-view=false !) qui masque les N+1 et garde la connexion pendant le rendu"""),
  ("Caches et masse", "", """// 2e niveau : hibernate.cache.use_second_level_cache=true, hibernate.cache.region.factory_class=jcache (Ehcache 3) ; @Cacheable @org.hibernate.annotations.Cache(usage = CacheConcurrencyStrategy.READ_WRITE) sur Zone, Equipe (référentiels) ; jamais sur des entités très écrites ; TTL et taille par région ; invalidation : Hibernate le fait pour ses propres écritures, pas pour une requête native ni pour un autre service → TTL court ou cache distribué
// cache de requêtes : hibernate.cache.use_query_cache + setHint("org.hibernate.cacheable", true) : utile seulement pour des requêtes identiques très fréquentes sur des tables stables
// batch : hibernate.jdbc.batch_size=50, order_inserts, order_updates ; SEQUENCE (pas IDENTITY) ; dans la boucle : if (i % 50 == 0) { em.flush(); em.clear(); } pour ne pas saturer le cache de session
// StatelessSession (Hibernate) pour un import de millions de lignes : pas de cache, pas de dirty checking, pas de cascade
// diagnostic : hibernate.generate_statistics=true → Statistics (requêtes, hits de cache, temps) ; log org.hibernate.SQL + BasicBinder pour les paramètres ; slow query log de PostgreSQL ; EXPLAIN sur les requêtes générées ; index sur toutes les clés étrangères (Hibernate n'en crée pas)""")],
 [("Deux opérateurs clôturent le même incident en même temps : que se passe-t-il avec <code>@Version</code> ?", "Le second UPDATE a <code>where version = 3</code> alors que la ligne est en 4 : 0 ligne modifiée → <code>OptimisticLockException</code> → rollback ; on informe l'utilisateur ou on réessaie avec les données fraîches. Sans @Version : mise à jour perdue silencieuse."),
  ("Question d'entretien : pourquoi désactiver Open Session In View ?", "Il garde la session (et la connexion) ouverte jusqu'à la fin du rendu de la vue : les accès paresseux dans la JSP passent, donc les N+1 sont invisibles en dev, et le pool se vide en prod. Charger ce dont la vue a besoin dans la transaction du service, puis fermer.")],
 ("Concurrence, cache et masse", ["Tests Testcontainers : mise à jour perdue reproduite sans @Version puis détectée avec ; verrou pessimiste avec timeout et deadlock provoqué entre deux threads.", "Cache 2e niveau Ehcache sur Zone/Equipe : statistiques de hits ; invalidation manquée après une requête native, puis corrigée.", "Import de 1 M d'incidents : boucle naïve (OOM) → batch + flush/clear → StatelessSession ; temps et mémoire mesurés."],
  "Résultats attendus : mise à jour perdue visible sans version, <code>OptimisticLockException</code> avec ; deadlock détecté par PostgreSQL en 1 s et une transaction annulée ; cache : 99 % de hits sur Zone ; import 1 M : naïf OOM à 300 k, batch 4 min / 400 Mo, StatelessSession 2 min / 80 Mo.")),

ch("Hibernate en production : Spring Data, Flyway, Envers, multi-tenant, tests, débogage", 'e',
 ["Spring Data JPA couvre 80 % des dépôts (méthodes dérivées, <code>@Query</code>, projections, spécifications, pagination) ; le reste passe par un dépôt personnalisé avec EntityManager ou jOOQ pour le SQL avancé.", "Schéma par Flyway (expand/contract, <code>lock_timeout</code>), audit par Envers (<code>@Audited</code> : tables _AUD et révisions), multi-tenant par colonne (<code>@TenantId</code>, filtre) ou par schéma/base, chiffrement de colonnes par convertisseur.", "Exploitation : pool Hikari dimensionné, statistiques et métriques (Micrometer), logs SQL ciblés, mises à jour majeures Hibernate (5 → 6 : jakarta, changements JPQL) préparées par les tests."],
 ["Structurer une couche de persistance Spring Data propre", "Mettre en place migrations, audit, multi-tenant", "Diagnostiquer les problèmes Hibernate en production et migrer de version"],
 [("Spring Data et migrations", "", """public interface IncidentRepository extends JpaRepository<Incident, Long>, JpaSpecificationExecutor<Incident> {
  @EntityGraph(attributePaths = "zone") Page<Incident> findByStatut(Statut s, Pageable p);                                    // méthode dérivée + graphe
  @Query("select new fr.crisis.dto.StatZone(z.code, count(i)) from Incident i join i.zone z group by z.code") List<StatZone> statsParZone();
  interface IncidentLigne { Long getId(); String getTitre(); @Value("#{target.zone.code}") String getZone(); }  Page<IncidentLigne> findByPriorite(Priorite p, Pageable pg);   // projection interface
  @Modifying @Query("update Incident i set i.statut = :ferme where i.creeLe < :limite") int fermerAnciens(Statut ferme, Instant limite);   // + @Transactional, clearAutomatically = true
}
// spécifications composables : IncidentSpecs.zone("N1").and(IncidentSpecs.texte("gaz")) ; repository.findAll(spec, PageRequest.of(0, 20, Sort.by("creeLe").descending()))
// application.yml : spring.jpa.open-in-view=false ; spring.jpa.properties.hibernate.jdbc.batch_size=50 ; spring.datasource.hikari.maximum-pool-size=10 ; spring.flyway.locations=classpath:db/migration
-- V12__incident_statut.sql : ALTER TABLE incident ADD COLUMN statut VARCHAR(10); UPDATE … par lots ; V13 : SET NOT NULL après backfill (expand/contract) ; lock_timeout=2s dans flyway.initSql"""),
  ("Envers, multi-tenant, débogage", "", """@Audited @Entity public class Incident { … }   // tables incident_aud + revinfo ; AuditReader r = AuditReaderFactory.get(em); r.createQuery().forRevisionsOfEntity(Incident.class, false, true).add(AuditEntity.id().eq(42L)).getResultList() ; @RevisionEntity avec l'utilisateur
// multi-tenant par colonne (Hibernate 6) : @TenantId private String org ; CurrentTenantIdentifierResolver lit l'organisation du jeton ; Hibernate filtre automatiquement lectures et écritures ; par schéma : MultiTenantConnectionProvider qui fait SET search_path ; par base : un DataSource par tenant (AbstractRoutingDataSource)
// chiffrement : @Convert(converter = ChiffreConverter.class) (AES-GCM via Vault Transit du niveau 7) sur les colonnes sensibles ; pas de requête possible sur la valeur chiffrée
// débogage prod : hibernate.generate_statistics + métriques Micrometer (hibernate.query.executions, sessions, cache hits) ; logging.level.org.hibernate.SQL=DEBUG ponctuellement ; datasource-proxy pour compter par requête HTTP ; pg_stat_statements pour voir les requêtes générées telles quelles ; « connection leak » Hikari : leakDetectionThreshold=20000
// Hibernate 5 → 6 : javax → jakarta, JPQL plus strict (fonctions, comparaisons de types), IDENTITY/SEQUENCE (nouvelle stratégie par défaut), suppression de Criteria legacy, @Type en @JdbcTypeCode/@JavaType ; méthode : tests d'intégration verts avant, mise à jour des dépendances, correction des avertissements, rejeu des tests""")],
 [("Une méthode Spring Data <code>findByZoneCodeAndPrioriteAndStatutOrderByCreeLeDesc</code> : bonne idée ?", "Lisible mais rigide et non composable ; au-delà de deux critères, une spécification ou une <code>@Query</code> nommée est plus claire et évite le N+1 (on y met le fetch)."),
  ("Question d'entretien : comment isoler les données de deux clients dans une même base ?", "Colonne de tenant avec filtre automatique (@TenantId) pour le coût minimal, schéma par tenant pour l'isolation logique et les migrations séparées, base par tenant pour l'isolation forte ; dans tous les cas le tenant vient de l'identité (jeton), jamais d'un paramètre.")],
 ("Persistance prête pour la production", ["Dépôts Spring Data avec EntityGraph, projections, spécifications, modification en masse ; Flyway expand/contract ; Envers sur Incident avec utilisateur en révision.", "Multi-tenant par colonne avec test d'isolation (un tenant ne lit jamais l'autre, même par requête native contrôlée) ; convertisseur de chiffrement.", "Tableau de bord Micrometer/Grafana des métriques Hibernate et Hikari ; migration Hibernate 5 → 6 sur une branche avec la liste des corrections."],
  "Preuve : l'historique Envers montre trois révisions avec l'auteur ; le test d'isolation échoue si on retire <code>@TenantId</code> ; Grafana montre les requêtes par seconde et les hits de cache ; la branche 6.x compile avec 14 corrections listées et tous les tests d'intégration verts.")),

ch("Projet complet, questions d'entretien et fiche de révision", 'e',
 ["Le projet : CrisisShield web classique en Struts 6 + Tiles + JSP + Hibernate 6 + PostgreSQL, Spring pour l'injection et les transactions, Flyway, tests Testcontainers, Docker Compose, pipeline GitLab avec OWASP ZAP et dependency-check ; puis la variante legacy Struts 1 pour l'exercice de migration.", "Les questions d'entretien portent sur le cycle de requête Struts, la sécurité OGNL, le cycle de vie des entités, le N+1, les verrous, les caches, et le jugement (quand utiliser quoi, comment migrer).", "La fiche condense les 20 concepts, 20 annotations, 20 pièges et 5 schémas à savoir refaire."],
 ["Livrer et expliquer le projet complet", "Répondre aux 40 questions d'entretien", "Réciter la fiche de révision"],
 [("Quarante questions", "", """1 Cycle d'une requête Struts 2 ? Filtre → mapper → proxy → intercepteurs → action → résultat → intercepteurs après. 2 Rôle de l'intercepteur params/validation/workflow ? Injection, validation, retour input. 3 ValueStack/OGNL ? Pile d'objets et langage d'expression ; danger si évalue une entrée. 4 Pourquoi devMode=false ? Expose la pile et le debug. 5 S2-045 ? OGNL dans le Content-Type multipart → RCE. 6 Struts 1 vs 2 ? ActionServlet/ActionForm vs POJO/intercepteurs ; Struts 1 fin de vie. 7 Migrer Struts 1 vers quoi ? Spring MVC par strangler. 8 forward vs redirect ? Même requête vs 302 ; PRG. 9 JSP scriptlets ? Interdits : EL + JSTL. 10 XSS en JSP ? c:out/fn:escapeXml partout ; ${} n'échappe pas. 11 CSRF ? Jeton par session vérifié sur POST ; s:token. 12 Portées ? page, request, session, application ; session = état serveur à limiter. 13 Tiles ? Layout central + définitions héritées. 14 SessionFactory vs Session ? Une par application (lourde) vs une par unité de travail (légère, non thread-safe). 15 États d'une entité ? transient, managed, detached, removed. 16 persist vs merge ? Attache une nouvelle vs copie dans une managed retournée. 17 LazyInitializationException ? Accès paresseux hors session ; charger dans la transaction, pas OSIV. 18 N+1 ? 1 + N requêtes sur une association ; fetch join, EntityGraph, batch, DTO. 19 Défaut de fetch ? ToOne EAGER, ToMany LAZY ; mettre LAZY partout. 20 Propriétaire d'une association ? Le côté avec la clé étrangère (@JoinColumn) ; mappedBy côté inverse. 21 equals/hashCode d'entité ? Sur une clé métier ou un id stable ; pas sur un id nul. 22 IDENTITY vs SEQUENCE ? IDENTITY empêche le batch d'insertion ; SEQUENCE avec allocationSize. 23 @Version ? Verrou optimiste : détection de mise à jour perdue. 24 Pessimiste ? SELECT FOR UPDATE, court, avec timeout. 25 Cache 1er/2e niveau ? Session ; partagé pour les référentiels avec stratégie et TTL. 26 hbm2ddl update ? Jamais en prod : Flyway + validate. 27 readOnly ? Pas de flush ni de dirty checking ; réplica possible. 28 @Transactional ignoré ? Méthode privée ou appel interne (proxy). 29 OSIV ? À désactiver : masque les N+1, tient la connexion. 30 JPQL vs natif ? Entités portables vs SQL spécifique ; les deux avec paramètres. 31 Criteria ? Requêtes dynamiques typées avec métamodèle. 32 Pagination keyset ? Filtre sur la dernière valeur au lieu d'OFFSET. 33 Héritage ? SINGLE_TABLE rapide, JOINED normalisé, TABLE_PER_CLASS à éviter. 34 ManyToMany ? Entité de liaison dès qu'il y a des attributs. 35 Bag ? List sans ordre : suppressions coûteuses ; Set ou @OrderColumn. 36 Batch ? batch_size + order_inserts + flush/clear ; StatelessSession pour la masse. 37 Envers ? Tables _AUD et révisions par @Audited. 38 Multi-tenant ? Colonne (@TenantId), schéma, base ; tenant depuis l'identité. 39 Hibernate 5 → 6 ? jakarta, JPQL strict, nouvelles annotations de types ; tests avant. 40 Combien de requêtes ? La question à poser à chaque écran ; test qui borne le compte."""),
  ("Fiche condensée", "", """ANNOTATIONS : @Entity @Table @Id @GeneratedValue @SequenceGenerator @Column @Enumerated(STRING) @Version @Embedded @Convert @ManyToOne(LAZY) @OneToMany(mappedBy, cascade, orphanRemoval) @JoinColumn @Inheritance @DiscriminatorColumn @NamedQuery @NamedEntityGraph @BatchSize @Cacheable @Audited @TenantId @Transactional(readOnly, propagation)
STRUTS : struts.xml (package, namespace, action, result, interceptor-stack) · ActionSupport · Preparable · ModelDriven · validation.xml · s:form s:textfield s:select s:iterator s:property s:url s:token · plugins Convention/JSON/REST/Tiles/Spring · constantes devMode, DynamicMethodInvocation, allowStaticMethodAccess, excludeParams
JSP : c:out c:forEach c:choose c:url c:set fmt:message fmt:formatDate fn:escapeXml · tag files · WEB-INF · scripting-invalid · PRG · session-config
PIÈGES : ${} sans échappement · devMode en prod · Struts non mis à jour · ActionForm en session · EAGER par défaut sur ToOne · N+1 · fetch de deux collections · pagination + fetch · IDENTITY et batch · equals sur id nul · hbm2ddl update · OSIV · @Transactional interne · verrou pessimiste long · cache 2e niveau sur entités écrites · requête native sans clear
SCHÉMAS : cycle Struts (filtre → intercepteurs → action → résultat) · états d'une entité · N+1 et ses quatre remèdes · verrou optimiste (version) · architecture du projet (JSP/Tiles → actions → services Spring → Hibernate → PostgreSQL)""")],
 [("Comment présenter ce projet en entretien pour une mission legacy ?", "Montrer qu'on sait lire et sécuriser l'existant (Struts 1, OGNL, XSS), qu'on mesure (compte de requêtes, N+1), et qu'on migre par étapes sans big bang ; une histoire STAR sur une lenteur Hibernate diagnostiquée vaut plus que la liste des annotations."),
  ("Que dire si on demande « Struts, c'est mort ? »", "Le projet open source vit (6.x, Jakarta), mais plus aucun projet neuf ne le choisit ; la valeur est de maintenir et migrer l'existant en sécurité. Struts 1, lui, est mort depuis 2013 et doit être isolé puis remplacé.")],
 ("Projet final", ["Application complète Struts 6 + JSP/Tiles + Hibernate 6 + Spring + Flyway + PostgreSQL en Compose, avec tests Testcontainers, compteur de requêtes par écran, ZAP et dependency-check en CI.", "Variante Struts 1 sécurisée et migration strangler d'un écran vers Spring Boot.", "Dossier de 6 pages : architecture, sécurité, performance (tableau N+1), migration, et les 40 questions répondues à voix haute chronométrées."],
  "Objectif : chaque écran borné à ≤ 3 requêtes SQL par un test, 0 alerte High ZAP, 0 CVE Struts/Hibernate en dependency-check, migration d'écran rejouée par Playwright sans différence, 36/40 questions en moins de 30 s.")),
]

d = sys.argv[1]
page('cours-struts-hibernate-jsp.html', 'Struts, Hibernate et JSP — de zéro à expert', "Douze chapitres pour maîtriser le web Java classique et son legacy : Servlets et JSP (EL, JSTL, tags, Tiles, i18n, sécurité), Struts 2/6 (architecture, actions, validation, OGNL, intercepteurs, plugins, sécurité S2-xxx), Struts 1 et sa migration, Hibernate 6 (mapping, cycle de vie, associations, N+1, JPQL/Criteria, transactions, verrous, caches, Spring Data, Flyway, Envers, multi-tenant), projet complet et 40 questions d'entretien. Tout en Docker (Maven, Tomcat, PostgreSQL), chaque chapitre a ses exercices corrigés et un travail pratique avec correction type.", "≈ 50 h de travail · prérequis : Java confirmé, notions de SQL, Docker Desktop · complète le cours PostgreSQL du niveau 8 (TP 47) et le cours Java PKI pour la sécurité.", SH, [('cours-java-pki-signature-electronique.html', 'Java PKI'), ('cours-data-platform-aws-talend.html', 'Data Platform'), ('devops-niveau-7-securite-devsecops.html', 'DevOps niveau 7')])
