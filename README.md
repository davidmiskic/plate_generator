# plate_generator
Arranges the given samples in the most separated way if possible
## Usage
The input data consists of 5 variables:

- the integer 96 or 384, defining the plate size,
- array of arrays of strings, which are the names of the samples assigned to the experiment (each array belongs to one experiment),
- array of arrays of strings, which are the names of the reagents which belong to each experiment (again each array belongs to one experiment),
- array of integers, where each integer defines the number of replicates for individual experiment,
- maximum allowed number of plates.

The output is a plotly plot of each plate, the function returns a dictionary of plates, consisting of a list of plate rows.
