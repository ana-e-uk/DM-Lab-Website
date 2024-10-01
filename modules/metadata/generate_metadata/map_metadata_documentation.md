# Map Metadata Documentation

## Description of Python Files
Given a CSV file with GPS trajectories containing the following columns: < trajectory_id, timestamp, latitude, longitude >,
you can utilize the following Python scripts to generate corrsponding map metadata:

* `constants.json` holds a dictionary that contains the **input, processed,** and **output** directory paths that our scripts will utilize. 
    * The raw trajectory data is in the **input** directory
    * Any output form the files that is not the final map metadata is in the **processed** directory
    * The final map metadata output is in the **output** directory

* `get_trajectory_metadata` generates the speed (instantaneous speed), compass direction (direction the point is heading), day type (week day or weekend), and time type (day or night) of each point of a GPS trajectory.

* `get_map_matching` gets the nearest edge (road) and node (intersection) of the OSMnx road network of each GPS trajectory point, and saves OSM structural metadata for the edges and nodes of the graph. Currently, there is a 10 meter buffer for an edge, a 40 meter buffer for a node, so for example if there is a point that is more than 10 meters away from the nearest edge, this point does not get an edge.

* `get_trajectory_segment_data` computes some speed statistics (average, maximum, and minimum speed), the compass direction (general cardinal or ordinal direction the trajectory segment is heading), day and time type (whether the trajectory segment timestamps fall on a weekend or weekday, day or night).

* `get_map_metadata` generates the metadata for each edge and node as described below.

## Calculating:

### `get_trajectory_metadata` Values

**Speed**
1. Calculate the time difference in hours between each consecutive point in a trajectory
2. Calculate the distance difference in miles between each consecutive point in a trajectory
3. Calculate the speed at a point by dividing the distance difference by the time difference ($\Delta x / \Delta t$)

**Bearing**
Currenly, the bearing/heading is assumed to be given.


TODO: determine how to calculate the bearing/heading of a point if bearing is not provided.

**Compass Direction**
The compass directions are defined as the cardinal and ordinal directions, which are North, East, South and West, and Northeast, Northwest, Southeast, and Southwest respectively.

The bearings (headings) of a point are the degrees of the angle of the direction the point is going where zero is North. The bearings are divided as follows into the compass directions:
* 'N': (337.5, 22.5),
* 'NE': (22.5, 67.5),
* 'E': (67.5, 112.5),
* 'SE': (112.5, 157.5),
* 'S': (157.5, 202.5),
* 'SW': (202.5, 247.5),
* 'W': (247.5, 292.5),
* 'NW': (292.5, 337.5)
(with left number being greater than or equal to)

So we assign each point a compass direction based on its bearing.

<!-- \begin{table}[]
\begin{tabular}{cc}
Bearing            & Compass Direction \\
{[} 337.5,  22.5 ) & N                 \\
{[} 22.5, 67.5 )   & NE                \\
{[} 67.5, 112.5 )  & E                 \\
{[} 112.5, 157.5)  & SE                \\
{[} 157.5, 202.5 ) & S                 \\
{[} 202.5, 247.5 ) & SW                \\
{[} 247.5, 292.5 ) & W                 \\
{[} 292.5, 337.5 ) & NW               
\end{tabular}
\end{table} -->

**Day**
We use the function `isoweekday()` for `datetime` objects from the package `datetime` to get the day of a timestamp for each point in the dataframe. This function returns a 1 for Monday, 2 for Tuesday, 3 for Wednesday, and so on. 

**Day Type**
We use the fuction `isoweekday()` for `datetime` objects from the package `datetime` to get the day type of a timestamp for each point in the dataframe. If the function returns a value corresponding to a week day (Monday through Friday), we assign a 1 to that point. If the function returns a value corresponding to a weekend (Saturday, Sunday), we assign a 0 to that point.

**Time Type**
We assume that the time type is military standard time, so the hours go from zero to twenty three. We have two time types: day and night, and we define 'day' hours as 4:00 - 18:00 and 'night' hours as 19:00 - 3:00. Each point gets a time type assigned based on the point's timestamp. Day gets coded as 1, while night gets coded as a -1.

**Time Bin**
Using both the day types and the time types, we split each point into a time bin:
* Weekend, Night (0 + -1) = -1
* Weekend, Day (0 + 1) = 1
* Week day, Night (1, -1) = 0
* Week day, Day (1 + 1) = 2

## `get_map_matching.py` Values
1. Get OSM graph G using osmnx package `graph_from_bbox` function. We use the minimum bounding box north, south, east, and west values as input, and get the 'drive' network only.
2. Assign edges and nodes to every point in the trajectory using the `osmnx.distance.nearest_edges` and `osmnx.distance.nearest_nodes` functions that "uses an R-tree spatial index and minimizes the euclidean distance from each point to the possible matches" for edges and " k-d tree for euclidean nearest neighbor search, which requires that scipy is installed as an optional dependency. If it is unprojected, this uses a ball tree for haversine nearest neighbor search, which requires that scikit-learn" for nodes. These functions return the distance from the roads
    * If the distance from a point to an edge is greater than 10 meters, we do not match the edge to that point.
    * If the distance from a point to a node is greater than 40 meters, we do not match the node to that point. This number was chosen because the advised slowing down time before an intersection where you need to stop is 150 feet which is about 45 meters.
3. We save additional OSM data for the nodes and edges of OSM graph G that were assigned to a point.
    * For edges, we save: Edge index ,OSM_oneway,OSM_lanes,OSM_name,OSM_highway,OSM_maxspeed,OSM_length
    * For nodes, we save: Node index ,OSM_street_count,OSM_highway
4. For each edge, use the location of its nodes to get a vector for it. This vector will be used to get a dot product of the edge and its trajectory segments.
5. For each node find the edges that correspond to it.

## For Trajectory SEGMENT data (`get_trajectory_segment_data`)
**Average Speed**
We take the mean of all the instantaneous speeds, and round it to the nearest whole number.

**Max and Min Speed**
We take the maximum (or minimum) speed observed and round it to the nearest whole number if need be.

**Compass Direction**
We care about the general direction the trajectory is heading on the road to help us figure out if a road is a one-way or two-way road. If all roads were straight, taking the most common heading (compass direction) value of a trajectory segment would give us the correct value even if there were some erroneous points. However, we cannot assume all roads are straight, so instead if a trajectory segment has more than one point:
* For an edge: we get the first and last point of a trajectory segment, get a vector for the trajectory segment, compute the dot product of the edge's vector computed in the map matching script and trajectory segment, and save if we got a positive, negative, or perpendicular value. If we get both positive and negative values, we assume the road is a two-way.
* For a node: we save the edge that corresponds to the last point of that trajectory segment. This should be the edge that the trajectory moved to and serve as a proxy for the road that is being turned on.

**Day Type, Time Type**
Take the most common value to eliminate erroneous points.

**Travel Time**
We want to calculate how long a trip took to travel across an edge or node, which means we need to calculate:
<!-- $\frac{t_k - t_1}{x_k - x_1}$, where $t_k$ is the last timestamp of that trip for that point ($t_1$ is the first), and $x_k, x_1$ are the corresponding locations of the first and last points. -->
$t_k - t_1$, where $t_k$ is the last timestamp of that trip for that edge or node and $t_1$ is the first. We also have a choice to compute $\frac{t_k - t_1}{x_k - x_1}$ instead, but we currently do not choose this.

## For Map Metadata (`get_map_metadata`)

### Functional Metadata: Edge and Node
If the edge has less than 7 trajectory segments corresponding to it, we just compute the functional metadata once together and save it as time_bin 3.

If we have more than 7 trajectory segments, for each time bin: [-1, 1, 0, 2], we calculate:

**Average Speed with CI**
If there are no values, return NaN, one value returs that value, and multiple values returns the mean. The CI is based on a t-distribution.

**Minimum, Maximum Speed**
If there are no values, return NaN, one value returs that value, and multiple values returns the min or max observed speed

**Travel Time with CI**
Same as average speed.

**Flow**
* For edges: Return the counts of positive, negative, or perpendicular. If there were only nan values, return empty dictionary.
* For nodes: Return the counts of the edges, where a count for an edge means the last timepoint of that trajectory segment was associated with that edge. If there were only nan values, return an empty dictionary.

**Boxplot**
If there are less than 4 trajectory segments, we just return the points instead of summary statistics that help us achieve a box-plot later on. If there are more than 5, we save the values that will help us plot a boxplot later on. We decided to plot a boxplot because the confidence intervals we compute assume the data is normally distributed, while the box plot just plots quartiles and can tell us if the data is skewed. This will give us a more accurate view of the data.

**Trajectory Count**
We save the number of trajectories at each time bin. This should be equal to the sum of the counts of the flow values unless flow is an empty dictionary.

### Structural Metadata: Edge
**OSM values**
We save the following OSM values:
* Oneway
* Lanes
* Name
* Highway
* Maxspeed
* Length

**Oneway**
If there are trajectories with positive and negative "compass directions", we can assume the street is a two-way street and the value for the edge is False. If we see only one type of value, either '-' or '+', we return True. We return None if we have no values.

**Trajectory Count** 
Total number of trajectories for that edge.

**OLD WAY, NOT USED: Oneway**
If there is more than one trajectory, we check every pair of compass directions of the trajectories, and return zero (the edge is a two-way street) if a pair of the compass directions from the trajectories are in opposite directions (the cardinal or ordinal directions are 180 degrees away, such as North-South, East-West, NE-SW etc.). We return 0.5 if there is no pairs of opposite-directions and there is a pair of directions that are in generally the opposite direction. For North, the generally opposite directions would be SW and SE. 

<!-- **Compass Directions**
From OSM, you can get the start and end point of an edge, as well as its geometry. An edge is either straight or curved. If it is straight, you can get the possible driving directions of an edge from the end points, if it bends or curves, you cannot, and have to analyze the geometry. Trajectories travel through  -->

### Structural Metadata: Node
**OSM values**
We save the following OSM values:
* Street count
* Highway
* Edges - this one is computed, the edges associated with that node on OSM

**Street Count**
We use the number of unique streets that occur in the flow dictionary as a proxy for the number of streets there are.

**Trajectory Count** 
Total number of trajectories for that node.