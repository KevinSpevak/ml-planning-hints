# utils for playing a blocksworld game
from .pddl import Domain, Problem
from .planning_world import PlanningWorld
from os.path import dirname, join
import numpy as np
import pdb

class BlocksworldGame:
    def __init__(self):
        self.pddl_path = join(dirname(dirname(__file__)), "pddl", "blocksworld")
        self.domain = Domain.read_from_file(join(self.pddl_path, "domain.pddl"))
        self.load_problem_file("sussman.pddl")

    def load_problem_file(self, fname):
        self.problem = Problem.read_from_file(self.domain, join(self.pddl_path, fname))
        self.world = PlanningWorld(self.problem)

    def open_cli(self):
        print("Starting blocksworld game. 'quit' to quit")
        while True:
            self.display_state()
            command = input("enter action --> ")
            if command == "quit":
                print("exiting game")
                break
            words = command.split()
            if len(command) == 0:
                continue
            if not words[0] in self.domain.actions:
                print("Unknown action " + words[0])
                continue
            action = words[0]
            args = words[1:]
            for arg in args:
                if not arg in self.problem.objects:
                    print("Unknown object " + arg)
                    continue
            if len(args) != self.domain.actions[action].arity:
                print("Wrong number of arguments for " + action)
                continue
            if self.world.is_legal(action, tuple(args)):
                self.world.take_action(action, tuple(args))
                if self.world.goal_satisfied():
                    self.display_state()
                    print("Goal Satisfied!")
                    print("Final state", self.world.state_expr())
                    break # TODO start new problem?
            else:
                print("Illegal action")


    def display_state(self):
        state = self.world.state_expr()
        stacks = [(clause[1],) for clause in state if clause[0] == "ontable"]
        holding = [clause[1] for clause in state if clause[0] == "holding"]
        holding = "|"+holding[0]+"|" if len(holding) > 0 else ''
        rest = [clause for clause in state if clause[0] == "on"]
        while len(rest) > 0:
            prev_level = [stack[-1] for stack in stacks]
            next_clause = [clause for clause in rest if clause[2] in prev_level][0]
            for i in range(len(stacks)):
                if stacks[i][-1] == next_clause[2]:
                    stacks[i] = stacks[i] + (next_clause[1],)
            rest.remove(next_clause)
        height = max([len(stack) for stack in stacks])
        for y in range(height):
            idx = height - y - 1
            row = ["|"+stack[idx]+"|" if len(stack) > idx else "   "
                   for stack in stacks]
            endl = "" if idx == 0 else "\n"
            print("".join(row), end=endl)
        print("  (>"+holding+"<)===")
