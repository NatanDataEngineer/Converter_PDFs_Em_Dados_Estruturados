import os
import camelot
import pandas as pd
import logging
from unidecode import unidecode
from src.configs.tools import RDSPostgreSQLManager;

# Configuring basic logging settings for python's logging module
logging.basicConfig(level=logging.INFO)

class PDFTableExtractor:

    def __init__(self, file_name, configs):
        self.path = os.path.abspath(f"src/files/pdf/{configs["name"].lower()}/{file_name}.pdf")
        self.csv_path = os.path.abspath(f"src/files/csv")
        self.file_name = file_name
        self.configs = configs

    def start():
        pass

    # Extraindo tabelas de um PDF com parâmetros muito específicos usando Camelot
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

        # Break PDF into three data frames and then merge them with pandas
        table_content = [self.fix_header(page.df) if fix else page.df for page in tables]
        result = pd.concat(table_content, ignore_index=True) if len(table_content) > 1 else table_content[0]
        return result

    '''
    Creates the target directory if it doesn't exist, generates a file path,
    and exports the DataFrame as a CSV using semicolon as separator.
    '''
    def save_csv(self, df, file_name):
        # Check if directory exists, if not create it
        if not os.path.exists(self.csv_path):
            os.makedirs(self.csv_path, exist_ok=True)

        # Create full path for the CSV file
        path = os.path.join(self.csv_path, f"{file_name}.csv")

        # Save DataFrame to CSV
        df.to_csv(path, sep=";", index=False)

    def add_infos():
        pass

    # Cleaning up the hearder
    @staticmethod
    def fix_header(df):
        df.columns = df.iloc[0] # Uses the first row as column names
        df = df.drop(0) # Removes the first row
        df = df.drop(df.columns[0], axis=1) # Removes the first column

    def sanitize_column_names():
        pass

    # Saving data from a pandas DataFrame into a specific table in a database.
    def send_to_db(df, table_name):
        try:
            # Connecting to the database using RDSPostgreSQLManager which provides an
            # SQLAlchemy connection
            conection = RDSPostgreSQLManager().alchemy
            # Iserting the DataFrame's content into a table using pandas
            df.to_sql(table_name, conection, if_exists="append", index=False)
            # Success message if succeeded 
            logging.info(f"Dados salvos no DB {table_name}")
        except Exception as e:
            logging.error(e)


if __name__== "__main__":
    extractor = PDFTableExtractor().start()

    print(extractor)