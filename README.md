# Checker AI with Monte Carlo Tree Search  

This is repository containing the code for playing checkers using Monte-Carlo-Tree-Search (MCTS). 
The package contains the code for:
* Simulating the board
* Training the MCTS agent
* Playing the MCTS agent against a random player
* Playing the MCTS agent against a human player

Here is an example of the MCTS performance after training on only 50 games of self play:

MCTS vs. Random Player           |  MCTS vs. Human Player
:-------------------------------:|:--------------------------------:
![](./videos/mcts_vs_random.gif) | ![](./videos/mcts_vs_player.gif)

## Installation

```
conda create --name myenv python=3.7 
conda activate myenv
git clone https://github.com/hemerson1/MCTS-Checkers.git
cd RLcycle
pip install -U -r requirements.txt
pip install -e .
```

## Licence

[MIT](https://choosealicense.com/licenses/mit/)
