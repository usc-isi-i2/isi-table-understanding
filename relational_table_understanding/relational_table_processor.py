# https://docs.google.com/document/d/1sCEkcXW5ibe09bmF81UlMi7qdhL3n68NPksOhCUlebk/edit
from util.string_utils import data_to_string
import numpy as np
from relational_table_understanding.edit_distance import edit_distance_score
from relational_table_understanding.elbow_point import find_elbow_point

class RelationalTableProcessor:
    def __init__(self, table):
        self.table = self.stringify_table(table)
        # This format is not final. Just for now. DO NOT stick to this
        self.header_rows = []
        self.time_cols = []
        self.measurement_cols = []
        self.meta_cols = []

    # Identify header rows
    # Identify time columns
    # Identify value columns

    def find_header_rows(self):
        # Method 1. Compute avg edit distance score for non header rows. Find elbow point.
        # Method 2. Find row where numeric entries start
        # If numeric entries start from the first row -> assume no header is present
        # If no numeric entries are present, then abort

        # EDIT DISTANCE
        # Top 30 rows should be enough to find the header
        num_rows_to_process = min(30, self.table.shape[0])
        t_table = np.copy(self.table[:num_rows_to_process])

        if num_rows_to_process >= 3:  # 3 is the minimum number of rows required to use this method
            scores = edit_distance_score(t_table)
            header_rows, elbow_score = find_elbow_point(scores)
        else:
            print("Table size is too small.")
            return

        if elbow_score >= -10:   # Arbitrary number based on small sample set
            print("Not a clear elbow")
            return

        if header_rows >= 10:
            # Possible misclassification. Need other methods to verify the results
            # Could there be no headers? Can we check this by trying to fit a linear regression through the points?
            header_rows = 0

        if header_rows == 0:
            # TODO: TODO: TODO: *** Find row where numeric entries start ***
            header_rows = 1

        print("Number of header_rows ", header_rows)

        self.header_rows = [i for i in range(header_rows)]

    def stringify_table(self, table):
        row, col = table.shape
        for i in range(row):
            for j in range(col):
                table[i][j] = data_to_string(table[i][j])

        return table

    def find_column_types(self):
        # find_column_types(self.table)
        pass

    # Understand headers
    def parse_table(self):
        # Identify headers
        self.find_header_rows()

        # self.find_column_types()
