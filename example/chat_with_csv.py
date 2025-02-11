from agent import Agent

agent = Agent(
    dfs="../data/data.csv"
)

print(agent.run("How many people live in San Francisco and under 50?"))