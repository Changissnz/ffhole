from falses.state_induction import * 
import unittest

"""
py -m tests.test_state_induction
"""
class StateInductionTypeMFUCMethods(unittest.TestCase):

    def test__StateInductionTypeMFUC__multiple_methods__case_1(self): 
        state_set = {3,4,23,12} 
        initial_hs_hyp = {3:{14,13},4:{233,411},23:{76,59,110},12:{396,544,100,43}} 

        si = StateInductionTypeMFUC(state_set,initial_hs_hyp=deepcopy(initial_hs_hyp)) 

        # check that state induction equals initial hypothesis 
        assert si.state_induction() == initial_hs_hyp

        si.add_frequencies_to_category(3,{101:45,456:45,222:44}) 
        si.update_induction() 

        # state induction changes at state=3, by most frequent
        q1 = si.state_induction()
        for x in state_set: 
            if x == 3: 
                assert q1[x] != initial_hs_hyp[x]
                assert q1[x] == {101,456}, "got {}".format(q1[x])
            else: 
                assert q1[x] == initial_hs_hyp[x] 
        #   check frequency map 
        assert si.fmap == defaultdict(dict,{3: {101:45,456:45,222:44}})

        #   check frequency map 
        si.add_frequencies_to_category(3,{101:20,456:20,222:14}) 
        assert si.fmap == defaultdict(dict,{3: {101:45+20,456:45+20,222:44+14}})
        si.update_induction() 
        assert si.state_induction() == {3:{101,456},4:{233,411},23:{76,59,110},12:{396,544,100,43}} 

        # set certain category 
        si.set_certain_category(3,{452}) 
        q2 = si.state_induction()

        # check that category=3 outputs {452}, even though it is not most frequent 
        for x in state_set: 
            if x == 3: 
                assert q2[x] != initial_hs_hyp[x] and q2[x] == {452} 
            else: 
                assert q2[x] == initial_hs_hyp[x] 

        # add frequency of 1011 to 3 
        si.add_frequencies_to_category(3,{1011:2000}) 

        # check that category=3 outputs {452}, even though it is not most frequent 
        q3 = si.state_induction()
        for x in state_set: 
            if x == 3: 
                assert q3[x] != initial_hs_hyp[x] and q3[x] == {452} 
            else: 
                assert q3[x] == initial_hs_hyp[x] 


if __name__ == '__main__':
    unittest.main()