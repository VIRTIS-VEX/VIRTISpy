# VIRTISpy

A Python class for read and manipulate the VIRTIS-VEX data cubes.

***

## Overview

 1.  VIRTIS
 2.  VIRTIS Data
 3.  VIRTISpy Methods
 4.  VIRTISpy Installation
 5.  Usage
 6.  Brief History

***

## 1. VIRTIS 


VIRTIS (Visible and Infrared Thermal Imaging Spectrometer) is a complex instrument initially devoted to the remote sensing study of comet Wirtanen on the Rosetta mission, at wavelengths between 0.3 and 5 µm. The focal planes, with state of the art CCD and infrared detectors achieve high sensitivity for low emissivity sources. Due to the high flexibility of operational modes of VIRTIS, these performances are also ideally adapted for the study of Venus atmosphere, both on night and day side. VIRTIS is therefore aimed to provide a 4-dimensional study of Venus atmosphere (2D imaging + spectral dimension + temporal variations), the spectral variations permitting a sounding at different levels of the atmosphere, from the ground up to the thermosphere. The infrared capability of VIRTIS is especially well fitted to the thermal sounding of the night side atmosphere (Taylor et al, 1997), which give a tomography of the atmosphere down to the surface.

***

## 2. VIRTIS Data


The VIRTIS data are spectral cubes stored in [PDS format](http://pds.nasa.gov).

VIRTIS data schema:

	             _____________________________________   ____
                /                                    /| /   /|
               /                                    / |/   / |
     Bands    /          Data Core                 /  /   /  |
             /                                    /  /   /   |
            /____________________________________/  /__ /    |
           |            Samples                  |  |  |     |
           |                                     |  |  |     | Side Planes
           |                              Lines  |  |  |     |
           |                                     |  |  |    /
           |                                     |  |  |   / 
           |                                     |  |  |  /   
           |                                     | /|  | /   
           |_____________________________________|/ |__|/    
             /                                     /  /      
            /_____________________________________/  /
           |        Bottom Planes                 | /
           |______________________________________|/



The dimensions, in Bands, Samples and Lines, of the Data Core, Side Planes and Bottom Planes are reported in the header of the file at the specifics key.

In the VIRTIS data set there are three different kind of files.

  + **\*\.QUB** - Raw data file
  + **\*\.CAL** - Calibrated data file
  + **\*\.GEO** - Geometry of the each pixel of the raw or calibrated file.
	
***

## 3. VIRTISpy Methods:

 __headerValue( _key_ )__ ( _key_  string ) return the value of the PDS label for the PDS the selected PDS keyword;  
 __getBand( _band_ )__ ( _band_ integer ) return a float matrix corresponding to the selected band;  
 __getSpectrum( _sample_ , _line_ )__ ( _sample_ integer; _line_ integer ) return an array containing the VIRTIS spectrum for the pixel at a specific sample and line;  
 __getWave()__ return an array containing the wavelength of each VIRTIS band;  
 __getHK( _key_ , _line_ )__ ( _key_ string, _line_ integer ) return the housekeeping value for the specific key and a specific line;  
 __getGeometry(  _plane_ )__ ( _plane_ integer or string ) return the geometry plane of the cube.


***  

##4. Installation:


To install from source, VIRTISpy-X.Y.Z.tar.gz from the [VIRTISpy GitHube site](https://github.com/RomoloPoliti/VIRTISpy), unpack, cd to VIRTISpy-X.Y.Z and run

```bash
	python setup.py install
```

***

## 5. Usage


Create the VIRTISpy object:

```python
	>>>from VIRTISpy import *
	>>>cb=VIRTISpy('VV0000_00.CAL')
```

Visualize the spectrum of the pixel (100,100):

```python
	>>>import matplotlib.pyplot as plt
	>>>sp=cb.getSpectrum(100,100)
	>>>sp=where(sp<=0,0,sp) # necessary to remove the not valid values
	>>>wl=cb.getWave()
	>>>plt.plot(wl,sp)
	>>>plt.xlabel('Wavelength [$\mu m$]')
	>>>plt.ylabel('%s [%s]'%(cb.headerValue('CORE_NAME'),cb.headerValue('CORE_UNIT')))
	>>>plt.show()
```

Visualize a picture:

```python
	>>> import matplotlib.cm as cm
	>>> img=cb.getBand(150)
	>>> img=where(img<=0,0,img)
	>>> plt.imshow(img,origin='lower',cmap=cm.gray,axes=None)
	>>> plt.show()
```


## 6. Brief History


VIRTISpy was started by Romolo Politi in November 2011 as Python porting of the IDL VIRTISpds developped by Stefan Erard.
