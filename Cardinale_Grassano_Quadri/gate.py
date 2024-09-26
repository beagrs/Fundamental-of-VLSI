#
#   Gate Class definition
#   Inverter, Nand, Nor
#

from typing import List
from metal import *

class Gate:
    def __init__(self, name, beta_gate, beta_inv, gamma_gate, metal:Metal, C_0_transistor, tau_ratio) -> None:
        self.name = name
        self.beta_gate = beta_gate
        self.beta_inv = beta_inv
        self.gamma_gate = gamma_gate
        self.C_0_transistor = C_0_transistor
        self.C_inv_true = (beta_inv + 1) * C_0_transistor
        self.C_inv = (beta_inv + 1)
        self.nb_input = None
        self.g = None
        self.p = None
        self.h = None
        self.b = 1
        self.C_load = None
        self.C_in_gate = None
        self.delay = None
        self.C_off = 0
        self.tau_ratio = tau_ratio
        self.metal = metal
        self.metalCap = metal.Ctot      # the metal that we consider is the output wire
    
    def __str__(self):
        return self.name + "\n" + "\tp = " + str(self.p) + "\n" + "\tg = "  + str(self.g) + "\n" + "\th = " + str(self.h) + "\n" + "\tb = " + str(self.b) + "\n" + "\tC_in_gate = " + str(self.C_in_gate) + "\n" + "\tC_off = " + str(self.C_off) + "\n"
        
    def set_load(self, load):
        """ 
        How to set the load:
        C_load = load * C_in_inv 
        """
        #self.C_load = load + self.metalCap
        self.C_load = load

        self.h = load / self.C_in_gate 
        # Without branch
        # self.delay = self.p + self.g * self.h
        
        #self.C_off += self.metalCap

        # With branch
        self.delay = self.p * self.tau_ratio + self.g * self.h * self.b

class Inverter(Gate):
    def __init__(self, name, beta_gate, beta_inv, gamma_gate, metal:Metal, C_0_transistor, tau_ratio) -> None:
        super().__init__(name, beta_gate, beta_inv, gamma_gate, metal, C_0_transistor, tau_ratio)
        self.nb_input = 1
        self.g = 1
        self.p = 1
        self.C_in_gate = self.C_inv_true * gamma_gate


class Nand(Gate):
    def __init__(self, name, beta_gate, beta_inv, gamma_gate, nb_input, metal:Metal, C_0_transistor, tau_ratio) -> None:
        super().__init__(name, beta_gate, beta_inv, gamma_gate, metal, C_0_transistor, tau_ratio)
        self.nb_input = nb_input
        self.g = (beta_gate + nb_input) / (self.C_inv)
        self.p = nb_input * (beta_gate + 1) / self.C_inv
        self.C_in_gate = gamma_gate * self.g * self.C_inv_true

class Nor(Gate):
    def __init__(self, name, beta_gate, beta_inv, gamma_gate, nb_input, metal:Metal, C_0_transistor, tau_ratio) -> None:
        super().__init__(name, beta_gate, beta_inv, gamma_gate, metal, C_0_transistor, tau_ratio)
        self.nb_input = nb_input
        self.g = (nb_input * beta_gate + 1) / (self.C_inv)
        self.p = nb_input * (beta_gate + 1) / self.C_inv
        self.C_in_gate = gamma_gate * self.g * self.C_inv_true

class Wire(Gate):
    def __init__(self, name, beta_gate, beta_inv, gamma_gate, metal:Metal, C_0_transistor, tau_ratio) -> None:
        super().__init__(name, beta_gate, beta_inv, gamma_gate, metal, C_0_transistor, tau_ratio)
        self.nb_input = 1
        self.C_in_gate = metal.Ctot
        self.p = 0
        self.g = self.C_in_gate / self.C_inv_true
        
        
class Branch(Gate):
    def __init__(self, name, gates:List[Gate]) -> None:
        """ 
        gates[0] -> gate used in the path
        """
        super().__init__(name, gates[0].beta_gate, gates[0].beta_inv, gates[0].gamma_gate, gates[0].metal, gates[0].C_0_transistor, gates[0].tau_ratio)
        self.nb_input = gates[0].nb_input
        self.g = gates[0].g
        self.p = gates[0].p
        self.C_in_gate = gates[0].C_in_gate
        self.gate_list = gates

        for i in range(1, len(gates)):
            self.C_off += gates[i].C_in_gate

    def __str__(self):
        last = " +-- "
        first = "---- "

        output = self.name + "\n"
        output += "\t" + first + self.gate_list[0].name + "\n"

        for i in range(1, len(self.gate_list)):
            output += "\t" + last + self.gate_list[i].name + "\n"
        
        return output
