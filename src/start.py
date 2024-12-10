import os
import camelot
import pandas as pd
import logging
from unidecode import unidecode

class PDFTableExtractor:

    def __init__(self, file_name, configs):
        self.path = os.path.abspath(f"src/files/pdf/{configs["name"].lower()}/{file_name}.pdf")
        self.csv_path = os.path.abspath(f"src/files/csv")
        self.file_name = file_name
        self.configs = configs

    def start():
        pass

    def get_table_data(self, t_area, t_columns, fix):
        tables = camelot.read_pdf(
            self.path,
            flavor=self.configs["flavor"],
            table_areas = t_area,
            columns = t_columns,
            strip_text = self.configs["strip_text"],
            page = self.configs["page"],
            password= self.configs["password"]
        )

        

    def save_csv():
        pass
    def add_infos():
        pass

    @staticmethod
    def fix_header(df):
        df.columns = df.iloc[0] # Uses the first row as column names
        df = df.drop(0) # Removes the first row
        df = df.drop(df.columns[0], axis=1) # Removes the first column

    def sanitize_column_names():
        pass
    def send_to_db():
        pass

if __name__== "__main__":
    extractor = PDFTableExtractor().start()

    print(extractor)