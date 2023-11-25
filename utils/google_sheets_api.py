import warnings
from datetime import datetime
from typing import Type, List

import gspread
from googleapiclient.errors import HttpError
from gspread import Client, Spreadsheet

from data.models import User, Product, Order, Base

warnings.filterwarnings("ignore", category=DeprecationWarning)
# Задолбал warning

# Constants
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SAMPLE_SPREADSHEET_ID = "1AxVYr1-BeCfCXffPfWZv4GX09YhXhF-_8qNsUQh52kQ"
SAMPLE_RANGE_NAME = "A1:E5"
CREDENTIALS_FILE = "../data/betmarket_creds.json"


class GoogleSheetsService:
    
    def __init__(self):
        self.client: Client = gspread.service_account(filename=CREDENTIALS_FILE, client_factory=Client)
    
    def generate_unique_sheet_name(self, base_name):
        unique_suffix = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f'{base_name}_{unique_suffix}'
    
    def create_sheets(self, spreadsheet, sheet_names):
        for name in sheet_names:
            spreadsheet.add_worksheet(title=name, rows="100", cols="20")
    
    def create_table(self, base_name):
        unique_name = self.generate_unique_sheet_name(base_name)
        spreadsheet: Spreadsheet = self.client.create(title=unique_name)
        return spreadsheet
    
    def get_data_from_model(self, session, model):
        # Получение всех записей из модели
        data = session.query(model).all()
        # Преобразование данных в формат списка списков
        return [[getattr(row, column.name) for column in model.__table__.columns] for row in data]
    
    def get_headers_from_model(self, model: Type[Base]) -> List[str]:
        return [column.name for column in model.__table__.columns]
    
    def format_data_for_sheet(self, records):
        # Форматирование данных для записи в лист
        formatted_data = []
        for record in records:
            row = [getattr(record, column.name) for column in record.__table__.columns]
            formatted_data.append(row)
        return formatted_data
    
    def write_model_data_to_sheet(self, spreadsheet, model: Type[Base], session):
        records = self.get_data_from_model(session, model)
        data = self.format_data_for_sheet(records)
        headers = self.get_headers_from_model(model)
        sheet_name = model.__tablename__.capitalize()
        worksheet = spreadsheet.worksheet(sheet_name)
        worksheet.append_row(headers)  # Запись заголовков
        worksheet.append_rows(data)  # Запись данных
    
    def create_and_populate_sheets(self, base_name, session):
        spreadsheet = self.create_table(base_name)
        models = [User, Product, Order]
        for model in models:
            self.create_sheets(spreadsheet, [model.__tablename__.capitalize()])
            self.write_model_data_to_sheet(spreadsheet, model, session)


if __name__ == "__main__":
    service = GoogleSheetsService()
    spreadsheet: Spreadsheet = service.create_table("Test")
    # spreadsheet1 = service.create("Test")
    # print(spreadsheet)
    # print(spreadsheet1)
