import os
import imagej
import cv2
import ast
import numpy as np
from io import StringIO
from skimage import io, exposure, img_as_uint, img_as_ubyte, img_as_float
from glob import glob
from contextlib import redirect_stderr

def apply_tform(im, ref, tform, multichannel=False):
    if multichannel:
        height, width, _ = ref.shape
    else:
        height, width = ref.shape
    transformed_img = cv2.warpPerspective(im.astype(np.uint8),
                        tform, (width, height), flags=cv2.INTER_CUBIC)
    return transformed_img

def find_pop_string(msg, s, e):
    check = msg.find(s)
    if check == -1:
        return -1, msg
    found = msg[msg.find(s)+len(s):msg.find(e)+len(e)]
    pop = msg[msg.find(e)+len(e):]
    return found, pop

# initialize imagej
ij = imagej.init('sc.fiji:fiji', mode='headless')
print(f"ImageJ version: {ij.getVersion()}")

# setup plugin and parameters
plugin = "Extract SIFT Correspondences"
params = {
    'source_image': '',
    'target_image': '',
    'initial_gaussian_blur': 3.60,
    'steps_per_scale_octave': 3,
    'minimum_image_size': 56,
    'maximum_image_size': 1280, 
    'feature_descriptor_size': 8, 
    'feature_descriptor_orientation_bins': 8,
    'closest/next_closest_ratio': 0.92,
    'filter maximal_alignment_error': 100,
    'minimal_inlier_ratio': 0.05,
    'minimal_number_of_inliers': 7, 
    'expected_transformation': 'Similarity'
}

# setup macros
macro_openIm = """
#@ String path
open(path);
"""
macro_closeAllIm = """
close("*");
"""

# setup sift stuff
R1_ims = glob('BF_set/Aperio/*') 
R2_ims = glob('BF_set/CAMM/*') 
source_ims = glob('BF_set/CAMM/*')  
out_path = 'BF_set/Registered'
R1_ims.sort()
R2_ims.sort()
source_ims.sort()
os.makedirs(out_path, exist_ok=True)

# ImageJ logging output is returned as stderr back to Python.
with redirect_stderr(StringIO()) as log:
    for R1_im, R2_im, source_im in zip(R1_ims, R2_ims, source_ims):
        ij.py.run_macro(macro_closeAllIm)
        ij.py.run_macro(macro_openIm, {'path': os.path.join(os.getcwd(), R1_im)})
        ij.py.run_macro(macro_openIm, {'path': os.path.join(os.getcwd(), R2_im)})

        params['source_image'] = os.path.basename(R2_im)
        params['target_image'] = os.path.basename(R1_im)

        result = ij.py.run_plugin(plugin, params)
        ij.py.run_macro(macro_closeAllIm)
        # tform_string = lambda msg, s, e : msg[msg.rfind(s)+len(s):msg.rfind(e)+len(e)]

tforms = []
searching = True
msg = log.getvalue()
tform = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
for i in range(len(source_ims)):
    error_idx = msg.find('No correspondences found.')
    tform_idx = msg.find('AffineTransform')
    if error_idx < tform_idx and error_idx != -1 or tform_idx == -1:
        error, msg = find_pop_string(msg, 'No correspondences found.', 'No correspondences found.')
        if error != -1:
            print(f'Slide registration failed at {source_ims[i]}, no correspondence found. Use previous tform matrix.')
            tforms.append(tform)
    elif error_idx == -1 and tform_idx == -1:
        print('Process done.')
    else:
        t_string, msg = find_pop_string(msg, 'AffineTransform', ']]')
        # t_string = t_string.replace('E-', '')
        tform = ast.literal_eval(t_string)
        tform = np.asarray(tform).reshape((2, 3))
        tform = np.concatenate((tform, np.array([[0, 0, 1]])), 0)
        tforms.append(tform)
        # break

for R1_im, source_im, tform in zip(R1_ims, source_ims, tforms):
    im_source = img_as_ubyte(io.imread(source_im))
    im_target = img_as_ubyte(io.imread(R1_im))

    t_target = apply_tform(im_source, im_target, tform.astype(np.float), multichannel=True)

    im_name = os.path.basename(source_im)
    io.imsave(os.path.join(out_path, im_name), t_target)