"""
Quantum Walk Post-Processing Module
===================================

This module provides tools for post-processing the results of quantum walk simulations,
particularly those using Qiskit's quantum circuits for modeling node transitions in graphs.

Main Use Cases:
---------------
1. **Post-processing results from superposition walks**, where the walker starts in a superposition state.
2. **Post-processing results from single-node walks**, where the walker starts from a single node.

Core Class:
-----------
- `ResultsDataframe`: Encapsulates a pandas DataFrame with quantum walk results and provides
  methods to filter, summarize, and reformat the data.

Available Methods:
------------------
ResultsDataframe(df):
    Initialize the post-processing class with a pandas DataFrame.

- `postprocess_superposition(A)`:
    Removes real edges and self-loops based on adjacency matrix `A`, then adds max/avg summary rows,
    and converts column names to decimal format.

- `postprocess_one_node()`:
    Adds max and average probability rows to results from a single-node walk.

- `add_max_and_avg()`:
    Appends rows showing maximum and average probabilities across all columns (excluding 'Time').

- `filter_connected_columns(A)`:
    Removes columns corresponding to real graph edges and self-connections using the adjacency matrix `A`.

- `convert_to_decimal()`:
    Renames columns from binary format (e.g., '001 010') to decimal format (e.g., '1-2') for better readability.

Typical Workflow:
-----------------
```python
rdf = ResultsDataframe(df)
rdf.postprocess_superposition(A)  # For superposition walk results
rdf.postprocess_one_node()        # For single-node walk results
"""


import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import UnitaryGate
from qiskit_aer import Aer
from qiskit.quantum_info import Operator
from scipy.linalg import expm
import pandas as pd
import math
# Post processing functions

class ResultsDataframe:
    """
    A class to manage and post-process quantum walk simulation results.
    """

    def __init__(self, df):
        self.df=df

    def postprocess_superposition(self, A):
        """
        Post-processes superposition walk results:
        removes real edge columns and appends P-max and P-avg rows.

        Parameters
        ----------
        df : pandas.DataFrame
            Raw DataFrame from superposition walk.
        A : np.ndarray
            Adjacency matrix representing the graph structure.

        Returns
        -------
        ResultsDataframe
            Cleaned and enhanced ResultsDataframe instance.
        """
        
        self.filter_connected_columns(A)
        self.add_max_and_avg()
        self.convert_to_decimal()
        return self

    def postprocess_one_node(self):
        """
        Post-processes one-node walk results by appending P-max and P-avg rows only.

        Parameters
        ----------
        df : pandas.DataFrame
            Raw DataFrame from single-node quantum walk.

        Returns
        -------
        ResultsDataframe
            Enhanced ResultsDataframe instance with max and avg rows.
        """
        
        self.add_max_and_avg()
        return self

    def add_max_and_avg(self):
        """
        Appends two rows to the DataFrame:
        - 'P-max' for the maximum probability seen per node or possible connection.
        - 'P-avg' for the average probability over time.

        Returns
        -------
        self : ResultsDataframe
        """
        self.df = self.df.copy()
        p_max = self.df.drop('Time', axis=1).max()
        p_avg = self.df.drop('Time', axis=1).mean()
        self.df.loc[len(self.df)] = ['P-max'] + p_max.tolist()
        self.df.loc[len(self.df)] = ['P-avg'] + p_avg.tolist()
        return self

    def filter_connected_columns(self, A):
        """
        Filters out DataFrame columns corresponding to real edges
        based on the provided adjacency matrix.

        Parameters
        ----------
        A : np.ndarray
            Adjacency matrix indicating actual edges in the graph.

        Returns
        -------
        self : ResultsDataframe
        """
        num_nodes = len(A)
        num_bits = math.ceil(math.log2(num_nodes))

        real_connections = {
            f'{i:0{num_bits}b} {j:0{num_bits}b}'
            for i in range(num_nodes) for j in range(num_nodes) if A[i, j] != 0
        }

        same_nodes ={
            f'{i:0{num_bits}b} {j:0{num_bits}b}'
            for i in range(num_nodes) for j in range(num_nodes) if i==j
        }

        columns_to_keep = [col for col in self.df.columns if col not in real_connections] # removes real edges
        columns_to_keep = [col for col in columns_to_keep if col not in same_nodes] # removes same nodes

        self.df = self.df[columns_to_keep]
        return self
    
    def convert_to_decimal(self):
        """
        Converts DataFrame column names from binary node-pair format (e.g., '001 010')
        to decimal format (e.g., '1 2').

        Assumes the format is fixed: two binary numbers separated by a space.
        Skips the 'Time' column.

        Returns
        -------
        self : ResultsDataframe
        """
        new_columns = {}
        for col in self.df.columns:
            if col == 'Time':
                new_columns[col] = col
            else:
                try:
                    part1, part2 = col.split()
                    new_columns[col] = f"{int(part1, 2)}-{int(part2, 2)}"
                except Exception:
                    new_columns[col] = col  

        self.df.rename(columns=new_columns, inplace=True)
        return self



        






    
