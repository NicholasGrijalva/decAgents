humor_prompt = (
    "Prompt: You are rating an image based on how funny it is. "
    "Take a detailed look at this image and provide your analysis in the exact JSON format shown below. "
    "Do not include any text outside of this JSON structure.\n\n"
    "{\n"
    '    "image_description": "<provide a detailed description of the image and what makes it funny>",\n'
    '    "rating": <integer between 1 and 10>,\n'
    '    "model": "<your model name>"\n'
    "}"
)
#todo eventually make it so this can take the imported text from ui and turn into prompt string. 