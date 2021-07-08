#!/usr/bin/env python3
from typing import List, Dict, Any, Optional, Tuple

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