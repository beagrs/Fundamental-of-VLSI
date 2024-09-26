#
#   Define Metal Wire
#

from quantiphy import Quantity

class Metal:
    def __init__(self, name, layer, width, length, S, isWL:bool) -> None:
        """
        Length, Width and S (distance between wires) must be expressed in um
        """
        self.name = name
        self.layer = layer
        self.width = width
        self.length = length
        self.area = length * width
        self.S = S
        self.S_0 = 0.1
        self.isWL = isWL
        self.set_cap()
        self.compute_wire_delay()
    
    def __str__(self):
        return self.name + "\n" + "\tL = " + str(self.length) + "\n" + "\tR_tot = " + str(Quantity(self.R, 'Ohm')) + "\n" + "\tW = " + str(self.width) + "\n" + "\tC_wire = " + str(Quantity(self.C_wire, 'F')) + "\n" + "\tC_tot = " + str(Quantity(self.Ctot, 'F')) + "\n" + "\tDelay = " + str(Quantity(self.tau, 's')) + "\n"
    
    def set_cap(self):
        # Define for metal 2 and metal 3. If other metal layers are inserted consider a zero parasitic
        # Capacitance normalized by the area [F / um^2]
        match self.layer:
            case 2:
                self.Cpp = 0.048e-15    # Parallel plate cap
                self.Cf = 0.009e-15     # Fringe cap
                self.Cc = 0.071e-15     # Coupling cap @ min distance
                self.R0 = 105e-3        # R_square
            case 3:
                self.Cpp = 0.034e-15
                self.Cf = 0.008e-15
                self.Cc = 0.072e-15
                self.R0 = 105e-3
            case _:
               self.Cpp = self.Cf = self.Cc = self.R0 = 0
        
        # Area of the wire = width * lengh (in um)
        self.C_wire = self.length * (self.width * self.Cpp + self.Cf)       # Total Wire capacitance
        self.R = self.R0 * self.length / self.width
        
        if (self.isWL):
            self.Cc = 3 * self.Cc * self.S_0 / self.S * self.length

        else:
            self.Cc =  4 * self.Cc * self.S_0 / self.S * self.length

        self.Ctot = self.C_wire + self.Cc       # Total capacitance

    def compute_wire_delay(self):
        self.tau = 0.69/2 * self.R * self.Ctot

        
