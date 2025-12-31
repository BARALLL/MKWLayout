# 3D track model viewer

You have several options for visualizing the 3D model of the track, depending on the tools you prefer and the file format of the model.

- For **.szs** or **.brres** files, the easiest method is usually the [noclip](https://noclip.website) website. You can simply drag and drop the file and freely move around the scene.
- For **.fbx** or **.dae** files, it’s often more convenient to use [3dviewer.net](https://3dviewer.net/), which is better suited to these common 3D formats.


To visualize a [KCL](https://wiki.tockdom.com/wiki/KCL_(File_Format)) (collision) file, you have a couple of good options:

- **Lorenzi’s KMP Editor** ([wiki](https://wiki.tockdom.com/wiki/Lorenzi%27s_KMP_Editor) · [website](https://hlorenzi.com/))  
  Includes a built‑in, color‑coded KCL viewer. It's a quick way to get a general visual overview of the collision layout, if you know the color code (quite intuitive).

- **Blender-MKW-Utilities** Blender add‑on by **Gabriela** ([wiki](https://wiki.tockdom.com/wiki/Blender_MKW_Utilities) · [profile](https://wiki.tockdom.com/wiki/Gabriela))  
  Lets you import the KCL directly into Blender and inspect (and edit) the exact collision flag assigned to each triangle, giving you much more detailed control than a simple overview.

- **Wiimms SZS Tools (wkclt)** ([wiki](https://szs.wiimm.de/) · [profile](https://wiki.tockdom.com/wiki/User:Wiimm))  
  A CLI tool that can decode KCL and convert it to formats like OBJ, often grouping by flags. You can then open the OBJ in any 3D viewer or 3D modeling program for custom visualization or further processing.