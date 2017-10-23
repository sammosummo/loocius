import numpy as np
from colour.models.rgb.deprecated import RGB_to_HSV

RGB = np.array([[1, 1, 1]])
print(RGB_to_HSV(RGB))