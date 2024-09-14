LANGUAGE_CHOICES = [
    ("en", "English"),
    ("es", "Spanish"),
    ("ru", "Russian"),
    ("he", "Hebrew"),
    ("ar", "Arabic"),
    ("zh", "Chinese"),
    ("de", "German"),
    ("la", "Latin"),
    ("fr", "French"),
    # Add more languages as needed
]

LANGUAGE_CHOICE_DICT = dict(LANGUAGE_CHOICES)

SUPPORTED_LANGUAGES = [code for code, _ in LANGUAGE_CHOICES]
