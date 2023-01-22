import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

from typing import List
from dotenv import load_dotenv
import os
from random import randrange
import exceptions


load_dotenv()

class GoogleSh:
    def __init__(self, range: str = None):        
        self.range = range
        self.service = self._get_service()
        self.sheet_id = os.environ.get('spreadsheet_id')
    
    @staticmethod
    def _get_service():
        CREED_FILE = 'creed2.json'
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            CREED_FILE, 
            'https://www.googleapis.com/auth/spreadsheets'    
        )
        credentials_gc = ServiceAccountCredentials.from_json_keyfile_name(
            CREED_FILE, 
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'    
        )
        httpAuth = credentials.authorize(httplib2.Http())
        service = build('sheets', 'v4', http = httpAuth)
        return service
             
    def create_sheet(self):
        spreadsheet = service.spreadsheats().create(
            body={
                'properties': {'title': 'Time&Money Managment'},
                'sheets': {'properties': {
                    'sheetType': 'GRID',
                    'sheetId': 0,
                    'title': 'Time&Money Managment',
                    'gridproperties': {'rowcount': 8, 'columncount':5}
                }
            }
        }).execute()
        
    def _create_codename_colomns(self):
        result = service.spreadsheets().values().batchUpdate(spreadsheetId=self.sheet_id, body={
        "valueInputOption": "USER_ENTERED",
        "data": [
            {"range": "Sheet1!A4:E4",
            "majorDimension": "ROWS",    
            "values": [['Num', "Category", "Value", "Cost", "Date"]]},
        ]
        }).execute()
        return result
       
    def add(self, amount, date, name, category, raw_message):
        Num = _num_column()
        range = int(Num) + 4
        result = service.spreadsheets().values().batchUpdate(spreadsheetId=self.sheet_id, body={
        "valueInputOption": "USER_ENTERED",
        "data": [
            {"range": f"Sheet1!A{range}:F{range}",
            "majorDimension": "ROWS", 
            "values": [[f'{Num}', f"{category}", f"{name}", f"{amount}", f"{date}", f"{raw_message}"]]},
        ]
        }).execute()
        return result    
       
    def get(self) -> List:
        try:
            values = service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=self.range,
                majorDimension='ROWS'
            ).execute()
            return values
        except exceptions.InvalidRequest as e:
            raise e 
        
    def dlt(self, row_id):
        range = row_id + 4
        
        result = service.spreadsheets().values().batchUpdate(spreadsheetId=self.sheet_id, body={
        "valueInputOption": "USER_ENTERED",
        "data": [
            {"range": f"Sheet1!A{range}:F{range}",
            "majorDimension": "ROWS", 
            "values": [['', '', '', '', '', '']]},
        ]
        }).execute()
            
        return result 
            
    def get_values(self):
        try:
            request_body = {
                'value_render_option': 'FORMATTED_VALUE',
                'data_filters': [] ,
                'date_time_render_option': ''
            }
            values = service.spreadsheets().values().batchGetByDataFilter(
                spreadsheetId=self.sheet_id,
                body=request_body).execute()
            return values
        except exceptions.InvalidRequest as e:
            raise e
            
           
service = GoogleSh._get_service()

def random_color() -> dict:
    return {
        "red": randrange(0, 255) / 255,
        "green": randrange(0, 255) / 255,
        "blue": randrange(0, 255) / 255,
        "alpha": randrange(0, 10) / 10 
    }
   

def _load_categories():
    values = {
        "Products": ['meat', 'fruits', 'vegetables', 'food', 'products', 'eggs', 'water'],
        "Communal payments": ['gas', 'electricity', 'water_payments', 'garbage', 'communal'],
        "Car expenses": ['buy car', 'machine parts', 'car', 'work car'],
        "Professional expenses": ['book', 'notebooke', 'tab', 'computer', 'reader'],
        "Taxes": ['budget', 'taxes'],
        "Enterteiment expenses": ['film', "concert", 'mcdonalds', 'cafe', 'restoran','gallery', 'theater','coffe'],
        "Medical expenses": ['tablets', 'doctor', 'analyzes'],
        "Child expenses": ['school'],
        "Telecommunication expenses": ['telephone', 'internet', 'tv'],
        "Other expenses": []
    } 
    return values

        
def _get_last_id():
    try:
        values = GoogleSh('A:A').get()
        *_, value_num = values['values'][-1]
        return value_num
    except exceptions.InvalidRequest as e:
        raise e      


def _num_column():
    try:
        num = int(_get_last_id())
    except:
        num = 0        
    num += 1
    return num


def _get():
    values = GoogleSh('A:F').get()
    return values['values'][3:]


def _search(id):
    results = GoogleSh('A:F').get()
    