# Automatic Histological Image Registration
Registration of histological images using stitching and registration plugins in [ImageJ/FIJI](https://imagej.net/software/fiji/) via [PyImageJ](https://github.com/imagej/pyimagej).

## Requirements
`env.yml` and [PyImageJ](https://github.com/imagej/pyimagej).

## Generate intermediate modality for multimodal image registration
Registering images of different imaging modalities can be difficult. One can convert the images into a common intermediate modality (pseudo modality) using methods such as [CoMIR](https://github.com/MIDA-group/CoMIR).  
To do this for histological images, patch extraction is often needed due to the big image size. Images are tiled into patches, converted into pseudo modality, stitched using [Grid/Collection plugin](https://imagej.net/plugins/grid-collection-stitching) in ImageJ/FIJI, and then registered. [pseudo_modality.ipynb](pseudo_modality.ipynb)
<div align="center">
  <img src="figures/stitching.png" width="900px" />
</div>

## Perform registration in pseudo modality
Once the images are converted into the common intermediate modality, conventional monomodal image registration such as SIFT feature matching can work well.  
Monomdoal image registraion using [SIFT landmark Correspondences](https://imagej.net/plugins/feature-extraction) in ImageJ/FIJI. [ij_sift_registration.ipynb](ij_sift_registration.ipynb)
<div align="center">
  <img src="figures/registration.png" width="900px" />
</div>
