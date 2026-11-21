# Data Challenge – Résilience du métro parisien

Projet réalisé en équipe pendant le Data Challenge IA Pau (sujet proposé par Alstom) : **simuler des pannes sur le réseau de métro parisien et repérer les inter-stations les plus critiques**.

## Le sujet

Étant donné :

- le plan du métro (liaisons entre stations),
- les positions GPS des stations,
- un fichier de flux de passagers (`de` → `vers`, `nombre`),

on cherche à :

1. prévoir le flux de passagers sur le réseau (chemin le plus court pour chaque trajet) ;
2. simuler la suppression de certaines inter-stations et mesurer l'impact sur les flux et les distances parcourues ;
3. identifier les liaisons les plus critiques.

## Ce que fait le projet

Tout est dans le notebook `Main.ipynb` :

1. **Chargement et nettoyage** des données (doublons de stations, parsing des coordonnées GPS).
2. **Modélisation du réseau** avec `networkx` : une station = un nœud, une liaison = une arête (307 nœuds, 377 arêtes). Distance fixe = 1 par défaut, ou distance haversine réelle (paramètre `USE_FIXED_DISTANCE`).
3. **Calcul des flux** : pour chaque couple (départ, arrivée), plus court chemin (Dijkstra), puis cumul des passagers sur chaque arête et chaque station. Option de pondération (`USE_PASSENGER_PONDERATION`) pour répartir un passager sur les éléments de son trajet.
4. **Points les plus chargés** : export dans `results/Overload_edges.csv` et `results/Overload_nodes.csv`.
5. **Arêtes contournables** : arêtes dont la suppression ne déconnecte pas le graphe (donc qui ne sont pas des ponts).
6. **Dégradation du réseau** : suppression aléatoire d'arêtes contournables, puis comparaison avec le réseau d'origine (écart de flux sur les arêtes et stations, écart de distance moyenne).
7. **Classement des inter-stations critiques** (suppression d'une arête à la fois).
8. **Cas réel** : application de la liste `data/interstations_supprimees.csv` et visualisation des flux sur le réseau dégradé.
9. **Génération de graphes dégradés** (`generated_graphs` + `node_ids.csv`) prévus comme jeu d'entraînement pour un GNN.

## Quelques résultats

Sur le réseau complet (distance fixe, sans pondération) :

- distance moyenne par passager : environ 10,4 inter-stations ;
- liaisons les plus chargées : Châtelet → Gare de Lyon, Châtelet → Pyramides, Gare de Lyon → Reuilly-Diderot ;
- stations les plus chargées : Châtelet, Gare de Lyon, Saint-Lazare, Nation, Madeleine.

Sur le cas réel (10 lignes dans `interstations_supprimees.csv`), 8 arêtes sont réellement supprimées. La ligne Saint-Marcel → Gare d'Austerlitz est le doublon inversé d'une autre ligne (déjà supprimée), et Guy Môquet – Porte de Saint-Ouen n'est pas contournable, donc le code l'ignore. Après suppression, Concorde → Madeleine passe de la 5e à la 3e liaison la plus chargée.

## Installation et utilisation

```bash
git clone https://github.com/Gotrone/data-challenge2025.git
cd data-challenge2025
pip install -r requirements.txt
jupyter notebook Main.ipynb
```

Le notebook se lance depuis la racine du dépôt (les chemins sont `data/` et `results/`). Les graines aléatoires sont fixées (`SEED = 42`) pour retrouver les mêmes résultats.

## Structure

```
.
├── Main.ipynb          # analyse complète
├── data/               # données d'entrée (CSV)
├── results/            # fichiers générés par le notebook
├── requirements.txt
└── README.md
```

## Corrections faites par rapport à la version du challenge

- **Dernière section** : le code lisait `position_gps_des_stations_de_metro.csv` à la place du plan du métro, ce qui donnait `KeyError: 'vers Station'`. Le graphe est maintenant construit depuis `plan_du_metro.csv`, et il n'est plus reconstruit juste après les suppressions (ce qui les annulait).
- **Flux sur les arêtes** : le graphe est non orienté mais les flux étaient stockés dans le sens du trajet, donc A→B et B→A étaient comptés séparément et mal retrouvés à l'affichage. Les clés sont maintenant triées.
- **Arêtes contournables** : remplacement de « copie du graphe + `has_path` pour chaque arête » par `nx.bridges`, même résultat, bien plus rapide.
- Reproductibilité (graine), chemins de fichiers, encodage UTF-8, `print` mal formaté dans `degrade_plan`, paramètre `use_passenger_ponderation` ignoré dans `analyze_degraded_graphs`.

## Limites

- **Le classement des inter-stations critiques ne porte que sur 10 arêtes** (`max_graphs=10` dans `analyze_degraded_graphs`, pour que le calcul reste court), prises dans l'ordre du graphe. Ce n'est donc pas un vrai classement des 368 arêtes contournables.
- **Distance = nombre d'inter-stations** par défaut. On ne tient pas compte des temps de trajet réels, des correspondances (longueur à pied), de la fréquence des rames ni de la capacité des lignes.
- **Un seul chemin le plus court par trajet** : tous les passagers d'un même trajet prennent le même chemin. En réalité, ils se répartissent et la congestion change les choix. Les flux sont donc probablement surestimés sur certaines liaisons.
- **Pas de modèle de capacité** : on mesure des flux, pas de saturation.
- Le graphe est **non orienté** et fusionne les lignes : on ne distingue pas une ligne d'une autre.
- Les mesures d'écart en pourcentage sont très grandes pour les arêtes à faible flux initial (écart maximum de plus de 2000 %) ; la moyenne est à lire avec précaution.
- Les stations sans position GPS n'ont pas de coordonnées, donc `USE_POSITIONS=True` en ignore certaines.
- **La partie GNN n'est pas dans ce dépôt** : le modèle (226 Mo) n'a pas pu être récupéré et le code associé ne tournait plus. Seule la génération du jeu de données (graphes dégradés + chemins optimaux) est conservée.
- L'impact énergétique (partie Green AI du challenge, plateforme GAIA) n'est pas inclus.

## Pistes d'amélioration

- Analyser **toutes** les arêtes contournables, en mettant en cache les plus courts chemins (ou en les recalculant seulement pour les trajets touchés).
- Passer à des **distances ou temps réels** (haversine, temps inter-stations, pénalité de correspondance).
- **Répartir les passagers** sur plusieurs chemins proches (k plus courts chemins) et itérer avec un modèle de congestion.
- Ajouter des **capacités** par ligne et mesurer la saturation, pas seulement le flux.
- Supprimer **plusieurs arêtes** à la fois (approche itérative évoquée dans le notebook) et tester les suppressions de stations.
- Reprendre le **GNN** (prédire si un nœud est sur le plus court chemin) et le comparer à Dijkstra en précision et en temps de calcul.
- Séparer le code du notebook dans un module Python (`src/`) et ajouter quelques tests.

## Données

Les fichiers de `data/` proviennent du Data Challenge (plan du métro, positions GPS des stations, flux de passagers).
