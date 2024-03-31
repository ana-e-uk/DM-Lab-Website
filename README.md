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
* `[module name]_pn.py` has the code that creates the Panel dashboard/web-page for the specific module
* `vizualization.py` has the code that is used by Panel to visualize the data
* `constants.py` has the constants used in the `main.py` and `visualization.py` scripts

**For Panel code:** Each module's Panel webpage/dashboard code is in that module's `module-scripts` file. The main webpage/dashboard code is in the `panel-scripts` folder.

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
    |__ constants.py
    |__ main.py
    |__ map_matching_pn.py
    |__ vizualization.py
|__ metadata
    |__ constants.py
    |__ main.py
    |__ metadata_pn.py
    |__ vizualization.py
|__ traj-split
    |__ constants.py
    |__ main.py
    |__ traj_split_pn.py
    |__ vizualization.py

panel-scripts
|__ utils
    |__ constants.py
    |__ data_processing.py
    |__ visualization.py
|__ main.py
|__ upload_data.py

requirements.txt (to be added)
```

### How to run the code
First, you need to create an environment and then install panel
```
conda create -n panel python=3.8
conda install panel
```

To run the code, use the following command
```
panel server [filename.py]
```
