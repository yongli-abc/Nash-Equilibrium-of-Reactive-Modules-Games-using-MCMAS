This repository holds the implemented tool for my master project: Nash Equilibrium of Reactive Modules Games using MCMAS.

Before running, please ensure you have already installed the MCMAS-SLK extension from this page (http://vas.doc.ic.ac.uk/software/extensions/).
Please also symbol-link the 'mcmas' executable into your PATH for executable. For example:
ln -s path/to/mcmas /usr/local/bin

As a result, you must be able to type 'mcmas' command directly within terminal, without specifying the path. Now you are OK to use this tool.

To use tool, please write your game in SRML format. There are several examples in the ./RML_examples directory. Then use './main yourRMLFile.rml' to run the tool. It will automatically analyse the existence of Nash Equilibrium in your game.

For writing a propositional formula, supported connectives are '&&, ||, !, ->'.
For writing a LTL formula as 'goal', supported temporal operators are 'X, F, G, U'. Please avoid use these letters in variables. It's recommended to use small-case letters for variables only.
