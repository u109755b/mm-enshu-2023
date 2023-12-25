MODEL2PATH = {
    "openhermes": "/workspace/models/OpenHermes-2.5-Mistral-7B",
    "zbeta": "/workspace/models/zephyr-7b-beta",
    "dolphin221": "/workspace/models/dolphin-2.2.1-mistral-7b",
    "psyfighter2": "/workspace/models/LLaMA2-13B-Psyfighter2",
}
MODEL2TEPLATE = {
    "openhermes": "<|im_start|>system\nYou are an AI assistant that follows instructions very well. Finish the tasks that given by the user as faithfully as you can.<|im_end|>\n<|im_start|>user\n{user_message}<|im_end|>\n<|im_start|>assistant\n",
    "zbeta": "<|system|>\nYou are an AI assistant that follows instructions very well. Finish the tasks that given by the user as faithfully as you can.</s>\n<|user|>\n{user_message}</s>\n<|assistant|>\n",
    "dolphin221": "<|im_start|>system\nYou are an AI assistant that follows instructions very well. Finish the tasks that given by the user as faithfully as you can.<|im_end|>\n<|im_start|>user\n{user_message}<|im_end|>\n<|im_start|>assistant\n",
    "psyfighter2": "### Instruction: \n{user_message}\n### Response: \n",
}
TASK2PROMPT = {
    "get_character_list": (
        "Start of Contents:\n{contents}\nEnd of Contents\n"
        "Instructions:\n"
        "You are given some contents from a novel segment. Your task is to extract relevant characters and introduction information for each character to construct a basic Knowledge Graph.\n"
        "Follow these steps:\n"
        "1. Read the provided contents\n"
        "2. Extract characters and check if there are any redundancy or duplication of characters. Exclude generic references such as 'crowd' or 'others'.\n"
        "3. For each character in the character list, extract their inforomation from the text segment.\n"
        "4. Check information you have extracted for each character. Only keep the information that is very essential and can identify each character.\n"
        "5. Create a structured list of characters in the format:\n"
        'Index i: [name: "Character Name", introduction: "brief, keyword-like description, (use "NONE" if no specific information is available)"],\n'
        "where 'Index i' is a consecutive integer starting at 1.\n"
    ),
    "get_character_info": (
        "Start of Contents:\n{contents}\nEnd of Contents\n"
        "Character list: {character_list}\n"
        "You are given some contents from a novel segment and a character list. Your task is to extract character introduction information for constructing a basic Knowledge Graph. The focus is on direct, defining attributes of the characters, not on their actions or storyline.\n"
        "Follow these steps:\n"
        "1. Read the provided text segment.\n"
        "2. For each character in the character list, extract their inforomation from the text segment.\n"
        "3. Check information you have extracted for each character. Only keep the information that is very essential that can identify each character.\n"
        "4. In cases where there is no information available that directly describes a character, record 'NONE' for the attributes of that character.\n"
        "5. Create a structured list in the format:\n"
        'Character 1: [introduction: "brief, keyword-like description or NONE if no information available"],\n'
        'Character 2: [introduction: "brief, keyword-like description or NONE if no information available"],\n'
        "...\n"
    ),
}
