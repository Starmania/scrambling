"""Module to encode the image

Example:
```python
from getscrambled import encode
import PIL.Image

img = PIL.Image.open("image.png")
blocks, encoded_img = encode.encode_block(img)
full_img = encode.add_data_image(encoded_img, blocks)

full_img.save("encoded_image.png")
```
"""
import json
import typing

import PIL
import PIL.Image
import numpy as np
import stegano

from .exceptions import ImageFormatError
from .constants import constants as C
from .shared import create_block_grid, arrange_blocks

if typing.TYPE_CHECKING:
    from typing import List, TypeVar

    T = TypeVar('T')
    Image = PIL.Image.Image


def add_data_image(image: "Image", blocks):
    """Add the blocks information to the image

    Args:
        image (Image): The image to be modified
        blocks (list[tuple[int, int]]): The positions of the blocks

    Raises:
        ImageFormatError: If the image is known to not be a PNG image

    Returns:
        Image: The modified image
    """
    if isinstance(image, str):
        image = PIL.Image.open(image)

    if image.format not in ("PNG", None):
        raise ImageFormatError(image)

    # Minimise the size of the variable "blocks"
    number_list = []
    for x, y in blocks:
        number_list.append(int(x))
        number_list.append(int(y))

    json_data = json.dumps(number_list, separators=(',', ':'))

    return stegano.lsb.hide(image, json_data)


def encode_blocks(image: "Image", block_size: int = None):
    """Create a new image with an random arrangement of the blocks of the original image

    Args:
        image (Image): The original image
        block_size (int, optional). Defaults to BS.

    Raises:
        ImageFormatError: If the image is known to not be a PNG image
    """
    if block_size is None:
        block_size = C.BLOCK_SIZE

    if isinstance(image, str):
        image = PIL.Image.open(image)

    if image.format not in ("PNG", None):
        raise ImageFormatError(image)

    # Generate blocks positions
    blocks = create_block_grid(*image.size, block_size)

    # Shuffle blocks
    np.random.shuffle(blocks)

    encoded_image = arrange_blocks(image, block_size, blocks)

    blocks.insert(0, (block_size, )*2)  # So we can recover the block size
    blocks.insert(0, image.size)  # So we can recover the original image size

    return blocks, encoded_image

def encode(image: "Image", block_size: int = None):
    """Encode the image with the blocks information

    Args:
        image (Image): The image to be encoded
        block_size (int, optional). Defaults to BS.

    Returns:
        Image: The modified image
    """
    blocks, encoded_img = encode_blocks(image, block_size)
    return add_data_image(encoded_img, blocks)
