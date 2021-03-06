import numpy as np

class Bus:
    def __init__(self, states, capacity=1, init_station=0):
        self.capacity = capacity
        self.empty_capacity = self.capacity
        # count time between consecutive stations, reset at arrival of station
        self.time_count = 0
        self.station = init_station
        self.terminal_station = len(states)
        self.states = states
        self.terminate_flag = self.station==self.terminal_station

    def move(self):
        self.time_count += 1

    def arrival(self):
        self.station += 1
        self.time_count = 0
        if self.station == self.terminal_station:
            self.terminate_flag = True
            # unload passenger at terminal state
            self.states[-1] += (self.capacity - self.empty_capacity)
            self.empty_capacity = self.capacity

    def take_passenger(self):
        if self.station != self.terminal_station:
            # check if bus has enough seats to take all ppl at current station
            num_passenger = self.states[self.station]
            if self.empty_capacity >= num_passenger:
                self.empty_capacity -= num_passenger
                self.states[self.station] = 0
            else:
                self.states[self.station] -= self.empty_capacity
                self.empty_capacity = 0


class TrafficSimulator:
    def __init__(self,
                 states=    [0, 2, 0, 0, 1, 0, 0, 1, 0],  # initial conditions at each station
                 goal_state=[0, 0, 0, 0, 0, 0, 0, 0, 4],
                 actions_dict={'wait': -1, "send0": 0}, #,'sendB':2,'sendC':3},  # wait, send new bus at A, B, or C, number corresponds to position A,B,C
                 traffic_condition=[1, 1, 1, 1, 1, 1, 1, 1, 1],  # time required between each station
                 bus_cost=1,  # cost for starting a new bus
                 ):

        self.time = 0
        self.initial_states = states.copy()
        self.states = states.copy()
        self.goal_state = goal_state
        self.actions = actions_dict.keys()
        self.actions_dict = actions_dict
        self.traffic_condition = traffic_condition
        # initial buses
        self.buses = []
        self.state = self.state_to_str()
        self.total_reward = 0
        self.bus_cost = bus_cost
        self.game_over = False
        self.pi = []

    def play(self, action):
        self.pi.append(action)
        if action not in self.actions:
            return -1
        # add extra bus if action is not wait
        extra_bus_fee = 0
        if action != 'wait':
            self.buses.append(Bus(self.states, init_station=self.actions_dict[action]))
            extra_bus_fee = -1 * self.bus_cost
        # loading bus, move bus
        for bus in self.buses:
            if bus.terminate_flag:
                continue
            bus.take_passenger()
            bus.move()
            if bus.time_count == self.traffic_condition[bus.station]:
                bus.arrival()

        self.state = self.state_to_str() #(tuple(self.states), tuple(self.bus_states))
        self.time += 1

        current_reward = -1 * sum(self.states[:-1])
        self.total_reward += current_reward

        # print("PLAYED ACTION", action, self.state, self.states, current_reward, self.total_reward)

        if self.states == self.goal_state:
            # print("PI:", self.pi)
            print("Send", len(self.buses), "buses.")
            self.game_over = True

        return self.state, current_reward

    def reset(self):
        self.time = 0
        self.states = self.initial_states.copy()
        self.state = self.state_to_str()
        self.buses = []
        self.total_reward = 0
        self.game_over = False
        self.pi = []
        return self.state

    def state_to_str(self):
        state_str = 0
        for state in self.states:
            state_str += state
        return "" + str(state_str)


