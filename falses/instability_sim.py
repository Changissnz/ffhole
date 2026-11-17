from .label_intrp import * 
from .kernel_repr import * 

"""
Type (D)erivable (C)onstituent (C)omposition. 
"""
class InstabilitySimulatorTypeDCC: 

    def __init__(self,K:KernelReprTypeDCCWSM,I:LabelInterpreterTypeCEE,ivec_map_function):
        assert type(K) == KernelReprTypeDCCWSM
        assert type(I) == LabelInterpreterTypeCEE 
        assert type(ivec_map_function) in {MethodType,FunctionType} 
        self.K = K 
        self.I = I 
        self.ivm_function = ivec_map_function
        return 

    def exec(self,primary_prng,secondary_prng,label,skew_path,skew_direction=1):  

        q = self.I.label_to_s_path(label,skew,skew_direction)
        i_vec = self.K.process_element(label) 
        return self.ivm_function(i_vec,primary_prng,secondary_prng)  