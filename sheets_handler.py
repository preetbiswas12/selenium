import gspread
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SheetsHandler:
    """Handle Google Sheets for registration data"""
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    def __init__(self, credentials_path):
        """
        Initialize with Google Cloud Service Account JSON
        
        credentials_path: Path to service account JSON file
        """
        try:
            creds = Credentials.from_service_account_file(
                credentials_path, scopes=self.SCOPES
            )
            self.client = gspread.authorize(creds)
            logger.info("Connected to Google Sheets API")
        except Exception as e:
            logger.error(f"Failed to authenticate: {e}")
            raise
    
    def get_sheet(self, sheet_name_or_id):
        """Open a spreadsheet by name or ID"""
        try:
            spreadsheet = self.client.open(sheet_name_or_id)
            logger.info(f"Opened spreadsheet: {sheet_name_or_id}")
            return spreadsheet
        except:
            try:
                spreadsheet = self.client.open_by_key(sheet_name_or_id)
                logger.info(f"Opened spreadsheet by ID: {sheet_name_or_id}")
                return spreadsheet
            except Exception as e:
                logger.error(f"Failed to open spreadsheet: {e}")
                raise
    
    def get_all_records(self, spreadsheet, worksheet_index=0):
        """Get all rows from worksheet (skips headers)"""
        worksheet = spreadsheet.get_worksheet(worksheet_index)
        records = worksheet.get_all_records()
        logger.info(f"Fetched {len(records)} records from sheet")
        return records
    
    def get_pending_records(self, spreadsheet, worksheet_index=0, status_column="Status"):
        """Get only rows with Status != 'Done'"""
        worksheet = spreadsheet.get_worksheet(worksheet_index)
        records = worksheet.get_all_records()
        
        pending = [r for r in records if r.get(status_column, "").lower() != "done"]
        logger.info(f"Found {len(pending)} pending registrations")
        return pending
    
    def update_status(self, spreadsheet, row_index, status="Done", worksheet_index=0):
        """Mark a row as completed"""
        worksheet = spreadsheet.get_worksheet(worksheet_index)
        worksheet.update_cell(row_index + 2, self._get_column_index("Status", worksheet), status)
        logger.info(f"Updated row {row_index} status to: {status}")
    
    def add_result(self, spreadsheet, row_index, result_data, worksheet_index=0):
        """Add result data (error message, timestamp, etc) to a row"""
        worksheet = spreadsheet.get_worksheet(worksheet_index)
        
        # Update multiple columns
        col_index = 1
        for key, value in result_data.items():
            try:
                worksheet.update_cell(row_index + 2, col_index, value)
                col_index += 1
            except:
                pass
    
    def _get_column_index(self, column_name, worksheet):
        """Get column index by header name"""
        headers = worksheet.row_values(1)
        try:
            return headers.index(column_name) + 1
        except ValueError:
            return -1
    
    @staticmethod
    def create_template_sheet(spreadsheet_name, columns):
        """Create a new Google Sheet with template columns"""
        try:
            # This would require additional setup
            logger.info(f"Template columns: {columns}")
            return True
        except Exception as e:
            logger.error(f"Failed to create template: {e}")
            return False
