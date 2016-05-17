#!/usr/bin/python
# -*- coding: utf8 -*-

""" Calculate the attenuation of a rectangular waveguide operated in TE10 mode """

import scipy.constants as co
import numpy as np
from skrf.tlineFunctions import *
from tabulate import tabulate

pi = np.pi
mue0 = co.mu_0
eps0 = co.epsilon_0
c0 = co.speed_of_light
eta0 = co.physical_constants['characteristic impedance of vacuum'][0]

def treat_wg_dimension(dimension):
    if np.shape(dimension) == (2,):
        a = dimension[0]
        b = dimension[1]
    else:
        a = dimension
        b = a/2.0
    return (a, b)

def wavenumber(f):
    return 2*pi*f/c0

def waveguide_attenuation_TE10(f, dimension, Rs):
    (a, b) = treat_wg_dimension(dimension)
    k  = wavenumber(f)
    kx = pi/a
    beta = np.sqrt(k**2 - kx**2)
    dB_per_Np = 8.686
    return Rs*(2*b*pi**2+a**3*k**2)/(a**3*b*beta*k*eta0) * dB_per_Np

def f_co(dimension, m=1, n=0):
    (a, b) = treat_wg_dimension(dimension)
    return c0/2 * np.sqrt( (m/a)**2 + (n/b)**2 )

data = []
for f_eval in np.array([320, 350, 380])*1e9:
    data.append([432, f_co(864e-6/2)/1e9, f_eval/1e9, waveguide_attenuation_TE10(f_eval, 432e-6, surface_resistivity(f_eval, 1.0/66e6, 1.0)), waveguide_attenuation_TE10(f_eval, 432e-6, surface_resistivity(f_eval, 1.0/10e6, 1.0))])
    data.append([480, f_co(480e-6)/1e9, f_eval/1e9, waveguide_attenuation_TE10(f_eval, 480e-6, surface_resistivity(f_eval, 1.0/66e6, 1.0)), waveguide_attenuation_TE10(f_eval, 480e-6, surface_resistivity(f_eval, 1.0/10e6, 1.0))])
    data.append([864, f_co(864e-6)/1e9, f_eval/1e9, waveguide_attenuation_TE10(f_eval, 864e-6, surface_resistivity(f_eval, 1.0/66e6, 1.0)), waveguide_attenuation_TE10(f_eval, 864e-6, surface_resistivity(f_eval, 1.0/10e6, 1.0))])

headers = [u"Base width (µm)", u"Cut-off (GHz)", u"f_evaluated (GHz)", u"a_c (dB/m), Cu", u"a_c (dB/m), Brass"]

print( tabulate(data, headers) )

