## 0.3.4 - 3-5-2021
### Added
- (class) YardsToCoordinatesConverter: Converts yards to Degrees (non-converted positions)
- (class) DegreesToCoordinatesConverter: Converts degrees to coordinates (half-converted positions)

### Changed
- Changed PositionConverter to YardsToCoordinatesConverter
- Changed the order of conversions. Now all Converter convert sequentially
- 

### Removed

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
- Removed filenames from statusbar in MerView

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


