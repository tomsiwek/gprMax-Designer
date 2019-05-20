class TMaterial(object):
    """
    Class representing material with its properties.
    """
    def __init__(self, epsilon_r = 0.0, sigma = 0.0, mu_r = 0.0, sigma_mag = 0.0, name = ""):
        "Properties of a material are explained in gprMax user manual"
        self.epsilon_r = epsilon_r      # permitivity
        self.sigma = sigma              # conductivity
        self.mu_r = mu_r                # permeability
        self.sigma_mag = sigma_mag      # magnetic loss
        self.name = name                # identifier (name)
    
    def velocity(self):
        "Calculate elecromagnetic wave velocity in a medium"
        c = 299792458   # Speed of light in vacuum
        return c/(self.epsilon_r**(0.5))
