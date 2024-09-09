from reader.file_reader import get_file_reader
from relational_table_understanding.relational_table_processor import RelationalTableProcessor


def main():

    input_file = "/Users/work/Projects/table-understanding/datamart_dataset/census/2007-11_ACS_Migration_Profile_In_Movers.xlsx"
    # input_file = "/Users/work/Projects/table-understanding/datamart_dataset/census/2007-11_ACS_Migration_Profile_Intra_State.xlsx"
    # input_file = "/Users/work/Projects/table-understanding/datamart_dataset/census/P1_County_1yr_interim.xlsx"
    # input_file = "/Users/work/Projects/table-understanding/datamart_dataset/census/Web_ACS2017_Educ.xlsx"
    reader = get_file_reader(input_file)

    for sheet in reader.get_sheets():
        rtp = RelationalTableProcessor(sheet)
        rtp.parse_table()


if __name__ == "__main__":
    main()
