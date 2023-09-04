from shapely.geometry import Polygon, Point, LineString, MultiLineString, MultiPolygon
import geopandas as gpd
from geopandas.tools import clip
import numpy as np
from typing import List, Tuple, Union
from geopandas import GeoDataFrame, GeoSeries
from pandas import Series
from scipy.spatial import Voronoi, voronoi_plot_2d
from shapely.ops import cascaded_union, polygonize, unary_union








import matplotlib.pyplot as plt


class UncertaintyPolygon:
    def __init__(self, target_point: Point, target_point_fcode: str, admin_boundary: gpd.GeoDataFrame, gazter: gpd.GeoDataFrame):
        # Transform to EPSG:3857 for consistent calculations
        original_crs = admin_boundary.crs
        self.target_point = gpd.GeoSeries([target_point], crs=original_crs).to_crs(epsg=3857).iloc[0]
        self.target_point_fcode = target_point_fcode
        self.admin_boundary = admin_boundary.to_crs(epsg=3857)
        self.gazter = gazter.to_crs(epsg=3857)
        
    def _calculate_buffer_distance(self, target_point: Point) -> gpd.GeoSeries:
        # Calculate distance from target point to all points in the gazter
        return self.gazter.distance(target_point)

    def _create_cone(self, num_sectors: int = 32) -> gpd.GeoSeries:
        # Calculate the distance to the farthest point in the gazter
        radius: float = self.gazter.distance(self.target_point).max()
        
        # Create cones using the projected target_point in EPSG:3857 based on the number of sectors
        angle_increment: float = 360 / num_sectors
        cones: List[Polygon] = []
        for i in range(num_sectors):
            # Define the starting and ending angles for each cone
            start_angle: float = i * angle_increment
            end_angle: float = (i + 1) * angle_increment
            # Generate a circular sector using explicit point generation
            angles = np.linspace(start_angle, end_angle, num=100)
            arc_points = [Point(self.target_point.x + radius * np.cos(np.radians(angle)),
                                self.target_point.y + radius * np.sin(np.radians(angle))) for angle in angles]
            # Create a polygon from the arc points and lines to the target point
            polygon_coords = [p.coords[0] for p in arc_points] + [self.target_point.coords[0], arc_points[0].coords[0]]
            polygon = Polygon(polygon_coords)
            
            cones.append(polygon)
            
        self.cones = gpd.GeoSeries(cones)
        return self.cones


    def _find_neighboring_points(self) -> gpd.GeoSeries:
        # Identify the nearest point to the target_point and exclude it

        # Extract the values from the gazter that have the same feature code as the target point (e.g. "PPL")
        gazter_same_fcode = self.gazter[self.gazter.feature_code == self.target_point_fcode]
        # If the target fcode is not equal to PPL then extract the values from PPL plus the values from the gazter that have the same feature code as the target point (e.g. "PPL")
        if self.target_point_fcode != "PPL":
            gazter_same_fcode = self.gazter[self.gazter.feature_code == "PPL"].append(gazter_same_fcode)
         
        nearest_point_idx = gazter_same_fcode.distance(self.target_point).idxmin()
        #nearest_point = self.gazter.loc[nearest_point_idx].geometry
        filtered_gazter = gazter_same_fcode.drop(index=nearest_point_idx)

        neighboring_points: List[Point] = []
        for i, cone in enumerate(self.cones):
            points_in_cone = filtered_gazter[filtered_gazter.geometry.intersects(cone)]
            if not points_in_cone.empty:
                #closest_point = points_in_cone.distance(self.target_point).idxmin()
                closest_point = points_in_cone.distance(self.target_point).nsmallest(2).index
                #neighboring_points.append(points_in_cone.loc[closest_point].geometry)
                neighboring_points.extend(points_in_cone.loc[closest_point].geometry.tolist())

            else:
                # Create a point for the empty sector in the centroid of the cone
                neighboring_points.append(cone.centroid)

        # Moved to _create_voronoi_diagram
        # Add the target_point back to the neighboring_points
        #neighboring_points.append(nearest_point)

        self.neighboring_points = gpd.GeoSeries(neighboring_points)
        return self.neighboring_points


    def _create_voronoi_diagram(self) -> Union[Polygon, None]:
        neighboring_points_with_target =  list(self.neighboring_points) + [self.target_point]
        neighboring_points_with_target = gpd.GeoSeries(neighboring_points_with_target, crs=self.neighboring_points.crs)
        coords = np.array([point.coords[0] for point in neighboring_points_with_target])
        
        # Check for collinearity
        if np.linalg.matrix_rank(coords - coords.mean(axis=0)) < 2:
            print("Collinear points detected. Cannot create Voronoi diagram.")
            return None

        # Create Voronoi diagram
        vor = Voronoi(coords)
        
        # Find the region index corresponding to the target point
        region_index = vor.point_region[-1]
        
        # Get the vertices for the region
        region = vor.regions[region_index]
        
        if -1 in region:
            # -1 indicates point at infinity, polygon is unbounded
            print("Target point's Voronoi polygon is unbounded.")
            
            # Create lines from Voronoi vertices and ridge vertices
            lines = [
                LineString(vor.vertices[line])
                for line in vor.ridge_vertices
                if -1 not in line
            ]

            # Create a single polygon from the union of these lines
            polygon = unary_union([p for p in polygonize(lines)])

            #polygon = polygon.intersection(unary_union(self.admin_boundary.geometry))

            # Clip the Voronoi polygon to the admin boundary
            #clipped_polygon = clip(gpd.GeoSeries(polygon, crs='epsg:3857'), self.admin_boundary).iloc[0]

            #if clipped_polygon is not None:
            #    polygon = clipped_polygon
            #else:
            #    print("No intersection between Voronoi polygon and admin boundary")
        else:
            # Create polygon from region
            polygon = Polygon([vor.vertices[i] for i in region])

        
        # Intersect with the admin boundary to handle unbounded regions
        boundary_union = unary_union(self.admin_boundary.geometry)
        intersected_polygon = polygon.intersection(boundary_union)

        if intersected_polygon.is_empty:
            print("No intersection between Voronoi polygon and admin boundary")
            self.target_voronoi_polygon = None
            return None
        
        # Check if the intersection restuls is a MultiPolygon
        if isinstance(intersected_polygon, MultiPolygon):
            # Select the polygon that contains the target point
            containing_polygons = [p for p in intersected_polygon.geoms if p.contains(self.target_point)]
            if containing_polygons:
                intersected_polygon = containing_polygons[0]
            else:
                print("No polygon contains the target point in the MultiPolygon.")
                self.target_voronoi_polygon = None
                return None

        polygon = intersected_polygon


        

        # Create a GeoSeries for the polygon with the appropriate CRS
        polygon_geoseries = gpd.GeoSeries([polygon], crs='epsg:3857')

        # Transform the GeoSeries to EPSG:4326
        self.target_voronoi_polygon = polygon_geoseries.to_crs(epsg=4326).iloc[0]

        return self.target_voronoi_polygon



def plot_cones(uncertainty_obj: UncertaintyPolygon):
    fig, ax = plt.subplots(figsize=(10, 10))
    uncertainty_obj.admin_boundary.plot(ax=ax, color='lightblue', edgecolor='black', alpha=0.3)
    uncertainty_obj.gazter.plot(ax=ax, color='green', markersize=5, label='gazter Points')
    uncertainty_obj.cones.boundary.plot(ax=ax, color='purple', label="Cones")
    ax.scatter(uncertainty_obj.target_point.x, uncertainty_obj.target_point.y, color='red', s=100, label='Target Point')
    ax.legend()
    plt.title("Cones Created Around Target Point")
    plt.show()

def plot_neighboring_points(uncertainty_obj: UncertaintyPolygon):
    fig, ax = plt.subplots(figsize=(10, 10))
    uncertainty_obj.admin_boundary.plot(ax=ax, color='lightblue', edgecolor='black', alpha=0.3)
    uncertainty_obj.gazter.plot(ax=ax, color='green', markersize=5, label='gazter Points')
    uncertainty_obj.cones.boundary.plot(ax=ax, color='purple', label="Cones")
    uncertainty_obj.neighboring_points.plot(ax=ax, color='orange', markersize=50, label="Neighboring Points")
    ax.scatter(uncertainty_obj.target_point.x, uncertainty_obj.target_point.y, color='red', s=100, label='Target Point')
    ax.legend()
    plt.title("Neighboring Points Identified for Each Cone")
    plt.show()


def plot_voronoi_zoomed_with_neighbors_transformed(uncertainty_obj: UncertaintyPolygon):
    # Transforming the target Voronoi polygon to EPSG:3857 to match the other geometries
    target_voronoi_polygon_geoseries = gpd.GeoSeries([uncertainty_obj.target_voronoi_polygon], crs="EPSG:4326")
    target_voronoi_polygon_transformed = target_voronoi_polygon_geoseries.to_crs(epsg=3857)

    # Plotting the zoomed-in Voronoi diagram
    fig, ax = plt.subplots(figsize=(10, 10))
    uncertainty_obj.admin_boundary.plot(ax=ax, color='lightblue', edgecolor='black', alpha=0.3)
    uncertainty_obj.gazter.plot(ax=ax, color='green', markersize=5, label='gazter Points')
    uncertainty_obj.cones.boundary.plot(ax=ax, color='purple', label="Cones")
    target_voronoi_polygon_transformed.plot(ax=ax, color='yellow', alpha=0.5, label="Voronoi Polygon")
    uncertainty_obj.neighboring_points.plot(ax=ax, color='blue', markersize=50, label="Neighboring Points")
    ax.scatter(uncertainty_obj.target_point.x, uncertainty_obj.target_point.y, color='red', s=100, label='Target Point')
    ax.legend()

    # Define zoom-in limits based on the bounding box of the target Voronoi polygon
    minx, miny, maxx, maxy = target_voronoi_polygon_transformed.total_bounds
    padding = 0.05 * max((maxx - minx), (maxy - miny))  # Padding to adjust the zoom level, relative to the size of the polygon
    ax.set_xlim(minx - padding, maxx + padding)
    ax.set_ylim(miny - padding, maxy + padding)

    plt.title("Zoomed-in Voronoi Diagram with Neighboring Points")
    plt.show()




def plot_voronoi_zoomed_with_neighbors_transformed_old(uncertainty_obj: UncertaintyPolygon):
    # Transforming the target Voronoi polygon to EPSG:3857 to match the other geometries
    target_voronoi_polygon_geoseries = gpd.GeoSeries([uncertainty_obj.target_voronoi_polygon], crs="EPSG:4326")
    target_voronoi_polygon_transformed = target_voronoi_polygon_geoseries.to_crs(epsg=3857)

    # Plotting the zoomed-in Voronoi diagram
    fig, ax = plt.subplots(figsize=(10, 10))
    uncertainty_obj.admin_boundary.plot(ax=ax, color='lightblue', edgecolor='black', alpha=0.3)
    uncertainty_obj.gazter.plot(ax=ax, color='green', markersize=5, label='gazter Points')
    uncertainty_obj.cones.boundary.plot(ax=ax, color='purple', label="Cones")
    target_voronoi_polygon_transformed.plot(ax=ax, color='yellow', alpha=0.5, label="Voronoi Polygon")
    uncertainty_obj.neighboring_points.plot(ax=ax, color='blue', markersize=50, label="Neighboring Points")
    ax.scatter(uncertainty_obj.target_point.x, uncertainty_obj.target_point.y, color='red', s=100, label='Target Point')
    ax.legend()

    # Define zoom-in limits
    minx, miny, maxx, maxy = uncertainty_obj.neighboring_points.total_bounds
    padding = 0.05  # Padding to adjust the zoom level
    ax.set_xlim(minx - padding, maxx + padding)
    ax.set_ylim(miny - padding, maxy + padding)

    plt.title("Zoomed-in Voronoi Diagram with Neighboring Points")
    plt.show()



def plot_voronoi_zoomed_with_neighbors(uncertainty_obj: UncertaintyPolygon):
    fig, ax = plt.subplots(figsize=(10, 10))
    uncertainty_obj.admin_boundary.plot(ax=ax, color='lightblue', edgecolor='black', alpha=0.3)
    uncertainty_obj.gazter.plot(ax=ax, color='green', markersize=5, label='gazter Points')
    uncertainty_obj.cones.boundary.plot(ax=ax, color='purple', label="Cones")
    gpd.GeoSeries(uncertainty_obj.target_voronoi_polygon).intersection(unary_union(uncertainty_obj.admin_boundary.geometry)).plot(ax=ax, color='yellow', alpha=0.5, label="Voronoi Polygon")
    uncertainty_obj.neighboring_points.plot(ax=ax, color='blue', markersize=50, label="Neighboring Points")
    ax.scatter(uncertainty_obj.target_point.x, uncertainty_obj.target_point.y, color='red', s=100, label='Target Point')
    ax.legend()
    
    # Define zoom-in limits based on the bounding box of all neighboring points
    minx, miny, maxx, maxy = uncertainty_obj.neighboring_points.total_bounds
    padding = 0.05  # Padding to adjust the zoom level
    ax.set_xlim(minx - padding, maxx + padding)
    ax.set_ylim(miny - padding, maxy + padding)
    
    plt.title("Zoomed-in Voronoi Diagram with Neighboring Points")
    plt.show()