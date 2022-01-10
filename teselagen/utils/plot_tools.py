#!/usr/bin/env python3
# Copyright (c) TeselaGen Biotechnology, Inc. and its affiliates. All Rights Reserved
# License: MIT
"""Plotting tools for DNA sequence objects."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING
import uuid

from dna_features_viewer import CircularGraphicRecord
from dna_features_viewer import GraphicFeature
from IPython.display import display_html
from IPython.display import display_javascript
from SecretColors import Palette

if TYPE_CHECKING:
    from typing import Any, Dict, List, Optional, Tuple, Union

    from matplotlib.axes import SubplotBase

    # from matplotlib.axes import Axes

# from dna_features_viewer import GraphicRecord


# TODO(diegovalenzuelaiturra): Verify the following output type is more appropriate: Tuple[Axes, Tuple[dict, dict]]:
def plot_plasmid_features(
    plasmid_length: int,
    features: List[Dict[str, Any]],
    figure_width: int = 5,
    palette: Optional[Palette] = None,
) -> Tuple[SubplotBase, Tuple[Any, Any]]:
    """Plots features in a circular dna sequence.

    Args:
        plasmid_length (int): Number of nucleotide bases of the plasmid sequence

        features (List[Dict[str, Any]]): Features as obtained from TeselaGen DNA Sequence object

        figure_width (int, optional): Width size of figure. Defaults to 5.

        palette (Optional[Palette], optional): A SecretColors color palette. \
            Defaults to None, meaning `Palette("material")` will be used.

    Returns:
        Tuple[AxesSubplot, Tuple[Any, Any]]: Axes and a tuple with Graphic features data
    """
    # Define random color palette
    if palette is None:
        palette = Palette('material')

    colors = palette.random(no_of_colors=len(features))

    # Create feat objects
    plot_feats = [
        GraphicFeature(
            start=feat['start'],
            end=feat['end'],
            strand=1 * feat['forward'],
            label=feat['name'],
            color=colors[i],
        ) for i, feat in enumerate(features)
    ]

    # Make graphic record and plot
    record = CircularGraphicRecord(sequence_length=plasmid_length, features=plot_feats)
    ax, _ = record.plot(figure_width=figure_width)

    # return ax, (features_levels, labels_data)
    return record.plot(ax)


# NOTE(diegovalenzuelaiturra): We should probably move `RenderJSON` class to `utils`
class RenderJSON:
    """Provides a an interactive visualization for json (or serializable list/dict) objects."""

    def __init__(
        self,
        json_data: Union[dict, list, str],
        height: str = 'max-content',
        width: str = '100%',
        background_color: str = '#f2f3ff',
    ) -> None:
        """Initiates json interactive visualization object for IPython.

        Args:
            json_data (Union[dict, list, str]): The object to be shown.

        Raises:
            TypeError: If input type is not supported
        """
        if isinstance(json_data, (dict, list)):
            self.json_str = json.dumps(json_data)
        elif isinstance(json_data, str):
            self.json_str = json_data
        else:
            raise TypeError(f"Can't process json_data of type {type(json_data)}")

        self.style = {
            'height': height,
            'width': width,
            'background_color': background_color,
        }

        self.uuid = str(uuid.uuid4())

    def _ipython_display_(self) -> None:
        """Renders JSON into collapsible HTML object by using.

        [renderjson.js](https://github.com/caldwell/renderjson)
        """
        display_html(f"""
            <div id="{self.uuid}" style="height: {self.style["height"]}; width:{self.style['width']};background-color: {self.style["background_color"]}";></div>
            """,
                     raw=True)

        display_javascript(f"""
            require(["https://rawgit.com/caldwell/renderjson/master/renderjson.js"], function() {{
            document.getElementById('{self.uuid}').appendChild(renderjson({self.json_str}))
            }});
            """,
                           raw=True)
