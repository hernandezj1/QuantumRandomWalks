"""
Quantum Random Walk Module
==========================

This module provides tools for simulating continuous-time quantum random walks (QRWs)
on graphs represented by adjacency matrices. The walks are modeled using Qiskit's quantum circuits
and simulated using Aer backends.

Included Capabilities:
----------------------
1. Quantum walk from a single start node evolving outward (e^{-iAt}).
2. Quantum walk from a single start node evolving inward (e^{iAt}).
3. Quantum walk from a superposition of all nodes.

Planned Capabilities:
----------------------
1. Pre-processing for specific network formats such as Gephi-csv exports
2. Post-processing utilities for extracting summary statistics and analyzing distributions.

Assumptions:
------------
- The adjacency matrix should be square of size 2^n × 2^n.
- Nodes are indexed from 0 to 2^n - 1 and correspond to binary quantum states.
- If your graph doesn't fit this format, preprocessing will be needed.

Classes:
--------
- `QuantumRandomWalk`: Encapsulates circuit setup, walk simulation (inward or outward), and measurement.
- `ResultsDataFrame`: Encapsulates all post-processing functions for the dataframe 

Functions:
----------
- `perform_one_node_walk`: Performs a continuous-time quantum walk from a specific start node over time steps.
- `perform_superpositioned_walk`: Performs a continous-time quantum walk starting at a superposition of all nodes

Dependencies:
-------------
- numpy
- pandas
- qiskit (QuantumCircuit, QuantumRegister, ClassicalRegister, Aer, Operator)
- scipy.linalg.expm
- math
"""


# Imports

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import UnitaryGate
from qiskit_aer import Aer
from qiskit.quantum_info import Operator
from scipy.linalg import expm
import pandas as pd
import math

# creating quantum circuit for quantum walk class and methods

class QuantumRandomWalk: 
    """
    A class to simulate a quantum random walk on a graph using its adjacency matrix.

    Attributes:
    -----------
    _adjacencymatrix : np.ndarray
        The adjacency matrix representing the graph.
    _numberofqubits : int
        Number of qubits required, based on the size of the adjacency matrix.
    _numberofnodes : int
        Total number of nodes (2 ** number of qubits).
    _qc : QuantumCircuit
        The quantum circuit used in the walk.
    _qr1, _qr2 : QuantumRegister
        Quantum registers used for superposition states.
    _cr1, _cr2 : ClassicalRegister
        Classical registers used for measuring superposition.
    _possible_nodes : list of str
        All possible node binary labels (for result analysis).
    _results_df : pd.DataFrame
        DataFrame to store simulation results.
    _counts : dict
        Dictionary storing counts from simulation output.
    """

    def __init__(self, A):
        """
        Initialize the quantum random walk using the graph's adjacency matrix.

        Parameters:
        -----------
        A : np.ndarray
            The adjacency matrix of the graph.
        """
        self._adjacencymatrix= A
        self._numberofqubits= int(np.log2(A.shape[0]))
        self._numberofnodes = 2 ** self._numberofqubits 
        

    def start_node_n(self, n):
        """
        Initialize the quantum circuit with a specific starting node.

        Parameters:
        -----------
        n : int
            The index of the node to initialize the walk from.
        """
        self._qc= QuantumCircuit(self._numberofqubits) 

        binary= format(n, f'0{self._numberofqubits}b')
    
        # Encode starting node 
        for i, bit in enumerate(reversed(binary)):  # Reverse to match Qiskit's qubit indexing
            if bit == '1':
                self._qc.x(i)
    
    def superposition(self): 
        """
        Prepare a quantum circuit in a full superposition state across all possible nodes.
        Uses two registers to apply entangled Hadamard+CNOT pattern.
        cr2 - measures starting node 
        cr1 - measures finishing node
        joint result will have probability of connection fo each node to every other node
        """
        self._qr1= QuantumRegister(self._numberofqubits)
        self._qr2= QuantumRegister(self._numberofqubits)
        self._cr1= ClassicalRegister(self._numberofqubits)
        self._cr2= ClassicalRegister(self._numberofqubits)
        self._qc= QuantumCircuit(self._qr1, self._qr2, self._cr1, self._cr2) # double so we can apply the CNOTs

        for i in range(self._numberofqubits): 
            self._qc.h(i) # apply hadamards to all nodes, creating all possible states 2 to the n
            self._qc.cx(i,i+ self._numberofqubits)
        

    def walk_out(self, t):
        """
        Apply the quantum walk operator e^{-iAt} for an "outgoing" walk.

        Parameters:
        -----------
        t : float
            Time step at which to apply the walk operator.
        """

        # Calculate e^{-iAt}
        i = complex(0, 1)
        U_minus = expm(-i * self._adjacencymatrix * t)  # e^{-iAt} 

        self._qc.unitary(Operator(U_minus), range(self._numberofqubits), label="U_minus")


    
    def walk_in(self, t):
        """
        Apply the quantum walk operator e^{iAt} for an "incoming" walk.

        Parameters:
        -----------
        t : float
            Time step at which to apply the walk operator.
        """

        # Calculate e^{-iAt}
        i = complex(0, 1)
        U_plus = expm(i * self._adjacencymatrix * t)  # e^{iAt} chnaged it to positive for in walk on node

        self._qc.unitary(Operator(U_plus), range(self._numberofqubits), label="U_plus")

        
    def complete_single_node(self):
        """
        Measure all qubits in the single node walk circuit.
        """
        self._qc.measure_all() 

    def complete_superposition(self): 
        """
        Measure both quantum registers in the superposition circuit.
        """
        self._qc.measure(self._qr1, self._cr1) 
        self._qc.measure(self._qr2, self._cr2)

    def simulator_measure(self, simulator='aer_simulator'): 
        """
        Run the quantum circuit on the specified simulator backend and collect measurement results.

        Parameters:
        -----------
        simulator : str
            Name of the Qiskit simulator backend to use with 'aer_simulator' as a default.
        """
        sim = Aer.get_backend(simulator) 
        result = sim.run(self._qc).result()
        self._counts = result.get_counts()
    




# Quantum walk functions

def perform_one_node_walk(Adj_Matrix, start_node, type_of_walk, total_time, step_interval): 
    """
    Simulates a continuous-time quantum random walk from a single starting node.

    Parameters
    ----------
    Adj_Matrix : np.ndarray
        The adjacency matrix of the graph representing the network.
    start_node : int
        The index of the node from which the walk starts.
    type_of_walk : str
        Type of unitary operator to use; must be either `'in'` or `'out'`.
        - `'in'`  uses U(t) = e^{iAt}
        - `'out'` uses U(t) = e^{-iAt}
    total_time : float
        The total time duration for which the quantum walk evolves.
    step_interval : float
        The time step increment between each walk measurement.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the time steps and the probability distribution over nodes at each time.
        The last two rows contain the maximum ('P-max') and average ('P-avg') probabilities per node.
    """

    num_nodes = len(Adj_Matrix)
    num_bits = math.ceil(math.log2(num_nodes))

    # Generate binary strings to interpret results
    possible_nodes = [f'{i:0{num_bits}b}' for i in range(num_nodes)]

    columns = ['Time'] + possible_nodes
    results_df = pd.DataFrame(columns=columns)

    for i in np.arange(0, total_time, step_interval):  
        # Creation of quantum walk for each interval
        qrw = QuantumRandomWalk(Adj_Matrix)
        qrw.start_node_n(start_node)

        # Selection of unitary
        if type_of_walk == 'in': 
            qrw.walk_in(i)
        elif type_of_walk == 'out': 
            qrw.walk_out(i)
        else: 
            print("Invalid type. Must select 'in' or 'out' walk")

        qrw.complete_single_node() # add measurements
        qrw.simulator_measure('aer_simulator')

        # Ensure all possible nodes are represented, even if they have a count of 0
        for node in possible_nodes:
            if node not in qrw._counts:
                qrw._counts[node] = 0

        shots = 1024  
        probabilities = {key: value / shots for key, value in qrw._counts.items()} # dividinng by shots to get the probability

        # Saving results to DataFrame
        row = [i] + [probabilities.get(node, 0) for node in possible_nodes]  # Ensure 0 if key not found
        results_df.loc[len(results_df)] = row

    new_columns =['Time']
    for i in range(0,qrw._numberofnodes): 
        new_columns.append(i)

    results_df.columns=new_columns

    return results_df



def perform_superpositioned_walk(Adj_Matrix, type_of_walk, total_time, step_interval):
    """
    Simulates a continuous-time quantum random walk starting in a superposition of all nodes.

    Parameters
    ----------
    Adj_Matrix : np.ndarray
        The adjacency matrix of the graph representing the network.
    type_of_walk : str
        Type of unitary operator to use; must be either `'in'` or `'out'`.
        - `'in'`  uses U(t) = e^{iAt}
        - `'out'` uses U(t) = e^{-iAt}
    total_time : float
        The total time duration for which the quantum walk evolves.
    step_interval : float
        The time step increment between each walk measurement.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the time steps and the probability distribution over all node-node connections at each time.
    """

    num_nodes = len(Adj_Matrix)
    num_bits = math.ceil(math.log2(num_nodes))

    # Generate binary strings representing each pair of nodes (cr2 + cr1)
    possible_connections = [f'{i:0{num_bits}b} {j:0{num_bits}b}' for i in range(num_nodes) for j in range(num_nodes)]

    columns = ['Time'] + possible_connections
    results_df = pd.DataFrame(columns=columns)

    for i in np.arange(0, total_time, step_interval):  
        # Creation of quantum walk for each interval
        qrw = QuantumRandomWalk(Adj_Matrix)
        qrw.superposition()

        # Selection of unitary
        if type_of_walk == 'in': 
            qrw.walk_in(i)
        elif type_of_walk == 'out': 
            qrw.walk_out(i)
        else: 
            print("Invalid type. Must select 'in' or 'out' walk")

        qrw.complete_superposition()
        qrw.simulator_measure('aer_simulator')

        # Ensure all possible nodes are represented, even if they have a count of 0
        for connection in possible_connections:
            if connection not in qrw._counts:
                qrw._counts[connection] = 0

        shots = 1024  
        probabilities = {key: value / shots for key, value in qrw._counts.items()} # dividinng by shots to get the probability

        # Saving results to DataFrame
        row = [i] + [probabilities.get(connection, 0) for connection in possible_connections]  # Ensure 0 if key not found
        results_df.loc[len(results_df)] = row

    return results_df