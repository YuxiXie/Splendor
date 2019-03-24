from DQN import DQN
from ENV import ENV


# Hyper Parameters
EPISODE = 10000 # Episode limitation
STEP = 1000 # Step limitation in an episode


def main():
	TEST = 64
	# initialize OpenAI Gym env and dqn agent
	env = ENV()
	agent = DQN(env)
	for episode in range(EPISODE):
		# initialize task
		state = env.reset()
		# train
		for step in range(STEP):
			# e-greedy action for train
			action = agent.egreedy_action(state, env) 
			next_state, reward, done, valid, _ = env.step(action)
			agent.perceive(state, action, reward, next_state, done)
			state = next_state
			if done:
			    break
		# test every 100 episodes
		if episode % 100 == 0:
			total_reward = 0
			for i in range(TEST):
				state = env.reset()
				for j in range(STEP):
				    # direct action for test
					action = agent.action(state, env) 
					#print(action)
					state, reward, done, valid, _ = env.step(action)
					total_reward += reward
					if done:
					    break
			ave_reward = total_reward / TEST
			if TEST < 1024:
				TEST *= 2
			print('episode: ' + str(episode) + '\tEvaluation Average Reward: ' + str(ave_reward))
			if ave_reward >= 100:
				break


if __name__ == '__main__':
  	main()
