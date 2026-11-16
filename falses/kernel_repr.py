from types import MethodType,FunctionType

def identity_form_function(): 

    def f(x): 
        return x 

    return f 


"""
Kernel Representation Type (D)erivable (C)onstituent (C)omposition. 
"""
class KernelReprTypeDCC: 

    def __init__(self,base_element_seq): 
        assert type(base_element_seq) == list and \
            len(base_element_seq) == len(set(base_element_seq))
        self.base_elements = base_element_seq

        # element idn -> (constituent set of element idns,formulation function to produce it) 
        self.e2info_map = dict() 
        self.preproc() 
        return 

    def preproc(self):

        for element in self.base_elements:
            self.e2info_map[element] = ({element},identity_form_function()) 
        return 

    def add_element(self,element,constituents,form_func): 
        assert element not in self.e2info_map, "element {} already stored!".format(element)
        for c in constituents: 
            assert c in self.e2info_map, "constituent {} not found in kernel".format(c) 
        assert type(form_func) in {MethodType,FunctionType}
        self.e2info_map[element] = (constituents,form_func)
        return 

    """
    constituent chains of element, starting from its immediate 
    constituents till the base elements. 
    """
    def constituent_chains(self,element):

        # case: element is base: 
        if element in self.base_elements: return [] 

        x = sorted(self.e2info_map[element][0]) 

        # used to store running result 
        q0 = [[[{x_}]] for x_ in x]
        # used to store elements to map to constituents 
        q1 = [[x_] for x_ in x] 

        # for queues q0,q1 
        stat_q = [False for x_ in x] 

        stat = True 

        while stat: 

            for (i,q_) in enumerate(q0): 
                r = q1[i] 
                r2 = [] 
                r2_ = [] 
                for r_ in r: 
                    C = self.e2info_map[r_][0]
                    print("CX: ",C)
                    # case: element is base 
                    if C == {r_}: 
                        continue 
                    
                    C_ = sorted(C) 
                    r2.append(C) 
                    r2_.extend(C_) 
                
                # case: no more constituents 
                if len(r2_) == 0: 
                    stat_q[i] = True 
                    continue 
                q_.append(r2) 
                q1[i] = r2_ 

            stat = stat_q.count(False)  
        return q0 

    def degree_of_element(self,element): 
        if element not in self.e2info_map: return -1 

        x = self.constituent_chains(element)
        return self.constituent_chain_to_degree(x) 

    def constituent_chain_to_degree(self,C): 
        if len(C) == 0: return 0 

        q = [len(c) for c in C] 
        return max(q)

