#
#   Optimum Sizing
#

from typing import List
from gate import *
from circuit import *
import math

RHO = 3.5911214766686221366492229257416

def copy_gate(gate:Inverter|Nand|Nor|Wire, new_gamma) -> Inverter|Nand|Nor:
    
    if type(gate) == Inverter:
        new_gate = Inverter(gate.name + "_opt", gate.beta_gate, gate.beta_inv, new_gamma, gate.metal, gate.C_0_transistor, gate.tau_ratio)
    
    elif type(gate) == Nand:
        new_gate = Nand(gate.name + "_opt", gate.beta_gate, gate.beta_inv, new_gamma, gate.nb_input, gate.metal, gate.C_0_transistor, gate.tau_ratio)
    
    #elif type(gate) == Wire:
    #    new_gate = Wire(gate.name + "_optimized", gate.beta_gate, gate.beta_inv, new_gamma, gate.metal, gate.C_0_transistor, gate.tau_ratio)
    else:
        new_gate = Nor(gate.name + "_opt", gate.beta_gate, gate.beta_inv, new_gamma, gate.nb_input, gate.metal, gate.C_0_transistor, gate.tau_ratio)

    return new_gate

def copy_branch(branch:Branch, new_gamma) -> Branch:
    optimized_branch = []
    for gate in branch.gate_list:
        optimized_branch.append(copy_gate(gate, new_gamma))
    return Branch(branch.name + "_opt", optimized_branch)


def optimized_gamma_vector(original_circuit:Circuit):
    gamma_vector = np.ones(original_circuit.N)
    gamma_vector[0] = original_circuit.circuit_gates[0].gamma_gate

    for i in range(1, original_circuit.N):
        if isinstance(original_circuit.circuit_gates[i], Wire):
            gamma_vector[i] = 1
        else:
            gamma_vector[i] = gamma_vector[i-1] * original_circuit.f_hat / (original_circuit.circuit_gates[i-1].b * original_circuit.g_vector[i])

    return gamma_vector


def optimize_circuit_size(original_circuit:Circuit):
    gamma_vector = optimized_gamma_vector(original_circuit)
    optimized_circuit = []
    for i in range(original_circuit.N):
        if type(original_circuit.circuit_gates[i]) == Branch:
            optimized_circuit.append(copy_branch(original_circuit.circuit_gates[i], gamma_vector[i]))
        
        elif type(original_circuit.circuit_gates[i]) == Wire:
            optimized_circuit.append(original_circuit.circuit_gates[i])
            
        else:
            optimized_circuit.append(copy_gate(original_circuit.circuit_gates[i], gamma_vector[i]))

    return Circuit(original_circuit.name + "_optimized", optimized_circuit, original_circuit.tau_2, original_circuit.tau_ratio, original_circuit.final_load)

def d_min_inverter(N, C_load, C_in, tau_ratio):
    return N * tau_ratio + N * pow(C_load / C_in, 1/N)

def optimal_nb_buffer(C_load, C_in, tau_ratio):
    H = C_load / C_in
    stages_rho_3_59 = 1/math.log(RHO, H)
    stage_rho_4 = 1/math.log(4, H)
    upper_even = math.ceil(stages_rho_3_59 / 2.) * 2
    lower_even = upper_even - 2
    print(f"Optimal stages number (rho = 3.59) = {stages_rho_3_59}")
    print("the delay is expressed in multiples of TAU_2 and it's only related to the buffers")
    print(f"\t -> delay (exact) = {d_min_inverter(stages_rho_3_59, C_load, C_in, tau_ratio)}")
    print(f"\t -> delay (N = {round(stages_rho_3_59)}) = {d_min_inverter(round(stages_rho_3_59), C_load, C_in, tau_ratio)}")
    print()
    print(f"Optimal stages number (rho = 4) = {stage_rho_4}")
    print(f"\t -> delay (exact) = {d_min_inverter(stage_rho_4, C_load, C_in, tau_ratio)}")
    print(f"\t -> delay (N = {round(stage_rho_4)}) = {d_min_inverter(round(stage_rho_4), C_load, C_in, tau_ratio)}")
    print()
    print(f"Upper even N = {upper_even}")
    print(f"\t -> delay = {d_min_inverter(upper_even, C_load, C_in, tau_ratio)}")
    print()
    print(f"Lower even N = {lower_even}")
    if (lower_even > 0):
        print(f"\t -> delay = {d_min_inverter(lower_even, C_load, C_in, tau_ratio)}")
    else:
        print("\t0 stages does not make sense")