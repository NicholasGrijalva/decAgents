humor_prompt = (
            "Prompt: You are rating an image based on how funny it is. "
            "Take a detailed look at this image and, after analyzing it, "
            "provide a json object with the following fields:\n"
            "- image_description: a detailed description of the image and what makes it funny\n"
            "- rating: a rating from 1 to 10, where 1 is not funny and 10 is most funny\n"
            "- model: the name of the AI model used for this analysis"
        )

#todo eventually make it so this can take the imported text from ui and turn into prompt string. 