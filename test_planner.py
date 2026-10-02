from agent.planner import Planner

planner = Planner()

plan = planner.create_plan(
    "Crie uma calculadora em Python com soma e subtração."
)

print("\nPLANO GERADO:")
print(plan)

print("\nETAPAS:")

for index, step in enumerate(plan["steps"], start=1):
    print(f"{index}. {step}")