from .prdcc_model import * 
from .label_intrp import * 

"""
(A)uto-(G)enerating Chained Label Interpreter Type (C)lass-(E)xpected (E)ffect. 

Starts with an initial <LabelInterpreterTypeCEE> and complementary <KernelReprTypeDCCWSM>. 
""" 
class AGChainedLabelInterpreterTypeCEE: 

    def __init__(self,c2w_map:dict,prg,form_type): 
        assert type(prg) in {MethodType,FunctionType}

        self.prg = prg 
        self.preproc(c2w_map,form_type) 
        return

    def preproc(self,c2w_map:dict,form_type): 
        label_seq = sorted(c2w_map.keys()) 
        label_seq = [str(ls) for ls in label_seq]
        self.pfgen = PRDCCFunctionGen(label_seq,self.prg,form_type)
        int_label_seq = [str(self.pfgen.element_to_int_label(l)) for l in label_seq]
        
        self.I = LabelInterpreterTypeCEE(deepcopy(label_seq)) 
        c2w_map_ = {str(self.pfgen.element_to_int_label(k)): v for k,v in c2w_map.items()}

        self.K = KernelReprTypeDCCWSM(int_label_seq,c2w_map_,idn_func=generate_form__identity)
        return


    def update_with_s_path(self,element,skew,skew_direction=1,is_literal_label:bool=False): 

        ix = self.pfgen.element_to_int_label(element) 
        P = self.I.label_to_s_path(element,skew,skew_direction)
        M = self.I.path_to_lmap(P)

        # iterate through every index and check for existence 
        l = len(self.I) 
        for i in range(l): 
            E = M[i]
            self.update_kernel(E) 
        return 

    def update_kernel(self,element): 
        element_ = set([str(self.pfgen.element_to_int_label(el)) for el in element]) 

        # case: element already found 
        if element in self.pfgen: 
            return 

        self.pfgen.add_element(element) 
        i = self.pfgen.element_to_int_label(element) 

        f0,f1 = self.pfgen.l2f_map[i]
        self.add_edge_weights(i,element,f0)

        w = float(round(prg_decimal(self.prg,[0.,1.]),5))
        self.K.add_element(str(i),element_,f0,f1,w)
        return 

    def add_edge_weights(self,idn,element,f0): 
        # case: edge weights pertain only to G-form. 
        if self.pfgen.ftype == "P": return 

        qx = f0(idn,element)

        new_weights = dict() 
        for q in qx: 
            if type(q) != tuple: 
                continue 

            q_ = (str(self.pfgen.element_to_int_label(q[0])),str(self.pfgen.element_to_int_label(q[1]))) 
            if q_ in self.K.weight_map:
                continue 

            new_weights[q_] = float(round(prg_decimal(\
                self.prg,[0.,1.]),5))

        self.K.add_weights(new_weights,overwrite_elements=False) 