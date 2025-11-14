from textual.theme import Theme


TEXTUAL_THEME = Theme(
    name='classic-black',
    primary='#7CA6C2',
    secondary='#5B5B5B',
    accent='#A9B7C6',
    foreground='#E5E5E5',
    background='#151618',
    surface='#1E2022',
    panel='#101112',
    boost="#016F60",
    success='#A3C995',
    warning='#E6C384',
    error='#D67B76',
    dark=True,
    variables={
        'footer-key-foreground': "#D2D05F",
        "input-cursor-text-style": "reverse",
    }
)