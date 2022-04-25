# Simulates the world defined by a planning problem
# tracks state space and models changes through actions
import pdb
import numpy as np
import copy
from .pddl import GroundAction

class PlanningWorld:
    def __init__(self, problem):
        self.problem = problem
        self.domain = problem.domain
        self.objects = self.problem.objects
        self.n = len(self.objects)
        self.obj_idx = {}
        for i in range(len(problem.objects)):
            self.obj_idx[problem.objects[i]] = i
        self.predicates = self.domain.predicates
        self.actions = self.domain.actions
        self.init_state()

    def init_state(self):
        self.ground_preds = self.problem.generate_ground_predicates()
        self.num_preds = len(self.ground_preds)
        self.pred_indices = {}
        for i in range(len(self.ground_preds)):
            self.pred_indices[self.ground_preds[i].expr()] = i
        self.ground_actions = self.problem.generate_ground_actions()
        self.num_actions = len(self.ground_actions)
        self.action_indices = {}
        for i in range(len(self.ground_actions)):
            self.action_indices[self.ground_actions[i].expr()] = i
        self.state = np.zeros(self.num_preds, np.bool_)
        self.set_state(self.problem.init)

        self.temp_state = np.zeros(self.num_preds, np.bool_)

    # return the index of a grounded predicate
    def pred_index(self, pred, args):
        return self.pred_indices[(pred,) + args]

    def action_index(self, action, args):
        return self.action_indices[(action,) + args]

    # takes a tuple of clauses (implicit AND) and updates the state
    # to make all clauses true
    def set_state(self, expr):
        for clause in expr:
            val = True
            if (clause[0] == "not"):
                clause = clause[1]
                val = False
            self.state[self.pred_index(clause[0], clause[1:])] = val

    # inverse of pred_index
    def pred_expr(self, index):
        return self.ground_preds[index].expr()

    def action_expr(self, index):
        return self.ground_actions[index].expr()

    # returns the state in expression form (tuple of true predicates)
    def state_expr(self):
        indices = np.where(self.state == True)[0]
        exprs = []
        for index in indices:
            exprs.append(self.pred_expr(index))
        return tuple(exprs)


    def all_true(self, clauses):
        pred_indices = [self.pred_index(clause[0], clause[1:]) for clause in clauses]
        return np.all(self.state[pred_indices])

    def is_legal(self, action, args):
        grounded = self.ground_actions[self.action_index(action, args)]
        return self.all_true(grounded.pre)

    def take_action(self, action, args):
        if not self.is_legal(action, args):
            raise Exception("illegal action " + str((action,) + args))
        grounded = self.ground_actions[self.action_index(action, args)]
        self.set_state(grounded.eff)

    def state_if_action(self, action, args):
        self.temp_state = copy.deepcopy(self.state)
        if not self.is_legal(action, args):
            raise Exception("illegal action " + str((action,) + args))
        grounded = self.ground_actions[self.action_index(action, args)]
        expr = grounded.eff

        for clause in expr:
            val = True
            if (clause[0] == "not"):
                clause = clause[1]
                val = False
            self.temp_state[self.pred_index(clause[0], clause[1:])] = val

        indices = np.where(self.temp_state == True)[0]
        exprs = []
        for index in indices:
            exprs.append(self.pred_expr(index))
        return tuple(exprs)


    def goal_satisfied(self):
        return self.all_true(self.problem.goal)
