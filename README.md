# pentago-python

[Pentago](https://en.wikipedia.org/wiki/Pentago) game implementation in Python with Q-learning and eventually also image recognition with the help of a webcam.


Definition and rules from Wikipedia :

> Pentago is a two-player abstract strategy game invented by Tomas Flodén. The Swedish company Mindtwister has the rights of developing and commercializing the product. The game is played on a 6×6 board divided into four 3×3 sub-boards (or quadrants). Taking turns, the two players place a marble of their color (either black or white) onto an unoccupied space on the board, and then rotate one of the sub-boards by 90 degrees either clockwise or anti-clockwise. A player wins by getting five of their marbles in a vertical, horizontal or diagonal row (either before or after the sub-board rotation in their move). If all 36 spaces on the board are occupied without a row of five being formed then the game is a draw."




## Installation

- Clone this repo
- Run `make install` to install dependencies
- Run `make start` to start the game
-You need to train the model a minimum of 50000 times before you can use it. Offcourse, it gets better over time.
-Adjust exploration_rate to 0 for competitive use or 1 to keep training during tests.
