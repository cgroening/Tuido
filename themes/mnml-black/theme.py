from textual.theme import Theme


TEXTUAL_THEME = Theme(
    name='mnml-black',
    primary="#C7C7C7",
    secondary='#5B5B5B',
    accent="#C5C5C5",
    foreground='#E5E5E5',
    background="#1A1A1A",
    surface="#1C1C1C",
    panel='#101112',
    boost="#555555",
    success="#A8C79D",
    warning="#DFC89E",
    error='#D67B76',
    dark=True,
    variables={
        'footer-key-foreground': "#919191",
        "input-cursor-text-style": "reverse",
    }
)