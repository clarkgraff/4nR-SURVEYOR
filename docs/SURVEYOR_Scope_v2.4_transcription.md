# 4nR-SURVEYOR — Complete Scope v2.4 (source transcription)

> Historical source preserved without abridgement. Extracted from original DOCX; some tabular layout is flattened. Later v2.5 manuscript, where available, takes precedence. Legacy wording is retained in this source.



---


4nR-SURVEYOR
COMPLETE SYSTEM SCOPE & DEVELOPMENT SPECIFICATION
Version 2.4 | 16 October 2026 | Consolidated self-contained scope

Audience: first-time developers, system architects, researchers and technical partners. This document is self-
contained. No earlier scope version is required to understand or implement it.

Status: Approved architectural direction and implementation requirements, with separately labelled candidate
models and unresolved engineering decisions. This scope is not a claim that proposed software or models have
been implemented or benchmarked.



EXECUTIVE SCOPE — WHY THIS SYSTEM EXISTS
Faire Wind & Song (FWaS) is a nine-season worldwide maritime expedition in which music, cuisine, history,
language, origins, culture and the natural environment inform where the expedition goes, whom it meets and what
it documents. The central mission is: “Discovering & exploring our commonalities. Acknowledging & celebrating
our uniqueness.” The companion principle is: “We are all the leaves of one tree.”

Its geographical mandate is expansive: investigate every destination The Faire Wind can potentially reach,
including uninhabited islands, Antarctic research stations, reefs, small communities, remote rivers and historic
sites. A location must not disappear from discovery because a population-filtered gazetteer does not contain it.

The expedition therefore requires two complementary locally operated software systems. NERDS is the planning
and mission-control application used by the Captain and expedition team; 4nR-SURVEYOR is the independent AI
intelligence service that researches, reasons, coordinates specialist agents, proposes alternatives and improves its
methods through evidence and experience. Both applications have separate codebases and separately testable
responsibilities.



MISSION OBJECTIVES & DELIVERABLES
1.   1. Worldwide discovery — identify expedition-relevant places and their alternate names, coordinates,
     geographic relationships, provenance and practical research significance, regardless of population or
     remoteness.
2.   2. Mission-driven research — investigate destinations and their music, cuisine, people, histories, origins,
     languages, architecture, biology and ecology; connect findings across disciplines rather than deliver
     disconnected answers.
3.   3. Active voyage intelligence — support NERDS through CHEKOV with researched passage candidates, seasonal
     versus near-term environmental analysis, optional route comparisons and continuing reassessment when
     conditions change.
4.   4. Independent verification — NERDS remains the authoritative route-calculation, geographic validation,
     distance/time accounting and Captain-facing plotting system. SURVEYOR proposals are inputs to be checked,
     not executable navigation authority.
5.   5. Onboard local AI — run reasoning and specialist workflows primarily on AMD local compute through
     configurable inference runtimes, while retaining the two independent Starlink Maritime connections for
     retrieval, updates and wider services. Local AI is a chosen capability, not a claim that the ship lacks
     connectivity.
6.   6. Multidisciplinary specialisation — operate six configurable suites: CHEKOV, EMERSON, BOURDAIN,
     CHAKOTAY, GOODALL and HADID, sharing well-governed evidence and requesting other specialists when a
     subject crosses disciplines.

                                    4nR-SURVEYOR · Development Scope v2.4 · 16 October 2026


---


7.   7. Continuous improvement — identify failures and inferior performance, investigate root causes, change
     models/tools/workflows where warranted, retest against established methods and independent evidence, adopt
     demonstrated improvements and preserve rollback.
8.   8. Expedition science & stewardship — collect instrumented environmental and vessel-performance
     observations with timestamps, locations, units, provenance, calibration and quality metadata, enabling long-
     term analysis and appropriately governed public sharing.
9.   9. Reproducible engineering — deliver documented APIs, local model profiles, source-aware research records,
     automated benchmarks, deployment instructions and acceptance tests; distinguish implemented capabilities
     from development intentions.



SYSTEM RESPONSIBILITIES & OPERATING RELATIONSHIP
NERDS — Mission control: Captain-facing waypoint discovery and expedition projects; zoomable Cesium globe;
sourced vector geographic data; connected routing; independently verified route geometry, distances, durations,
ETAs and multimodal plans; persistent operation using its existing databases if SURVEYOR is unavailable.

4nR-SURVEYOR — Intelligence gatekeeper: accepts mission/research requests, interprets the task, delegates to
appropriate suites, selects and operates locally available models and tools, manages evidence, returns structured
findings and route proposals, performs quality assessment and coordinates learning. It is an independently
deployable application, not code embedded inside NERDS.

Specialist suites — Research disciplines: CHEKOV (navigation, metocean and route intelligence); EMERSON (music
and ethnomusicology); BOURDAIN (cuisine and foodways); CHAKOTAY (culture, history, archaeology,
anthropology, language, origins and communities); GOODALL (biology, ecology, oceanography, environment and
climate); HADID (architecture, geometry, structural principles, materials and built heritage). Each suite is a
configured collection of models, retrieval resources, specialist tools and tested workflows; a suite need not
correspond to a separately resident large language model.

AMD local compute — Infrastructure: provides the CPU/GPU/NPU and memory environment for local inference,
numerical processing and knowledge retrieval. Lemonade and Qwen3-30B-A3B are the initial baseline; additional
candidates and their statuses are documented later in this same specification.



END-TO-END EXAMPLE: CAPTAIN REQUESTS A DESTINATION
The Captain enters “Lay in a course for Saint Peter & Saint Paul Rocks” in NERDS. NERDS resolves the current
mission context and asks SURVEYOR to investigate. SURVEYOR delegates navigational research to CHEKOV and,
where relevant, engages GOODALL, CHAKOTAY or another specialist. CHEKOV returns sourced candidate corridors
and comparative assessments; NERDS checks the geographic connectivity and independently calculates routes,
distances, voyage time and unresolved sections. The Captain reviews credible choices and approves one. As
conditions change, SURVEYOR can propose a revision, but NERDS does not silently replace the approved course.

For a voyage six months away, analysis relies on climatology, seasonal patterns and qualified outlooks. For a
passage tomorrow, it uses time-valid forecasts and observations. Vessel suitability restrictions are a separate
ON/BYPASS advisory system during BETA, default BYPASS; the setting never permits routes across land or
fabricated connected waterways.



DOCUMENT AUTHORITY & READING ORDER
This is a single cumulative specification. The original 14 October v1.0 requirements, the v2 multi-agent design and
the v2.1–v2.2 model evaluations are all included below. Earlier version files are retained for history but are not
required to understand or implement this document. Later architectural decisions supersede conflicting earlier



                                4nR-SURVEYOR · Development Scope v2.4 · 16 October 2026


---


descriptions—for example, SURVEYOR is an independent application collaborating with NERDS, notwithstanding
an older v1.0 phrase describing the service as “within NERDS”.

Read the foundation requirements first, followed by the multi-agent architecture, model selection and the
candidate-status register. Candidate models are proposals for evaluation, not evidence of benchmarked operation,
licence clearance or implemented integrations.



How to read this specification
Start with the original system definition, research mission, configuration and classification framework. The
subsequent chapters extend this foundation into the six specialised AI suites, the NERDS integration contract, model
selection, evaluation and development acceptance tests. All essential requirements from the original v1.0 scope are
included below. v2.3 is the single controlling document; previous versions are revision history only.



System at a glance
4nR-SURVEYOR is a separate, locally operated AI research, orchestration and learning application for Faire Wind &
Song. It dispatches work to six specialist suites: CHEKOV (navigation), EMERSON (music), BOURDAIN (cuisine),
CHAKOTAY (human heritage), GOODALL (biology and environment), and HADID (architecture and engineering).
NERDS is the separate mission-control and mapping application: it requests intelligence from SURVEYOR,
independently validates geographic route proposals, and retains the authoritative voyage plan. The six suites may
share models, use specialist models and software tools, and maintain specialist knowledge while contributing to a
common evidence store.



I. PURPOSE, RESEARCH FOUNDATIONS & BASELINE REQUIREMENTS


1. Purpose & identity
4nR-SURVEYOR is the locally operated AI research intelligence within NERDS (Navigation & Expedition Research
Discovery Surveyor), supporting the Faire Wind & Song global expedition. NERDS is the host application; 4nR-
SURVEYOR is the agent; Qwen3 is the current foundation model; Lemonade is the current inference server. The
agent name is configurable, independent of the underlying model.

Mission statement: “Discovering & exploring our commonalities. Acknowledging & celebrating our uniqueness.”

Companion principle: “We are all the leaves of one tree.”

The agent investigates relationships among peoples, places, music, cuisine, history, languages, cultural practices,
environments & the routes that connect them. Its role is research, discovery, synthesis & source-aware
interpretation. NERDS remains the system of record for approved user preferences, projects, waypoints and
research findings.



2. Current verified technical baseline
 Component                                                  Observed / agreed state
                                                            NERDS Electron for Windows, v0.1.0 installed and tested;
 Application
                                                            private GitHub master: clarkgraff/NERDS
 Local hardware                                             GMKtec AMD Strix Halo, 128 GB unified memory
                                                            Unsloth Qwen3-30B-A3B-GGUF, Q4_0; downloaded, located
 Language model
                                                            and loaded
 Runtime                                                    Lemonade Server v2026.41.1; Llama.cpp ROCm installed



                                4nR-SURVEYOR · Development Scope v2.4 · 16 October 2026


---


    Local endpoint                                           http://127.0.0.1:13305/api/v1 (working NERDS configuration)
                                                             NERDS discovered the model and returned “NERDS
    Verified integration
                                                             CONNECTION SUCCESSFUL” from an end-to-end test prompt
                                                             Lemonade reported approximately 82 tokens/s and 0.97 s
    Observed inference                                       time to first token on one test; GPU/backend use during that
                                                             measurement not independently verified
                                                             Permanent 4nR-SURVEYOR system identity, production
    Not implemented                                          conversation interface, master SURVEYOR preferences,
                                                             autonomous route-driven investigations
Observed limitations: The current NERDS panel is a local-model connection/test interface. Model discovery and
simple prompt/response work. An earlier longer research prompt did not display a response; its cause is
undiagnosed. Do not treat a successful short test as proof that long-running or structured research workflows are
implemented.



3. Architectural principles
     Offline-first: local research and inference remain useful at sea without continuous connectivity.
     Store & Forward: acquire selected material when connected; index and reuse it offline. AI-CACHE (planned 8 TB
      NVMe) and AI-ARCHIVE (planned 80 TB usable RAID 6) are separate storage tiers.
     User-approved scope: natural-language research directives are interpreted into detailed proposals, never
      silently promoted to approved master preferences.
     A stable scholarly classification foundation underpins familiar user-facing labels and examples in parentheses.
     Data-driven SURVEYOR modules: classification trees, option descriptions, aliases, source references and
      approval states belong in structured configuration/data rather than separate hard-coded dialogs.
     Research outputs retain source provenance, geographical and temporal context; distinguish sourced evidence
      from inference.
     Research computation and downloads are bounded by master preferences; discovery of a topic does not itself
      authorise a deep investigation.
     4nR-SURVEYOR orchestrates research and supports navigation analysis; deterministic routing computations
      are separately testable software components.



4. Master SURVEYOR Preferences — approved V1 workflow
The expedition-wide natural-language RESEARCH DIRECTIVE replaces a broad checklist of active investigations as
the primary statement of research intent. The Faire Wind & Song mission statement supplies the initial foundation;
users may add paragraphs describing topical, regional and historical priorities.

    Stage                                                    Required behaviour
                                                             User writes/edits the natural-language expedition research
    1 — Directive
                                                             directive; store original text and revisions.
                                                             4nR-SURVEYOR proposes main disciplines, category
    2 — Interpretation                                       selections and detailed SUB-MENU OPTIONS across all
                                                             applicable frameworks.
                                                             Show complete proposed hierarchy, including categories,
    3 — Full review                                          subcategories and refinements; distinguish AI-proposed, user-
                                                             added and user-excluded items.
                                                             Left-click toggles whole category; right-click → OPTIONS
    4 — Interaction
                                                             opens detailed refinements. Multiple selections supported.
                                                             User edits, accepts or rejects proposals; only explicitly
    5 — Approval
                                                             approved configuration becomes active.
                                                             Save named master profiles with directive, full structured
    6 — Persistence
                                                             selections, approval metadata and revisions.
    7 — Inheritance                                          SURVEYOR- and WAYPOINT-level settings inherit master



                                 4nR-SURVEYOR · Development Scope v2.4 · 16 October 2026


---


                                                                defaults, with explicit local overrides.
                                                                Changing a directive creates a proposed diff
    8 — Revision                                                (additions/removals/refinements); preserve user decisions
                                                                until revised approval.
Cross-category search semantics: support REQUIRED / PREFERRED / ANY where relevant. Selecting a whole category
with no refinements means the complete selected category, rather than an empty or disabled query.



5. Route-driven discovery & investigation control
     When a route/waypoint is added or updated, NERDS can initiate a limited preliminary survey of approved
      SURVEYOR areas, prioritising already cached sources and data.
     4nR-SURVEYOR indexes candidate findings against classification IDs, place/region, relevant period, aliases and
      source links; it populates location-relevant selectors.
     Expose suggested discoveries without overwriting the stable MASTER CLASSIFICATION or APPROVED USER
      PREFERENCES.
     Present the user with relevant options to pursue, defer or dismiss; initiate deeper work according to approved
      preferences and resource limits.
     Make discoveries reusable across waypoints and disciplines (for example, Taíno foodways across CULTURE,
      CUISINE & HISTORY).
     Support a NEW DISCOVERIES inbox, with selected/deferred/dismissed state; this remains a proposed
      presentation detail pending implementation.
     Bound acquisition by geography, investigation depth, data budget, time budget and concurrency. Full bulk
      download of NOAA United States ENC charts is excluded from the current scope.



6. SURVEYOR user interface convention
Every module shares: a main category selector; formal or descriptive category name; readily recognised examples
in parentheses; right-click OPTIONS for hierarchical details; multi-select; saved selections; an optional custom-
interest text field; and discovery indicators for suggested refinements. The underlying taxonomy may cross formal
classification families when user familiarity requires it (for example KEYBOARD INSTRUMENTS in MUSIC).



7. Five approved V1 classification frameworks
7.1 MUSIC
Established research foundations: Hornbostel–Sachs / MIMO; Smithsonian Folkways; MusicBrainz; UNESCO
Intangible Cultural Heritage; RILM.

    Main selector                                               Illustrative refinements/examples
                                                                Traditional / folk, classical, jazz, blues, popular, ceremonial,
    GENRE & TRADITIONS
                                                                experimental; regional subgenres
    TIME PERIOD                                                 Historical era, century, decade, contemporary activity
                                                                Idiophones (bells, gongs, rattles, slit-log drums);
                                                                membranophones (bongos, congas, timpani); chordophones
    INSTRUMENTATION
                                                                (guitars, harps, musical bows); aerophones (flutes, horns,
                                                                conch shells); electrophones (synthesisers, theremins)
                                                                Pianos, pipe/Hammond organs, harpsichords, harmoniums,
    KEYBOARD INSTRUMENTS — cross-classification
                                                                synthesisers, celestas
                                                                Singing, chanting, throat singing, clapping, stamping, found
    VOCAL / BODY / OBJECT TRADITIONS
                                                                objects, water-based sound
                                                                Communities, regional names, diaspora, migration and local
    CULTURAL / ETHNIC ORIGINS
                                                                terminology



                                  4nR-SURVEYOR · Development Scope v2.4 · 16 October 2026


---


                                                              Solo/ensemble, dance, improvisation, metre, scale, musical
    PERFORMANCE & STRUCTURE
                                                              form
    LANGUAGE, FUNCTION & INFLUENCES                           Lyrics/dialects, ceremonies, work, protest, cultural exchange
                                                              Active performers, institutions, festivals, venues, teaching
    PEOPLE, EVENTS & LOCATIONS
                                                              traditions
Formal organological classification and familiar overlapping search groupings coexist; maintain canonical IDs plus
local-language names and aliases.

7.2 CUISINE
Research foundations: FoodOn; LanguaL; UNESCO Intangible Cultural Heritage. Sixteen V1 categories (the initial
fifteen plus culinary equipment & utensils):

     CULINARY TRADITIONS (regional, Indigenous, ancestral, diasporic, fusion)
     INGREDIENTS (vegetables, fruits, grains, meats, seafood, herbs, spices)
     COOKING METHODS (roasting, grilling, frying, steaming, smoking, fermenting)
     DISHES & FOOD TYPES (soups, stews, breads, dumplings, desserts)
     FLAVOURS & SEASONINGS (sweet, sour, salty, bitter, umami, spicy)
     FOOD PRESERVATION (curing, drying, pickling, fermenting)
     CULINARY HISTORY (trade routes, migration, historical foodways)
     CULTURAL / ETHNIC ORIGINS (communities, diaspora, regional peoples)
     FOOD PRODUCTION (farming, fishing, foraging, herding)
     DINING TRADITIONS (family meals, feasts, street food)
     BEVERAGES (tea, coffee, fermented drinks, spirits)
     CHEFS & FOOD ARTISANS (home cooks, bakers, fishers, producers)
     MARKETS & FOOD VENUES (markets, stalls, restaurants, farms)
     DIETARY TRADITIONS (vegetarian, halal, kosher, fasting)
     TIME PERIOD (ancient, medieval, colonial, industrial, contemporary)
     CULINARY EQUIPMENT & UTENSILS (tagines, tandoors, woks, grinding stones, steamers)

7.3 CULTURE
Research foundations: Yale HRAF / Outline of Cultural Materials; UNESCO Intangible Cultural Heritage; Getty Art &
Architecture Thesaurus. Seventeen V1 categories:

     PEOPLES & COMMUNITIES (Indigenous peoples, ethnic communities, diaspora)
     LANGUAGE & ORAL TRADITIONS (dialects, storytelling, folklore)
     CUSTOMS & SOCIAL PRACTICES (greetings, hospitality, gift-giving)
     FESTIVALS & CELEBRATIONS (carnivals, harvest festivals, parades)
     BELIEFS & SPIRITUALITY (religious, ancestral, sacred practices)
     RITUALS & RITES OF PASSAGE (births, weddings, funerals)
     FAMILY & SOCIAL ORGANISATION (kinship, leadership, social roles)
     CLOTHING & ADORNMENT (textiles, jewellery, body art)
     ARTS & CRAFTSMANSHIP (weaving, pottery, carving)
     DANCE & PERFORMANCE (traditional dance, theatre, puppetry)
     GAMES & RECREATION (traditional sports, board games)
     WORK & LIVELIHOODS (fishing, farming, trading)
     TRADITIONAL KNOWLEDGE (navigation, astronomy, ecological knowledge)
     HOMES & EVERYDAY LIFE (households, neighbourhood life)
     CULTURAL EXCHANGE & CHANGE (migration, blending, adaptation)
     COMMUNITY SPACES & GATHERINGS (markets, squares, meeting places)
     ANCIENT PEOPLES, CULTURES & CIVILISATIONS (Dorset, Denisovans, ancestral Taíno, Maya, etc.)




                                 4nR-SURVEYOR · Development Scope v2.4 · 16 October 2026


---


Ancient-peoples OPTIONS distinguish extinct human lineages, archaeological cultures, ancient civilisations,
historical peoples, Indigenous ancestral cultures, continuity/descendants, and disappearance/transformation.
Arawakan and Maya peoples have living descendants/communities; neither is labelled categorically extinct.

CULTURAL CONTEXT can refine living traditions, historical traditions, revival/preservation, contemporary
expression and cross-cultural connections. Preserve communities’ own names and terminology.

7.4 HISTORY
Approved V1 selectors: PREHISTORY & ARCHAEOLOGY; CIVILISATIONS & EMPIRES; EXPLORATION &
NAVIGATION; MIGRATION & SETTLEMENT; TRADE & ECONOMICS; CONFLICT & POLITICAL CHANGE; SCIENCE &
TECHNOLOGY; SOCIAL & CULTURAL HISTORY; SLAVERY & HUMAN DISPLACEMENT; BIOGRAPHIES & HISTORICAL
FIGURES; ENVIRONMENTAL HISTORY; MARITIME HISTORY; HISTORICAL PERIODS & CHRONOLOGY.

Representative examples include ancient settlements, Phoenicians/Romans/Maya, maritime trade routes, diaspora,
Atlantic forced migration, shipwrecks and historical periods. Candidate foundation resources: Library of Congress
Subject Headings, Getty TGN, Wikidata and PeriodO. Timeline presentation remains an open implementation detail.

7.5 ARCHITECTURE
Approved V1 selectors: ARCHITECTURAL STYLES; INDIGENOUS & VERNACULAR ARCHITECTURE; ANCIENT
STRUCTURES; RELIGIOUS & CEREMONIAL BUILDINGS; RESIDENTIAL ARCHITECTURE; CIVIC & PUBLIC BUILDINGS;
INDUSTRIAL & MARITIME STRUCTURES; ENGINEERING & INFRASTRUCTURE; CONSTRUCTION MATERIALS;
CONSTRUCTION TECHNIQUES; URBAN DESIGN & SETTLEMENTS; ARCHITECTS & CRAFTSPEOPLE; HERITAGE &
PRESERVATION; ENVIRONMENTAL ADAPTATION; ARCHITECTURAL PERIODS.

Examples: Gothic and Art Deco; longhouses and adobe dwellings; pyramids; mosques; markets; shipyards and
lighthouses; bridges, aqueducts and canals; masonry and timber framing. Candidate research foundations: Getty
AAT, UNESCO World Heritage, Arches and CIDOC CRM. Familiar cross-classification searches such as LIGHTHOUSES
must remain possible.



8. Four provisional modules — V1 scaffolding; refine in situ
    Module                                 Provisional selectors                     Candidate foundations
                                           Families, writing systems, dialects,
                                                                                     Glottolog, Ethnologue, ISO 639, UNESCO
    LANGUAGE & LINGUISTICS                 endangered languages, oral
                                                                                     language resources
                                           communication, etymology, migration
                                           Sites/excavations, artefacts, dating
                                           methods, prehistoric technology,          Getty AAT, CIDOC CRM, Archaeology
    ARCHAEOLOGY
                                           archaeological cultures, underwater       Data Service, Open Context
                                           archaeology
                                           Flora, fauna, ecosystems, biodiversity,   Catalogue of Life, GBIF, IUCN, Darwin
    NATURAL HISTORY
                                           evolution, geological history             Core
                                           Indigenous technologies, historical
                                           inventions, maritime engineering,
    SCIENCE & TECHNOLOGY                   astronomy, medicine, mathematics,         Library of Congress, UNESCO, Wikidata
                                           agriculture, transport, contemporary
                                           innovation
These modules are approved as provisional classification starting points, not fully researched taxonomies. Their
OPTIONS trees are to be refined during use, with explicit approval for changes to master settings.



9. Knowledge, retrieval & evidence
     Record an entity/topic once where possible, with stable internal ID, descriptive label, aliases, source references,
      associated classifications, time period and geographic footprint.



                                  4nR-SURVEYOR · Development Scope v2.4 · 16 October 2026


---


     Maintain three distinct layers: MASTER CLASSIFICATIONS (stable); DISCOVERED SUBJECTS (dynamic);
      APPROVED USER PREFERENCES (persistent).
     Build retrieval over the local research catalogue and original supporting documents; a vector index is a
      proposed technique, not yet an implemented requirement or chosen vendor.
     Retain source URL/identifier, organisation/author, retrieval date, licence/usage notes and evidence excerpts or
      references for claims.
     Cross-link relevant findings between MUSIC, CUISINE, CULTURE, HISTORY, ARCHITECTURE and provisional
      modules.
     Distinguish facts, disputed claims and inferred cultural relationships. Show source basis when user inspects a
      finding.
     Permit updates/corrections and de-duplicate repeat acquisitions; the archive is a durable research resource, not
      merely a chat history.



10. Relation to NERDS navigation & storage
NERDS controls ROUTE PLOT, WAYPOINTS, vessel preferences, route and time calculations, environmental layers,
media indexing and storage. 4nR-SURVEYOR uses waypoint positions, names and route context to scope
investigations; may assist in finding relevant maritime/environmental datasets; and surfaces findings
geographically. It does not replace the independently testable routing/navigation engine.

Mapping remains CesiumJS offline-first, with globe and Mercator views as planned. The Earth Nullschool open-
source visualization is a proposed source of MIT-licensed animation techniques for environmental overlays; retain
copyright and full licence when code is reused. Bulk acquisition of the NOAA US ENC database is explicitly deferred.
Acquire selected environmental and geographical data by region when required.



11. Credits, licensing & research foundations
Add ABOUT → CREDITS & LICENCES → RESEARCH FOUNDATIONS with clear distinctions between scholarly
inspiration, actual research/data sources and incorporated third-party software/data licences. Crediting inspiration
does not imply affiliation or endorsement. Check reuse terms before importing entire controlled vocabularies or
datasets.

    Area                                                      Attribution targets
                                                              Hornbostel–Sachs; MIMO; Smithsonian Folkways;
    MUSIC
                                                              MusicBrainz; UNESCO; RILM
    CUISINE                                                   FoodOn; LanguaL; UNESCO
    CULTURE                                                   Yale HRAF / Outline of Cultural Materials; UNESCO; Getty AAT
                                                              Library of Congress; Getty TGN; Wikidata; PeriodO
    HISTORY
                                                              (candidate)
                                                              Getty AAT; UNESCO World Heritage; Arches; CIDOC CRM
    ARCHITECTURE
                                                              (candidate)
                                                              Cameron Beccario / Earth Nullschool; MIT licence, copyright
    Environmental visualisation
                                                              and permission notice as required




12. Proposed implementation order & acceptance criteria
Implementation is not authorised merely by this document. Preserve the current unfinished Codex
waypoint/marine-routing task; reconcile any new work against the repository and current build first.

    Increment                                                 Minimum acceptance evidence
                                                              NERDS presents 4nR-SURVEYOR; submits persistent system
    A — Agent identity
                                                              instructions to Lemonade; can conduct a multi-turn



                                  4nR-SURVEYOR · Development Scope v2.4 · 16 October 2026


---


                                                              conversation; reopens saved conversation.
                                                              Natural-language directive produces structured proposed
    B — Master preferences                                    disciplines/categories/OPTIONS; complete hierarchy can be
                                                              reviewed and edited; no changes active until approval.
                                                              Approved master profile reloads; mission and waypoint
    C — Persistence/inheritance                               overrides persist; regenerated directive shows diffs and does
                                                              not erase user decisions.
                                                              A waypoint triggers bounded local-first discovery; sourced
    D — Route-driven discovery                                findings populate selectors; user may choose/defer/dismiss;
                                                              cross-module links retained.
                                                              Five approved frameworks and four provisional frameworks
    E — Nine-module catalogue                                 load from structured definitions; selectors and right-click
                                                              OPTIONS are functional.
                                                              Finding provenance is visible; research foundations and
    F — Source attribution                                    licences are accessible; bundled licences follow applicable
                                                              obligations.




13. Open engineering decisions — do not mistake for approvals
     Exact storage schema, index/search technology, embedding model and persistence format.
     Exact interaction layout for full nine-module preference review, NEW DISCOVERIES inbox and source/evidence
      panels.
     Research limits: time, bandwidth, data volume, concurrency, refresh periods and geographic radius.
     How NERDS handles model non-response, timeouts, streaming, cancellations and diagnostic logging.
     Exact long-running background workflow and job queue for online/offline Store & Forward acquisition.
     Detailed classification definitions and source reuse permissions for the four provisional modules.
     Current Codex working-tree contents and the final scope of the pending waypoint/marine-routing build.



14. Reference links
NERDS repository: https://github.com/clarkgraff/NERDS

FoodOn: https://foodon.org/ | https://github.com/FoodOntology/foodon

LanguaL: https://www.langual.org/

MusicBrainz API: https://musicbrainz.org/doc/MusicBrainz_API

UNESCO Intangible Cultural Heritage: https://ich.unesco.org/en/lists

HRAF Outline of Cultural Materials: https://hraf.yale.edu/resources/reference/outline-of-cultural-materials/

Getty AAT: https://www.getty.edu/research/tools/vocabularies/aat/

Earth Nullschool original source and licence: https://github.com/cambecc/earth |
https://github.com/cambecc/earth/blob/master/LICENSE.md

Glottolog: https://glottolog.org/ | GBIF: https://www.gbif.org/ | PeriodO: https://perio.do/

END OF V1 SCOPE — The document records the agreed design baseline and explicitly identifies provisional material
and unresolved implementation choices.




                                  4nR-SURVEYOR · Development Scope v2.4 · 16 October 2026


---


II. MULTI-AGENT SYSTEM ARCHITECTURE & OPERATIONS


1. Governing purpose & authority
4nR-SURVEYOR is an independently operable, locally hosted AI intelligence and orchestration platform serving
Faire Wind & Song, NERDS and authorised research clients. NERDS is the expedition mission-control application,
captain-facing interface and authoritative voyage state; 4nR-SURVEYOR is the AI gatekeeper directing six
specialised suites. Neither application is merged into the other. NERDS retains full core route-planning and project
operations when SURVEYOR is unavailable.

Architectural correction to v1.0: the v1.0 description of SURVEYOR as intelligence “within NERDS” means integrated
service relationship, NOT an embedded dependency or common codebase. The applications are independent
products joined by a versioned interface.

Human control: “We are driving the car, not getting run over by it.” The Captain and expedition team determine
objectives and approve consequential decisions; recommendations do not silently override approved voyage plans.



2. Approved six-suite roster
Suite                                  Principal responsibility                Specialist breadth

CHEKOV                                 Navigation & voyage intelligence        Geospatial routing; marine weather
                                                                               & currents; multi-objective
                                                                               alternatives; passage time/energy
                                                                               forecasts; observations; vessel-
                                                                               performance learning
EMERSON                                Music & ethnomusicology                 Instrument classification; musical
                                                                               history and communities; artist
                                                                               discovery; audio analysis;
                                                                               transcription; local traditions
BOURDAIN                               Cuisine & foodways                      Regional cuisines; culinary
                                                                               heritage; ingredients; food
                                                                               production; chefs; techniques; local
                                                                               producers and markets
CHAKOTAY                               Human heritage & cultural sciences      Culture; history; archaeology;
                                                                               anthropology; linguistics; origins;
                                                                               migration; contemporary
                                                                               communities; biological
                                                                               anthropology in cooperation with
                                                                               GOODALL
GOODALL                                Biology & environmental sciences        Biology; marine biology; botany;
                                                                               zoology; microbiology; biodiversity;
                                                                               ecosystems; oceanography;
                                                                               conservation; climate and
                                                                               environmental observations
HADID                                  Architecture & engineering              Built heritage; architectural history;
                                                                               geometry; structural principles;
                                                                               materials; traditional construction;
                                                                               engineering and preservation

Suites are agent/workflow domains, not necessarily individual language-model instances. They can share a
foundation model, use individual specialist models or combine numerical tools with inference. Each suite has
independent configuration, permissions, indexes, tests and improvement records.


                                4nR-SURVEYOR · Development Scope v2.4 · 16 October 2026


---


v1.0 category taxonomies remain intact. V1 MUSIC maps to EMERSON; CUISINE to BOURDAIN; CULTURE, HISTORY,
LANGUAGE & LINGUISTICS and ARCHAEOLOGY to CHAKOTAY; ARCHITECTURE to HADID; NATURAL HISTORY and
environmental biology to GOODALL. Cross-disciplinary classifications and the v1 SCIENCE & TECHNOLOGY
provisional module remain searchable; SURVEYOR dispatches such investigations to suitable suites without
removing or reducing any existing selector.



3. SURVEYOR core services
Service                                                    Required responsibilities

Mission dispatcher                                         Accept structured research/expedition requests;
                                                           interpret scope; break work into dependencies;
                                                           determine which suites participate.
Orchestrator                                               Assign tasks, coordinate cross-suite research, reconcile
                                                           overlaps and contradictions; bounded retries;
                                                           cancellation and durable checkpoints.
Model manager                                              Per-suite configurable reasoning, audio, vision,
                                                           embedding, forecasting and specialist models; backend
                                                           independence; lifecycle, caching and fallback.
Tool manager                                               Controlled access to geospatial processing, numerical
                                                           solvers, document acquisition, audio analysis,
                                                           environmental and research APIs.
Evidence & knowledge manager                               Canonical entities; source provenance; specialist
                                                           indexes; common relationships; uncertainty, disputes
                                                           and access/usage rights.
Evaluation & learning engine                               Benchmark outcomes, diagnose failures, run candidate
                                                           improvements and adopt only verified gains, with
                                                           versioning and rollback.
Resource scheduler                                         Prioritise navigation-critical tasks; bound concurrency,
                                                           CPU/GPU, memory, time, power and connectivity use.
Observations service                                       Ingest timestamped vessel and environmental
                                                           telemetry, maintain raw data, quality flags, calibration
                                                           and analysis products.
NERDS integration adapter                                  Versioned bidirectional messages,
                                                           authentication/permissions, job status, results,
                                                           diagnostics, import and independent revalidation.




4. Agent configuration & specialised models
   Each suite maintains an editable model profile: primary reasoning model; optional specialist models; fallback;
    inference backend; quantisation; context limits; structured-output rules; resource and runtime limits.
   Each suite maintains a separate tool policy, specialist sources/indexes, skills/workflows, benchmark corpus and
    experiment history.
   Model selection is replaceable without rebuilding NERDS or SURVEYOR. The platform may share one resident
    model across suites and load specialist models on demand.
   Baseline development environment: AMD Ryzen AI Max / Strix Halo-class local hardware, Lemonade server
    and Qwen3-30B-A3B family as specified in v1.0. These are initial selections, not architectural lock-in.
   Task execution must be locally operable. Starlink Maritime connectivity is available aboard The Faire Wind
    through two independent setups; remote services and data acquisition are complementary capabilities, not
    prerequisites for routine local research.

                                4nR-SURVEYOR · Development Scope v2.4 · 16 October 2026


---


5. Shared knowledge, evidence & research governance
Use a hybrid knowledge system: canonical shared identities for places, people, groups, events, time periods,
scientific observations and source records; domain-specific specialist indexes for the six suites; durable original
evidence with exact source and licence metadata. An Amazonian community is one place identity with music,
cuisine, language, history, architecture and biodiversity relationships, not six competing records.

   Preserve all v1.0 MASTER CLASSIFICATIONS, DISCOVERED SUBJECTS and APPROVED USER PREFERENCES as
    distinct layers, including approval and inheritance rules.
   An agent may propose changes to the master research directive or classifications; only approved modifications
    enter master settings.
   Claims must distinguish measured observations, sourced documents, scholarly interpretations, contested
    accounts and AI inference.
   Cross-suite collaboration carries citations, provenance, dates, geographic scope, evidence confidence and any
    disagreement into the final research package.
   Background research and acquisitions remain bounded by approved geographic, depth, bandwidth, time,
    storage and concurrency limits; deferred tasks persist.



6. CHEKOV — intelligent navigation & Captain’s route selection
NERDS receives the Captain’s destination and voyage priorities, issues a structured planning request to SURVEYOR,
and SURVEYOR dispatches CHEKOV with supporting tools and agents. CHEKOV proposes up to TEN genuinely
distinct candidate passages (fewer when evidence supports fewer). NERDS independently validates vector
connectivity, calculates the actual route geometry, distance, duration, energy estimates where supported and
identifies unknowns. The Captain compares candidates and approves the authoritative route.

Balanced Passage is multi-objective, weighing time, distance, weather, sea state, prevailing winds, currents, energy,
navigational complexity and expedition priorities. Hard geographic connectivity is always enforced. Vessel
suitability is a separate ON/BYPASS user preference, with BETA default BYPASS; enabling ON initially supplies
advisories without rejecting valid geographic geometry. No arbitrary offshore access substitutions, invented links
or route lines crossing land.

   The Captain can request up to ten alternatives; each displays provenance, geometric verification result, NM,
    timing/uncertainty, weather basis, energy assumptions and reason for ranking.
   Six-month planning uses seasonal climatology, historical distributions and probabilistic outlooks; near-term
    routing uses time-valid marine forecasts and observations; underway analysis uses updated data and
    telemetry.
   NERDS verifies CHEKOV outputs with its independently testable vector graph and numerical methods. A
    rejected proposal returns structured diagnostics for further research and revision.
   CHEKOV may evaluate AI-generated routes against established routing tools. Underperformance requires WHY
    analysis—data, assumptions, forecast, algorithms or workflows—then proposed improvements, repeatable
    retesting and measured promotion.
   The selected route remains under Captain control. Active monitoring can propose changes promptly; it cannot
    silently replace the authorised route or directly command steering/propulsion.
   NERDS retains vector-first routing and a geographically accurate zoomable Cesium globe showing waypoints
    and route polylines; accuracy outranks decorative imagery.



7. Learning & method improvement
Operational learning is explicit engineering work, not merely accumulating chat histories. Every suite shall
preserve task inputs, sources, chosen models/tools, outputs, verification, measured outcomes, failure details and



                                 4nR-SURVEYOR · Development Scope v2.4 · 16 October 2026


---


reasons for revisions. The learning cycle is EXECUTE → MEASURE → INVESTIGATE WHY → EXPERIMENT → RETEST
→ ADOPT OR REJECT → MONITOR.

SURVEYOR shall have the ability to investigate why an AI technique fails to exceed an established benchmark,
formulate a new workflow or computational approach, test it against held-out and regression cases and retain
proven improvements with rollback. Learning may change retrieval, prompts, algorithms, model choice,
calibration or ultimately model weights where data justify training. Unverified self-modification is not promoted to
production.



8. Observational science & open knowledge ambitions
The Faire Wind expedition should collect relevant weather, water and vessel operational observations wherever
instrumentation allows: timestamped WGS84 position, course/speed, winds, pressure, temperature, humidity,
waves, currents, water temperature/salinity as available, energy systems, propulsion and deviations from forecasts.
GOODALL manages biological/environmental scientific analysis; CHEKOV uses navigation-relevant observations;
SURVEYOR maintains long-term evidence and quality management.

Retain original measurements, calibration metadata, equipment details, timestamps, location, quality flags and
derived estimates separately. Investigate openly sharing eligible observation datasets and potentially distributing a
free maritime intelligence/navigation product in the future. Public release is subject to data licences, consent,
privacy, provenance and research quality.



9. Bidirectional API contract
Type                                    Direction                               Meaning

MissionRequest                          NERDS → SURVEYOR                        Destination, objectives, departure
                                                                                window, mandatory stops,
                                                                                authorised research scope and
                                                                                constraints.
TaskPlan / TaskProgress                 SURVEYOR → NERDS                        Agent assignments; progress;
                                                                                bounded execution; cancel/resume;
                                                                                completion states.
ResearchFinding                         SURVEYOR → NERDS                        Structured claims, identifiers,
                                                                                source links, classifications,
                                                                                temporal/geographic context.
RouteCandidateSet                       SURVEYOR/CHEKOV → NERDS                 Candidate waypoint corridors;
                                                                                coordinates; forecast assumptions;
                                                                                ranks and evidence.
RouteValidationFeedback                 NERDS → SURVEYOR                        Per-segment acceptance/rejection,
                                                                                geometry diagnostics, independent
                                                                                computations and unresolved
                                                                                evidence.
ObservationBatch                        NERDS / instruments → SURVEYOR          Raw and quality-tagged
                                                                                vessel/weather/water
                                                                                measurements.
ImprovementProposal                     SURVEYOR → reviewer/NERDS               Proposed updated method,
                                                                                evidence, benchmark comparison,
                                                                                change/rollback record.
KnowledgePackage                        SURVEYOR → NERDS                        Versioned, signed or checksummed
                                                                                import bundle; de-duplicable


                                4nR-SURVEYOR · Development Scope v2.4 · 16 October 2026


---


                                                                              geographic intelligence.

Define schema versions, request/job IDs, timestamps in UTC, idempotency keys, source IDs, input/output hashes,
typed error states, task deadlines, cancel/resume, security/permissions, offline queueing and machine-readable
validation feedback. Store large artefacts by content-addressed reference. Support operation on one Windows host
or on separate onboard LAN computers.



10. Independent NERDS operational boundary
   NERDS owns the Captain UI, authoritative project and expedition state, waypoints, vector geographic store,
    route validation and numerical calculations, CesiumJS globe and presentation.
   NERDS must perform established geographic routing and save/open projects with SURVEYOR stopped or
    unavailable.
   SURVEYOR owns AI investigation, cross-suite coordination, model execution, evidence acquisition,
    environmental interpretation and validated learning pipelines.
   CHEKOV may propose intelligent route alternatives; NERDS independently verifies and records the Captain-
    approved result. Each can use specialist numerical tools without duplicating the authoritative geometry state.
   Do not merge NERDS_CODEX, NERDS_COPILOT and the separately developed 4nR-SURVEYOR repositories.



11. Development increments & acceptance tests
Increment                                                 Minimum demonstrable acceptance

A — Core service                                          Standalone SURVEYOR starts locally; registers suites;
                                                          calls Lemonade; creates durable jobs; can
                                                          cancel/resume; returns structured source-aware
                                                          response.
B — Six suites                                            Each named suite can execute relevant tasks with
                                                          configurable tool/model profile and own tests; cross-
                                                          suite three-agent task completes.
C — Knowledge                                             Canonical entity record shared across three suites,
                                                          with preserved evidence provenance and independent
                                                          indexes; master approvals remain untouched.
D — CHEKOV integration                                    SURVEYOR sends multiple route candidates and NERDS
                                                          rechecks vector geometry, accounts for
                                                          valid/unresolved legs and compares against
                                                          conventional methods.
E — Continuous learning                                   One deliberately failing approach is diagnosed,
                                                          redesigned, independently benchmarked and either
                                                          accepted with evidence or rejected.
F — Environment                                           Timestamped sensor sample ingest,
                                                          provenance/quality flags, storage of raw versus
                                                          derived values and collaboration of GOODALL with
                                                          CHEKOV.
G — Persistence & security                                Restart preserves jobs/settings/history; local access
                                                          control; bounded resources; offline operations; no
                                                          changes to NERDS master preferences without
                                                          approval.
H — Regression & release                                  Repeatable tests and audit reports; no unresolved tests
                                                          counted as passes; no MSI or deployment until
                                                          explicitly authorised.


                               4nR-SURVEYOR · Development Scope v2.4 · 16 October 2026


---


12. Engineering decisions to resolve during implementation
   Programming language/runtime and process isolation; exact Lemonade adapter and model inventory;
    schema/transport and authentication.
   Which domain tools and models are used in each suite, and objective benchmark datasets for their selection.
   Spatial data validation, scientific data licences, observation instruments and sharing permissions.
   Priority queues, timeouts, resource budgeting, concurrency, source sync and failure recovery.
   Shared-knowledge persistence/semantic search/graph choices and migration from existing v1 records.
   Exact Captain candidate-comparison UI and bidirectional route-feedback UX.



Relationship to the original scope & requirements preservation
Part II below is the COMPLETE October 14 v1.0 design baseline reproduced as its original Word document body,
including all tables and selectors. This is intentional: v2.0 adds central orchestration, six agent suites, independent
deployment, CHEKOV route intelligence and explicit learning without losing detailed research taxonomy, user
preferences, source lists, data/storage assumptions or provisional modules. In a conflict, the explicit v2.0
amendment governs; otherwise v1.0 remains in force. V1 implementation observations are historical baseline facts,
not necessarily the current NERDS/Codex implementation status.




                                 4nR-SURVEYOR · Development Scope v2.4 · 16 October 2026


---


III. SPECIALIST MODEL SELECTION & EVALUATION


A. Shared baseline & model-selection policy
Initial common reasoning baseline: Qwen3-30B-A3B through Lemonade on an AMD Ryzen AI Max / Strix Halo-class
development platform. Each suite may use this shared reasoning model, a separately loaded specialist model, and
deterministic computational tools. SURVEYOR is the model gatekeeper: selects capabilities by task, schedules
memory and compute resources, records inference provenance, and compares model performance against an
established baseline.

A model is not approved merely because it runs or appears convincing. For every candidate, record the exact
checkpoint and quantisation, licence and intended-use restrictions, inference runtime, memory demand, load time,
tokens/sec or task throughput, energy/power where measurable, response latency, benchmark accuracy, error
patterns, operating requirements, and reproducible inputs. Avoid simultaneous loading of all specialist models by
default.



B. Initial six-suite candidate matrix
 SUITE                        PRIMARY REASONING               SPECIALIST CANDIDATES             EVALUATION PRIORITY

 CHEKOV                       Qwen3-30B-A3B                   Microsoft Aurora                  Route feasibility and geodesic
                              (reasoning/orchestration)       (experimental weather/wave        reproducibility; forecast skill
                                                              prediction); calibrated vessel-   versus reputable forecasts;
                                                              performance models;               ETA/energy forecast error;
                                                              deterministic vector/graph        seasonal vs next-day horizon
                                                              routing

 EMERSON                      Qwen3-30B-A3B                   Whisper large-v3-turbo            Transcription error by
                              (ethnomusicology/research)      (speech transcription); Music     language, instrument/timbre
                                                              Flamingo (research-only           recognition, music-caption
                                                              evaluation candidate); audio      accuracy, cultural-source
                                                              embeddings/signal analysis        quality; review model licence
                                                                                                before use

 BOURDAIN                     Qwen3-30B-A3B (culinary         Qwen3-VL-8B-Instruct              Ingredient identification on
                              research)                       (ingredients/food images);        representative field images;
                                                              Whisper large-v3-turbo            recipe/technique factuality;
                                                              (interviews); multilingual        translation fidelity; source
                                                              embeddings                        provenance

 CHAKOTAY                     Qwen3-30B-A3B                   Qwen3-VL-8B-Instruct              Multilingual retrieval quality,
                              (history/anthropology/linguis   (historic                         citation accuracy,
                              tics)                           manuscripts/artefacts);           chronological/identity
                                                              Qwen3-Embedding-0.6B or           disambiguation; oral-history
                                                              4B + reranker; Whisper large-     transcription; uncertainty
                                                              v3-turbo                          representation

 GOODALL                      Qwen3-30B-A3B (scientific       Microsoft Aurora                  Species identification
                              synthesis)                      (weather/ocean waves;             precision, observation-vs-
                                                              research evaluation); Qwen3-      inference separation,
                                                              VL-8B-Instruct (field images);    forecast skill, sensor quality-
                                                              time-series anomaly               control and time-series
                                                              detection/forecasting models      anomaly rates

 HADID                        Qwen3-30B-A3B                   Qwen3-VL-8B-Instruct              Image-to-feature recognition,
                              (architecture/materials         (buildings/plans/images);         construction-method
                              research)                       CAD/BIM/geometry                  verification, diagram
                                                              inspection tools; multilingual    interpretation, geometry
                                                              retrieval                         integrity; engineering claims
                                                                                                independently checked

Suite operational requirements (from the preceding matrix):

                               4nR-SURVEYOR · Development Scope v2.4 · 16 October 2026


---


   CHEKOV — Weather-route research, alternative corridors, forecast comparison, uncertainty, vessel-specific
    learning.
   EMERSON — Multilingual artist research, music/audio description, transcription, instruments, musical
    connections.
   BOURDAIN — Ingredients, techniques, regional foodways, producer research, menu and visual interpretation.
   CHAKOTAY — Cultural history, communities, archaeology, languages, oral histories, origins and migration.
   GOODALL — Biology, botany, zoology, marine ecosystems, conservation, climate/oceanographic observations.
   HADID — Architectural history, built heritage, materials, construction methods, spatial/structural analysis.



C. Runtime classes, compatibility & licence gates
   CLASS 1 — Lemonade-first GGUF/llama.cpp inference. Start with the existing Qwen3-30B-A3B model and
    compatible supported checkpoints. Confirm exact model identifier and quantisation on the installed Lemonade
    release; the public model catalogue changes over time.
   CLASS 2 — Multimodal vision and transcription. Evaluate Qwen3-VL-8B-Instruct and Whisper large-v3-turbo
    where the chosen local backend supports the exact model and its preprocessing; otherwise isolate these
    services behind SURVEYOR adapters rather than assume Lemonade support.
   CLASS 3 — Specialist scientific/audio models. Aurora and Music Flamingo are research/evaluation candidates
    with their own runtimes, input pipelines and usage constraints; do not assume they execute through Lemonade
    or are appropriate for unrestricted commercial deployment. For Music Flamingo, the checked release identifies
    non-commercial research use, and Aurora documentation notes non-academic usage concerns: confirm terms
    and obtain permissions as needed before deployment.
   CLASS 4 — Retrieval. Pilot Qwen3-Embedding-0.6B for compact multilingual indexing, compare 4B on difficult
    retrieval, and add a reranker if measurable. Do not replace source citations with embedding similarity scores.
   CLASS 5 — Deterministic engines. Geodesy, connected vector topology, routing graph validation, energy
    accounting, CAD geometry and sensor calibration remain numerical computations used by agents. SURVEYOR
    may generate proposals and investigate failures; NERDS independently verifies course geometry and passage
    accounting.



D. Selection, experimentation & continuous learning contract
10. Each suite registers capabilities and one or more model profiles: model ID, version/checkpoint hash, licence,
    local runtime URL/adapter, context and quantisation, resource ceilings, tool permissions, specialist data
    indexes, benchmark profile, fallback profile and configuration revision.
11. On every task SURVEYOR selects an eligible model and records why. A task may invoke several specialists
    sequentially: for example, EMERSON transcribes an interview, analyses a recording and sends its sourced
    cultural context to CHAKOTAY.
12. Run benchmark datasets before adopting a model or model update. Maintain domain-specific holdout tests and
    production-like tasks. Compare with existing best methods, investigate where an AI workflow falls short, revise
    tools/prompts/models and retest. Record failure investigations as first-class evidence.
13. Promotion to operational use requires benchmark evidence, licence approval, offline/restart success,
    reproducibility, recoverable fallbacks and rollback. The six suites are not automatically authorised to update
    their own production model weights or routing algorithms.
14. Capacity planning must measure actual installed AMD system memory, concurrent model footprint and
    throughput. Schedule inference according to operational priority: CHEKOV time-sensitive route investigation
    ahead of background research, without silently discarding queued work.




                                4nR-SURVEYOR · Development Scope v2.4 · 16 October 2026


---


E. Development acceptance tests for this addendum
15. For each of the six suites, at least one primary model profile and one documented specialist-model evaluation
    plan exist; absent specialist runtimes are reported explicitly.
16. For each model candidate, the source URL, version, licence, local runtime compatibility, resource envelope and
    representative benchmarking method are recorded.
17. SURVEYOR routes a representative task to each of six suites and preserves task-level model provenance and
    source citations.
18. SURVEYOR demonstrates at least one cross-suite task, fallback after unavailable specialist model, priority
    scheduling and clean model unload/reload.
19. The learning engine demonstrates diagnosis, experiment, retest, comparative evidence, guarded adoption and
    rollback using a known failed baseline.
20. NERDS remains independent and can verify CHEKOV route geometry without trusting AI-generated distances
    or asserted waterway connections.



F. Candidate reference sources & verification
   Lemonade official model catalogue — https://lemonade-server.ai/docs/models.html
   Lemonade per-model backend configuration —
    https://github.com/lemonade-sdk/lemonade/blob/main/docs/api/lemonade.md
   Qwen3-VL-8B-Instruct model card — https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct
   Qwen3-Embedding-0.6B model card — https://huggingface.co/Qwen/Qwen3-Embedding-0.6B
   Qwen3 embedding/reranking series — https://qwenlm.github.io/blog/qwen3-embedding/
   Microsoft Aurora official repository — https://github.com/microsoft/aurora
   Microsoft Aurora research and usage information — https://www.microsoft.com/en-us/research/project/aurora-
    forecasting/faq/
   Music Flamingo model card and usage terms — https://huggingface.co/nvidia/music-flamingo-hf
   Music Flamingo updated research documentation —
    https://huggingface.co/docs/transformers/model_doc/musicflamingo



IV. COMPLETE MODEL CANDIDATE REGISTER


A. Candidate-status definitions
   ACTIVE BASELINE — Designated starting configuration already specified by the project; exact installed
    checkpoint and runtime must be verified.
   PRIORITY EVALUATION — High-value next candidate; no completed suite-specific benchmark is claimed.
   SECONDARY EVALUATION — Plausible alternative or specialist option awaiting comparison, runtime
    assessment, or evidence.
   RESEARCH ONLY / LICENCE GATE — Restrict to research until licensing, commercial use and integration
    requirements are explicitly resolved.
   FUTURE / DATA GATE — Useful capability but lacks validated task data, compatible instrumentation, training
    data or runtime.
   DETERMINISTIC REFERENCE — Established algorithm or external authoritative data product, used as
    benchmark or tool rather than a language model.




                                4nR-SURVEYOR · Development Scope v2.4 · 16 October 2026


---


B. Central 4nR-SURVEYOR — orchestrator model candidates
Candidate                   Status                         Role                           Why / adoption gate

Qwen3-30B-A3B               ACTIVE BASELINE                General reasoning, tool        Initial Lemonade / AMD
                                                           calling, request               target; validate installed
                                                           decomposition, six-suite       quantisation, context
                                                           coordination                   length, JSON reliability,
                                                                                          throughput and memory
                                                                                          footprint.
Qwen3-8B                    PRIORITY EVALUATION            Low-latency dispatch,          Compare task routing,
                                                           classification, summaries,     tool selection and
                                                           fallback                       structured output against
                                                                                          30B-A3B; check exact
                                                                                          Lemonade support.
Qwen3-32B                   SECONDARY                      Dense reasoning                Compare reasoning
                            EVALUATION                     reference for difficult        quality against MoE
                                                           cross-disciplinary             baseline at available
                                                           synthesis                      unified-memory and
                                                                                          power budgets.
Mistral Small 3.1 24B       SECONDARY                      Alternative general-           Independent model-
Instruct                    EVALUATION                     purpose agent                  family comparator; exact
                                                           orchestration and              licence, variant, GGUF
                                                           multimodal reasoning           and Lemonade
                                                                                          compatibility need
                                                                                          confirmation.
Gemma 3 27B IT              SECONDARY                      Multilingual / multimodal      Alternative family to
                            EVALUATION                     comparative reasoning          reduce single-model bias;
                                                                                          confirm licence terms and
                                                                                          hardware performance.
Qwen3-Embedding-0.6B /      PRIORITY EVALUATION            Shared multilingual            Dedicated embedding
4B                                                         retrieval; small/large         service, not the decision-
                                                           accuracy-throughput            making orchestrator;
                                                           comparison                     evaluate cross-domain
                                                                                          recall.
Qwen3-Reranker-0.6B /       PRIORITY EVALUATION            Evidence reranking for         Measure top-k evidence
4B                                                         provenance-grounded            precision and latency;
                                                           synthesis                      adapter and availability
                                                                                          must be verified.
Cross-encoder / classical   DETERMINISTIC                  Search precision baseline,     Use SQLite FTS and
retrieval baseline          REFERENCE                      source retrieval and           deterministic filters; do
                                                           indexing                       not make embedding-only
                                                                                          retrieval a requirement.




C. CHEKOV — navigation, metocean & voyage optimisation
Candidate / tool                       Status                                  Why considered / gate

Qwen3-30B-A3B                          ACTIVE BASELINE                         Route strategy reasoning and query
                                                                               orchestration; NERDS must
                                                                               independently verify geometry and
                                                                               calculations.
Microsoft Aurora / Aurora 1.5          PRIORITY EVALUATION · LICENCE           Scientific weather/ocean-wave


                                4nR-SURVEYOR · Development Scope v2.4 · 16 October 2026


---


                                          GATE                                    inference, ensemble and horizon
                                                                                  research; separate PyTorch
                                                                                  runtime, required meteorological
                                                                                  inputs; operational/commercial
                                                                                  conditions need review.
ECMWF IFS / ERA5; NOAA GFS /              DETERMINISTIC REFERENCE                 Authoritative forecasts, reanalysis
GEFS / WW3                                                                        and wave-data comparison;
                                                                                  validate resolution, valid time,
                                                                                  acquisition terms and offline cache.
GraphHopper / OSRM-class                  DETERMINISTIC REFERENCE                 Graph topology, A*/Dijkstra,
routing algorithms; native vector                                                 geodesic distance and constrained-
graph & geodesic solvers                                                          waterway tests; not AI models.
XGBoost / LightGBM vessel-                FUTURE / DATA GATE                      Learn vessel-specific SOG, passage
performance predictor                                                             time and energy residuals from
                                                                                  measured voyages; held-out
                                                                                  validation mandatory.
Time-series foundation                    SECONDARY EVALUATION                    Potential onboard environmental /
forecaster (Chronos-2 candidate)                                                  equipment time-series baseline;
                                                                                  suitability and availability to be
                                                                                  verified.




D. EMERSON — audio, music & ethnomusicology
Candidate                                 Status                                  Why considered / gate

Qwen3-30B-A3B                             ACTIVE BASELINE                         Artist/instrument research,
                                                                                  multilingual context, provenance-
                                                                                  linked synthesis.
Whisper large-v3-turbo / large-v3         PRIORITY EVALUATION                     Interviews, oral history and lyrics
                                                                                  transcription; compare language,
                                                                                  dialect and music-background
                                                                                  accuracy; distinct audio runtime.
Music Flamingo (NVIDIA)                   RESEARCH ONLY / LICENCE GATE            Music understanding/reasoning;
                                                                                  released model identifies non-
                                                                                  commercial research restrictions,
                                                                                  so not approved for FWaS
                                                                                  commercial deployment.
CLAP (audio-text embeddings)              PRIORITY EVALUATION                     Audio search, tagging and
                                                                                  instrument/sound retrieval;
                                                                                  measure region-specific bias and
                                                                                  retrieval precision.
Basic Pitch / librosa / Essentia          SECONDARY EVALUATION                    Pitch, tempo and spectral feature
                                                                                  analysis; deterministic DSP plus
                                                                                  model-assisted tasks; research
                                                                                  accuracy and licences.
Demucs / source separation                SECONDARY EVALUATION                    Multitrack/stem isolation for
                                                                                  research workflow; check model
                                                                                  checkpoint licence and audio
                                                                                  fidelity.




                                   4nR-SURVEYOR · Development Scope v2.4 · 16 October 2026


---


E. BOURDAIN — cuisine & foodways
Candidate                             Status                                  Why considered / gate

Qwen3-30B-A3B                         ACTIVE BASELINE                         Multilingual regional cuisine
                                                                              research and source reconciliation.
Qwen3-VL-8B-Instruct                  PRIORITY EVALUATION                     Ingredient, dish and preparation-
                                                                              image reasoning; local multimodal
                                                                              runtime and independent visual
                                                                              tests required.
Gemma 3 12B / 27B IT                  SECONDARY EVALUATION                    Cross-family vision/multilingual
                                                                              comparison; candidate checkpoint
                                                                              & runtime review.
Qwen3-Embedding / Reranker            PRIORITY EVALUATION                     Retrieve terms, recipes, food
                                                                              history and multilingual aliases
                                                                              from evidence archives.
FoodOn + LanguaL ontologies           DETERMINISTIC REFERENCE                 Structured food terminology and
                                                                              classification, not predictive AI;
                                                                              source mapping and licences.




F. CHAKOTAY — culture, history, archaeology, linguistics & human heritage
Candidate                             Status                                  Why considered / gate

Qwen3-30B-A3B                         ACTIVE BASELINE                         Cross-disciplinary reasoning and
                                                                              multilingual historical research.
Qwen3-VL-8B-Instruct                  PRIORITY EVALUATION                     Maps, manuscripts, historical
                                                                              imagery and archaeological
                                                                              context; not standalone artefact
                                                                              authentication.
Qwen3-Embedding-0.6B / 4B +           PRIORITY EVALUATION                     Cross-language source matching
Reranker                                                                      and canonical people/place/event
                                                                              research.
Whisper large-v3-turbo                SECONDARY EVALUATION                    Oral histories, dialect
                                                                              documentation and spoken-
                                                                              language research; transcription
                                                                              review required.
NLLB-200 / MADLAD-400                 SECONDARY EVALUATION                    Low-resource multilingual
translation                                                                   translation comparator; per-
                                                                              language benchmarks & licence
                                                                              review.
Glottolog / PeriodO / HRAF /          DETERMINISTIC REFERENCE                 Language, chronology, culture and
UNESCO sources                                                                intangible-heritage authority
                                                                              mapping; access and reuse policies
                                                                              apply.




G. GOODALL — biology, ecology, environment & climate
Candidate                             Status                                  Why considered / gate

Qwen3-30B-A3B                         ACTIVE BASELINE                         Literature synthesis, ecological
                                                                              research planning and scientific


                               4nR-SURVEYOR · Development Scope v2.4 · 16 October 2026


---


                                                                               evidence reconciliation.
Microsoft Aurora / Aurora 1.5          PRIORITY EVALUATION · LICENCE           Weather, wave and Earth-system
                                       GATE                                    evaluation; shared CHEKOV model
                                                                               services, scientific domain
                                                                               validation and operational
                                                                               licensing review.
NASA/IBM Prithvi-EO-2.0                SECONDARY EVALUATION                    Earth-observation representation
                                                                               for land-cover/environmental
                                                                               change; satellite imagery and
                                                                               geospatial input requirements.
BioCLIP / iNaturalist computer         SECONDARY EVALUATION                    Biodiversity image retrieval and
vision family                                                                  species-assistance; avoid
                                                                               unwarranted species certainty;
                                                                               taxonomy verification.
BirdNET                                SECONDARY EVALUATION                    Bird acoustic identification, with
                                                                               instrument and geographic
                                                                               benchmarks; licence review.
XGBoost / time-series anomaly          FUTURE / DATA GATE                      Weather/water/vessel observations
detection                                                                      and anomaly monitoring; requires
                                                                               calibrated longitudinal sensor data.
GBIF / WoRMS / NOAA /                  DETERMINISTIC REFERENCE                 Taxonomy, marine species and
Copernicus datasets                                                            climate/ocean observations;
                                                                               provenance and download/access
                                                                               policy.




H. HADID — architecture, geometry & engineering
Candidate                              Status                                  Why considered / gate

Qwen3-30B-A3B                          ACTIVE BASELINE                         Architectural history, engineering
                                                                               concepts, sources and materials
                                                                               research.
Qwen3-VL-8B-Instruct                   PRIORITY EVALUATION                     Built-environment visual analysis
                                                                               and diagram interpretation;
                                                                               geometry verification required.
Segment Anything family (SAM 2 /       SECONDARY EVALUATION                    Image segmentation of
later checkpoints)                                                             architectural components and
                                                                               deterioration; specific model
                                                                               versions, licence and runtime
                                                                               review.
Depth Anything V2                      SECONDARY EVALUATION                    Monocular visual depth cues, not
                                                                               surveyed measurements;
                                                                               photogrammetric validation
                                                                               required.
Open3D / Blender geometry / IFC +      DETERMINISTIC REFERENCE                 Geometry, point clouds and model
CAD toolchain                                                                  interrogation; structural claims
                                                                               require calibrated data and
                                                                               accepted engineering methods.
Getty AAT / architectural heritage     DETERMINISTIC REFERENCE                 Controlled architecture vocabulary
registries                                                                     and historic provenance.



                                4nR-SURVEYOR · Development Scope v2.4 · 16 October 2026


---


I. Cross-suite model evaluation and active selection
   An individual suite may register multiple models with distinct tasks; SURVEYOR chooses the candidate by
    capability, licence, verified local availability, context, data modality, latency, power and historical benchmark
    record. Selection reason and checkpoint hash shall accompany every task.
   PER-CANDIDATE REGISTER: canonical model/checkpoint identifier, download/source URL, published date,
    version/hash, model owner, licence, intended use, selected inference runtime, model/quantisation format,
    input modalities, CPU/GPU/NPU memory and measured throughput, benchmark dataset, status owner,
    benchmark outcome, rejection reason and next evaluation action.
   NO PERFORMANCE CLAIMS WITHOUT TESTS: statuses designate evaluation priority, not measured accuracy or
    a proven fit for installed AMD hardware. Every suite must maintain a best-known operational configuration
    and at least one fallback or deterministic alternative.
   LICENCE GATES: differentiate source-code licences from model checkpoint/data licences. Music Flamingo is
    non-commercial research in the reviewed release; Aurora documentation indicates an open research model
    but directs commercial use enquiries separately. Neither is silently promoted to unrestricted deployment.
   Cross-suite reuse: SURVEYOR, CHEKOV and GOODALL may share one Aurora inference service when
    supported; EMERSON and CHAKOTAY may share one Whisper service. Duplicate model processes are avoided
    where safe; each suite maintains separate datasets and evaluation tasks.
   Performance and power: record actual idle/loaded memory, model swapping, response latency, energy,
    context-window behaviour and task completion on the AMD hardware in hand. Do not presume NPU
    deployment when a checkpoint requires PyTorch/GPU execution.
   Improvement cycle: benchmark → diagnose underperformance → research alternative
    checkpoints/workflows/data → experiment → retest on holdout cases → promote with audit record and rollback.
    Preserve failures as training and evaluation evidence, not as silent model substitutions.



J. Candidate references for continuing evaluation
   https://lemonade-server.ai/docs/models.html
   https://huggingface.co/Qwen/Qwen3-30B-A3B
   https://huggingface.co/Qwen/Qwen3-8B
   https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct
   https://huggingface.co/Qwen/Qwen3-Embedding-0.6B
   https://github.com/microsoft/aurora
   https://microsoft.github.io/aurora/models.html
   https://www.microsoft.com/en-us/research/project/aurora-forecasting/faq/
   https://huggingface.co/nvidia/music-flamingo-hf
   https://github.com/openai/whisper
   https://github.com/LAION-AI/CLAP
   https://github.com/ibm-granite/granite-geospatial
   https://github.com/facebookresearch/sam2
   https://github.com/isl-org/DPT
   https://github.com/birdnet-team/BirdNET-Analyzer

END OF V2.2 MODEL-CANDIDATE REGISTER




                                4nR-SURVEYOR · Development Scope v2.4 · 16 October 2026