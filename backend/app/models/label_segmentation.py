from typing import List, Tuple

from models.label import LabelBase


class LabelSegmentation(LabelBase):
    """
    The core data of segmentation
    """

    mask: List[Tuple[float, float]]
