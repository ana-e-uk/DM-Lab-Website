from ipyleaflet import Map, basemaps, FullScreenControl, basemap_to_tiles, DrawControl

center = (42.5, -41)
zoom = 2
map = Map(basemap=basemaps.OpenStreetMap.Mapnik, center=center, zoom=zoom, height = 700, scroll_wheel_zoom=True)

chosen_traj_filename = ''

bounding_box = []