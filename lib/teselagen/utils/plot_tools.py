#!/usr/bin/env python3
from typing import List, Dict, Any, Optional, Tuple
import uuid
from IPython.display import display_javascript, display_html, display
import json

from dna_features_viewer import GraphicFeature, CircularGraphicRecord #, GraphicRecord
from SecretColors import Palette
from matplotlib.axes import SubplotBase


def plot_plasmid_features(
    plasmid_length: int, 
    features: List[Dict[str, Any]], 
    figure_width: int=5, 
    palette: Optional[Palette]=None)->Tuple[SubplotBase, Tuple[Any, Any]]:
    """Plots features in a circular dna sequence

    Args:
        plasmid_length (int): Number of nucleotid bases of the plasmid sequence
        features (List[Dict[str, Any]]): Features as obtained from TeselaGen DNA Sequence object
        figure_width (int, optional): Width size of figure. Defaults to 5.
        palette (Optional[Palette], optional): A SecretColors color palette. Defaults to None, menaing 
            `Palette("material")` will be used.

    Returns:
        Tuple[AxesSubplot, Tuple[Any, Any]]: Axes and a tuple with Graphic features data
    """
    # Define random color pallete
    if palette is None:
        palette = Palette("material")
    colors = palette.random(no_of_colors=len(features))
    # Create feat objects
    plot_feats = [
        GraphicFeature(start=feat['start'], end=feat['end'], strand=1*feat['forward'], label=feat['name'], color=colors[i]) 
        for i, feat in enumerate(features)]
    # Make graphic record and plot
    record = CircularGraphicRecord(sequence_length=plasmid_length, features=plot_feats)
    ax, _ = record.plot(figure_width=figure_width)
    return record.plot(ax)



class RenderJSON(object):
    def __init__(self, json_data):
        if isinstance(json_data, dict):
            self.json_str = json.dumps(json_data)
        else:
            self.json_str = json_data
        self.uuid = str(uuid.uuid4())

    def _ipython_display_(self):
        display_html(f"""
            <div id="{self.uuid}" style="height: max-content; width:100%;background-color: #f2f3ff";></div>
            """, raw=True)
        display_javascript("""
            require(["https://rawgit.com/caldwell/renderjson/master/renderjson.js"], function() {
            document.getElementById('%s').appendChild(renderjson(%s))
            });
            """ % (self.uuid, self.json_str), raw=True)