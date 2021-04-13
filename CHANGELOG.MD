## v0.2 - 06-04-2021
### Added
#### Classes
- MerFilter: Provides filter functionality for every dataframe of the MER
- Converter: Keeps a converting method and concerned columns so that all 
  converters can be applied in a loop

#### Functionalities
- A dataframe can now be filtered on column
- Filters can be toggled
- Columns can be toggled
- All Filters can be reset at once
- All columns can be toggled at once

#### Utilities
- README.MD

## Changed
- Converter functions are now in a class holding this function so that all functions  
have the same interface and can be applied by using a loop. New converter functions can be added easily now.

## v0.1 - 30-03-2021
### Added
#### Classes
- MerGui: Mainframe of the application
- MerKeeper: Keeps all MER data and MER dataframes
- MerTree: Provides navigation functionality through different dataframes  
  because one MER is split into several dataframes containing all info belonging to one event identifier  
- MerViewer: GUI for showing a dataframe in table structure
- Dataframe: Business logic for exploring a dataframe
  
#### Functionalities
- Import functionality for .txt and .zip files
- Navigating through dataframes of the MER using the MerTree navigation panel  

#### Utilities
- Converting datetime columns to one DATE and one TIME column
- Rename duplicate columns
- CHANGELOG.MD


