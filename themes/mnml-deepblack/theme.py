from textual.theme import Theme


TEXTUAL_THEME = Theme(
    name='mnml-deepblack',
    primary="#C7C7C7",
    secondary='#5B5B5B',
    accent="#C5C5C5",
    foreground='#E5E5E5',
    background="#000000",
    surface="#1C1C1C",
    panel='#101112',
    boost="#555555",
    success="#50CE23",
    warning="#E4AC45",
    error="#DF372F",
    dark=True,
    variables={
        'footer-key-foreground': "#E7E7E7",
        "input-cursor-text-style": "reverse",
    }
)