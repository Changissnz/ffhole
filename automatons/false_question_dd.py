from .false_question_agents import * 

"""
False Question Type (D)elay and (D)ivert. 

Composed of four primary components: 
(1) <QuestionTypeSWPS>: subjective question representative used to facilitate 
    questioning activity between two agents. The two agents are either 
        (<FQSwarmAgent> questions <FQSwarmAgent>) OR 
        (<FQSwarmAgent> questions <FQSubjectTypeDD>). 
(2) <FQSubjectTypeDD>: subjected to questioning activity. Primary purpose 
    is to traverse one of the <NodePaths> in the solution set of <ObjectiveTypeUSGMP> 
(3) <FQSwarmAgent>: composed of k agents, arranged in a connected graph (graph with one 
    component). Swarm agents act as antagonists to <FQSubjectTypeDD> traversing a 
    solution path. 
(4) <ObjectiveTypeUSGMP>: objective of the subject. Based on q unique paths of a simple 
    undirected graph, each with the same starting node. 

Every time method<exec_one_objective> is called, a new <ObjectiveTypeUSGMP> is generated 
by `Q`. This is the main method that processes the unit problem of this automaton. 
---------------------------------------------------------------------------------

<FQSubjectTypeDD> `fs` is to travel one of the solution paths specified in `subject_objective`. 
At every node in its current path P, until 
    |P| >= MAX_{p in subject_objective}(|p|), 
`fs` has to perform actions in a chain-of-questioning C, and the results from these actions 
influence the probability that `fs` takes a next node, from its current node, that is 
one of the next nodes in the set of solution paths of `subject_objective`. 

The chain-of-questioning C is initiated by `fas` choosing a starting agent `A`. `A` 
questions `fs` on the answer to question `Q`. Question process goes as such for any 
two agents (questioner S,responder R). 
- R sends its answer to questioner S. 
- S makes decision: 
    have R provide "proof" XOR 
    accept R's answer and "pass" it to active swarm agent neighbors. 
- The decision of S is a simple rule: if `S.error_term` < 0.5, `S` accepts 
  R's answer. Otherwise, it demands "proof". 

  NOTE: the `error_term` is the ratio of auto-corrected edges, from the <QuestionTypeSWPS>'s 
        execution of a <ProofDifferentialSimulatorTypeACSGT>'s main method. 
- Proof process is done through `Q.proof_process`. The results from this method are 
  used as parameters for method<FQSwarmAgent.decision_p>. The rule is if the path 
  difference score of the proof path is less than half the length of the proof path, 
  then proof is accepted. 
- If the proof is accepted, then the questioning agent changes its answer to the one 
  provided by the answering agent. Otherwise, responder changes its answer to the one 
  provided by the questioning agent. 

If S decides to "pass" answer of R, it passes only to its active swarm agent neighbors. 
When every neighbor S_n processes this pass of answer from S, S_n demands proof from 
S. S_n also demands proof from `fs` if 
    `fs` != R. 
NOTE: this is a triangulation scheme where questioner S_n demands proof of answer from 
      both the immediate sender and the central subject `fs` of the automaton. 

NOTE: there is a limit to how many questioning actions a swarm agent can take for every 
    chain-of-questioning, so that there is no possibility the process enters an infinite 
    loop. 

NOTE: the <FQSubjectTypeDD> does not answer the question of `Q` with a constant singleton 
      for any swarm agent. Instead, it relies on <InconsistentFunctionTypeESAR>, a map 
      structure, the most important maps being 
        (0) M_exp : agent idn -> agent's expected answer 
        (1) M_r : agent idn -> subject's most recent answer to agent. 
      These two maps are mutable, and are updated every time there is questioning from 
      swarm agent to `fs`. 

      The subject `fs` chooses to answer agent A_i with either M_exp[i] (its prediction of 
      A_i's expected answer) or M_r[i] (consistent answer to A_i), via the PRNG of `fs`. 

The counter-probability, that is, the probability of `fs` traversing a next node that is 
not a next node, given the current node, of any of the solution paths in `subject_objective`, 
is `fs.rejects / (fs.accepts + fs.rejects)`. This counter-probability is applied through 
`fs`'s PRNG-generated decimal value d in [0.,1.]. 

---------------------------------------------------------------------------------------

NOTE: see the class variable<cumulative_*> for more information on important measures 
collected throughout the automaton's run. 
""" 
class FalseQuestionTypeDD: 

    def __init__(self,Q:QuestionTypeSWPS,fs:FQSubjectTypeDD,fas:FQSwarmAgent,\
        subject_objective:ObjectiveTypeUSGMP,verbose=True): 
        assert type(Q) == QuestionTypeSWPS
        assert type(fs) == FQSubjectTypeDD
        assert type(fas) == FQAgentSwarm
        assert type(subject_objective) == ObjectiveTypeEFIT

        self.Q = Q 
        self.fs = fs
        self.fas = fas 
        self.subject_objective = subject_objective
        self.verbose = verbose 

        self.queue_pass_proc = deque() 
        self.queue_proof_proc = deque() 

        self.fin_stat = False 

        # agent idn -> error from auto-correction process in proofs 
        self.cumulative_errors = Counter(dict())
        # agent idn -> number of inconsistencies (changes) in answers of  
        #           subject to swarm agent, due to swarm agent's rejection 
        #           of proof. 
        self.cumulative_inconsistencies_S = Counter(dict())
        # agent idn -> number of answers from subject to agent that differ 
        #              from agent's current answer. 
        self.cumulative_inconsistencies_A0 = Counter(dict())
        # agent idn -> total number of inconsistent answers from any other agent 
        self.cumulative_inconsistencies_A1 = Counter(dict())

        # cumulative path difference between subject's traversed paths 
        # and solution paths. 
        self.cumulative_path_score = 0 
        return 

    """
    main method #1 
    """
    def exec_one_objective(self): 
        self.fin_stat = False 

        while not self.fin_stat: 
            next(self) 

        self.update_scores() 
        self.update_subject_obj()
        return

    """
    main method #2 
    """
    def __next__(self): 
        if self.fin_stat: return 

        if self.subject_objective.fin_stat: 
            self.fin_stat = True 
            return 

        self.exec_q_round() 
        self.exec_subject_travel() 
    
    """
    main method #3
    """
    def exec_q_round(self): 
        self.fas.agent_action_ctr_map.clear() 
        self.start_q_chain() 

        while len(self.queue_pass_proc) > 0 or len(self.queue_proof_proc) > 0: 
            self.exec_q_round_() 

    def exec_subject_travel(self): 
        q = zero_div(self.fs.rejects,self.fs.rejects + self.fs.accepts,0.0) 
        self.subject_objective.exec(q,self.fs.prg)

    """
    starts the questioning round 
    """
    def start_q_chain(self): 

        A = self.fas.first_q_agent()
        self.exec_q(A,self.fs) 
        return

    """
    runs the questioning round after it has started. Every call 
    executes one proof process between questioning and answering 
    agents, and one pass process from the previous questioning agent 
    to its neighbors. 
    """
    def exec_q_round_(self): 
        # next proof 
        if len(self.queue_proof_proc) > 0: 
            x = self.queue_proof_proc.popleft() 

            A0 = self.idn_to_agent(x[0]) 
            A1 = self.idn_to_agent(x[1]) 
            self.exec_proof(A0,A1)  

        # next pass (bfs-order) 
        if len(self.queue_pass_proc) > 0: 
            q = self.queue_pass_proc.popleft() 
            for q_ in q: 
                A0,A1 = self.idn_to_agent(q_[0]),self.idn_to_agent(q_[1]) 
                self.exec_pass(A0,A1) 
        
        if self.verbose: 
            print("==================================")
        return 

    """
    executes question action from `q_agent` to `a_agent` 
    """
    def exec_q(self,q_agent,a_agent): 

        # pass answer 
        stat = a_agent == self.fs
        if stat: 
            ans = a_agent.answer(q_agent.idn)  
        else: 
            ans = a_agent.answer() 

        q_agent.recv_answer(ans,stat) 
        self.fas.update_action_ctr(q_agent.idn) 

        # questioning agent makes decision 
        D = q_agent.decision_0()

        if self.verbose: 
            s0,s1 = self.agent_to_idn(q_agent),self.agent_to_idn(a_agent) 
            print("q={},a={} --> q {}".format(s0,s1,D)) 

        # proof demanded; questioning agent requires one from both the sender 
        # Swarm Agent and the Subject. 
        if D == "proof":
            self.enqueue_proof_proc(q_agent,self.fs) 
            if self.agent_to_idn(a_agent) != "subject": 
                self.enqueue_proof_proc(q_agent,a_agent) 
        else: 
            self.enqueue_pass_proc(q_agent)
        return 

    """
    Agent `q_agent` demands `a_agent` prove its answer. 
    Process occurs via <ProofDifferentialSimulatorTypeACSGT>. 
    """ 
    def exec_proof(self,q_agent,a_agent): 
        prg0 = a_agent.prg 
        prg1 = q_agent.prg   
        pf,score,autocorrect_ratio = self.Q.proof_process(prg0,prg1)

        a_agent.update_error_term(autocorrect_ratio) 

        D2 = q_agent.decision_p(pf,score) 
        if self.verbose: 
            print("-- {} provides proof to {}".format(self.agent_to_idn(a_agent),self.agent_to_idn(q_agent))) 
            print("-- proof decision: {}, score: {}   {}".format(D2,score,autocorrect_ratio))

        # case: subject is answering agent
        if a_agent == self.fs:
            a_agent.num_queries += 1 
            a_agent.update_ar_count(D2 == "accept") 
            # subject changes its answer to something else 
            if D2 == "reject":  
                alt_answer = q_agent.contra_answer(q_agent.received_answer)
                a_agent.update_answer(q_agent.idn,alt_answer,"exp") 
            # subject updates its most recent answer sent to agent 
            a_agent.update_answer(q_agent.idn,q_agent.received_answer,"sent")

        self.fas.update_action_ctr(q_agent.idn) 
        self.enqueue_pass_proc(q_agent)

    def exec_pass(self,s_agent,r_agent): 
        self.exec_q(r_agent,s_agent)
        return 

    #------------------------ queue update methods 

    def enqueue_proof_proc(self,q_agent,a_agent): 

        idn0 = self.agent_to_idn(q_agent)
        idn1 = self.agent_to_idn(a_agent) 

        if self.verbose: 
            print("[!] {} demands proof from {}".format(idn0,idn1))

        self.queue_proof_proc.append((idn0,idn1)) 

    def enqueue_pass_proc(self,q_agent): 
        neighbors = self.fas.active_neighbor_agents(q_agent.idn) 
        neighbors = prg_seqsort(sorted(neighbors),self.fas.collective_prg)

        if self.verbose: 
            print("{} passes to neighbors: {}".format(self.agent_to_idn(q_agent),neighbors)) 

        X = [] 
        for n in neighbors: 
            X.append((q_agent.idn,n)) 
        self.queue_pass_proc.append(X) 
        return 

    def idn_to_agent(self,idn): 
        if idn == "subject": return self.fs 
        return self.fas.idn_to_agent(idn) 

    def agent_to_idn(self,a_agent): 
        return "subject" if type(a_agent) == FQSubjectTypeDD else \
            a_agent.idn

    #------------------------------------------ objective update function 

    def update_subject_obj(self): 
        start_node,node_path_soln = self.Q.choose_node_path_solution() 
        self.subject_objective = ObjectiveTypeEFIT(self.Q.G,start_node,node_path_soln)

    #------------------------------------------ performance measures 

    def display_score(self): 
        print("-- cumulative errors")
        for k,v in self.cumulative_errors.items(): print("* {} : {}".format(k,v)) 
        print() 

        print("-- subject inconsistencies (answers to agents)") 
        for k,v in self.cumulative_inconsistencies_S.items(): print("* {} : {}".format(k,v)) 
        print() 

        print("-- agent inconsistencies from subject") 
        for k,v in self.cumulative_inconsistencies_A0.items(): print("* {} : {}".format(k,v)) 
        print() 

        print("-- agent inconsistencies from other agents") 
        for k,v in self.cumulative_inconsistencies_A1.items(): print("* {} : {}".format(k,v)) 
        print() 

        print("-- path score: ",self.cumulative_path_score)

    def error_terms(self): 
        D = self.fas.error_terms() 
        D["subject"] = self.fs.error_term
        return D 

    def inconsistencies(self): 
        M = self.fas.inconsistency_map() 
        M0 = self.fs.incon_func.inconsistency_count
        return M0,M 

    def path_score(self): 
        return self.subject_objective.score_path(self.subject_objective.npath)

    def update_scores(self): 
        # add scores to cumulative maps  
        errors = self.error_terms()
        self.cumulative_errors += Counter(errors) 

        incons = self.inconsistencies() 

        self.cumulative_inconsistencies_S += Counter(incons[0]) 

        incons10 = {k:v[0] for k,v in incons[1].items()}
        incons11 = {k:v[1] for k,v in incons[1].items()}

        self.cumulative_inconsistencies_A0 += Counter(incons10) 
        self.cumulative_inconsistencies_A1 += Counter(incons11) 

        self.cumulative_path_score += self.path_score() 
        
        # clear present counters 
        self.fas.clear_counters() 
        self.fs.clear_counters() 
        return 