# Data Challenge – Paris Metro Network Resilience

Team project from the IA Pau Data Challenge (subject proposed by Alstom): **simulate disruptions on the Paris metro network and identify the most critical inter-stations**.

Stack: Python, pandas, networkx, matplotlib, Jupyter.

## Table of contents

- [Contributions](#contributions)
- [Problem](#problem)
- [Approach](#approach)
- [Results](#results)
- [Setup and usage](#setup-and-usage)
- [Repository structure](#repository-structure)
- [Fixes since the challenge version](#fixes-since-the-challenge-version)
- [Limitations](#limitations)
- [Possible improvements](#possible-improvements)

## Contributions

Group project from the IA Pau Data Challenge: the team worked on it together and shared the work. This repository is my own clean version of the challenge code. I rewrote the analysis, translated it to English, fixed the bugs listed below and analysed all 368 bypassable edges.

## Problem

Input data (original French file and column names are kept):

- the metro map (`plan_du_metro.csv`),
- GPS positions of the stations (`position_gps_des_stations_de_metro.csv`),
- passenger flows (`passagers.csv`: 93,942 trips `de` → `vers` with a passenger count `nombre`, 468,804 passengers in total).

Goals:

1. estimate the passenger flow on every connection and station (shortest path for each trip);
2. simulate the removal of inter-stations and measure the effect on flows and travel distances;
3. identify the most critical inter-stations.

## Approach

Everything is in `Main.ipynb`.

1. **Loading and cleaning**: duplicate stations, parsing GPS coordinates.
2. **Graph** (`networkx`): one station = one node, one connection = one edge (307 nodes, 377 edges). The edge weight is 1 by default, or the real haversine distance (`USE_FIXED_DISTANCE`).
3. **Flows**: for each trip, shortest path (Dijkstra), then passengers are accumulated on every edge and station. An option (`USE_PASSENGER_WEIGHTING`) spreads one passenger over all the items of their path.
4. **Most loaded edges and stations**: exported to `results/Overload_edges.csv` and `results/Overload_nodes.csv`.
5. **Bypassable edges**: edges whose removal does not disconnect the graph (they are not bridges). 368 of the 377 edges qualify.
6. **Degradation analysis**: remove one bypassable edge at a time (all 368), then compare with the original network (flow difference on edges and stations, difference in average travel distance). The ranking is exported to `results/critical_intersections.csv`.
7. **Real case**: apply `data/removed_interstations.csv` and plot the flows on the degraded network.
8. **GNN training set**: generate random degraded graphs with their optimal paths, plus `results/node_ids.csv`.

## Results

Full network (fixed distance, no weighting):

- average travel distance per passenger: about 10.4 inter-stations;
- most loaded connections: Châtelet – Gare de Lyon (about 74,000 passengers), Gare de Lyon – Reuilly-Diderot, Châtelet – Pyramides;
- most loaded stations: Châtelet (about 243,000), Gare de Lyon, Saint-Lazare, Nation, Madeleine.

Top 5 inter-stations whose removal increases the average travel distance the most (out of the 368 tested):

| Removed inter-station | Increase in average distance |
|---|---|
| Daumesnil – Michel Bizot | 7.0 % |
| Michel Bizot – Porte Dorée | 5.8 % |
| Porte de Charenton – Porte Dorée | 4.7 % |
| Buzenval – Nation | 4.2 % |
| Liberté – Porte de Charenton | 3.8 % |

These connections are in the east of Paris (Charenton branch of line 8, line 9 near Nation). They are bypassable, but only through long detours in the graph.

Real case: `removed_interstations.csv` has 10 rows and 8 edges are actually removed. The row Saint-Marcel → Gare d'Austerlitz is the reversed duplicate of another row, and Guy Môquet – Porte de Saint-Ouen is not bypassable (the code skips it). After the removal, Concorde – Madeleine moves from the 5th to the 3rd most loaded connection.

## Setup and usage

```bash
git clone https://github.com/Gotrone/paris-metro-resilience.git
cd paris-metro-resilience
python -m venv .venv
.venv\Scripts\activate        # Linux / macOS: source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook Main.ipynb
```

- Run the notebook **from the repository root** (paths are `data/` and `results/`).
- Full run takes about 5 minutes (most of it is the analysis of the 368 degraded graphs).
- Random seeds are fixed (`SEED = 42`).
- The GNN dataset cell writes `results/generated_graphs.json` (ignored by git because it can be regenerated).

## Repository structure

```
.
├── Main.ipynb          # full analysis (with outputs)
├── data/               # input CSV files
├── results/            # files produced by the notebook
├── requirements.txt
└── README.md
```

## Fixes since the challenge version

- **Last section**: the code read the GPS file instead of the metro map (`KeyError: 'vers Station'`). The graph is now built from `plan_du_metro.csv`, and it is no longer rebuilt right after the removals (which cancelled them).
- **Edge flows**: the graph is undirected but flows were stored in the direction of the trip, so A→B and B→A were counted separately and not found again when plotting. Keys are now sorted.
- **Speed**: one Dijkstra run per origin station (instead of one per trip) and `nx.bridges` for bypassable edges. This makes it possible to analyse all 368 edges instead of 10.
- Misc: random seed, file paths, UTF-8 encoding, badly formatted `print` in `degrade_plan`, `use_passenger_weighting` ignored in `analyze_degraded_graphs`, English naming and documentation.

## Limitations

- **Distance = number of inter-stations** by default. Travel times, transfer walking time, train frequency and line capacity are not modelled.
- **A single shortest path per trip.** With a fixed distance many paths are tied and the choice between them is arbitrary, so flows depend slightly on it and are probably overestimated on some connections (in reality passengers spread out).
- **No capacity or congestion model**: we measure flows, not saturation.
- The graph is **undirected** and merges all lines: lines are not distinguished.
- Percentage differences are very large for edges with a low initial flow (more than 2,000 % at most), so averages should be read with care.
- Only one edge is removed at a time: the cumulative effect of simultaneous failures is not captured.
- With `USE_POSITIONS=True`, stations without GPS coordinates are ignored.
- **The GNN part is not in this repository**: the trained model (226 MB) could not be recovered and the related code no longer ran. Only the dataset generation is kept.
- Energy impact (Green AI part of the challenge, GAIA platform) is not included.
- No automated tests: results were checked by re-running the notebook and reading the outputs.

## Possible improvements

- Use **real travel times** (inter-station times, transfer penalty).
- **Spread passengers** over several close paths (k shortest paths) and iterate with a congestion model.
- Add **line capacities** and measure saturation.
- Remove **several edges at once** (iterative approach sketched in the notebook) and test station removals.
- Rebuild the **GNN** (predict whether a node is on the shortest path) and compare it with Dijkstra in accuracy and run time.
- Move the code out of the notebook into a Python module (`src/`) and add tests.

## Data

The files in `data/` come from the Data Challenge (metro map, station GPS positions, passenger flows).
