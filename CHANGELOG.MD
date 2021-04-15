## 0.3 - 15-4-2021
### Changed
- Refactored architecture to MVC
- Using Signals and Slots

### Removed
- (Class) MerKeeper

### Added
- (Class) MerController: Updates view, Manipulates model
- (Class) MerModel: Changes View with Signals
- (Class) MerView: Contains only GUI elements now, Reads properties from Model

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


