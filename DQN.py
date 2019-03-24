# @auther: YuxiXie - sigridcc@pku.edu.cn

import tensorflow as tf 
import numpy as np 
import random
from collections import deque


# Hyper Parameters for DQN
GAMMA = 0.9 # discount factor for target Q 
INITIAL_EPSILON = 0.5 # starting value of epsilon
FINAL_EPSILON = 0.01 # final value of epsilon
REPLAY_SIZE = 50000 # experience replay buffer size
BATCH_SIZE = 256 # size of minibatch
STATE_DIM = 1344
ACTION_DIM = 45
HIDDEN_DIM = 128
GEMS_DICT = {"blue": 0, "green": 1, "red": 2, "black": 3, "white": 4, "gold": 5}
COLORS = ['blue', 'green', 'red', 'black', 'white']
bi2index = {'11100':0, '11010':1, '11001':2, '10110':3, '10101':4, '10011':5, '01110':6, '01101':7, '01011':8, '00111':9}
index2bi = ['11100', '11010', '11001', '10110', '10101', '10011', '01110', '01101', '01011', '00111' ]


class DQN():
    # Spendor Agent
    def __init__(self, env):
        # init experience replay
        self.replay_buffer = deque()
        # init some parameters
        self.time_step = 0
        self.epsilon = INITIAL_EPSILON
        self.state_dim = STATE_DIM
        self.action_dim = ACTION_DIM
        # init Q network structure
        self.create_Q_network()
        # init iterate policy
        self.create_training_method()
        # init session
        self.session = tf.InteractiveSession()
        self.session.run(tf.initialize_all_variables())
        self.saver = tf.train.Saver()
        # loading networks
        self.saver = tf.train.Saver()
        try:
            checkpoint = tf.train.get_checkpoint_state("agents")
            if checkpoint and checkpoint.model_checkpoint_path:
                self.saver.restore(self.session, checkpoint.model_checkpoint_path)
        except:
            return

    def create_Q_network(self):
        # network weights
        W1 = self.weight_variable([self.state_dim, HIDDEN_DIM])
        b1 = self.bias_variable([HIDDEN_DIM])
        W2 = self.weight_variable([HIDDEN_DIM, self.action_dim])
        b2 = self.bias_variable([self.action_dim])
        # input layer
        self.state_input = tf.placeholder("float", [None, self.state_dim])
        # hidden layers
        h_layer = tf.nn.relu(tf.matmul(self.state_input, W1) + b1)
        print(h_layer)
        # Q Value layer
        self.Q_value = tf.matmul(h_layer, W2) + b2

    def create_training_method(self):
        # one hot presentation
        self.action_input = tf.placeholder("float", [None, self.action_dim]) 
        self.y_input = tf.placeholder("float", [None])
        Q_action = tf.reduce_sum(tf.multiply(self.Q_value, self.action_input),reduction_indices = 1)
        self.cost = tf.reduce_mean(tf.square(self.y_input - Q_action))
        self.optimizer = tf.train.AdamOptimizer(0.0001).minimize(self.cost)

    def perceive(self, state, action, reward, next_state, done):
        self.replay_buffer.append((state, action, reward, next_state, done))
        if len(self.replay_buffer) > REPLAY_SIZE:
            # remove when overflow
            self.replay_buffer.popleft()
        if len(self.replay_buffer) > BATCH_SIZE:
            # train trigger
            self.train_Q_network()

    def train_Q_network(self):
        self.time_step += 1
        # Step 1: obtain random minibatch from replay memory
        minibatch = random.sample(self.replay_buffer, BATCH_SIZE)
        state_batch = [data[0] for data in minibatch]
        action_batch = [data[1] for data in minibatch]
        reward_batch = [data[2] for data in minibatch]
        next_state_batch = [data[3] for data in minibatch]
        # Step 2: calculate y
        y_batch = []
        Q_value_batch = self.Q_value.eval(feed_dict = {self.state_input:next_state_batch})
        for i in range(0, BATCH_SIZE):
            done = minibatch[i][4]
            if done:
                y_batch.append(reward_batch[i])
            else:
                y_batch.append(reward_batch[i] + GAMMA * np.max(Q_value_batch[i]))
        # run
        self.optimizer.run(feed_dict = {
            self.y_input:y_batch,
            self.action_input:action_batch,
            self.state_input:state_batch
            })
        # save network every 1000 iteration
        if self.time_step % 1000 == 0:
            self.saver.save(self.session, 'agents/dqn', global_step = self.time_step)

    def egreedy_action(self, state, env):
        #print(state)
        Q_value = self.Q_value.eval(feed_dict = {
           self.state_input:[state]
            })[0]
        act = random.randint(0, self.action_dim - 1)
        if random.random() <= self.epsilon:
            action = np.zeros(self.action_dim)
            action[act] = 1
            while (self.verify(action, env) == False):
                act = random.randint(0, self.action_dim - 1)
                action = np.zeros(self.action_dim)
                action[act] = 1
        else:
            act = np.argmax(Q_value) 
            action = np.zeros(self.action_dim)
            action[act] = 1
            while (self.verify(action, env) == False):
                act = random.randint(0, self.action_dim - 1)
                action = np.zeros(self.action_dim)
                action[act] = 1
        if self.time_step % 100 == 0:
            self.epsilon -= (INITIAL_EPSILON - FINAL_EPSILON) / 10000
        return action 

    def action(self, state, env):
        #print(state)
        act = np.argmax(self.Q_value.eval(feed_dict = {
            self.state_input:[state]
            })[0])
        action = np.zeros(self.action_dim)
        action[act] = 1
        while (self.verify(action, env) == False):
            act = random.randint(0, self.action_dim - 1)
            action = np.zeros(self.action_dim)
            action[act] = 1
        #print(act)
        return action

    def weight_variable(self, shape):
        initial = tf.truncated_normal(shape)
        return tf.Variable(initial)

    def bias_variable(self, shape):
        initial = tf.constant(0.01, shape = shape)
        return tf.Variable(initial)

    def verify(self, action, env):
        psedo_env = env
        try:
            a, b, c, is_valid, _ = psedo_env.step(action) 
            return is_valid
        except:
            #print(is_valid)
            return False
