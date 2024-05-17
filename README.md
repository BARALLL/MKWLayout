# MKW Layout Generation


## Dataset
### Disclaimer
This research project is based on the analysis of circuits created by members of our community. These circuits are an expression of their unique creativity and constitute their intellectual property. Consequently, the dataset used in this research cannot be shared or disclosed publicly.

The purpose of this research is purely exploratory and aims to understand the human creative process and understand what constitutes a great track, i.e., what makes a track a good track. Artistic creation must remain the prerogative of human beings and their personal expression.

### Generating the dataset
### Images
The creation of the image part of the dataset involves 3 steps. For the tabular data, see 

#### 1. Track Collection 
Collect mario kart wii tracks in .szs format. For example, you can use this website [Tockdom.com](https://wiki.tockdom.com/wiki/Main_Page). Is is preferable to download tracks that are part of a reputable distribution. This will ensure the quality of the track.

Regroup the .szs files in a single folder.

#### 2. Minimap Extraction
##### Design Choices
<!-- Ces circuits on le plus souvent un décor entourant la route. Comme la route peut etre composé de plusieurs section avec des objets different, nous ne pouvons pas identifier les objets qui le compose directement. De plus comme les objets sont séparé par textures, il se peut qu'une partie de la route utilise une meme texture qu'un élement du decor, ce qui serait penible pour identifier ce qui est décor et ce qui est route. Le plus simple pour extraire la route est donc d'utiliser la minimap. Cette minimap est en effet également un modèle 3D et non une texture 2D et doit être modifier par le createur du circuit. Le seul probleme avec cette méthode est que le createur peut decider d'aplatir le modèle 3D, ne gardant donc aucune information de hauteur, mais cela est une minorité des cas. Dans ce cas, nous vous conseillons de revenir dans l'outil Brawlcrate et d'extraire les parties de circuits constuituant la route sous format `obj`. Dans un logiciel 3D tel que Blender, retirer toutes les textures et materiaux puis combinez les differentes sections du circuit et exporter l'unique objet resultant sous format `.dae`. (l'outil suivant dans la pipeline de creation du dataset devrait pouvoir supporter plusieurs objet mais il est preferable de l'avoir en un objet unique). -->

These tracks often feature scenery surrounding the racing lane. We have to make sure that only the racing lane is extracted. Since the racing lane can be composed of multiple sections incorporating distinct 3D objects, it's impossible to directly identify the elements that constitute it. Furthermore, the same texture could be used in both certain portions of the road and elements of the scenery, making it difficult to distinguish between these two entities. The most reliable method for extracting the track is therefore to utilize the minimap. This minimap is not a simple 2D texture but 3D model that is defined by the track creator. A potential drawback of this approach is the possibility that the creator flattens the this minimap, thereby removing any information related to elevation. However, this situation remains a minority. In this specific case, it is recommended to return to the Brawlcrate tool in order to extract the different sections of the track in `.obj` format. Then, in a 3D modeling software such as Blender, it is advisable to remove all textures and materials and merge the different sections of the track. Export the resulting object in `.dae` format. (Although the next step in the dataset creation pipeline could theoretically support multiple objects, it is preferable to provide a single unified object.)


##### Usage
Using the Brawlcrate tool, go to the Tool menu and click on Run Script. Select the script `brawlcrate_minimap_scraping.py`. Follow the instructions given by the script.

#### 3. Material Map Creation
This step was initially designed to create a normalized height map of the race track. It later turned out that this process could be extended to generate any map from the 3D object, such as a normal map that could add value to the model as an additional channel. all you have to do is design a shader that extracts the desired information to a texture.

##### Design Choices
AI models processing 3D information (mesh) are inherently complex. The addition of this supplementary dimension can significantly compromise the model's ability to generalize and comprehend creative processes. Moreover, the crucial lack of data makes this task particularly challenging.

A promising strategy to mitigate these challenges is to reduce the third dimension (height) to a grayscale channel of the image. Although this may result in some loss of information (for example, when one part of the circuit overlaps another), the majority of the information is retained and allows the model's training.

Similarly, we can project the 3D direction (x, y, z) of the circuit onto a three-channel RGB representation, transforming complex spatial information into a more accessible format for machine learning.


<!-- Les modeles d'AI traitant le d'information 3D sont de gros modeles complexes. La dimension supplémentaire combinée a cette complexité peuvent vraiment altérer la capacité du modele a generaliser et a comprendre le processus creatif. De plus, le cruciel manque de donnée rend cette tache d'autant plus dur. Ainsi, une bonne idée pour contrer cela est de réduire la 3ème dimension (la hauteur) a la channel greyscale de l'image. Cela permet un peut d'information (dans le cas ou une partie du circuit overlap une autre) mais retiens l'information dans la majorité des cas, tout en permettant l'entrainement du modele.

De la meme manière que la hauteur, nous pouvons mapper la direction (x,y,z) du circuit en 1 point en une images a 3 channels RGB. -->

##### Usage
Organize your `.dae` files into a single directory (which should already be mostly complete from the previous step). Download the `material_map_generator.zip` Blender Add-on from the Releases section.

Launch Blender and ensure you're running a supported version. Navigate to Edit >> Preferences >> Add-ons, then click the downward-pointing arrow in the top right of the Preferences window. Select "Install from Disk" and choose the downloaded zip file. Activate the add-on by checking the box next to its name if not already enabled.

Press 'N' to display the viewport panel (alternatively, click the left-pointing arrow on the right side of the viewport near the Rotate View gizmo). Locate and select the Material Map Generator panel.

Configure your settings:

- Select the source folder containing your `.dae` files
- Choose a destination folder for generated material maps
- Optionally, designate a folder for processed `.dae` files to simplify potential restart scenarios

Click "Generate Material Maps" to initiate the process.




You can also add images from other sources, as long as they have the same format as the existing images and are relevant to the AI task you are trying to accomplish.

<!-- Regroup the `.dae` files in a single folder (should be pretty much done by the previous step). Download the `material_map_generator.zip` Blender Addon file in `Releases`. Start Blender (make sure you have a supported version). Go into Menu Edit >> Preferences >> Add-ons >> Click the Arrow pointing down in the top right of the Prefereence window >> Click on Install from Disk >> Select the zip file. Activate it clicking on the checkbox aligned with the Add-ons name if not already checked. Tap 'N' to display the viewport panel (or the arrow pointing left on the right side of the viewport near the Rotate View gizmo). Select Material Map Generator. Select the source folder and the destination folder. You can also select the folder to which the `.dae` that are processed are moved so that is anything happen it is easier to restart without re processing everything. Generate all Material Maps using the button of the same name.   

You should be able to add images from other sources, provided they have the same format as the other images and are relevant to the task you're trying to achieve with the AI. -->

#### Tabular data
This is were it gets very long. The data the author created involves watching the Best Known Times (BKT) videos for each track, and take note of around 45 varied features decomposed into 3 feature sets. 
- The 1st feature set is composed of 33 features that includes a wide range of strategy & techniques employed by the driver, presence and shape of certain elements.
- The 2nd feature set is composed of general track description: length, pace, number of certain elements (like tricks, flips, moving objects), number of turns etc.
- The 3rd feature set is the harder to gather, to justify and to understand ; it is composed of feature that tries to quantify the human experience of various aspect of this track.
    - 3 sentiment score (Keep, Indifferent, Remove) from different player population (competitive, top level, mid level, casual). These are only available for track present in the CTGP pack. Theses data are taken from the polls realized by the community to determine the future of the pack.
    - Other features: casuality, theme & atmosphere,	visuals, jankiness etc. These are very hard to gather and justify and are the most prone to biais and subjectivity.



### Dependencies
This project was updated for Brawlcrate v0.42 Hotfix 1 & Blender 4.2.

### Improvements
- Usage of a Conditional GAN (cGAN) to incorporate Tabular data.
- Usage of a Semi-Supervised SGAN (SGAN) to allow for liberty in the track used (not part of CTGP).
- Same improvements but using a VAE.
- Explore the use of Low Rank Adaptation (LoRA) for this task.
- Add additional channels containing potential valuable information for the model: Track direction, road width gradient away from center, Normal map.


###### TODO
- Refactor utility functions to a separate utils file.