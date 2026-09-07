from agent.agent import Agent


agent = Agent("Crie um arquivo Python para dizer hello word e depois o execute com 'python hello.py'")

agent.run(max_iterations=3)

print("\nStatus final:", agent.state.status)
print("Iterações:", agent.state.iteration)
print("Última decisão:", agent.state.last_decision)
print("Último resultado:", agent.state.last_result)