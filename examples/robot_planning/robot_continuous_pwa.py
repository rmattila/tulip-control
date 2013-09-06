#!/usr/bin/env python
"""
This example is an extension of the robot_continuous.py
code by Petter Nilsson and Nok Wongpiromsarn. It demonstrates 
the use of TuLiP for systems with piecewise affine dynamics.

Necmiye Ozay, August 26, 2012
"""

import numpy as np

from tulip import *
from tulip import spec, synth
import tulip.polytope as pc
from tulip.abstract import prop2part, discretize

# Problem parameters
input_bound = 0.4
uncertainty = 0.05

# Continuous state space
cont_state_space = pc.Polytope.from_box(np.array([[0., 3.],[0., 2.]]))

# Assume, for instance, our robot is traveling on a nonhomogenous surface (xy plane), 
# resulting in different dynamics at different parts of the plane. 
# Since the continuous state space in this example is just xy position, different
# dynamics in different parts of the surface can be modeled as a piecewise 
# affine system as follows:

# subsystem0
A0 = np.array([[1.1052, 0.],[ 0., 1.1052]])
B0 = np.array([[1.1052, 0.],[ 0., 1.1052]])
E0 = np.array([[1,0],[0,1]])
U0 = pc.Polytope.from_box(input_bound*np.array([[-1., 1.],[-1., 1.]]))
W0 = pc.Polytope.from_box(uncertainty*np.array([[-1., 1.],[-1., 1.]]))
dom0 = pc.Polytope.from_box(np.array([[0., 3.],[0.5, 2.]]))
sys_dyn0 = hybrid.LtiSysDyn(A0,B0,E0,[],U0,W0,dom0)


# subsystem1
A1 = np.array([[0.9948, 0.],[ 0., 1.1052]])
B1 = np.array([[-1.1052, 0.],[ 0., 1.1052]])
E1 = np.array([[1,0],[0,1]])
U1 = pc.Polytope.from_box(input_bound*np.array([[-1., 1.],[-1., 1.]]))
W1 = pc.Polytope.from_box(uncertainty*np.array([[-1., 1.],[-1., 1.]]))
dom1 = pc.Polytope.from_box(np.array([[0., 3.],[0., 0.5]]))
sys_dyn1 = hybrid.LtiSysDyn(A1,B1,E1,[],U1,W1,dom1)


# Build piecewise affine system from its subsystems
sys_dyn = hybrid.PwaSysDyn([sys_dyn0,sys_dyn1], cont_state_space)


# Continuous proposition
cont_props = {}
cont_props['home'] = pc.Polytope.from_box(np.array([[0., 1.],[0., 1.]]))
cont_props['lot'] = pc.Polytope.from_box(np.array([[2., 3.],[1., 2.]]))

# Compute the proposition preserving partition of the continuous state space
cont_partition = prop2part.prop2part(cont_state_space, cont_props)
disc_dynamics = discretize.discretize(cont_partition, sys_dyn, closed_loop=True, \
                N=8, min_cell_volume=0.1, verbose=0)


# Specifications

# Environment variables and assumptions

env_vars = {'park'}
env_init = set()                # empty set
env_prog = '!park'
env_safe = set()                # empty set

# System variables and requirements

sys_vars = {'X0reach'}
sys_init = {'X0reach'}          
sys_prog = {'home'}               # []<>home
sys_safe = {'next(X0reach) == lot || (X0reach && !park)'}
sys_prog |= {'X0reach'}

# Create the specification
specs = spec.GRSpec(env_vars, sys_vars, env_init, sys_init,
                    env_safe, sys_safe, env_prog, sys_prog)

# Synthesize
ctrl = synth.synthesize('jtlv', specs, disc_dynamics.ofts)


# Generate a graphical representation of the controller for viewing
#! TODO: save_png should probably not be a method in transys?
if ctrl:
    ctrl.save('png', 'robot_gr1.png')

# Simulation