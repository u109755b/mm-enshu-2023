from transformers import AutoModelForCausalLM, AutoTokenizer
from utils.constants import MODEL2PATH, MODEL2TEPLATE, TASK2PROMPT

lguage_model = AutoModelForCausalLM.from_pretrained(MODEL2PATH["openhermes"]).to(
    "cuda:0"
)
tokenizer = AutoTokenizer.from_pretrained(MODEL2PATH["openhermes"])

input_s = input("Enter a sentence: ")
while input_s != "exit":
    input_ids = tokenizer.encode(
        MODEL2TEPLATE["openhermes"].format(user_message=input_s), return_tensors="pt"
    ).to("cuda:0")
    outputs = lguage_model.generate(
        input_ids, max_length=1000, do_sample=True, top_p=0.9, top_k=50
    )
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(generated_text)
    input_s = input("Enter a sentence: ")
