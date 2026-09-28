"""Génère cours-01-react.html et cours-02-angular.html (zéro → expert) dans le gabarit du parcours.
Usage : python3 front_gen.py <dossier cours-devops>"""
import re, sys, html as H, pathlib
d = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].endswith('cours-devops') else '/home/claude/work/cours-devops')
HEAD = re.search(r'^.*?</head>', (d/'devops-00-fondations.html').read_text(), flags=re.S).group(0)
EXTRA = """
.pagenav{display:flex;flex-wrap:wrap;gap:.6rem;margin-bottom:1rem;font-size:.9rem}
.pagenav a{color:#fff;text-decoration:none;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.22);padding:.3rem .75rem;border-radius:6px}
.footnav{display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap;margin-top:2rem;padding-top:1.2rem;border-top:1px solid var(--line)}
.footnav a{text-decoration:none;font-weight:700;background:var(--paper);border:1px solid var(--line);padding:.6rem 1rem;border-radius:var(--radius)}
.toc{background:var(--paper);border:1px solid var(--line);border-radius:var(--radius);padding:1rem 1.2rem;margin:0 0 1.5rem}
.toc ol{margin:.4rem 0 0;padding-left:1.3rem;columns:2;column-gap:2rem}
.toc li{break-inside:avoid;margin:.2rem 0}
@media(max-width:700px){.toc ol{columns:1}}
body{padding-bottom:2rem}
@media print{.pagenav,.footnav{display:none}}
</style>"""
HEAD = HEAD.replace('</style>', EXTRA, 1)
LVL = {'j': ('lvl-junior', 'Débutant'), 'c': ('lvl-confirme', 'Confirmé'), 's': ('lvl-senior', 'Senior'), 'e': ('lvl-expert', 'Expert')}

def page(fn, title, lead, meta, chapters, other):
    h = re.sub(r'<title>[^<]*</title>', f'<title>{H.escape(title)}</title>', HEAD)
    b = f'''<body>
<header class="hero"><div class="in">
<div class="pagenav"><a href="index.html">← Accueil du parcours</a>{''.join(f'<a href="{h}">{l}</a>' for h, l in other)}</div>
<div class="level">Cours frontend — de zéro à expert</div>
<h1>{H.escape(title)}</h1>
<p class="lead">{lead}</p>
<p>{meta}</p>
</div></header>
<div class="single with-toc">
<div class="toc"><strong>Sommaire</strong><ol>{''.join(f'<li><a href="#c{i}">{H.escape(c["t"])}</a></li>' for i, c in enumerate(chapters, 1))}</ol></div>
'''
    for i, c in enumerate(chapters, 1):
        cls, lbl = LVL[c['l']]
        b += f'<article id="c{i}"><div class="chaphead"><span class="chapnum">Chapitre {i}</span><span class="badge {cls}">{lbl}</span></div><h2>{H.escape(c["t"])}</h2>\n'
        b += f'<div class="bref"><span class="tag">En 30 secondes</span><ol>{"".join(f"<li>{x}</li>" for x in c["bref"])}</ol></div>\n'
        b += f'<div class="objectifs"><strong>À la fin de ce chapitre, tu sauras</strong><ul>{"".join(f"<li>{x}</li>" for x in c["obj"])}</ul></div>\n'
        for st, txt, code in c['sec']:
            b += f'<h3>{H.escape(st)}</h3><p>{txt}</p>'
            if code: b += f'<pre><code>{H.escape(code)}</code></pre>\n'
        for k, (q, s) in enumerate(c['exo'], 1):
            b += f'<div class="exo"><span class="tag">Exercice {i}.{k}</span><p>{q}</p><details><summary>Corrigé</summary><div class="sol">{s}</div></details></div>\n'
        tt, steps, sol = c['tp']
        b += f'<div class="tp"><span class="tag">Travail pratique {i} — {H.escape(tt)}</span><ol>{"".join(f"<li>{x}</li>" for x in steps)}</ol><details><summary>Correction type</summary><div class="sol">{sol}</div></details></div>\n'
        b += '</article>\n'
    b += f'''<div class="footnav"><a href="index.html">← Accueil du parcours</a><a href="{other[0][0]}">{other[0][1]} →</a></div>
</div>
<script>
(function(){{ var root=document.documentElement; try{{ var t=localStorage.getItem('devops-theme'); if(t) root.setAttribute('data-theme',t); }}catch(e){{}}
  document.querySelectorAll('pre').forEach(function(pre){{ var b=document.createElement('button'); b.type='button'; b.className='copy'; b.textContent='Copier';
    b.addEventListener('click',function(){{ var t=pre.querySelector('code').textContent; navigator.clipboard.writeText(t).then(function(){{ b.textContent='Copié !'; setTimeout(function(){{ b.textContent='Copier'; }},1500); }}); }}); pre.appendChild(b); }});
}})();
</script>
</body></html>'''
    (d/fn).write_text(h + '\n' + b); print(fn, len(chapters), 'chapitres')

def ch(t, l, bref, obj, sec, exo, tp): return dict(t=t, l=l, bref=bref, obj=obj, sec=sec, exo=exo, tp=tp)
DOCK = "Tout tourne en conteneur : <code>docker run --rm -it -v \"$PWD:/app\" -w /app -p 5173:5173 node:22 bash</code>, puis les commandes npm dedans (ou un <code>compose.yaml</code> avec un service <code>node</code>). Rien n'est installé sur le poste."

# ================================================================ REACT
REACT = [
ch("JavaScript moderne et TypeScript : le socle", 'j',
 ["React est du JavaScript : modules, fonctions fléchées, destructuring, promesses et <code>async/await</code> se lisent avant tout composant.", "TypeScript ajoute des types vérifiés à la compilation : un composant typé documente ses props et ses états.", "Le toolchain (Node 22, npm, Vite) tourne dans un conteneur ; le navigateur ne voit que du JS transpilé."],
 ["Lire et écrire du JS ES2022 sans surprise (immutabilité, spread, optional chaining)", "Typer une fonction, un objet, une union discriminée en TypeScript", "Lancer un projet Node en Docker sans rien installer"],
 [("Ce qu'il faut savoir du langage", "Cinq idées reviennent partout dans React : les fonctions sont des valeurs (on passe des callbacks), les objets et tableaux se copient au lieu de se modifier (spread), le destructuring lit props et états, les promesses gèrent l'asynchrone, les modules découpent le code.",
"""const user = { id: 1, name: 'Alice', roles: ['ops'] };
const updated = { ...user, name: 'Alice B.' };            // nouvel objet, user intact
const [first, ...rest] = user.roles;                       // destructuring
const label = user.profile?.city ?? 'inconnue';           // optional chaining, nullish
const ids = [3, 1, 2].filter(n => n > 1).map(n => n * 2);  // pas de boucle for
async function load() { try { const r = await fetch('/api/incidents'); if (!r.ok) throw new Error(r.statusText); return await r.json(); } catch (e) { console.error(e); return []; } }"""),
  ("TypeScript : types, unions, génériques", "Le type d'une prop ou d'un état est le contrat du composant. Les unions discriminées modélisent un état de chargement sans booléens contradictoires ; les génériques typent un hook ou une liste réutilisable.",
"""type Priority = 'P1' | 'P2' | 'P3';
interface Incident { id: number; title: string; priority: Priority; zone: string; createdAt: string }
type Loading<T> = { status: 'idle' } | { status: 'loading' } | { status: 'error'; error: string } | { status: 'ok'; data: T };
function describe(s: Loading<Incident[]>): string {
  switch (s.status) { case 'ok': return `${s.data.length} incidents`; case 'error': return s.error; default: return '…'; }   // exhaustif : TS refuse un cas oublié
}
const byPriority = <T extends { priority: Priority }>(xs: T[], p: Priority) => xs.filter(x => x.priority === p);"""),
  ("Le poste : Node en Docker", DOCK, """# compose.yaml
services:
  web:
    image: node:22
    working_dir: /app
    volumes: [".:/app", "node_modules:/app/node_modules"]   # volume nommé : rapide sous Windows
    ports: ["5173:5173"]
    command: sh -c "npm ci && npm run dev -- --host"
volumes: { node_modules: {} }""")],
 [("Réécris sans muter : une fonction <code>close(incidents, id)</code> qui renvoie la liste avec l'incident <code>id</code> passé en <code>status: 'closed'</code>.", "<code>const close = (xs: Incident[], id: number) => xs.map(x => x.id === id ? { ...x, status: 'closed' } : x);</code> — <code>map</code> renvoie un nouveau tableau, le spread un nouvel objet ; les autres éléments sont réutilisés tels quels (c'est ce que React compare)."),
  ("Pourquoi une union discriminée plutôt que <code>{ loading: boolean; error?: string; data?: T }</code> ?", "Avec trois champs, l'état <code>loading: true, data: [...]</code> est représentable mais absurde ; l'union rend les états impossibles non représentables, et le <code>switch</code> exhaustif force à traiter chaque cas.")],
 ("Un projet TypeScript en conteneur", ["Crée un projet <code>npm create vite@latest crisisshield-web -- --template react-ts</code> dans le conteneur node:22.", "Ajoute <code>strict: true</code> et <code>noUncheckedIndexedAccess</code> dans <code>tsconfig.json</code>.", "Écris <code>src/domain/incident.ts</code> avec les types ci-dessus et trois fonctions pures testées (Vitest)."],
  "<code>docker compose run --rm web npm create vite@latest . -- --template react-ts</code> ; <code>npm i -D vitest</code> ; test : <code>expect(close([a], a.id)[0].status).toBe('closed')</code> et <code>expect(close([a], a.id)[0]).not.toBe(a)</code> (nouvel objet). Le <code>strict</code> fait apparaître les <code>undefined</code> possibles dès la première lecture d'index.")),

ch("Démarrer : Vite, JSX, composants et props", 'j',
 ["Un composant est une fonction qui reçoit des props et renvoie du JSX ; il se rend à nouveau quand ses props ou son état changent.", "JSX est du JavaScript : accolades pour les expressions, <code>className</code>, listes avec <code>key</code> stable.", "Le rendu est déclaratif : on décrit l'interface pour un état donné, jamais « ajoute un élément au DOM »."],
 ["Créer et composer des composants fonctionnels typés", "Rendre conditionnellement et itérer avec des clés correctes", "Structurer un projet Vite (dossiers, alias, lint)"],
 [("Composants et props", "Une prop est en lecture seule ; <code>children</code> compose. Les props typées remplacent la documentation.",
"""type BadgeProps = { priority: Priority; children?: React.ReactNode };
export function Badge({ priority, children }: BadgeProps) {
  const color = { P1: 'red', P2: 'orange', P3: 'gray' }[priority];
  return <span className={`badge badge-${color}`}>{children ?? priority}</span>;
}
export function IncidentCard({ incident }: { incident: Incident }) {
  return (
    <article className="card">
      <h3>{incident.title}</h3>
      <Badge priority={incident.priority} />
      {incident.zone && <p>Zone {incident.zone}</p>}          {/* rendu conditionnel */}
    </article>
  );
}"""),
  ("Listes et clés", "La clé identifie un élément entre deux rendus : jamais l'index quand la liste change d'ordre ou se filtre, sinon React réutilise le mauvais DOM (champ de formulaire qui garde la valeur du voisin).",
"""export function IncidentList({ items }: { items: Incident[] }) {
  if (items.length === 0) return <p>Aucun incident.</p>;
  return <ul>{items.map(i => <li key={i.id}><IncidentCard incident={i} /></li>)}</ul>;
}"""),
  ("Structure du projet", "Un dossier par domaine (<code>incidents/</code>, <code>auth/</code>) contenant composants, hooks et api, plutôt qu'un dossier <code>components/</code> global. Alias <code>@/</code> dans Vite et tsconfig. ESLint avec <code>eslint-plugin-react-hooks</code> dès le premier jour.", None)],
 [("Ce composant a un bug : <code>items.map((i, idx) => &lt;Row key={idx} item={i} /&gt;)</code> avec une liste triable. Lequel ?", "En triant, l'élément à l'index 0 change mais sa clé reste 0 : React garde le DOM (et l'état interne, par exemple un input) de l'ancien élément 0 et ne fait que changer ses props. Clé = identifiant stable de la donnée."),
  ("Pourquoi <code>&lt;button onClick={handle()}&gt;</code> déclenche-t-il l'action au rendu ?", "Les accolades évaluent l'expression : <code>handle()</code> appelle la fonction pendant le rendu et passe son résultat. Il faut passer la fonction : <code>onClick={handle}</code> ou <code>onClick={() => handle(id)}</code>.")],
 ("La liste des incidents", ["Composants <code>IncidentList</code>, <code>IncidentCard</code>, <code>Badge</code> avec des données en dur.", "Un tri par priorité et un filtre par zone en props.", "Snapshot du rendu avec Testing Library."],
  "<code>render(&lt;IncidentList items={fixtures} /&gt;)</code> puis <code>screen.getAllByRole('listitem')</code> ; le tri est une fonction pure <code>sortByPriority</code> testée à part. Vérifier dans les DevTools React que la clé est l'identifiant.")),

ch("État et événements : useState et les formulaires", 'j',
 ["<code>useState</code> déclare un état local ; le modifier déclenche un nouveau rendu ; l'état est immuable (on remplace, on ne mute pas).", "Les mises à jour sont regroupées (batching) et asynchrones : utiliser la forme fonctionnelle <code>set(prev => …)</code> quand la nouvelle valeur dépend de l'ancienne.", "Faire remonter l'état (lifting state up) au plus proche ancêtre commun, pas plus haut."],
 ["Gérer des états locaux simples et composés sans mutation", "Écrire un formulaire contrôlé et un non contrôlé, et choisir", "Faire communiquer deux composants frères"],
 [("useState et immutabilité", "Muter un tableau (<code>push</code>) ne change pas sa référence : React ne voit rien. On crée un nouveau tableau.",
"""const [incidents, setIncidents] = useState<Incident[]>([]);
const add = (i: Incident) => setIncidents(prev => [...prev, i]);                 // forme fonctionnelle : sûre en cas de plusieurs appels
const close = (id: number) => setIncidents(prev => prev.map(x => x.id === id ? { ...x, status: 'closed' } : x));
const [filter, setFilter] = useState({ zone: '', priority: '' as Priority | '' });
const setZone = (zone: string) => setFilter(f => ({ ...f, zone }));"""),
  ("Formulaire contrôlé", "La valeur de l'input vient de l'état et chaque frappe met l'état à jour : l'état est la source de vérité, la validation est immédiate.",
"""export function NewIncident({ onCreate }: { onCreate: (i: Omit<Incident, 'id'>) => void }) {
  const [title, setTitle] = useState('');
  const [priority, setPriority] = useState<Priority>('P2');
  const valid = title.trim().length >= 3;
  return (
    <form onSubmit={e => { e.preventDefault(); if (valid) { onCreate({ title: title.trim(), priority, zone: 'N1', createdAt: new Date().toISOString() }); setTitle(''); } }}>
      <input value={title} onChange={e => setTitle(e.target.value)} aria-label="Titre" />
      <select value={priority} onChange={e => setPriority(e.target.value as Priority)}>{(['P1','P2','P3'] as const).map(p => <option key={p}>{p}</option>)}</select>
      <button disabled={!valid}>Créer</button>
    </form>
  );
}"""),
  ("Remonter l'état", "Le filtre et la liste sont frères : l'état du filtre vit dans le parent, qui passe la valeur au filtre et la liste filtrée à la liste. Règle : l'état vit dans le composant le plus bas qui en a besoin et qui englobe tous ses lecteurs.", None)],
 [("<code>setCount(count + 1); setCount(count + 1);</code> dans le même gestionnaire : le compteur augmente de combien ?", "De 1 : les deux appels lisent le même <code>count</code> capturé par la closure et sont regroupés. Avec <code>setCount(c => c + 1)</code> deux fois, +2."),
  ("Quand préférer un input non contrôlé (<code>ref</code>, <code>defaultValue</code>) ?", "Gros formulaires où chaque frappe ne doit pas re-rendre, intégration de bibliothèques DOM, fichiers (<code>input type=file</code> est toujours non contrôlé). React Hook Form (chapitre 8) utilise ce mode par défaut.")],
 ("Créer et clôturer un incident", ["Formulaire de création contrôlé avec validation et bouton désactivé.", "Bouton « Clôturer » sur chaque carte ; l'état vit dans <code>App</code>.", "Test : créer un incident, vérifier qu'il apparaît, le clôturer."],
  "<code>App</code> tient <code>incidents</code> et passe <code>onCreate</code> et <code>onClose</code>. Test Testing Library : <code>await user.type(screen.getByLabelText('Titre'), 'Fuite')</code>, <code>user.click(screen.getByRole('button', { name: 'Créer' }))</code>, <code>expect(screen.getByText('Fuite')).toBeInTheDocument()</code>. Aucune mutation : ESLint <code>no-param-reassign</code> ne signale rien.")),

ch("Effets, cycle de vie et données distantes", 'c',
 ["<code>useEffect</code> synchronise le composant avec l'extérieur (réseau, DOM, abonnement) après le rendu ; ce n'est pas « componentDidMount ».", "Le tableau de dépendances doit être complet (règle ESLint) ; le nettoyage annule ce que l'effet a commencé ; StrictMode exécute l'effet deux fois en dev pour le prouver.", "<code>useRef</code> garde une valeur entre rendus sans re-rendre : élément DOM, minuteur, dernière valeur."],
 ["Écrire un effet correct avec nettoyage et gestion de la course", "Charger des données avec états loading/error/ok et annulation", "Savoir quand ne pas utiliser d'effet (valeur dérivée, événement)"],
 [("Un effet de chargement correct", "Sans annulation, une réponse lente d'un ancien filtre écrase la réponse du nouveau. <code>AbortController</code> et un drapeau <code>cancelled</code> règlent la course.",
"""function useIncidents(zone: string) {
  const [state, setState] = useState<Loading<Incident[]>>({ status: 'idle' });
  useEffect(() => {
    const ctrl = new AbortController();
    setState({ status: 'loading' });
    fetch(`/api/incidents?zone=${encodeURIComponent(zone)}`, { signal: ctrl.signal })
      .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json() as Promise<Incident[]>; })
      .then(data => setState({ status: 'ok', data }))
      .catch(e => { if (e.name !== 'AbortError') setState({ status: 'error', error: e.message }); });
    return () => ctrl.abort();          // nettoyage : la requête précédente est annulée
  }, [zone]);                            // dépendance complète
  return state;
}"""),
  ("Ce qui n'est pas un effet", "Une valeur dérivée se calcule pendant le rendu (<code>const open = incidents.filter(...)</code>), pas dans un effet qui la copie dans un état. Une réaction à un clic se fait dans le gestionnaire. Un effet qui « resynchronise » un état à partir d'un autre est presque toujours un bug de conception.", None),
  ("useRef et le DOM", "Focus au montage, minuteur à nettoyer, valeur précédente : <code>ref.current</code> se lit et s'écrit sans rendu.",
"""const input = useRef<HTMLInputElement>(null);
useEffect(() => { input.current?.focus(); }, []);
const timer = useRef<number>();
useEffect(() => { timer.current = window.setInterval(refresh, 30_000); return () => clearInterval(timer.current); }, [refresh]);""")],
 [("Pourquoi StrictMode monte-t-il chaque composant deux fois en développement ?", "Pour révéler les effets sans nettoyage (double abonnement, double requête visible) : un effet correct survit à monter → nettoyer → remonter. En production, un seul montage."),
  ("<code>useEffect(() => { setTotal(items.length) }, [items])</code> : que corriger ?", "Supprimer l'état <code>total</code> et calculer <code>const total = items.length</code> au rendu. L'effet ajoute un rendu inutile et une fenêtre où <code>total</code> est faux.")],
 ("Charger les incidents de l'API CrisisShield", ["Hook <code>useIncidents(zone)</code> avec annulation ; proxy Vite vers <code>http://api:8080</code>.", "Affichage des trois états ; rafraîchissement toutes les 30 s.", "Test avec MSW : réponse lente sur la zone A puis rapide sur la zone B, la B gagne."],
  "<code>vite.config.ts</code> : <code>server.proxy['/api'] = { target: 'http://api:8080' }</code> (nom du service Compose). MSW : <code>http.get('/api/incidents', async ({ request }) => { const zone = new URL(request.url).searchParams.get('zone'); await delay(zone === 'A' ? 300 : 10); return HttpResponse.json(fixtures[zone]); })</code>. Test : changer de A à B puis <code>await screen.findByText(fixtures.B[0].title)</code> et <code>expect(screen.queryByText(fixtures.A[0].title)).toBeNull()</code>.")),

ch("Composition avancée : context, reducer, hooks personnalisés, mémoïsation", 'c',
 ["Un hook personnalisé extrait de la logique réutilisable (état + effets) sans rien changer au modèle de rendu.", "<code>useReducer</code> centralise des transitions d'état complexes ; le contexte partage une valeur dans un sous-arbre sans props intermédiaires (pas un store global).", "<code>useMemo</code>, <code>useCallback</code>, <code>React.memo</code> évitent des calculs ou rendus coûteux : on mesure avant, et le React Compiler les rend souvent inutiles."],
 ["Écrire un hook personnalisé testable", "Modéliser un état avec un reducer typé et un contexte", "Décider quand mémoïser, et prouver le gain avec le Profiler"],
 [("Hook personnalisé", "Toute fonction qui appelle des hooks et commence par <code>use</code>. Il encapsule une préoccupation (débounce, localStorage, requête) et se teste avec <code>renderHook</code>.",
"""export function useDebounced<T>(value: T, ms = 300): T {
  const [v, setV] = useState(value);
  useEffect(() => { const t = setTimeout(() => setV(value), ms); return () => clearTimeout(t); }, [value, ms]);
  return v;
}
// usage : const q = useDebounced(search); useIncidents(q);"""),
  ("useReducer et contexte", "Les actions nomment ce qui se passe ; le reducer est pur et testable sans React ; le contexte fournit état et dispatch au sous-arbre.",
"""type Action = { type: 'created'; incident: Incident } | { type: 'closed'; id: number } | { type: 'loaded'; incidents: Incident[] };
function reducer(state: Incident[], a: Action): Incident[] {
  switch (a.type) { case 'loaded': return a.incidents; case 'created': return [a.incident, ...state]; case 'closed': return state.map(x => x.id === a.id ? { ...x, status: 'closed' } : x); }
}
const IncidentsCtx = createContext<{ incidents: Incident[]; dispatch: React.Dispatch<Action> } | null>(null);
export function IncidentsProvider({ children }: { children: React.ReactNode }) {
  const [incidents, dispatch] = useReducer(reducer, []);
  const value = useMemo(() => ({ incidents, dispatch }), [incidents]);   // référence stable : les consommateurs ne re-rendent que si incidents change
  return <IncidentsCtx.Provider value={value}>{children}</IncidentsCtx.Provider>;
}
export const useIncidentsStore = () => { const c = useContext(IncidentsCtx); if (!c) throw new Error('IncidentsProvider manquant'); return c; };"""),
  ("Mémoïsation : quand", "Un rendu React coûte peu ; une liste de 5 000 lignes triée à chaque frappe coûte. Règle : Profiler d'abord, <code>useMemo</code> sur le calcul coûteux, <code>React.memo</code> sur le composant feuille qui re-rend pour rien, <code>useCallback</code> uniquement pour stabiliser une prop passée à un composant mémoïsé. Le React Compiler (React 19) automatise l'essentiel : activé, on retire ces hooks.",
"""const sorted = useMemo(() => [...incidents].sort(byPriority), [incidents]);
const onClose = useCallback((id: number) => dispatch({ type: 'closed', id }), [dispatch]);
const Row = React.memo(function Row({ item, onClose }: RowProps) { … });""")],
 [("Pourquoi <code>useMemo(() => ({ incidents, dispatch }), [incidents])</code> dans le Provider ?", "Sans lui, un nouvel objet est créé à chaque rendu du Provider : tous les consommateurs du contexte re-rendent même si rien n'a changé. Le contexte compare la valeur par référence."),
  ("Le contexte est-il un store global ? Que se passe-t-il avec un contexte qui contient tout l'état de l'application ?", "Tout consommateur re-rend à chaque changement de n'importe quel champ. Le contexte sert à l'injection (thème, utilisateur, dispatch) ; l'état global fréquent va dans un store à sélecteurs (chapitre 7).")],
 ("Store d'incidents par reducer + contexte", ["Reducer typé avec tests unitaires purs (sans React).", "Provider et hook <code>useIncidentsStore</code> ; la liste et le formulaire ne reçoivent plus de props.", "Profiler : mesurer le rendu de 2 000 lignes avant/après <code>React.memo</code> sur la ligne."],
  "Tests : <code>expect(reducer([], { type: 'created', incident: a })).toEqual([a])</code>. Profiler (onglet React DevTools) : enregistrer une frappe dans le filtre ; avant : 2 000 <code>Row</code> re-rendus (≈ 40 ms) ; après <code>memo</code> + <code>useCallback</code> : 0 ligne re-rendue. Noter que le React Compiler donne le même résultat sans code.")),

ch("Routage, données serveur et chargement asynchrone", 'c',
 ["React Router déclare les pages, les paramètres et les routes imbriquées ; le code de chaque page se charge à la demande (<code>lazy</code>).", "TanStack Query gère l'état serveur (cache, revalidation, invalidation, retries) : plus de <code>useEffect</code> de chargement.", "<code>Suspense</code> et les error boundaries déclarent les états d'attente et d'erreur à l'endroit du layout, pas dans chaque composant."],
 ["Structurer une application multi-pages avec layouts imbriqués", "Charger, mettre en cache et invalider des données serveur avec TanStack Query", "Découper le bundle par route et gérer les erreurs de rendu"],
 [("Routes et chargement paresseux", "", """import { createBrowserRouter, RouterProvider, Outlet, useParams } from 'react-router-dom';
const IncidentsPage = lazy(() => import('./incidents/IncidentsPage'));
const router = createBrowserRouter([
  { path: '/', element: <Layout />, errorElement: <ErrorPage />, children: [
    { index: true, element: <Home /> },
    { path: 'incidents', element: <Suspense fallback={<Spinner />}><IncidentsPage /></Suspense> },
    { path: 'incidents/:id', element: <IncidentDetail /> },
  ] },
]);
function Layout() { return <><Nav /><main><Outlet /></main></>; }
export default function App() { return <RouterProvider router={router} />; }"""),
  ("TanStack Query : état serveur", "Une clé décrit la donnée ; la requête est partagée, mise en cache, rafraîchie en arrière-plan ; une mutation invalide les clés concernées.",
"""const qc = new QueryClient({ defaultOptions: { queries: { staleTime: 30_000, retry: 2 } } });
export const incidentsQuery = (zone: string) => queryOptions({ queryKey: ['incidents', zone], queryFn: ({ signal }) => api.get<Incident[]>(`/incidents?zone=${zone}`, { signal }) });
function IncidentsPage() {
  const { zone } = useFilters();
  const { data, isPending, error } = useQuery(incidentsQuery(zone));
  const create = useMutation({ mutationFn: api.createIncident, onSuccess: () => qc.invalidateQueries({ queryKey: ['incidents'] }) });
  if (isPending) return <Spinner />; if (error) return <ErrorBox error={error} />;
  return <><NewIncident onCreate={i => create.mutate(i)} /><IncidentList items={data} /></>;
}"""),
  ("Error boundary", "Une erreur pendant le rendu démonte tout l'arbre sans boundary. Un composant de classe (ou <code>react-error-boundary</code>) l'attrape et affiche un repli, par zone du layout.",
"""import { ErrorBoundary } from 'react-error-boundary';
<ErrorBoundary fallbackRender={({ error, resetErrorBoundary }) => <ErrorBox error={error} onRetry={resetErrorBoundary} />}>
  <Suspense fallback={<Spinner />}><IncidentDetail /></Suspense>
</ErrorBoundary>""")],
 [("Quelle différence entre <code>staleTime</code> et <code>gcTime</code> ?", "<code>staleTime</code> : durée pendant laquelle une donnée est considérée fraîche (pas de refetch au montage) ; <code>gcTime</code> : durée de conservation en cache d'une requête sans observateur avant suppression."),
  ("Pourquoi une mutation invalide-t-elle plutôt que de modifier le cache à la main ?", "L'invalidation redemande la vérité au serveur ; la mise à jour manuelle (<code>setQueryData</code>) est plus rapide mais peut diverger. On combine : mise à jour optimiste puis invalidation (chapitre 7).")],
 ("Pages liste et détail", ["Routes <code>/incidents</code> et <code>/incidents/:id</code>, layout avec navigation, page en <code>lazy</code>.", "Requêtes TanStack Query avec <code>queryOptions</code> partagées et préchargement au survol (<code>prefetchQuery</code>).", "Error boundary par page ; test d'une erreur 500 avec MSW."],
  "<code>onMouseEnter={() => qc.prefetchQuery(incidentQuery(id))}</code> sur le lien. MSW renvoie <code>HttpResponse.error()</code> ou un 500 : la page affiche <code>ErrorBox</code> et le bouton « Réessayer » relance (<code>resetErrorBoundary</code> + <code>refetch</code>). Vérifier dans l'onglet Réseau que le bundle de la page n'est chargé qu'à la navigation.")),

ch("État global, signals et React 19", 's',
 ["Trois familles d'état : local (useState), serveur (TanStack Query), global client (store). Le global client est souvent plus petit qu'on ne croit.", "Zustand (store simple à sélecteurs), Redux Toolkit (structure et outillage pour les grosses équipes), atomes et signals (Jotai, Preact Signals) : granularité fine, rendu sans traverser l'arbre.", "React 19 : <code>use()</code>, actions et <code>useActionState</code>, <code>useOptimistic</code>, le React Compiler ; les Server Components déplacent une partie du rendu côté serveur."],
 ["Choisir et implémenter un store adapté (Zustand, Redux Toolkit, atomes)", "Comprendre les signals dans l'écosystème React et leur différence avec le modèle de rendu", "Utiliser les nouveautés React 19 : actions, optimiste, compiler"],
 [("Zustand : le store à sélecteurs", "Un store hors de l'arbre, des sélecteurs qui ne re-rendent que ce qui lit la tranche concernée, et du middleware (persist, devtools, immer).",
"""import { create } from 'zustand';
import { persist } from 'zustand/middleware';
type Filters = { zone: string; priority: Priority | ''; setZone: (z: string) => void; reset: () => void };
export const useFilters = create<Filters>()(persist(set => ({
  zone: '', priority: '',
  setZone: zone => set({ zone }),
  reset: () => set({ zone: '', priority: '' }),
}), { name: 'crisis-filters' }));
// composant : const zone = useFilters(s => s.zone);   → ne re-rend que si zone change"""),
  ("Redux Toolkit, en deux mots", "Slices (<code>createSlice</code> : reducer + actions générées), <code>createAsyncThunk</code> ou RTK Query pour le serveur, DevTools avec voyage dans le temps, conventions strictes utiles à 30 développeurs. Pour une application de taille moyenne, Zustand + TanStack Query couvrent le besoin avec dix fois moins de code.", None),
  ("Signals et atomes dans React", "Un signal est une valeur réactive : ses lecteurs sont recalculés quand elle change, sans que le composant parent re-rende. React n'a pas de signals natifs (son modèle est « re-rendre le composant »), mais Jotai (atomes) et @preact/signals-react en donnent la granularité. Différence clé : avec un signal, seul le nœud qui lit <code>count.value</code> se met à jour ; avec useState, tout le composant. C'est le modèle qu'Angular a adopté nativement (cours Angular, chapitre 4).",
"""// Jotai
const zoneAtom = atom('');
const openIncidentsAtom = atom(get => get(incidentsAtom).filter(i => i.status === 'open' && (!get(zoneAtom) || i.zone === get(zoneAtom))));   // dérivé, mis en cache
function ZoneFilter() { const [zone, setZone] = useAtom(zoneAtom); return <input value={zone} onChange={e => setZone(e.target.value)} />; }
function Count() { const open = useAtomValue(openIncidentsAtom); return <span>{open.length}</span>; }   // seul Count re-rend
// Preact Signals
const count = signal(0);
function Counter() { return <button onClick={() => count.value++}>{count}</button>; }   // le texte se met à jour sans re-rendre Counter"""),
  ("React 19 : actions, optimiste, use, compiler", "", """// action de formulaire avec état de soumission
const [state, formAction, pending] = useActionState(async (_prev: string | null, fd: FormData) => {
  try { await api.createIncident({ title: String(fd.get('title')), priority: 'P2', zone: 'N1' }); return null; } catch (e) { return (e as Error).message; }
}, null);
<form action={formAction}><input name="title" /><button disabled={pending}>Créer</button>{state && <p role="alert">{state}</p>}</form>
// mise à jour optimiste
const [optimistic, addOptimistic] = useOptimistic(incidents, (cur, i: Incident) => [i, ...cur]);
// use() : lire une promesse ou un contexte, avec Suspense
const incident = use(incidentPromise);
// React Compiler (babel-plugin-react-compiler) : mémoïse automatiquement ; on retire useMemo/useCallback manuels après vérification""")],
 [("Une application a : le thème, l'utilisateur connecté, les incidents chargés de l'API, un brouillon de formulaire. Où va chaque état ?", "Thème et utilisateur : contexte ou petit store persistant. Incidents : TanStack Query (état serveur). Brouillon : état local du formulaire, éventuellement persisté par un store si on doit y revenir."),
  ("Pourquoi les signals n'ont-ils pas été ajoutés à React alors que Vue, Angular, Solid les ont ?", "Le modèle React est « l'interface est une fonction de l'état, on re-rend et on réconcilie » ; les signals contournent le rendu. L'équipe React préfère rendre le rendu moins coûteux (Compiler) que changer le modèle. Les bibliothèques externes offrent le choix.")],
 ("Filtres globaux et création optimiste", ["Store Zustand persistant pour les filtres, avec sélecteurs ; DevTools branchés.", "Création d'incident avec <code>useOptimistic</code> et invalidation TanStack Query ; rollback visible si l'API renvoie 500.", "Variante : les mêmes filtres en atomes Jotai ; comparer le nombre de rendus au Profiler."],
  "Optimiste : <code>addOptimistic(temp)</code> dans une action, puis <code>await create.mutateAsync(i)</code> ; si erreur, React revient à <code>incidents</code> et on affiche l'erreur. Profiler : avec Zustand, seuls les composants qui lisent <code>zone</code> re-rendent ; avec Jotai, idem, et les dérivés (<code>openIncidentsAtom</code>) ne se recalculent que si une dépendance change.")),

ch("Formulaires, validation et accessibilité", 's',
 ["React Hook Form gère les formulaires par refs (non contrôlés) : performant, peu de rendus, validation intégrée.", "Zod définit le schéma une fois : validation côté client, typage TypeScript inféré, et le même schéma peut valider côté serveur.", "Accessibilité : labels associés, messages d'erreur annoncés (<code>aria-describedby</code>, <code>role=alert</code>), navigation clavier ; testée par Testing Library et axe."],
 ["Construire un formulaire complexe (tableaux de champs, dépendances) avec React Hook Form", "Valider avec un schéma Zod partagé avec l'API", "Rendre un formulaire accessible et le tester"],
 [("Schéma Zod et formulaire", "", """const incidentSchema = z.object({
  title: z.string().trim().min(3, 'Au moins 3 caractères').max(200),
  priority: z.enum(['P1', 'P2', 'P3']),
  zone: z.string().regex(/^[A-Z][0-9]$/, 'Format A1'),
  contacts: z.array(z.object({ email: z.string().email() })).max(5),
});
type IncidentForm = z.infer<typeof incidentSchema>;
export function IncidentForm({ onSubmit }: { onSubmit: (v: IncidentForm) => Promise<void> }) {
  const { register, handleSubmit, control, formState: { errors, isSubmitting } } = useForm<IncidentForm>({ resolver: zodResolver(incidentSchema), defaultValues: { priority: 'P2', contacts: [] } });
  const { fields, append, remove } = useFieldArray({ control, name: 'contacts' });
  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      <label htmlFor="title">Titre</label>
      <input id="title" {...register('title')} aria-invalid={!!errors.title} aria-describedby="title-err" />
      {errors.title && <p id="title-err" role="alert">{errors.title.message}</p>}
      {fields.map((f, i) => <div key={f.id}><input {...register(`contacts.${i}.email`)} aria-label={`Contact ${i + 1}`} /><button type="button" onClick={() => remove(i)}>Retirer</button></div>)}
      <button type="button" onClick={() => append({ email: '' })}>Ajouter un contact</button>
      <button disabled={isSubmitting}>Enregistrer</button>
    </form>
  );
}"""),
  ("Le même schéma côté API", "Le schéma Zod vit dans un paquet partagé (<code>@crisisshield/contracts</code>) ou est généré depuis l'OpenAPI de l'API Spring (<code>openapi-zod-client</code>) : une seule source de vérité, les erreurs de l'API (RFC 9457) mappées sur les champs avec <code>setError</code>.", None),
  ("Accessibilité testée", "", """// vitest + jest-axe
const { container } = render(<IncidentForm onSubmit={vi.fn()} />);
expect(await axe(container)).toHaveNoViolations();
await user.click(screen.getByRole('button', { name: 'Enregistrer' }));
expect(await screen.findByRole('alert')).toHaveTextContent('Au moins 3 caractères');""")],
 [("Pourquoi <code>noValidate</code> sur le formulaire ?", "Pour désactiver la validation HTML native (bulles du navigateur, non stylables, non annoncées de façon cohérente) et laisser Zod produire des messages contrôlés et accessibles."),
  ("Un champ « zone » dépend de la priorité (P1 exige une zone). Comment l'exprimer ?", "<code>incidentSchema.superRefine((v, ctx) => { if (v.priority === 'P1' && !v.zone) ctx.addIssue({ path: ['zone'], message: 'Zone obligatoire en P1', code: 'custom' }); })</code> ; RHF affiche l'erreur sur <code>zone</code>.")],
 ("Formulaire d'incident complet", ["Schéma Zod partagé, formulaire RHF avec contacts dynamiques et règle croisée P1/zone.", "Erreurs de l'API (422 RFC 9457) mappées sur les champs.", "Zéro violation axe ; test clavier (Tab, Entrée) avec user-event."],
  "Mapping : <code>catch (e) { if (isProblem(e)) e.errors.forEach(err => setError(err.field as keyof IncidentForm, { message: err.message })) }</code>. Test clavier : <code>await user.tab(); expect(screen.getByLabelText('Titre')).toHaveFocus();</code> puis <code>user.keyboard('{Enter}')</code> soumet.")),

ch("Tests, qualité et outillage", 's',
 ["Vitest + Testing Library testent le comportement vu par l'utilisateur (rôles, textes), pas l'implémentation ; MSW simule l'API au niveau réseau.", "Playwright teste le parcours réel dans un navigateur, en CI, contre le build de production.", "TypeScript strict, ESLint (react-hooks, jsx-a11y), Prettier, et la couverture sur le nouveau code forment la quality gate."],
 ["Écrire des tests de composants robustes (rôles, async, MSW)", "Mettre en place les tests de bout en bout Playwright en conteneur", "Configurer lint, types stricts, couverture et un pipeline GitLab CI"],
 [("Test de composant avec MSW", "", """// src/test/setup.ts
export const server = setupServer(...handlers);
beforeAll(() => server.listen({ onUnhandledRequest: 'error' })); afterEach(() => server.resetHandlers()); afterAll(() => server.close());
// IncidentsPage.test.tsx
it('affiche les incidents puis en crée un', async () => {
  renderWithProviders(<IncidentsPage />);            // QueryClient + Router + store dans un wrapper de test
  expect(await screen.findByRole('heading', { name: 'Fuite gaz' })).toBeInTheDocument();
  await user.type(screen.getByLabelText('Titre'), 'Inondation');
  await user.click(screen.getByRole('button', { name: 'Créer' }));
  expect(await screen.findByRole('heading', { name: 'Inondation' })).toBeInTheDocument();   // MSW a reçu le POST et la liste est invalidée
});"""),
  ("Playwright en conteneur", "", """# compose.test.yaml : services web (build prod servi par nginx), api (MSW en mode serveur ou l'API réelle en Testcontainers), e2e (mcr.microsoft.com/playwright:v1.48.0-noble)
docker compose -f compose.test.yaml run --rm e2e npx playwright test --reporter=line
// e2e/incidents.spec.ts
test('crée et clôture un incident', async ({ page }) => {
  await page.goto('/incidents');
  await page.getByLabel('Titre').fill('Fuite');
  await page.getByRole('button', { name: 'Créer' }).click();
  await expect(page.getByRole('heading', { name: 'Fuite' })).toBeVisible();
  await page.getByRole('button', { name: 'Clôturer' }).first().click();
  await expect(page.getByText('closed')).toBeVisible();
});"""),
  ("Pipeline", "", """# .gitlab-ci.yml (extrait)
stages: [check, test, build, e2e]
lint: { stage: check, image: node:22, script: [npm ci, npm run lint, npx tsc --noEmit] }
unit: { stage: test, image: node:22, script: [npm ci, npx vitest run --coverage], coverage: '/All files[^|]*\\|[^|]*\\s+([\\d.]+)/', artifacts: { reports: { junit: junit.xml } } }
build: { stage: build, image: node:22, script: [npm ci, npm run build], artifacts: { paths: [dist/] } }
e2e: { stage: e2e, image: mcr.microsoft.com/playwright:v1.48.0-noble, services: [{ name: crisisshield/api:latest, alias: api }], script: [npm ci, npx vite preview --port 4173 & npx playwright test] }""")],
 [("Pourquoi <code>getByRole</code> plutôt que <code>getByTestId</code> ?", "Le rôle est ce que voit l'utilisateur et le lecteur d'écran : le test échoue si le bouton devient un div cliquable (régression d'accessibilité) ; un test-id survit à tout, y compris aux régressions."),
  ("Que teste-t-on en unitaire, en composant, en bout en bout ?", "Unitaire : fonctions pures (reducer, tri, schéma). Composant : un écran avec MSW (majorité des tests). Bout en bout : 5 à 10 parcours critiques contre le build réel, pas plus.")],
 ("Quality gate du front CrisisShield", ["Vitest avec MSW, couverture publiée ; ESLint react-hooks + jsx-a11y ; <code>tsc --noEmit</code> bloquant.", "Playwright en conteneur sur trois parcours ; traces conservées en cas d'échec.", "Pipeline GitLab avec les quatre étapes et rapport JUnit dans la MR."],
  "Vérifier que la MR affiche l'onglet Tests, que <code>tsc</code> échoue sur un <code>any</code> implicite, et que Playwright produit <code>trace.zip</code> (<code>trace: 'retain-on-failure'</code>) ouvrable avec <code>npx playwright show-trace</code>.")),

ch("Production : performance, sécurité, déploiement, SSR", 'e',
 ["Un build Vite produit des fichiers statiques hashés servis par nginx ; le code est découpé par route et les dépendances lourdes chargées à la demande.", "Web Vitals (LCP, INP, CLS) se mesurent en vrai (RUM) et en CI (Lighthouse) ; la performance perçue vient du découpage, du cache et du rendu progressif.", "Sécurité front : XSS (jamais <code>dangerouslySetInnerHTML</code> sans sanitisation), CSP stricte, jeton hors du navigateur (BFF), dépendances scannées, sous-ressources intègres."],
 ["Optimiser le bundle et mesurer les Web Vitals", "Sécuriser une SPA (XSS, CSP, authentification par BFF)", "Déployer en conteneur nginx durci et comprendre quand passer au SSR (Next.js, Remix)"],
 [("Build et image de production", "", """# Dockerfile
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci --ignore-scripts
COPY . .
RUN npm run build
FROM nginxinc/nginx-unprivileged:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf     # try_files $uri /index.html ; cache immutable sur /assets ; en-têtes CSP, HSTS, nosniff ; proxy /api → api:8080
EXPOSE 8080
# runtime : read-only, cap-drop ALL, USER 101 (déjà non root)"""),
  ("Performance", "<code>npx vite-bundle-visualizer</code> montre ce qui pèse ; <code>lazy</code> par route et pour les composants lourds (cartes, éditeurs) ; <code>@tanstack/react-virtual</code> pour les longues listes ; images en WebP avec dimensions ; <code>web-vitals</code> envoie LCP/INP/CLS à l'API de métriques ; Lighthouse CI avec budget (<code>lighthouserc.json</code> : performance ≥ 90).", None),
  ("Sécurité", "", """// XSS : React échappe le texte ; le danger est dangerouslySetInnerHTML → DOMPurify.sanitize(html) si vraiment nécessaire
// CSP (nginx) : default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self' https://api.crisisshield.example; frame-ancestors 'none'
// Authentification : BFF (Spring Cloud Gateway, cours DevOps TP 41) avec cookie HttpOnly SameSite=Lax ; le front n'a jamais de jeton ; CSRF par en-tête X-CSRF-Token
// Dépendances : npm audit en CI, Renovate, lockfile, --ignore-scripts ; SRI si un script tiers est chargé
// Ne jamais mettre de secret dans VITE_* : tout ce qui est compilé est public"""),
  ("SSR et Server Components", "Quand le SEO ou le premier affichage compte (site public, e-commerce), le rendu côté serveur (Next.js, Remix/React Router v7, TanStack Start) envoie du HTML prêt, puis hydrate. Les React Server Components rendent une partie de l'arbre uniquement côté serveur (accès direct aux données, zéro JS envoyé pour ces composants). Pour une application métier authentifiée comme CrisisShield, la SPA derrière un BFF reste le bon choix ; savoir expliquer ce qu'apporterait le SSR est la réponse d'entretien.", None)],
 [("Pourquoi <code>try_files $uri /index.html</code> dans nginx ?", "Le routage est côté client : une URL profonde (<code>/incidents/42</code>) rechargée doit servir <code>index.html</code> pour que React Router prenne le relais ; sans cela, 404."),
  ("Une variable <code>VITE_API_KEY</code> est-elle secrète ?", "Non : tout ce qui commence par <code>VITE_</code> est inliné dans le bundle et lisible par quiconque ouvre les sources. Les secrets restent côté serveur (BFF).")],
 ("Mise en production du front CrisisShield", ["Image nginx non root avec CSP, cache immutable, proxy vers l'API ; scan Trivy et signature (niveau 7 du parcours DevOps).", "Bundle analysé et découpé ; Lighthouse CI avec budget ; web-vitals envoyés à Prometheus via l'API.", "Déploiement Kubernetes derrière le BFF avec le Deployment de référence (TP 26) ; test Playwright contre le déploiement staging."],
  "Attendu : image < 30 Mo, Lighthouse performance ≥ 90 sur /incidents, CSP sans <code>unsafe-inline</code> pour les scripts (Vite n'en a pas besoin), en-tête <code>Cache-Control: public, max-age=31536000, immutable</code> sur <code>/assets/*</code> et <code>no-cache</code> sur <code>index.html</code>, aucun jeton dans localStorage (vérifié par le test Playwright <code>expect(await page.evaluate(() => Object.keys(localStorage))).not.toContain('token')</code>).")),
]

# ================================================================ ANGULAR
ANG = [
ch("TypeScript et RxJS : le socle d'Angular", 'j',
 ["Angular est écrit en TypeScript et l'exige : classes, décorateurs, génériques, types stricts.", "RxJS modélise les flux asynchrones (HTTP, événements, formulaires) par des Observables composables ; depuis Angular 16, les signals couvrent l'état synchrone et RxJS reste pour les flux.", "L'outillage (Angular CLI, esbuild, Vitest ou Karma) tourne dans un conteneur node:22."],
 ["Utiliser les constructions TypeScript qu'Angular emploie (classes, décorateurs, génériques, <code>strict</code>)", "Lire et composer des Observables (map, switchMap, catchError, takeUntilDestroyed)", "Créer un projet Angular en Docker"],
 [("TypeScript côté Angular", "", """interface Incident { id: number; title: string; priority: 'P1' | 'P2' | 'P3'; zone: string; status: 'open' | 'closed' }
type IncidentDraft = Omit<Incident, 'id' | 'status'>;
// tsconfig : "strict": true, "strictTemplates": true (angularCompilerOptions), "noPropertyAccessFromIndexSignature": true"""),
  ("RxJS : les cinq opérateurs qui font 90 % du travail", "<code>map</code> transforme, <code>switchMap</code> remplace la requête précédente (recherche), <code>catchError</code> convertit une erreur en valeur, <code>debounceTime</code> et <code>distinctUntilChanged</code> filtrent les frappes, <code>takeUntilDestroyed</code> désabonne avec le composant. Un Observable est paresseux : rien ne part avant <code>subscribe</code> (ou le pipe <code>async</code>, ou <code>toSignal</code>).",
"""search$ = this.query.valueChanges.pipe(
  debounceTime(300), distinctUntilChanged(),
  switchMap(q => this.api.search(q).pipe(catchError(() => of([] as Incident[])))),
  takeUntilDestroyed(),
);"""),
  ("Le poste : Angular CLI en conteneur", "", """docker run --rm -it -v "$PWD:/app" -w /app -p 4200:4200 node:22 bash
npx -y @angular/cli@19 new crisisshield-web --standalone --style=scss --ssr=false --skip-git
cd crisisshield-web && npx ng serve --host 0.0.0.0     # http://localhost:4200
# ou compose.yaml identique à celui du cours React, commande : npx ng serve --host 0.0.0.0 --poll 2000 (montage Windows)""")],
 [("Quelle différence entre <code>mergeMap</code> et <code>switchMap</code> pour une recherche ?", "<code>mergeMap</code> garde toutes les requêtes en vol : la réponse la plus lente peut arriver en dernier et écraser la bonne. <code>switchMap</code> annule la précédente à chaque nouvelle valeur : seul le dernier résultat compte."),
  ("Pourquoi un Observable qui n'est pas souscrit ne fait-il aucune requête ?", "Il est une recette, pas une exécution ; chaque <code>subscribe</code> exécute la recette. C'est ce qui permet de composer sans effet de bord, et aussi le piège : deux <code>async</code> sur le même Observable HTTP font deux requêtes (d'où <code>shareReplay</code> ou <code>toSignal</code>).")],
 ("Projet Angular en conteneur", ["Crée le projet standalone en conteneur, active <code>strictTemplates</code>.", "Écris <code>src/app/domain/incident.ts</code> et un service <code>IncidentApi</code> avec <code>HttpClient</code> (mock par <code>provideHttpClient</code> + interceptor en dev).", "Un Observable de recherche avec debounce/switchMap, testé avec <code>fakeAsync</code> et <code>HttpTestingController</code>."],
  "Test : <code>tick(300)</code> après <code>query.setValue('fu')</code>, <code>httpMock.expectOne(r => r.url.includes('q=fu'))</code> ; changer la valeur avant la réponse et vérifier que la première requête est annulée (<code>req.cancelled</code>).")),

ch("Démarrer : composants standalone, templates et control flow", 'j',
 ["Un composant = une classe avec décorateur, un template et des styles ; standalone par défaut, il importe ce qu'il utilise.", "Le template a sa propre syntaxe : interpolation, property binding <code>[x]</code>, event binding <code>(x)</code>, two-way <code>[(x)]</code>, et le control flow natif <code>@if</code>, <code>@for</code>, <code>@switch</code>.", "Le pipe formate à l'affichage ; le service porte la logique ; le composant relie les deux."],
 ["Créer des composants standalone et les composer", "Écrire des templates avec bindings et control flow, dont <code>track</code> dans <code>@for</code>", "Utiliser les pipes intégrés et en écrire un"],
 [("Un composant standalone", "", """@Component({
  selector: 'cs-incident-card',
  imports: [DatePipe, PriorityBadge],
  template: `
    <article class="card">
      <h3>{{ incident().title }}</h3>
      <cs-priority-badge [priority]="incident().priority" />
      @if (incident().zone) { <p>Zone {{ incident().zone }}</p> }
      <time>{{ incident().createdAt | date:'short' }}</time>
      <button (click)="close.emit(incident().id)" [disabled]="incident().status === 'closed'">Clôturer</button>
    </article>`,
})
export class IncidentCard {
  incident = input.required<Incident>();     // input signal (chapitre 3)
  close = output<number>();
}"""),
  ("Control flow et listes", "<code>track</code> est obligatoire dans <code>@for</code> : il joue le rôle de la <code>key</code> React. <code>@empty</code> gère la liste vide, <code>@defer</code> charge un bloc à la demande.",
"""@for (i of incidents(); track i.id) {
  <cs-incident-card [incident]="i" (close)="onClose($event)" />
} @empty { <p>Aucun incident.</p> }
@switch (state().status) { @case ('loading') { <cs-spinner /> } @case ('error') { <cs-error [error]="state().error" /> } @default { … } }
@defer (on viewport) { <cs-incident-map [incidents]="incidents()" /> } @placeholder { <p>Carte…</p> }"""),
  ("Pipes", "Purs par défaut (recalcul seulement si l'entrée change). Un pipe personnalisé :",
"""@Pipe({ name: 'priorityLabel' })
export class PriorityLabelPipe implements PipeTransform { transform(p: Priority) { return { P1: 'Critique', P2: 'Haute', P3: 'Normale' }[p]; } }""")],
 [("Pourquoi <code>@for</code> exige-t-il <code>track</code> ?", "Sans identité stable, Angular détruit et recrée tout le DOM de la liste à chaque changement ; avec <code>track i.id</code>, il déplace et met à jour. L'ancien <code>*ngFor</code> le rendait optionnel et c'était la première cause de lenteur."),
  ("<code>[disabled]=\"x\"</code> contre <code>disabled=\"{{x}}\"</code> ?", "Le property binding assigne la propriété DOM avec un booléen ; l'interpolation écrit une chaîne dans l'attribut : <code>disabled=\"false\"</code> désactive quand même. Toujours <code>[prop]</code> pour les booléens.")],
 ("Liste d'incidents", ["Composants <code>IncidentList</code>, <code>IncidentCard</code>, <code>PriorityBadge</code>, pipe <code>priorityLabel</code>, données en dur.", "Tri et filtre par inputs ; carte en <code>@defer</code>.", "Test de composant avec <code>TestBed</code> et <code>fixture.debugElement.queryAll(By.css('article'))</code>."],
  "Le test : <code>fixture.componentRef.setInput('items', fixtures); fixture.detectChanges(); expect(cards.length).toBe(3)</code>. Vérifier l'absence de <code>NgIf/NgFor</code> importés : le control flow natif n'a pas besoin de <code>CommonModule</code>.")),

ch("Composants en profondeur : inputs, outputs, projection, cycle de vie", 'j',
 ["<code>input()</code>, <code>output()</code>, <code>model()</code> remplacent les décorateurs <code>@Input/@Output</code> : typés, obligatoires possibles, transformables, et réactifs (ce sont des signals).", "La projection (<code>ng-content</code>) compose des composants génériques ; <code>viewChild()</code> et <code>contentChild()</code> accèdent aux enfants, en signals aussi.", "Le cycle de vie se réduit à peu de choses avec les signals : <code>constructor</code> + <code>inject</code>, <code>effect</code>, <code>afterNextRender</code> pour le DOM, <code>DestroyRef</code> pour le nettoyage."],
 ["Typer et transformer les entrées, émettre des sorties, faire du two-way avec <code>model()</code>", "Composer par projection et accéder aux enfants", "Choisir le bon hook de cycle de vie, et s'en passer le plus souvent"],
 [("Inputs, outputs, model", "", """export class ZoneFilter {
  zones = input<string[]>([]);
  placeholder = input('Toutes les zones', { transform: (v: string) => v.trim() });
  value = model<string>('');                       // two-way : [(value)]="zone" côté parent
  changed = output<string>();
  select(z: string) { this.value.set(z); this.changed.emit(z); }
}
// parent : <cs-zone-filter [zones]="zones()" [(value)]="zone" (changed)="reload()" />"""),
  ("Projection de contenu", "", """@Component({ selector: 'cs-panel', template: `<section><header><ng-content select="[title]" /></header><ng-content /></section>` })
export class Panel {}
// <cs-panel><h2 title>Incidents ouverts</h2><cs-incident-list … /></cs-panel>
// accès aux enfants : list = viewChild.required(IncidentList); items = contentChildren(IncidentCard);"""),
  ("Cycle de vie moderne", "", """export class IncidentDetail {
  private api = inject(IncidentApi);
  private destroyRef = inject(DestroyRef);
  id = input.required<number>();
  incident = signal<Incident | null>(null);
  constructor() {
    effect(() => { const id = this.id(); this.api.get(id).pipe(takeUntilDestroyed(this.destroyRef)).subscribe(i => this.incident.set(i)); });   // réagit au changement d'id (voir resource() au chapitre 5)
    afterNextRender(() => this.chart.render());   // DOM prêt, jamais en SSR
  }
}""")],
 [("Quand <code>ngOnInit</code> reste-t-il utile ?", "Presque plus : les inputs signals sont lisibles dès le constructeur via <code>effect</code> ou <code>computed</code>. Il reste pour du code impératif à exécuter une fois après l'initialisation des inputs non-signals (composants anciens)."),
  ("Pourquoi <code>input.required()</code> plutôt qu'un input avec valeur par défaut ?", "Le compilateur (<code>strictTemplates</code>) refuse l'usage du composant sans cet input : l'erreur est à la compilation, pas un <code>undefined</code> au runtime.")],
 ("Filtre réutilisable et panneau", ["<code>ZoneFilter</code> avec <code>model()</code> et transformation ; <code>Panel</code> avec projection nommée.", "<code>IncidentDetail</code> qui recharge quand <code>id</code> change ; nettoyage par <code>DestroyRef</code>.", "Tests : two-way binding depuis un composant hôte de test."],
  "Test hôte : <code>@Component({ template: '&lt;cs-zone-filter [(value)]=\"zone\" /&gt;', imports: [ZoneFilter] }) class Host { zone = 'N1' }</code> ; cliquer une zone et vérifier <code>host.zone</code>. Vérifier qu'un changement d'input <code>id</code> annule la requête précédente (HttpTestingController).")),

ch("Signals en profondeur : signal, computed, effect, linkedSignal, interop RxJS", 'c',
 ["<code>signal</code> est une valeur réactive ; <code>computed</code> dérive avec mise en cache et dépendances suivies automatiquement ; <code>effect</code> exécute un effet de bord quand ses dépendances changent.", "Les signals rendent la détection de changement locale : Angular ne vérifie que les vues qui lisent un signal modifié ; avec <code>OnPush</code> puis en mode zoneless, Zone.js disparaît.", "<code>toSignal</code>/<code>toObservable</code> font le pont avec RxJS ; <code>linkedSignal</code> exprime un état dérivé mais réinitialisable ; <code>untracked</code> lit sans dépendre."],
 ["Modéliser l'état d'un composant avec signal/computed/effect sans piège", "Expliquer la détection de changement avec signals, OnPush et zoneless", "Choisir entre signal et Observable, et convertir dans les deux sens"],
 [("Les primitives", "", """export class IncidentsPage {
  incidents = signal<Incident[]>([]);
  zone = signal('');
  priority = signal<Priority | ''>('');
  filtered = computed(() => this.incidents().filter(i => (!this.zone() || i.zone === this.zone()) && (!this.priority() || i.priority === this.priority())));   // recalculé seulement si une dépendance change
  openCount = computed(() => this.filtered().filter(i => i.status === 'open').length);
  add(i: Incident) { this.incidents.update(xs => [i, ...xs]); }          // update = nouvelle référence
  close(id: number) { this.incidents.update(xs => xs.map(x => x.id === id ? { ...x, status: 'closed' } : x)); }
  constructor() {
    effect(() => { localStorage.setItem('zone', this.zone()); });        // effet : persistance
    effect(() => { const n = this.openCount(); untracked(() => this.title.set(`${n} ouverts`)); });   // lecture sans dépendance
  }
}"""),
  ("linkedSignal et les pièges", "Une sélection qui doit se réinitialiser quand la liste change : <code>linkedSignal</code> dérive une valeur initiale mais reste modifiable. Pièges : écrire un signal dans un <code>effect</code> (interdit sans <code>allowSignalWrites</code>, et signe d'un <code>computed</code> manquant) ; lire un signal en dehors d'un contexte réactif (pas de mise à jour) ; muter l'objet au lieu de le remplacer (l'égalité par référence ne voit rien).",
"""selected = linkedSignal(() => this.filtered()[0] ?? null);   // revient au premier élément quand le filtre change, mais l'utilisateur peut choisir un autre
// mauvais : effect(() => this.total.set(this.items().length))  → bon : total = computed(() => this.items().length)"""),
  ("Détection de changement, OnPush, zoneless", "Historiquement Zone.js interceptait tout événement asynchrone et Angular revérifiait tout l'arbre. Avec <code>OnPush</code>, un composant n'est vérifié que si un input change, un événement part de lui, ou un signal lu par son template change. En mode zoneless (<code>provideExperimentalZonelessChangeDetection()</code>, stable en v20), seules les notifications de signals et les événements déclenchent la vérification : plus de Zone.js, moins de travail, comportement prévisible. Règle : tout nouveau composant en <code>OnPush</code>, état en signals.",
"""bootstrapApplication(App, { providers: [provideExperimentalZonelessChangeDetection(), provideRouter(routes), provideHttpClient()] });
@Component({ …, changeDetection: ChangeDetectionStrategy.OnPush })"""),
  ("Interop RxJS", "", """incidents = toSignal(this.api.list(), { initialValue: [] as Incident[] });     // Observable → signal (souscrit, désabonne avec le composant)
zone$ = toObservable(this.zone);                                                // signal → Observable, pour debounce/switchMap
results = toSignal(this.zone$.pipe(debounceTime(300), switchMap(z => this.api.search(z))), { initialValue: [] });""")],
 [("Pourquoi un <code>computed</code> n'est-il pas recalculé à chaque lecture ?", "Il est mémoïsé : il garde sa valeur tant qu'aucun signal lu pendant son dernier calcul n'a changé (suivi des dépendances dynamique, à chaque exécution). Un <code>computed</code> jamais lu n'est jamais calculé (paresseux)."),
  ("Quand garder RxJS avec les signals ?", "Pour les flux dans le temps : débounce, annulation (switchMap), retries, WebSocket, combinaison d'événements. Les signals portent l'état courant ; on convertit à la frontière avec <code>toSignal</code>.")],
 ("Page incidents entièrement en signals, zoneless", ["État, filtres et dérivés en signal/computed ; sélection en <code>linkedSignal</code> ; persistance par <code>effect</code>.", "Application en zoneless et tous les composants en OnPush ; vérifier avec le Profiler Angular DevTools que seule la vue concernée est vérifiée.", "Recherche avec <code>toObservable</code> + debounce + switchMap → <code>toSignal</code>."],
  "DevTools → Profiler : une frappe dans le filtre ne déclenche que la vérification de <code>IncidentsPage</code> et de la liste (pas du header). Test : <code>TestBed.flushEffects()</code> après <code>zone.set('N1')</code> puis <code>expect(localStorage.getItem('zone')).toBe('N1')</code>. Le <code>linkedSignal</code> : après un changement de filtre, <code>selected()</code> est le premier filtré ; après <code>selected.set(autre)</code>, il le reste jusqu'au prochain changement de filtre.")),

ch("Services, injection de dépendances, HttpClient et resource()", 'c',
 ["Un service porte la logique et l'état partagé ; <code>inject()</code> le fournit là où il faut, selon une hiérarchie d'injecteurs (racine, route, composant).", "<code>HttpClient</code> renvoie des Observables ; les intercepteurs fonctionnels ajoutent jeton, gestion d'erreur, retries ; <code>httpResource</code> et <code>resource()</code> apportent le chargement piloté par signals.", "Les tokens d'injection configurent (URL d'API, feature flags) sans couplage."],
 ["Écrire des services injectables et comprendre les portées", "Appeler une API avec intercepteurs, typage et gestion d'erreur", "Charger des données avec <code>resource()</code>/<code>httpResource()</code> pilotés par des signals"],
 [("Services et injection", "", """export const API_URL = new InjectionToken<string>('API_URL');
@Injectable({ providedIn: 'root' })                       // singleton, tree-shakable
export class IncidentApi {
  private http = inject(HttpClient); private base = inject(API_URL);
  list(zone = '') { return this.http.get<Incident[]>(`${this.base}/incidents`, { params: { zone } }); }
  create(d: IncidentDraft) { return this.http.post<Incident>(`${this.base}/incidents`, d); }
}
// app.config.ts : { provide: API_URL, useValue: '/api' } ; portée route : providers: [IncidentsStore] sur la route → une instance par sous-arbre de route"""),
  ("Intercepteurs fonctionnels", "", """export const authInterceptor: HttpInterceptorFn = (req, next) => next(req.clone({ withCredentials: true }));   // cookie BFF, pas de jeton en JS
export const problemInterceptor: HttpInterceptorFn = (req, next) => next(req).pipe(catchError((e: HttpErrorResponse) => throwError(() => Problem.from(e))));   // RFC 9457 → objet métier
export const retryInterceptor: HttpInterceptorFn = (req, next) => req.method === 'GET' ? next(req).pipe(retry({ count: 2, delay: 300 })) : next(req);
provideHttpClient(withInterceptors([authInterceptor, retryInterceptor, problemInterceptor]))"""),
  ("resource() et httpResource()", "Un chargement déclaratif : la requête dépend de signals, se relance quand ils changent, annule la précédente, expose <code>value</code>, <code>status</code>, <code>error</code>, <code>isLoading</code> et <code>reload()</code>.",
"""zone = signal('');
incidents = httpResource<Incident[]>(() => ({ url: '/api/incidents', params: { zone: this.zone() } }), { defaultValue: [] });
// template : @if (incidents.isLoading()) { <cs-spinner /> } @else if (incidents.error()) { … } @else { @for (i of incidents.value(); track i.id) { … } }
// version générique (toute promesse) :
detail = resource({ request: () => ({ id: this.id() }), loader: ({ request, abortSignal }) => fetch(`/api/incidents/${request.id}`, { signal: abortSignal }).then(r => r.json() as Promise<Incident>) });""")],
 [("Deux composants injectent <code>IncidentsStore</code> déclaré <code>providedIn: 'root'</code> ; un troisième le déclare dans ses <code>providers</code>. Combien d'instances ?", "Deux : la racine pour les deux premiers, une instance dédiée au sous-arbre du troisième (et de ses enfants). C'est la hiérarchie des injecteurs ; utile pour un état par page."),
  ("Pourquoi <code>withCredentials</code> et pas un en-tête <code>Authorization</code> ?", "Le jeton reste dans un cookie HttpOnly posé par le BFF : le JavaScript ne peut pas le lire ni le voler par XSS. L'en-tête Authorization impliquerait un jeton lisible en JS (localStorage), à éviter.")],
 ("API CrisisShield avec intercepteurs et resource", ["<code>IncidentApi</code> typé avec token <code>API_URL</code> ; trois intercepteurs ; erreurs RFC 9457 converties.", "Page liste avec <code>httpResource</code> piloté par le filtre ; détail avec <code>resource</code> et <code>reload()</code>.", "Tests avec <code>HttpTestingController</code> : retry sur GET, pas sur POST ; erreur 422 mappée."],
  "Test retry : <code>httpMock.expectOne(url).flush(null, { status: 503, statusText: 'x' })</code> deux fois puis une réponse OK : un seul résultat côté abonné. Pour POST : une seule requête. <code>httpResource</code> : changer <code>zone</code> deux fois rapidement → la première requête est annulée (<code>expectOne</code> ne trouve qu'une requête en vol).")),

ch("Routage : lazy loading, guards, resolvers et inputs de route", 'c',
 ["Les routes sont un tableau typé ; chaque fonctionnalité se charge paresseusement par <code>loadComponent</code>/<code>loadChildren</code>.", "Guards et resolvers sont des fonctions (<code>CanActivateFn</code>) qui injectent ce qu'elles veulent ; ils renvoient booléen, <code>UrlTree</code> ou Observable.", "<code>withComponentInputBinding()</code> injecte paramètres, query et données de route directement dans les <code>input()</code> du composant."],
 ["Organiser les routes par fonctionnalité avec chargement paresseux", "Protéger et préparer des routes avec guards et resolvers fonctionnels", "Lire paramètres et données de route par inputs signals"],
 [("Routes et lazy loading", "", """export const routes: Routes = [
  { path: '', component: Home },
  { path: 'incidents', loadChildren: () => import('./incidents/incidents.routes').then(m => m.INCIDENT_ROUTES), canActivate: [authGuard] },
  { path: '**', component: NotFound },
];
// incidents.routes.ts
export const INCIDENT_ROUTES: Routes = [
  { path: '', component: IncidentsPage, title: 'Incidents' },
  { path: ':id', component: IncidentDetail, resolve: { incident: incidentResolver }, title: incidentTitle },
];
provideRouter(routes, withComponentInputBinding(), withPreloading(PreloadAllModules), withViewTransitions())"""),
  ("Guards et resolvers fonctionnels", "", """export const authGuard: CanActivateFn = () => { const auth = inject(AuthStore); const router = inject(Router); return auth.isLoggedIn() ? true : router.createUrlTree(['/login']); };
export const roleGuard = (role: string): CanActivateFn => () => inject(AuthStore).roles().includes(role);
export const incidentResolver: ResolveFn<Incident> = route => inject(IncidentApi).get(Number(route.paramMap.get('id')));"""),
  ("Inputs de route", "", """export class IncidentDetail {
  id = input.required<number, string>({ transform: numberAttribute });   // depuis :id
  incident = input.required<Incident>();                                   // depuis resolve
  tab = input<string>('details');                                          // depuis ?tab=
}""")],
 [("Pourquoi renvoyer un <code>UrlTree</code> plutôt que faire <code>router.navigate</code> dans un guard ?", "Le guard reste pur et testable, la navigation est atomique (pas de course entre l'annulation et la redirection) et le router gère l'historique correctement."),
  ("Un resolver qui met 3 s bloque l'affichage. Alternative ?", "Ne pas résoudre : naviguer tout de suite et charger dans le composant avec <code>resource()</code> et un état de chargement ; réserver le resolver aux données indispensables et rapides (ou afficher un indicateur de navigation).")],
 ("Routage de CrisisShield", ["Routes lazy par fonctionnalité (incidents, carte, admin) avec <code>authGuard</code> et <code>roleGuard('admin')</code>.", "Détail par inputs de route ; titre dynamique ; préchargement.", "Tests de guard avec <code>TestBed.runInInjectionContext</code> ; test de navigation avec <code>RouterTestingHarness</code>."],
  "Guard : <code>TestBed.runInInjectionContext(() => authGuard(route, state))</code> renvoie <code>UrlTree</code> vers <code>/login</code> quand <code>isLoggedIn</code> est faux. Harness : <code>await harness.navigateByUrl('/incidents/42', IncidentDetail)</code> puis <code>expect(component.id()).toBe(42)</code>. Vérifier dans l'onglet Réseau que <code>incidents-*.js</code> n'est chargé qu'à la navigation.")),

ch("Formulaires : réactifs typés, validation, et signal forms", 's',
 ["Les formulaires réactifs sont des objets typés (<code>FormGroup&lt;{…}&gt;</code>) dans la classe : validation synchrone et asynchrone, valeurs et états observables ou en signals.", "Les validateurs sont des fonctions pures et composables ; les erreurs s'affichent avec un composant réutilisable et accessible.", "Les signal forms (expérimental en v20, à suivre) décrivent un formulaire à partir d'un modèle en signal et d'un schéma : la direction du framework."],
 ["Construire un formulaire réactif typé avec groupes, tableaux et validateurs croisés", "Afficher les erreurs de façon accessible et mapper celles de l'API", "Comprendre ce que changent les signal forms"],
 [("Formulaire réactif typé", "", """export class IncidentForm {
  private fb = inject(NonNullableFormBuilder);
  form = this.fb.group({
    title: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(200)]],
    priority: this.fb.control<Priority>('P2'),
    zone: ['', Validators.pattern(/^[A-Z][0-9]$/)],
    contacts: this.fb.array<FormControl<string>>([]),
  }, { validators: [zoneRequiredForP1] });
  submitting = signal(false);
  value = toSignal(this.form.valueChanges, { initialValue: this.form.value });
  addContact() { this.form.controls.contacts.push(this.fb.control('', Validators.email)); }
  async submit() { if (this.form.invalid) { this.form.markAllAsTouched(); return; } this.submitting.set(true); try { await firstValueFrom(this.api.create(this.form.getRawValue())); this.form.reset(); } catch (e) { mapProblem(e as Problem, this.form); } finally { this.submitting.set(false); } }
}
export const zoneRequiredForP1: ValidatorFn = c => c.get('priority')?.value === 'P1' && !c.get('zone')?.value ? { zoneRequired: true } : null;"""),
  ("Affichage accessible des erreurs", "", """<label for="title">Titre</label>
<input id="title" formControlName="title" [attr.aria-invalid]="form.controls.title.invalid && form.controls.title.touched" aria-describedby="title-err" />
<cs-field-errors id="title-err" [control]="form.controls.title" />    <!-- composant : @if (control().touched) { @for (e of errors(); track e) { <p role="alert">{{ e }}</p> } } -->"""),
  ("Signal forms (aperçu)", "Un modèle en signal, un schéma de validation, des champs dérivés : <code>const model = signal({ title: '', priority: 'P2' }); const f = form(model, s => { required(s.title); minLength(s.title, 3); });</code> puis <code>[field]=\"f.title\"</code> dans le template. Le formulaire devient une projection réactive du modèle, sans <code>FormControl</code>. À utiliser en veille technologique, pas encore en production (API expérimentale).", None)],
 [("Pourquoi <code>NonNullableFormBuilder</code> ?", "Avec le builder classique, <code>reset()</code> remet <code>null</code> et les types deviennent <code>string | null</code> partout. Non nullable : reset à la valeur initiale, types propres, <code>getRawValue()</code> directement typé <code>IncidentDraft</code>."),
  ("Validation asynchrone (unicité du titre) : comment éviter une requête par frappe ?", "<code>updateOn: 'blur'</code> sur le contrôle, ou un <code>AsyncValidatorFn</code> avec <code>timer(300).pipe(switchMap(() => api.exists(v)))</code> ; l'état <code>pending</code> désactive le bouton.")],
 ("Formulaire d'incident", ["Formulaire réactif typé avec contacts dynamiques, validateur croisé P1/zone, validateur asynchrone d'unicité.", "Composant <code>FieldErrors</code> accessible ; erreurs 422 de l'API mappées avec <code>setErrors</code>.", "Tests : validité, erreurs affichées après <code>touched</code>, mapping API ; axe sans violation."],
  "Mapping : <code>problem.errors.forEach(e => form.get(e.field)?.setErrors({ server: e.message }))</code>. Test asynchrone : <code>fakeAsync</code>, <code>control.setValue('Fuite'); tick(300); httpMock.expectOne(...).flush({ exists: true }); expect(control.hasError('taken')).toBeTrue()</code>.")),

ch("État global : service + signals, NgRx SignalStore, Store classique", 's',
 ["Le premier store Angular est un service <code>providedIn: 'root'</code> avec des signals privés en écriture et des <code>computed</code> publics en lecture.", "NgRx SignalStore structure ce modèle (état, computed, méthodes, hooks, features réutilisables comme <code>withEntities</code>) sans le cérémonial actions/reducers/effects.", "Le Store NgRx classique (Redux) garde son sens pour de très grosses équipes avec besoin d'audit d'actions ; pour le reste, SignalStore."],
 ["Écrire un store en service + signals avec API en lecture seule", "Utiliser NgRx SignalStore avec entités, méthodes RxJS et hooks", "Choisir entre les trois approches et argumenter"],
 [("Store en service", "", """@Injectable({ providedIn: 'root' })
export class IncidentsStore {
  private api = inject(IncidentApi);
  private _incidents = signal<Incident[]>([]);
  private _status = signal<'idle' | 'loading' | 'error'>('idle');
  readonly incidents = this._incidents.asReadonly();
  readonly open = computed(() => this._incidents().filter(i => i.status === 'open'));
  readonly loading = computed(() => this._status() === 'loading');
  load(zone: string) { this._status.set('loading'); this.api.list(zone).subscribe({ next: xs => { this._incidents.set(xs); this._status.set('idle'); }, error: () => this._status.set('error') }); }
  close(id: number) { const before = this._incidents(); this._incidents.update(xs => xs.map(x => x.id === id ? { ...x, status: 'closed' } : x));   // optimiste
    this.api.close(id).subscribe({ error: () => this._incidents.set(before) }); }
}"""),
  ("NgRx SignalStore", "", """export const IncidentsStore = signalStore(
  { providedIn: 'root' },
  withEntities<Incident>(),
  withState({ zone: '', status: 'idle' as 'idle' | 'loading' | 'error' }),
  withComputed(({ entities, zone }) => ({ open: computed(() => entities().filter(i => i.status === 'open' && (!zone() || i.zone === zone()))) })),
  withMethods((store, api = inject(IncidentApi)) => ({
    setZone: (zone: string) => patchState(store, { zone }),
    load: rxMethod<string>(pipe(tap(() => patchState(store, { status: 'loading' })), switchMap(zone => api.list(zone).pipe(tapResponse({ next: xs => patchState(store, setAllEntities(xs), { status: 'idle' }), error: () => patchState(store, { status: 'error' }) }))))),
    close: (id: number) => patchState(store, updateEntity({ id, changes: { status: 'closed' } })),
  })),
  withHooks({ onInit(store) { store.load(store.zone); } }),   // rxMethod accepte un signal : recharge quand zone change
);
// composant : store = inject(IncidentsStore); template : @for (i of store.open(); track i.id) …"""),
  ("Choisir", "Service + signals : par défaut, jusqu'à quelques stores. SignalStore : dès que l'état a des entités, du chargement, des features partagées (<code>withDevtools</code>, <code>withStorageSync</code>), ou plusieurs développeurs. Store Redux (<code>@ngrx/store</code>) : audit des actions, time-travel, très grosses applications historiques ; à ne pas introduire dans un projet neuf sans raison. Dans tous les cas : l'état serveur peut aussi passer par <code>httpResource</code> ou TanStack Query Angular.", None)],
 [("Pourquoi exposer <code>asReadonly()</code> ?", "Pour que seul le store modifie l'état : un composant ne peut pas faire <code>store.incidents.set([])</code>. Les transitions passent par des méthodes nommées, testables."),
  ("<code>rxMethod</code> reçoit un signal <code>store.zone</code> : que se passe-t-il ?", "Il s'abonne au signal (via <code>toObservable</code>) : chaque changement de zone traverse le pipe (<code>switchMap</code> annule la requête précédente). Un appel avec une valeur simple exécute une fois.")],
 ("Store des incidents en trois versions", ["Service + signals avec clôture optimiste et rollback.", "Même fonctionnalité en SignalStore avec entités, <code>rxMethod</code>, DevTools.", "Tableau comparatif (lignes de code, testabilité, réactivité) et décision écrite (ADR)."],
  "Test du store service : <code>store.close(1)</code> → <code>open()</code> ne contient plus 1 immédiatement ; <code>httpMock.expectOne(...).error(new ProgressEvent('x'))</code> → 1 est revenu. SignalStore : <code>TestBed.inject(IncidentsStore)</code>, <code>store.setZone('N1')</code>, <code>expectOne(r => r.params.get('zone') === 'N1')</code>. ADR attendu : SignalStore retenu pour CrisisShield (entités + chargement + équipe), service pour les petits états (thème, filtres).")),

ch("Tests : unitaires, composants, harnesses et bout en bout", 's',
 ["Vitest (par défaut depuis v20, ou Karma/Jest avant) avec <code>TestBed</code> teste composants et services dans un DOM ; les signals se testent en lisant leur valeur, les effets avec <code>TestBed.flushEffects()</code>.", "Les component harnesses (CDK) testent un composant par son API utilisateur (cliquer, lire), stables face aux changements de DOM.", "Playwright pour les parcours critiques contre le build réel, en conteneur, en CI."],
 ["Tester services, stores et composants signals", "Utiliser HttpTestingController, harnesses et RouterTestingHarness", "Mettre en place Playwright et la couverture dans GitLab CI"],
 [("Composant avec signals", "", """it('filtre par zone', () => {
  const fixture = TestBed.configureTestingModule({ imports: [IncidentsPage], providers: [provideHttpClientTesting(), provideZonelessChangeDetection()] }).createComponent(IncidentsPage);
  fixture.componentInstance.incidents.set(fixtures);
  fixture.componentInstance.zone.set('N1');
  fixture.detectChanges();
  expect(fixture.nativeElement.querySelectorAll('article').length).toBe(2);
});"""),
  ("Harness", "", """@Component(…) export class IncidentCardHarness extends ComponentHarness {
  static hostSelector = 'cs-incident-card';
  title = this.locatorFor('h3'); closeBtn = this.locatorFor('button');
  async getTitle() { return (await this.title()).text(); }
  async close() { await (await this.closeBtn()).click(); }
}
const loader = TestbedHarnessEnvironment.loader(fixture);
const cards = await loader.getAllHarnesses(IncidentCardHarness);
await cards[0].close(); expect(await cards[0].getTitle()).toContain('Fuite');"""),
  ("Playwright et CI", "Même approche que le cours React (chapitre 9) : image <code>mcr.microsoft.com/playwright</code>, build de production servi par nginx, API réelle ou mockée, 5 à 10 parcours ; pipeline lint → <code>ng test</code> (couverture) → <code>ng build</code> → e2e. <code>ng test --watch=false --browsers=ChromeHeadless</code> ou Vitest en mode jsdom pour les composants.", None)],
 [("Pourquoi <code>fixture.detectChanges()</code> reste-t-il nécessaire avec des signals en test ?", "En test, la détection de changement n'est pas automatique (pas d'événement, pas de scheduler zoneless actif par défaut) ; <code>detectChanges()</code> ou <code>await fixture.whenStable()</code> applique les mises à jour au DOM."),
  ("Qu'apporte un harness par rapport à <code>querySelector</code> ?", "Une API stable et sémantique partagée entre tests unitaires et e2e (Playwright supporte les harnesses CDK) ; un changement de balise ne casse pas les tests.")],
 ("Quality gate du front Angular", ["Tests de la page incidents (signals, store, HTTP) avec couverture ≥ 80 % sur le nouveau code.", "Harness pour <code>IncidentCard</code> réutilisé dans deux tests.", "Playwright en conteneur sur trois parcours ; pipeline GitLab avec rapport JUnit et artefact de couverture."],
  "<code>ng test --code-coverage --watch=false</code> produit <code>coverage/lcov.info</code> lu par SonarQube ; le job échoue sous 80 % sur le nouveau code par la quality gate. Playwright : <code>page.getByRole('button', { name: 'Clôturer' })</code> ; trace conservée en échec.")),

ch("Production : build, budgets, SSR/hydration, sécurité, i18n, migrations", 'e',
 ["<code>ng build</code> (esbuild) produit des bundles hashés ; les budgets (<code>angular.json</code>) font échouer le build si une page grossit trop ; <code>@defer</code> et les routes lazy tiennent la taille.", "Angular SSR (<code>@angular/ssr</code>) rend côté serveur et hydrate (incrémentalement avec <code>@defer (hydrate on …)</code>) : utile pour le SEO et le premier affichage, optionnel pour une application métier.", "Sécurité : sanitisation automatique des bindings, jamais <code>bypassSecurityTrust*</code> sans revue, CSP avec nonce, BFF pour l'authentification, mises à jour Angular par <code>ng update</code> avec schematics."],
 ["Configurer build, budgets et image nginx durcie", "Mettre en place le SSR et l'hydratation, et savoir quand", "Sécuriser, internationaliser et maintenir une application Angular"],
 [("Build et image", "", """// angular.json : "budgets": [{ "type": "initial", "maximumWarning": "500kB", "maximumError": "1MB" }, { "type": "anyComponentStyle", "maximumError": "8kB" }]
# Dockerfile
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci --ignore-scripts
COPY . .
RUN npx ng build --configuration production
FROM nginxinc/nginx-unprivileged:1.27-alpine
COPY --from=build /app/dist/crisisshield-web/browser /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf      # try_files → index.html, cache immutable sur *.js/*.css hashés, CSP, proxy /api
# analyse : npx ng build --stats-json && npx esbuild-visualizer --metadata dist/…/stats.json"""),
  ("SSR et hydratation", "", """npx ng add @angular/ssr          # server.ts (Express), main.server.ts, provideClientHydration(withEventReplay())
// hydratation incrémentale : @defer (hydrate on viewport) { <cs-incident-map … /> }
// contraintes : pas d'accès direct à window/document au rendu (afterNextRender, isPlatformBrowser), HttpClient avec TransferState (withHttpTransferCacheOptions) pour ne pas refaire les requêtes côté client
// image SSR : node:22-alpine qui lance dist/…/server/server.mjs, derrière le même nginx"""),
  ("Sécurité", "Angular échappe toute interpolation et sanitise <code>[innerHTML]</code>, <code>[href]</code>, <code>[style]</code> ; <code>DomSanitizer.bypassSecurityTrustHtml</code> est le seul moyen d'injecter du HTML brut et doit être revu comme un <code>dangerouslySetInnerHTML</code>. CSP : <code>ngCspNonce</code> sur le composant racine pour les styles inlinés. Authentification par BFF et cookie HttpOnly (chapitre 5). Dépendances : <code>npm audit</code>, Renovate ; <code>ng update</code> à chaque version majeure (deux par an), avec les schematics de migration (control flow, standalone, signals inputs).", None),
  ("Internationalisation et maintenance", "<code>@angular/localize</code> : marquer avec <code>i18n</code>, extraire (<code>ng extract-i18n</code>), un build par locale servi par chemin (<code>/fr/</code>, <code>/en/</code>) ; ou Transloco pour le changement à chaud. Maintenance : <code>ng update @angular/core @angular/cli</code> par version, lire le guide de mise à jour, exécuter les migrations automatiques (<code>ng generate @angular/core:control-flow</code>, <code>:signal-inputs</code>, <code>:standalone</code>), tests verts avant fusion.", None)],
 [("Une application métier derrière authentification a-t-elle besoin du SSR ?", "Rarement : pas de SEO, l'utilisateur attend de toute façon les données ; le SSR ajoute un serveur Node à exploiter. Il se justifie pour un site public ou un premier affichage critique (portail citoyen). Réponse attendue en entretien : savoir le mettre en place et savoir dire non."),
  ("Le build échoue avec « budget exceeded ». Que faire ?", "Analyser (<code>--stats-json</code>), déplacer la dépendance lourde dans une route lazy ou un bloc <code>@defer</code>, remplacer la bibliothèque (moment → date-fns/Intl), ou justifier et relever le budget dans la MR avec le chiffre.")],
 ("Mise en production du front Angular CrisisShield", ["Budgets, image nginx non root avec CSP et cache, scan et signature (niveau 7 DevOps).", "Variante SSR avec hydratation incrémentale sur la carte ; mesurer LCP avec et sans.", "Déploiement Kubernetes derrière le BFF ; Playwright sur staging ; <code>ng update</code> planifié par Renovate avec les migrations."],
  "Attendu : bundle initial < 500 kB, LCP < 2,5 s en Lighthouse CI, CSP avec nonce (<code>ngCspNonce</code>) et sans <code>unsafe-inline</code> script, aucun jeton dans le stockage navigateur, et la MR Renovate d'<code>@angular/core</code> avec <code>ng update</code> exécuté en CI (job qui lance les migrations et échoue si le diff n'est pas commité).")),
]
