# DM-Lab-Website
This repository holds the code that implements the Open Source Metadata Project website.

The website is currently created using [Panel](https://panel.holoviz.org), an open-source Python library for building applications and dashboards. 

The goal of the website is to provide visualization and sharing of map (road network) metadata, along with visualizations of functionalities such as trajectory splitting, and map-matching of GPS trajectories.

### How to run the code
First, create an environment and then install panel
```
conda create -n panel
conda install panel ipywidgets ipyleaflet shapely geopandas ipykernel
pip install osmnx
```

To run the code, use the following command
```
panel serve main.py
```
and click on the link in the terminal.

`main.py` is the script that generates and updates the dashboard, and calls other scripts depending on the choices made by the user on the dahsboard.

### Website Functionality Goals
1. Upload GPS trajectory files
2. Process trajectories and provide:
    
    * Trajectory segmentation
    * Map-matching
    * Metadata
    * Visualization and downloadable results of the above

#### Assumptions
1. Each file contains one trajectory. Even if you fed in different trajectories in the same file. The script will randomly select one of them and plot it
2. Map matching may take some time, so the user is expected to wait for sometime to see the output
3. The used library of map matching is limited somehow. It only outputs the matched road per point which is discontinuous rather than the whole trajectory of roads which is continous
4. The library has a problem with the map extraction. It disregards roads that are disconneted in the roads extraction part. A modified version may be used here to adjust this.

### File Structure
The repository has the file structure outlined below. In general:

**For specific module documentation:** Go to `docs/[module name]`

**For specific module code:** Each module has their own folder in the `modules` folder. 
* `__init__.py` creates the Panel objects and calls necessary functions for that module's functionality
* `functions.py` has functions used by `__init__.py`
* `vizualization.py` has functions that provide visualization


```
data
|__ examples
    |__ data files
|__ input
    |__ uploads
        |__ data files
    |__ data files
|__ output
    |__ data files

docs
|__ general.ipynb
|__ map_matching.ipynb
|__ metadata.ipynb
|__ module_example.ipynb
|__ traj_split.ipynb

module-scripts
|__ map-matching
    |__ __init__.py
    |__ constants.py
    |__ functions.py
    |__ sample.py
    |__ vizualization.py
|__ metadata
    |__ __init__.py
    |__ constants.json
    |__ functions.py
    |__ vizualization.py
|__ traj-split
    |__ __init__.py
    |__ constants.py
    |__ functions.py
    |__ traj_split_pn.py
    |__ vizualization.py

utils
|__ constants.py
|__ data_processing.py
|__ visualization.py

.gitignore
config.py
constants.py
draft_upload_data.py
main.py
map.html
notebook.ipynb
README.md
userdefined_components.py
visualization.py
```