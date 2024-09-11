# naming variables for convenience
def labellize(label) -> str:
    return f'images/{label}.png'

flag        = labellize('flag')
mine        = labellize('mine')
unclicked   = labellize('unclicked')
safe        = labellize('safe')