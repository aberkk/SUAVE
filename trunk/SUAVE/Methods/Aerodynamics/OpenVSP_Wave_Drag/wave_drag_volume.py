# wave_drag_volume.py
# 
# Created:  Jun 2014, T. Macdonald
# Modified: Apr 2017, T. Macdonald

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

import copy
import numpy as np

# ----------------------------------------------------------------------
#   Wave Drag Volume
# ----------------------------------------------------------------------

def wave_drag_volume(conditions,geometry,flag105,num_slices=20,num_rots=10):
    """ SUAVE.Methods.wave_drag_volume(conditions,configuration,fuselage)
        computes the wave drag due to lift 
        Based on http://adg.stanford.edu/aa241/drag/ssdragcalc.html
        
        Inputs: total_length, Sref, t/c, Mach

        Outputs:

        Assumptions:

        
    """
    
    import vsp

    # unpack inputs
    freestream   = conditions.freestream
    ref_area     = geometry.reference_area
    tag          = geometry.tag
    
    # conditions
    Mc  = copy.copy(freestream.mach_number)
    cd_w_all = np.zeros(np.shape(Mc))
    vsp.ClearVSPModel()
    vsp.ReadVSPFile(tag+'.vsp3')
    vsp.SetIntAnalysisInput('WaveDrag', 'NumSlices', [num_slices])
    vsp.SetIntAnalysisInput('WaveDrag', 'NumRotSects', [num_rots]) 
    
    if flag105 is True:
        vsp.SetDoubleAnalysisInput('WaveDrag', 'Mach', [1.05])    
        ridwd = vsp.ExecAnalysis('WaveDrag')        
        cd_w = vsp.GetDoubleResults(ridwd,'CDWave')
        cd_w = cd_w[0]*100./ref_area # default ref area in VSP doesn't seem to have an easy change
        return cd_w
    
    # Read data from file if possible, otherwise calculate new value
    for ii,mach in enumerate(Mc):
        if mach[0] >= 1.05:
            old_array = np.load('volume_drag_data_' + geometry.tag + '.npy')
            if np.any(old_array[:,0]==mach[0]):
                cd_w = np.array([[float(old_array[old_array[:,0]==mach[0],1])]])
            else:
                vsp.SetDoubleAnalysisInput('WaveDrag', 'Mach', [float(mach)])
                ridwd = vsp.ExecAnalysis('WaveDrag') 
                cd_w = vsp.GetDoubleResults(ridwd,'CDWave')
                cd_w = cd_w[0]*100./ref_area
                new_save_row = np.array([[mach[0],cd_w]])
                comb_array = np.append(old_array,new_save_row,axis=0)
                np.save('volume_drag_data_' + geometry.tag + '.npy', comb_array)
            cd_w_all[ii] = cd_w
    
    return cd_w_all