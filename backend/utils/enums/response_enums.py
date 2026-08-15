from enum import Enum

class ResponseSignals(Enum):

    # Validation Responses
    INVALID_FILE_TYPE = 'Invalid File Type'
    INVALID_FILE_SIZE = 'File Size Too Large'
    INVALID_TRANSLATION_LANGUAGE = 'Invalid Translation Language'
    INVALID_EMPTY_TEXT = 'Invalid Empty Text'
    INVALID_LONG_TEXT = 'Text Too Long'
    VALID_FILE = 'Valid File'
    VALID_TEXT = 'Valid Text'

    # General Responses
    SUCCESS_UPLOAD = 'File Uploaded Successfully'
    FAILED_UPLOAD = 'Failed to Upload File'
    FAILED_SAVING = 'Failed to save file'
    PAPER_FILE_NOT_FOUND = 'Paper File Not Found'
    SUMMARY_FILE_NOT_FOUND = 'Summary File Not Found'

    # Paper Responses
    PAPER_NOT_FOUND = "Paper Not Found"
    PAPER_EXISTS = 'Paper Already Exists'
    PAPER_DISPLAY_ERROR = 'Failed To Display Paper'
    PAPER_UPDATE_SUCCESS = 'Paper Updated Successfully'
    PAPER_UPDATE_ERROR = 'Failed to Update Paper'
    PAPER_RENAME_SUCCESS = 'Paper Renamed Successfully'
    PAPER_RENAME_ERROR = 'Failed to Rename Paper'

    # Chunk Responses
    NO_CHUNKS_CREATED = 'No Chunks Created'
    NO_PAPER_CHUNKS = "No Paper Chunks Founded"

    # Project Responses
    PROJECT_CREATED_SUCCESS = 'Project Created Successfully'
    PROJECT_UPDATED_SUCCESS = 'Project Updated Successfully'
    PROJECT_NOT_FOUND = 'Project Not Found'
    PROJECT_CREATION_FAILED = 'Failed to Create Project'
    PROJECT_RENAME_FAILED = 'Failed to Rename Project'

    #Vector DB Responses
    VDB_CONNECTION_ERROR = 'Failed to Connect to Vector DB'
    VDB_INSERT_ERROR = 'Failed to Insert Into Vector DB'
    VDB_INSERT_SUCCESS = 'Inserted Into Vector DB Successfully'
    VDB_INFO_RETRIEVED_SUCCESS = 'Vector DB Collection Retrieved Successfully'
    VDB_INFO_RETRIEVED_ERROR = 'Failed to Retrieve Vector DB Collection Info'
    VDB_SEARCH_ERROR = 'Failed to Search Vector DB'
    VDB_SEARCH_SUCCESS = 'Vector DB Search Successful'
    VDB_NO_SEARCH_RESULTS = 'No Results Found in Vector DB'
    VDB_UNSUPPORTED_PROVIDER = 'Unsupported Vector DB Provider'
    VDB_COLLECTION_NOT_FOUND = 'Vector DB Collection Not Found'

    #RAG Responses
    RAG_ANSWER_ERROR = 'Failed to Generate Answer'
    RAG_NO_ANSWER = 'No Answer Generated'
    RAG_ANSWER_SUCCESS = 'Answer Generated Successfully'

    #Summary Responses
    SUMMARY_NOT_FOUND = 'Summary Not Found'
    SUMMARY_GENERATION_FAILED = 'Failed to Generate Summary'
    SUMMARY_GENERATION_SUCCESS = 'Summary Generated Successfully'
    SUMMARY_EXISTS = 'Summary Already Exists for this Paper'
    SUMMARY_DISPLAY_ERROR = 'Failed to Display Summary'
    SUMMARY_UPDATE_ERROR = 'Failed to Update Summary'
    SUMMARY_UPDATE_SUCCESS = 'Summary Updated Successfully'
    SUMMARY_RENAME_SUCCESS = 'Summary Renamed Successfully'
    SUMMARY_RENAME_ERROR = 'Failed to Rename Summary'

    # Translator Responses
    TRANSLATION_SUCCESS = 'Text Translated Successfully'
    TRANSLATION_ERROR = 'Failed to Translate Text'

    # Explanation Responses
    EXPLANATION_SUCCESS = 'Text Explained Successfully'
    EXPLANATION_ERROR = 'Failed to Explain Text'
