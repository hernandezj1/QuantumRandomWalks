# QuantumRandomWalk package

This package was built as the final summary assignment for the University of Rhode Island Quantum Computinhg Graduate Certificate by Jose Hernandez. The original project utilized quantum random walks to calculate probability of visit per node with a start node x or probability of edge existence between all possible pair nodes.

The purpose of this package is to allow network scientists to programmatically apply continous time quantum random walks on their own networks without needing signficant quantum preparation or onboarding.m This is alos meant as a begginer-friendly introductionn to quantu circuits which is why every effort has been made to simplify parameters and inputs as much as possible. 

## Capabilities: 

__Included Capabilities:__

1. Quantum walk from a single start node evolving outward (e^{-iAt}).
2. Quantum walk from a single start node evolving inward (e^{iAt}).
3. Quantum walk from a superposition of all nodes.

__Planned Capabilities:__

1. Pre-processing for specific network formats such as Gephi-csv exports
2. Post-processing utilities for extracting summary statistics and analyzing distributions.

__Assumptions:__

**NOTE: A preprocessing module will be added before first major release to complete this preprocessing automatically for any network**

- The adjacency matrix should be square of size 2^n × 2^n.
- Nodes are indexed from 0 to 2^n - 1 and correspond to binary quantum states.
- If your graph doesn't fit this format, preprocessing will be needed.

## Content: 

__Classes:__

- `QuantumRandomWalk`: Encapsulates circuit setup, walk simulation (inward or outward), and measurement.
- `ResultsDataFrame`: Encapsulates all post-processing functions for the dataframe 

__Functions:__

- `perform_one_node_walk`: Performs a continuous-time quantum walk from a specific start node over time steps.
- `perform_superpositioned_walk`: Performs a continous-time quantum walk starting at a superposition of all nodes


