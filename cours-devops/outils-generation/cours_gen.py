"""Génère cours-vue.html, cours-cloud.html et régénère cours-react.html / cours-angular.html avec un chapitre 11 expert.
Usage : python3 cours_gen.py [<dossier cours-devops>]"""
import sys; sys.path.insert(0, '/home/claude')
from front_gen import page, ch, REACT, ANG, d

# ================================================================ chapitres 11 expert React / Angular
REACT.append(ch("Expert : architecture à l'échelle, rendu concurrent, micro-frontends, observabilité", 'e',
 ["À l'échelle, la structure compte plus que le framework : monorepo (pnpm workspaces + Turborepo ou Nx), découpage par fonctionnalité, design system versionné avec Storybook.", "Le rendu concurrent (<code>useTransition</code>, <code>useDeferredValue</code>) garde l'interface réactive pendant les calculs ; la virtualisation et les Web Workers déplacent le coût hors du thread principal.", "Micro-frontends par Module Federation seulement quand plusieurs équipes déploient indépendamment ; sinon un monorepo suffit. L'observabilité front (OpenTelemetry web, erreurs, Web Vitals) ferme la boucle avec le niveau 6 du parcours DevOps."],
 ["Organiser un monorepo front avec bibliothèques partagées et design system", "Utiliser les API concurrentes de React et mesurer l'effet", "Décider et mettre en œuvre des micro-frontends, et instrumenter le front"],
 [("Monorepo et design system", "", """# pnpm-workspace.yaml : packages: [apps/*, packages/*]
# apps/crisisshield-web, apps/admin ; packages/ui (composants + Storybook + tokens CSS), packages/contracts (types et schémas Zod générés depuis l'OpenAPI), packages/config (eslint, tsconfig)
# turbo.json : pipeline build/test/lint avec cache distant ; chaque package a son tsconfig qui étend packages/config
// packages/ui/src/Button.stories.tsx
export default { component: Button, args: { children: 'Créer' } } satisfies Meta<typeof Button>;
export const Primary: StoryObj<typeof Button> = {};
export const Disabled: StoryObj<typeof Button> = { args: { disabled: true } };
// tests visuels : Chromatic ou Playwright screenshots sur Storybook ; a11y addon"""),
  ("Rendu concurrent et gros volumes", "", """const [q, setQ] = useState('');
const deferredQ = useDeferredValue(q);                       // la liste se met à jour avec la valeur « en retard », l'input reste fluide
const [isPending, startTransition] = useTransition();
const onZone = (z: string) => startTransition(() => setZone(z));   // mise à jour non urgente : React peut l'interrompre
const rowVirtualizer = useVirtualizer({ count: incidents.length, getScrollElement: () => parentRef.current, estimateSize: () => 48 });   // 50 000 lignes, 30 nœuds DOM
const worker = useMemo(() => new Worker(new URL('./cluster.worker.ts', import.meta.url), { type: 'module' }), []);   // clustering de la carte hors du thread principal"""),
  ("Micro-frontends et observabilité", "Module Federation (Vite plugin ou Rspack) expose un module distant chargé à l'exécution ; partager React en singleton, versions alignées, contrat d'intégration testé. Alternative plus simple : un monorepo avec déploiements indépendants par route. Observabilité : <code>@opentelemetry/sdk-trace-web</code> avec propagation du <code>traceparent</code> vers l'API (la trace du TP 34 commence dans le navigateur), Sentry ou GlitchTip pour les erreurs avec source maps, <code>web-vitals</code> vers Prometheus.",
"""// vite.config.ts (hôte)
federation({ name: 'shell', remotes: { map: 'http://map.crisis.local/assets/remoteEntry.js' }, shared: ['react', 'react-dom', 'react-router-dom'] })
const IncidentMap = lazy(() => import('map/IncidentMap'));
// OTel web
const provider = new WebTracerProvider({ resource: new Resource({ 'service.name': 'crisisshield-web' }) });
provider.addSpanProcessor(new BatchSpanProcessor(new OTLPTraceExporter({ url: '/otel/v1/traces' })));
registerInstrumentations({ instrumentations: [new FetchInstrumentation({ propagateTraceHeaderCorsUrls: [/api\\./] }), new DocumentLoadInstrumentation()] });""")],
 [("Quand les micro-frontends sont-ils une erreur ?", "Quand une seule équipe les maintient : on paie la duplication de dépendances, les contrats, les versions partagées et les tests d'intégration sans gagner l'indépendance de déploiement qui les justifie."),
  ("Différence entre <code>useTransition</code> et <code>useDeferredValue</code> ?", "<code>useTransition</code> marque une mise à jour d'état comme non urgente (on contrôle le <code>set</code>) ; <code>useDeferredValue</code> retarde une valeur qu'on ne contrôle pas (prop reçue). Les deux laissent React interrompre le rendu pour traiter une frappe.")],
 ("CrisisShield à l'échelle", ["Monorepo pnpm + Turborepo : <code>web</code>, <code>admin</code>, <code>ui</code> (Storybook, 10 composants, tests a11y), <code>contracts</code> généré depuis l'OpenAPI.", "Liste de 50 000 incidents virtualisée avec filtre en <code>useDeferredValue</code> ; clustering de la carte dans un Worker ; mesures INP avant/après.", "Carte exposée en module fédéré chargé par le shell ; traces OTel du navigateur jusqu'à PostgreSQL visibles dans Tempo."],
  "INP : filtre sur 50 000 lignes 480 ms → 40 ms (virtualisation + deferred) ; Worker : le thread principal reste < 16 ms pendant le clustering. Tempo : une trace <code>document-load → fetch /api/incidents → api → SELECT</code> avec le même trace_id. Turborepo : second build en cache < 5 s.")))

ANG.append(ch("Expert : Nx, micro-frontends, CDK, performance, Web Components, migrations", 'e',
 ["Nx structure un monorepo Angular en bibliothèques par domaine (feature, ui, data-access, util) avec des frontières vérifiées par lint et un cache de build.", "Le CDK fournit overlay, virtual scroll, drag-and-drop, harnesses ; Angular Material se thème par tokens ; les Angular Elements exportent un composant en Web Component.", "Micro-frontends par Native Federation quand plusieurs équipes déploient séparément ; observabilité OTel web ; migrations par schematics (<code>ng update</code>, NgModules → standalone, signals) sans réécriture."],
 ["Organiser un monorepo Nx avec règles de dépendances", "Optimiser une application Angular lourde (virtual scroll, defer, OnPush partout, budgets) et l'instrumenter", "Exposer et consommer des micro-frontends et des Web Components ; piloter les migrations"],
 [("Nx et frontières", "", """npx create-nx-workspace@latest crisis --preset=angular-monorepo --appName=web --standalone --style=scss
npx nx g @nx/angular:library incidents-feature --directory=libs/incidents/feature --tags=scope:incidents,type:feature
npx nx g @nx/angular:library incidents-data-access --tags=scope:incidents,type:data-access
# .eslintrc : @nx/enforce-module-boundaries : type:feature peut importer ui, data-access, util ; type:ui n'importe que ui et util ; scope:incidents n'importe pas scope:admin
npx nx affected -t test,lint,build      # seulement ce qui a changé, avec cache"""),
  ("Performance et CDK", "", """<cdk-virtual-scroll-viewport itemSize="48" class="list">
  <cs-incident-card *cdkVirtualFor="let i of incidents(); trackBy: trackId" [incident]="i" />
</cdk-virtual-scroll-viewport>
@defer (on idle; prefetch on viewport) { <cs-incident-map [incidents]="filtered()" /> }
// audit : Angular DevTools → Profiler (composants sans OnPush) ; ng build --stats-json ; budgets ; NgOptimizedImage pour les images ; provideZonelessChangeDetection()
// clustering hors thread : new Worker(new URL('./cluster.worker', import.meta.url)) — ng g web-worker cluster"""),
  ("Micro-frontends, Web Components, migrations", "", """# Native Federation : ng add @angular-architects/native-federation --type remote (carte) / --type host (shell) ; loadRemoteModule({ remoteName: 'map', exposedModule: './routes' }) dans les routes lazy
# Angular Elements : createCustomElement(IncidentCard, { injector }) ; customElements.define('cs-incident-card', el) → utilisable dans une page legacy JSP (TP 50) ou dans Vue/React
# Migrations : ng update @angular/core@20 @angular/cli@20 ; ng g @angular/core:standalone ; ng g @angular/core:control-flow ; ng g @angular/core:signal-inputs ; ng g @angular/core:output-migration ; tests verts entre chaque
# Observabilité : @opentelemetry/sdk-trace-web + FetchInstrumentation (propagation vers l'API), Sentry Angular avec ErrorHandler""")],
 [("Pourquoi des tags <code>scope</code> et <code>type</code> plutôt qu'un dossier par équipe ?", "Le lint vérifie les dépendances entre tags : une feature admin ne peut pas importer la data-access incidents. La structure devient une règle exécutée, pas une convention."),
  ("Un composant Angular exporté en Web Component dans une page React : que perd-on ?", "L'injection de dépendances du shell, le routeur partagé et le typage des inputs (attributs texte) ; on gagne l'indépendance totale. À réserver aux frontières entre technologies ou aux migrations progressives.")],
 ("CrisisShield en monorepo Nx", ["Workspace Nx avec libs par domaine et frontières lintées ; <code>nx affected</code> en CI.", "Liste virtualisée de 50 000 incidents, carte en <code>@defer</code>, zoneless, budgets ; Profiler avant/après.", "Carte en remote Native Federation ; <code>IncidentCard</code> en Web Component intégré dans la page JSP du legacy du TP 50 ; traces OTel jusqu'à la base."],
  "Attendu : violation de frontière volontaire (feature admin → data-access incidents) refusée par le lint ; CI <code>nx affected</code> ne rebuild que la lib touchée ; INP < 100 ms sur la liste ; le Web Component s'affiche dans la JSP avec ses styles encapsulés (ShadowDom) ; trace navigateur → API → SQL dans Tempo.")))

# ================================================================ VUE
VUE = [
ch("Le socle : JavaScript moderne, TypeScript et Vite", 'j',
 ["Vue 3 s'écrit en TypeScript dans des composants monofichiers (<code>.vue</code>) compilés par Vite.", "Les mêmes bases qu'en React et Angular : immutabilité, destructuring, promesses, modules, types et unions discriminées.", "Tout tourne dans un conteneur node:22 ; <code>create-vue</code> génère le projet avec TypeScript, Router, Pinia, Vitest et Playwright."],
 ["Écrire du JS/TS moderne sans surprise", "Créer un projet Vue 3 + TypeScript en Docker", "Lire un composant monofichier"],
 [("Créer le projet", "", """docker run --rm -it -v "$PWD:/app" -w /app -p 5173:5173 node:22 bash
npm create vue@latest crisisshield-web -- --ts --router --pinia --vitest --playwright --eslint
cd crisisshield-web && npm ci && npm run dev -- --host
# compose.yaml : même modèle que le cours React (volume nommé node_modules)"""),
  ("Un composant monofichier", "", """<script setup lang="ts">
import { ref } from 'vue';
const props = defineProps<{ title: string }>();
const count = ref(0);
</script>
<template>
  <h1>{{ props.title }}</h1>
  <button @click="count++">Cliqué {{ count }} fois</button>
</template>
<style scoped>button { font-weight: 700; }</style>"""),
  ("Types du domaine", "Mêmes types que dans les deux autres cours : <code>Incident</code>, <code>Priority</code>, <code>Loading&lt;T&gt;</code> en union discriminée ; <code>vue-tsc</code> vérifie les templates.", None)],
 [("Que fait <code>&lt;script setup&gt;</code> ?", "Il compile le bloc en fonction <code>setup()</code> : tout ce qui est déclaré au niveau supérieur (variables, fonctions, imports de composants) est disponible dans le template, sans <code>return</code>. C'est la syntaxe recommandée."),
  ("Pourquoi <code>scoped</code> sur le style ?", "Vue ajoute un attribut de données unique aux éléments du composant et réécrit les sélecteurs : les styles ne fuient pas. Sans lui, un <code>button {}</code> touche toute l'application.")],
 ("Projet Vue en conteneur", ["Projet généré avec TypeScript, Router, Pinia, Vitest, Playwright ; <code>vue-tsc --noEmit</code> en script.", "Types du domaine et trois fonctions pures testées.", "Un premier composant <code>IncidentCard</code> avec props typées."],
  "<code>npm run type-check</code> échoue sur une prop absente dans le template (<code>strictTemplates</code> équivalent via vue-tsc). Test : <code>mount(IncidentCard, { props: { incident } }).text()</code> contient le titre.")),

ch("Templates, directives et rendu", 'j',
 ["Le template est du HTML augmenté : <code>{{ }}</code>, <code>:prop</code> (v-bind), <code>@event</code> (v-on), <code>v-if/v-else</code>, <code>v-for</code> avec <code>:key</code>, <code>v-model</code>.", "<code>v-if</code> retire du DOM, <code>v-show</code> masque ; <code>v-for</code> exige une clé stable comme partout.", "Les événements natifs ont des modificateurs (<code>.prevent</code>, <code>.stop</code>, <code>.enter</code>) qui évitent du code."],
 ["Écrire un template complet avec conditions, listes et événements", "Choisir entre v-if et v-show, et lier des classes/styles dynamiques", "Utiliser les modificateurs d'événements et de v-model"],
 [("Directives essentielles", "", """<template>
  <p v-if="state.status === 'loading'">Chargement…</p>
  <p v-else-if="state.status === 'error'" role="alert">{{ state.error }}</p>
  <ul v-else>
    <li v-for="i in state.data" :key="i.id" :class="{ closed: i.status === 'closed', ['prio-' + i.priority]: true }">
      {{ i.title }} <button @click.stop="emit('close', i.id)" :disabled="i.status === 'closed'">Clôturer</button>
    </li>
  </ul>
  <input v-model.trim="query" @keyup.enter="search" placeholder="Rechercher" />
  <details v-show="open"><summary>Filtres</summary>…</details>
</template>"""),
  ("Rendu conditionnel et listes", "Ne jamais mettre <code>v-if</code> et <code>v-for</code> sur le même élément (priorité de <code>v-if</code> en Vue 3) : filtrer avec un <code>computed</code>. Clé = identifiant, jamais l'index d'une liste réordonnable.", None)],
 [("<code>v-if</code> ou <code>v-show</code> pour un onglet qu'on bascule cent fois ?", "<code>v-show</code> : le DOM reste, seul <code>display</code> change, pas de re-création. <code>v-if</code> pour ce qui est rarement affiché ou coûteux à garder monté."),
  ("<code>@click.stop.prevent</code> : dans quel ordre ?", "Les modificateurs s'appliquent dans l'ordre écrit : <code>stopPropagation</code> puis <code>preventDefault</code>. Pratique pour un bouton dans une carte cliquable.")],
 ("Liste d'incidents", ["<code>IncidentList</code>, <code>IncidentCard</code>, <code>PriorityBadge</code> avec données en dur ; tri et filtre via <code>computed</code>.", "Recherche avec <code>v-model.trim</code> et <code>@keyup.enter</code>.", "Test Vue Test Utils : <code>findAll('li')</code>, émission de <code>close</code>."],
  "<code>const w = mount(IncidentList, { props: { items } }); await w.find('button').trigger('click'); expect(w.emitted('close')![0]).toEqual([items[0].id])</code>. Le filtre est un <code>computed</code>, pas un <code>v-if</code> dans le <code>v-for</code>.")),

ch("Réactivité : ref, reactive, computed, watch — les signals de Vue", 'c',
 ["<code>ref</code> enveloppe une valeur (<code>.value</code>) ; <code>reactive</code> rend un objet profondément réactif par Proxy ; le template déballe les refs.", "<code>computed</code> dérive avec mise en cache et suivi automatique des dépendances (c'est un signal dérivé) ; <code>watch</code>/<code>watchEffect</code> réagissent par effet de bord.", "Le rendu est à granularité fine : seuls les composants dont les dépendances ont changé se mettent à jour ; on ne perd pas la réactivité tant qu'on ne déstructure pas un <code>reactive</code>."],
 ["Modéliser l'état avec ref/reactive/computed sans perdre la réactivité", "Utiliser watch et watchEffect à bon escient (et savoir quand un computed suffit)", "Expliquer le modèle de réactivité de Vue et le comparer aux signals Angular et à React"],
 [("Les primitives", "", """import { ref, reactive, computed, watch, watchEffect, toRefs } from 'vue';
const incidents = ref<Incident[]>([]);
const filters = reactive({ zone: '', priority: '' as Priority | '' });
const filtered = computed(() => incidents.value.filter(i => (!filters.zone || i.zone === filters.zone) && (!filters.priority || i.priority === filters.priority)));
const openCount = computed(() => filtered.value.filter(i => i.status === 'open').length);
function close(id: number) { const i = incidents.value.find(x => x.id === id); if (i) i.status = 'closed'; }   // mutation autorisée : le Proxy la voit
watch(() => filters.zone, (zone, old) => { localStorage.setItem('zone', zone); });                                 // source précise
watchEffect(() => { document.title = `${openCount.value} ouverts`; });                                              // dépendances automatiques
const { zone } = toRefs(filters);   // déstructurer sans perdre la réactivité"""),
  ("Pièges", "Déstructurer un <code>reactive</code> (<code>const { zone } = filters</code>) donne une copie inerte → <code>toRefs</code>. Oublier <code>.value</code> hors template. Remplacer un <code>reactive</code> entier (<code>filters = {…}</code>) casse le lien → muter ses champs ou utiliser un <code>ref</code>. Un <code>watch</code> qui copie une valeur dans une autre est un <code>computed</code> manquant.", None),
  ("Comparaison des trois modèles", "Vue : réactivité par Proxy et suivi automatique, mutation permise, rendu par composant à granularité fine. Angular : signals explicites (<code>signal()/set/update</code>), immutabilité par référence, zoneless. React : re-rendu du composant sur <code>setState</code>, immutabilité obligatoire, mémoïsation ou Compiler. Les trois convergent vers « valeur réactive + dérivé + effet » ; Vue l'a depuis 2014.", None)],
 [("Pourquoi <code>computed</code> plutôt qu'une méthode appelée dans le template ?", "La méthode est réévaluée à chaque rendu ; le <code>computed</code> est mis en cache tant que ses dépendances ne changent pas. Pour un filtre sur 10 000 lignes, la différence se voit."),
  ("<code>watch(filters, cb)</code> ne se déclenche pas quand <code>filters.zone</code> change. Pourquoi ?", "Sur un <code>reactive</code>, <code>watch</code> est profond par défaut… mais sur un <code>ref</code> d'objet il ne l'est pas sans <code>{ deep: true }</code>. Et préférer une source précise <code>() => filters.zone</code> : moins de déclenchements, intention claire.")],
 ("Page incidents réactive", ["État en ref/reactive, dérivés en computed, persistance par watch, titre par watchEffect.", "Sélection courante qui se réinitialise quand le filtre change (watch sur <code>filtered</code>).", "Vue DevTools : vérifier que seule la liste se met à jour à la frappe ; test avec <code>nextTick</code>."],
  "Test : <code>filters.zone = 'N1'; await nextTick(); expect(w.findAll('li').length).toBe(2)</code>. DevTools → Timeline : un changement de filtre déclenche le rendu de <code>IncidentList</code> seulement. Le <code>linkedSignal</code> d'Angular s'écrit ici <code>const selected = ref(); watch(filtered, xs => selected.value = xs[0] ?? null)</code>.")),

ch("Composants : props, emits, slots, v-model, provide/inject", 'c',
 ["<code>defineProps</code>/<code>defineEmits</code> typés ; <code>defineModel</code> crée un two-way binding en une ligne.", "Les slots (par défaut, nommés, avec portée) composent ; <code>provide/inject</code> partage dans un sous-arbre (thème, dispatch), pas un store global.", "Cycle de vie : <code>onMounted</code>, <code>onUnmounted</code>, <code>onErrorCaptured</code> ; <code>&lt;Teleport&gt;</code>, <code>&lt;KeepAlive&gt;</code>, <code>&lt;Transition&gt;</code> pour les cas classiques."],
 ["Écrire des composants réutilisables avec props, emits, model et slots", "Partager par provide/inject avec un token typé", "Utiliser les composants intégrés (Teleport, KeepAlive, Transition)"],
 [("Props, emits, model", "", """<script setup lang="ts">
const props = withDefaults(defineProps<{ zones: string[]; placeholder?: string }>(), { placeholder: 'Toutes les zones' });
const emit = defineEmits<{ changed: [zone: string] }>();
const model = defineModel<string>({ default: '' });        // parent : <ZoneFilter v-model="zone" />
function select(z: string) { model.value = z; emit('changed', z); }
</script>"""),
  ("Slots et provide/inject", "", """<!-- Panel.vue --><section><header><slot name="title" /></header><slot :count="items.length">Aucun élément</slot></section>
<!-- usage --><Panel><template #title><h2>Incidents</h2></template><template #default="{ count }">{{ count }} incidents</template></Panel>
// theme.ts
export const ThemeKey: InjectionKey<Ref<'light' | 'dark'>> = Symbol('theme');
provide(ThemeKey, theme);                 // dans App
const theme = inject(ThemeKey)!;          // dans un descendant, typé"""),
  ("Composants intégrés", "<code>&lt;Teleport to=\"body\"&gt;</code> pour une modale hors du flux ; <code>&lt;KeepAlive&gt;</code> garde l'état d'un onglet démonté ; <code>&lt;Transition&gt;</code> anime l'entrée/sortie par classes CSS ; <code>onErrorCaptured</code> joue le rôle d'error boundary.", None)],
 [("<code>defineModel</code> contre <code>props.value</code> + <code>emit('update:value')</code> ?", "C'est la même chose compilée : <code>defineModel</code> génère la prop et l'événement, et renvoie un <code>ref</code> qu'on lit et écrit. Moins de code, même contrat."),
  ("Quand provide/inject est-il le mauvais outil ?", "Pour un état global fréquent lu partout : chaque changement propage sans sélecteur, et le couplage est implicite. Pinia pour ça ; provide/inject pour l'injection contextuelle (thème, configuration, dispatch).")],
 ("Filtre, panneau et modale", ["<code>ZoneFilter</code> avec <code>defineModel</code>, <code>Panel</code> avec slots nommés et portée, thème par provide/inject.", "Modale de création en <code>Teleport</code> avec <code>Transition</code> ; erreurs capturées par <code>onErrorCaptured</code>.", "Tests : v-model depuis un composant hôte, slot rendu, injection avec <code>global.provide</code>."],
  "Test : <code>mount(ZoneFilter, { props: { modelValue: 'N1', 'onUpdate:modelValue': e => (v = e) } })</code>. <code>mount(Comp, { global: { provide: { [ThemeKey as symbol]: ref('dark') } } })</code>. La modale est trouvée dans <code>document.body</code> (Teleport), pas dans le wrapper : <code>attachTo: document.body</code>.")),

ch("Composition API et composables", 'c',
 ["Un composable est une fonction <code>useX()</code> qui encapsule état réactif, dérivés et effets : l'équivalent du hook React, sans règle d'ordre d'appel.", "VueUse fournit 200 composables prêts (debounce, localStorage, fetch, intersection observer) : ne pas réécrire.", "Un composable se teste seul (dans un composant hôte minimal ou avec <code>effectScope</code>) et se compose avec d'autres."],
 ["Extraire une logique en composable typé et testé", "Utiliser VueUse et un composable de chargement avec annulation", "Organiser les composables par domaine"],
 [("Un composable de chargement", "", """export function useIncidents(zone: Ref<string>) {
  const state = ref<Loading<Incident[]>>({ status: 'idle' });
  let ctrl: AbortController | undefined;
  watch(zone, async z => {
    ctrl?.abort(); ctrl = new AbortController();
    state.value = { status: 'loading' };
    try { const r = await fetch(`/api/incidents?zone=${encodeURIComponent(z)}`, { signal: ctrl.signal }); if (!r.ok) throw new Error(`HTTP ${r.status}`); state.value = { status: 'ok', data: await r.json() }; }
    catch (e) { if ((e as Error).name !== 'AbortError') state.value = { status: 'error', error: (e as Error).message }; }
  }, { immediate: true });
  onScopeDispose(() => ctrl?.abort());
  return { state: readonly(state), reload: () => watchTrigger() };
}
// usage : const zone = ref(''); const { state } = useIncidents(zone);"""),
  ("VueUse", "", """import { useDebounce, useLocalStorage, useIntersectionObserver, useFetch } from '@vueuse/core';
const query = ref(''); const debounced = useDebounce(query, 300);
const zone = useLocalStorage('zone', '');                                   // ref persistant
const { data, error, isFetching, execute } = useFetch(() => `/api/incidents?q=${debounced.value}`, { refetch: true }).json<Incident[]>();""")],
 [("Pourquoi les composables n'ont-ils pas la « règle des hooks » de React ?", "Ils s'exécutent une fois dans <code>setup</code> ; l'état vit dans des refs, pas dans un tableau indexé par ordre d'appel. On peut les appeler conditionnellement (mais rarement utile)."),
  ("Un composable qui reçoit une valeur brute (<code>useIncidents('N1')</code>) : problème ?", "Il ne réagit pas au changement. Accepter <code>MaybeRefOrGetter&lt;string&gt;</code> et lire avec <code>toValue()</code> : le composable marche avec une valeur, un ref ou un getter.")],
 ("Composables de CrisisShield", ["<code>useIncidents</code> avec annulation et <code>MaybeRefOrGetter</code> ; <code>useFilters</code> persistant (VueUse).", "Test du composable avec MSW : la réponse lente de l'ancienne zone ne gagne pas.", "Dossier <code>composables/</code> par domaine, exportés depuis un index."],
  "Test : <code>const zone = ref('A'); const { state } = withSetup(() => useIncidents(zone)); zone.value = 'B'; await flushPromises(); expect(state.value).toMatchObject({ status: 'ok', data: fixtures.B })</code>, avec MSW qui retarde la zone A.")),

ch("Vue Router : pages, lazy loading, guards et données", 's',
 ["Les routes sont un tableau ; chaque vue se charge paresseusement par <code>() => import()</code> ; <code>&lt;RouterView&gt;</code> imbriqué pour les layouts.", "Guards globaux et par route (<code>beforeEnter</code>) renvoient <code>true</code>, une route ou <code>false</code> ; <code>props: true</code> transmet les paramètres en props.", "TanStack Query pour Vue (<code>@tanstack/vue-query</code>) gère l'état serveur comme dans le cours React."],
 ["Configurer routes, layouts et chargement paresseux", "Protéger des routes et passer les paramètres en props typées", "Charger et invalider des données serveur avec vue-query"],
 [("Routes et guards", "", """const router = createRouter({ history: createWebHistory(), routes: [
  { path: '/', component: () => import('./layouts/Main.vue'), children: [
    { path: '', component: () => import('./views/Home.vue') },
    { path: 'incidents', component: () => import('./views/IncidentsView.vue'), meta: { requiresAuth: true } },
    { path: 'incidents/:id', component: () => import('./views/IncidentDetail.vue'), props: r => ({ id: Number(r.params.id) }) },
  ] },
  { path: '/:pathMatch(.*)*', component: NotFound },
] });
router.beforeEach(to => { const auth = useAuthStore(); if (to.meta.requiresAuth && !auth.isLoggedIn) return { path: '/login', query: { redirect: to.fullPath } }; });"""),
  ("vue-query", "", """const zone = ref('');
const { data, isPending, error } = useQuery({ queryKey: ['incidents', zone], queryFn: ({ signal }) => api.list(zone.value, signal), staleTime: 30_000 });   // la clé contient un ref : refetch quand zone change
const qc = useQueryClient();
const create = useMutation({ mutationFn: api.create, onSuccess: () => qc.invalidateQueries({ queryKey: ['incidents'] }) });""")],
 [("Pourquoi <code>props: true</code> plutôt que <code>useRoute().params</code> dans le composant ?", "Le composant devient indépendant du routeur : testable avec <code>mount(Detail, { props: { id: 42 } })</code>, réutilisable ailleurs, et typé."),
  ("Une route protégée charge son composant avant le guard ?", "Non : le guard s'exécute avant la résolution du composant lazy ; un utilisateur non connecté ne télécharge jamais le code de la page.")],
 ("Pages liste et détail", ["Routes lazy avec layout, guard d'authentification et redirection après login.", "Requêtes vue-query avec invalidation et préchargement au survol.", "Test de navigation avec un routeur mémoire (<code>createMemoryHistory</code>)."],
  "Test : <code>router.push('/incidents'); await router.isReady(); expect(router.currentRoute.value.path).toBe('/login')</code> quand non connecté. Onglet Réseau : <code>IncidentsView-*.js</code> chargé seulement après connexion.")),

ch("État global avec Pinia", 's',
 ["Pinia est le store officiel : un store = <code>defineStore</code> avec état, getters (computed) et actions ; syntaxe « setup » recommandée (refs et fonctions).", "Les composants lisent le store par <code>storeToRefs</code> pour garder la réactivité ; DevTools, persistance et tests intégrés.", "Trois familles d'état comme ailleurs : local (ref), serveur (vue-query), global client (Pinia). Pinia remplace Vuex."],
 ["Écrire un store Pinia en syntaxe setup avec actions asynchrones", "Consommer le store sans perdre la réactivité", "Tester un store et un composant qui l'utilise"],
 [("Store setup", "", """export const useIncidentsStore = defineStore('incidents', () => {
  const incidents = ref<Incident[]>([]);
  const zone = ref('');
  const status = ref<'idle' | 'loading' | 'error'>('idle');
  const open = computed(() => incidents.value.filter(i => i.status === 'open' && (!zone.value || i.zone === zone.value)));
  async function load() { status.value = 'loading'; try { incidents.value = await api.list(zone.value); status.value = 'idle'; } catch { status.value = 'error'; } }
  async function close(id: number) { const before = incidents.value; incidents.value = incidents.value.map(x => x.id === id ? { ...x, status: 'closed' } : x); try { await api.close(id); } catch { incidents.value = before; } }   // optimiste
  watch(zone, load, { immediate: true });
  return { incidents, zone, status, open, load, close };
}, { persist: { pick: ['zone'] } });   // pinia-plugin-persistedstate
// composant : const store = useIncidentsStore(); const { open, status } = storeToRefs(store); store.close(id);"""),
  ("Tests", "", """setActivePinia(createPinia());
const store = useIncidentsStore();
server.use(http.post('/api/incidents/1/close', () => HttpResponse.error()));
await store.close(1); expect(store.incidents[0].status).toBe('open');   // rollback
// composant avec store simulé : mount(List, { global: { plugins: [createTestingPinia({ initialState: { incidents: { incidents: fixtures } }, stubActions: false })] } })""")],
 [("<code>const { open } = useIncidentsStore()</code> : que se passe-t-il ?", "<code>open</code> devient une valeur figée (déstructuration d'un objet réactif). <code>storeToRefs(store)</code> renvoie des refs pour l'état et les getters ; les actions se déstructurent librement."),
  ("Pinia ou vue-query pour les incidents ?", "Les incidents sont de l'état serveur : vue-query (cache, revalidation) ; Pinia garde les filtres, la session, les préférences. Combiner les deux est la norme.")],
 ("Store des incidents", ["Store Pinia setup avec chargement, clôture optimiste et rollback, persistance de la zone.", "Composants lisant par <code>storeToRefs</code> ; DevTools : voyage dans l'état.", "Variante : incidents en vue-query, filtres en Pinia ; comparer."],
  "Test de rollback vert ; <code>createTestingPinia</code> pour la liste. Comparaison attendue : vue-query supprime <code>load</code>, <code>status</code> et le <code>watch</code> du store, et ajoute cache et refetch en arrière-plan.")),

ch("Formulaires, validation et accessibilité", 's',
 ["VeeValidate + Zod (ou Valibot) : schéma unique, validation par champ ou à la soumission, composants <code>Form</code>/<code>Field</code> ou composables <code>useForm</code>/<code>useField</code>.", "<code>v-model</code> et les modificateurs couvrent les formulaires simples ; VeeValidate prend le relais pour tableaux de champs, dépendances et erreurs serveur.", "Accessibilité : labels, <code>aria-invalid</code>, <code>aria-describedby</code>, <code>role=alert</code> ; testée par axe."],
 ["Construire un formulaire complexe avec VeeValidate et Zod", "Mapper les erreurs RFC 9457 de l'API sur les champs", "Rendre et tester l'accessibilité"],
 [("useForm + Zod", "", """const schema = toTypedSchema(z.object({ title: z.string().trim().min(3, 'Au moins 3 caractères'), priority: z.enum(['P1','P2','P3']), zone: z.string().regex(/^[A-Z][0-9]$/, 'Format A1'), contacts: z.array(z.object({ email: z.string().email() })).max(5) })
  .superRefine((v, ctx) => { if (v.priority === 'P1' && !v.zone) ctx.addIssue({ path: ['zone'], code: 'custom', message: 'Zone obligatoire en P1' }); }));
const { handleSubmit, errors, isSubmitting, setErrors, defineField } = useForm({ validationSchema: schema, initialValues: { priority: 'P2', contacts: [] } });
const [title, titleAttrs] = defineField('title');
const { fields, push, remove } = useFieldArray<{ email: string }>('contacts');
const onSubmit = handleSubmit(async values => { try { await api.create(values); } catch (e) { if (isProblem(e)) setErrors(Object.fromEntries(e.errors.map(x => [x.field, x.message]))); } });"""),
  ("Template accessible", "", """<form @submit="onSubmit" novalidate>
  <label for="title">Titre</label>
  <input id="title" v-model="title" v-bind="titleAttrs" :aria-invalid="!!errors.title" aria-describedby="title-err" />
  <p v-if="errors.title" id="title-err" role="alert">{{ errors.title }}</p>
  <div v-for="(f, i) in fields" :key="f.key"><input v-model="f.value.email" :aria-label="`Contact ${i + 1}`" /><button type="button" @click="remove(i)">Retirer</button></div>
  <button type="button" @click="push({ email: '' })">Ajouter un contact</button>
  <button :disabled="isSubmitting">Enregistrer</button>
</form>""")],
 [("Pourquoi <code>defineField</code> plutôt que <code>useField</code> pour chaque champ ?", "<code>defineField</code> renvoie le modèle et les attributs (blur, validation) en une ligne, adapté à <code>v-model</code> natif ; <code>useField</code> reste pour les composants de champ personnalisés."),
  ("Validation à la frappe ou au blur ?", "Au blur pour la première erreur (ne pas crier avant que l'utilisateur ait fini), puis à la frappe une fois le champ en erreur : <code>validateOnBlur: true, validateOnInput: false</code> puis <code>validateOnModelUpdate</code> après première erreur — c'est le défaut de VeeValidate.")],
 ("Formulaire d'incident", ["Schéma Zod partagé, formulaire VeeValidate avec contacts dynamiques et règle P1/zone.", "Erreurs 422 mappées par <code>setErrors</code> ; soumission désactivée pendant l'envoi.", "Zéro violation axe ; test clavier."],
  "Test : <code>await w.find('#title').setValue('Fu'); await w.find('form').trigger('submit'); expect(await w.find('[role=alert]').text()).toContain('Au moins 3')</code> ; MSW 422 → <code>errors.title</code> égal au message serveur ; <code>axe(w.element)</code> sans violation.")),

ch("Tests : Vitest, Vue Test Utils, MSW, Playwright", 's',
 ["Vue Test Utils monte un composant dans jsdom ; on interroge par rôle et texte (Testing Library pour Vue existe aussi) ; MSW simule l'API.", "Les composables se testent dans un hôte minimal ; les stores avec <code>createTestingPinia</code> ; le routeur en mémoire.", "Playwright couvre les parcours critiques contre le build ; pipeline GitLab avec type-check, lint, unit, build, e2e."],
 ["Tester composants, composables, stores et routes", "Mettre en place MSW et Playwright en conteneur", "Configurer la quality gate"],
 [("Composant + MSW", "", """it('crée un incident', async () => {
  const w = mount(IncidentsView, { global: { plugins: [router, createPinia(), VueQueryPlugin] } });
  expect(await findByRole(w.element, 'heading', { name: 'Fuite gaz' })).toBeTruthy();   // @testing-library/dom
  await w.find('#title').setValue('Inondation'); await w.find('form').trigger('submit'); await flushPromises();
  expect(w.text()).toContain('Inondation');
});"""),
  ("Pipeline", "Identique au cours React : <code>vue-tsc --noEmit</code>, ESLint (<code>eslint-plugin-vue</code>, a11y), <code>vitest run --coverage</code>, <code>vite build</code>, Playwright dans <code>mcr.microsoft.com/playwright</code> ; rapport JUnit et couverture dans la MR.", None)],
 [("<code>await nextTick()</code> ou <code>await flushPromises()</code> ?", "<code>nextTick</code> attend le prochain rendu Vue ; <code>flushPromises</code> vide la file des promesses (réponses MSW, <code>await</code> dans les actions). Après une requête simulée, il faut le second."),
  ("Que stubber, que ne pas stubber ?", "Stubber les composants lourds et sans rapport (carte), jamais le composant testé ni ses enfants directs qui portent le comportement ; <code>shallowMount</code> est rarement le bon choix.")],
 ("Quality gate du front Vue", ["Tests composants avec MSW, composables et store ; couverture ≥ 80 % sur le nouveau code.", "Playwright en conteneur sur trois parcours.", "Pipeline GitLab en cinq jobs."],
  "MR avec onglet Tests, couverture publiée, trace Playwright en cas d'échec ; <code>vue-tsc</code> bloque sur une prop manquante dans un template.")),

ch("Production : Nuxt et SSR, performance, sécurité, déploiement", 'e',
 ["Build Vite + nginx durci comme pour React ; <code>defineAsyncComponent</code> et routes lazy découpent ; <code>&lt;Suspense&gt;</code> pour les composants asynchrones.", "Nuxt apporte SSR, rendu hybride par route, routage par fichiers, server routes (Nitro), <code>useFetch</code> avec transfert d'état : le choix pour un site public ; SPA + BFF pour l'application métier.", "Sécurité : <code>v-html</code> est le <code>dangerouslySetInnerHTML</code> de Vue (DOMPurify), CSP, pas de secret dans <code>VITE_*</code>, dépendances scannées."],
 ["Optimiser et déployer une SPA Vue en conteneur", "Mettre en place Nuxt (SSR, hybride, server routes) et savoir quand", "Sécuriser et observer une application Vue en production"],
 [("Découpage et Suspense", "", """const IncidentMap = defineAsyncComponent({ loader: () => import('./IncidentMap.vue'), loadingComponent: Spinner, delay: 200 });
<Suspense><IncidentDetail :id="id" /><template #fallback><Spinner /></template></Suspense>   <!-- IncidentDetail a un await dans setup -->
// Dockerfile et nginx.conf : identiques au cours React (try_files, cache immutable, CSP, proxy /api)"""),
  ("Nuxt en trois notions", "", """npx nuxi@latest init crisisshield-site      # dans node:22
# pages/incidents/[id].vue → route ; server/api/incidents.get.ts → route serveur Nitro (BFF intégré) ; composables auto-importés
const { data, status } = await useFetch(`/api/incidents/${id}`);   // exécuté côté serveur, état transféré, pas de double requête
// nuxt.config.ts : routeRules: { '/': { prerender: true }, '/incidents/**': { ssr: true }, '/admin/**': { ssr: false } }   // hybride par route
# déploiement : node .output/server/index.mjs (image node:22-alpine) ou préRendu statique sur nginx"""),
  ("Sécurité et observabilité", "<code>v-html</code> uniquement avec <code>DOMPurify.sanitize</code> ; CSP avec nonce en SSR (Nuxt Security module) ; authentification par BFF et cookie HttpOnly ; <code>npm audit</code>, Renovate ; OTel web et <code>web-vitals</code> comme pour React ; Nuxt : <code>nuxt analyze</code> pour le bundle.", None)],
 [("Quand choisir Nuxt plutôt que Vue seul ?", "SEO, premier affichage critique, contenu public, ou besoin d'un BFF léger intégré (Nitro). Pour CrisisShield (authentifié, métier) : Vue SPA derrière le BFF Spring ; le portail public d'information de crise, lui, serait en Nuxt pré-rendu."),
  ("<code>routeRules</code> avec <code>ssr: false</code> sur <code>/admin</code> : pourquoi ?", "L'administration n'a pas besoin de SEO ni de premier rendu serveur, et évite les pièges d'hydratation (composants riches, accès à window) : rendu client uniquement, comme une SPA.")],
 ("Mise en production du front Vue", ["Image nginx non root avec CSP, cache, scan et signature ; Lighthouse CI avec budget.", "Portail public d'information en Nuxt pré-rendu (3 pages) avec une server route qui lit l'API ; mesurer LCP.", "Déploiement Kubernetes des deux (SPA derrière BFF, portail statique) avec le Deployment de référence."],
  "Attendu : SPA < 30 Mo d'image, performance Lighthouse ≥ 90 ; portail Nuxt pré-rendu servi par nginx avec LCP < 1,5 s ; aucun jeton dans le navigateur ; <code>v-html</code> absent du code (règle ESLint <code>vue/no-v-html</code> activée).")),
]

# ================================================================ CLOUD
CLOUD = [
ch("Fondations : modèles de service, régions, responsabilité partagée, premier compte", 'j',
 ["IaaS, CaaS, PaaS, FaaS, SaaS : plus on monte, moins on exploite et moins on contrôle ; on choisit le niveau le plus haut compatible avec les contraintes.", "Région, zone de disponibilité, edge : multi-AZ est le minimum, multi-région une décision coûteuse.", "Le compte se prépare avant la première ressource : MFA sur root, identité SSO, budget et alertes, CloudTrail. Ce cours utilise AWS comme référence et donne les équivalents Azure et GCP."],
 ["Expliquer les modèles de service et de déploiement et choisir", "Créer un compte gouverné (root verrouillé, SSO, budget, journal) en conteneur", "Estimer un coût avant de créer"],
 [("Le compte, dans l'ordre", "", """# console : MFA sur root, puis plus jamais root ; IAM Identity Center : un utilisateur, un groupe Admins, un permission set ; Billing : budget 20 $/mois avec alertes 50/80/100 %
alias awsc='docker run --rm -it -v "$HOME/.aws:/root/.aws" amazon/aws-cli'
awsc configure sso && awsc sso login --profile sandbox
awsc sts get-caller-identity --profile sandbox          # assumed-role/AWSReservedSSO_… : aucune clé statique
awsc cloudtrail create-trail --name org --s3-bucket-name trail-$ACCOUNT --is-multi-region-trail --profile sandbox && awsc cloudtrail start-logging --name org --profile sandbox
awsc ce get-cost-and-usage --time-period Start=$(date -d '-30 days' +%F),End=$(date +%F) --granularity MONTHLY --metrics UnblendedCost --profile sandbox"""),
  ("Estimer avant de créer", "AWS Pricing Calculator, <code>infracost</code> sur du Terraform, et les trois postes qu'on oublie : NAT Gateway, sortie de données, adresses IP publiques. Règle du cours : chaque TP se termine par la destruction et la vérification (<code>resourcegroupstaggingapi get-resources</code>).", None),
  ("Équivalents", "Compte ↔ abonnement (Azure) ↔ projet (GCP) ; région/AZ identiques ; Identity Center ↔ Entra ID ↔ Cloud Identity ; CloudTrail ↔ Activity Log ↔ Cloud Audit Logs ; Cost Explorer ↔ Cost Management ↔ Billing reports.", None)],
 [("Pourquoi ne jamais utiliser root après la configuration ?", "Root échappe à toutes les politiques IAM et SCP : une clé root fuitée est un compte perdu. On le verrouille par MFA et on l'utilise pour trois opérations (facturation, fermeture, récupération)."),
  ("Une région ou plusieurs pour CrisisShield ?", "Une région, trois AZ : disponibilité 99,99 % des services managés, latence locale, données en France/UE. Multi-région seulement pour un RTO global ou une exigence réglementaire, avec le coût des données répliquées.")],
 ("Compte sandbox gouverné", ["Root sous MFA, Identity Center, profil SSO en conteneur, budget et alertes, CloudTrail multi-région, GuardDuty.", "Un bucket S3 privé chiffré, puis destruction et vérification « rien ne reste ».", "Tableau des équivalents AWS/Azure/GCP pour dix services."],
  "Preuve : sortie de <code>get-caller-identity</code> sans utilisateur IAM ; <code>~/.aws/credentials</code> absent ; coût du mois < 1 $ ; <code>get-resources</code> ne renvoie que trail, GuardDuty et Config.")),

ch("Identité et accès : IAM, rôles, OIDC, organisation", 'j',
 ["Tout est refusé par défaut ; un deny explicite gagne toujours ; les politiques d'identité, de ressource, les SCP et les permission boundaries se combinent.", "Plus aucune clé statique : rôles pour les machines (instance profile, rôle de tâche), OIDC pour la CI, Identity Center pour les humains.", "Organizations et SCP bornent ce qu'un compte peut faire, même pour son administrateur."],
 ["Écrire et lire une politique IAM au moindre privilège", "Faire assumer un rôle par une charge, une CI (OIDC) et un humain (SSO)", "Structurer une organisation avec SCP"],
 [("Politique au moindre privilège", "", """{ "Version": "2012-10-17", "Statement": [
  { "Effect": "Allow", "Action": ["s3:GetObject", "s3:PutObject"], "Resource": "arn:aws:s3:::crisis-uploads/*", "Condition": { "StringEquals": { "s3:x-amz-server-side-encryption": "aws:kms" } } },
  { "Effect": "Allow", "Action": "secretsmanager:GetSecretValue", "Resource": "arn:aws:secretsmanager:eu-west-3:123456789012:secret:crisis/prod/db-*" } ] }
# tester : awsc iam simulate-principal-policy --policy-source-arn arn:aws:iam::…:role/crisis-api-task --action-names s3:DeleteObject --resource-arns arn:aws:s3:::crisis-uploads/x
# Access Analyzer : findings sur les accès externes ; IAM Access Advisor : actions jamais utilisées → à retirer"""),
  ("OIDC pour la CI, rôle pour la charge", "", """resource "aws_iam_openid_connect_provider" "gitlab" { url = "https://gitlab.local" client_id_list = ["https://gitlab.local"] }
resource "aws_iam_role" "ci_deploy" {
  assume_role_policy = jsonencode({ Statement = [{ Effect = "Allow", Principal = { Federated = aws_iam_openid_connect_provider.gitlab.arn }, Action = "sts:AssumeRoleWithWebIdentity",
    Condition = { StringEquals = { "gitlab.local:sub" = "project_path:crisisshield/api:ref_type:branch:ref:main" } } }] }) }
# job : id_tokens: { AWS_TOKEN: { aud: https://gitlab.local } } → aws sts assume-role-with-web-identity --role-arn … --web-identity-token $AWS_TOKEN --duration-seconds 900
# ECS : task_role_arn = rôle avec la politique ci-dessus ; EKS : IRSA / Pod Identity ; EC2 : instance profile"""),
  ("Organisation et SCP", "", """# OUs : security, shared, workloads/{dev,prod} ; SCP « garde-fous » attachée à la racine :
{ "Effect": "Deny", "Action": "*", "Resource": "*", "Condition": { "StringNotEquals": { "aws:RequestedRegion": ["eu-west-3", "eu-west-1"] }, "ArnNotLike": { "aws:PrincipalARN": "arn:aws:iam::*:role/OrgAdmin" } } }
{ "Effect": "Deny", "Action": ["cloudtrail:StopLogging", "cloudtrail:DeleteTrail", "guardduty:DeleteDetector"], "Resource": "*" }
# Azure : Management Groups + Azure Policy ; GCP : Organization Policy + folders""")],
 [("Une politique d'identité autorise <code>s3:*</code>, la politique du bucket refuse la suppression : résultat ?", "Refus : le deny explicite de la politique de ressource gagne. C'est ce qui protège les sauvegardes même contre un rôle trop large."),
  ("Pourquoi <code>ref:main</code> dans la condition du rôle CI ?", "Sans elle, une branche de fonctionnalité (donc n'importe quel contributeur) pourrait assumer le rôle de déploiement. La condition lie le rôle à l'identité exacte du pipeline.")],
 ("Identité de CrisisShield", ["Rôle de tâche au moindre privilège, testé par <code>simulate-principal-policy</code> et Access Analyzer.", "Rôle OIDC GitLab borné à main ; job qui déploie sans variable secrète ; tentative depuis une autre branche refusée.", "Organisation à quatre comptes avec deux SCP ; preuve qu'un admin de compte ne peut pas créer en us-east-1."],
  "Preuves : <code>simulate</code> → implicitDeny sur <code>s3:DeleteObject</code> ; job de branche : <code>AccessDenied</code> à l'assume-role ; <code>aws ec2 run-instances --region us-east-1</code> depuis le compte dev → <code>explicit deny in a service control policy</code>.")),

ch("Réseau : VPC, routage, sécurité, DNS, équilibrage, hybride", 'c',
 ["Un VPC de production : trois AZ × (public, privé, base), tables de routage explicites, NAT par AZ en prod, endpoints pour S3/ECR/Secrets, aucune IP publique sur les instances.", "Security groups par référence (stateful, allow seulement) pour tout ; NACL pour quelques refus grossiers ; Network Firewall pour l'inspection.", "Route 53 (zones publiques et privées, routage pondéré/latence/failover), ALB/NLB, CloudFront, et l'hybride par VPN site-à-site ou Direct Connect, Transit Gateway en hub."],
 ["Concevoir et coder un VPC de production", "Chaîner SG, endpoints, DNS et load balancer", "Relier un site et le cloud, et choisir entre peering et Transit Gateway"],
 [("VPC en Terraform (module)", "", """module "network" {
  source = "terraform-aws-modules/vpc/aws"; version = "~> 5.13"
  name = "crisis-prod"; cidr = "10.20.0.0/16"; azs = ["eu-west-3a", "eu-west-3b", "eu-west-3c"]
  public_subnets = ["10.20.1.0/24", "10.20.2.0/24", "10.20.3.0/24"]; private_subnets = ["10.20.11.0/24", "10.20.12.0/24", "10.20.13.0/24"]; database_subnets = ["10.20.21.0/24", "10.20.22.0/24", "10.20.23.0/24"]
  enable_nat_gateway = true; one_nat_gateway_per_az = true; enable_dns_hostnames = true; enable_flow_log = true; flow_log_destination_type = "s3"
}
resource "aws_vpc_endpoint" "s3" { vpc_id = module.network.vpc_id; service_name = "com.amazonaws.eu-west-3.s3"; route_table_ids = module.network.private_route_table_ids }
# Interface endpoints : ecr.api, ecr.dkr, secretsmanager, logs, sts — avec un SG qui n'accepte que 443 depuis le VPC"""),
  ("Chaîne SG et LB", "", """Internet → ALB (SG : 443 depuis 0.0.0.0/0, WAF) → SG api (8080 depuis SG alb) → SG db (5432 depuis SG api)
# Route 53 : zone publique crisisshield.example (alias A → ALB), zone privée crisis.internal (services) ; enregistrement failover vers la région secondaire avec health check
# CloudFront devant le front statique (S3 privé + OAC) et devant l'ALB : cache, TLS au bord, Shield
# NLB quand il faut TCP brut, IP fixe ou PrivateLink pour exposer un service à un autre VPC sans peering"""),
  ("Hybride et multi-VPC", "VPN site-à-site (IPsec, minutes à monter, ~1 Gb/s) pour commencer ; Direct Connect (liaison dédiée, latence stable) quand le trafic ou la conformité l'exigent. Peering pour deux VPC ; Transit Gateway dès trois VPC ou un site : hub avec tables de routage par spoke (spokes isolés entre eux). IPAM pour éviter les chevauchements ; Route 53 Resolver pour le DNS croisé.", None)],
 [("Un NAT par AZ en prod, un seul en dev : pourquoi ?", "Un NAT vit dans une AZ ; si elle tombe, les sous-réseaux privés des autres AZ perdent Internet. En prod on paie trois NAT pour la résilience ; en dev on économise 64 $/mois."),
  ("Peering ou Transit Gateway ?", "Peering : point à point, non transitif, gratuit hors trafic, bien pour deux VPC. TGW : hub, transitif, tables de routage, VPN et Direct Connect attachés, coût par attachement et par Go ; obligatoire dès que ça devient un graphe.")],
 ("Réseau de CrisisShield", ["VPC trois AZ en module avec endpoints, flow logs vers S3, NAT par AZ en prod et unique en dev (variable).", "ALB + WAF + certificat ACM + Route 53, chaîne de SG par référence, CloudFront devant le front.", "Tunnel VPN (LocalStack ou tunnel WireGuard du TP 24) et Transit Gateway avec deux spokes isolés ; test : spoke A ne joint pas spoke B, les deux joignent shared."],
  "Preuves : <code>curl</code> depuis un conteneur privé vers S3 passe sans NAT (flow log : destination endpoint) ; <code>nc -zv</code> de A vers B expire, vers shared passe ; infracost montre le NAT à 32 $ × 3 en prod et × 1 en dev.")),

ch("Calcul : EC2, conteneurs (ECS, EKS), serverless, autoscaling", 'c',
 ["EC2 quand on veut la machine (ou un logiciel qui l'exige) ; ECS Fargate pour des conteneurs sans nœuds ; EKS pour Kubernetes standard ; Lambda et App Runner pour l'événementiel et le PaaS.", "L'autoscaling se fait sur une métrique qui reflète la charge (requêtes par cible, lag), avec des politiques de suivi de cible ; Spot et Graviton réduisent la facture.", "Les images de machine viennent de Packer (cours DevOps TP 18), les images de conteneur sont déployées par digest."],
 ["Choisir le service de calcul avec des critères", "Déployer un service conteneurisé sur ECS Fargate et sur EKS", "Configurer l'autoscaling et les instances Spot/Graviton"],
 [("ECS Fargate, en Terraform", "", """resource "aws_ecs_service" "api" {
  name = "api"; cluster = aws_ecs_cluster.main.id; task_definition = aws_ecs_task_definition.api.arn; desired_count = 2; launch_type = "FARGATE"
  capacity_provider_strategy { capacity_provider = "FARGATE_SPOT"; weight = 2 } capacity_provider_strategy { capacity_provider = "FARGATE"; weight = 1; base = 1 }   # 1 tâche garantie on-demand, le reste Spot
  network_configuration { subnets = module.network.private_subnets; security_groups = [aws_security_group.api.id] }
  load_balancer { target_group_arn = aws_lb_target_group.api.arn; container_name = "api"; container_port = 8080 }
  deployment_circuit_breaker { enable = true; rollback = true }; lifecycle { ignore_changes = [desired_count] }
}
resource "aws_appautoscaling_target" "api" { service_namespace = "ecs"; resource_id = "service/crisis/api"; scalable_dimension = "ecs:service:DesiredCount"; min_capacity = 2; max_capacity = 10 }
resource "aws_appautoscaling_policy" "api" { policy_type = "TargetTrackingScaling"; target_tracking_scaling_policy_configuration { predefined_metric_specification { predefined_metric_type = "ALBRequestCountPerTarget"; resource_label = "…" } target_value = 500 } }"""),
  ("EKS en deux commandes, et ce qui change", "", """# module terraform-aws-modules/eks : cluster 1.31, nœuds managés Graviton (m7g) en 3 AZ, add-ons vpc-cni/coredns/ebs-csi, IRSA ou Pod Identity, Karpenter pour le scaling des nœuds
awsc eks update-kubeconfig --name crisis --profile sandbox   # puis tout le niveau 5 du parcours DevOps s'applique tel quel
# différences avec kind : LoadBalancer = NLB/ALB via AWS Load Balancer Controller ; StorageClass gp3 via EBS CSI ; identités des Pods par IRSA/Pod Identity ; audit vers CloudWatch ; coût : 73 $/mois le control plane + nœuds"""),
  ("EC2 quand même", "Pour un logiciel non conteneurisable, un GPU, ou une base auto-gérée : Auto Scaling Group sur une AMI Packer, instance profile, SSM Session Manager (pas de SSH ni de port 22), Spot pour le batch, Savings Plans sur le socle. Critères de choix en entretien : compétence de l'équipe, portabilité, profil de charge, coût à l'échelle, exploitation.", None)],
 [("ECS Fargate ou EKS pour une équipe de quatre ?", "Fargate : pas de nœuds, pas de control plane à payer ni à mettre à jour, IAM natif ; on perd la portabilité et l'écosystème Kubernetes. EKS si l'équipe a la compétence et vise plusieurs clouds ou des outils Kubernetes (ArgoCD, Kyverno)."),
  ("Pourquoi <code>ALBRequestCountPerTarget</code> plutôt que le CPU ?", "Le CPU réagit tard et dépend de la JVM ; le nombre de requêtes par cible reflète la charge réelle et l'objectif (55 req/s par Pod mesuré au TP 45).")],
 ("CrisisShield sur ECS puis EKS", ["Service ECS Fargate avec Spot pondéré, circuit breaker, autoscaling sur requêtes par cible ; test de charge k6 et observation du scaling.", "Cluster EKS Graviton par module ; déploiement du chart du TP 28 avec ALB Controller et Pod Identity ; comparaison de coût infracost ECS contre EKS.", "Destruction complète."],
  "Preuves : <code>describe-services</code> montre desired 2 → 6 pendant k6 puis retour ; sur EKS, <code>kubectl get svc</code> avec l'adresse de l'ALB, <code>aws sts get-caller-identity</code> depuis un Pod renvoie le rôle Pod Identity ; infracost : ECS ≈ 60 $ contre EKS ≈ 190 $ pour la même charge en sandbox.")),

ch("Stockage et données : S3, EBS/EFS, RDS/Aurora, DynamoDB, caches, sauvegardes", 'c',
 ["S3 : objet, 11 neuf de durabilité, classes et cycle de vie, versioning et Object Lock, chiffrement par défaut, accès privé (OAC pour CloudFront).", "EBS pour un disque d'instance, EFS pour un partage NFS, FSx pour les cas spécialisés ; snapshots automatisés par Data Lifecycle Manager ou AWS Backup.", "RDS Multi-AZ, Aurora (stockage réparti, bascule en secondes, Global Database), DynamoDB (clé-valeur à l'échelle, modèle d'accès d'abord), ElastiCache (Redis) : chacun pour un profil, et AWS Backup pour tout."],
 ["Configurer un bucket S3 sûr et économique", "Choisir et déployer la base adaptée (RDS, Aurora, DynamoDB) avec sauvegardes testées", "Mettre en place un cache et une politique de sauvegarde centralisée"],
 [("S3 sûr par défaut", "", """resource "aws_s3_bucket" "uploads" { bucket = "crisis-uploads-${local.account}" }
resource "aws_s3_bucket_public_access_block" "u" { bucket = aws_s3_bucket.uploads.id; block_public_acls = true; block_public_policy = true; ignore_public_acls = true; restrict_public_buckets = true }
resource "aws_s3_bucket_server_side_encryption_configuration" "u" { bucket = aws_s3_bucket.uploads.id; rule { apply_server_side_encryption_by_default { sse_algorithm = "aws:kms"; kms_master_key_id = aws_kms_key.data.arn } bucket_key_enabled = true } }
resource "aws_s3_bucket_versioning" "u" { bucket = aws_s3_bucket.uploads.id; versioning_configuration { status = "Enabled" } }
resource "aws_s3_bucket_lifecycle_configuration" "u" { bucket = aws_s3_bucket.uploads.id; rule { id = "tiering"; status = "Enabled"; transition { days = 30; storage_class = "INTELLIGENT_TIERING" } noncurrent_version_expiration { noncurrent_days = 90 } abort_incomplete_multipart_upload { days_after_initiation = 7 } } }
# sauvegardes : bucket dédié avec object_lock_configuration { rule { default_retention { mode = "COMPLIANCE"; days = 30 } } } dans un compte séparé + réplication"""),
  ("Bases : RDS, Aurora, DynamoDB", "", """resource "aws_rds_cluster" "main" { engine = "aurora-postgresql"; engine_version = "16.4"; database_name = "crisis"; master_username = "crisis"; manage_master_user_password = true; storage_encrypted = true; backup_retention_period = 14; deletion_protection = true; enabled_cloudwatch_logs_exports = ["postgresql"] }
resource "aws_rds_cluster_instance" "w" { count = 2; cluster_identifier = aws_rds_cluster.main.id; instance_class = "db.r7g.large"; performance_insights_enabled = true }   # 1 writer + 1 reader, bascule < 30 s
# RDS Proxy devant Aurora : pooling pour Lambda et ECS, IAM auth
resource "aws_dynamodb_table" "sessions" { name = "crisis-sessions"; billing_mode = "PAY_PER_REQUEST"; hash_key = "pk"; range_key = "sk"; attribute { name = "pk"; type = "S" } attribute { name = "sk"; type = "S" } ttl { attribute_name = "expires"; enabled = true } point_in_time_recovery { enabled = true } }
# DynamoDB : modéliser par requêtes (single-table design), pas par entités ; GSI pour les autres accès ; jamais de scan en production"""),
  ("Sauvegardes centralisées et test", "AWS Backup : un plan (quotidien 35 j, mensuel 1 an), un coffre avec Vault Lock dans un compte de sauvegarde, copie inter-région ; restauration testée en CI (comme le TP 44) : restaurer le snapshot Aurora de la veille dans un cluster temporaire, lancer les tests, détruire, publier la durée.", None)],
 [("<code>manage_master_user_password = true</code> : que change-t-il ?", "Le mot de passe est généré et stocké dans Secrets Manager avec rotation gérée ; il n'apparaît ni dans le code ni dans le state Terraform. C'est le « zéro secret statique » du niveau 7 appliqué à RDS."),
  ("DynamoDB pour les incidents de CrisisShield ?", "Non : requêtes ad hoc, jointures, géographie, transactions multi-tables → PostgreSQL. DynamoDB pour les sessions, les compteurs, les événements par clé avec un modèle d'accès connu et un débit élevé.")],
 ("Données de CrisisShield sur AWS", ["Buckets uploads et sauvegardes (Object Lock, compte séparé), CloudFront + OAC pour le front.", "Aurora PostgreSQL writer + reader, RDS Proxy, Performance Insights ; DynamoDB pour les sessions avec TTL ; ElastiCache Redis pour le cache.", "Plan AWS Backup avec Vault Lock et job de restauration testée ; destruction (avec <code>skip_final_snapshot</code> justifié en sandbox)."],
  "Preuves : bascule Aurora forcée (<code>failover-db-cluster</code>) chronométrée < 30 s pendant une boucle curl ; suppression d'un objet du coffre refusée (WORM) ; restauration du snapshot dans un cluster temporaire en 9 min avec tests verts ; <code>aws s3api get-bucket-policy-status</code> → non public.")),

ch("Serverless et événementiel : Lambda, files, événements, orchestration", 's',
 ["Lambda exécute du code par événement, facturé à la milliseconde ; les limites (15 min, mémoire, cold start) orientent les usages : traitements courts, événementiels, pics irréguliers.", "SQS (file, retries, DLQ), SNS (fan-out), EventBridge (bus, règles, schémas), Step Functions (orchestration avec compensation) : l'architecture événementielle du niveau 8 en services managés.", "API Gateway (HTTP API) ou ALB devant Lambda ; Java natif (Quarkus/GraalVM) ou SnapStart pour le cold start ; Powertools pour logs, traces et métriques."],
 ["Déployer une fonction Java sur Lambda avec cold start maîtrisé", "Composer SQS, SNS, EventBridge avec DLQ et idempotence", "Orchestrer un flux avec Step Functions et exposer par API Gateway"],
 [("Lambda Java natif", "", """resource "aws_lambda_function" "report" {
  function_name = "crisis-report"; runtime = "provided.al2023"; handler = "not.used"; architectures = ["arm64"]; memory_size = 512; timeout = 60
  filename = "report-lambda/target/function.zip"; source_code_hash = filebase64sha256("report-lambda/target/function.zip"); role = aws_iam_role.report.arn
  environment { variables = { DB_SECRET_ARN = aws_secretsmanager_secret.db.arn, POWERTOOLS_SERVICE_NAME = "report" } }
  tracing_config { mode = "Active" }; vpc_config { subnet_ids = module.network.private_subnets; security_group_ids = [aws_security_group.lambda.id] }
}
resource "aws_lambda_event_source_mapping" "queue" { event_source_arn = aws_sqs_queue.reports.arn; function_name = aws_lambda_function.report.arn; batch_size = 10; function_response_types = ["ReportBatchItemFailures"] }
# JVM classique : runtime java21 + snap_start { apply_on = "PublishedVersions" } → cold start 3 s → 200 ms ; natif : 120 ms (mesuré au TP 46)"""),
  ("Files et événements", "", """resource "aws_sqs_queue" "reports" { name = "crisis-reports"; visibility_timeout_seconds = 90; redrive_policy = jsonencode({ deadLetterTargetArn = aws_sqs_queue.reports_dlq.arn, maxReceiveCount = 3 }) }
resource "aws_cloudwatch_event_rule" "incident_created" { event_bus_name = "crisis"; event_pattern = jsonencode({ source = ["crisis.incidents"], "detail-type" = ["IncidentCreated"], detail = { priority = ["P1"] } }) }
resource "aws_cloudwatch_event_target" "notify" { rule = aws_cloudwatch_event_rule.incident_created.name; event_bus_name = "crisis"; arn = aws_sns_topic.p1.arn; dead_letter_config { arn = aws_sqs_queue.events_dlq.arn } retry_policy { maximum_retry_attempts = 5 } }
# l'API publie sur EventBridge (PutEvents) depuis l'outbox ; consommateurs idempotents par id d'événement ; Schema Registry EventBridge pour les contrats"""),
  ("Step Functions et API Gateway", "Une machine d'états « déclarer une crise » : créer les incidents liés (Lambda), mobiliser (Lambda, retry), notifier (SNS), avec des états Catch qui déclenchent la compensation — l'équivalent managé de la saga Temporal du TP 46, avec historique dans la console. API Gateway HTTP API + autorisateur JWT (Keycloak) devant les fonctions ; throttling et clés d'API pour les partenaires ; logs d'accès vers CloudWatch.", None)],
 [("Que fait <code>ReportBatchItemFailures</code> ?", "La fonction renvoie la liste des messages en échec : seuls ceux-là reviennent dans la file, les autres sont acquittés. Sans, tout le lot est rejoué et les messages traités le sont deux fois."),
  ("Lambda dans un VPC : coût caché ?", "Pas de cold start supplémentaire depuis 2019 (ENI partagées), mais pas de sortie Internet sans NAT : d'où les endpoints VPC pour Secrets Manager, S3 et les services appelés, et RDS Proxy pour ne pas saturer la base en connexions.")],
 ("Reporting et notifications serverless", ["Lambda Java native ARM avec Powertools, SQS + DLQ, event source mapping avec échecs partiels ; mesure des cold starts natif/SnapStart/JVM.", "Bus EventBridge <code>crisis</code>, règle P1 → SNS (e-mail de test) avec DLQ ; schéma enregistré.", "Step Functions « déclarer une crise » avec compensation testée ; HTTP API avec autorisateur JWT Keycloak ; traces X-Ray de bout en bout."],
  "Preuves : cold start natif ≈ 120 ms, SnapStart ≈ 250 ms, JVM ≈ 3 s ; message empoisonné dans la DLQ après 3 tentatives ; exécution Step Functions avec état Failed et compensation visible ; appel sans jeton → 401 par API Gateway avant toute fonction.")),

ch("Observabilité et sécurité cloud : CloudWatch, CloudTrail, GuardDuty, KMS, WAF", 's',
 ["CloudWatch (métriques, logs, alarmes, Container Insights) et X-Ray sont le socle natif ; OpenTelemetry (ADOT) exporte vers Prometheus/Tempo/Loki du niveau 6 quand on veut rester portable.", "CloudTrail (qui a fait quoi), Config (est-ce conforme), GuardDuty (menace détectée), Security Hub (agrégation, CIS), Inspector (vulnérabilités), Detective : chaque service répond à une question ; on les active tous avant la première charge.", "KMS (clés, rotation, politiques, chiffrement d'enveloppe), Secrets Manager (rotation), WAF (règles gérées, rate limit), Shield : la sécurité des données et du bord."],
 ["Instrumenter et alerter avec CloudWatch, ou exporter par ADOT", "Activer et exploiter les services de détection et de conformité", "Chiffrer avec KMS et protéger le bord avec WAF"],
 [("Alarmes et logs", "", """resource "aws_cloudwatch_metric_alarm" "api_5xx" { alarm_name = "api-5xx-rate"; comparison_operator = "GreaterThanThreshold"; evaluation_periods = 2; threshold = 1
  metric_query { id = "e1"; expression = "100*m1/m2"; label = "5xx %"; return_data = true }
  metric_query { id = "m1"; metric { namespace = "AWS/ApplicationELB"; metric_name = "HTTPCode_Target_5XX_Count"; period = 60; stat = "Sum"; dimensions = { LoadBalancer = aws_lb.main.arn_suffix } } }
  metric_query { id = "m2"; metric { namespace = "AWS/ApplicationELB"; metric_name = "RequestCount"; period = 60; stat = "Sum"; dimensions = { LoadBalancer = aws_lb.main.arn_suffix } } }
  alarm_actions = [aws_sns_topic.oncall.arn]; treat_missing_data = "notBreaching" }
resource "aws_cloudwatch_log_group" "api" { name = "/crisis/api"; retention_in_days = 30; kms_key_id = aws_kms_key.logs.arn }
# Logs Insights : fields @timestamp, level, msg | filter level = "ERROR" | stats count() by bin(5m) ; métrique filtre → alarme
# ADOT Collector en sidecar ECS ou DaemonSet EKS : receivers otlp → exporters awsxray, prometheusremotewrite (AMP) ou vers la stack du niveau 6"""),
  ("Détection et conformité", "", """awsc guardduty create-detector --enable --features '[{"Name":"RUNTIME_MONITORING","Status":"ENABLED"}]' --profile sandbox
awsc securityhub enable-security-hub --enable-default-standards --profile sandbox     # CIS, AWS Foundational
awsc configservice put-config-rule --config-rule '{"ConfigRuleName":"s3-bucket-ssl-requests-only","Source":{"Owner":"AWS","SourceIdentifier":"S3_BUCKET_SSL_REQUESTS_ONLY"}}' --profile sandbox
awsc inspector2 enable --resource-types ECR EC2 LAMBDA --profile sandbox
# test GuardDuty : awsc guardduty create-sample-findings ; Security Hub → findings CIS triés par sévérité ; Prowler pour un rapport hors AWS (TP 42)"""),
  ("KMS, secrets, WAF", "", """resource "aws_kms_key" "data" { description = "crisis data"; enable_key_rotation = true; policy = data.aws_iam_policy_document.kms.json }   # politique : admin par rôle, usage par rôle de tâche, jamais *
resource "aws_secretsmanager_secret_rotation" "db" { secret_id = aws_secretsmanager_secret.db.id; rotation_lambda_arn = module.rotation.arn; rotation_rules { automatically_after_days = 30 } }
resource "aws_wafv2_web_acl" "main" { scope = "REGIONAL"; default_action { allow {} }
  rule { name = "common"; priority = 1; override_action { none {} } statement { managed_rule_group_statement { name = "AWSManagedRulesCommonRuleSet"; vendor_name = "AWS" } } visibility_config { … } }
  rule { name = "rate"; priority = 2; action { block {} } statement { rate_based_statement { limit = 2000; aggregate_key_type = "IP" } } visibility_config { … } } }""")],
 [("Pourquoi une alarme sur un pourcentage et pas sur un compte de 5xx ?", "Un compte dépend du trafic : 50 erreurs sur 100 requêtes est grave, sur 100 000 non. Le ratio est le SLI ; c'est la logique des SLO du niveau 6 en CloudWatch."),
  ("Une clé KMS avec <code>Principal: *</code> dans sa politique : risque ?", "Quiconque a une politique IAM autorisant <code>kms:Decrypt</code> peut déchiffrer ; la politique de clé doit nommer les rôles autorisés. Access Analyzer le signale.")],
 ("Observabilité et sécurité de CrisisShield sur AWS", ["Alarmes SLI (5xx, latence p95 par <code>TargetResponseTime</code>), logs chiffrés avec rétention, Logs Insights sauvegardées, ADOT vers X-Ray et vers Prometheus.", "GuardDuty, Security Hub, Config, Inspector activés par Terraform dans le compte security ; sample findings ; rapport Prowler avant/après.", "Clé KMS par domaine de données, rotation Secrets Manager testée, WAF avec règles gérées et limite de débit prouvée par k6."],
  "Preuves : alarme déclenchée par un k6 qui provoque 2 % de 5xx, notification SNS reçue ; trace X-Ray ALB → ECS → Aurora ; Security Hub score CIS ; <code>secretsmanager rotate-secret</code> puis connexion de l'API sans redémarrage ; k6 à 3 000 req/min depuis une IP → 403 WAF au-delà de 2 000.")),

ch("Infrastructure as Code et landing zone : Terraform, Organizations, Control Tower, CI/CD", 's',
 ["Tout passe par Terraform (modules versionnés, state distant verrouillé, plan en MR, apply manuel) ; CloudFormation/CDK sont à connaître pour lire l'existant.", "La landing zone (Organizations, comptes par fonction, SCP, réseau hub, journalisation centrale, vending de comptes) précède la première charge ; Control Tower l'automatise, Terraform la reproduit (voir TP 49 en LocalStack).", "Le pipeline infra a ses propres garde-fous : fmt, validate, tflint, trivy config, infracost, OPA sur le plan, drift détecté chaque nuit."],
 ["Structurer un dépôt Terraform multi-comptes et multi-environnements", "Déployer une landing zone (Control Tower ou Terraform) avec vending de comptes", "Outiller le pipeline infra et détecter la dérive"],
 [("Structure et backend", "", """infra/
  modules/{network,ecs-service,aurora,s3-secure}/       # versionnés par tag Git ou registry privé
  envs/{dev,staging,prod}/{network,data,app}/            # un state par compte × environnement × domaine
  global/{organization,identity,dns}/
terraform { backend "s3" { bucket = "crisis-tfstate-security"; key = "prod/app.tfstate"; region = "eu-west-3"; dynamodb_table = "tflock"; kms_key_id = "…"; encrypt = true } }
provider "aws" { region = "eu-west-3"; assume_role { role_arn = "arn:aws:iam::${var.account}:role/TerraformDeploy" } default_tags { tags = { Env = var.env, Owner = "platform", CostCenter = "crisis" } } }"""),
  ("Landing zone", "Control Tower : comptes Log Archive et Audit, guardrails (SCP + Config), Account Factory ; Terraform AFT ou le module « account vending » du TP 49 pour créer un compte conforme en une MR (OU, rôle, CloudTrail, Config, budget, VPC depuis IPAM). Identity Center pour les humains, permission sets par rôle métier, revue trimestrielle exportée.", None),
  ("Pipeline infra", "", """stages: [validate, plan, apply, drift]
validate: { script: [terraform fmt -check -recursive, terraform validate, tflint --recursive, trivy config --exit-code 1 --severity HIGH,CRITICAL ., conftest test --policy policy/ plan.json] }
plan: { script: [terraform plan -out=tfplan -lock-timeout=5m, terraform show -json tfplan > plan.json, infracost diff --path plan.json --format table], artifacts: { paths: [tfplan, plan.json] } }
apply: { stage: apply, when: manual, rules: [{ if: $CI_COMMIT_BRANCH == "main" }], resource_group: prod, environment: prod, script: [terraform apply tfplan] }
drift: { rules: [{ if: $CI_PIPELINE_SOURCE == "schedule" }], script: [terraform plan -detailed-exitcode -lock=false || (echo "DÉRIVE" && exit 1)] }
# identité : id_tokens + assume-role-with-web-identity (chapitre 2) ; aucune clé""")],
 [("Pourquoi un state par domaine et par compte ?", "Rayon d'impact (une erreur réseau ne touche pas la base), droits distincts (le rôle app ne peut pas modifier le réseau), plan rapide, verrous indépendants. Les workspaces partagent tout cela."),
  ("Control Tower ou Terraform pur ?", "Control Tower pour démarrer vite avec les bonnes pratiques AWS et un support ; Terraform pur (ou AFT) quand on veut tout en code et multi-cloud. Les deux se combinent : Control Tower pour le socle, Terraform pour le reste.")],
 ("Landing zone et pipeline infra de CrisisShield", ["Organisation (LocalStack pour Organizations, AWS pour le reste en sandbox) avec comptes security/shared/workloads, SCP, CloudTrail organisation, module de vending testé (<code>terraform test</code>).", "Dépôt structuré, backend chiffré et verrouillé, modules versionnés, pipeline avec plan en MR, apply manuel, OPA (8 règles du TP 51), infracost.", "Job de dérive nocturne : créer un tag à la main, vérifier que le job échoue et ouvre un ticket."],
  "Preuves : MR avec le plan et le coût commentés ; apply refusé hors main ; job drift rouge avec le diff du tag ; nouveau compte créé par MR avec CloudTrail et budget dès la création.")),

ch("Azure et GCP : équivalences, spécificités, multi-cloud et souveraineté", 's',
 ["Les concepts sont identiques (identité, réseau, calcul managé, base managée, secrets, journaux) ; les noms, les défauts et surtout l'identité diffèrent : Entra ID et identités managées chez Azure, projets et comptes de service chez GCP.", "Azure : groupes de ressources et abonnements, réseau moins isolant par défaut, AKS, Container Apps, intégration Microsoft 365. GCP : projets, VPC global, GKE de référence, Cloud Run, facturation à la seconde, BigQuery.", "Multi-cloud subi, choisi ou portable ; SecNumCloud, Bleu, S3NS pour la souveraineté ; la vraie dépendance est dans l'identité, les données et les compétences."],
 ["Traduire une architecture AWS en Azure et en GCP, en Terraform", "Expliquer ce qui est structurellement différent chez chacun", "Argumenter une stratégie cloud (mono, portable, multi) et la souveraineté"],
 [("Le même service, trois fois", "", """# Azure
resource "azurerm_container_app" "api" { name = "api"; container_app_environment_id = azurerm_container_app_environment.env.id; resource_group_name = azurerm_resource_group.rg.name; revision_mode = "Single"
  identity { type = "SystemAssigned" }; template { container { name = "api"; image = "crisisacr.azurecr.io/api@sha256:…"; cpu = 0.5; memory = "1Gi" } min_replicas = 2; max_replicas = 10 } ingress { external_enabled = true; target_port = 8080 } }
resource "azurerm_postgresql_flexible_server" "db" { name = "crisis-db"; zone = "1"; high_availability { mode = "ZoneRedundant" }; sku_name = "GP_Standard_D2ds_v5"; version = "16" }
# GCP
resource "google_cloud_run_v2_service" "api" { name = "api"; location = "europe-west9"; template { service_account = google_service_account.api.email; containers { image = "europe-west9-docker.pkg.dev/crisis/api@sha256:…"; resources { limits = { cpu = "1", memory = "1Gi" } } } scaling { min_instance_count = 1; max_instance_count = 10 } } }
resource "google_sql_database_instance" "db" { name = "crisis-db"; database_version = "POSTGRES_16"; region = "europe-west9"; settings { tier = "db-custom-2-7680"; availability_type = "REGIONAL"; backup_configuration { enabled = true; point_in_time_recovery_enabled = true } } }"""),
  ("Tableau d'équivalences", "", """| Concept            | AWS                    | Azure                        | GCP                      |
| Compte             | Account / Organizations| Subscription / Mgmt groups   | Project / Folders / Org  |
| Identité humaine   | Identity Center        | Entra ID                     | Cloud Identity           |
| Identité de charge | Rôle IAM               | Identité managée             | Compte de service        |
| Réseau             | VPC (régional)         | VNet (régional)              | VPC (global)             |
| Conteneurs sans nœud | ECS Fargate, App Runner| Container Apps               | Cloud Run                |
| Kubernetes         | EKS                    | AKS                          | GKE (Autopilot)          |
| Fonctions          | Lambda                 | Functions                    | Cloud Functions / Run    |
| Base relationnelle | RDS / Aurora           | Flexible Server / SQL DB     | Cloud SQL / AlloyDB      |
| Objets             | S3                     | Blob Storage                 | Cloud Storage            |
| Secrets            | Secrets Manager        | Key Vault                    | Secret Manager           |
| Journal d'API      | CloudTrail             | Activity Log                 | Cloud Audit Logs         |
| Garde-fous         | SCP                    | Azure Policy                 | Organization Policy      |"""),
  ("Souveraineté et stratégie", "Cloud de confiance : hébergement qualifié SecNumCloud (OVHcloud, Outscale, Cloud Temple), Bleu (Microsoft via Orange/Capgemini) et S3NS (Google via Thales) en qualification. Stratégie : un cloud principal, une architecture portable (conteneurs, PostgreSQL, Terraform, OpenTelemetry, secrets par variable, identité par rôle), pas de multi-cloud actif sans exigence explicite ; plan de réversibilité écrit (TP 24).", None)],
 [("Qu'est-ce qui est vraiment différent chez GCP ?", "Le VPC est global (sous-réseaux régionaux dans un même réseau), les projets sont l'unité de tout (IAM, facturation, quotas), IAM est hiérarchique par ressource, et GKE Autopilot gère les nœuds. Ça change la conception réseau et l'organisation."),
  ("Le client exige « multi-cloud pour ne pas dépendre ». Que réponds-tu ?", "La dépendance qui coûte est celle des données, de l'identité et des compétences, pas celle d'un fournisseur de calcul. Un cloud principal, une architecture portable et une réversibilité testée coûtent dix fois moins qu'un multi-cloud actif, et répondent au risque réel.")],
 ("CrisisShield en trois clouds, sans compte", ["Trois répertoires Terraform (aws, azure, gcp) qui passent <code>validate</code> ; tableau d'équivalences complété avec 15 services.", "Estimation de coût par les trois calculateurs pour le même profil ; écart et conclusion.", "Note d'une page : stratégie cloud recommandée pour un client public français (souveraineté, réversibilité, coût)."],
  "Attendu : les trois <code>validate</code> verts en conteneur ; AWS ≈ 160 $, Azure ≈ 175 $, GCP ≈ 150 $ (ordres de grandeur) ; la note conclut à un cloud principal qualifié ou une région UE avec clauses, briques portables, plan de réversibilité, pas de multi-cloud actif.")),

ch("Expert : FinOps, Well-Architected, migration, certifications", 'e',
 ["FinOps : informer (tags, allocation, coût par unité), optimiser (éteindre, redimensionner, architecture, engagements — dans cet ordre), opérer (rapport mensuel, anomalies, décisions).", "Le Well-Architected Framework (six piliers) est la grille de revue d'une architecture ; savoir la dérouler sur CrisisShield est une réponse d'entretien complète.", "Migration : découverte, 7 R, fondations, vagues, données (DMS), décommissionnement (TP 50) ; certifications : Solutions Architect Associate puis Professional, ou Security Specialty, préparées par ce cours."],
 ["Mettre en place une pratique FinOps mesurée", "Réaliser une revue Well-Architected et en tirer un plan", "Conduire une migration vers le cloud et préparer une certification"],
 [("FinOps en pratique", "", """provider "aws" { default_tags { tags = { Owner = "…", Env = var.env, Service = "crisisshield", CostCenter = "lab" } } }   # tout est attribuable
# ordre des leviers (TP 23) : 1) éteindre dev la nuit (EventBridge Scheduler → ecs update-service --desired-count 0, rds stop-db-instance) 2) redimensionner (Compute Optimizer, Performance Insights) 3) architecture (endpoints, Graviton, Intelligent-Tiering, rétention des logs) 4) Savings Plans sur le socle stable après un mois
awsc ce get-cost-and-usage --group-by Type=TAG,Key=Env … ; awsc ce create-anomaly-monitor … ; budgets par environnement avec action (dev) ou alerte (prod)
# métrique : coût / 1 000 requêtes (ou par incident traité) — seule mesure qui distingue croissance et gaspillage"""),
  ("Well-Architected sur CrisisShield", "", """| Pilier                 | Question type                                  | CrisisShield (preuve)                                   | Écart |
| Excellence opérationnelle | Tout est en code, déployé par pipeline, observé ? | Terraform, GitOps, SLO (niveaux 3, 5, 6)                | runbooks partiels |
| Sécurité               | Identité, détection, protection des données, réponse | Niveau 7 + chapitres 2 et 7                             | revue d'accès trimestrielle |
| Fiabilité              | Multi-AZ, sauvegardes testées, PRA, limites connues | Aurora multi-AZ, restore-test, TP 44                    | quotas non demandés |
| Performance            | Bon service pour la charge, mesuré             | TP 45, autoscaling sur requêtes                          | cache CloudFront à régler |
| Coût                   | Attribué, optimisé, revu                       | Tags, extinction dev, Graviton                           | Savings Plan à décider |
| Durabilité             | Région bas carbone, extinction, densité         | eu-west-3, Spot, ARM                                     | rapport carbone |
# outil : Well-Architected Tool (console) avec les questions par pilier ; revue annuelle avec plan d'actions priorisé"""),
  ("Migration et certifications", "Migration (voir TP 50 en local) : Migration Evaluator/Application Discovery, 7 R, landing zone, DMS avec CDC pour les bases, MGN pour les VM, vagues par criticité, retour arrière daté, décommissionnement prouvé, coût avant/après. Certifications : SAA-C03 couvre les chapitres 1 à 7 ; SAP-C02 ajoute organisation, migration, multi-comptes, hybride (chapitres 8 à 10) ; Security Specialty s'appuie sur le niveau 7 du parcours. Méthode : un examen blanc par semaine, chaque erreur reliée à un chapitre.", None)],
 [("Une facture qui monte de 30 % : bonne ou mauvaise nouvelle ?", "Ça dépend du coût par unité : si le trafic a monté de 50 % et le coût de 30 %, le coût unitaire a baissé (sain) ; si le trafic est stable, c'est du gaspillage ou une anomalie. Sans coût par unité, on ne peut pas répondre."),
  ("Pourquoi s'engager (Savings Plan) seulement après avoir optimisé ?", "Un engagement fige la dépense pendant un à trois ans ; s'engager sur des instances surdimensionnées ou allumées la nuit, c'est payer le gaspillage à prix réduit au lieu de le supprimer.")],
 ("Revue finale de CrisisShield sur AWS", ["Rapport FinOps du mois : coût par tag, leviers appliqués avec gain, coût par 1 000 requêtes, prévision, trois décisions ; détecteur d'anomalies et budgets.", "Revue Well-Architected complète (six piliers, preuves, écarts, plan à 90 jours) dans docs/cloud/well-architected.md.", "Plan de migration d'un legacy vers cette architecture (réutiliser le TP 50) et un examen blanc SAA corrigé avec les chapitres à revoir."],
  "Attendu : le rapport tient sur une page avec des chiffres issus de Cost Explorer ; la revue WAF a au moins un écart par pilier avec une action datée ; l'examen blanc est corrigé question par question avec le renvoi au chapitre ; tout le sandbox est détruit et la facture du mois est sous le budget.")),
]

if __name__ == '__main__':
    page('cours-react.html', 'React — de zéro à expert', "Onze chapitres pour maîtriser React 19 avec TypeScript : composants, état, effets, données serveur, état global (stores, atomes, signals), formulaires, tests, production, puis l'échelle (monorepo, rendu concurrent, micro-frontends, observabilité). Projet fil conducteur : le front de CrisisShield. Tout tourne en Docker, chaque chapitre a ses exercices corrigés et un travail pratique avec correction type.", "≈ 45 h de travail · prérequis : Docker Desktop, notions de HTML/CSS · voir aussi les cours <a href=\"cours-angular.html\" style=\"color:#fff\">Angular</a> et <a href=\"cours-vue.html\" style=\"color:#fff\">Vue</a> pour comparer les trois modèles de réactivité.", REACT, ('cours-angular.html', 'Cours Angular'))
    page('cours-angular.html', 'Angular — de zéro à expert', "Onze chapitres pour maîtriser Angular 19/20 : composants standalone, signals (signal, computed, effect, linkedSignal, resource), injection de dépendances, routage, formulaires typés, NgRx SignalStore, tests, SSR, production, puis l'échelle (Nx, micro-frontends, CDK, Web Components, migrations). Projet fil conducteur : le front de CrisisShield. Tout tourne en Docker, chaque chapitre a ses exercices corrigés et un travail pratique avec correction type.", "≈ 45 h de travail · prérequis : Docker Desktop, notions de HTML/CSS · voir aussi les cours <a href=\"cours-react.html\" style=\"color:#fff\">React</a> et <a href=\"cours-vue.html\" style=\"color:#fff\">Vue</a>.", ANG, ('cours-vue.html', 'Cours Vue'))
    page('cours-vue.html', 'Vue.js — de zéro à expert', "Dix chapitres pour maîtriser Vue 3 avec TypeScript : composants monofichiers, réactivité (ref, reactive, computed, watch — les signals de Vue), Composition API et composables, Vue Router, Pinia, formulaires (VeeValidate + Zod), tests, Nuxt et production. Projet fil conducteur : le front de CrisisShield. Tout tourne en Docker, chaque chapitre a ses exercices corrigés et un travail pratique avec correction type.", "≈ 40 h de travail · prérequis : Docker Desktop, notions de HTML/CSS · voir aussi les cours <a href=\"cours-react.html\" style=\"color:#fff\">React</a> et <a href=\"cours-angular.html\" style=\"color:#fff\">Angular</a> : même projet, trois modèles de réactivité.", VUE, ('cours-react.html', 'Cours React'))
    page('cours-cloud.html', 'Cloud — de zéro à expert', "Dix chapitres pour maîtriser le cloud avec AWS comme référence et les équivalents Azure et GCP : compte et identité, réseau, calcul (ECS, EKS, Lambda), données, serverless et événementiel, observabilité et sécurité, IaC et landing zone, multi-cloud et souveraineté, FinOps, Well-Architected, migration et certifications. Tout en Terraform depuis un conteneur, sur un compte sandbox détruit après chaque TP (ou LocalStack). Ce cours approfondit le niveau 4 du parcours DevOps et renvoie aux TP existants.", "≈ 50 h de travail · prérequis : niveaux 0 à 3 du parcours DevOps (Docker, Git, Terraform) · coût : quelques euros de sandbox AWS, tout est détruit en fin de TP · voir le <a href=\"devops-niveau-4-cloud.html\" style=\"color:#fff\">niveau 4</a> pour l'introduction.", CLOUD, ('devops-niveau-4-cloud.html', 'Niveau 4 — Cloud'))
