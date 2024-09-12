import numpy as np 

def standard(r, params, z0):
    r_min = r.min()
    c = 1/params['Radius']
    k = params['Conic']
    def core(r):
        delta = 1-(1+k)*c**2*r**2
        delta = np.where(delta < 0, 0, delta)

        z = c*r**2/(1+np.sqrt(delta))
        return z 
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
        delta = 1-(1+k)*c**2*(r-r0)**2
        delta = np.where(delta < 0, 0, delta)
        z = c*(r-r0)**2/(1+np.sqrt(delta))
        return z
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

PARAMS = {
    "Standard": ['SemiDiameter', 'Radius', 'Conic', ],
    "OffsetCircle": ['SemiDiameter', 'Radius', 'Conic', 'Center', ],
    "EvenAsphere": ['SemiDiameter','Radius', 'Conic', 'AsphereTerm', 'AsphereParams' ],
    "Line": ['SemiDiameter', 'EndZ']
}

HELP_STRING ={
    'surface_explain':{
    "Standard" : "标准曲面，也就是球面和非球面",
    "OffsetCircle": "偏心圆，圆心不在中心，常用来作为弧段之间的圆角过渡",
    "EvenAsphere": "偶次非球面",
    "Line": "直线"
    },
    'params_explain':{
    "SemiDiameter": "半口径，弧段边缘到光轴的距离",
    "Radius": "曲率半径",
    "Conic": "圆锥系数 Q值(Conic值)",
    "Center": "偏中心圆的圆心到光轴的距离",
    "AsphereTerm": "偶次非球面项的个数",
    "AsphereParams": "偶次非球面项各项的系数",
    "EndZ": "直线终点的矢高"
    }
}