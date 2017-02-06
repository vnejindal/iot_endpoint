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

fname_dict[fnameA] = eval(fnameA)
fname_dict[fnameB] = eval(fnameB)
"""
fname_dict[fnameA] = func_name_A
fname_dict[fnameB] = func_name_B
"""

def entry():
    parsed_json = {}
    parsed_json['id'] = 10
    parsed_json['type'] = 'temperature'
    
    #print type(parsed_json)
    print fname_dict
    
    fname_dict[fnameA]()
    fname_dict[fnameB](parsed_json)

entry()
