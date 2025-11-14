from textual.theme import Theme


# https://userpage.fu-berlin.de/mirjamk/htmlkurs/16farben.html
TEXTUAL_THEME = Theme(
    name='pure-sweet16',
    primary='black',
    secondary='aqua',
    accent='lime',
    foreground='white',
    background='navy',
    surface='purple',
    panel='black',
    success='lime',
    warning='yellow',
    error='red',
    dark=True,
    variables={
        'footer-key-foreground': 'yellow',
    }
)