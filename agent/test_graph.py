from agent.graph import graph


result = graph.invoke({
    "question": "Explain what DataPilot is in one sentence.",
    "answer": "",
})


print("\n===== DataPilot Agent =====")
print("Question:", result["question"])
print("Answer:", result["answer"])