
class FQAgent: 

    def __init__(self): 
        self.error_term = 0.0 
        self.num_iterations = 0 

    def update_error_term(self,autocorrect_ratio):
        assert 0. <= autocorrect_ratio <= 1.

        q = (self.error_term * self.num_iterations) + autocorrect_ratio
        self.num_iterations += 1 
        self.error_term = q / self.num_iterations 
        return 

"""
unit agent for False Question Agent Swarm. 
"""
class FQSwarmAgent(FQAgent): 

    def __init__(self,idn,initial_answer,neighbor_agents:list): 
        super().__init__()

        self.idn = idn 
        self.initial_answer = initial_answer
        self.current_answer = initial_answer

        # stores answer from any sender 
        self.received_answer = None 

        # stores answer only from <FQSubjectAgent> 
        self.received_answer_from_subject = None 

        self.neighbor_agents = None 
        self.update_neighbor_agents(neighbor_agents) 

        self.inconsistent_subject_answers = 0 

        self.dec0 = None 
        return 

    def update_neighbor_agents(self,agents): 
        for x in agents: assert type(x) == FQSwarmAgent
        self.neighbor_agents = agents 

    def recv_answer(self,sender_ans,is_sender_subject:bool): 

        self.received_answer = sender_ans 

        if is_sender_subject: 
            if self.received_answer != self.received_answer_from_subject: 
                self.inconsistent_subject_answers += 1 
        
        # demand proof 
        if self.error_term < 0.5: 
            self.dec0 = "proof"
        # accept answer and pass to next 
        else: 
            self.current_answer = sender_ans 
            self.dec0 = "pass" 
        return 

    def send_answer(self,to_neighbors:bool): 
        return -1 

    """
    demand proof of answer or pass answer 
    """
    def decision_0(self): 
        return self.dec0 

    """
    accept or reject `received_answer`. 
    """
    def decision_p(self,pf,pf_score): 

        # accept new answer: 
        if pf_score < sum(pf.ve_score()) / 2.0: 
            self.current_answer = self.received_answer
            return "accept" 

        return "reject"

class FQAgentSwarm: 

    def __init__(self,swarm_agent_map:dict,swarm_graph:defaultdict,max_questions_per_round):  
        assert type(swarm_agent_map) == dict and type(swarm_graph) == defaultdict 
        assert set(swarm_agent_map.keys()) == set(swarm_graph.keys())
        assert graph_component_size(swarm_graph) == 1 

        self.swarm_agent_map = swarm_agent_map 
        self.swarm_graph = swarm_graph

        self.queue = deque() 
        return 

    #def preproc(self): 
    #    for k,v in self.swarm_agent_map.items(): 
    #        v.update_neighbor_agents()

    def idn_to_agent(self,idn): 
        return self.swarm_agent_map[idn] 

    def agent_exp_answers(self): 
        return {k:v.current_answer for k,v in self.swarm_agent_map.items()} 

    def agent_received_answers(self): 
        return {k:v.received_answer for k,v in self.swarm_agent_map.items()} 


"""
(F)alse (Q)uestion Subject, Type (D)elay and (D)ivert. 

Subject agent is to achieve an 
"""
class FQSubjectTypeDD(FQAgent): 

    def __init__(self,incon_func):  
        assert type(incon_func) == InconsistentFunctionTypeESAR
        super().__init__()

        self.incon_func = incon_func 
        return 

    def answer(self,s_agent:FQSwarmAgent):
        assert type(s_agent) == FQSwarmAgent

        return self.incon_func.answer

        return 

    def update_answer(self,a_idn,ans,answer_type): 
        self.incon_func.update_answer(a_idn,ans,answer_type) 

    @staticmethod 
    def generate_instance(agent_swarm:FQAgentSwarm,default_ans,possible_answer_set,missing_answer_ratio,\
        incorrect_answer_ratio,prg):  

        assert type(agent_swarm) == FQAgentSwarm
        assert default_ans in possible_answer_set and type(possible_answer_set) == set 

        # generate the inconsistent function 
        #       gather the swarm agent answers for the appropriate quality 
        agent2exp_map = agent_swarm.agent_exp_answers() 
        assert set(agent2exp_map.values()).issubset(possible_answer_set) 

        num_missing_answers = ceil(len(agent2exp_map) * missing_answer_ratio)
        num_incorrect_answers = ceil((len(agent2exp_map) - num_missing_answers) * incorrect_answer_ratio) 
        
        no_answers = prg_choose_n(sorted(agent2exp_map.keys()),num_missing_answers,prg,is_unique_picker=True) 
        for a in no_answers: agent2exp_map[a] = None 

        with_answers = set(agent2exp_map.keys()) - set(no_answers) 
        incorrect_answers = prg_choose_n(sorted(with_answers),num_incorrect_answers,prg,is_unique_picker=True) 
        for a in incorrect_answers: 
            actual = agent2exp_map[a] 
            alternatives = possible_answer_set - {actual} 

            if len(alternatives) == 0: continue 
            alternatives = sorted(alternatives) 
            i = int(prg()) % len(alternatives) 

            agent2exp_map[a] = alternatives[i] 

        #       gather the other variables 
        agent2recv_map = agent_swarm.agent_received_answers() 
        agent_relation_graph = deepcopy(agent_swarm.agent_relation_graph) 

        ifunc = InconsistentFunctionTypeESAR(default_ans,agent2exp_map,agent2recv_map,\
            agent_relation_graph,prg)

        

        return -1 