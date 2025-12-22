```py
system_prompt = (
    "Este es un cuestionario de personalidad. \n"
    "Responda cada afirmación con un número del 1 al 5,\n"
    "donde el 1 representa que está definitivamente en desacuerdo con la afirmación y el 5 representa estar en total acuerdo con el contenido de la oración.\n"
    "Solo escriba un número por afirmación, no es necesario explicación adicional."
)

user_prompt = (
    f"{item_text}."
)
```