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

    # Automating the workflow of extracting, cleaning and saving data from PDFs into a dabase
    def start(self):
        logging.info(f"Start pdf - {self.file_name}")
        header = self.get_table_data(self.configs["header_table_areas"], self.configs["header_columns"], self.configs["header_fix"])
        main = self.get_table_data(self.configs["table_areas"], self.configs["columns"], self.configs["fix"])
        small = self.get_table_data(self.configs["small_table_areas"], self.configs["small_columns"], self.configs["small_fix"])

        main = self.add_infos(header, main)
        small = self.add_infos(header, small)

        main = self.sanitize_column_names(main)
        if self.configs["small_sanitize"]:
            small = self.sanitize_column_names(small)

        logging.info(f"Saving csv - {self.file_name}")
        self.save_csv(main, self.file_name)
        self.save_csv(small, f"{self.file_name}_small")

        logging.info(f"Sending to DB - {self.file_name}")
        self.send_to_db(main, f"Fatura_{self.configs["name"]}".lower())
        self.send_to_db(small, f"Fatura_{self.configs["name"]}_small".lower())

        return{"main": main, "small": small}


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

    # Creates the target directory if it doesn't exist, generates a file path,
    # and exports the DataFrame as a CSV using semicolon as separator.
    def save_csv(self, df, file_name):
        # Check if directory exists, if not create it
        if not os.path.exists(self.csv_path):
            os.makedirs(self.csv_path, exist_ok=True)

        # Create full path for the CSV file
        path = os.path.join(self.csv_path, f"{file_name}.csv")

        # Save DataFrame to CSV
        df.to_csv(path, sep=";", index=False)

    # Combining info from header with some info from content
    def add_infos(self, header, content):
        # This grabs the first row of the header DataFrame as a series called infos
        infos = header.iloc[0];

        # It takes the values from the first row of header and repeats them to create a new DataFrame
        df = pd.DataFrame([infos.value] * len(content), columns=header.columns)

        # Merging the content DataFrame and the newly created DataFrame side-by-side
        # Ensures that the indices of both DataFrames are reset so they align properly.
        content = pd.concat([content.reset_index(drop=True), df.reset_index(drop=True)], axis=1)

        # Adding timestamp(current date) for every row
        content["Data de Inserção"] = pd.Timestamp('today').normalize()
        return content
        
    # Cleaning up the hearder
    @staticmethod
    def fix_header(df):
        df.columns = df.iloc[0] # Uses the first row as column names
        df = df.drop(0) # Removes the first row
        df = df.drop(df.columns[0], axis=1) # Removes the first column

    # Formating the text in the DataFrame before saving into the Database
    def sanitize_column_names(self, df ):
        # Removing "ç" and "accents"
        df.columns = df.columns.map(lambda x: unidecode(x))

        # Replacing " " with "_"
        df.columns = df.columns.str.replace(" ", "_")

        # Replacing special characters
        df.columns = df.columns.str.replace(r"\W", "", regex=True)

        # Passing text to lowercase
        df.columns = df.columns.str.lower()

        return df

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

    # Retrieving a list of file names from a specific folder 
    def list_files(folder):
        try:
            files = [os.path.splitext(f)[0] for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
            return files
        except FileNotFoundError:
            logging.info(f"A pasta '{folder}' não foi encontrada.")
            return []
        except Exception as e:
            logging.info(f"Ocorreu um erro: {e}")
            return []


if __name__== "__main__":
    
    extractor = PDFTableExtractor().start()

    print(extractor)