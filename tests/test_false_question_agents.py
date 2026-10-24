from automatons.false_question_agents import * 
import unittest

def sample_FQAgentSwarm__V20(prg): 
    num_agents = 20  
    possible_answer_set = {0,1,2,3,4,5} 
    max_agent_actions_per_round = 5 
    agent_prg_lcg_degree_range = [3,7] 

    return FQAgentSwarm.generate_instance(num_agents,possible_answer_set,\
        max_agent_actions_per_round,prg,agent_prg_lcg_degree_range,\
        edge_connectivity_range=[0.1,0.3])

"""
py -m tests.test_false_question_agents
"""
class FalseQuestionAgentMethods(unittest.TestCase):

    def test__FQSwarmAgent__recv_answer__case_1(self): 
        prg = prg__LCG(873.2,-633.63,68.66,97166.6) 

        fas = sample_FQAgentSwarm__V20(prg) 

        A9 = fas.idn_to_agent(9) 
        assert A9.answer() == 2 

        sender_ans = 4 

        A9.recv_answer(sender_ans,is_sender_subject=True) 
        assert A9.inconsistent_answers == 1 and A9.inconsistent_subject_answers == 0 
        assert A9.dec0 == "proof"
        assert A9.received_answer_from_subject == sender_ans
        assert A9.answer() == 2 

        A9.recv_answer(sender_ans,is_sender_subject=True) 
        assert A9.inconsistent_answers == 2 and A9.inconsistent_subject_answers == 0 
        assert A9.dec0 == "proof"

        sender_ans2 = 3 
        A9.recv_answer(sender_ans2,is_sender_subject=True) 
        assert A9.inconsistent_answers == 3 and A9.inconsistent_subject_answers == 1 
        assert A9.dec0 == "proof"

        sender_ans3 = 1 
        A9.recv_answer(sender_ans3,is_sender_subject=False) 
        assert A9.inconsistent_answers == 4 and A9.inconsistent_subject_answers == 1 
        assert A9.dec0 == "proof"

        A9.error_term = 0.5 
        A9.recv_answer(sender_ans3,is_sender_subject=False) 
        assert A9.dec0 == "pass"

    def test__FQSwarmAgent__decision_p__case_1(self): 
        prg = prg__LCG(873.2,-633.63,68.66,97166.6) 

        fas = sample_FQAgentSwarm__V20(prg) 

        A9 = fas.idn_to_agent(9) 
        assert A9.answer() == 2 

        sender_ans = 5 
        A9.recv_answer(sender_ans,is_sender_subject=True) 
        pf = NodePath.preload([5,6,7,9],[1,1,1]) 

        pscore0 = 3 
        d0 = A9.decision_p(pf,pscore0)
        assert d0 == "reject" 
        assert A9.answer() == 2 

        pscore1 = 1 
        d1 = A9.decision_p(pf,pscore1) 
        assert d1 == "accept" 
        assert A9.answer() == sender_ans

    def test__FQSubjectTypeDD__answer__case_1(self): 

        prg = prg__LCG(873.2,-633.63,68.66,97166.6) 
        fas = sample_FQAgentSwarm__V20(prg) 

        default_ans = 3 
        possible_answer_set = {0,1,2,3,4,5} 
        missing_answer_ratio = 0.5
        incorrect_answer_ratio = 0.5 
        prg0 = prg__LCG(73.2,33.63,-1168.66,1866.6) 
        fs = FQSubjectTypeDD.generate_instance(fas,default_ans,possible_answer_set,missing_answer_ratio,\
                incorrect_answer_ratio,prg0)

        # test out discrepancies between answers of Swarm Agents 5,7 and Subject 
        Q5 = set()
        for _ in range(100): 
            q = fs.answer(5)
            Q5 |= {q} 

        Q7 = set() 
        for _ in range(100): 
            q = fs.answer(7)
            Q7 |= {q} 

        assert Q5 == {3} == Q7 
        assert fas.idn_to_agent(5).answer() == 3 
        assert fas.idn_to_agent(7).answer() == 1 

        # now test out class variables 
        D = fs.incon_func.agent2exp_map 
        i,m = 0,0 
        for j in range(20): 
            if type(D[j]) == type(None): 
                m += 1 
                continue

            if D[j] != fas.idn_to_agent(j).answer(): 
                i += 1 

        assert i == 5 and m == 10 

        # test out accuracy of answering 
        D2 = dict() 
        for j in range(20): 
            D2[j] = fs.answer(j) 

        c = 0 
        for j in range(20): 
            if D2[j] == fas.idn_to_agent(j).answer(): 
                c += 1 
        assert c == 4, "got {}".format(c) 

if __name__ == '__main__':
    unittest.main()