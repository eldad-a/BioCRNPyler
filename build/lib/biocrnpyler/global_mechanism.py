from warnings import warn

from .mechanism import Mechanism
from .chemical_reaction_network import reaction  
#Global mechanisms are a lot like mechanisms. They are called only by mixtures
#  on a list of all species have been generated by components. Global mechanisms are meant
#  to work as universal mechanisms that function on each species or all species of some
#  type or with some attribute. Global mechanisms may only act on one species at a time.
#
#In order to decide which species a global mechanism acts upon, the filter_dict is used.
#       filter_dict[specie.type / specie.attributes / specie.name / repr(specie)] = True / False
#  For each specie, its type, name, and attributes are sent through the filter_dict. If True
#  is returned, the GlobalMechanism will act on the species. If False is returned, the
#  the GlobalMechanism will not be called. If there are conflicts in the filter_dict, an error is raised.
#
#If the specie's name, type, and attributes are all not in the filter_dict, the GlobalMechanism will
#  be called if default_on == True and not called if default_on == False.
#Note that the above filtering is done automatically. Any parameters needed by the global mechanism must be
#  in the Mixture's parameter dictionary. These methods are assumed to take a sinlge species
#  as input.
#
#An example of a global mechanism is degradation via dilution which is demonstrated in the Tests folder.
#
#GlobalMechanisms should be used cautiously or avoided alltogether - the order in which they are called
# may have to be carefully user defined in the subclasses of Mixture in order to ensure expected behavior.

class GlobalMechanism(Mechanism):
    def __init__(self, name, type = "", filter_dict = {}, default_on = False):
        self.filter_dict = filter_dict
        self.default_on = default_on
        Mechanism.__init__(self, name = name, type = type)

    #applies the filter dictionary to determine if a global mechanism acts on a species
    def apply_filter(self, s):
        fd = self.filter_dict
        use_mechanism = None

        for a in s.attributes+[s.type, repr(s), s.name]:
            if a in fd:
                if use_mechanism == None:
                    use_mechanism = fd[a]
                elif use_mechanism != fd[a]:
                    raise AttributeError("species "+repr(s)+" has multiple attributes(or type) which conflict with global mechanism filter"+repr(self))

        if use_mechanism == None:
            use_mechanism = self.default_on

        return use_mechanism


    def update_species_global(self, species_list, parameters):
        new_species = []
        for s in species_list:
            use_mechanism = self.apply_filter(s)
            if use_mechanism:
                new_species += self.update_species(s, parameters)

        return new_species

    def update_reactions_global(self, species_list, parameters):
        fd = self.filter_dict
        new_reactions = []
        for s in species_list:
            use_mechanism = self.apply_filter(s)

            if use_mechanism:
                new_reactions += self.update_reactions(s, parameters)

        return new_reactions

    #All global mechanisms must use update_species functions with these inputs
    def update_species(self, s, parameters):
        return []

    #All global mechanisms must use update_reactions functions with these inputs
    def update_reactions(self, s, parameters):
        return []

class Dilution(GlobalMechanism):
    def __init__(self, name = "global_degredation_via_dilution", type = "dilution", filter_dict = {}, default_on = True):
        GlobalMechanism.__init__(self, name = name, type = type, default_on = True, filter_dict = filter_dict)

    def update_reactions(self, s, parameters):
        k_dil = parameters["kdil"]
        rxn = reaction([s], [], k_dil)
        return [rxn]

#Global Mechanism to Constutively Create Certain Species at the rate of dilution. 
#Useful for keeping machinery species like ribosomes and polymerases at a constant concentration.
class AnitDilutionConstiutiveCreation(GlobalMechanism):
    def __init__(self, name = "anti_dilution_constiuitive_creation", type = "dilution", filter_dict = {}, default_on = True):
        GlobalMechanism.__init__(self, name = name, type = type, default_on = False, filter_dict = filter_dict)

    def update_reactions(self, s, parameters):
        k_dil = parameters["kdil"]
        rxn = reaction([], [s], k_dil)
        return [rxn]
