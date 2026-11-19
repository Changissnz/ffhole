from types import MethodType,FunctionType
from collections import deque,defaultdict
from morebs2.matrix_methods import is_number 
import numpy as np 

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

        # used to store the result of calculating all constituent forms 
        # for element 
        self.ccache = deque() 
        return 

    def preproc(self,idn_func):

        for element in self.base_elements:
            self.e2info_map[element] = ({element},idn_func())  
        return 

    """
    main method #1 

    calculates all constituent forms pertaining to `element`, starting 
    from the `element`'s direct constituent form, moving down (in ordering 
    by idn) to every other constituent element's constituent forms.

    NOTE: the constituent form of an element is the output from its formulation 
          function, not necessarily the literal constituent identifiers for it. 
    """
    def constituent_forms(self,element): 
        assert element in self.e2info_map
        self.ccache.clear() 
        self.ccache.append(element)
        c_vec = [] 
        while len(self.ccache) > 0: 
            element_ = self.ccache.popleft() 
            C = self.constituent_form_(element_)
            c_vec.append(C) 
        return c_vec

    def constituent_form_(self,element): 
        # add the instability scores for all other elements 
        cx = self.e2info_map[element][0]
        f = self.e2info_map[element][1] 

        # case: no identities 
        if not cx == {element}:
            self.ccache.extend(sorted(cx)) 
        return f(element,cx)

    """
    main method #2 

    constituent chains of element, starting from its immediate 
    constituents till the base elements. 

    return:
    - list, every element E is a list of elements 
            that is a list of sets of elements: 

            E := [s_0,s_1,s_2,...]
            s_i := [set i0, set i1,...]. 

    NOTE: constituent chains are comprised of constituent identifiers, 
          which are not necessarily the forms. 
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
        self.scache = deque() 
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
    def instability_vec(self,element): 
        assert element in self.weight_map
        self.scache.clear() 
        self.scache.append(element) 

        # first instability score is that of element 
        i_vec = [self.weight_map[element]] 

        while len(self.scache) > 0: 
            element_ = self.scache.popleft() 
            i_vec2 = self.process_element_instability_(element_) 
            i_vec.extend(list(i_vec2)) 
        return i_vec

    def process_element_instability_(self,element):

        # add the instability scores for all other elements 
        cx = self.e2info_map[element][0] 
        f = self.e2info_map[element][1] 

        c_form = f(element,cx) 

        #   non-base constituents cannot be edges 
        non_base_constituents = [c for c in c_form if (c not in self.base_elements \
            and type(c) != tuple)]  

        #   the other instability scores 
        sx = self.e2info_map[element][2] 
        i_vec = sx(c_form,self.weight_map)

        self.scache.extend(non_base_constituents)
        return i_vec 