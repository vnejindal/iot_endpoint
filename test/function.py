"""
test file for experiment on functions 
"""

initial_name = 'func_name_'

endname = ['A', 'B']

def func_name_A():
    print 'func_name_A'

def func_name_B(id):
    print 'func_name_B', id
    
fnameA = initial_name + endname[0]
fnameB = initial_name + endname[1]

fname_dict = {}

fname_dict[fnameA] = func_name_A
fname_dict[fnameB] = func_name_B

fname_dict[fnameA]()
fname_dict[fnameB](10)