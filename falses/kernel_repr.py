from types import MethodType,FunctionType
from collections import deque,defaultdict
from morebs2.matrix_methods import is_number 

def identity_form_function(): 

    def f(x,constituents): 
        return x 
    return f 

def instability_score_vector(c_form_seq,weight_map): 
    return [weight_map[c] for c in c_form_seq]


"""
Kernel Representation Type (D)erivable (C)onstituent (C)omposition. 
"""
class KernelReprTypeDCC: 

    def __init__(self,base_element_seq,idn_func=identity_form_function): 
        assert type(base_element_seq) == list and \
            len(base_element_seq) == len(set(base_element_seq))
        self.base_elements = base_element_seq

        # element idn -> (constituent set of element idns,formulation function to produce it) 
        self.e2info_map = dict() 
        self.preproc(idn_func) 

        # used to store the result of processing an element 
        self.pcache = deque() 
        return 

    def preproc(self,idn_func):

        for element in self.base_elements:
            self.e2info_map[element] = ({element},idn_func())  
        return 

    """
    main method #1 

    processes all elements of constituent chains that comprise element  
    """
    def process_element(self,element): 
        C = self.constituent_chains(element) 

        self.pcache.clear() 

        for C_ in C: 
            q = self.process_one_c_chain(C_) 
            for q_ in q: self.pcache.append(q_)
        return list(self.pcache) 

    def process_one_c_chain(self,c_chain:list): 
        for c in c_chain: 
            yield self.process_element_setseq(c) 

    def process_element_setseq(self,element_seq:list): 
        q = [] 
        for x in element_seq: 
            x_ = sorted(x)
            for x1 in x_: 
                cx = self.e2info_map[x1][0] 
                f = self.e2info_map[x1][1] 
                q.append(f(x1,cx)) 
        return q 

    """
    main method #2 

    constituent chains of element, starting from its immediate 
    constituents till the base elements. 

    return:
    - list, every element E is a list of elements 
            that is a list of sets of elements: 

            E := [s_0,s_1,s_2,...]
            s_i := [set i0, set i1,...]. 
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

    """
    main method #3 
    """
    def add_element(self,element,constituents,form_func): 
        assert element not in self.e2info_map, "element {} already stored!".format(element)
        for c in constituents: 
            assert c in self.e2info_map, "constituent {} not found in kernel".format(c) 
        assert type(form_func) in {MethodType,FunctionType}
        self.e2info_map[element] = (constituents,form_func)
        return 

    def degree_of_element(self,element): 
        if element not in self.e2info_map: return -1 

        x = self.constituent_chains(element)
        return self.constituent_chains_to_degree(x) 

    def constituent_chains_to_degree(self,C): 
        if len(C) == 0: return 0 

        q = [len(c) for c in C] 
        return max(q)

"""
Kernel Representation Type (D)erivable (C)onstituent (C)omposition (W)ith (S)tability (M)easures.
"""
class KernelReprTypeDCCWSM(KernelReprTypeDCC): 

    def __init__(self,base_element_seq,weight_map,idn_func=identity_form_function): 
        self.weight_map = weight_map  

        super().__init__(base_element_seq,idn_func)
        return 

    def preproc(self,idn_func): 
        for x in self.base_elements: 
            self.e2info_map[x] = ({x},idn_func(),instability_score_vector,self.weight_map[x]) 

    def add_element(self,element,constituents,form_func,s_func,weight_value): 
        assert element not in self.e2info_map, "element {} already stored!".format(element)
        for c in constituents: 
            assert c in self.e2info_map, "constituent {} not found in kernel".format(c) 
        assert type(form_func) in {MethodType,FunctionType}
        assert type(s_func) in {MethodType,FunctionType}
        assert is_number(weight_value)
        self.e2info_map[element] = (constituents,form_func,s_func)
        self.weight_map[element] = weight_value
        return

    """
    NOTE: method used in the case of graphs, where edges exist between elements 
    """
    def add_weights(self,weight_map,overwrite_elements:bool= True): 

        if not overwrite_elements: 
            q = set(weight_map.keys()).intersection(set(self.weight_map.keys())) 
            assert not len(q)

        self.weight_map.update(weight_map)
        return 

    """
    return:
    - np.ndarray, one-dimensional vector of instability scores mapped from the constituent 
        chains of the element. 
    """
    def process_element(self,element): 
        q = super().process_element(element) 
        q1 = [] 
        for q_ in q: q1.extend(q_) 
        return np.array(q1)  

    def process_element_setseq(self,element_seq:list): 
        q = [] 
        for x in element_seq: 
            x_ = sorted(x)
            for x1 in x_: 
                cx = self.e2info_map[x1][0] 
                f = self.e2info_map[x1][1] 

                c_form = f(x1,cx) 
                s_func = self.e2info_map[x1][2] 
                i_vec = s_func(c_form,self.weight_map)
                q.append(i_vec)  
        return q 