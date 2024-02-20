# DM-Lab-Website
This repository holds the code that implements the Open Source Metadata/Trajectory/Map Project website.

The website is created using [Panel](https://panel.holoviz.org), an open-source Python library for building applications and dashboards. 

The goal of the website is to provide various functionalities such as trajectory split, map-matching, and metadata generation, from uploaded GPS trajectories.

### Website Functionality
The website can:

1. Take in GPS trajectories
2. Process trajectories and provide:
    
    * Trajectory splits
    * Map-matching
    * Metadata
    * Visualization and downloadable results of the above

### File Structure
The repository has the file structure outlined below. In general:

**For specific module documentation:** Go to `docs/[module name]`

**For specific module code:** Each module has their own folder in the `module-scripts` folder. 
* `main.py` has the code that runs the module's data processing
* `vizualization.py` has the code that is used by Panel to visualize the data

**For Panel code:** Each module's Panel code, as well as the main website page, is in the `panel-scripts` folder.

```
data
|__ input
    |__ data_files
|__ output
    |__ data files

docs
|__ general.ipynb
|__ module_example.ipynb
|__ api_example.ipynb
|__ map_matching
|__ metadata
|__ traj_split

module-scripts
|__ map-matching
    |__ constants.py
    |__ main.py
    |__ vizualization.py
|__ metadata
    |__ constants.py
    |__ main.py
    |__ vizualization.py
|__ traj-split
    |__ constants.py
    |__ main.py
    |__ vizualization.py

panel-scripts
|__ main.py
|__ map_matching_pn.py
|__ metadata_pn.py
|__ traj_split_pn.py
|__ ...

utils
|__ visualization.py
|__ data_processing.py
```
