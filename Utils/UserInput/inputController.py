from .speechInput import speechInput


def receiveInput(text):

    prompt = input(f"{text} (Press 'Enter' for Speech)→ \n").strip().lower()
    return prompt or speechInput()

