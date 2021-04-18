## Bulk image resizer

# This script simply resizes all the images in a folder to one-eigth their
# original size. It's useful for shrinking large cell phone pictures down
# to a size that's more manageable for model training.

# Usage: place this script in a folder of images you want to shrink,
# and then run it.

import numpy as np
import cv2
import os

dir_path = os.getcwd()

count = 0

for filename in os.listdir(dir_path):
    size = os.path.getsize(filename) / 1000    # gets filesize in KB
    # If the images are not .JPG images, change the line below to match the image type.
    if filename.endswith(".JPG") and size > 300:
        image = cv2.imread(filename)
        dsize = (1280, 720)
        #resized = cv2.resize(image, dsize, interpolation=cv2.INTER_AREA)
        # You can also use the below to change the image size by a certain factor
        resized = cv2.resize(image, None, fx=.5, fy=.5, interpolation=cv2.INTER_AREA)
        cv2.imwrite(filename,resized)
        count += 1

        # To print image dimensions
        #image = cv2.imread(filename)
        #print(image.shape)

print(f'Done! Resized {count} images.')