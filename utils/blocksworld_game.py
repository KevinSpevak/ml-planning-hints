# utils for playing a blocksworld game
from .pddl import Domain, Problem
from .planning_world import PlanningWorld
from os.path import dirname, join

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
            print("Current State:", self.world.state_expr())
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
                    print("Goal Satisfied!")
                    print("Final state", self.world.state_expr())
                    break # TODO start new problem?
            else:
                print("Illegal action")
