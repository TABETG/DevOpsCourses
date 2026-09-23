"""Pages frontend et cloud. Usage : python3 front_pages.py <dossier cours-devops>"""
import sys, runpy
g = runpy.run_path(__import__('pathlib').Path(__file__).with_name('front_gen.py'), run_name='front')
ch, page, REACT, ANG, DOCK = g['ch'], g['page'], g['REACT'], g['ANG'], g['DOCK']

# ================================================================ React : chapitre 11
REACT.append(ch("Patrons avancés : composition, rendu concurrent, portails, i18n", 'e',
 ["Les compound components et les render props/children-as-function donnent des API de composant flexibles sans explosion de props.", "Le rendu concurrent (<code>useTransition</code>, <code>useDeferredValue</code>) garde l'interface réactive pendant un calcul ou un rendu lourd ; <code>startTransition</code> marque une mise à jour comme non urgente.", "Portails, virtualisation, i18n et thème sont les briques d'une application d'entreprise ; chacune a une bibliothèque de référence."],
 ["Concevoir une API de composant composable (compound, headless)", "Utiliser les transitions et les valeurs différées pour la fluidité", "Mettre en place portails, listes virtualisées, i18n et thème"],
 [("Compound components", "Un parent tient l'état dans un contexte privé ; les enfants nommés le consomment. L'appelant compose librement : <code>&lt;Tabs&gt;&lt;Tabs.List&gt;…&lt;/Tabs.List&gt;&lt;Tabs.Panel id=\"a\"&gt;…&lt;/Tabs.Panel&gt;&lt;/Tabs&gt;</code>. Les bibliothèques « headless » (Radix, React Aria, Headless UI) livrent l'accessibilité et le comportement, jamais le style.",
"""const TabsCtx = createContext<{ active: string; setActive: (id: string) => void } | null>(null);
export function Tabs({ defaultTab, children }: { defaultTab: string; children: React.ReactNode }) { const [active, setActive] = useState(defaultTab); return <TabsCtx.Provider value={{ active, setActive }}>{children}</TabsCtx.Provider>; }
Tabs.Tab = function Tab({ id, children }: { id: string; children: React.ReactNode }) { const c = useContext(TabsCtx)!; return <button role="tab" aria-selected={c.active === id} onClick={() => c.setActive(id)}>{children}</button>; };
Tabs.Panel = function Panel({ id, children }: { id: string; children: React.ReactNode }) { const c = useContext(TabsCtx)!; return c.active === id ? <div role="tabpanel">{children}</div> : null; };"""),
  ("Rendu concurrent", "", """const [query, setQuery] = useState('');
const deferred = useDeferredValue(query);                 // la liste lourde suit avec retard, l'input reste fluide
const [isPending, startTransition] = useTransition();
const onZone = (z: string) => startTransition(() => setZone(z));   // changement de page non urgent : l'ancienne reste affichée, isPending pour un indicateur
const rows = useMemo(() => filterHeavy(incidents, deferred), [incidents, deferred]);"""),
  ("Portails, virtualisation, i18n, thème", "", """createPortal(<Modal onClose={close}>…</Modal>, document.body)     // sort du flux DOM, garde le contexte React (focus trap avec react-aria)
const v = useVirtualizer({ count: rows.length, getScrollElement: () => ref.current, estimateSize: () => 48 });   // @tanstack/react-virtual : 50 000 lignes, 30 DOM nodes
// i18n : react-i18next, fichiers JSON par locale, useTranslation() ; ICU pour le pluriel : t('incidents', { count }) ; dates par Intl.DateTimeFormat
// thème : variables CSS sur :root[data-theme], prefers-color-scheme, stockage du choix ; jamais de thème en props partout""")],
 [("Pourquoi une transition plutôt qu'un simple <code>setState</code> pour changer de page de résultats ?", "React garde l'ancienne interface affichée et interactive jusqu'à ce que la nouvelle soit prête, au lieu d'afficher un état vide ou un spinner ; <code>isPending</code> permet un indicateur discret."),
  ("Une modale dans un composant profondément imbriqué apparaît coupée par un <code>overflow: hidden</code>. Solution ?", "Un portail vers <code>document.body</code> : le DOM sort du conteneur, le contexte et les événements React restent ceux du parent.")],
 ("Tableau d'incidents d'entreprise", ["Compound <code>Tabs</code> accessible (clavier, aria) ; modale de détail par portail avec focus trap.", "Recherche avec <code>useDeferredValue</code> sur 20 000 incidents virtualisés ; profil avant/après.", "i18n fr/en avec pluriels ICU et dates Intl ; thème clair/sombre persistant ; axe sans violation."],
  "Profiler : sans <code>useDeferredValue</code>, chaque frappe bloque ~120 ms ; avec, l'input répond en < 16 ms et la liste suit. Virtualisation : 20 000 lignes, ~40 nœuds DOM. Test i18n : <code>t('incidents', { count: 2 })</code> → « 2 incidents » et « 2 incidents » en anglais avec la forme <code>_other</code>.")))

# ================================================================ Angular : chapitre 11
ANG.append(ch("Patrons avancés : directives, host directives, CDK, Material, micro-frontends, Nx", 'e',
 ["Une directive ajoute un comportement à un élément existant ; les host directives composent des directives sur un composant sans héritage.", "Le CDK (overlay, drag-drop, virtual scroll, a11y) et Angular Material (composants Material 3, thèmes) sont la base d'interface d'entreprise ; on les étend, on ne les réécrit pas.", "À l'échelle : monorepo Nx (bibliothèques, graphe de dépendances, cache) et micro-frontends par Module Federation (Native Federation) quand plusieurs équipes livrent indépendamment."],
 ["Écrire des directives d'attribut et structurelles, et composer par host directives", "Utiliser le CDK (overlay, virtual scroll, a11y) et thémer Material", "Organiser un monorepo Nx et décider d'un micro-frontend"],
 [("Directives et host directives", "", """@Directive({ selector: '[csHighlightPriority]', host: { '[class.p1]': 'priority() === "P1"', '[attr.title]': 'label()' } })
export class HighlightPriority { priority = input.required<Priority>({ alias: 'csHighlightPriority' }); label = computed(() => `Priorité ${this.priority()}`); }
@Directive({ selector: '[csTrackClicks]' }) export class TrackClicks { private t = inject(Telemetry); @HostListener('click') onClick() { this.t.event('click'); } }
@Component({ selector: 'cs-action-button', hostDirectives: [TrackClicks, { directive: HighlightPriority, inputs: ['csHighlightPriority: priority'] }], … })   // composition sans héritage"""),
  ("CDK et Material", "", """// virtual scroll : <cdk-virtual-scroll-viewport itemSize="48"> <article *cdkVirtualFor="let i of incidents(); trackBy: byId"> … </cdk-virtual-scroll-viewport>
// overlay : const ref = this.overlay.create({ positionStrategy: this.overlay.position().flexibleConnectedTo(origin).withPositions([…]), hasBackdrop: true }); ref.attach(new ComponentPortal(IncidentPreview, null, injector));
// a11y : FocusTrap (cdkTrapFocus), LiveAnnouncer.announce('Incident créé'), FocusMonitor
// Material 3 : @use '@angular/material' as mat; html { @include mat.theme((color: (primary: mat.$azure-palette, tertiary: mat.$blue-palette), typography: Roboto, density: 0)); }"""),
  ("Nx et micro-frontends", "Nx : un dépôt, des applications et des bibliothèques (<code>libs/incidents/feature</code>, <code>libs/incidents/data-access</code>, <code>libs/shared/ui</code>) avec des règles de dépendance (<code>@nx/enforce-module-boundaries</code>), un graphe, un cache de build et de test, <code>nx affected</code> en CI. Micro-frontends : Native Federation (ou Module Federation) expose un remote (<code>exposes: { './routes': 'incidents.routes.ts' }</code>) chargé par le shell via <code>loadRemoteModule</code> ; à réserver aux organisations où plusieurs équipes déploient à des rythmes différents, car le coût (versions partagées, styles, authentification, tests d'intégration) est élevé.", None)],
 [("Quand une directive plutôt qu'un composant ?", "Quand on ajoute un comportement à un élément existant (surbrillance, suivi, autofocus, permission) sans posséder son template. Un composant possède sa vue."),
  ("Trois équipes, une application Angular, déploiements bloqués les uns par les autres : micro-frontends ou monorepo Nx ?", "D'abord Nx : frontières de bibliothèques, <code>affected</code>, un seul déploiement rapide. Les micro-frontends ne se justifient que si les équipes doivent déployer en production indépendamment, avec le coût d'intégration assumé.")],
 ("Kit d'interface CrisisShield", ["Directive de priorité et host directive de télémétrie sur un bouton d'action ; tests de directive.", "Liste virtualisée CDK de 20 000 incidents ; aperçu en overlay avec focus trap et annonce a11y ; thème Material 3 clair/sombre.", "Migration du projet en workspace Nx avec trois bibliothèques et règles de frontières ; <code>nx affected -t test</code> en CI."],
  "Test de directive : composant hôte avec <code>[csHighlightPriority]=\"'P1'\"</code>, vérifier la classe <code>p1</code> et le <code>title</code>. Nx : <code>npx create-nx-workspace</code> en conteneur, <code>nx graph</code> exporté en image dans <code>docs/</code>, une règle de frontière volontairement violée (feature importe data-access d'un autre domaine) qui fait échouer le lint.")))

# ================================================================ VUE
VUE = [
ch("Démarrer : Vite, SFC, réactivité et templates", 'j',
 ["Vue 3 avec la Composition API : un composant est un fichier <code>.vue</code> (template, script setup, style) ; l'état est réactif par <code>ref</code> et <code>reactive</code>.", "Le template est du HTML augmenté : <code>{{ }}</code>, <code>v-bind</code> (<code>:</code>), <code>v-on</code> (<code>@</code>), <code>v-if</code>, <code>v-for</code> avec <code>:key</code>, <code>v-model</code>.", "La réactivité est fine par défaut : seul ce qui lit une valeur modifiée est recalculé, c'est le modèle des signals."],
 ["Créer un projet Vue 3 + TypeScript en Docker", "Écrire des SFC avec <code>&lt;script setup&gt;</code>, ref/reactive/computed", "Maîtriser les directives de template et les clés"],
 [("Projet et premier composant", DOCK, """docker run --rm -it -v "$PWD:/app" -w /app -p 5173:5173 node:22 sh -c "npm create vue@latest crisisshield-web -- --ts --router --pinia --vitest --eslint && cd crisisshield-web && npm i && npm run dev -- --host"
<!-- src/components/IncidentCard.vue -->
<script setup lang="ts">
import type { Incident } from '@/domain/incident';
const props = defineProps<{ incident: Incident }>();
const emit = defineEmits<{ close: [id: number] }>();
</script>
<template>
  <article class="card">
    <h3>{{ incident.title }}</h3>
    <PriorityBadge :priority="incident.priority" />
    <p v-if="incident.zone">Zone {{ incident.zone }}</p>
    <button :disabled="incident.status === 'closed'" @click="emit('close', incident.id)">Clôturer</button>
  </article>
</template>
<style scoped>.card { border: 1px solid var(--line); border-radius: 8px; padding: 1rem }</style>"""),
  ("ref, reactive, computed", "<code>ref</code> enveloppe une valeur (<code>.value</code> dans le script, déballé dans le template) ; <code>reactive</code> rend un objet profondément réactif ; <code>computed</code> dérive avec cache. Règle : <code>ref</code> partout, <code>reactive</code> pour les objets de formulaire ; ne jamais détruire la réactivité en destructurant un <code>reactive</code> (<code>toRefs</code>).",
"""const incidents = ref<Incident[]>([]);
const zone = ref('');
const filtered = computed(() => incidents.value.filter(i => !zone.value || i.zone === zone.value));
const openCount = computed(() => filtered.value.filter(i => i.status === 'open').length);
function close(id: number) { incidents.value = incidents.value.map(i => i.id === id ? { ...i, status: 'closed' } : i); }   // ou mutation directe : Vue la suit aussi"""),
  ("Listes et clés", "", """<ul><li v-for="i in filtered" :key="i.id"><IncidentCard :incident="i" @close="close" /></li></ul>
<p v-if="filtered.length === 0">Aucun incident.</p>
<select v-model="zone"><option value="">Toutes</option><option v-for="z in zones" :key="z">{{ z }}</option></select>""")],
 [("Pourquoi <code>const { zone } = reactive({ zone: '' })</code> ne réagit-il plus ?", "La destructuration copie la valeur primitive hors du proxy réactif. Utiliser <code>toRefs</code> ou des <code>ref</code> séparés."),
  ("<code>v-if</code> contre <code>v-show</code> ?", "<code>v-if</code> crée/détruit l'élément (coût au basculement, rien en mémoire si faux) ; <code>v-show</code> bascule <code>display</code> (coût initial, basculement gratuit). <code>v-show</code> pour ce qui change souvent.")],
 ("Liste d'incidents", ["Projet Vue 3 TS en conteneur ; composants <code>IncidentList</code>, <code>IncidentCard</code>, <code>PriorityBadge</code>.", "Filtre par zone avec <code>v-model</code> et computed ; clôture d'incident.", "Test Vitest + Vue Test Utils : rendu, clic, émission."],
  "<code>const w = mount(IncidentCard, { props: { incident } }); await w.find('button').trigger('click'); expect(w.emitted('close')![0]).toEqual([incident.id])</code>. Vérifier dans Vue DevTools que seul <code>filtered</code> se recalcule au changement de zone.")),

ch("Composants en profondeur : props, événements, v-model, slots, cycle de vie", 'j',
 ["<code>defineProps</code>/<code>defineEmits</code> typés, <code>defineModel</code> pour le two-way, <code>defineExpose</code> pour l'API publique.", "Les slots (par défaut, nommés, scoped) composent ; <code>provide/inject</code> partage dans un sous-arbre ; <code>&lt;Teleport&gt;</code> et <code>&lt;Transition&gt;</code> sont intégrés.", "Cycle de vie : <code>onMounted</code>, <code>onUnmounted</code>, <code>watch</code>/<code>watchEffect</code> ; la plupart des besoins se règlent par <code>computed</code>."],
 ["Concevoir des composants réutilisables avec v-model et slots scoped", "Partager par provide/inject de façon typée", "Choisir entre computed, watch et watchEffect"],
 [("defineModel et slots", "", """<!-- ZoneFilter.vue -->
<script setup lang="ts">
const model = defineModel<string>({ default: '' });
defineProps<{ zones: string[] }>();
</script>
<template><select v-model="model"><option value="">Toutes</option><option v-for="z in zones" :key="z">{{ z }}</option></select></template>
<!-- Panel.vue : slots nommés et scoped -->
<template><section><header><slot name="title" /></header><slot :count="items.length" /></section></template>
<!-- usage --> <Panel :items="incidents"><template #title><h2>Incidents</h2></template><template #default="{ count }">{{ count }} incidents</template></Panel>"""),
  ("provide / inject typé", "", """export const IncidentsKey: InjectionKey<{ incidents: Ref<Incident[]>; close: (id: number) => void }> = Symbol('incidents');
provide(IncidentsKey, { incidents, close });                       // parent
const store = inject(IncidentsKey)!;                                // descendant, à n'importe quelle profondeur"""),
  ("watch et watchEffect", "<code>computed</code> pour dériver ; <code>watch(source, cb)</code> pour réagir à un changement précis (requête, persistance) avec l'ancienne valeur ; <code>watchEffect</code> suit automatiquement ce qu'il lit. Nettoyage avec <code>onCleanup</code> (annulation de fetch).",
"""watch(zone, async (z, _old, onCleanup) => { const ctrl = new AbortController(); onCleanup(() => ctrl.abort()); incidents.value = await api.list(z, ctrl.signal); }, { immediate: true });
watchEffect(() => localStorage.setItem('zone', zone.value));
onMounted(() => input.value?.focus()); onUnmounted(() => clearInterval(timer));""")],
 [("Pourquoi un <code>InjectionKey</code> symbol plutôt qu'une chaîne ?", "Le symbole est unique (pas de collision) et porte le type : <code>inject(IncidentsKey)</code> est typé sans annotation."),
  ("<code>watch(() => props.id, load)</code> ne se déclenche pas au montage. Pourquoi ?", "<code>watch</code> est paresseux par défaut ; ajouter <code>{ immediate: true }</code> ou utiliser <code>watchEffect</code>.")],
 ("Filtre, panneau et détail", ["<code>ZoneFilter</code> avec <code>defineModel</code>, <code>Panel</code> avec slots nommés et scoped.", "Détail qui recharge sur changement d'id avec annulation.", "Test des slots et du v-model avec un composant hôte."],
  "Test v-model : <code>mount(ZoneFilter, { props: { modelValue: 'N1', 'onUpdate:modelValue': e => w.setProps({ modelValue: e }) } })</code>. Vérifier l'annulation : deux changements d'id rapides, un seul résultat appliqué (mock de fetch avec délai).")),

ch("Composables et réactivité avancée", 'c',
 ["Un composable est une fonction <code>useX()</code> qui encapsule état réactif et effets ; VueUse en fournit deux cents (débounce, fetch, storage, media).", "<code>shallowRef</code>, <code>markRaw</code>, <code>toRef</code>, <code>readonly</code>, <code>customRef</code> règlent la granularité et les performances.", "<code>effectScope</code> regroupe des effets pour les détruire ensemble (base de Pinia)."],
 ["Écrire et tester des composables", "Contrôler la profondeur de réactivité pour les gros objets", "Utiliser VueUse à bon escient"],
 [("Composable", "", """export function useIncidents(zone: Ref<string>) {
  const data = ref<Incident[]>([]); const status = ref<'idle' | 'loading' | 'error'>('idle'); const error = ref<string | null>(null);
  watch(zone, async (z, _o, onCleanup) => {
    const ctrl = new AbortController(); onCleanup(() => ctrl.abort()); status.value = 'loading';
    try { data.value = await api.list(z, ctrl.signal); status.value = 'idle'; } catch (e) { if ((e as Error).name !== 'AbortError') { status.value = 'error'; error.value = (e as Error).message; } }
  }, { immediate: true });
  const open = computed(() => data.value.filter(i => i.status === 'open'));
  return { data: readonly(data), open, status, error, reload: () => zone.value = zone.value };
}
// VueUse : const q = refDebounced(search, 300); const { data } = useFetch(url, { refetch: true }).json<Incident[]>(); useLocalStorage('zone', '');"""),
  ("Granularité", "", """const big = shallowRef<Incident[]>([]);   // suivi de la référence seulement : remplacer le tableau déclenche, muter un élément non → 10× plus rapide sur 50 000 objets
const chart = markRaw(new Chart(…));        // jamais proxyfié (instances de bibliothèques)
const title = toRef(props, 'title');        // ref liée à une prop
const bounced = customRef((track, trigger) => { let v = ''; let t: number; return { get() { track(); return v; }, set(n) { clearTimeout(t); t = setTimeout(() => { v = n; trigger(); }, 300); } }; });"""),
  ("Tester un composable", "", """it('charge à la création et recharge sur changement de zone', async () => {
  vi.spyOn(api, 'list').mockResolvedValue(fixtures);
  const zone = ref('N1'); const { data, status } = useIncidents(zone);
  await flushPromises(); expect(status.value).toBe('idle'); expect(data.value).toHaveLength(3);
  zone.value = 'N2'; await flushPromises(); expect(api.list).toHaveBeenLastCalledWith('N2', expect.any(AbortSignal));
});   // ou withSetup() pour les composables qui utilisent onMounted""")],
 [("Quand <code>shallowRef</code> ?", "Grande structure remplacée d'un bloc (résultat d'API, données de graphique) : on évite le proxy profond ; on remplace la référence pour déclencher."),
  ("Un composable qui appelle <code>onMounted</code> testé hors composant lève un avertissement. Solution ?", "L'exécuter dans un composant de test (<code>withSetup</code> : <code>createApp({ setup() { r = useX(); return () => {} } }).mount(div)</code>) ou éviter les hooks de cycle de vie dans le composable.")],
 ("Composables de CrisisShield", ["<code>useIncidents</code>, <code>useDebounced</code> (customRef), <code>useTheme</code> (VueUse useDark).", "Carte de 50 000 points en <code>shallowRef</code> + <code>markRaw</code> ; mesure avant/après.", "Tests des composables avec <code>flushPromises</code>."],
  "Mesure (Performance panel) : <code>ref</code> profond sur 50 000 objets : ~400 ms à l'affectation ; <code>shallowRef</code> : ~30 ms. Le <code>readonly(data)</code> renvoyé empêche un composant de muter l'état du composable.")),

ch("Vue Router : pages, chargement paresseux, guards, données", 'c',
 ["Routes déclaratives avec composants importés dynamiquement ; routes imbriquées et nommées ; <code>&lt;RouterView&gt;</code> et <code>&lt;RouterLink&gt;</code>.", "Guards globaux et par route (<code>beforeEnter</code>, <code>onBeforeRouteLeave</code>) ; <code>props: true</code> injecte les paramètres en props.", "Les données se chargent dans le composant (composable) ou par un guard ; TanStack Query Vue apporte cache et invalidation."],
 ["Structurer une application multi-pages avec chargement paresseux", "Protéger des routes et confirmer la sortie d'un formulaire", "Charger et mettre en cache avec TanStack Query Vue"],
 [("Routes", "", """const router = createRouter({ history: createWebHistory(), routes: [
  { path: '/', component: Home },
  { path: '/incidents', component: () => import('@/pages/IncidentsPage.vue'), meta: { auth: true }, children: [
    { path: ':id', name: 'incident', component: () => import('@/pages/IncidentDetail.vue'), props: r => ({ id: Number(r.params.id), tab: r.query.tab ?? 'details' }) } ] },
  { path: '/:pathMatch(.*)*', component: NotFound },
] });
router.beforeEach(to => { const auth = useAuthStore(); if (to.meta.auth && !auth.isLoggedIn) return { path: '/login', query: { redirect: to.fullPath } }; });
// composant : onBeforeRouteLeave(() => form.dirty ? confirm('Quitter sans enregistrer ?') : true);"""),
  ("TanStack Query Vue", "", """const zone = ref('');
const { data, isPending, error } = useQuery({ queryKey: ['incidents', zone], queryFn: ({ signal }) => api.list(zone.value, signal), staleTime: 30_000 });   // la clé réactive relance la requête
const qc = useQueryClient();
const create = useMutation({ mutationFn: api.create, onSuccess: () => qc.invalidateQueries({ queryKey: ['incidents'] }) });""")],
 [("Pourquoi <code>props: true</code> (ou une fonction) plutôt que <code>useRoute()</code> dans le composant ?", "Le composant reste indépendant du routeur : testable avec de simples props, réutilisable hors route."),
  ("Un guard asynchrone qui charge des données avant d'afficher : bon ou mauvais ?", "Acceptable pour une donnée indispensable et rapide (permissions) ; sinon naviguer tout de suite et afficher un état de chargement dans la page.")],
 ("Pages liste et détail", ["Routes lazy avec <code>meta.auth</code> et redirection ; détail en props.", "TanStack Query Vue avec clé réactive et invalidation à la création ; préchargement au survol.", "Test de guard et test de navigation avec un routeur mémoire (<code>createMemoryHistory</code>)."],
  "Test : <code>router.push('/incidents'); await router.isReady(); expect(router.currentRoute.value.path).toBe('/login')</code> sans authentification. Vérifier le chunk séparé de la page dans l'onglet Réseau.")),

ch("État global : Pinia, stores setup, persistance, et Vue Vapor", 's',
 ["Pinia est le store officiel : un store est un composable global (<code>defineStore</code> en syntaxe setup : refs, computed, fonctions), typé, avec DevTools et plugins.", "Trois familles d'état : local (ref), serveur (TanStack Query ou un store de données), global client (Pinia) ; l'état serveur n'a pas vocation à vivre dans Pinia.", "Vue Vapor (compilation sans DOM virtuel) et les signals alpha de Vue 3.5+ (<code>shallowRef</code>, <code>useTemplateRef</code>, <code>onWatcherCleanup</code>, hydratation paresseuse) sont la direction du framework."],
 ["Écrire des stores Pinia en syntaxe setup avec getters, actions et persistance", "Tester un store et l'utiliser dans les composants sans perdre la réactivité", "Situer Vue par rapport aux signals et à Vapor"],
 [("Store Pinia (setup)", "", """export const useIncidentsStore = defineStore('incidents', () => {
  const items = ref<Incident[]>([]); const zone = ref(''); const status = ref<'idle' | 'loading' | 'error'>('idle');
  const open = computed(() => items.value.filter(i => i.status === 'open' && (!zone.value || i.zone === zone.value)));
  async function load() { status.value = 'loading'; try { items.value = await api.list(zone.value); status.value = 'idle'; } catch { status.value = 'error'; } }
  function close(id: number) { const before = items.value; items.value = items.value.map(i => i.id === id ? { ...i, status: 'closed' } : i); api.close(id).catch(() => { items.value = before; }); }   // optimiste + rollback
  return { items, zone, status, open, load, close };
}, { persist: { pick: ['zone'] } });   // pinia-plugin-persistedstate
// composant : const store = useIncidentsStore(); const { open, zone } = storeToRefs(store);   // storeToRefs garde la réactivité ; les actions se destructurent directement"""),
  ("Tests", "", """beforeEach(() => setActivePinia(createPinia()));
it('clôture de façon optimiste puis revient en arrière', async () => {
  const s = useIncidentsStore(); s.items = fixtures; vi.spyOn(api, 'close').mockRejectedValue(new Error('500'));
  s.close(1); expect(s.open.find(i => i.id === 1)).toBeUndefined();
  await flushPromises(); expect(s.open.find(i => i.id === 1)).toBeDefined();
});
// composant : mount(Page, { global: { plugins: [createTestingPinia({ initialState: { incidents: { items: fixtures } } })] } })"""),
  ("Signals et Vapor", "La réactivité de Vue (<code>ref</code>/<code>computed</code>/<code>watch</code>) est déjà un système de signals : dépendances suivies, recalcul minimal. Vue 3.5 expose le cœur (<code>@vue/reactivity</code>) avec la même sémantique que les propositions TC39. Vue Vapor compile les templates en opérations DOM directes sans DOM virtuel (comme Solid) : moins de mémoire, démarrage plus rapide, opt-in par composant. En entretien : Vue = signals depuis 2014 (Vue 2 avec getters/setters, Vue 3 avec proxies) ; Angular les a adoptés en 2023, React reste sur le rendu par composant.", None)],
 [("Pourquoi <code>storeToRefs</code> ?", "Destructurer un store perd la réactivité des refs et computed (ce sont des propriétés du proxy) ; <code>storeToRefs</code> les extrait en refs liées. Les fonctions, elles, se destructurent sans problème."),
  ("Les incidents chargés de l'API doivent-ils être dans Pinia ?", "Si on utilise TanStack Query, non : le cache serveur est déjà un store avec invalidation. Pinia garde l'état client (filtres, sélection, utilisateur, brouillons). Sans TanStack Query, un store de données Pinia est acceptable.")],
 ("Store d'incidents et filtres persistants", ["Store Pinia setup avec optimiste/rollback, filtres persistés, DevTools.", "Composants qui consomment via <code>storeToRefs</code> ; tests avec <code>createTestingPinia</code>.", "Comparatif écrit Pinia / Zustand / SignalStore (ADR)."],
  "Attendu : le test de rollback vert, la zone restaurée après rechargement (<code>localStorage.incidents</code> ne contient que <code>zone</code>), et l'ADR qui note que les trois modèles sont des stores à signals avec des API différentes.")),

ch("Formulaires, validation et accessibilité", 's',
 ["<code>v-model</code> avec modificateurs (<code>.trim</code>, <code>.number</code>, <code>.lazy</code>) suffit aux formulaires simples ; VeeValidate + Zod (ou Valibot) pour les formulaires complexes.", "Le schéma partagé avec l'API garantit les mêmes règles des deux côtés ; les erreurs de l'API se mappent sur les champs.", "Accessibilité : labels, <code>aria-invalid</code>, messages en <code>role=alert</code>, testés avec axe."],
 ["Construire un formulaire complexe avec VeeValidate et Zod", "Mapper les erreurs de l'API et tester l'accessibilité", "Utiliser les modificateurs de v-model à bon escient"],
 [("VeeValidate + Zod", "", """<script setup lang="ts">
const schema = toTypedSchema(z.object({ title: z.string().trim().min(3, 'Au moins 3 caractères'), priority: z.enum(['P1','P2','P3']), zone: z.string().regex(/^[A-Z][0-9]$/, 'Format A1'), contacts: z.array(z.object({ email: z.string().email() })).max(5) }).superRefine((v, ctx) => { if (v.priority === 'P1' && !v.zone) ctx.addIssue({ path: ['zone'], code: 'custom', message: 'Zone obligatoire en P1' }); }));
const { handleSubmit, errors, isSubmitting, setErrors, defineField } = useForm({ validationSchema: schema, initialValues: { priority: 'P2', contacts: [] } });
const [title, titleAttrs] = defineField('title');
const { fields, push, remove } = useFieldArray<{ email: string }>('contacts');
const onSubmit = handleSubmit(async v => { try { await api.create(v); } catch (e) { if (isProblem(e)) setErrors(Object.fromEntries(e.errors.map(x => [x.field, x.message]))); } });
</script>
<template>
  <form @submit="onSubmit" novalidate>
    <label for="title">Titre</label><input id="title" v-model="title" v-bind="titleAttrs" :aria-invalid="!!errors.title" aria-describedby="title-err" />
    <p v-if="errors.title" id="title-err" role="alert">{{ errors.title }}</p>
    <div v-for="(f, i) in fields" :key="f.key"><Field :name="`contacts[${i}].email`" :aria-label="`Contact ${i + 1}`" /><button type="button" @click="remove(i)">Retirer</button></div>
    <button type="button" @click="push({ email: '' })">Ajouter un contact</button>
    <button :disabled="isSubmitting">Enregistrer</button>
  </form>
</template>"""),
  ("Accessibilité testée", "", """const { container } = render(IncidentForm);   // @testing-library/vue
expect(await axe(container)).toHaveNoViolations();
await fireEvent.click(screen.getByRole('button', { name: 'Enregistrer' }));
expect(await screen.findByRole('alert')).toHaveTextContent('Au moins 3 caractères');""")],
 [("<code>v-model.lazy</code> : quand ?", "Pour valider ou recalculer seulement à la perte de focus (<code>change</code>) plutôt qu'à chaque frappe (<code>input</code>) : champs coûteux ou validation distante."),
  ("Pourquoi <code>toTypedSchema</code> ?", "Il adapte le schéma Zod à VeeValidate et infère les types des valeurs : <code>handleSubmit</code> reçoit un objet typé, et les noms de champs sont vérifiés.")],
 ("Formulaire d'incident", ["Schéma Zod partagé, VeeValidate avec tableau de contacts et règle croisée, erreurs 422 mappées.", "Zéro violation axe, test clavier.", "Variante minimale sans bibliothèque (v-model + computed) pour comparer."],
  "La variante minimale montre le seuil : au-delà de trois champs avec règles croisées et tableaux, VeeValidate évite de réécrire touched/dirty/submitCount. Test clavier : <code>await userEvent.tab(); expect(screen.getByLabelText('Titre')).toHaveFocus()</code>.")),

ch("Tests, qualité et outillage", 's',
 ["Vitest + Vue Test Utils (ou Testing Library Vue) pour les composants ; MSW pour l'API ; Playwright pour les parcours.", "vue-tsc vérifie les templates (<code>strictTemplates</code> de Vue) ; ESLint plugin-vue et Prettier ; Volar dans l'éditeur.", "Le pipeline : lint → types → unitaires avec couverture → build → e2e, comme pour React et Angular."],
 ["Tester composants, composables et stores", "Vérifier les types des templates avec vue-tsc", "Monter le pipeline complet"],
 [("Composant avec MSW et store", "", """it('affiche puis crée un incident', async () => {
  render(IncidentsPage, { global: { plugins: [createTestingPinia({ stubActions: false }), VueQueryPlugin] } });
  expect(await screen.findByRole('heading', { name: 'Fuite gaz' })).toBeInTheDocument();
  await userEvent.type(screen.getByLabelText('Titre'), 'Inondation');
  await userEvent.click(screen.getByRole('button', { name: 'Créer' }));
  expect(await screen.findByRole('heading', { name: 'Inondation' })).toBeInTheDocument();
});"""),
  ("Types et pipeline", "", """# package.json : "typecheck": "vue-tsc --noEmit -p tsconfig.app.json --composite false"
# .gitlab-ci.yml : lint (eslint + typecheck) → unit (vitest run --coverage, junit) → build (vite build) → e2e (image playwright, vite preview)
# vitest.config.ts : environment: 'jsdom', setupFiles: ['src/test/setup.ts'] (MSW), coverage.provider: 'v8'""")],
 [("Vue Test Utils ou Testing Library Vue ?", "VTU accède à l'instance (wrapper.vm, émissions) : utile pour tester un composant isolé et ses événements. Testing Library force la perspective utilisateur (rôles) : préférable pour les pages."),
  ("Pourquoi vue-tsc en plus de tsc ?", "tsc ne comprend pas les fichiers <code>.vue</code> ni les templates ; vue-tsc vérifie les props, les événements et les expressions de template.")],
 ("Quality gate du front Vue", ["Tests page + composables + store, couverture publiée ; vue-tsc bloquant.", "Playwright en conteneur sur trois parcours.", "Pipeline GitLab identique aux deux autres fronts (fichier partagé par <code>include</code>)."],
  "Le fichier CI partagé (<code>ci/frontend.yml</code>) est inclus par les trois projets avec des variables (<code>TYPECHECK_CMD</code>) : une seule chaîne à maintenir. Trace Playwright conservée en échec.")),

ch("Production : build, performance, sécurité, SSR avec Nuxt", 'e',
 ["Build Vite, image nginx non root, CSP, cache immutable : identique aux autres fronts ; l'analyse du bundle (<code>rollup-plugin-visualizer</code>) guide le découpage (routes lazy, <code>defineAsyncComponent</code>).", "Sécurité : Vue échappe les interpolations ; <code>v-html</code> est le <code>dangerouslySetInnerHTML</code> (DOMPurify) ; jamais de template compilé à partir d'une entrée utilisateur ; BFF pour l'authentification.", "Nuxt apporte SSR/SSG/hybride, routage par fichiers, <code>useFetch</code> avec transfert d'état, server routes et déploiement partout (Nitro)."],
 ["Optimiser et sécuriser une SPA Vue en production", "Choisir entre SPA, SSR et SSG, et mettre en place Nuxt", "Déployer en conteneur derrière le BFF"],
 [("Build et sécurité", "", """// vite.config.ts : build.rollupOptions.output.manualChunks pour isoler les dépendances lourdes ; plugin visualizer
// composants lourds : const IncidentMap = defineAsyncComponent(() => import('./IncidentMap.vue'));
// v-html : <div v-html="DOMPurify.sanitize(html)" /> — seulement pour du contenu de confiance déjà filtré côté serveur
// CSP nginx : script-src 'self' (Vite production n'a pas d'inline) ; connect-src l'API ; frame-ancestors 'none'
// pas de secret dans import.meta.env.VITE_* ; authentification par cookie HttpOnly via BFF (withCredentials)
# Dockerfile : identique au cours React (node:22-alpine build → nginx-unprivileged), dist/ → /usr/share/nginx/html"""),
  ("Nuxt", "", """npx nuxi@latest init crisisshield-portal        # en conteneur node:22
// pages/incidents/[id].vue → route automatique ; const { data, status } = await useFetch(`/api/incidents/${route.params.id}`)   // rendu serveur, état transféré, pas de double requête
// server/api/incidents.get.ts : export default defineEventHandler(async e => $fetch(`${useRuntimeConfig().apiBase}/incidents`, { headers: { cookie: getHeader(e, 'cookie') ?? '' } }))   // le serveur Nuxt joue le BFF
// nuxt.config.ts : routeRules: { '/': { prerender: true }, '/incidents/**': { ssr: true }, '/admin/**': { ssr: false } }   // hybride : statique, SSR, SPA par route
// build : nuxi build → .output/ (Nitro) ; image node:22-alpine qui lance .output/server/index.mjs ; ou nuxi generate pour du statique""")],
 [("Quand Nuxt plutôt que Vue seul ?", "Site public (SEO, premier affichage), contenu statique ou hybride, besoin de routes serveur ou d'un BFF intégré. Une application métier authentifiée reste une SPA Vue derrière un BFF existant."),
  ("<code>v-html</code> avec une chaîne venant de l'API est-il sûr ?", "Non par défaut : l'API peut relayer un contenu saisi par un autre utilisateur. Sanitiser côté serveur et côté client (DOMPurify), et limiter aux cas où le HTML est nécessaire.")],
 ("Mise en production du front Vue et variante Nuxt", ["Image nginx durcie, CSP, cache immutable, scan et signature ; Lighthouse CI ≥ 90.", "Portail public en Nuxt hybride (accueil prérendu, incidents en SSR, admin en SPA) ; mesure LCP contre la SPA.", "Déploiement Kubernetes avec le Deployment de référence ; Playwright sur staging."],
  "Attendu : SPA bundle initial < 200 kB gzip, LCP Nuxt < 1,2 s sur l'accueil prérendu contre ~2,2 s en SPA ; aucun jeton dans le navigateur ; <code>routeRules</code> vérifiées par des requêtes curl (accueil : HTML complet sans JS exécuté ; admin : coquille SPA).")),

ch("Comparer React, Angular et Vue : choisir et argumenter", 'e',
 ["Les trois résolvent le même problème (interface = fonction de l'état) avec trois modèles : React re-rend le composant et réconcilie ; Angular et Vue suivent des signals fins.", "Le choix dépend de l'équipe, de l'écosystème existant, de la durée de vie du projet et des contraintes (SSR, mobile, design system) plus que des benchmarks.", "Savoir dire la même chose dans les trois vocabulaires est ce qu'un Tech Lead doit maîtriser en entretien et en architecture."],
 ["Mettre en correspondance les concepts des trois frameworks", "Argumenter un choix avec des critères non idéologiques", "Migrer ou coexister (micro-frontends, Web Components)"],
 [("Table de correspondance", "", """| Concept              | React                         | Angular                          | Vue                              |
| État local           | useState                      | signal()                         | ref()/reactive()                 |
| Dérivé               | useMemo / calcul au rendu     | computed()                       | computed()                       |
| Effet                | useEffect                     | effect() / afterNextRender       | watch / watchEffect              |
| Props                | props typées                  | input() / input.required()       | defineProps                      |
| Événement            | callback prop                 | output()                         | defineEmits                      |
| Two-way              | value + onChange              | model()                          | defineModel / v-model            |
| Composition          | children / hooks / context    | ng-content / DI / host directives| slots / composables / provide    |
| Données serveur      | TanStack Query               | httpResource / resource / RxJS   | TanStack Query Vue / composable  |
| État global          | Zustand, Redux, Jotai         | service + signals, SignalStore   | Pinia                            |
| Routage              | React Router                  | @angular/router                  | Vue Router                       |
| Formulaires          | React Hook Form + Zod         | Reactive Forms typés / signal forms | VeeValidate + Zod            |
| SSR                  | Next.js, Remix, RSC           | @angular/ssr, hydratation incrémentale | Nuxt, Nitro                |
| Tests                | Vitest + RTL + MSW            | Vitest/TestBed + harnesses       | Vitest + VTU/TL + MSW            |
| Réactivité           | re-rendu + réconciliation (+ Compiler) | signals + OnPush/zoneless | signals (proxies), Vapor         |"""),
  ("Critères de choix", "Équipe (compétences existantes, recrutement local) ; écosystème imposé (design system, back-office Angular, mobile React Native) ; durée de vie et gouvernance (Angular : versions semestrielles guidées, migrations automatiques ; React : écosystème libre, choix à faire ; Vue : entre les deux, un seul chemin recommandé par brique) ; besoin SSR/SEO (les trois le font) ; taille (les trois tiennent des applications de plusieurs centaines d'écrans). Ce qui ne devrait pas décider : les benchmarks de rendu, les modes, le CV du Tech Lead.", None),
  ("Coexister et migrer", "Web Components (Angular Elements, <code>defineCustomElement</code> Vue, wrappers React) partagent un design system entre fronts ; micro-frontends (Native Federation, single-spa) font cohabiter deux frameworks pendant une migration strangler ; jamais de réécriture globale : page par page, derrière le même BFF, avec les tests de bout en bout comme filet.", None)],
 [("Un client a un back-office Angular de 400 écrans et veut « passer à React ». Ta réponse ?", "Pourquoi ? Si c'est la dette (version ancienne, pas de signals), la mise à niveau Angular coûte 10 % d'une réécriture et apporte les mêmes bénéfices. Si c'est le recrutement ou un nouveau produit, coexistence par micro-frontends et nouveaux écrans en React, jamais de big bang."),
  ("Les signals rendent-ils Angular et Vue « plus rapides » que React ?", "Sur des mises à jour fines et fréquentes, oui mesurablement ; sur une application typique, la différence est invisible et React 19 avec Compiler réduit l'écart. La performance vient des données (requêtes, cache, virtualisation), pas du framework.")],
 ("Le même écran dans les trois frameworks", ["Page incidents (liste, filtre, création, clôture optimiste) en React, Angular et Vue, contre la même API et les mêmes tests Playwright.", "Tableau mesuré : lignes de code, taille du bundle, temps de première interaction, temps de dev.", "ADR de choix pour CrisisShield avec trois critères pondérés."],
  "Résultat typique : bundles 45 / 95 / 40 kB gzip, lignes ~300 / ~380 / ~260, Playwright identique pour les trois (même rôles, mêmes textes). L'ADR retient un framework pour des raisons d'équipe et d'écosystème, et note que la décision est réversible page par page grâce au BFF et aux tests e2e partagés.")),
]

# ================================================================ CLOUD
CLOUD = [
ch("Qu'est-ce que le cloud : modèles, régions, responsabilité, coût", 'j',
 ["Le cloud est de l'infrastructure à la demande, facturée à l'usage, exposée par des API : ce qui change tout, c'est l'API, pas la localisation.", "IaaS, CaaS, PaaS, FaaS, SaaS : plus on monte, moins on exploite et moins on contrôle ; on choisit le niveau le plus haut compatible avec les contraintes.", "Responsabilité partagée : le fournisseur sécurise « le cloud », le client sécurise « dans le cloud » (IAM, données, configuration, code)."],
 ["Expliquer les modèles de service et de déploiement, régions et zones", "Lire une facture et prévoir les postes surprises", "Créer un compte sandbox gouverné en Docker (CLI en conteneur)"],
 [("Vocabulaire", "Région : ensemble de datacenters (zones de disponibilité) proches ; zone : datacenter isolé ; edge : points de présence CDN. Multi-AZ est le minimum de production ; multi-région est rare et cher. Élasticité : ajouter/retirer à la demande ; le prix de l'élasticité est la facturation à la seconde et la variabilité.", None),
  ("Premier compte, gouverné dès le premier jour", "", """alias awsc='docker run --rm -it -v "$HOME/.aws:/root/.aws" amazon/aws-cli'
# console : MFA sur root puis plus jamais root ; IAM Identity Center avec un utilisateur et un permission set ; budget 20 $/mois avec alertes 50/80/100 %
awsc configure sso && awsc sso login --profile sandbox && awsc sts get-caller-identity --profile sandbox
awsc ce get-cost-and-usage --time-period Start=2026-09-01,End=2026-09-30 --granularity MONTHLY --metrics UnblendedCost --profile sandbox
# équivalents : az login (image mcr.microsoft.com/azure-cli), gcloud auth login (image google/cloud-sdk)""")],
 [("Une VM éteinte coûte-t-elle quelque chose ?", "Le calcul non, mais le disque attaché, l'adresse IP réservée et les snapshots oui : « éteint » n'est pas « supprimé »."),
  ("Qui est responsable d'un bucket S3 public contenant des données clients ?", "Le client : la configuration d'accès est « dans le cloud ». AWS fournit Block Public Access ; l'activer est de la responsabilité du client.")],
 ("Compte sandbox et facture", ["Compte AWS avec root sous MFA, Identity Center, budget et alertes, CloudTrail activé ; CLI uniquement en conteneur.", "Créer puis supprimer une ressource de chaque type (VM, disque, bucket) et lire la facture le lendemain.", "Tableau : modèles de service avec un exemple AWS/Azure/GCP chacun et ce que le client gère."],
  "Preuve : sortie de <code>get-caller-identity</code> avec un rôle SSO (pas d'utilisateur IAM), capture du budget, et la ligne de coût du lendemain (quelques centimes : le disque du volume, l'IP). Rien ne reste (<code>resourcegroupstaggingapi get-resources</code> vide).")),

ch("Identité et accès : IAM, rôles, fédération, zéro clé statique", 'j',
 ["Tout est refusé par défaut ; une politique autorise ; un deny explicite gagne. Identité (qui), ressource (quoi), organisation (SCP) s'évaluent ensemble.", "Un rôle est une identité temporaire assumée par une charge, un humain fédéré ou un autre compte : plus aucune clé d'accès statique.", "Moindre privilège se construit par les journaux (CloudTrail, IAM Access Analyzer), pas par devinette."],
 ["Écrire et lire une politique IAM, comprendre l'ordre d'évaluation", "Donner une identité à une VM, un conteneur, une fonction, un pipeline (OIDC) et un humain (SSO)", "Auditer et réduire les permissions"],
 [("Politique et rôle", "", """{ "Version": "2012-10-17", "Statement": [
  { "Effect": "Allow", "Action": ["s3:GetObject", "s3:PutObject"], "Resource": "arn:aws:s3:::crisis-uploads/*", "Condition": { "StringEquals": { "aws:PrincipalTag/team": "crisis" } } },
  { "Effect": "Deny", "Action": "s3:*", "Resource": "*", "Condition": { "Bool": { "aws:SecureTransport": "false" } } } ] }
# rôle de tâche ECS / instance profile EC2 / rôle Lambda : la charge assume le rôle, les identifiants sont injectés et tournent seuls
# pipeline GitLab : id_tokens → sts assume-role-with-web-identity (OIDC), bound sur projet et branche
# humains : Identity Center (AWS), Entra ID (Azure), Cloud Identity (GCP) → SSO, MFA, sessions courtes"""),
  ("Auditer", "", """awsc iam generate-service-last-accessed-details --arn arn:aws:iam::123456789012:role/crisis-api --profile sandbox   # services utilisés → retirer le reste
awsc accessanalyzer list-findings --analyzer-arn … --profile sandbox    # ressources exposées à l'extérieur
# CloudTrail : chaque appel API avec identité, IP, résultat ; Athena pour interroger""")],
 [("Une politique d'identité autorise <code>s3:*</code>, la politique du bucket refuse tout sauf un rôle précis. Résultat pour un autre rôle ?", "Refus : le deny explicite de la politique de ressource gagne. Et si le bucket n'avait pas de deny mais seulement un allow ciblé, l'allow d'identité suffirait (même compte)."),
  ("Pourquoi un jeton OIDC de pipeline vaut-il mieux qu'une clé d'accès dans les variables CI ?", "Il est signé par la plateforme CI, lié au projet et à la branche, échangé contre des identifiants de 15 minutes à 1 heure, non copiable et non réutilisable : une fuite est inutile.")],
 ("Identités sans clé", ["Rôle pour une VM (instance profile) qui lit un bucket ; rôle assumé par un pipeline GitLab par OIDC ; utilisateur SSO avec MFA.", "Access Analyzer et last-accessed pour réduire un rôle trop large ; Athena sur CloudTrail : « qui a lu ce bucket ? ».", "Aucune clé dans <code>~/.aws/credentials</code> ni dans GitLab."],
  "Preuve : <code>curl 169.254.169.254/latest/meta-data/iam/security-credentials/</code> depuis la VM (IMDSv2) montre des identifiants temporaires ; le job GitLab affiche <code>assumed-role/gitlab-main</code> ; le rôle passe de <code>s3:*</code> à deux actions après last-accessed ; Athena renvoie l'identité et l'IP de chaque <code>GetObject</code>.")),

ch("Réseau : VPC, sous-réseaux, routage, sécurité, connectivité", 'c',
 ["Un VPC est un réseau privé isolé ; les sous-réseaux publics ont une route vers Internet, les privés sortent par NAT ou pas du tout ; trois zones, trois niveaux (public, application, données).", "Security groups (stateful, par référence) pour tout ; NACL pour quelques refus ; endpoints pour parler aux services sans Internet.", "Connectivité : peering, Transit Gateway (hub), VPN site-à-site, Direct Connect ; DNS privé et résolution hybride."],
 ["Dessiner et coder un VPC de production en trois zones", "Sécuriser les flux par security groups référencés et endpoints", "Relier des réseaux (peering, TGW, VPN) et comprendre le DNS privé"],
 [("VPC de production en Terraform", "", """module "network" { source = "terraform-aws-modules/vpc/aws"; version = "~> 5.13"
  name = "crisis-prod"; cidr = "10.20.0.0/16"; azs = ["eu-west-3a", "eu-west-3b", "eu-west-3c"]
  public_subnets = ["10.20.1.0/24", "10.20.2.0/24", "10.20.3.0/24"]; private_subnets = ["10.20.11.0/24", "10.20.12.0/24", "10.20.13.0/24"]; database_subnets = ["10.20.21.0/24", "10.20.22.0/24", "10.20.23.0/24"]
  enable_nat_gateway = true; one_nat_gateway_per_az = true; enable_dns_hostnames = true; enable_flow_log = true }
resource "aws_vpc_endpoint" "s3" { vpc_id = module.network.vpc_id; service_name = "com.amazonaws.eu-west-3.s3"; route_table_ids = module.network.private_route_table_ids }
# SG : alb (443 depuis 0.0.0.0/0) → api (8080 depuis sg alb) → db (5432 depuis sg api) ; aucun CIDR interne"""),
  ("Connectivité et DNS", "Peering : deux VPC, pas transitif, simple. Transit Gateway : hub pour N VPC et le site, routage centralisé. VPN site-à-site : IPsec sur Internet, minutes à mettre en place, débit limité. Direct Connect : lien dédié, semaines, pour les gros volumes ou la latence. DNS : zone privée Route 53 associée aux VPC ; résolveurs entrants/sortants pour l'hybride ; Azure VNet + Private DNS, GCP VPC global (multi-région natif) + Cloud DNS.", None)],
 [("Pourquoi un NAT par zone en production ?", "Un NAT unique dans la zone A tombe avec la zone A : les instances de B et C perdent Internet. Le coût (3 × 32 $) est le prix de la résilience ; en dev, un seul NAT."),
  ("Une instance privée doit lire S3 : NAT ou endpoint ?", "Endpoint Gateway S3 : gratuit, trafic interne, pas de facturation NAT. Le NAT ne sert qu'à ce qui n'a pas d'endpoint.")],
 ("VPC de CrisisShield", ["VPC trois zones en Terraform (LocalStack ou sandbox), security groups par référence, endpoints S3/ECR/Secrets Manager, flow logs.", "Peering vers un second VPC (labo) et test de résolution DNS privée.", "Schéma des tables de routage et estimation infracost."],
  "Preuve : <code>terraform plan</code> propre, flow logs dans CloudWatch montrant un flux refusé, <code>nslookup api.crisis.internal</code> depuis le VPC pair, infracost ≈ 100 $/mois pour trois NAT (et ≈ 35 $ avec un seul : la décision est chiffrée).")),

ch("Calcul : VM, conteneurs managés, serverless", 'c',
 ["EC2/VM : contrôle total, exploitation à charge (patch, SSH, images) ; ECS Fargate / Cloud Run / Container Apps : conteneurs sans nœuds ; EKS/AKS/GKE : Kubernetes standard ; Lambda/Functions : par événement.", "Le choix se fait par profil de charge (continu, intermittent, événementiel), compétence d'équipe, portabilité et coût à l'échelle.", "Images dorées, auto-scaling groups, instances Spot et Graviton sont les leviers de la VM ; digest, rôle de tâche et circuit breaker ceux du conteneur."],
 ["Déployer une VM propre (image, user-data, auto-scaling) et un conteneur Fargate", "Écrire et déployer une fonction serverless avec ses limites en tête", "Choisir le bon service de calcul et le justifier"],
 [("Fargate : conteneur sans nœud", "", """resource "aws_ecs_task_definition" "api" { family = "api"; requires_compatibilities = ["FARGATE"]; network_mode = "awsvpc"; cpu = 512; memory = 1024; execution_role_arn = aws_iam_role.exec.arn; task_role_arn = aws_iam_role.task.arn
  container_definitions = jsonencode([{ name = "api", image = "${aws_ecr_repository.api.repository_url}@${var.digest}", portMappings = [{ containerPort = 8080 }],
    secrets = [{ name = "DB_PASSWORD", valueFrom = "${aws_secretsmanager_secret.db.arn}:password::" }], logConfiguration = { logDriver = "awslogs", options = { "awslogs-group" = "/crisis/api", "awslogs-region" = "eu-west-3", "awslogs-stream-prefix" = "api" } },
    healthCheck = { command = ["CMD-SHELL", "wget -qO- http://localhost:8080/actuator/health || exit 1"], interval = 15, startPeriod = 60 } }]) }
resource "aws_ecs_service" "api" { …; desired_count = 2; launch_type = "FARGATE"; deployment_circuit_breaker { enable = true; rollback = true }; lifecycle { ignore_changes = [desired_count] } }
resource "aws_appautoscaling_target" "api" { min_capacity = 2; max_capacity = 8; … }   # cible CPU 60 %"""),
  ("Lambda, en Java", "", """// Quarkus natif ou Spring Cloud Function ; handler → événement (S3, SQS, EventBridge, API Gateway)
// limites : 15 min, 10 Go, cold start (Java JVM ≈ 3 s → SnapStart ou natif ≈ 150 ms), pas de connexions persistantes (RDS Proxy)
awsl lambda invoke --function-name report --payload '{"org":"org-1"}' /tmp/o.json --log-type Tail --query LogResult --output text | base64 -d | grep -E 'Init Duration|Duration'
// quand : rare, court, événementiel ; jamais pour une API à trafic continu (coût et latence)""")],
 [("Trafic continu de 60 req/s, équipe de 4, pas de Kubernetes en place : quel calcul ?", "ECS Fargate (ou Cloud Run/Container Apps) : conteneurs sans nœuds, rôle de tâche, auto-scaling, coût prévisible. EKS seulement si la portabilité ou l'écosystème Kubernetes est requis."),
  ("Pourquoi <code>ignore_changes = [desired_count]</code> ?", "L'auto-scaling pilote ce nombre ; sans l'ignorer, chaque apply Terraform le remettrait à la valeur du code.")],
 ("CrisisShield en trois calculs", ["API en Fargate avec auto-scaling et circuit breaker ; VM d'outillage en ASG avec image dorée et user-data ; générateur de rapport en Lambda natif.", "Test de charge k6 : l'auto-scaling monte à 5× ; cold start mesuré JVM contre natif.", "Tableau de décision avec coût mensuel de chaque option (calculatrice AWS)."],
  "Preuve : <code>describe-services</code> montre 2 → 6 tâches pendant k6 et un rollback automatique sur une image cassée ; Lambda JVM Init 2 900 ms contre natif 120 ms ; tableau : Fargate ≈ 30 $, EKS ≈ 73 $ (control plane) + nœuds, Lambda ≈ 0,20 $ pour 10 000 rapports.")),

ch("Stockage et bases de données managées", 'c',
 ["Objet (S3), bloc (EBS), fichier (EFS) : trois besoins ; l'objet est la base de tout (données, sauvegardes, artefacts, sites statiques).", "Bases managées : RDS/Aurora (relationnel), DynamoDB (clé-valeur à l'échelle), ElastiCache (cache), OpenSearch ; le fournisseur gère patch, sauvegardes, bascule ; le client gère schéma, requêtes, dimensionnement.", "Protection des données : chiffrement par défaut (KMS), versioning, Object Lock, réplication, sauvegardes testées."],
 ["Configurer un bucket sûr (privé, chiffré, versionné, cycle de vie, lock)", "Déployer une base RDS multi-AZ et comprendre réplica, Aurora, PITR", "Choisir entre relationnel, clé-valeur et cache selon le besoin"],
 [("S3 : la configuration de référence", "", """resource "aws_s3_bucket" "uploads" { bucket = "crisis-uploads-123456789012" }
resource "aws_s3_bucket_public_access_block" "u" { bucket = aws_s3_bucket.uploads.id; block_public_acls = true; block_public_policy = true; ignore_public_acls = true; restrict_public_buckets = true }
resource "aws_s3_bucket_server_side_encryption_configuration" "u" { bucket = aws_s3_bucket.uploads.id; rule { apply_server_side_encryption_by_default { sse_algorithm = "aws:kms"; kms_master_key_id = aws_kms_key.data.arn } } }
resource "aws_s3_bucket_versioning" "u" { bucket = aws_s3_bucket.uploads.id; versioning_configuration { status = "Enabled" } }
resource "aws_s3_bucket_lifecycle_configuration" "u" { bucket = aws_s3_bucket.uploads.id; rule { id = "tiering"; status = "Enabled"; transition { days = 30; storage_class = "INTELLIGENT_TIERING" }; noncurrent_version_expiration { noncurrent_days = 90 } } }
# sauvegardes : bucket séparé, compte séparé, Object Lock COMPLIANCE 30 j, réplication inter-région"""),
  ("RDS et Aurora", "", """resource "aws_db_instance" "main" { engine = "postgres"; engine_version = "16.4"; instance_class = "db.t4g.medium"; multi_az = true; storage_encrypted = true; backup_retention_period = 7; deletion_protection = true; publicly_accessible = false; performance_insights_enabled = true; … }
# multi-AZ : réplique synchrone, bascule ~1 min, zéro perte ; réplica de lecture : asynchrone, décharge les lectures ; Aurora : stockage réparti 3 AZ, bascule en secondes, Global Database
# PITR : restauration à la seconde dans une nouvelle instance ; testée chaque mois (script)
# DynamoDB : clé de partition + tri, capacité à la demande, TTL, streams ; pour les accès par clé à très haut débit, pas pour les jointures""")],
 [("Une table de sessions de 50 000 écritures/s : RDS ou DynamoDB ?", "DynamoDB : accès par clé, débit linéaire, TTL intégré. RDS plafonne et coûte en instance ; un cache Redis est l'alternative si la durabilité n'est pas requise."),
  ("Versioning activé, un objet supprimé par erreur : récupérable ?", "Oui : la suppression pose un marqueur, les versions restent ; on supprime le marqueur. Avec Object Lock, même une suppression de version est impossible avant l'échéance.")],
 ("Données de CrisisShield", ["Bucket uploads de référence + bucket de sauvegardes verrouillé dans un compte séparé ; test de suppression refusée.", "RDS multi-AZ avec bascule provoquée (<code>reboot --force-failover</code>) chronométrée ; restauration PITR dans une instance de test.", "Table DynamoDB de sessions avec TTL ; ElastiCache Redis pour le cache."],
  "Preuve : bascule RDS en 48 s avec 3 requêtes en erreur (Hikari retente) ; PITR restaurée à T-10 min contient l'enregistrement témoin ; <code>aws s3 rm</code> sur le bucket verrouillé → <code>AccessDenied</code> même en admin.")),

ch("Sécurité cloud : détection, chiffrement, secrets, conformité", 's',
 ["Les quatre services de fondation avant toute charge : CloudTrail (qui a fait quoi), Config (est-ce conforme), GuardDuty (est-ce anormal), Security Hub (agrégation, CIS) ; équivalents Azure Defender/Policy et GCP Security Command Center.", "KMS chiffre tout par défaut (enveloppe) ; Secrets Manager/Key Vault/Secret Manager avec rotation ; jamais de secret dans le code ni les variables.", "Conformité : CIS benchmark automatisé (Prowler), SCP pour interdire l'ininterdisable, preuves collectées par script."],
 ["Activer et lire les services de détection", "Chiffrer et gérer les secrets avec rotation", "Produire un rapport CIS et corriger par le code"],
 [("Fondations de sécurité", "", """awsc cloudtrail create-trail --name org --s3-bucket-name crisis-trail-… --is-multi-region-trail --enable-log-file-validation && awsc cloudtrail start-logging --name org
awsc guardduty create-detector --enable ; awsc securityhub enable-security-hub --enable-default-standards ; awsc configservice put-configuration-recorder …
# SCP (organisation) : deny cloudtrail:StopLogging, deny hors régions autorisées, deny ec2:RunInstances sans tag Owner, deny création de clés d'accès utilisateur
# KMS : une clé par domaine de données (uploads, base, sauvegardes), rotation annuelle, politique de clé restreinte ; chiffrement d'enveloppe : la clé de données est chiffrée par la clé KMS
# Secrets Manager : rotation Lambda du mot de passe RDS tous les 30 j ; l'application lit le secret par rôle, jamais par variable"""),
  ("CIS et preuves", "", """docker run --rm -v "$HOME/.aws:/home/prowler/.aws:ro" -v "$PWD/reports:/home/prowler/output" toniblyx/prowler:4 aws --profile sandbox --compliance cis_2.0_aws --output-formats html,json-ocsf
# corriger en Terraform (pas en console) puis rejouer ; les findings restants deviennent des exceptions datées""")],
 [("GuardDuty signale un appel API depuis une IP Tor avec le rôle de la CI. Que fais-tu ?", "Révoquer les sessions du rôle (politique deny avec <code>aws:TokenIssueTime</code>), chercher dans CloudTrail ce que la session a fait, faire tourner les secrets touchés, chercher la fuite (jeton dans un log ?), post-mortem. Le jeton OIDC court limite les dégâts."),
  ("Pourquoi une clé KMS par domaine de données ?", "Rayon d'impact et gouvernance : une politique de clé par usage, une révocation ciblée (crypto-shredding des sauvegardes d'un client), un audit par clé.")],
 ("Fondations de sécurité du compte CrisisShield", ["CloudTrail, Config, GuardDuty, Security Hub activés en Terraform ; SCP de garde-fous ; Access Analyzer.", "KMS par domaine, Secrets Manager avec rotation, application qui lit par rôle.", "Prowler avant/après avec 10 findings corrigés en code ; script de preuves mensuel."],
  "Preuve : Security Hub score CIS passant de ~40 % à > 85 %, une rotation Secrets Manager observée (nouvelle version, application reconnectée sans redémarrage), et un test SCP : <code>StopLogging</code> refusé même en administrateur.")),

ch("Infrastructure as Code et livraison sur le cloud", 's',
 ["Rien à la main : Terraform (ou OpenTofu, CloudFormation, Bicep, Pulumi) décrit tout, avec state distant verrouillé, modules, environnements séparés.", "Le pipeline : fmt/validate → scan (trivy config, checkov) → coût (infracost) → plan en MR → apply manuel avec identité OIDC ; dérive détectée en continu.", "Images (Packer), configuration (Ansible ou cloud-init), déploiement applicatif (digest, blue/green, canary avec CodeDeploy ou le LB)."],
 ["Structurer un dépôt Terraform multi-environnements avec modules et tests", "Monter un pipeline IaC sûr avec plan en MR et apply OIDC", "Déployer une application par digest avec bascule progressive"],
 [("Structure et pipeline", "", """infra/
  modules/{network,compute,database,security}/    # testés : terraform test avec mock_provider
  envs/{dev,staging,prod}/                         # un state par env : backend s3 (versioning, lock DynamoDB) ; key = env/component.tfstate
# .gitlab-ci.yml
plan: { image: hashicorp/terraform:1.9, id_tokens: { AWS_ID: { aud: sts.amazonaws.com } }, script: [terraform init, terraform fmt -check -recursive, terraform validate, trivy config --exit-code 1 --severity HIGH,CRITICAL ., infracost breakdown --path ., terraform plan -out=plan.bin, terraform show -no-color plan.bin > plan.txt], artifacts: { paths: [plan.bin, plan.txt] } }   # tfcmt poste plan.txt dans la MR
apply: { stage: apply, when: manual, rules: [{ if: $CI_COMMIT_BRANCH == "main" }], resource_group: prod, script: [terraform apply plan.bin] }
drift: { rules: [{ if: $CI_PIPELINE_SOURCE == "schedule" }], script: [terraform plan -detailed-exitcode || (echo dérive && exit 1)] }"""),
  ("Déploiement progressif", "Nouvelle image par digest → nouveau target group (green) → tests → bascule pondérée du listener ALB (10 %, 50 %, 100 %) avec alarmes CloudWatch comme critères d'arrêt → suppression du blue. CodeDeploy (ECS blue/green), ou Argo Rollouts sur EKS, automatisent cette séquence.", None)],
 [("Pourquoi <code>apply</code> manuel et sur main seulement ?", "Le plan est revu dans la MR ; l'apply engage la production et doit être une décision explicite, avec <code>resource_group</code> pour éviter deux apply simultanés. Un apply automatique se justifie en dev."),
  ("Une ressource a été modifiée en console. Que fait le pipeline de dérive ?", "Le <code>plan -detailed-exitcode</code> renvoie 2 : le job échoue et ouvre un ticket ; la correction passe par le code (adopter ou revenir), jamais par le state à la main.")],
 ("Plateforme CrisisShield en IaC", ["Dépôt Terraform modulaire avec tests, trois environnements, backend verrouillé.", "Pipeline complet avec plan commenté en MR, apply OIDC manuel, dérive planifiée.", "Déploiement blue/green de l'API sur ECS avec bascule pondérée et rollback sur alarme."],
  "Preuve : une MR montre le plan et le coût ; un apply depuis un poste échoue (pas d'identifiants) ; le job de dérive détecte un tag ajouté en console ; le blue/green revient seul en arrière quand on déploie une image dont le healthcheck échoue.")),

ch("Observabilité, fiabilité et exploitation dans le cloud", 's',
 ["Métriques, logs et traces natifs (CloudWatch, X-Ray ; Azure Monitor ; Cloud Operations) ou OpenTelemetry vers sa propre pile ; alarmes sur des SLO, pas sur des seuils bruts.", "Haute disponibilité : multi-AZ partout, auto-scaling, health checks, DNS avec bascule ; reprise : sauvegardes testées, RTO/RPO par service, exercice de bascule.", "Exploitation : patch par remplacement (images), fenêtres, runbooks, astreinte, post-mortems."],
 ["Instrumenter et alerter sur SLO avec les services natifs ou OpenTelemetry", "Concevoir la HA et un PRA cloud (multi-AZ, réplication, bascule DNS)", "Exploiter sans SSH : SSM, images, remplacement"],
 [("Alarmes sur SLO", "", """resource "aws_cloudwatch_metric_alarm" "api_5xx" { alarm_name = "api-error-budget"; comparison_operator = "GreaterThanThreshold"; evaluation_periods = 3; threshold = 1
  metric_query { id = "e"; expression = "100 * errors / requests"; label = "5xx %" ; return_data = true }
  metric_query { id = "errors"; metric { namespace = "AWS/ApplicationELB"; metric_name = "HTTPCode_Target_5XX_Count"; period = 60; stat = "Sum"; dimensions = { LoadBalancer = aws_lb.main.arn_suffix } } }
  metric_query { id = "requests"; metric { namespace = "AWS/ApplicationELB"; metric_name = "RequestCount"; period = 60; stat = "Sum"; dimensions = { LoadBalancer = aws_lb.main.arn_suffix } } }
  alarm_actions = [aws_sns_topic.page.arn]; ok_actions = [aws_sns_topic.page.arn] }
# logs : awslogs → CloudWatch Logs Insights (fields @timestamp, level, msg | filter level = "ERROR" | stats count() by bin(5m)) ; rétention 30 j ; traces : ADOT collector sidecar → X-Ray ou Tempo"""),
  ("PRA cloud", "Sauvegardes : snapshots RDS automatiques + copie inter-région, S3 réplication vers un compte isolé, AWS Backup avec vault verrouillé. Bascule : Aurora Global Database (<code>failover-global-cluster</code>), Route 53 health check + failover record, infrastructure secondaire par le même Terraform (pilot light). Exercice trimestriel chronométré ; SSM Session Manager remplace SSH (journalisé, sans port ouvert).", None)],
 [("Pourquoi une expression métrique (ratio) plutôt qu'un seuil sur le nombre de 5xx ?", "Le nombre dépend du trafic : 50 erreurs à 3 h du matin et 50 erreurs à midi n'ont pas le même sens. Le ratio est le SLI ; le seuil est la consommation du budget."),
  ("Comment patcher une flotte de VM sans SSH ?", "Nouvelle image dorée (Packer), mise à jour du launch template, instance refresh de l'ASG (remplacement progressif avec health checks). SSM pour les commandes ponctuelles, journalisées.")],
 ("Exploitation de CrisisShield", ["Alarmes SLO (disponibilité, latence p95) avec SNS → astreinte ; Logs Insights sauvegardées ; traces X-Ray ou OTel.", "PRA : réplication S3 et RDS inter-région, bascule Route 53 testée et chronométrée, coût mesuré puis détruit.", "Instance refresh de l'ASG avec une nouvelle image ; SSM Session Manager ; port 22 fermé partout."],
  "Preuve : alarme déclenchée par k6 injectant 2 % d'erreurs (à T+3 min) et revenue OK ; bascule Route 53 en ~90 s (TTL 60 s) avec boucle curl ; instance refresh sans requête perdue ; <code>describe-security-groups</code> sans règle sur 22.")),

ch("FinOps : comprendre, optimiser, opérer le coût", 's',
 ["Informer (tags, allocation par équipe et par service, coût par unité), optimiser (éteindre, redimensionner, architecture, engagements — dans cet ordre), opérer (rapport mensuel, anomalies, décisions).", "Les postes cachés : NAT, trafic sortant, logs sans rétention, snapshots, instances de dev la nuit, IP publiques, LoadBalancers oubliés.", "Spot pour l'interruptible, Savings Plans après optimisation sur le socle stable, Graviton partout où c'est possible."],
 ["Allouer les coûts par tag et calculer un coût par unité", "Appliquer les leviers dans l'ordre et mesurer le gain", "Mettre en place budgets, anomalies et rapport mensuel"],
 [("Allocation et leviers", "", """provider "aws" { default_tags { tags = { Owner = "crisis", Env = var.env, Service = "crisisshield", CostCenter = "lab" } } }
awsc ce get-cost-and-usage --time-period Start=2026-09-01,End=2026-10-01 --granularity MONTHLY --metrics UnblendedCost --group-by Type=TAG,Key=Env --output table
# 1. éteindre : EventBridge Scheduler → ecs update-service --desired-count 0 à 20 h, rds stop-db-instance (dev) ; 2. redimensionner : Compute Optimizer, Performance Insights → t4g.medium → small ; 3. architecture : endpoints, rétention logs 30 j, Intelligent-Tiering, Graviton ; 4. engagements : Savings Plan 1 an sur le socle prod après un mois de mesure
awsc ce create-anomaly-monitor --anomaly-monitor '{"MonitorName":"services","MonitorType":"DIMENSIONAL","MonitorDimension":"SERVICE"}'"""),
  ("Coût par unité et rapport", "Coût mensuel / requêtes (ou incidents traités) : la seule métrique qui distingue croissance et gaspillage. Rapport d'une page : coût par équipe, top 3 services, leviers appliqués avec gain, prévision, trois décisions. Budgets par environnement avec action automatique en dev (retrait des droits de création à 100 %), alerte seulement en prod.", None)],
 [("La facture monte de 30 % et le trafic de 30 % : problème ?", "Non si le coût par unité est stable ou baisse ; oui s'il monte. Sans coût unitaire, on ne peut pas répondre."),
  ("Quand acheter un Savings Plan ?", "Après avoir éteint, redimensionné et corrigé l'architecture, sur la part stable mesurée pendant un mois ; s'engager avant fige le gaspillage pour un an.")],
 ("FinOps sur le compte CrisisShield", ["Tags obligatoires (default_tags + règle Config), allocation par Env et Service, coût par 1 000 requêtes.", "Leviers 1 à 3 appliqués et mesurés ; détecteur d'anomalies ; budgets avec action en dev.", "Rapport mensuel d'une page avec trois décisions."],
  "Résultat attendu : ≈ 160 → ≈ 95 $/mois (−40 %) sans engagement ; coût par 1 000 requêtes 0,42 → 0,25 $ ; une anomalie détectée en < 24 h lors d'un test (instance oubliée).")),

ch("Architecture cloud, multi-cloud, souveraineté et certification", 'e',
 ["Le Well-Architected Framework (six piliers : excellence opérationnelle, sécurité, fiabilité, performance, coût, durabilité) est la grille de revue ; chaque décision se justifie par un pilier et un coût.", "Multi-cloud subi, choisi ou portable ; la vraie dépendance est l'identité, le réseau, les services serverless et les données ; une architecture portable (conteneurs, PostgreSQL, Terraform, OpenTelemetry) garde le choix.", "Souveraineté : SecNumCloud, cloud de confiance (Bleu, S3NS), hébergement européen ; savoir produire un dossier de réversibilité. Certification : Solutions Architect Associate (puis Professional/DevOps), AZ-104/305, GCP ACE."],
 ["Revoir une architecture avec le Well-Architected Framework", "Traduire une architecture AWS en Azure et GCP et décider du multi-cloud", "Préparer une certification avec le parcours et le sandbox"],
 [("Architecture de référence CrisisShield", "", """Route 53 → CloudFront (front statique S3 + WAF) → ALB (TLS, WAF) → ECS Fargate api ×N (3 AZ, rôle de tâche) → RDS PostgreSQL multi-AZ + réplica ; ElastiCache Redis ; S3 uploads (KMS) ; MSK ou SQS pour les événements ; Lambda natif pour les rapports ; Secrets Manager ; CloudWatch + OTel ; CloudTrail/GuardDuty/Config/Security Hub ; sauvegardes inter-région dans un compte isolé ; Terraform, pipeline OIDC
# revue Well-Architected : pour chaque pilier, 3 questions, réponse, preuve (TP), écart ; ex. fiabilité : « comment récupérez-vous d'une panne de zone ? » → multi-AZ + bascule RDS testée (chapitre 8)"""),
  ("Équivalences et portabilité", "", """| AWS            | Azure                    | GCP                    |
| VPC / SG       | VNet / NSG               | VPC / firewall rules   |
| ALB            | Application Gateway      | Cloud Load Balancing   |
| ECS Fargate    | Container Apps           | Cloud Run              |
| EKS            | AKS                      | GKE                    |
| RDS / Aurora   | Flexible Server          | Cloud SQL / AlloyDB    |
| S3             | Blob Storage             | Cloud Storage          |
| IAM rôle       | identité managée         | compte de service      |
| Secrets Manager| Key Vault                | Secret Manager         |
| CloudTrail     | Activity Log             | Cloud Audit Logs       |
| Lambda         | Functions                | Cloud Functions / Run  |
# portable : conteneur, PostgreSQL, Terraform, OTel, Keycloak ; spécifique : identité, réseau, serverless, facturation""")],
 [("Un client exige « pas de dépendance à un fournisseur ». Réponse d'architecte ?", "On distingue portable (briques standard, dossier de réversibilité avec formats et délais) et multi-cloud actif (deux déploiements, deux équipes : coût humain énorme). On promet le premier, on chiffre le second, on ne le fait que sur exigence réglementaire ou client explicite."),
  ("Comment préparer le Solutions Architect Associate avec ce parcours ?", "Les dix chapitres couvrent les domaines de l'examen ; chaque TP est un scénario d'examen vécu. Ajouter : lecture des FAQ des services clés, deux examens blancs chronométrés, et le sandbox pour vérifier chaque doute au lieu de mémoriser.")],
 ("Dossier d'architecture et revue Well-Architected", ["Architecture de référence de CrisisShield dessinée (C4 ou diagramme AWS) avec justification par pilier et coût à trois ans (calculatrice).", "Revue Well-Architected : 18 questions, preuves, écarts, plan.", "Version Azure et GCP du même schéma avec les trois estimations ; dossier de réversibilité d'une page ; plan de préparation certification."],
  "Livrable : dossier de 8 pages relu par un pair, coût à 3 ans ≈ 6 k$/an année 1, écarts Well-Architected priorisés (ex. WAF absent sur l'ALB, sauvegardes non testées → corrigés), dossier de réversibilité avec formats (dump PostgreSQL, objets S3, Terraform) et délai (2 semaines), et un calendrier de 6 semaines vers l'examen.")),
]

d = sys.argv[1]
NAV = [('cours-react.html', 'React'), ('cours-angular.html', 'Angular'), ('cours-vue.html', 'Vue'), ('cours-cloud.html', 'Cloud')]
def nav(me): return [n for n in NAV if n[0] != me]
page('cours-react.html', 'React — de zéro à expert', "Onze chapitres pour maîtriser React 19 avec TypeScript : composants, état, effets, données serveur, état global (stores, atomes, signals), formulaires, tests, production, patrons avancés. Projet fil conducteur : le front de CrisisShield. Tout tourne en Docker, chaque chapitre a ses exercices corrigés et un travail pratique avec correction type.", "≈ 45 h de travail · prérequis : Docker Desktop, notions de HTML/CSS · les cours Angular et Vue se lisent en miroir, et le chapitre 9 du cours Vue compare les trois.", REACT, nav('cours-react.html'))
page('cours-angular.html', 'Angular — de zéro à expert', "Onze chapitres pour maîtriser Angular 19/20 : composants standalone, signals (signal, computed, effect, linkedSignal, resource), injection de dépendances, routage, formulaires typés, NgRx SignalStore, tests, SSR, production, directives, CDK, Nx et micro-frontends. Projet fil conducteur : le front de CrisisShield. Tout tourne en Docker, chaque chapitre a ses exercices corrigés et un travail pratique avec correction type.", "≈ 45 h de travail · prérequis : Docker Desktop, notions de HTML/CSS · les cours React et Vue se lisent en miroir.", ANG, nav('cours-angular.html'))
page('cours-vue.html', 'Vue.js — de zéro à expert', "Neuf chapitres pour maîtriser Vue 3 avec TypeScript : SFC et réactivité (ref, computed, watch), composants et slots, composables et réactivité avancée, Vue Router, Pinia, formulaires, tests, production avec Nuxt, et un chapitre final qui compare React, Angular et Vue. Projet fil conducteur : le front de CrisisShield. Tout tourne en Docker, chaque chapitre a ses exercices corrigés et un travail pratique avec correction type.", "≈ 35 h de travail · prérequis : Docker Desktop, notions de HTML/CSS.", VUE, nav('cours-vue.html'))
page('cours-cloud.html', 'Cloud — de zéro à expert', "Dix chapitres pour maîtriser le cloud (AWS en fil rouge, équivalences Azure et GCP) : modèles et compte, identité, réseau, calcul, stockage et bases, sécurité, infrastructure as code et livraison, observabilité et reprise, FinOps, architecture et certification. Projet fil conducteur : CrisisShield sur AWS. Tout passe par la CLI en conteneur et Terraform, chaque chapitre a ses exercices corrigés et un travail pratique avec correction type.", "≈ 50 h de travail · prérequis : Docker Desktop, un compte AWS sandbox (quelques euros au total, tout est détruit après chaque TP) · complète le niveau 4 du parcours DevOps, qui va plus vite et plus loin sur Terraform.", CLOUD, nav('cours-cloud.html'))
