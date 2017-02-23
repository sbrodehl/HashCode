import numpy as np
import pandas as pd


def read_dataset(filepath):
    # open the file
    with open(filepath) as fis:
        line_count = 0
        for _ in fis:
            line_count += 1
        fis.seek(0)
        
        print(line_count)

        for i in range(line_count):
            pass

