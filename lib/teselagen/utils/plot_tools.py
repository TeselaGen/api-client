#!/usr/bin/env python3
from typing import List, Dict, Any, Optional, Tuple, Union
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
        palette (Optional[Palette], optional): A SecretColors color palette. Defaults to None, meaning 
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
    """ Provides a an interactive visualization for json (or serializable list/dict) objects"""
    def __init__(
        self, 
        json_data: Union[dict, list, str],
        height: str="max-content",
        width: str="100%",
        background_color: str= "#f2f3ff"
        ):
        """Initiates json interactive visualization object for IPython

        Args:
            json_data (Union[dict, list, str]): The object to be shown.

        Raises:
            TypeError: If input type is not supported
        """
        if isinstance(json_data, (dict, list)) :
            self.json_str = json.dumps(json_data)
        elif isinstance(json_data, str):
            self.json_str = json_data
        else:
            raise TypeError(f"Can't process json_data of type {type(json_data)}")
        self.style={"height": height, "width": width, "background_color": background_color}
        self.uuid = str(uuid.uuid4())

    def _ipython_display_(self):
        """Renders JSON into collapsible HTML object by using [renderjson.js](https://github.com/caldwell/renderjson)
        """
        display_html(f"""
            <div id="{self.uuid}" style="height: {self.style["height"]}; width:{self.style['width']};background-color: {self.style["background_color"]}";></div>
            """, raw=True)
        display_javascript("""
            require(["https://rawgit.com/caldwell/renderjson/master/renderjson.js"], function() {
            document.getElementById('%s').appendChild(renderjson(%s))
            });
            """ % (self.uuid, self.json_str), raw=True)