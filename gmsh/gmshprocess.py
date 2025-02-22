import gmsh
import re

gmsh.initialize()
gmsh.open("model.step")

def add_boundary(bbox, name, volumes):
    xmin, ymin, zmin, xmax, ymax, zmax = bbox

    x_width = xmax - xmin
    radius = max(ymax - ymin + 5, zmax - zmin + 5) / 2.0
    y_center = (ymin + ymax) / 2.0
    z_center = (zmin + zmax) / 2.0
    
    disk_tag = gmsh.model.occ.addCylinder(xmin, y_center, z_center, x_width, 0, 0, radius)
    disk_name = f"{name}_bound"
    gmsh.model.occ.synchronize()
    gmsh.model.setEntityName(3, disk_tag, disk_name)
    volumes.append((3, disk_tag, disk_name))

__volumes = gmsh.model.getEntities(3)
names = []

for vol in __volumes:
    name = gmsh.model.getEntityName(vol[0], vol[1])
    print(f"Name :{name}")
    names.append(name)

sanitized_names = []
null_counter = 0
for name in names:
    match = re.match(r".*/([^/\s]+)(?:\s[^/]+)?(?:/[^/]+)?$", name)
    sanitized = match.group(1) if match else name if name is not "" else f"null_{++null_counter}"
    sanitized_names.append(sanitized)

volumes = []
for i, rest in enumerate(__volumes):
    volumes.append((rest[0], rest[1], sanitized_names[i]))

fan_volume = [volume for volume in volumes if "fan" in volume[2]]
for (vol_dim, vol_tag, name) in fan_volume:
        bbox = gmsh.model.getBoundingBox(vol_dim, vol_tag)
        add_boundary(bbox, name, volumes)

gmsh.model.occ.synchronize()

gmsh.option.setNumber("Mesh.MeshSizeMin", 2)
gmsh.option.setNumber("Mesh.MeshSizeMax", 8)

gmsh.model.mesh.generate(2)
for each_vol in volumes:
    surfaces = gmsh.model.getBoundary([(each_vol[0], each_vol[1])])
    surf_tags = [s[1] for s in surfaces]

    pg = gmsh.model.addPhysicalGroup(2, surf_tags)
    print(f"{each_vol[2]}")
    gmsh.write(f"{each_vol[2]}.stl")
    gmsh.model.removePhysicalGroups([(2, pg)])

bbox = gmsh.model.getBoundingBox(-1, -1)
print(f"""
    xmin = {bbox[0]}   xmax = {bbox[3]}
    ymin = {bbox[1]}   ymax = {bbox[4]}
    zmin = {bbox[2]}   zmax = {bbox[5]}
""")

gmsh.finalize()