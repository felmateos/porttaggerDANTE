import re

contractions = {
    r"(?<![\w.])no(s)?(?![$\w])": r"em o\g<1>",
    r"(?<![\w.])na(s)?(?![$\w])": r"em a\g<1>",
    r"(?<![\w.])da(s)?(?![$\w])": r"de a\g<1>",
    r"(?<![\w.])do(s)?(?![$\w])": r"de o\g<1>",
    r"(?<![\w.])ao(s)?(?![$\w])": r"a o\g<1>",
    r"(?<![\w.])à(s)?(?![$\w])": r"a a\g<1>",
    r"(?<![\w.])pela(s)?(?![$\w])": r"por a\g<1>",
    r"(?<![\w.])pelo(s)?(?![$\w])": r"por o\g<1>",
    r"(?<![\w.])nesta(s)?(?![$\w])": r"em esta\g<1>",
    r"(?<![\w.])neste(s)?(?![$\w])": r"em este\g<1>",
    r"(?<![\w.])nessa(s)?(?![$\w])": r"em essa\g<1>",
    r"(?<![\w.])nesse(s)?(?![$\w])": r"em esse\g<1>",
    r"(?<![\w.])num(?![$\w])": r"em um",
    r"(?<![\w.])nuns(?![$\w])": r"em uns",
    r"(?<![\w.])numa(s)?(?![$\w])": r"em uma\g<1>",
    r"(?<![\w.])nisso(?![$\w])": r"em isso",
    r"(?<![\w.])naquele(s)?(?![$\w])": r"em aquele\g<1>",
    r"(?<![\w.])naquela(s)?(?![$\w])": r"em aquela\g<1>",
    r"(?<![\w.])naquilo(?![$\w])": r"em aquilo",
    r"(?<![\w.])duma(s)?(?![$\w])": r"de uma\g<1>",
    r"(?<![\w.])daqui(?![$\w])": r"de aqui",
    r"(?<![\w.])dali(?![$\w])": r"de ali",
    r"(?<![\w.])daquele(s)?(?![$\w])": r"de aquele\g<1>",
    r"(?<![\w.])daquela(s)?(?![$\w])": r"de aquela\g<1>",
    r"(?<![\w.])deste(s)?(?![$\w])": r"de este\g<1>",
    r"(?<![\w.])desta(s)?(?![$\w])": r"de esta\g<1>",
    r"(?<![\w.])desse(s)?(?![$\w])": r"de esse\g<1>",
    r"(?<![\w.])dessa(s)?(?![$\w])": r"de essa\g<1>",
    r"(?<![\w.])daí(?![$\w])": r"de aí",
    r"(?<![\w.])dum(?![$\w])": r"de um",
    r"(?<![\w.])donde(?![$\w])": r"de onde",
    r"(?<![\w.])disto(?![$\w])": r"de isto",
    r"(?<![\w.])disso(?![$\w])": r"de isso",
    r"(?<![\w.])daquilo(?![$\w])": r"de aquilo",
    r"(?<![\w.])dela(s)?(?![$\w])": r"de ela\g<1>",
    r"(?<![\w.])dele(s)?(?![$\w])": r"de ele\g<1>",
    r"(?<![\w.])nisto(?![$\w])": r"em isto",
    r"(?<![\w.])nele(s)?(?![$\w])": r"em ele\g<1>",
    r"(?<![\w.])nela(s)?(?![$\w])": r"em ela\g<1>",
    r"(?<![\w.])d'?ele(s)?(?![$\w])": r"de ele\g<1>",
    r"(?<![\w.])d'?ela(s)?(?![$\w])": r"de ela\g<1>",
    r"(?<![\w.])noutro(s)?(?![$\w])": r"em outro\g<1>",
    r"(?<![\w.])aonde(?![$\w])": r"a onde",
    r"(?<![\w.])àquela(s)?(?![$\w])": r"a aquela\g<1>",
    r"(?<![\w.])àquele(s)?(?![$\w])": r"a aquele\g<1>",
    r"(?<![\w.])àquilo(?![$\w])": r"a aquilo",
    r"(?<![\w.])contigo(?![$\w])": r"com ti",
    r"(?<![\w.])né(?![$\w])": r"não é",
    r"(?<![\w.])comigo(?![$\w])": r"com mim",
    r"(?<![\w.])contigo(?![$\w])": r"com ti",
    r"(?<![\w.])conosco(?![$\w])": r"com nós",
    r"(?<![\w.])consigo(?![$\w])": r"com si",
    r"(?<![\w.])pra(?![$\w])": r"para a",
    r"(?<![\w.])pro(?![$\w])": r"para o",
}


expansions = {
    r'^em o(s)?$': r'no\g<1>',
    r'^em a(s)?$': r'na\g<1>',
    r'^de a(s)?$': r'da\g<1>',
    r'^de o(s)?$': r'do\g<1>',
    r'^a o(s)?$': r'ao\g<1>',
    r'^a a(s)?$': r'à\g<1>',
    r'^por a(s)?$': r'pela\g<1>',
    r'^por o(s)?$': r'pelo\g<1>',
    r'^em esta(s)?$': r'nesta\g<1>',
    r'^em este(s)?$': r'neste\g<1>',
    r'^em essa(s)?$': r'nessa\g<1>',
    r'^em esse(s)?$': r'nesse\g<1>',
    r'^em um$': r'num',
    r'^em uns$': r'nuns',
    r'^em uma(s)?$': r'numa\g<1>',
    r'^em isso$': r'nisso',
    r'^em aquele(s)?$': r'naquele\g<1>',
    r'^em aquela(s)?$': r'naquela\g<1>',
    r'^em aquilo$': r'naquilo',
    r'^de uma(s)?$': r'duma\g<1>',
    r'^de aqui$': r'daqui',
    r'^de ali$': r'dali',
    r'^de aquele(s)?$': r'daquele\g<1>',
    r'^de aquela(s)?$': r'daquela\g<1>',
    r'^de este(s)?$': r'deste\g<1>',
    r'^de esta(s)?$': r'desta\g<1>',
    r'^de esse(s)?$': r'desse\g<1>',
    r'^de essa(s)?$': r'dessa\g<1>',
    r'^de aí$': r'daí',
    r'^de um$': r'dum',
    r'^de onde$': r'donde',
    r'^de isto$': r'disto',
    r'^de isso$': r'disso',
    r'^de aquilo$': r'daquilo',
    r'^de ela(s)?$': r"dela\g<1>",
    r'^de ele(s)?$': r"dele\g<1>",
    r'^em isto$': r'nisto',
    r'^em ele(s)?$': r'nele\g<1>',
    r'^em ela(s)?$': r'nela\g<1>',
    r'^em outro(s)?$': r'noutro\g<1>',
    r'^a onde$': r'aonde',
    r'^a aquela(s)?$': r'àquela\g<1>',
    r'^a aquele(s)?$': r'àquele\g<1>',
    r'^a aquilo$': r'àquilo',
    r'^com ti$': r'contigo',
    r'^não é$': r'né',
    r'^com mim$': r'comigo',
    r'^com nós$': r'conosco',
    r'^com si$': r'consigo',
    r'^para a$': r'pra',
    r'^para o$': r'pro'
}

def replace_keep_case(word, replacement, text):
    """
    Custom function for replace keeping the original case.
    Parameters
    ----------
    word: str
        Text to be replaced.
    replacement: str
        String to replace word.
    text:
        Text to be processed.
    Returns
    -------
    str:
        Processed string
    """

    def func(match):
        g = match.group()
        repl = match.expand(replacement)
        if g.islower():
            return repl.lower()
        if g.istitle():
            return repl.capitalize()
        if g.isupper():
            return repl.upper()
        if g[0].isupper():
            return repl[0].upper() + repl[1:]
        return repl

    return re.sub(word, func, text, flags=re.I)


def expand_contractions(text: str) -> str:
    """
    Replace contractions to their based form.
    Parameters
    ----------
    text: str
        Text that may contain contractions.
    Returns
    -------
    str:
        Text with expanded contractions.
    """

    for contraction in contractions.keys():
        replace_str = contractions[contraction]
        text = replace_keep_case(contraction, replace_str, text)

    return text
