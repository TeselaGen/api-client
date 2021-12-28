#!/usr/bin/env python3
# Copyright (c) TeselaGen Biotechnology, Inc. and its affiliates. All Rights Reserved
# License: MIT

from __future__ import annotations

from typing import List, Optional

from dna_features_viewer import GraphicFeature
from dna_features_viewer import GraphicRecord


def show_crispr_grna_results(
    sequence: str,
    guides: List[dict],
    indexes: Optional[List[int]] = None,
    scoreField: str = "onTargetScore",
):
    """Shows guide rnas results for CRISPR.

    Args:
        sequence (str): A string containing the complete organism sequence

        guides (dict): A table on 'records' format that contains guides info.\
            The required fields are `start` (int), `end` (ind), indicating the limits of the guide in sequence's index.

        indexes(list): Indexes (start and end) of the targeted sequence within the complete sequence. \
            If not set, the targeting sequence is not shown.

        scoreField (str): Select which score from GRNA tool show in the chart. \
            Available scores are "onTargetScore" (default) and "offTargetScore"
    """
    targeting_seq_feat = []
    # Show main targeted sequence if index are set. If not, we calculate indexes to limit plot range at the `crop`
    # instruction.
    if indexes is not None:
        targeting_seq_feat = [
            GraphicFeature(
                start=indexes[0],
                end=indexes[1],
                color="#cffccc",
                label="Sequence",
                strand=+1,
            ),
        ]
    else:
        # TODO(diegovalenzuelaiturra): Check behavior is the same when using generators instead of lists.
        # indexes = [min([x['start'] for x in guides]), max([x['end'] for x in guides])]
        indexes = [min(x['start'] for x in guides), max(x['end'] for x in guides)]

    # Plot records
    record = GraphicRecord(
        sequence=sequence,
        features=targeting_seq_feat + [
            GraphicFeature(
                start=x['start'],
                end=x['end'] + 1,
                color="#ffcccc",
                label=f"{scoreField}: {x[scoreField]}",
                strand=+1 if x['forward'] else -1,
            ) for x in guides
        ],
    )

    # Limit plot range
    record = record.crop((indexes[0] - 10, indexes[1] + 11))  # crop

    # Plot and set to show sequence
    ax, _ = record.plot(figure_width=20)

    record.plot_sequence(ax)
