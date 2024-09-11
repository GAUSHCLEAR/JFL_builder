import numpy as np 

def standard(r, params, z0):
    r_min = r.min()
    c = 1/params['Radius']
    k = params['Conic']
    def core(r):
        return c*r**2/(1+np.sqrt(1-(1+k)*c**2*r**2))
    z = core(r)
    z_min = core(r_min)
    return z - z_min + z0

def offset_circle(r, params, z0):
    r_min = r.min()
    r_max = r.max()
    c = 1/params['Radius']
    k = params['Conic']
    r0 = params['Center']
    def core(r):
        return c*(r-r0)**2/(1+np.sqrt(1-(1+k)*c**2*(r-r0)**2))
    z = core(r)
    z_min = core(r_min)
    return z - z_min + z0

def even_asphere(r,params,z0): 
    c = 1/params['Radius'] 
    k = params['Conic'] 
    def core(r):
        z = c*r**2/(1+np.sqrt(1-(1+k)*c**2*r**2)) 
        asphere = 0 
        for i in range(params['AsphereTerm']): 
            asphere += params['AsphereParams'][i]*r**(2*(i+1)) 
        return z + asphere
    z = core(r)
    z_min = core(r.min())
    return z -z_min + z0

def line(r, params, z0):
    delta_z = params['EndZ'] - z0
    start_r = r.min()
    delta_r = params['SemiDiameter'] - start_r
    z = delta_z * (r - start_r) / delta_r
    return z + z0

TYPE_TO_FUNCTION = {
    'Standard': standard,
    'OffsetCircle': offset_circle,
    'EvenAsphere': even_asphere,
    'Line': line
}