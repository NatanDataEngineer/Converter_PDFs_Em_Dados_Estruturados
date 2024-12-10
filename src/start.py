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
            self.path, # path to the PDF file
            flavor=self.configs["flavor"], # parsing method for tables
            table_areas = t_area, # specific area in the PDF to extract tables from
            columns = t_columns, # specific columns positions
            strip_text = self.configs["strip_text"], # removes extra withespace 
            page = self.configs["page"], # specific page(s) to extract from
            password= self.configs["password"] # PDF password if encrypted
        )

        # Quebrar o PDF em três data frames e depois concatena-los com o pandas
        table_content = [self.fix_header(page.df) if fix else page.df for page in tables]
        result = pd.concat(table_content, ignore_index=True) if len(table_content) > 1 else table_content[0]
        return result

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