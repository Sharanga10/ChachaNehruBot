from llama_cpp import Llama

llm = Llama(
    model_path="/Users/abhismac/models/sarvam/Sarvam-M-24B-Q4_K_M.gguf",
    n_ctx=2048,
    n_threads=6
)

output = llm("Q: भारत के प्रथम प्रधानमंत्री कौन थे?\nA:", max_tokens=32)
print(output)