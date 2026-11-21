# Data Challenge – Résilience du métro parisien

Projet réalisé en équipe pendant le Data Challenge IA Pau (sujet proposé par Alstom) : **simuler des pannes sur le réseau de métro parisien et repérer les inter-stations les plus critiques**.

Stack : Python, pandas, networkx, matplotlib, Jupyter.

## Sommaire

- [Le sujet](#le-sujet)
- [Démarche](#démarche)
- [Résultats](#résultats)
- [Installation et utilisation](#installation-et-utilisation)
- [Structure du dépôt](#structure-du-dépôt)
- [Corrections apportées](#corrections-apportées)
- [Limites](#limites)
- [Pistes d'amélioration](#pistes-damélioration)

## Le sujet

À partir de :

- le plan du métro (`plan_du_metro.csv`),
- les positions GPS des stations (`position_gps_des_stations_de_metro.csv`),
- un fichier de flux de passagers (`passagers.csv` : 93 942 trajets `de` → `vers`, 468 804 passagers au total),

on cherche à :

1. estimer le flux de passagers sur chaque liaison et chaque station (chemin le plus court pour chaque trajet) ;
2. simuler la suppression d'inter-stations et mesurer l'effet sur les flux et les distances parcourues ;
3. identifier les inter-stations les plus critiques.

## Démarche

Tout est dans `Main.ipynb`.

1. **Chargement et nettoyage** : doublons de stations, lecture des coordonnées GPS.
2. **Graphe** (`networkx`) : une station = un nœud, une liaison = une arête. On obtient 307 nœuds et 377 arêtes. La distance vaut 1 par arête par défaut, ou la distance haversine réelle (`USE_FIXED_DISTANCE`).
3. **Flux** : pour chaque trajet, plus court chemin (Dijkstra), puis cumul des passagers sur les arêtes et les stations. Une option (`USE_PASSENGER_PONDERATION`) répartit un passager sur les éléments de son trajet.
4. **Points les plus chargés** : export vers `results/Overload_edges.csv` et `results/Overload_nodes.csv`.
5. **Arêtes contournables** : arêtes dont la suppression ne déconnecte pas le graphe (ce ne sont pas des ponts). Il y en a 368 sur 377.
6. **Dégradation** : suppression d'une arête contournable à la fois, pour les 368 arêtes, puis comparaison avec le réseau d'origine (écart de flux sur les arêtes et les stations, écart de distance moyenne). Le classement est exporté dans `results/critical_intersections.csv`.
7. **Cas réel** : application de `data/interstations_supprimees.csv` et affichage des flux sur le réseau dégradé.
8. **Jeu d'entraînement pour un GNN** : génération de graphes dégradés aléatoires avec leurs chemins optimaux, et de `results/node_ids.csv`.

## Résultats

Réseau complet (distance fixe, sans pondération) :

- distance moyenne par passager : environ 10,4 inter-stations ;
- liaisons les plus chargées : Châtelet – Gare de Lyon (≈ 74 000 passagers), Gare de Lyon – Reuilly-Diderot, Châtelet – Pyramides ;
- stations les plus chargées : Châtelet (≈ 243 000), Gare de Lyon, Saint-Lazare, Nation, Madeleine.

Les 5 inter-stations dont la suppression augmente le plus la distance moyenne (sur les 368 testées) :

| Inter-station supprimée | Hausse de la distance moyenne |
|---|---|
| Daumesnil – Michel Bizot | 7,0 % |
| Michel Bizot – Porte Dorée | 5,8 % |
| Porte de Charenton – Porte Dorée | 4,7 % |
| Buzenval – Nation | 4,2 % |
| Liberté – Porte de Charenton | 3,8 % |

Ces liaisons sont à l'est de Paris (branche de Charenton de la ligne 8, ligne 9 près de Nation). Elles sont contournables, mais seulement par de longs détours dans le graphe.

Cas réel : sur les 10 lignes de `interstations_supprimees.csv`, 8 arêtes sont supprimées. Saint-Marcel → Gare d'Austerlitz est le doublon inversé d'une autre ligne, et Guy Môquet – Porte de Saint-Ouen n'est pas contournable (le code l'ignore). Après suppression, Concorde – Madeleine passe de la 5e à la 3e liaison la plus chargée.

## Installation et utilisation

```bash
git clone https://github.com/Gotrone/data-challenge2025.git
cd data-challenge2025
python -m venv .venv
.venv\Scripts\activate        # Linux / macOS : source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook Main.ipynb
```

- Lancer le notebook **depuis la racine du dépôt** (les chemins sont `data/` et `results/`).
- Durée d'exécution complète : environ 5 minutes (l'essentiel est l'analyse des 368 graphes dégradés).
- Les graines aléatoires sont fixées (`SEED = 42`).
- La cellule de génération du jeu GNN écrit `results/generated_graphs.json` (ignoré par git, car regénérable).

## Structure du dépôt

```
.
├── Main.ipynb          # analyse complète (avec les sorties)
├── data/               # données d'entrée (CSV)
├── results/            # fichiers produits par le notebook
├── requirements.txt
└── README.md
```

## Corrections apportées

Par rapport à la version rendue pendant le challenge :

- **Dernière section** : le code lisait le fichier GPS au lieu du plan du métro (`KeyError: 'vers Station'`). Le graphe est maintenant construit depuis `plan_du_metro.csv`, et il n'est plus reconstruit juste après les suppressions (ce qui les annulait).
- **Flux sur les arêtes** : le graphe est non orienté, mais les flux étaient stockés dans le sens du trajet, donc A→B et B→A étaient comptés à part et mal retrouvés à l'affichage. Les clés sont maintenant triées.
- **Vitesse** : un seul Dijkstra par station de départ (au lieu d'un par trajet) et `nx.bridges` pour les arêtes contournables. Cela permet d'analyser les 368 arêtes au lieu de 10.
- Divers : graine aléatoire, chemins de fichiers, encodage UTF-8, `print` mal formaté dans `degrade_plan`, paramètre `use_passenger_ponderation` ignoré dans `analyze_degraded_graphs`.

## Limites

- **Distance = nombre d'inter-stations** par défaut. On ne tient compte ni des temps de trajet, ni des correspondances (marche), ni de la fréquence des rames, ni de la capacité des lignes.
- **Un seul chemin le plus court par trajet.** Beaucoup de chemins sont à égalité avec une distance fixe, et le choix est arbitraire. Les flux dépendent donc un peu de ce choix, et ils sont probablement surestimés sur certaines liaisons : en vrai, les passagers se répartissent.
- **Pas de modèle de capacité ni de congestion** : on mesure des flux, pas une saturation.
- Le graphe est **non orienté** et fusionne les lignes : on ne distingue pas une ligne d'une autre.
- Les écarts en pourcentage sont très grands pour les arêtes à faible flux initial (plus de 2000 % au maximum) ; la moyenne est à lire avec précaution.
- Une seule arête supprimée à la fois : on ne voit pas les effets cumulés de pannes simultanées.
- Avec `USE_POSITIONS=True`, les stations sans coordonnées GPS sont ignorées.
- **La partie GNN n'est pas dans ce dépôt** : le modèle (226 Mo) n'a pas pu être récupéré et le code associé ne tournait plus. Seule la génération du jeu de données est conservée.
- L'impact énergétique (Green AI, plateforme GAIA) n'est pas inclus.
- Pas de tests automatiques : les résultats ont été vérifiés en relançant le notebook et en relisant les sorties.

## Pistes d'amélioration

- Passer à des **temps réels** : temps inter-stations, pénalité de correspondance.
- **Répartir les passagers** sur plusieurs chemins proches (k plus courts chemins), puis itérer avec un modèle de congestion.
- Ajouter des **capacités** par ligne et mesurer la saturation.
- Supprimer **plusieurs arêtes** à la fois (approche itérative notée dans le notebook) et tester des suppressions de stations.
- Reprendre le **GNN** (prédire si un nœud est sur le plus court chemin) et le comparer à Dijkstra en précision et en temps de calcul.
- Sortir le code du notebook dans un module Python (`src/`) et ajouter quelques tests.

## Données

Les fichiers de `data/` proviennent du Data Challenge (plan du métro, positions GPS des stations, flux de passagers).
