


    brew install virtualenv
    virtualenv -p python3.7 venv
    source venv/bin/activate

Install genet:

    pip3 install -e .

## Problems:

### virtual env cannot find python 3.7

```
RuntimeError: failed to find interpreter for Builtin discover of python_spec='python3.7'
```

    brew install pyenv
    pyenv install 3.7.13
    virtualenv -p /path/to/.pyenv/versions/3.7.13/bin/python3.7 venv

### Problems installing pandas, numpy, scipy, scikit-learn

```
ERROR: Could not build wheels for numpy, which is required to install pyproject.toml-based projects
```

try running:

    python3 -m pip install --upgrade pip
    brew reinstall openblas
    pip3 install cython 
    OPENBLAS="$(brew --prefix openblas)" MACOSX_DEPLOYMENT_TARGET=11.1 pip3 install numpy==1.21.6 --no-use-pep517
    OPENBLAS="$(brew --prefix openblas)" MACOSX_DEPLOYMENT_TARGET=11.1 pip3 install pandas==1.3.5 --no-use-pep517
    pip install pybind11 pythran
    OPENBLAS="$(brew --prefix openblas)" CFLAGS="-falign-functions=8 ${CFLAGS}" pip3 install scipy==1.7.0 --no-use-pep517
    OPENBLAS="$(brew --prefix openblas)" MACOSX_DEPLOYMENT_TARGET=11.1 pip3 install scikit-learn==0.24.2 --no-use-pep517

before running `pip3 install -e .` again.

If the problem persists, try conda



### GeNet installs but while importing spatial libraries are missing

Importing the `genet` package may result in an error:

```
OSError: dlopen(/Users/kasia.kozlowska/PycharmProjects/CML/genet/venv/lib/libgeos_c.dylib, 0x0006): tried: 
'/path/to/venv/lib/libgeos_c.dylib' (no such file), 
'/usr/local/lib/libgeos_c.dylib' (no such file), '/usr/lib/libgeos_c.dylib' (no such file)
```

from [here](https://stackoverflow.com/questions/11294556/missing-libgeos-c-so-on-osx), try:

    brew uninstall geos gdal geoip libspatialite librasterlite spatialite-gui spatialite-tools
    brew cleanup
    brew install geos
    brew install gdal geoip libspatialite librasterlite spatialite-gui spatialite-tools
    brew cleanup

(Find the actual paths to those files on your computer, they're not guaranteed to be in the same place as below)

    GEOS_LIBRARY_PATH = '/System/Volumes/Data/opt/homebrew/Cellar/geos/3.11.0/' 
    GDAL_LIBRARY_PATH = '/Library/Frameworks/GDAL.framework/GDAL' 
    GEOIP_LIBRARY_PATH = '/usr/local/Cellar/geoip/1.4.8/lib/libGeoIP.dylib'

If you need help finding the libraries try looking for them:

    `find . -name "libgeos*"`

This worked for some people. Not me though, I found and created symlinks for the following files 

    sudo ln -s /System/Volumes/Data/opt/homebrew/Cellar/geos/3.11.0/lib/libgeos_c.dylib /usr/local/lib/libgeos_c.dylib
    ln -s /System/Volumes/Data/opt/homebrew/Cellar/geoip/1.6.12/lib/libGeoIP.dylib /path/to/genet/venv/lib/libGeoIP.dylib
    ln -s /System/Volumes/Data/opt/homebrew/Cellar/gdal/3.5.2/lib/libgdal.dylib /path/to/genet/venv/lib/libgdal.dylib


