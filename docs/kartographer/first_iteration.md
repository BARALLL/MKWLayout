# The approach of our first iteration

AI models that operate directly on 3D meshes are inherently complex. The extra spatial dimension greatly increases data size and model complexity, the crucial lack of data in our case makes this task particularly challenging.  

A practical way to reduce this complexity is to **project the 3D geometry onto 2D images**. We can project the track onto a 2D plane (top-down view) and encode the height (z) at each point as a grayscale value. This creates a heightmap: some vertical information is lost in overlapping regions (e.g., bridges or overpasses), but most of the structural information is preserved and becomes much easier for 2D models to process. We can also stack multiple images as multiple channels to add other kind of informations, for example, normals as RGB.

These projections trade a small amount of geometric precision for much simpler inputs and better data efficiency, which can improve training feasibility and model performance in our low data context (~5,000 unique tracks/samples, [see this section for more details](../data/dataset.md#tracks)).

Under this formulation, this becomes a image generation problem.


## Lessons learned from this first attempt

One limitation became obvious: we don't have (and realistically won't ever have) enough unique tracks to train a robust model from track data alone. This became key for our second approach, which led us to collect other types of data and brought us to a more promising approach. This first realization, and the prospect of collecting other kinds of data in meaningful quantities, prompted us to rethink our design and return to a 3D input format for the track, which is strictly richer than 2D. See section [Kartographer - Why these inputs?](./approach.md#why-these-inputs) for more details.

