# Kartographer: MKW Layout Generation

## Project Overview

This project aims to study the creative and gameplay-driven design choices behind Mario Kart Wii track layouts. By analyzing community-created tracks and how players actually drive them, we aim to extract design-relevant signals like enjoyment, challenge, creativity, and balance — in a way that can both help human designers reason about a layout and eventually support controlled generation of new tracks that target specific gameplay qualities.

This repository contain the code for:

- **Kartographer:** a generative world model for Mario Kart Wii tracks. Please see [our approach](./kartographer/approach.md) for a better understanding of the project. *(in progress)*
- **MKW Telemetry Visualizer** to visualize the data extracted by our [MKW Logger](https://github.com/BARALLL/mkw-logger). Please see [MKW Telemetry Visualizer explained](./mkwdashboard/mkw_dashboard.md).
- Data processing tools

!!! info "Quick Start Guide"

    <div class="grid cards" markdown>

    -   :material-text-box-edit: __The Methodology__
        
        Understand [our approach](./kartographer/approach.md#the-difficult-nature-of-a-layout-design-track-geometry-as-strategy) and why we made specific [design decisions](./kartographer/approach.md#why-these-inputs).

    -   :material-database: __The Data__
        
        Read about the [dataset availability](./data/dataset_availability.md) and learn about the [dataset](./data/dataset.md).

    -   :material-monitor-dashboard: __Visualizer__
        
        Learn how to [visualize MKW telemetry data](./mkwdashboard/mkw_dashboard.md) using our visualizer tool.

    -   :material-book-open-page-variant: __Research Purpose__
        
        Read about the [context of this project](index.md#research-purpose).

    </div>



## Research Purpose

This project is exploratory research aimed at better understanding human creative work, e.g., what tends to make a track effective or compelling. We designed the project to respect creators by not redistributing their works in bulk and by keeping provenance back to original sources, while allowing reproducibility.

We do not intend this work to replace creators or appropriate their expression, but to augment our understanding of design theory. We view artistic creation as a human practice rooted in personal expression, and we encourage any use of this tool to respect creators' rights, credit, and agency.

!!! note
    for any type of question related to Mario Kart Wii, the [Tockdom](https://wiki.tockdom.com/wiki/Main_Page) website is an excellent resource.