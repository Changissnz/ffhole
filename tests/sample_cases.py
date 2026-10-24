from falses.question_swps import * 
from xFS_bots.graph_models.graph_gen import * 
import unittest

def sample_QuestionTypeSWPS__V22(prg,\
    proof_simulation_output_space_range=\
        DEFAULT_QUESTION_PROOF_SIMULATION_OUTPUT_SPACE_RATIO_RANGE): 
    is_dsg = False 
    is_realtime_gen = True 
    vertex_degree = 22 
    edge_connectivity = 0.2 
    verbose = False 

    gg = GraphGen(is_dsg,prg,is_realtime_gen,\
        vertex_degree,edge_connectivity,verbose)
    gg.full_run() 
    G = gg.d 
    G = graph_to_one_component(G,prg) 

    answer_set = {0,1,2,3,4,5} 
    node_path_soln_size_range = [2,6] 
    max_num_path_corrections_range = [2,7] 
    start_node_for_paths = 3 

    return QuestionTypeSWPS(G,answer_set,node_path_soln_size_range,\
        max_num_path_corrections_range,prg,start_node_for_paths=None,\
        proof_simulation_output_space_range=proof_simulation_output_space_range) 

'''
ObjectiveTypeEFIT(ObjectiveTypeUSGMP): 

    def __init__(self,G,start_node,node_path_solution_seq): 
''' 