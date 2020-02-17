# Game Of Life

The Game of Life was invented in 1970 by the British mathematician John Horton Conway. It is the best-known example of a cellular automaton which is any system in which rules are  applied to cells and their neighbors in a regular grid.

This repository is my PyQt implementation of Conway's Game of Life, that follows the architectural pattern **Model-View-Controller**. 

![Game of Life Tool](images/app.gif)

## Game of Life Rules


![Game of Life population's evolution](images/GOL.png)

The game is played on a two-dimensional grid (or board). Each grid location is either empty (*Dead* cell) or populated (*Alive* cell) by a single cell. A location’s neighbors are any cells in the surrounding eight adjacent   locations. The simulation of starts from an initial state of populated locations and then progresses through time. The evolution of the board state is governed by a few simple rules:

* each populated location with one or zero neighbors dies (from *loneliness*);
* each populated location with four or more neighbors dies (from *overpopulation*);
* each populated location with two or three neighbors survives;
* each unpopulated location that becomes populated if it has exactly three populated neighbors.


## My Implementation

In the [Model](model.py) there are definitions and methods for managing application's data.

The [View](view.py) is the user interface.

The core part of the game is implemented in [Cell.py](Components/Cell.py), where is implemented the logic of any cells of the Game Of Life universe.


## Functionalities

![My Game of Life GUI](images/app_GUI.png)

### Play/Pause evolution and clear the board
The user can always start the evolution of the current Game of Life board. In every moment he can stop the cells' updates either clearing the universe (with the dedicate button) or simply stop it clicking on the appropriate icon. If the user wants to see just one update of the grid, he can use the tool bar menu (the green arrow) or the Edit menu choosing the Next action.

### Variable framerate
The user can set the framerate of the board evolution with a slider, that choice will affect the speed of the updates.

### Drawing and editing of state
The user can draw or edit the board state. If the interactions are done with left clicks (clicks or holding down the mouse), those will generate new alive cells. In the same way with right clicks the user will clear cells, that are dead.

### Save board state
Every board state can be saved by the user in multiple way: using the button in the bottom or choosing the save action that is in the File menu and in the tool bar menu. If the user select Save As option in the File menu, he can specifies the path where the data has to be saved.

### Choose initial board state
The user can choose the initial state of the board with a saved state or with a Game of Life pattern. Possible ways for loading previous state are the button in the bottom of the GUI, the open action in the tool bar (the folder icon) and in the File menu.

### Zooming of board
With the + and - buttons in the right bottom of the application, the user can zoom the board.

### Cell History
Selecting the appropiate check box, the user can observate the last five states of every cells in the board. Alive cells have different color: oldest alive cells got less color intensiry. 
For show just one state's history the user can click on the History action in the tool bar or in the Edit menu. 

# Playing Game of Life


Clone the repository and enjoy with Game of Life!

```sh
$ cd GameOfLife
$ python ./main.py
```

## Requirements

My implementation is tested with the following packages versions.

| Package | Version |
| ------ | ------ | 
| Python | 3.7 |
| PyQt | 5.9 | 
| numpy | 1.17 |


