class AppStrings:
    """Centralized strings for the application"""
    
    # Window Titles
    APP_TITLE = "SmashGen"
    
    # General Actions
    ACTION_ADD = "Add"
    ACTION_REMOVE = "Remove"
    ACTION_EDIT = "Edit"
    ACTION_ENABLE = "Enable"
    ACTION_DISABLE = "Disable"
    ACTION_GENERATE = "Generate"
    ACTION_DOWNLOAD = "Download"
    ACTION_CANCEL = "Cancel"
    ACTION_SAVE = "Save"
    ACTION_CLOSE = "Close"
    ACTION_SELECT_ALL = "Select All"
    ACTION_DESELECT_ALL = "Deselect All"
    ACTION_MORE = "More Actions"
    
    # Mod List / Batch Actions
    BATCH_GENERATE_TOOLTIP = "Generate Info.toml for Selected"
    BATCH_ENABLE_TOOLTIP = "Enable Selected"
    BATCH_DISABLE_TOOLTIP = "Disable Selected"
    BATCH_REMOVE_TOOLTIP = "Remove Selected"
    BATCH_GENERATE = "Generate Info.toml"
    
    # Dialogs
    DIALOG_TITLE_NO_SELECTION = "No Selection"
    DIALOG_MSG_NO_SELECTION = "Please select mods to process."
    DIALOG_TITLE_CONFIRM_DELETE = "Confirm Deletion"
    DIALOG_MSG_CONFIRM_DELETE = "Are you sure you want to permanently delete {count} selected mod(s)?\nThis action cannot be undone."
    DIALOG_TITLE_SYNC = "Sync Mods"
    DIALOG_MSG_SYNC = "This will delete any mods in the export folder that are disabled or removed, and copy all enabled mods.\nThis may take some time.\n\nContinue?"
    
    # Status / Progress
    STATUS_SEARCHING = "Searching GameBanana..."
    STATUS_FETCHING_DATA = "Fetching mod data..."
    STATUS_FETCHING_DESC = "Fetching description..."
    STATUS_DATA_FETCHED = "Data fetched successfully"
    STATUS_USING_EXISTING_URL = "Using existing URL"
    STATUS_LOADING = "Loading..."
    STATUS_LOADING_DETAILS = "Loading details..."
    STATUS_EXPORTING = "Exporting..."
    STATUS_EXPORTING_PERCENT = "Exporting... {percent}%"
    
    # Workspace
    LBL_EXPORT_BUTTON = "Export Enabled Mods ({count})"
    WARN_CONFIG_DIRS = "<b>Warning:</b> Directories not set.<br><a href='config' style='color: {color};'>Open Config</a>"
    TOOLTIP_EXPORT_INVALID = "Export directory is invalid or not set in Config"
    TOOLTIP_WORKSPACE_EXPORTING = "Exporting: {message}"
    
    # Preview / Details
    LBL_WIFI_SAFE = "Wifi-Safe"
    LBL_NOT_WIFI_SAFE = "Not Wifi-Safe"
    LBL_MOVESET = "Moveset"
    LBL_FINAL_SMASH = "Final Smash"
    LBL_UNKNOWN_MOD = "Unknown Mod"
    
    # Context Menu
    CTX_OPEN_FOLDER = "Open Folder"
    CTX_OPEN_WEB = "Open Web Page"
    CTX_COPY_ID = "Copy Mod ID"
    CTX_MOD_OPTIONS = "Mod Options"
    CTX_DOWNLOAD_ALL = "Download All"
    
    # Assignments
    HEADER_ASSIGNMENTS = "{entity} Assignments"
    PLACEHOLDER_SELECT_ENTITY = "Select Entity"
    PLACEHOLDER_SELECT_SLOTS = "Select Slots"
    TOOLTIP_ADD_ROW = "Add Assignment Row"
    
    # Dates / Time
    TIME_JUST_NOW = "Just now"
    TIME_DAYS_AGO = "{days}d"
    TIME_WEEKS_AGO = "{weeks}w"
    TIME_MONTHS_AGO = "{months}mo"
    TIME_YEARS_AGO = "{years}y"
    TIME_HOURS_AGO = "{hours}h"
    TIME_MINUTES_AGO = "{minutes}m"
    
    # Misc
    TXT_UNKNOWN = "Unknown"
    
    # Errors
    ERR_GAMEBANANA_NOT_FOUND = "Could not find mod on GameBanana"
    ERR_FETCH_FAILED = "Failed to fetch mod data"
    ERR_ROOT_DIR_NOT_SET = "Root directory is not set in Config. Please set it before adding mods."
    
    # Navigation / Tabs
    NAV_INSTALLED = "Installed"
    NAV_ONLINE = "Online"
    
    # Add Menu
    ADD_FROM_FOLDER = "Add from Folder..."
    ADD_FROM_ZIP = "Add from ZIP..."
