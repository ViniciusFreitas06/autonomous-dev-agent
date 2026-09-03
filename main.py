from agent.agent import Agent


agent = Agent("Explique o que é um agente de IA.")

agent.run(max_iterations=3)

print("\nStatus final:", agent.state.status)
print("Iterações:", agent.state.iteration)
print("Última decisão:", agent.state.last_decision)
print("Último resultado:", agent.state.last_result)