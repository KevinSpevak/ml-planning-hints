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
        names = list(self.predicates.keys())
        self.pred_offsets = {}
        offset = 0
        for i in range(len(names)):
            name = names[i]
            pred = self.predicates[name]
            self.pred_offsets[name] = offset
            offset += self.n**pred.arity
        self.num_preds = offset
        names = list(self.actions.keys())
        self.action_offsets = {}
        offset = 0
        for i in range(len(names)):
            name = names[i]
            action = self.actions[name]
            self.action_offsets[name] = offset
            offset += self.n**action.arity
        self.num_actions = offset
        self.state = np.zeros(offset, np.bool_)
        self.set_state(self.problem.init)

        self.temp_state = np.zeros(offset, np.bool_)

    # Assigns each set of args a int in the range [0, n^arity) where n is
    # the number of objects. This is used to order ground predicates
    # in the state space representation
    def ground_number(self, args):
        num = 0
        for i in range(len(args)):
            num += self.obj_idx[args[i]] * self.n**i
        return num

    # return the index of a grounded predicate
    def pred_index(self, pred, args):
        return self.pred_offsets[pred] + self.ground_number(args)

    def action_index(self, action, args):
        return self.action-offsets[action] + self.ground_number(args)

    # takes a tuple of clauses (implicit AND) and updates the state
    # to make all clauses true
    def set_state(self, expr):
        for clause in expr:
            val = True
            if (clause[0] == "not"):
                clause = clause[1]
                val = False
            self.state[self.pred_index(clause[0], clause[1:])] = val

    # inverse of ground_num
    def ground_args(self, num, arity):
        args = []
        for i in range(arity):
            idx = num % self.n
            args.append(self.objects[idx])
            num = int((num - idx) / self.n)
        return tuple(args)

    # inverse of pred_index
    def pred_expr(self, index):
        offset, name = sorted([(self.pred_offsets[name], name) for name in self.pred_offsets if self.pred_offsets[name] <= index])[-1]
        args = self.ground_args(index - offset, self.predicates[name].arity)
        return (name,) + args

    def action_expr(self, index):
        offset, name = sorted([(self.action_offsets[name], name) for name in self.action_offsets if self.action_offsets[name] <= index])[-1]
        args = self.ground_args(index - offset, self.actions[name].arity)
        return (name,) + args

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
        grounded = GroundAction(self.domain.actions[action], args)
        return self.all_true(grounded.pre)

    def take_action(self, action, args):
        if not self.is_legal(action, args):
            raise Exception("illegal action " + str((action,) + args))
        grounded = GroundAction(self.domain.actions[action], args)
        self.set_state(grounded.eff)

    def state_if_action(self, action, args):
        self.temp_state = copy.deepcopy(self.state)
        if not self.is_legal(action, args):
            raise Exception("illegal action " + str((action,) + args))
        grounded = GroundAction(self.domain.actions[action], args)
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
