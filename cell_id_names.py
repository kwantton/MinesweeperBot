# naming variables for convenience
def cell_id(label):
    return f'images/{label}.png'

flag    = cell_id('flag')
mine    = cell_id('mine')
unclicked  = cell_id('unclicked')
safe    = cell_id('safe')