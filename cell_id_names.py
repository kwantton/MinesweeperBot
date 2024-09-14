# naming variables for convenience
def labellize(label) -> str:
    return f'images/{label}.png'

flag        = labellize('flag')
mine        = labellize('mine')
unclicked   = labellize('unclicked')
safe        = labellize('safe')

def read_number_from_label(label : str) -> int:
    return int(label[7])                # the number is the 8th letter, so label[7], of the label. No regex needed unless the location or name is changed, of course.