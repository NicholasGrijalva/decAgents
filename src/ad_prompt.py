ad_prompt = (
    "Prompt: You are CHOOSING an image based on how good of an advertisement it is. "
    "Take a detailed look at these images and provide your reasoning only for the CHOSEN analysis in the exact JSON format shown below. "
    "Do not include any text outside of this JSON structure.\n\n"
    "{\n"
    '    "image_description": "<provide a detailed description of the image and what makes it funny>",\n'
    '    "choice": <integer between 1 and the number of images. Denoting which image you chose.>\n'
    "}"
)