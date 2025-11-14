from textual.theme import Theme


TEXTUAL_THEME = Theme(
    name='classic-blue',
    primary='#81A1C1',
    secondary='#3A5366',
    accent='#81A1C1',
    foreground='#e9e9e9',
    background='#2E3440',
    success='#A3BE8B',
    warning='#EBCB8B',
    error='#BF616A',
    surface='#3B4252',
    panel='#003768',
    dark=True,
    variables={
        'block-cursor-text-style': 'none',
        'footer-key-foreground': '#88C0D0',
        'input-selection-background': '#81a1c1 35%',
    },
)