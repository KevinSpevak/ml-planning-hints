# utils for playing a blocksworld game
from .pddl import Domain, Problem
from .planning_world import PlanningWorld
from os.path import dirname, join
import numpy as np
import pdb
import random

class BlocksworldGame:
    def __init__(self, num_blocks=None):
        self.pddl_path = join(dirname(dirname(__file__)), "pddl", "blocksworld")
        self.domain = Domain.read_from_file(join(self.pddl_path, "domain.pddl"))
        if num_blocks:
            self.random_instance(num_blocks)
        else:
            self.load_problem_file("sussman.pddl")

    def load_problem_file(self, fname):
        self.problem = Problem.read_from_file(self.domain, join(self.pddl_path, fname))
        self.world = PlanningWorld(self.problem)

    # random n-block problem instance with goal to
    # stack all the blocks in ordered tower
    def random_instance(self, n):
        blocks = [chr(65+i) for i in range(n)]
        random.shuffle(blocks)
        top_blocks, init = [], []
        for block in blocks:
            place = random.choice(top_blocks + ["table"])
            if place == "table":
                init.append(("ontable", block))
            else:
                init.append(("on", block, place))
                top_blocks.remove(place)
            top_blocks.append(block)
        for block in top_blocks:
            init.append(("clear", block))
        init.append(("handempty",))
        blocks.sort()
        goal = [("on", blocks[i], blocks[i+1])
                for i in range(len(blocks) - 1)]
        self.problem = Problem("random", self.domain, blocks, tuple(init), tuple(goal))
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

    def open_cli_num(self):
        print("Starting number input based cli")
        while True:
            self.display_state()
            for i in range(self.world.num_actions):
                print(i, self.world.action_expr(i))
            command = input("enter action")
            expr = self.world.action_expr(int(command))
            if self.world.is_legal(expr[0], expr[1:]):
                self.world.take_action(expr[0], expr[1:])
                if self.world.goal_satisfied():
                    self.display_state()
                    print("Goal Satisfied!")
                    print("Final state", self.world.state_expr())
                    break # TODO start new problem?
            else:
                print("Illegal action")

    # bad name, this function trains a q table from scratch
    # we will also have a funciton that read a q table from a file
    # perhaps we will call that ql_implement?
    def ql_learn_init(self):
        self.q_table = np.zeros((self.world.num_actions,1))
        self.mask = np.ones((self.world.num_actions,1))
        self.state_index = {}
        self.state_index[self.world.state_expr()] = 0
        print("Starting learning process")
        for i in range(self.world.num_actions):
            print(i, self.world.action_expr(i))

        e = 1 #epsilon
        a = .9 #alpha
        y = .9 #gamma
        t = 0
        while e > 0.1:
            self.display_state()

            # choose action part
            state = self.state_index[self.world.state_expr()]
            if random.random()>e:
                command = np.argmax(np.transpose(self.q_table)[state])
                print("Agent greedily chose", command)
            else:
                print("Random action!")
                indices = np.where(np.transpose(self.mask)[state] == 1)[0]
                command = random.choice(indices)
                print("Agent chose", command)
            # end of action selection

            expr = self.world.action_expr(int(command))
            if self.world.is_legal(expr[0], expr[1:]):
                # take action
                self.world.take_action(expr[0], expr[1:])

                # observe s'
                if not self.world.state_expr() in self.state_index:
                    print("We're not in Kansas anymore!")
                    self.state_index[self.world.state_expr()] = len(self.state_index)
                    self.q_table = np.append(self.q_table, np.zeros((self.world.num_actions,1)), axis=1)
                    self.mask = np.append(self.mask, np.ones((self.world.num_actions,1)), axis=1)

                reward = 0
                if self.world.goal_satisfied():
                    self.display_state()
                    print("Goal Satisfied!")
                    print("Final state", self.world.state_expr())
                    reward = 1
                # update q table
                max_a = np.amax(np.transpose(self.q_table)[self.state_index[self.world.state_expr()]] )
                self.q_table[command][state] += a * (reward + y* max_a - self.q_table[command][state])
                t += 1
                if self.world.goal_satisfied() or t>1000:
                    t = 0
                    e *= .95
                    self.__init__(3)
                    if not self.world.state_expr() in self.state_index:
                        print("We're not in Kansas anymore!")
                        self.state_index[self.world.state_expr()] = len(self.state_index)
                        self.q_table = np.append(self.q_table, np.zeros((self.world.num_actions,1)), axis=1)
                        self.mask = np.append(self.mask, np.ones((self.world.num_actions,1)), axis=1)
            else:
                print("Illegal action")
                self.mask[int(command)][self.state_index[self.world.state_expr()]] = 0
        print(self.q_table)
        print(self.mask)
        np.save('q_table',self.q_table)
        np.save('q_mask',self.mask)
        # save state index too

    def test_q(self):
        self.q_table = np.load('q_table.npy')
        self.q_mask = np.load('q_mask.npy')
        # load state index
        print(self.q_table)
        print(self.mask)


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
