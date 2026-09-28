from .false_entry_agents import * 
from morebs2.numerical_generator import modulo_in_range,prg__single_to_int

"""
Features two classes of agents, a Defender network (<FESurface>) and <FEAgent>s, 
spawned by an <FEAgentSpawn>. 

Automaton facilitates traversal activity of <FEAgent>s through the Defender network, 
until they each reach an endpoint or are terminated by the Defender network's trap 
mechanism. 

At each timestamp, the execution occurs in two phases. 

(I) Appearance phase. 
    - additional agents spawn, in limits of `max_active_agents` and `max_agents`. 
    - automaton transmits agent next-node weight range hypotheses to Defender. 
    - Defender designates probable nodes as traps and modifies its appearance of node 
      weights for this designation. 

(II) Trap execution phase. 
    - agents traverse to their next node. 
    - Defender's traps activate. 
    - trapped agents are eliminated. 
    - agents that reached an endpoint of the Defender are successful, 
      placed in the `passed` cache. 

        Agent spawning step
        -------------------
The `tstep_inaccuracy` is a ratio on the weight range hypotheses an agent, during spawning, 
receives. Surface retrieves a path from one of its entry points to one of its end points. 
This path p of q nodes is associated with q weights. If `tstep_inaccuracy` is 0.0, every i'th 
weight range the agent receives fits exactly p[i]'s actual weight (variable<weight>). If 
`tstep_inaccuracy` is 1.0, the weight range fits all of p[i-1]'s neighbors, in which p[i] is 
included. 

NOTE: decision-making of both classes of agents depend on PRNGs given to them. 

NOTE: see file<falses.false_entry_functions> for more explanatory comments and code. 
"""
class FalseEntry: 

    def __init__(self,surface:FESurface,agent_spawn:FEAgentSpawn,prg,max_active_agents:int,max_agents:int,\
        tstep_inaccuracy:float,verbose=False):  
        
        assert type(surface) == FESurface 
        assert type(agent_spawn) == FEAgentSpawn
        assert agent_spawn.end_points == surface.end_points
        assert type(max_active_agents) == int and max_active_agents > 0 
        assert max_active_agents <= max_agents 
        assert 0 <= tstep_inaccuracy <= 1.0 
        assert type(verbose) == bool 

        self.surface = surface 
        self.spawn = agent_spawn 
        self.surface.verbose = verbose 

        self.prg = prg 

        self.agents = dict() 
        self.max_active_agents = max_active_agents 
        self.max_agents = max_agents 
        self.tstep_inaccuracy = tstep_inaccuracy
        self.verbose = verbose 

        self.acount = 0 

        self.passed = set() 
        self.terminated = set() 
        return

    def __next__(self): 
        if self.verbose: 
            print("---- occupied nodes")
            print(self.surface.occupied_nodes)
            print() 

        self.exec_phase_1() 
        self.exec_phase_2()

        if self.verbose: print("======================")


    #---------------------------------- spawning new agents 

    def generate_hyp_for_agent(self): 
        q = sorted(self.surface.entry_points)
        i = int(self.prg()) % len(q) 

        entry = q[i] 

        return self.surface.prg_choose_weight_range_hypothesis_for_entry(entry,self.spawn.hyp_type,self.tstep_inaccuracy)

    def allow_spawn(self): 
        # case: max number of agents reached
        if self.acount >= self.max_agents: 
            return 

        # case: spawn 
        d0 = self.max_active_agents - len(self.agents)
        d1 = self.max_agents - len(self.agents) 
        d = min([d0,d1]) 
        if d <= 0: return 

        i = modulo_in_range(int(self.prg()),[1,d + 1]) 

        for _ in range(i): 
            hyp = self.generate_hyp_for_agent() 
            a = self.spawn.spawn_from_hyp(hyp)
            self.agents[a.idn] = a 
            self.acount += 1 

    #----------------------------------- transmitting agent weight-range hypotheses to <FESurface> 

    def exec_agent_wr_hyp(self): 
        M = {}
        for idn,a in self.agents.items(): 
            a.set_next_weight_range() 
            M[idn] = deepcopy(a.next_wr) 
        return M 

    def transmit_agent_wr_hyp_to_surface(self): 
        M = self.exec_agent_wr_hyp() 
        self.surface.load_agent_hyp_map(M) 
        return

    def exec_surface_appearance(self): 
        self.surface.project_appearance() 
        return 

    def exec_phase_1(self): 
        self.allow_spawn() 
        self.transmit_agent_wr_hyp_to_surface() 
        self.exec_surface_appearance() 


    #---------------------------------- agents make moves and surface executes traps

    def agent_decision_(self,idn): 
        A = self.agents[idn] 
        loc = A.node_loc 

        q = self.surface.agent_location_to_appeared_node_weights(loc) 
        x = A.choose_next_loc(q) 
        return x 

    def exec_agent_decisions(self): 
        agent_idns = sorted(self.agents.keys())
        decisions = {} 
        for k in agent_idns: 
            decisions[k] = self.agent_decision_(k)

        if self.verbose: 
            print("---- decisions")
            print(decisions)
        return decisions 

    def exec_phase_2(self):
        d = self.exec_agent_decisions() 
        self.surface.update_agent_locations(d) 
        terminated_agents = self.surface.remove_trapped_agents()

        if self.verbose: 
            print("---- terminated")
            print(terminated_agents) 

        for t in terminated_agents: 
            self.terminated |= {self.agents[t]}
            del self.agents[t] 
        
        passed = self.surface.passed_agents()
        for p in passed: del self.agents[p] 
        self.passed |= passed 