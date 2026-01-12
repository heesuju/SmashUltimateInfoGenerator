# SmashUltimateInfoGenerator - Technical Documentation

## Project Overview

**SmashUltimateInfoGenerator** (SmashGen) is a PyQt6-based mod manager for Super Smash Bros. Ultimate that automatically generates `info.toml` files for mods. The application scans mod folders, detects included elements (skins, effects, sounds, etc.), and creates standardized metadata files following the `info.toml` format used by the Arcropolis mod loader.

## Architecture

### Entry Point

The application starts in [`main.py`](file:///c:/DEV/SmashUltimateInfoGenerator/main.py):

```python
QApplication → ConfigManager → MainMenu → show()
```

1. Creates a PyQt6 `QApplication`
2. Initializes `ConfigManager` to load user settings
3. Applies the selected theme (dark/light) via `qdarktheme`
4. Creates and displays the `MainMenu` window

### Project Structure

```
SmashUltimateInfoGenerator/
├── main.py                 # Application entry point
├── data/                   # Data files and cache
│   ├── character_data.csv  # Character names and metadata
│   ├── item_names.csv      # Item definitions
│   └── cache/              # Saved configuration
├── src/
│   ├── constants/          # Enums, strings, styles, UI parameters
│   ├── core/               # Business logic
│   │   ├── scanner.py      # Mod directory scanner
│   │   ├── mod_loader.py   # Async mod loading with threading
│   │   ├── formatting.py   # String formatting utilities
│   │   ├── data.py         # TOML generation and file operations
│   │   └── web/            # Web scraping for GameBanana
│   ├── managers/           # State management
│   │   ├── config_manager.py   # User configuration
│   │   ├── mod_manager.py      # Mod collection and selection
│   │   ├── filter_manager.py   # Filtering state
│   │   └── data_manager.py     # Character/item data access
│   ├── models/             # Data models (Pydantic)
│   │   ├── mod.py          # Mod and Character models
│   │   └── settings.py     # Application settings
│   ├── ui/                 # PyQt6 UI components
│   │   ├── main_menu.py    # Main window
│   │   ├── mod_list.py     # Mod list/grid view
│   │   ├── edit_panel.py   # Mod editing panel
│   │   ├── filter_panel.py # Filtering controls
│   │   ├── preview_panel.py# Mod preview
│   │   └── components/     # Reusable UI widgets
│   └── utils/              # Utility functions
│       ├── toml.py         # TOML read/write operations
│       ├── file.py         # File system operations
│       ├── csv_helper.py   # CSV parsing
│       └── hash.py         # Hash generation for mod IDs
└── assets/                 # Images and resources
```

## Core Workflow

### 1. Mod Scanning Process

#### Trigger
User selects a root directory containing mod folders → `ModManager.scan_all()` is called

#### Flow
```
ModManager.scan_all()
  ↓
ModLoader (with ThreadPool for parallel processing)
  ↓
For each mod folder:
  ├─ ModWorker.run()
  ├─ load_toml() - Check for existing info.toml
  ├─ scan_mod() - Analyze directory structure
  │   ├─ scan_character() - Detect fighters and slots
  │   ├─ scan_fighter() - Check for skins/motion/kirby hat
  │   ├─ scan_effect() - Detect effect files
  │   ├─ scan_sound() - Find voice/sfx/narrator
  │   ├─ scan_ui() - Detect UI and name changes
  │   ├─ scan_stage() - Check for stage mods
  │   ├─ scan_item() - Detect item mods
  │   ├─ scan_stream() - Victory theme detection
  │   ├─ scan_camera() - Victory animation detection
  │   └─ scan_thumbnail() - Look for preview.webp
  ├─ Auto-generate display_name, mod_name, category
  └─ emit(mod) → ModManager.on_progress()
```

#### Scanner Deep Dive ([`scanner.py`](file:///c:/DEV/SmashUltimateInfoGenerator/src/core/scanner.py))

The scanner uses pattern matching and directory traversal to detect mod contents:

**Character Detection:**
- Scans `fighter/` and `effect/fighter/` directories
- Extracts fighter names (e.g., "mario", "sonic")
- Detects slot numbers from folders like `c00`, `c01`, `c02` (costume slots)
- Checks for actual model files vs. recolors
- Creates `Character` objects with `Fighter` enum and slot list

**Element Detection:**
- Searches directory trees for specific keywords
- Analyzes file extensions (`.eff`, `.msbt`, `.xmsbt`)
- Uses regex patterns to differentiate between:
  - Single-slot effects vs. all-slot effects
  - Custom names vs. single custom names
  - Skin mods vs. simple recolors

**Category Assignment:**
- Automatically categorizes based on detected elements:
  - `FIGHTER` - Has skin/motion/recolor
  - `STAGE` - Contains stage files
  - `EFFECTS` - Only effect files
  - `AUDIO` - Voice/sound/narrator
  - `UI` - UI replacements
  - `MISC` - Everything else

### 2. Data Models

#### Mod Model ([`models/mod.py`](file:///c:/DEV/SmashUltimateInfoGenerator/src/models/mod.py))

```python
class Mod(BaseModel):
    display_name: str        # User-friendly name
    description: str         # Mod description
    authors: str            # Creator names
    category: Category      # Fighter/Stage/Effects/etc.
    version: str            # Semantic version (1.0.0)
    mod_name: str           # Cleaned mod name
    url: str                # GameBanana URL
    wifi_safe: Wifi         # Safe/Uncertain/Unsafe
    folder_name: str        # Target folder name
    path: str               # Current directory path
    thumbnail: str          # Preview image path
    hash: str               # Unique identifier
    characters: list[Character]  # Fighters and slots
    includes: list[Element] # Detected elements
    contains_info: bool     # Has existing info.toml
    is_selected: bool       # UI selection state
```

#### Character Model
```python
class Character(BaseModel):
    fighter: Fighter        # Fighter enum (MARIO, SONIC, etc.)
    slots: list[int]        # Costume slots [0, 1, 2, ...]
```

### 3. Name Formatting ([`formatting.py`](file:///c:/DEV/SmashUltimateInfoGenerator/src/core/formatting.py))

The application provides sophisticated name formatting:

**Display Name Generation:**
- Template: `{characters} {slots} {mod} {category}`
- Example: `Sonic C01 Shadow`
- Removes redundant information
- Groups characters by series (e.g., "Pokemon Trainer" instead of listing all 3)

**Mod Name Extraction:**
- Strips character names from folder name
- Removes slot numbers
- Cleans special characters
- Removes "over" prefix patterns
- Handles camel case splitting
- Example: `Sonic_C01_Shadow_The_Hedgehog` → `Shadow The Hedgehog`

**Folder Name Cleaning:**
- Removes blacklisted characters (Windows incompatible)
- Trims consecutive delimiters
- Removes empty brackets
- Example: `Fighter_Sonic[C01]_Shadow`

**Slot Formatting:**
- Converts `[0, 1, 2, 5, 6, 7]` → `C00-02,05-07`
- Detects consecutive ranges
- Uppercase/lowercase options

### 4. UI Architecture ([`ui/main_menu.py`](file:///c:/DEV/SmashUltimateInfoGenerator/src/ui/main_menu.py))

The main window uses a horizontal layout:

```
┌─────────────────────────────────────────┬──────┐
│ ModList                │ SidePanel       │ Nav  │
│ (List/Grid View)       │ (Conditional)   │ Menu │
│                        │                 │      │
│ - Thumbnails           │ FilterPanel     │ [F]  │
│ - Mod names            │ PreviewPanel    │ [P]  │
│ - Categories           │ EditPanel       │ [E]  │
│ - Checkboxes           │ ConfigPanel     │      │
│                        │                 │ [C]  │
└────────────────────────┴─────────────────┴──────┘
```

**Components:**
- **ModList**: Displays all mods in list or grid layout with filtering
- **FilterPanel**: Filter by character, category, elements, wifi safety, etc.
- **PreviewPanel**: Shows mod details and metadata
- **EditPanel**: Edits mod properties, fetches data from GameBanana
- **ConfigPanel**: Application settings (theme, formats, directories)
- **Navigation**: Icon-based sidebar to switch panels

**State Management:**
- `ModManager`: Holds mod collection, tracks selection/focus
- `FilterManager`: Stores active filter parameters
- `ConfigManager`: Persists user settings to JSON

### 5. TOML Generation ([`core/data.py`](file:///c:/DEV/SmashUltimateInfoGenerator/src/core/data.py))

When the user clicks "Apply":

```python
generate_toml(mod: Mod):
    1. mod.to_dict() - Convert Mod to dictionary (excludes internal fields)
    2. dump_toml(mod.path, data) - Write info.toml to mod directory
    3. rename_folder(old_path, new_path) - Rename folder to match folder_name
```

**Batch Generation:**
- Uses `ThreadPoolExecutor` for parallel processing
- Generates info.toml for multiple selected mods
- Reports completion count

### 6. GameBanana Integration ([`core/web/`](file:///c:/DEV/SmashUltimateInfoGenerator/src/core/web/))

The application can scrape GameBanana mod pages to auto-fill metadata:

**Features:**
- Extract mod name from page title
- Get author names
- Fetch mod description
- Download preview images
- Retrieve version information
- Check NSFW flag
- Determine wifi safety

**Implementation:**
- Uses Selenium WebDriver for JavaScript-heavy pages
- Falls back to static scraping with BeautifulSoup when possible
- Singleton pattern for WebDriver management
- Threaded scraping to avoid blocking UI

### 7. Character Data Management

**Character CSV (`data/character_data.csv`):**
```
Key,Value,Custom,Group,Alt,Gender
mario,Mario,Mario,,,
luigi,Luigi,Luigi,,,
peach,Peach,Peach,,,
ptrainer,Pokemon Trainer,Pokemon Trainer,Pokemon,,
pzenigame,Squirtle,Squirtle,Pokemon,ptrainer,
```

**DataManager ([`managers/data_manager.py`](file:///c:/DEV/SmashUltimateInfoGenerator/src/managers/data_manager.py)):**
- Loads CSV data once at startup
- Provides lookup methods for character names, groups, icons
- Handles character grouping (e.g., Pokemon Trainer includes Squirtle/Ivysaur/Charizard)
- Supports gender variants (e.g., "Robin.M", "Robin.F")

## Key Technologies

- **PyQt6**: Modern Qt6 bindings for desktop UI
- **qdarktheme**: Dark/light theme support
- **Pydantic**: Data validation and modeling
- **tomli/tomli_w**: TOML parsing and writing
- **Selenium**: Web scraping for GameBanana
- **ThreadPoolExecutor**: Parallel mod scanning and TOML generation

## Multi-threading Strategy

1. **Mod Loading**: `QThreadPool` with `ModWorker` runnables
   - Each mod folder scanned in parallel
   - Signals emitted for progress updates
   - UI remains responsive during scan

2. **Web Scraping**: Separate threads for GameBanana requests
   - `ScraperThread` extends `QThread`
   - Prevents UI freezing during network operations

3. **Batch Operations**: `concurrent.futures` for TOML generation
   - Processes multiple mods simultaneously
   - Reports aggregate results

## Configuration Persistence

**Settings Model ([`models/settings.py`](file:///c:/DEV/SmashUltimateInfoGenerator/src/models/settings.py)):**
- Saved as JSON in `data/cache/`
- Includes:
  - Root directory path
  - Display name format template
  - Folder name format template
  - Default theme
  - List layout preference
  - Workspace selection

**ConfigManager:**
- Loads settings on startup
- Provides getters for config values
- Saves changes back to JSON

## Enums and Constants

**Category**: Fighter, Stage, Effects, UI, Param, Audio, Misc

**Element**: Skin, Recolor, Motion, Effect, Voice, SFX, Narrator, Custom Name, UI, Kirby Hat, Stage, Item, Moveset, Final Smash, Victory Theme, Victory Animation

**Fighter**: All 89 Smash Ultimate fighters with internal IDs (mario, sonic, ptrainer, etc.)

**Wifi**: Safe, Uncertain, Not Safe

## File System Operations

**Key Utilities ([`utils/file.py`](file:///c:/DEV/SmashUltimateInfoGenerator/src/utils/file.py)):**
- `is_valid_dir()`: Check directory existence
- `is_valid_file()`: Check file existence
- `get_children()`: List subdirectories
- `get_children_by_extension()`: Recursive file search by extension
- `search_dir_by_keyword()`: Find directories containing keyword
- `search_files_for_pattern()`: Regex pattern matching in filenames
- `rename_folder()`: Safe folder renaming with conflict detection
- `copy_file()`: File copying operations

## Common Workflows

### Workflow 1: First Time Setup
1. User launches application
2. Selects root mod directory in ConfigPanel
3. Application scans all mod folders
4. Displays mods in ModList with auto-detected metadata

### Workflow 2: Edit Existing Mod
1. User selects mod from ModList
2. Clicks Edit icon in Navigation
3. EditPanel shows current mod data
4. User can:
   - Paste GameBanana URL and click "Get" to auto-fill
   - Manually edit fields
   - Change characters, slots, category
   - Update description
5. Click "Apply" to:
   - Generate `info.toml` in mod folder
   - Rename folder to match new folder_name

### Workflow 3: Batch Processing
1. User filters mods (e.g., all Fighter mods without info.toml)
2. Selects multiple mods via checkboxes
3. Clicks batch action
4. Application generates info.toml for all selected mods in parallel

### Workflow 4: Filter and Search
1. User opens FilterPanel
2. Sets filters:
   - Character (multi-select)
   - Category
   - Elements (must include X)
   - Slot range
   - Has info.toml
   - Wifi safety
3. ModList updates in real-time
4. Can favorite, hide, or enable/disable filtered mods

## Design Patterns

1. **Manager Pattern**: Centralized state management (`ModManager`, `ConfigManager`, `FilterManager`)
2. **Observer Pattern**: Callbacks for state changes (`add_focus_callback`, `set_callback`)
3. **Singleton Pattern**: `WebdriverSingleton` for shared browser instance
4. **Worker Pattern**: `ModWorker` runnables for async operations
5. **Model-View Pattern**: Pydantic models separated from UI components

## Error Handling

- TOML parsing errors: Falls back to empty mod, logs error
- File access errors: Permission and file-not-found handling in all file operations
- Web scraping failures: Graceful degradation, error signals to UI
- Invalid directory: Skips invalid mod folders during scan

## Future Extensibility

The architecture supports future enhancements:
- Additional scan targets (new element types)
- Custom formatting templates (user-defined)
- Plugin system for custom scanners
- Export to other mod manager formats
- Cloud sync for mod collections
- Automatic update detection via GameBanana API

## Summary

SmashUltimateInfoGenerator is a well-architected PyQt6 application that automates the tedious process of creating mod metadata files. It combines intelligent directory scanning, web scraping, and a polished UI to help mod managers organize large collections of Super Smash Bros. Ultimate mods efficiently. The use of threading, Pydantic models, and centralized state management makes the codebase maintainable and performant even with hundreds of mods.
