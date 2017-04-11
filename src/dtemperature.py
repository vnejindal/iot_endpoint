"""
Functions related to temperature read_sensor
"""

####### Unit Conversion Functions #########

def c2f(t):
    return (t*9/5.0)+32

def c2k(t):
    return t+273.15

def f2c(t):
    return (t-32)*5.0/9

def f2k(t):
    return (t+459.67)*5.0/9

def k2c(t):
    return t-273.15

def k2f(t):
    return (t*9/5.0)-459.67

def s2s(t): #Same to Same
    return t

####### Unit Conversion Functions #########

index_dict = {'kelvin':0, 'celcius': 1, 'fahrenheit': 2}
marray = [[s2s, k2c, k2f], [c2k, s2s, c2f], [f2k, f2c, s2s]]

def convert_unit(reading, funit, tunit):
    """
    Converts 'reading' from 'funit' to 'tunit'
      funit, tunit: kelvin, celcius, fahrenheit (all in lowercase) 
    
                 kelvin   celcius    fahrenheit 
      kelvin       s2s      k2c         k2f 
      celcius      c2k      s2s         c2f
      fahrenheit   f2k      f2c         s2s
    """
    global index_dict
    global marray
    return marray[index_dict[funit]][index_dict[tunit]](reading)

#print convert_unit(1234, 'kelvin', 'celcius')
