#
#   Circuit Class definition
#

import numpy as np
from tabulate import tabulate
from typing import List
from gate import *
from quantiphy import Quantity

class Circuit:
    def __init__(self, name, circuit:List[Gate], tau_2, tau_ratio, final_load) -> None:
        """
        C_load = final_load * C_in_inv
        
        tau_2 : delay of the minimum size inverter
        """
        self.name = name
        self.circuit_gates = circuit
        self.N = len(self.circuit_gates)
        self.tau_2 = tau_2
        self.tau_ratio = tau_ratio      # tau1 / tau2
        self.final_load = final_load
        self.b_vector = self.compute_b()
        self.delay = self.compute_circuit_delay(final_load)
        self.p_vector = np.array(list(map(lambda gate: gate.p, self.circuit_gates)))
        self.g_vector = np.array(list(map(lambda gate: gate.g, self.circuit_gates)))
        self.h_vector = np.array(list(map(lambda gate: gate.h, self.circuit_gates)))

        self.B = np.prod(self.b_vector)
        self.G = np.prod(self.g_vector)
        self.H = None

        self.f_hat = None
        self.minimum_delay = self.comupute_min_delay()


    def __str__(self) -> str:
        output = ""
        for idx, gate in enumerate(self.circuit_gates):
            output += gate.name
            if (idx != len(self.circuit_gates)-1):
                output += " -> " 
        return output
    
    def info(self):
        first_row = ['']
        p_row = ['p']
        g_row = ['g']
        h_row = ['h']
        b_row = ['b']
        gamma_row = ['gamma']
        c_in = ['Cin']
        c_load = ['Cload']
        c_off = ['C_off']
        delay_gate = ['gate delay']

        for gate in self.circuit_gates:
            first_row.append(gate.name)
            p_row.append(str(f"{gate.p:.3f}"))
            g_row.append(str(f"{gate.g:.3f}"))
            h_row.append(str(f"{gate.h:.3f}"))
            b_row.append(str(f"{gate.b:.3f}"))
            gamma_row.append(str(f"{gate.gamma_gate:.3f}"))
            c_in.append(str(Quantity(gate.C_in_gate, 'F')))
            c_load.append(str(Quantity(gate.C_load, 'F')))
            c_off.append(str(Quantity(gate.C_off, 'F')))
            delay_gate.append(str(Quantity(gate.delay * self.tau_2, 's')))
        
        all_data = [first_row, p_row, g_row, h_row, b_row, gamma_row, c_in, c_load, c_off, delay_gate]
        
        print(f"Circuit name: {self.name}")
        print(tabulate(all_data,headers='firstrow',tablefmt='fancy_grid'))
        print()
        delay = Quantity(self.delay, 's')
        min_delay = Quantity(self.minimum_delay, 's')
        print(f"Delay of the circuit = {delay}")
        print(f"Minimum achievable delay = {min_delay}")
        print(f"Number of stages = {self.N}")
        print(f"Tau_2 = {str(Quantity(self.tau_2, 's'))}")
        print(f"Tau_ratio = {self.tau_ratio:.3f}")
        print(f"F_hat = {self.f_hat:.3f}")
        print(f"Final load = {self.final_load:.3f} * C_in_inv")
        print(f"H = {self.H:.3f}")
        print(f"G = {self.G:.3f}")
        print(f"B = {self.B:.3f}")

        """ branches_nb = 0
        print()
        print("Branches details")
        for gate in self.circuit_gates:
            if type(gate) == Branch:
                print(gate)
                print()
                branches_nb += 1
        if branches_nb == 0:
            print("no external branches in this circuit!") """
    
    def compute_circuit_delay(self, load):
        total_delay = 0
        # load last gate includes wire capacitance; previous gates wire capacitance is included in the next gate Coff
        for i in range(len(self.circuit_gates)):
            if (i == len(self.circuit_gates)-1):
                self.circuit_gates[i].set_load(load * self.circuit_gates[i].C_inv_true + self.circuit_gates[i].metalCap)
            else:
                #self.circuit_gates[i+1].C_off += self.circuit_gates[i].metalCap
                self.circuit_gates[i].set_load(self.circuit_gates[i+1].C_in_gate) 
            
            total_delay += self.circuit_gates[i].delay

        return total_delay * self.tau_2  
    
    def comupute_min_delay(self):
        self.H = (self.circuit_gates[-1].C_load) / (self.circuit_gates[0].C_in_gate * self.circuit_gates[0].gamma_gate)
        self.f_hat = pow(self.H * np.prod(self.g_vector) * self.B, 1/self.N)
        min_delay = sum(self.p_vector) * self.tau_ratio + self.N * self.f_hat
        return min_delay * self.tau_2
    
    def compute_b(self):
        b_vector = np.ones(self.N)
        for i in range(self.N-1):
            #self.circuit_gates[i+1].C_off += self.circuit_gates[i].metalCap
            self.circuit_gates[i].b = (self.circuit_gates[i+1].C_in_gate + self.circuit_gates[i+1].C_off) / self.circuit_gates[i+1].C_in_gate
            b_vector[i] = self.circuit_gates[i].b
        
        return b_vector