from itertools import product
import copy
import math
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
import numpy as np
import string


def calculate_wells(sample_arrays, reagent_arrays, replicates, limit):
    current = 0
    for i in range(0, len(replicates)):
        current += len(sample_arrays[i])*len(reagent_arrays[i])*replicates[i]
        if current > limit: return False
    return True


# multichannel pipettes: x8, x12, x16
# 384: 16 rows x 24 cols
# 96: 8 rows x 12 cols
# keep them close by and in a continuous area as much as possible, try to repeat the patterns from experiment to experiment
# replicates - usually from same bigger container, optimally pippeted sequentially
# samples and reagents mixed in plate - use the one with larger count and less groups
def generate(plate_size, sample_arrays, reagent_arrays, replicates, max_plates):
    def visualize_plates(plates):
        for q, key in enumerate(plates.keys()):
            plate = plates[key]
            val_plate = np.zeros((y, x))
            for i, row in enumerate(plate):
                for j, elem in enumerate(row):
                    if elem is not None:
                        val_plate[i, j] = list(sample_dict.keys()).index(elem[0]) + list(reagent_dict.keys()).index(
                            elem[1])
                    else:
                        val_plate[i, j] = np.nan
            fig = ff.create_annotated_heatmap(val_plate, annotation_text=plate, x=[i + 1 for i in range(x)],
                                              y=list(string.ascii_uppercase[0:y])[::-1], hoverinfo="skip")
            fig.show()

    assert plate_size in (384, 96)
    assert calculate_wells(sample_arrays, reagent_arrays, replicates, plate_size*max_plates) is True

    x = 12 if plate_size == 96 else 24
    y = 8 if plate_size == 96 else 16

    # make all pairs
    pairs = []
    for i in range(0, len(replicates)):
        experiment_pairs = [list(p) for p in product(sample_arrays[i], reagent_arrays[i])]
        for p in experiment_pairs: pairs += [p.copy() for _ in range(replicates[i])]
    print(pairs)

    # calculate group counts
    sample_dict = {}
    reagent_dict = {}
    for p in pairs:
        if p[0] not in sample_dict.keys(): sample_dict[p[0]] = 0
        if p[1] not in reagent_dict.keys(): reagent_dict[p[1]] = 0
        sample_dict[p[0]] += 1
        reagent_dict[p[1]] += 1

    # where more groups, order by them, so less switching
    chosen = sample_dict if len(sample_dict.keys()) >= len(reagent_dict.keys()) else reagent_dict
    print("chosen", chosen)
    filling = []
    for key in chosen.keys():
        for i, sample in enumerate(pairs):
            if key in sample and len(sample) != 3:
                filling.append(sample)
                pairs[i].append(True)

    needed_plates = math.ceil(len(filling)/plate_size)
    free_wells = needed_plates*plate_size - len(filling)
    byrow, bycol = 0, 0
    for key in chosen.keys():  # how many free wells would separating groups require
        byrow += x - chosen[key]%x
        bycol += y - chosen[key]%y

    plates = {}
    cnt = 0
    ckeys = list(chosen.keys())
    ckeys.reverse()
    ckey = None

    if len(ckeys) <= y*needed_plates and byrow <= free_wells: # in each row own group
        print("first")
        for plate in range(1, needed_plates+1):
            plates[plate] = []
            for i in range(y):
                r = []
                try:  # if we did not reach the end of the group
                    if (cnt+1 < len(filling) and ckey not in filling[cnt+1]) or ckey is None: ckey = ckeys.pop()
                except:break
                for j in range(x):
                    if cnt < len(filling) and ckey in filling[cnt]: r.append(filling[cnt][0:2])
                    if cnt < len(filling) and ckey not in filling[cnt]: break
                    cnt += 1
                while len(r) != x: r.append(None)
                print(plate, i+1, r)
                plates[plate].append(r)
            plates[plate].reverse()
    elif len(ckeys) <= x*needed_plates and bycol <= free_wells:  # in each column own group
        print("second")
        for plate in range(1, needed_plates+1):
            plates[plate] = []
            for i in range(x):
                c = []
                try:  # if we did not reach the end of the group
                    if (cnt + 1 < len(filling) and ckey not in filling[cnt + 1]) or ckey is None: ckey = ckeys.pop()
                except:break
                for j in range(y):
                    if cnt < len(filling) and ckey in filling[cnt]: c.append(filling[cnt][0:2])
                    if cnt < len(filling) and ckey not in filling[cnt]: break
                    cnt += 1
                while len(c) != y: c.append(None)
                print(plate, c)
                plates[plate].append(c)
        plates[plate].reverse()
        plates[plate] = np.flipud(np.array(plates[plate]).T)
    else:  # put sequentially
        print("third")
        for plate in range(1, needed_plates+1):
            plates[plate] = []
            for i in range(y):
                r = []
                for j in range(x):
                    if cnt < len(filling): r.append(filling[cnt][0:2])
                    cnt+=1
                while len(r) != x: r.append(None)
                print(plate, r)
                plates[plate].append(r)
            plates[plate].reverse()

    visualize_plates(plates)
    return plates


### first option - by rows
# generate(
#   96,
#   [['Sample-1', 'Sample-2', 'Sample-3'], ['Sample-1', 'Sample-2', 'Sample-3']],
#   [['<Pink>'], ['<Green>']],
#   [3, 2],
#   1
# )

### third option - sequentially
# generate(
#   96,
#   [['Sample-1', 'Sample-2', 'Sample-3'], ['Sample-1', 'Sample-2', 'Sample-3'], ['Sample-1', 'Sample-2', 'Sample-3'], ['Sample-1', 'Sample-2', 'Sample-3']],
#   [['<Pink>'], ['<Green>'], ["Black"], ["Blue"]],
#   [10, 10, 2, 10],
#   1
# )

### second option - by columns
generate(
  96,
  [['Sample-1', 'Sample-3'], ['Sample-2', 'Sample-3'], ['Sample-1', 'Sample-3']],
  [['<Pink>', '<Green>', "Blacck", "Blue", "red", "violett"], ['<Pinkk>', '<Green>', "Blue", "redd"], [ '<Green>', "Black", "Bluue", "reddd", "violet"]],
  [1, 1, 1],
  1
)

### too many samples - error
# generate(
#   96,
#   [['Sample-1', 'Sample-2', 'Sample-3'], ['Sample-1', 'Sample-2', 'Sample-3'], ['Sample-1', 'Sample-2', 'Sample-3'], ['Sample-1', 'Sample-2', 'Sample-3']],
#   [['<Pink>'], ['<Green>'], ["Black"], ["Blue"]],
#   [10, 10, 2, 12],
#   1
# )