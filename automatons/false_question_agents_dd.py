from falses.question_swps import * 
from falses.incon_esar import * 
from morebs2.numerical_generator import prg_to_LCG_stack,merge_two_prgs
from xFS_bots.graph_models.graph_gen import * 
from xFS_bots.graph_models.community import graph_component_size

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

    def __init__(self,idn,initial_answer,possible_answer_set:set,prg):  
        super().__init__()

        assert initial_answer in possible_answer_set
        assert type(possible_answer_set) == set and len(possible_answer_set) > 1 
        assert idn != "subject" 

        self.idn = idn 
        self.initial_answer = initial_answer
        self.current_answer = initial_answer
        self.answer_set = possible_answer_set
        self.prg = prg 

        # stores answer from any sender 
        self.received_answer = None 

        # stores answer only from <FQSubjectAgent> 
        self.received_answer_from_subject = None 

        self.neighbor_agents = None 
        self.inconsistent_subject_answers = 0 
        self.inconsistent_answers = 0 

        self.dec0 = None 
        return 

    def recv_answer(self,sender_ans,is_sender_subject:bool): 

        self.received_answer = sender_ans 

        if is_sender_subject: 
            if self.received_answer != self.current_answer: 
                self.inconsistent_subject_answers += 1 
            self.received_answer_from_subject = sender_ans 

        if self.received_answer != self.current_answer: 
            self.inconsistent_answers += 1 

        # demand proof 
        if self.error_term < 0.5: 
            self.dec0 = "proof"
        # accept answer and pass to next 
        else: 
            self.current_answer = sender_ans 
            self.dec0 = "pass" 
        return 

    def answer(self): 
        return self.current_answer 

    def contra_answer(self,given_ans): 
        q = sorted(self.answer_set - {given_ans}) 
        i = int(self.prg()) % len(q) 
        return q[i]

    """
    demand proof of answer or pass answer 
    """
    def decision_0(self): 
        return self.dec0 

    """
    accept or reject `received_answer`. 
    """
    def decision_p(self,pf,pf_score): 

        assert type(pf) == NodePath 
        # accept new answer: 
        if pf_score < (len(pf) - 1) / 2.0: 
            self.current_answer = self.received_answer
            return "accept" 

        return "reject"

class FQAgentSwarm: 

    def __init__(self,swarm_agent_map:dict,swarm_graph:defaultdict,max_agent_actions_per_round):  
        assert type(swarm_agent_map) == dict and type(swarm_graph) == defaultdict 
        assert set(swarm_agent_map.keys()) == set(swarm_graph.keys())
        assert graph_component_size(swarm_graph) == 1 

        self.swarm_agent_map = swarm_agent_map 
        self.swarm_graph = swarm_graph
        self.max_agent_actions_per_round = max_agent_actions_per_round

        self.preproc() 
        return 

    def preproc(self): 
        idns = sorted(self.swarm_agent_map) 
        self.collective_prg = self.swarm_agent_map[idns[0]].prg 

        operators = [add,sub] 
        for i in range(1,len(idns)): 
            prg2 = self.swarm_agent_map[idns[i]].prg 
            operator = operators[(i - 1) % 2] 
            self.collective_prg = merge_two_prgs(self.collective_prg,prg2,operator) 

        self.agent_action_ctr_map = defaultdict(int) 
        return 

    def active_neighbor_agents(self,a_idn):
        N = self.neighbors_of_agent(a_idn) 
        return {n for n in N if self.agent_action_ctr_map[n] < self.max_agent_actions_per_round}  

    def neighbors_of_agent(self,a_idn): 
        assert a_idn in self.swarm_graph 
        return self.swarm_graph[a_idn] 

    def first_q_agent(self): 
        idns = sorted(self.swarm_agent_map) 
        i = int(self.collective_prg()) % len(idns) 
        return self.swarm_agent_map[i] 

    def idn_to_agent(self,idn): 
        return self.swarm_agent_map[idn] 

    def agent_exp_answers(self): 
        return {k:v.current_answer for k,v in self.swarm_agent_map.items()} 

    def agent_received_answers(self): 
        return {k:v.received_answer for k,v in self.swarm_agent_map.items()} 

    def update_action_ctr(self,a_idn): 
        self.agent_action_ctr_map[a_idn] += 1 

    def error_terms(self):
        return {k:v.error_term for k,v in self.swarm_agent_map.items()}

    def inconsistency_map(self): 
        return {k:(v.inconsistent_subject_answers,v.inconsistent_answers) for k,v in self.swarm_agent_map.items()}

    """
    clear error terms and inconsistent answer counts. 
    """
    def clear_counters(self): 
        for v in self.swarm_agent_map.values(): 
            v.error_term = 0. 
            v.num_iterations = 0 
            v.inconsistent_subject_answers = 0 
            v.inconsistent_answers = 0 
        return

    @staticmethod
    def generate_instance(num_agents,possible_answer_set,max_agent_actions_per_round,prg,\
        agent_prg_lcg_degree_range,edge_connectivity_range=[0.1,0.3]):

        assert 1 < num_agents < 51, "max of 50 agents!" 
        answers = prg_choose_n(sorted(possible_answer_set),num_agents,\
            prg__single_to_int(prg),is_unique_picker=False)

        prng_seq = [] 
        for _ in range(num_agents): 
            degree = modulo_in_range(int(prg()),agent_prg_lcg_degree_range) 
            prg2 = prg_to_LCG_stack(prg,degree,[add,sub]) 
            prng_seq.append(prg2) 
        
        swarm_agent_map = dict() 
        for i,(a,p) in enumerate(zip(answers,prng_seq)): 
            A = FQSwarmAgent(i,a,deepcopy(possible_answer_set),p) 
            swarm_agent_map[i] = A 
        
        edge_connectivity = modulo_in_range(prg(),edge_connectivity_range)
        gg = GraphGen(is_dsg=False,prg=prg,is_realtime_gen=bool(int(prg()) % 2),\
            vertex_degree=num_agents,edge_connectivity=edge_connectivity) 
        gg.full_run() 
        swarm_graph = graph_to_one_component(gg.d,prg) 

        return FQAgentSwarm(swarm_agent_map,swarm_graph,max_agent_actions_per_round)

"""
(F)alse (Q)uestion Subject, Type (D)elay and (D)ivert. 

Subject agent is to achieve an 
"""
class FQSubjectTypeDD(FQAgent): 

    def __init__(self,incon_func):  
        assert type(incon_func) == InconsistentFunctionTypeESAR
        super().__init__()

        self.incon_func = incon_func 
        self.prg = self.incon_func.prg 

        self.num_queries = 0
        # used to keep track of accepted and rejected proofs 
        self.accepts = 0  
        self.rejects = 0 
        return 

    def load_prg(self,prg): 
        assert type(prg) in {MethodType,FunctionType}
        self.incon_func.prg = prg 
        self.prg = prg 

    def answer(self,a_idn):
        self.num_queries += 1 
        return self.incon_func.answer(a_idn)

    def update_ar_count(self,do_accept:bool): 
        if do_accept: self.accepts += 1 
        else: self.rejects += 1 

    def update_answer(self,a_idn,ans,answer_type): 
        self.incon_func.update_answer(a_idn,ans,answer_type) 

    def clear_counters(self): 
        self.incon_func.inconsistency_count.clear() 
        self.num_queries = 0 
        self.accepts = 0 
        self.rejects = 0 

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

        prg_ = prg__single_to_int(prg)
        no_answers = prg_choose_n(sorted(agent2exp_map.keys()),num_missing_answers,prg_,is_unique_picker=True) 
        for a in no_answers: agent2exp_map[a] = None 

        with_answers = set(agent2exp_map.keys()) - set(no_answers) 
        incorrect_answers = prg_choose_n(sorted(with_answers),num_incorrect_answers,prg_,is_unique_picker=True) 
        for a in incorrect_answers: 
            actual = agent2exp_map[a] 
            alternatives = possible_answer_set - {actual} 

            if len(alternatives) == 0: continue 
            alternatives = sorted(alternatives) 
            i = int(prg()) % len(alternatives) 

            agent2exp_map[a] = alternatives[i] 

        #       gather the other variables 
        agent2recv_map = agent_swarm.agent_received_answers() 
        agent_relation_graph = deepcopy(agent_swarm.swarm_graph) 

        ifunc = InconsistentFunctionTypeESAR(default_ans,agent2exp_map,agent2recv_map,\
            agent_relation_graph,prg)

        return FQSubjectTypeDD(ifunc) 