# Import necessary libraries
import numpy as np
import matplotlib.pyplot as plt
import gym
import socket

#Get hostname of the computer
hostname = socket.gethostname()

# Define environment, state, GAMMA, ETA, max steps, and number of episodes
ENV = 'CartPole-v1'
NUM_DIGITIZED = 6
GAMMA = 0.99  # decrease rate
ETA = 0.5  # learning rate
MAX_STEPS = 300  # steps for 1 episode
NUM_EPISODES = 200  # number of episodes


# Define a class for an agent
class Agent:
    def __init__(self, num_states, num_actions):
        self.brain = Brain(num_states, num_actions)

    def update_Q_function(self, observation, action, reward, observation_next):
        self.brain.update_Q_table(observation, action, reward, observation_next)

    def get_action(self, observation, step):
        action = self.brain.decide_action(observation, step)
        return action


# Define a class for the brain
class Brain:
    # Initialize Q table
    def __init__(self, num_states, num_actions):
        self.num_actions = num_actions  # the number of CartPole actions

        self.q_table = np.random.uniform(low=0, high=1, size=(NUM_DIGITIZED ** num_states, num_actions))

    # Define Q table size
    def bins(self, clip_min, clip_max, num):

        return np.linspace(clip_min, clip_max, num + 1)[1: -1]

    # Get the position of the observation state in the Q table
    def digitize_state(self, observation):
        # get the discrete state in total 1296 states
        cart_pos, cart_v, pole_angle, pole_v = observation


        digitized = [
            np.digitize(cart_pos, bins=self.bins(-2.4, 2.4, NUM_DIGITIZED)),
            np.digitize(cart_v, bins=self.bins(-3.0, 3.0, NUM_DIGITIZED)),
            np.digitize(pole_angle, bins=self.bins(-0.5, 0.5, NUM_DIGITIZED)),  # angle represent by radian
            np.digitize(pole_v, bins=self.bins(-2.0, 2.0, NUM_DIGITIZED))
        ]

        return sum([x * (NUM_DIGITIZED ** i) for i, x in enumerate(digitized)])

    # Update Q table
    def update_Q_table(self, observation, action, reward, observation_next):
        state = self.digitize_state(observation)
        state_next = self.digitize_state(observation_next)
        Max_Q_next = max(self.q_table[state_next][:])
        self.q_table[state, action] = self.q_table[state, action] + \
                                      ETA * (reward + GAMMA * Max_Q_next - self.q_table[state, action])

    # Make an action
    def decide_action(self, observation, episode):
        # epsilon-greedy
        state = self.digitize_state(observation)
        epsilon = 0.5 * (1 / (episode + 1))

        if epsilon <= np.random.uniform(0, 1):
            action = np.argmax(self.q_table[state][:])
        else:
            action = np.random.choice(self.num_actions)

        return action


# Define environment startup class
class Environment:
    def __init__(self):
        # test for visualizing
        # self.env = gym.make(ENV, render_mode="human")
        self.env = gym.make(ENV)
        num_states = self.env.observation_space.shape[0]
        num_actions = self.env.action_space.n
        self.agent = Agent(num_states, num_actions)

    def run(self):
        complete_episodes = 0
        is_episode_final = False
        frames = []

        # save the episode
        x = []
        # save the steps
        y = []

        for episode in range(NUM_EPISODES):
            observation = self.env.reset()[0]

            for step in range(MAX_STEPS):
                action = self.agent.get_action(observation, episode)
                observation_next, _, done, _, __ = self.env.step(action)
                if done:
                    if step < 195:
                        reward = -1
                        complete_episodes = 0
                    else:
                        reward = 1
                        complete_episodes += 1
                else:
                    reward = 0
                self.agent.update_Q_function(observation, action, reward, observation_next)
                observation = observation_next
                if done:
                    print('{0} Episode: Finished after {1} time steps'.format(episode, step + 1))
                    x.append(episode)
                    y.append(step + 1)
                    break
        # draw a graph
        plt.title('CartPole-v1')
        plt.xlabel('Episode')
        plt.ylabel('Step')
        plt.plot(x, y, linewidth =1.5, color='slateblue', linestyle=(0,()), alpha=0.8, label=hostname)
        plt.legend()
        # save the graph in 'out' with container's hostname
        plt.savefig("/root/project/out/out_" + hostname + ".png")
        # plt.show()

q = Environment()
q.run()