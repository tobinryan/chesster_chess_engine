# Chesster the Chess Engine Readme
## Introduction
**Chesster, the Chess Engine,** is a program written in Python that allows you to play chess against a computer opponent. It implements a variety of chess-specific algorithms and techniques to make intelligent moves and provide a challenging game. This readme will provide an overview of how the engine works, highlighting key components and techniques used.

## Graphical User Interface (GUI)
The GUI is built using Python and Pygame and provides a user-friendly interface for playing chess. It includes the following features:

- **Sounds**: The GUI includes sounds after each move, depending on whether it's a quiet move, capture, causes check, promotion, or castling.

- **Possible Move Display**: When you click on a piece, the GUI displays the possible moves for that piece, making it easier to plan your moves and understand the available options.


## Bitboard Approach
The engine uses a **bitboard-based approach** to represent the chessboard and the pieces on it. Bitboards are 64-bit integers where each bit represents the presence or absence of a piece on a specific square. This allows for efficient manipulation of piece positions and moves using binary operations in parallel.

## Move Generation
**Move generation** is a critical component of the engine. It calculates all possible legal moves for the current board position. The engine uses bitboards to generate moves for each piece type, including pawns, knights, bishops, rooks, queens, and kings.

### Opening Book
At the beginning of the game, the engine uses the Titan **opening book** to determine its initial moves. The opening book contains a collection of well-known opening sequences and allows the engine to start the game with established opening moves.

### Bitboard Representation
Bitboards are used to represent the positions of different pieces on the board. For example, there are separate bitboards for white pawns, black pawns, white knights, and so on.
Bitwise operations (AND, OR, XOR) are employed to calculate possible moves, attacks, and captures for each piece type.

### Move Generation for Different Pieces
Move generation functions are implemented for each piece type, including pawn moves, knight moves, sliding piece moves (rooks, bishops, queens), and king moves.
The engine uses bit manipulation to determine possible legal moves and employs hyperbola quintessence to quickly determine sliding piece move generation.

### Perft Function
The engine implements the **Perft function** to test move generation. Perft is a tool for checking the correctness of the move generation code by counting the number of leaf nodes in the game tree for a given depth. It helps ensure that the engine generates legal moves accurately.

## Alpha-Beta Pruning
**Alpha-beta pruning** is used to search through the game tree and evaluate potential moves efficiently. It reduces the number of nodes that need to be evaluated by cutting off branches that are guaranteed to be worse than the best discovered move.

## Minimax Algorithm
The engine employs a **minimax algorithm**, which explores the game tree by considering both maximizing (white's) and minimizing (black's) positions.
Alpha-beta pruning is applied to avoid evaluating branches that do not affect the final result.

## Quiescence Search
**Quiescence search** is a specialized search that focuses on positions where the game is volatile, such as capturing pieces or checking the opponent's king. It ensures that the engine evaluates positions where tactical opportunities arise. The engine performs a quiescence search at the end of the regular search to evaluate positions where capturing pieces or checks are possible.
This prevents the horizon effect, where the engine would miss tactical opportunities.

## Evaluation Function
The **evaluation function** is used to assign a numerical value to a given board position, indicating how favorable it is for one side. It considers various factors, such as piece values, piece mobility, pawn structure, king safety, and control of key squares.

### Piece Values
Each piece is assigned a value (e.g., pawn = 1, knight = 3, bishop = 3, rook = 5, queen = 9) to assess material advantage.
The engine evaluates the total material balance between the two sides.

### Positional Factors
The engine considers factors like piece mobility and king safety (castling rights, open files).
Control of the center and key squares is also evaluated.

## Castling, En Passant, and Promotion
The engine handles **castling** and **en passant** moves, two special rules in chess.

### Castling
Castling moves are detected based on the positions of the king and rooks.
The engine ensures that the squares between the king and rook are empty, and the king is not in check.
Castling rights are updated after a successful castling move.

### En Passant
En passant captures are detected when a pawn moves two squares forward from its starting position.
The engine identifies the square where the capturing pawn can be attacked in the next move.

### Pawn Promotion
Pawn promotion is supported, allowing pawns to be promoted to other pieces (typically queens) upon reaching the opponent's back rank.

## Hashing and Transposition Tables
**Hashing** is used to store board positions and their evaluations to avoid redundant calculations during the search. **Transposition tables** are implemented to store and retrieve previously evaluated positions, reducing computation time.

## Importing and Exporting FEN Positions
The engine allows you to **import FEN positions** to start a game from a specific position. You can also **export a FEN position** at any point to save a game or share it with others.

## Insufficient Material
The engine checks for **insufficient material** on the board. If both sides have insufficient material to checkmate, the game is declared a draw.

## Endgame Handling
The engine has logic to handle different endgame scenarios, such as checkmate, stalemate, three-move repetition, the fifty-move rule, and insufficient material. It exits the game and declares a result when any of these conditions are met.

## Conclusion
This Chess Engine is a sophisticated program that combines various chess algorithms and techniques to provide a challenging and competitive chess-playing experience. It leverages bitboards, alpha-beta pruning, quiescence search, evaluation functions, and other chess-specific tools to make intelligent moves and play a strong game of chess. 
