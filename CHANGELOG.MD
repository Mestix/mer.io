## 1.0 - 29-6-2021
### Added
- (class) SonarPlanConverter for converting sonar plan 44

## 0.6 - 27-6-2021
## Added
- Help dialog with instruction manual
- Save theme settings locally

## Changed
- Fixed the bug where the import menu stayed disabled when all tasks finished
- Save environment settings in json

## Removed
- Removed column-rename functions from converters because this causes error sensitivities in the presets
- Removed MWC preset (this was only for test purposes)

## 0.5 - 24-6-2021
### Added
- (class) DegreesConverter for formatting degree values
- (class) ReferenceConverter for removing reference column
- (class) SonicConverter for composing Sonic data and additional columns
- (class) TimeConverter for converting Time and Duration columns
- (class) YardsToNMConverter for converting yard columns to Nautical Mile

### Changed
- Changed formatting for positions (it was not correct before)
- Removed index while exporting to Excel
- Changed the way a reference is set (use date/time cols instead of filename)
- Changed the way Mers ae removed from bulk export when skipping option is on
- Added some extra regex expressions for determining numeric columns while importing Mer

### Removed
- Themes, app has only one light and dark theme now

## 0.4 - 17-5-2021
### Added
- /src/assets/presets folder for adding json presets
- Added preset retrieval to ExportModule which Converts json preset to python dict and transforms DataFrame according to preset before exporting.
- (class) ColumnNotFoundException: Raises when the preset has a column value which is not in the DataFrame
- (class) IdentifierNotFoundException: Raises when the preset has an identifier which is not in the DataFrame
- Upgrade Code GUID to setup.py for automatically uninstall old versions of the program when installing

### Changed
- Separated utility methods to the folder which the utility methods belong to. Each folder has now its own utility file.
- Removed reference to Explorer and DataFrameViewer from DataFrameModel. DataFrameModel just emits signal now when changed.
- BulkHandler and FileHandler now keep lists of running tasks. When a task is finished, it gets removed from this list and garbage collected.

### Removed
- (class) MerModel: MerModel class became so little that it could just be a Dictionary in MerController

## 0.3.6 - 6-5-2021
### Added
- Themes

### Changed
- TreeView is now ListView and called IdentifierView
- Searching for identifiers, replaces underscores for spaces (no need to add underscores anymore)

## 0.3.5 - 5-5-2021
### Added
- Logger
- (class) BulkHandler: for importing, converting and exporting multiple mers from a directory at once
- (class) ExportModule: for handling export functionality on thread
- (class) FileHandler: for handling mer imports that should show on screen
- Status messages in status bar

### Changed
- MerController has now both bulk and file handlers.
- MerController is now only responsible for connecting signals between model, view and handlers
- While bulk export tasks are running, single file import is been disabled because the program will get very slow


## 0.3.4 - 3-5-2021
### Added
- (class) YardsToCoordinatesConverter: Converts yards to Degrees (non-converted positions)
- (class) DegreesToCoordinatesConverter: Converts degrees to coordinates (half-converted positions)
- Version number to window title

### Changed
- Changed PositionConverter to YardsToCoordinatesConverter
- Changed the order of conversions. Now all Converters convert sequentially

## 0.3.3 - 3-5-2021
### Added
- Added Setter for DataFrameModel df_unfiltered which now automatically changes df as well
- Added a REFERENCE column to DataFrame for recognizing to which Mer a column belongs (for adding multiple mers)

### Changed
- Moved tactical scenario verification and mocking to Mer Controller
- PositionConverter now converts data based on the Tactical Scenario from which mer the data belongs to  
  (previously it was just picking the first occurrence of a tactical scenario)

### Removed
- Removed continue_without_tact_scenario signal from MerView
- Removed tactical scenario and names property from MerModel
- Removed filenames from status bar in MerView

## 0.3.2 - 30-4-2021
### Added
- (class) ConvertModule: for separating import and convert functionality
- (class) IImporter: interface for expanding import formats
- (class) BinaryImporter: Empty class for holding future Binary import functionality
- (class) TextImporter: Import a mer text import and convert it to an intern DataFrame Model without any data conversions
- Added a few custom Exceptions

## 0.3.1 - 30-4-2021
### Added
- (class) IConverter: interface for expanding converters
- (class) PositionConverter: Converts positions in yards to coordinates 

## 0.3 - 21-4-2021
### Added
- (func) Add checkboxes to Identifier tree for selecting Identifiers for export  
- (func) Add a Select All Checkbox above Identifier tree for selecting and deselecting all Identifiers at once    
- (func) Export selected identifiers with data to excel
- (func) Select destination folder for export
- (func) Give a name for export file
- (Class) ImportState enum
- (Class) MerController: Updates view, Manipulates model
- (Class) MerModel: Changes View with Signals
- (Class) MerView: Contains only GUI elements now, Reads properties from Model

### Changed
- (func) Changed Toggle buttons in Filter form to Checkbox
- (Misc) Moved all Mer/DataFrame creation func to Thread
- Refactored architecture to MVC
- Using Signals and Slots

### Removed
- Removed different import signals from MerController  
  Replaced them for one import signal with an Enum ImportState  
- (Class) MerKeeper

## v0.2 - 06-04-2021
### Added
- (Class) MerFilter: Provides filter functionality for every dataframe of the MER
- (Class) Converter: Keeps a converting method and concerned columns so that all 
  converters can be applied in a loop
- (Func) A dataframe can now be filtered on column
- (Func) Filters can be toggled
- (Func) Columns can be toggled
- (Func) All Filters can be reset at once
- (Func) All columns can be toggled at once

#### Utilities
- README.MD

## Changed
- Converter functions are now in a class holding this function so that all functions  
have the same interface and can be applied by using a loop. New converter functions can be added easily now.

## v0.1 - 30-03-2021
### Added
- (Class) MerGui: Mainframe of the application
- (Class) MerKeeper: Keeps all MER data and MER dataframes
- (Class) MerTree: Provides navigation functionality through different dataframes  
  because one MER is split into several dataframes containing all info belonging to one event identifier  
- (Class) MerViewer: GUI for showing a dataframe in table structure
- (Class) Dataframe: Business logic for exploring a dataframe
- (Func) Import functionality for .txt and .zip files
- (Func) Navigating through dataframes of the MER using the MerTree navigation panel
- (Func) Converting datetime columns to one DATE and one TIME column
- (Func) Rename duplicate columns
- (Misc) CHANGELOG.MD


