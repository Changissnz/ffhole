from automatons.false_entry import * 
from morebs2.numerical_generator import prg__LCG
from xFS_bots.graph_models.graph_gen import * 
from xFS_bots.quant.cee_map import * 
import unittest

def run_FalseEntry_sample_R(G,max_active_agents,tstep_inaccuracy,num_entry,num_endpoints,\
    surface_prg,agent_prg,fe_prg): 

    node_weight_range = [10,300] ## [10.,10.]
    max_computation_size = 50 

    S = FESurface.generate_instance(G,node_weight_range,num_entry,num_endpoints,max_computation_size,surface_prg)

    A = FEAgentSpawn(agent_prg,"seq",deepcopy(S.end_points)) 

    max_agents = 2000 

    F = FalseEntry(S,A,fe_prg,max_active_agents,max_agents,\
        tstep_inaccuracy,verbose=False)

    for _ in range(100): 
        next(F) 

        # check for reset 
        assert F.surface.trapped_nodes() == set() 
        for n in F.surface.node_map.values(): assert n.weight == n.weight_appearance
    return F 

"""
return:
- G, agent PRNG, False Entry PRNG 
"""
def default_FalseEntry_test_varset(): 

    prg = prg__LCG(80.21,-512.5,521.54,6767.7) 
    S = SymmetricLatticeGraphGen((5,5),prg,(5,6),\
        is_dsg=False)
    S.make()

    G = S.G 
    prg2 = prg__LCG(56.4,-132.1,458.7,2020+76/79) 
    prg3 = prg__LCG(-565.4,133.5,-913.5,-9797.111) 

    return G,prg2,prg3 

"""
py -m tests.test_false_entry
"""
# NOTE: runtime on developer's device: approx. 180 seconds. 
class FalseEntryFunctions(unittest.TestCase):

    """
    test demonstrates poor agent passing rate @ 23.5%.
    """
    def test__FalseEntry__next__case_1(self): 
        G,prg2,prg3 = default_FalseEntry_test_varset() 

        max_active_agents = 10 
        tstep_inaccuracy = 0.0
        num_entry = 10#4 
        num_endpoints = 10#5 

        prg1 = prg__LCG(80.21,-512.5,521.54,6767.7) 

        F = run_FalseEntry_sample_R(G,max_active_agents,tstep_inaccuracy,num_entry,num_endpoints,\
            prg1,prg2,prg3)

        assert len(F.passed) == 24, "got {}".format(len(F.passed))
        assert len(F.terminated) == 102, "got {}".format(len(F.terminated))

    """
    test parameters identical to case #1, except for `tstep_inaccuracy`=0.5. 

    test demonstrates worse agent passing rate @ 14.5%.
    """
    def test__FalseEntry__next__case_2(self): 
        G,prg2,prg3 = default_FalseEntry_test_varset() 

        max_active_agents = 10    
        tstep_inaccuracy = 0.5 
        num_entry = 10#4 
        num_endpoints = 10#5 

        prg1 = prg__LCG(80.21,-512.5,521.54,6767.7) 

        F = run_FalseEntry_sample_R(G,max_active_agents,tstep_inaccuracy,num_entry,num_endpoints,\
            prg1,prg2,prg3)

        assert len(F.passed) == 12
        assert len(F.terminated) == 83  

    """
    test parameters identical to case #2, except for `tstep_inaccuracy`=1.0. 

    test demonstrates worse agent passing rate @ 8.8%.
    """
    def test__FalseEntry__next__case_3(self): 

        G,prg2,prg3 = default_FalseEntry_test_varset() 

        max_active_agents = 10    
        tstep_inaccuracy = 1.0 
        num_entry = 10#4 
        num_endpoints = 10#5 

        prg1 = prg__LCG(80.21,-512.5,521.54,6767.7) 

        F = run_FalseEntry_sample_R(G,max_active_agents,tstep_inaccuracy,num_entry,num_endpoints,\
            prg1,prg2,prg3)

        assert len(F.passed) == 8
        assert len(F.terminated) == 90 

    """
    test demonstrates zero agent passing rate.
    """
    def test__FalseEntry__next__case_3(self): 

        G,prg2,prg3 = default_FalseEntry_test_varset() 

        max_active_agents = 2  
        tstep_inaccuracy = 0.0
        num_entry = 10#4 
        num_endpoints = 10#5 

        prg1 = prg__LCG(80.21,-512.5,521.54,6767.7) 

        F = run_FalseEntry_sample_R(G,max_active_agents,tstep_inaccuracy,num_entry,num_endpoints,\
            prg1,prg2,prg3)

        assert len(F.passed) == 0, "got {}".format(len(F.passed))
        assert len(F.terminated) == 144, "got {}".format(len(F.terminated))  

    """
    test demonstrates 51.2% agent passing rate. 
    """
    def test__FalseEntry__next__case_4(self): 
        G,prg2,prg3 = default_FalseEntry_test_varset() 

        max_active_agents = 50  
        tstep_inaccuracy = 0.0
        num_entry = 10#4 
        num_endpoints = 10#5 

        prg1 = prg__LCG(80.21,-512.5,521.54,6767.7) 

        F = run_FalseEntry_sample_R(G,max_active_agents,tstep_inaccuracy,num_entry,num_endpoints,\
            prg1,prg2,prg3)

        assert len(F.passed) == 150, "got {}".format(len(F.passed))
        assert len(F.terminated) == 293, "got {}".format(len(F.terminated))

if __name__ == '__main__':
    unittest.main()