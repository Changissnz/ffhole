from xFS_bots.graph_models.micrograph import * 
from xFS_bots.graph_models.graph_gen import * 
from morebs2.matrix_methods import is_valid_range
from morebs2.numerical_generator import prg_decimal,modulo_in_range
from morebs2.measures import zero_div

"""
Uncertainty Simulator Type (G)enerated (G)raph (D)ifferential.

For every output measure of uncertainty, compares the generated graph 
from an external PRNG with `prg`. 
"""
class UncertaintySimulatorTypeGGD: 

    def __init__(self,prg,vertex_degree_range,edge_connectivity_range): 
        assert is_valid_range(vertex_degree_range,True,False) 
        assert is_valid_range(edge_connectivity_range,False,False) 

        self.prg = prg  
        self.vd_range = vertex_degree_range
        self.ec_range = edge_connectivity_range
        return 

    def cmp(self,ext_prg): 
        is_dsg = int(self.prg()) % 2 
        is_realtime_gen = prg_decimal(self.prg,[0.,1]) > 0.5
        vertex_degree = modulo_in_range(int(self.prg()),self.vd_range)
        edge_connectivity = modulo_in_range(self.prg(),self.ec_range) 

        G0 = GraphGen(is_dsg,self.prg,is_realtime_gen,vertex_degree,edge_connectivity)
        G0.full_run()

        G1 = GraphGen(is_dsg,ext_prg,is_realtime_gen,vertex_degree,edge_connectivity)
        G1.full_run()

        d0,d1 = G0.d,G1.d 

        M0,M1 = MicroGraph(d0),MicroGraph(d1) 

        s00 = M0.ve_score()
        s01 = M0.sub_ve_score(M1)

        s10 = M1.ve_score()
        s11 = M1.sub_ve_score(M0)

        d = np.sum(np.array(s00) + np.array(s10))
        n = np.sum(np.array(s01) + np.array(s11))
        return zero_div(n,d,1.0) 