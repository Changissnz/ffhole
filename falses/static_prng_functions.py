from seqbuild.intigers.mod_prng import * 
from morebs2.numerical_generator import prg__single_to_nvec,safe_modulo_in_range,\
    prg__single_to_int,prg_choose_n
from morebs2.measures import zero_div,zero_div_
from operator import sub,mul
from math import ceil 

DEFAULT_PRNG_NAIC__STD_PAIRWISE_OPS = [add,sub,mul,zero_div_] 
DEFAULT_PRNG_NAIC__NUM_OPS_RANGE = [3,9] 

"""
output PRNG struct <NoiseAddedIterableContainer> used by 
function<node_to_weight_vector_function__type_NAIC> and 
function<node_to_variable_subset_function__type_NAIC>. 
"""
def generate_PRNG_struct__type_NAIC(prg,cycle_length): 
    C = prg__single_to_nvec(prg,cycle_length)() 
    return NoiseAddedIterableContainer(list(C),v=None,op_first=True) 

"""
output PRNG struct <NoiseAddedIterableContainerV2> used by 
function<node_to_weight_vector_function__type_NAIC> and 
function<node_to_variable_subset_function__type_NAIC>. 
"""
def generate_PRNG_struct__type_NAIC_V2(prg,cycle_length,num_ops_range=DEFAULT_PRNG_NAIC__NUM_OPS_RANGE): 

    C = prg__single_to_nvec(prg,cycle_length)() 

    num_ops = safe_modulo_in_range(int(prg()),num_ops_range)

    l_range = [ceil(cycle_length * 1/2),cycle_length * 2]

    prg_ = prg__single_to_int(prg) 
    function_vec = prg_choose_n(DEFAULT_PRNG_NAIC__STD_PAIRWISE_OPS,num_ops,prg_,\
        is_unique_picker=False)
    X = NoiseAddedIterableContainerV2(list(C),l_range,v=None,function_vec=function_vec,op_first=True) 
    return X 