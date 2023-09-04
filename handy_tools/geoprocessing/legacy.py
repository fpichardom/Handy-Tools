    
#class UncertaintyPolygon(object):
#     def __init__(self, target_point:Point, target_point_fcode:str, adm_boundary:GeoDataFrame, gazzeteer:GeoDataFrame)-> None:
#         self.target_point = target_point
#         self.target_point_fcode = target_point_fcode
#         self.adm_boundary = adm_boundary
#         self.gazzeteer = gazzeteer
#         self.cones = self._create_cone()
#         self.neighboring_points = self._find_neighboring_points()
# def _create_cone(self, num_sectors: int = 16) -> gpd.GeoSeries:
    #     # Calculate the distance to the farthest point in the gazzeteer
    #     self.gazzeteer['distance'] = self.gazzeteer.apply(lambda row: self.target_point.distance(row.geometry), axis=1)
    #     farthest_point: Point = self.gazzeteer.loc[self.gazzeteer['distance'].idxmax()]
    #     radius: float = self.target_point.distance(farthest_point.geometry)
        
    #     # Define the number of sectors and the angle increment
    #     angle_increment: float = 360 / num_sectors

    #     cones: List[Polygon] = []
    #     for i in range(num_sectors):
    #         # Define the starting and ending angles for each cone
    #         start_angle: float = i * angle_increment
    #         end_angle: float = (i + 1) * angle_increment
            
    #         # Create arc by computing points along the circumference
    #         angles: np.ndarray = np.linspace(start_angle, end_angle, num=100)
    #         arc_points: List[Point] = [Point(self.target_point.x + radius * np.cos(np.radians(angle)),
    #                                         self.target_point.y + radius * np.sin(np.radians(angle))) for angle in angles]
            
    #         # Create a polygon from the arc points and lines to the target point
    #         polygon_coords: List[Tuple[float, float]] = [p.coords[0] for p in arc_points] + [self.target_point.coords[0], arc_points[0].coords[0]]
    #         polygon: Polygon = Polygon(polygon_coords)
    #         cones.append(polygon)

    #     return gpd.GeoSeries(cones)

    
    
    # def _find_neighboring_points(self)->GeoSeries:
    #     neighboring_points:List[Point] = []
    #     for cone in self.cones:
    #         # Find points that intersect the cone
    #         points_in_cone = self.gazzeteer[self.gazzeteer.geometry.intersects(cone)]
            
    #         # If there are points in the cone, select the closest one to the target point
    #         if not points_in_cone.empty:
    #             closest_point = points_in_cone.distance(self.target_point).idxmin()
    #             neighboring_points.append(points_in_cone.loc[closest_point].geometry)
    #     self.neighboring_points = gpd.GeoSeries(neighboring_points)
    #     return self.neighboring_points
    




    # def _calculate_buffer_distance(self, target_point:Point)->GeoSeries:
    #     # Calculate distance from target point to all points in the gazzeteer
    #     return self.gazzeteer.distance(target_point)

    # def _create_cone(self, num_sectors:int = 16)->Series:
    #     # Calculate the buffer distance
    #     buffer_distance = self._calculate_buffer_distance(self.target_point).max()

    #     # Create a buffer around the target point
    #     buffer = self.target_point.buffer(buffer_distance)

    #     # Calcualte angle step size
    #     angle_step = 360 / num_sectors

    #     # Generate the cones
    #     cones:List[Polygon] = []
    #     for i in range(num_sectors):
    #         start_angle = i * angle_step
    #         end_angle = (i + 1) * angle_step
    #         if end_angle == 360:
    #             end_angle = 0
    #         cone = buffer.intersection(Polygon(self.target_point.buffer(buffer_distance * 1.1).exterior).difference(Polygon(self.target_point.buffer(buffer_distance * 0.9).exterior)))
    #         cones.append(cone.boundary)
    #     return GeoSeries(geometry=cones)




    # def _create_voronoi_diagram(self):
    #     # Check if neighboring points were calculated
    #     if self.neighboring_points:
    #         # Convert neighboring points to numpy array
    #         coords = np.array([p.coords[0] for p in self.neighboring_points])

    #         # Create Voronoi diagram
    #         vor = Voronoi(coords)

    #         # Get target region
    #         target_region_index = vor.point_region[-1]
    #         target_region = vor.regions[target_region_index]

    #         if -1 in target_region:
    #             # If the target region is unbounded, create bounded polygon
    #             lines = [LineString(vor.vertices[line]) for line in vor.ridge_vertices if -1 not in line and all(i in target_region for i in line)]
    #             bounded_target_voronoi_lines = MultiLineString(lines).intersection(self.target_point.buffer(self.radius))
    #             bounded_target_voronoi_polygon = Polygon(bounded_target_voronoi_lines)
    #             self.target_voronoi_polygon = bounded_target_voronoi_polygon
    #         else:
    #             # If the target region is bounded, create polygon directly
    #             polygon = Polygon([vor.vertices[i] for i in target_region if i != -1])
    #             self.target_voronoi_polygon = polygon

    #         # Return Voronoi object and target Voronoi polygon
    #         return vor, self.target_voronoi_polygon

    #     else:
    #         # If no neighboring points were calculated, set target Voronoi polygon to None
    #         self.target_voronoi_polygon = None
    #         return None, None


# # Bind the method with polygon output and typing to the uncertainty_instance_v2 instance
# uncertainty_instance_v2._create_cone = MethodType(_create_cone_with_polygon_output_typed, uncertainty_instance_v2)

# # Re-run the method with typing and visualize the results
# cones_with_polygon_output_typed = uncertainty_instance_v2._create_cone()

# fig, ax = plt.subplots(figsize=(10, 10))
# adm_boundary_expanded.plot(ax=ax, color='lightblue', edgecolor='black', alpha=0.3)
# gazzeteer.plot(ax=ax, color='green', markersize=5, label='Gazzeteer Points')
# cones_with_polygon_output_typed.boundary.plot(ax=ax, color='purple', label="Cones")
# ax.scatter(target_point.x, target_point.y, color='red', s=100, label='Target Point')
# ax.legend()
# plt.title("Cones with Polygon Output (Typed) Around Target Point")
# plt.show()


    # def _find_neighboring_points(self) -> gpd.GeoSeries:
    #     neighboring_points: List[Point] = []
    #     for cone in self.cones:
    #         # Find points that intersect the cone
    #         points_in_cone = self.gazzeteer[self.gazzeteer.geometry.intersects(cone)]
            
    #         # If there are points in the cone, select the closest one to the target point
    #         if not points_in_cone.empty:
    #             closest_point = points_in_cone.distance(self.target_point).idxmin()
    #             neighboring_points.append(points_in_cone.loc[closest_point].geometry)
                
    #     self.neighboring_points = gpd.GeoSeries(neighboring_points)
    #     return self.neighboring_points






class UncertaintyPolygon(object):
    def __init__(self, target_point:Point, target_point_fcode:str, adm_boundary:GeoDataFrame, gazzeteer:GeoDataFrame):
        self.target_point = target_point
        self.target_point_fcode = target_point_fcode
        self.gazzeteer = gazzeteer
        self.adm_boundary = adm_boundary
        self.uncertainty_polygon = self._create_uncertainty_polygon()

    def _create_cone(self, num_sectors=16):
        self.gazzeteer['distance'] = self.gazzeteer.apply(lambda row: self.target_point.distance(row.geometry), axis=1)
        farthest_point = self.gazzeteer.loc[self.gazzeteer['distance'].idxmax()]
        #radius = farthest_point['distance']
        radius = self.target_point.distance(farthest_point.geometry)
        self.radius = radius
        num_sectors = num_sectors
        angle_increment = 360 / num_sectors

        def create_conical_buffer(target_point, radius, start_angle, end_angle):
            # Create arc by computing points along the circumference
            angles = np.linspace(start_angle, end_angle, num=100)
            arc_points = [Point(target_point.x + radius * np.cos(np.radians(angle)),
                                target_point.y + radius * np.sin(np.radians(angle))) for angle in angles]
            
            # Create a polygon from the arc points and lines to the target point
            polygon_coords = [p.coords[0] for p in arc_points] + [target_point.coords[0], arc_points[0].coords[0]]
            polygon = Polygon(polygon_coords)
            
            return polygon


        # Create cones
        cones = []
        for i in range(num_sectors):
            start_angle = i * angle_increment
            end_angle = (i + 1) * angle_increment
            cone = create_conical_buffer(self.target_point, radius, start_angle, end_angle)
            cones.append(cone)

        # Return some details about the first few cones
        #cones[:3], [cone.is_valid for cone in cones[:3]]



        #cone = create_conical_buffer(self.target_point, radius, farthest_point['angle'] - 30, farthest_point['angle'] + 30)

        self.cones = cones
        return cones
    
    def _find_neighboring_points(self):

        def find_nearest_point(cone: Polygon, points: GeoDataFrame) -> GeoDataFrame:
            
            # if the fcode of the target point is not in the points geodataframe then return None
            if self.target_point_fcode not in points['feature_code'].values:
                return None
            # filter points geodataframe to only include points of the same fcode as the target point
            points = points[points['feature_code'] == self.target_point_fcode]
            # If the fcode is not PPL then the filter should include all points that are PPL and the fcode of the target point
            if self.target_point_fcode != 'PPL':
                points = points[(points['feature_code'] == 'PPL') | (points['feature_code'] == self.target_point_fcode)]

            points_within_cone = points[points.intersects(cone)]
            #print("Points within cone:\n", points_within_cone)  # Debugging print
            if not points_within_cone.empty:
                min_index = points_within_cone['distance'].idxmin()
                #print("Min index:", min_index)  # Debugging print
                return points_within_cone.loc[min_index]
                #return points_within_cone.iloc[points_within_cone.distance(cone).argmin()]
        
        
        neighboring_points = []
        for cone in self.cones: # Make sure to use 'cone' here, not 'con'
            nearest_point = find_nearest_point(cone, self.gazzeteer) # Replace 'all_points' with the correct variable name
            if nearest_point is not None:
                neighboring_points.append(nearest_point.geometry)
        
        # Include the target point
        #print(len(neighboring_points))   
        neighboring_points.append(self.target_point)
        #print(len(neighboring_points))
        self.neighboring_points = neighboring_points
        return neighboring_points
    
    
    def _create_voronoi_diagram(self):
        if self.neighboring_points:
            coords = np.array([p.coords[0] for p in self.neighboring_points])
            
            # Remove duplicate points
            #coords = np.unique(coords, axis=0)

            #Check for colliniarity
            #if np.linalg.matrix_rank(coords - coords.mean(axis=0)) < 2:
            #    print("Collinear points detected. Cannot create Voronoi diagram.")
            #    return None
            
            #if np.any(np.isnan(coords)) or np.any(np.isinf(coords)):
            #    print("NaN or Inf vales detected. Cannot create Voronoi diagram.")
            #    return None
            
            # Create Voronoi diagram
            #try:

            # Check for collinearity
            if np.linalg.matrix_rank(coords - coords.mean(axis=0)) < 2:
                self.target_voronoi_polygon = None
                print("Collinear points detected. Cannot create Voronoi diagram.")
                #return None

            # try:
            #     voronoi = Voronoi(coords)
            # # ... rest of your code ...

            # except QhullError as e:
            #     print("QhullError detected:", e)
            #     print(coords)
            #     self.target_voronoi_polygon = None
            #     return None

            voronoi = Voronoi(coords)
            
            circle_boundary = self.target_point.buffer(self.radius)


            # Find the region index corresponding to the target point
            #target_region_index = len(self.neighboring_points) - 1
            target_region_index = voronoi.point_region[-1]
            target_region = voronoi.regions[target_region_index]

            # If the region is unbounded, intersect it with the circular boundary
            if -1 in target_region:
                #target_region_vertices = [voronoi.vertices[i] for i in target_region if i != -1]
                # Get the ridges for the target Voronoi region, excluding those with -1
                lines = [LineString(voronoi.vertices[line]) for line in voronoi.ridge_vertices if -1 not in line and all(i in target_region for i in line)]

                # Merge the lines and intersect with the circular boundary
                bounded_target_voronoi_lines = MultiLineString(lines).intersection(circle_boundary)

                # Create a polygon from the bounded lines
                bounded_target_voronoi_polygon = Polygon(bounded_target_voronoi_lines)

                self.target_voronoi_polygon = bounded_target_voronoi_polygon
                return bounded_target_voronoi_polygon
            else:
                # Create a polygon directly from the target region if it is already bounded
                polygon = Polygon([voronoi.vertices[i] for i in target_region if i != -1])
                self.target_voronoi_polygon = polygon
                return polygon

            #except QhullError as e:
            #    print("QhullError detected:", e)
            #    print(coords)
            #    #raise e
            #    return None
        else:
            self.target_voronoi_polygon = None
            return None

    #             # Create a MultiPolygon object that includes the vertices of the unbounded region
    #             unbounded_multipolygon = MultiPolygon([Polygon([voronoi.vertices[i] for i in target_region if i != -1]), circle_boundary])
    #             # Intersect the MultiPolygon with the circular boundary to bound the target region
    #             bounded_polygon = unbounded_multipolygon.intersection(circle_boundary)
    #         else:
    #             bounded_polygon = Polygon([voronoi.vertices[i] for i in target_region])

    #     self.target_voronoi_polygon = bounded_polygon
    #     return bounded_polygon
    # else:
    #     self.target_voronoi_polygon = None
    #     return None





    #         #Bound the Voronoi diagram by the circular boundary
    #         line_polygons = [Polygon(voronoi.vertices[line]) for line in voronoi.ridge_vertices if -1 not in line]
    #         bounded_voronoi = MultiPolygon(line_polygons).intersection(circle_boundary)



    #         if target_region and len(target_region) > 4:
    #             target_polygon = Polygon([voronoi.vertices[i] for i in target_region if i != -1])
    #             if -1 in target_region:
    #                 # If -1 is in region, then it is unbounded
    #                 target_polygon = target_polygon.intersection(circle_boundary)

    #         voronoi_polygons = []
    #         for region in voronoi.regions:
    #             if not region: continue
    #             polygon = Polygon(voronoi.vertices[i] for i in region if i != -1)
    #             if -1 in region:
    #                 # If -1 is in region, then it is unbounded
    #                 polygon = polygon.intersection(circle_boundary)
    #             voronoi_polygons.append(polygon)
            
    #         target_voronoi_polygon = voronoi_polygons[-1]
    #         self.target_voronoi_polygon = target_voronoi_polygon
    #         return target_voronoi_polygon
    #     else:
    #         self.target_voronoi_polygon = None
    #         return None
    

    def _clip_voronoi_diagram(self):
        if self.target_voronoi_polygon:
            clipped_polygon = self.target_voronoi_polygon.intersection(self.adm_boundary.geometry)
            self.clipped_polygon = clipped_polygon
            return clipped_polygon
        else:
            self.clipped_polygon = None
            return self.clipped_polygon
    def _create_uncertainty_polygon(self):
        self._create_cone()
        self._find_neighboring_points()
        self._create_voronoi_diagram()
        return self._clip_voronoi_diagram()
