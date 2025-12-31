import bpy
import bmesh
import pathlib
from bpy.props import StringProperty
import mathutils
from contextlib import contextmanager
import traceback

DEBUG = False


class MissingResourceError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


def console_print(*args, **kwargs):
    context = bpy.context
    for a in context.screen.areas:
        if a.type == "CONSOLE":
            c = {}
            c["area"] = a
            c["space_data"] = a.spaces.active
            c["region"] = a.regions[-1]
            c["window"] = context.window
            c["screen"] = context.screen
            with context.temp_override(**c):
                s = " ".join([str(arg) for arg in args])
                for line in s.split("\n"):
                    bpy.ops.console.scrollback_append(text=line)


def apply_transformations():
    bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
    bpy.ops.object.transform_apply()


def select_mesh_objects(selected_objs):
    mesh_objects = [obj for obj in selected_objs if obj.type == "MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for obj in mesh_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = (
        bpy.context.selected_objects[0] if bpy.context.selected_objects else None
    )
    bpy.context.view_layer.update()
    return mesh_objects


def join_mesh_objects():
    if not bpy.context.selected_objects:
        return None
    bpy.ops.object.join()
    return bpy.context.selected_objects[0]


def clear_materials(joined_object):
    joined_object.data.materials.clear()


def setup_material(joined_object, material_name):
    mat = bpy.data.materials.get(material_name)
    if not mat:
        raise MissingResourceError(f"Material '{material_name}' not found.")
    joined_object.data.materials.append(mat)
    return mat


def ensure_uv_layer():
    if not bpy.context.object.data.uv_layers:
        bpy.ops.mesh.uv_texture_add()


def set_view_to_top():
    area = next(
        (area for area in bpy.context.screen.areas if area.type == "VIEW_3D"), None
    )
    if area:
        region = next(
            (region for region in area.regions if region.type == "WINDOW"), None
        )
        if region:
            with bpy.context.temp_override(area=area, region=region):
                bpy.ops.view3d.view_axis(type="TOP")
                bpy.ops.view3d.view_selected()


def scale_uv_to_max_no_overflow():
    obj = bpy.context.active_object
    if not obj or obj.type != "MESH":
        print("No active mesh object found.")
        return

    bm = bmesh.from_edit_mesh(obj.data)
    uv_layer = bm.loops.layers.uv.active

    if not uv_layer:
        print("No active UV layer found.")
        return

    # find uv bounds
    min_u, min_v = 1.0, 1.0
    max_u, max_v = 0.0, 0.0
    for face in bm.faces:
        for loop in face.loops:
            uv = loop[uv_layer].uv
            min_u = min(min_u, uv.x)
            min_v = min(min_v, uv.y)
            max_u = max(max_u, uv.x)
            max_v = max(max_v, uv.y)

    uv_width = max_u - min_u
    uv_height = max_v - min_v
    scale_x = 1.0 / uv_width if uv_width > 0 else 1.0
    scale_y = 1.0 / uv_height if uv_height > 0 else 1.0

    scale = min(scale_x, scale_y)

    # Scale and translate UVs
    for face in bm.faces:
        for loop in face.loops:
            # scale
            uv = loop[uv_layer].uv
            uv.x = (uv.x - min_u) * scale
            uv.y = (uv.y - min_v) * scale

            # center the uv
            uv.x -= (scale * uv_width - 1.0) / 2.0
            uv.y -= (scale * uv_height - 1.0) / 2.0

    bmesh.update_edit_mesh(obj.data)


def project_uv_from_view():
    if bpy.context.active_object and bpy.context.active_object.type == "MESH":
        for area in bpy.context.screen.areas:
            if area.type == "VIEW_3D":
                override = bpy.context.copy()
                override["area"] = area  # Set the 3D Viewport as the context area
                override["region"] = area.regions[-1]  # Set the region to the view
                override["space_data"] = area.spaces.active  # Set the space data
                break
        else:
            raise MissingResourceError("No 3D Viewport found.")

        # Create a UV map if it doesn't exist
        if not bpy.context.active_object.data.uv_layers:
            bpy.ops.mesh.uv_texture_add()

        override["mode"] = "EDIT"
        with bpy.context.temp_override(**override):
            bpy.ops.mesh.select_all(action="SELECT")
            bpy.ops.uv.project_from_view(
                camera_bounds=False, correct_aspect=True, scale_to_bounds=False
            )
            scale_uv_to_max_no_overflow()
    else:
        raise MissingResourceError("No mesh object is selected or active.")


def bake_material_map(joined_object, image_name, image_size=512):
    img = bpy.data.images.new(image_name, image_size, image_size)
    mat = joined_object.material_slots[0].material
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    img_node = nodes.get("Image Texture")

    if img_node:
        img_node.select = True
        nodes.active = img_node
        img_node.image = img

        bpy.context.view_layer.objects.active = joined_object
        bpy.context.scene.render.engine = "CYCLES"
        bpy.context.scene.render.bake.use_pass_direct = False
        bpy.context.scene.render.bake.use_pass_indirect = False
        bpy.context.scene.render.bake.use_pass_color = True

        bpy.ops.object.bake(
            type="DIFFUSE",
            width=image_size,
            height=image_size,
            target="IMAGE_TEXTURES",
            margin=0,
            margin_type="ADJACENT_FACES",
            use_clear=True,
        )
    else:
        raise MissingResourceError("Image Texture node not found.")

    return img


def save_image(img, img_path, image_name):
    if not img_path.exists():
        img_path.mkdir(parents=True)
    img.save_render(filepath=str(img_path / image_name))


@contextmanager
def encapsulate_context(pre_func=None, post_func=None, *args, **kwargs):
    pre_func_result = None
    if pre_func:
        pre_func_result = pre_func(*args, **kwargs)  # Store result
    try:
        yield pre_func_result
    finally:
        if post_func:
            post_func(pre_func_result, *args, **kwargs)  # Pass result to post_func


def store_viewport_settings(*args, **kwargs):
    viewport_settings = dict()
    viewport_settings["area"] = next(
        (area for area in bpy.context.screen.areas if area.type == "VIEW_3D"), None
    )
    viewport_settings["space"] = next(
        (
            space
            for space in viewport_settings["area"].spaces
            if space.type == "VIEW_3D"
        ),
        None,
    )
    viewport_settings["camera_location"] = viewport_settings[
        "space"
    ].region_3d.view_location.copy()
    viewport_settings["camera_rotation"] = viewport_settings[
        "space"
    ].region_3d.view_rotation.copy()
    viewport_settings["camera_perspective"] = viewport_settings[
        "space"
    ].region_3d.view_perspective
    return viewport_settings


def restore_viewport_settings(viewport_settings, *args, **kwargs):
    viewport_settings["space"].region_3d.view_location = viewport_settings[
        "camera_location"
    ]
    viewport_settings["space"].region_3d.view_rotation = viewport_settings[
        "camera_rotation"
    ]
    viewport_settings["space"].region_3d.view_perspective = viewport_settings[
        "camera_perspective"
    ]


def store_selected(*args, **kwargs):
    # store selected objects
    active_object = bpy.context.active_object
    original_selected_objs = [
        obj for obj in bpy.context.selected_objects if obj.type == "MESH"
    ]
    obj_visibility = {obj.name: obj.hide_viewport for obj in bpy.data.objects}

    mesh_obj = select_mesh_objects(bpy.context.selected_objects)

    bpy.ops.object.duplicate_move()
    new_objects = bpy.context.selected_objects
    obj_names = set(obj.name for obj in new_objects)

    for obj in bpy.data.objects:
        if obj.name not in obj_names:
            obj.hide_viewport = True
            obj.select_set(False)

    bpy.ops.object.select_all(action="DESELECT")
    mesh_obj = select_mesh_objects(new_objects)

    return {
        "copied_objects": mesh_obj,
        "original_selected_objs": original_selected_objs,
        "active_object": active_object,
        "obj_visibility": obj_visibility,
    }


def restore_selected(pre_res, *args, **kwargs):
    # remove copied objects
    bpy.ops.object.select_all(action="DESELECT")
    for obj in pre_res["copied_objects"]:
        obj.select_set(True)
        bpy.ops.object.delete()

    # restore original objects
    bpy.ops.object.select_all(action="DESELECT")
    for obj in pre_res["original_selected_objs"]:
        obj.hide_viewport = False
        obj.select_set(True)

    # restore object visibility
    for obj in bpy.data.objects:
        obj.hide_viewport = pre_res["obj_visibility"].get(obj.name, obj.hide_viewport)

    # restore active object
    bpy.context.view_layer.objects.active = pre_res["active_object"]


def delete_new_objects(obj_before):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in bpy.data.objects:
        if obj.name not in obj_before:
            obj.select_set(True)
    bpy.ops.object.delete()


def generate_material_map(file_name):
    """Generates a material map for the selected object."""
    selected_objs = bpy.context.selected_objects

    if not selected_objs or bpy.context.active_object is None:
        raise Exception("No mesh objects selected.")

    bpy.ops.object.mode_set(mode="OBJECT")

    apply_transformations()

    if not selected_objs:
        return {"CANCELLED"}

    joined_object = join_mesh_objects()
    if not joined_object:
        return {"CANCELLED"}

    apply_transformations()

    # Get the material name from the settings
    material_name = bpy.context.scene.settings.material_name
    mat = setup_material(joined_object, material_name)
    if not mat:
        return {"CANCELLED"}

    ensure_uv_layer()
    set_view_to_top()
    bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP", iterations=1)

    bpy.context.view_layer.objects.active = joined_object
    if bpy.context.active_object.mode != "EDIT":
        bpy.ops.object.mode_set(mode="EDIT")

    project_uv_from_view()
    bpy.ops.object.editmode_toggle()

    # Use the material name in the image name
    image_name = f"{file_name}_{material_name}_map.png"

    img = bake_material_map(joined_object, image_name)
    if not img:
        return {"CANCELLED"}

    img_path = (
        pathlib.Path(bpy.context.scene.settings.material_maps_path).absolute()
        if bpy.context.scene.settings.material_maps_path != ""
        else pathlib.Path(bpy.context.scene.settings.directory_path).absolute()
        / "material_maps"
    )
    save_image(img, img_path, image_name)
    bpy.data.images.remove(img)

    return {"FINISHED"}


class Settings(bpy.types.PropertyGroup):
    dae_path: StringProperty(subtype="DIR_PATH")
    material_maps_path: StringProperty(subtype="DIR_PATH")
    processed_dae_path: StringProperty(subtype="DIR_PATH")
    material_name: StringProperty(
        name="Material Name",
        description="Name of the material to be used for generating the map",
        default="addon_mat"
    )


class MaterialMapGeneratorOperator(bpy.types.Operator):
    bl_idname = "material_map.generate"
    bl_label = "Generate Material Map"
    bl_description = "Generate Material Map of selected object"

    def execute(self, context):
        file_name = pathlib.Path(bpy.context.blend_data.filepath).stem
        with encapsulate_context(
            pre_func=store_viewport_settings, post_func=restore_viewport_settings
        ):
            with encapsulate_context(
                pre_func=store_selected, post_func=restore_selected
            ):
                try:
                    result = generate_material_map(file_name)
                except Exception as e:
                    self.report({"ERROR"}, str(e))
                    result = {"CANCELLED"}
        if result == {"FINISHED"}:
            img_path = (
                pathlib.Path(bpy.context.scene.settings.material_maps_path).absolute()
                if bpy.context.scene.settings.material_maps_path != ""
                else pathlib.Path(bpy.context.scene.settings.directory_path).absolute()
                / "material_maps"
            )
            self.report(
                {"INFO"},
                f"Material map saved as {file_name}_material_map.png in {img_path}",
            )
        return result


class BatchMaterialMapGeneratorOperator(bpy.types.Operator):
    bl_idname = "material_maps_dae.generate"
    bl_label = "Generate Material Maps (Batch)"
    bl_description = "Generate Material Maps for .dae files in the chosen directory"

    def execute(self, context):
        source_path = pathlib.Path(bpy.context.scene.settings.dae_path).absolute()
        if not source_path.exists() or not source_path.is_dir():
            self.report(
                {"ERROR"}, "Source .dae directory does not exist or is not a directory."
            )
            return {"CANCELLED"}
        processed_path = (
            pathlib.Path(bpy.context.scene.settings.processed_dae_path).absolute()
            if bpy.context.scene.settings.processed_dae_path != ""
            else None
        )

        if not processed_path.exists():
            processed_path.mkdir(parents=True)

        count = 0
        selected_objs = bpy.context.selected_objects
        bpy.ops.object.select_all(action="DESELECT")
        with encapsulate_context(
            pre_func=store_viewport_settings, post_func=restore_viewport_settings
        ):
            with encapsulate_context(
                pre_func=store_selected, post_func=restore_selected
            ):
                bpy.ops.object.select_all(action="DESELECT")
                obj_before = set((obj.name for obj in bpy.data.objects))
                for file in source_path.glob("*.dae"):
                    try:
                        import_result = bpy.ops.wm.collada_import(filepath=str(file))
                        if import_result == {"CANCELLED"}:
                            raise Exception(f"Error importing .dae file {file}")

                        obj_after = set((obj.name for obj in bpy.data.objects))
                        name_new_objs = obj_after - obj_before
                        new_objs = [
                            bpy.data.objects[obj_name] for obj_name in name_new_objs
                        ]
                        select_mesh_objects(new_objs)

                        result = generate_material_map(file.stem)
                        if result == {"CANCELLED"}:
                            self.report({"WARNING"}, f"Failed to process {file}.")
                        else:
                            count += 1
                            if processed_path is not None:
                                file.rename(processed_path / file.name)

                    except MissingResourceError as e:
                        self.report({"ERROR"}, str(e))
                        return {"CANCELLED"}
                    except Exception as e:
                        self.report(
                            {"ERROR"},
                            f"Error processing {file}{": " + str(traceback.format_exc()) if DEBUG else ''}",
                        )
                    finally:
                        delete_new_objects(obj_before)

        self.report({"INFO"}, f"Processed {count} .dae files.")
        for obj in selected_objs:
            obj.select_set(True)
        return {"FINISHED"}


class MaterialMapGeneratorPanel(bpy.types.Panel):
    bl_label = "Material Map Generator"
    bl_idname = "SCENE_PT_material_map_generator"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Material Map Generator"

    def draw(self, context):
        layout = self.layout
        layout.operator(MaterialMapGeneratorOperator.bl_idname)
        layout.operator(BatchMaterialMapGeneratorOperator.bl_idname)
        layout.prop(
            context.scene.settings,
            "dae_path",
            text="Source .dae Folder",
            expand=True,
            placeholder="Please select a folder containing .dae files for batch processing",
        )
        layout.prop(
            context.scene.settings,
            "material_maps_path",
            text="Material Map Save Folder",
            expand=True,
            placeholder="<source_dae_folder>/material_maps",
        )
        layout.prop(
            context.scene.settings,
            "processed_dae_path",
            text="Correctly Processed .dae Output Folder",
            expand=True,
            placeholder="<source_dae_folder>",
        )
        layout.prop(
            context.scene.settings,
            "material_name",
            text="Material Name"
        )