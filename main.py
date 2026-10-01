from agent.agent import Agent


agent = Agent("Crie um arquivo calculadora.py com uma função somar(a, b) que receba dois números e retorne a soma deles.")

agent.run(max_iterations=3)

print("\nStatus final:", agent.state.status)
print("Iterações:", agent.state.iteration)
print("Última decisão:", agent.state.last_decision)
print("Último resultado:", agent.state.last_result)