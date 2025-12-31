# Dataset

### Tracks

In the best case we can collect around 5,000 tracks. Producing a high quality track take an enormous amount of time and dedication. It is therefore not reasonable to think that it is possible to produce more of it manually. Furthermore, since it takes a long time to create a "good" track, these represent only a small portion of the dataset.

Collect mario kart wii tracks in `.szs` format. For example, you can use the [Tockdom](https://wiki.tockdom.com/wiki/Main_Page) website, including, in particular, pages [List of Custom Tracks](https://wiki.tockdom.com/wiki/List_of_Custom_Tracks) and [Custom Track Distributions](https://wiki.tockdom.com/wiki/Custom_Track_Distribution) (a distribution being a collection of tracks).

### Tabular data

We created this tabular dataset to probe the model's capabilities. It will be released soon. This is were the creation process of the dataset gets very long. The data the author created involves watching the Best Known Times (BKT) videos for each [CTGP](https://wiki.tockdom.com/wiki/CTGP_Revolution) track, and take note of around 45 varied features decomposed into 3 feature sets. 

- The 1st feature set is composed of 33 features that includes a wide range of mecanical tech employed by the player, presence and shape of certain elements.
- The 2nd feature set is composed of general track description: length, pace, number of certain elements (like tricks, flips, moving objects), number of turns etc.
- The 3rd feature set is the harder to gather, to justify and to understand; it is composed of feature that tries to quantify the human experience of various aspect of this track.
    - 3 sentiment score (Keep, Indifferent, Remove) from different player population (competitive, top level, mid level, casual). **These ratings are exclusive to tracks featured in the CTGP pack**. The data is sourced from community polls that aim to shape the future of the CTGP distribution. We extend our gratitude to the Admins for orchestrating these polls and to the community for providing valuable insights. To access this data, join the [CTGP Track Tester Discord Server](https://discord.com/invite/sjPzuJ7PwD) and search for "sheet". Then, navigate to the Google Sheet titled "CTGP Backroom Informational Page" and select any "Track Rating Data" page.
    - Other features: casuality, theme & atmosphere, visuals, jankiness etc. These are very hard to gather and justify and are the most prone to biais and subjectivity.

### Telemetry

A file per race, containing ~50 game engine signals per player, 12 players, 60 Hz, from our [MKW Logger](https://github.com/BARALLL/mkw-logger).

!!! info
    One console records a per-frame snapshot of all 12 players from that console’s point of view. Because Mario Kart Wii uses peer‑to‑peer (RACEDATA) updates that arrive with delay (and not all peers are updated every frame), the snapshot reflects the recording console's latest received + locally simulated estimates (dead reckoning), not a global ground truth. In a full 12‑player room, any given peer may only receive fresh updates from another player every ~22 frames on average (plus Internet latency), so the recorded states are not globally time-aligned. As a result, the position you see for another driver on your screen can differ from what they see on theirs.

    ??? info "Technical details (MKWii online protocol facts that affect logging)"
        *   **Peer-to-Peer Architecture (P2P):** Unlike modern games with dedicated servers, MKWii uses a P2P mesh topology for gameplay. Each console calculates its own physics and sends data directly to the other 11 consoles via **UDP** packets. (TCP is only used for the initial matchmaking/login via the Master Server).
        *   **Staggered Updates (The "Round-Robin" Limit):** In the original game (Vanilla), the Wii's network adapter does not send updates to all 11 opponents simultaneously every frame. Instead, it cycles through them, sending updates to specific peers in a round-robin fashion. This means you might receive fresh position data from "Player A" only every few frames (approx. 10–30Hz effective update rate depending on lobby size), forcing the game to rely heavily on prediction algorithms.
        *   **Dead Reckoning:** When the game waits for a new packet, it assumes the opponent is continuing at their last known velocity. If the opponent actually turned or stopped during that gap, they will appear to "teleport" or "snap" to the correct position once the new packet finally arrives.
        *   **Room Host Authority:** While movement is P2P, one console acts as the "Room Host" to synchronize shared events (like the Item Roulette RNG and race start timer) to prevent major game-breaking desyncs.


See the [Regarding telemetry data availability](dataset_availability.md#regarding-telemetry) section. There's also the possibility (very partial solution) to download Time Trials replays (`.rkg` files) from Chadsoft website using our [BKT Downloader](https://github.com/BARALLL/mkw-bkt-downloader) and producing log files from those, but it will mean one player (no interaction) and very limited item usage.

---

## Generation of the dataset for the first iteration
### Images

The creation of the image portion of the dataset involves two steps after the tracks have been collected.

#### 2. Minimap Extraction
##### Design Choices


:   Mario Kart Wii tracks often feature scenery surrounding the racing lane. We have to make sure that only the racing lane is extracted, since we are not interested in the scenery to understand the track layout. Since the racing lane can be composed of multiple sections incorporating distinct 3D objects, it's impossible to directly identify the elements that constitute it. Furthermore, the same texture could be used in both certain portions of the road and elements of the scenery, making it difficult to distinguish between these two entities. The most reliable method for extracting the track is therefore to utilize the minimap. This minimap is not a simple 2D texture but 3D model that is defined by the track creator. A potential drawback of this approach is the possibility that the creator flattens the this minimap, thereby removing any information related to elevation. However, this situation remains a minority. In this specific case, it is recommended to return to the Brawlcrate tool in order to extract the different sections of the track in `.obj` format. Then, in a 3D modeling software such as Blender, it is advisable to remove all textures and materials and merge the different sections of the track. Export the resulting object in `.dae` format. (Although the next step in the dataset creation pipeline could theoretically support multiple objects, it is preferable to provide a single unified object.)


##### Usage

:   Using the Brawlcrate tool, go to the Tool menu and click on Run Script. Select the script `brawlcrate_minimap_scraping.py`. Follow the instructions given by the script. This will extract the mini-maps as `.dae` files from a `.szs` file.

#### 3. Material Map Creation

This step was originally intended to generate a normalized height map of the race track. Later, we realized that the same workflow could be extended to produce other texture maps from the 3D object, such as a normal map that could be used as an additional channel to help the model. However, this should be done in moderation, as it adds capacity to the model. The only requirement is a shader that writes the desired data into a texture. A height-map shader is included.

##### Design Choices

<div class="no-bullets" markdown="1">
- AI models processing 3D information (mesh) are inherently complex. The addition of this supplementary dimension can significantly compromise the model's ability to generalize and comprehend creative processes. Moreover, the crucial lack of data makes this task particularly challenging.
- A promising strategy to mitigate these challenges is to reduce the third dimension (height) to a grayscale channel of the image. Although this may result in some loss of information (for example, when one part of the circuit overlaps another), the majority of the information is retained and allows the model's training.
- Similarly, we can project the 3D direction (x, y, z) of the circuit onto a three-channel RGB representation, transforming complex spatial information into a more accessible format for machine learning.
</div>

##### Usage

<div class="no-bullets" markdown="1">
- Organize your `.dae` files into a single directory (which should already be mostly complete from the previous step). Download the `material_map_generator.zip` Blender Add-on from the Releases section (or download the material_map_generator folder under data_tools/ and zip it manually).
- Launch Blender and ensure you're running a [supported version](dataset.md#dependencies). Navigate to `Edit >> Preferences >> Add-ons`, then click the downward-pointing arrow in the top right of the Preferences window. Select `"Install from Disk"` and choose the downloaded zip file. Activate the add-on by checking the box next to its name if not already enabled.
- Press `'N'` to display the viewport panel (alternatively, click the left-pointing arrow on the right side of the viewport near the Rotate View gizmo). Locate and select the Material Map Generator panel.
</div>

: Configure your settings:

    - Select the source folder containing your `.dae` files
    - Choose a destination folder for generated material maps
    - Choose the material map
    - Optionally, designate a folder for processed `.dae` files to simplify potential restart scenarios

<div class="no-bullets" markdown="1">
- Click `"Generate Material Maps"` to initiate the process.
- You can also add images from other sources, as long as they have the same format as the existing images and are relevant to the AI task you are trying to accomplish.
</div>

### Dependencies

Data tools were updated for Brawlcrate v0.42 Hotfix 1 & Blender 4.2.