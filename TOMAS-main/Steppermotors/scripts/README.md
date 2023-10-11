The TOMAS ICRH antenna has a matching system that consists of three capacitors. Resonance matching and impedance matching can
be achieved by changing the capacitors, essentially moving one of the capacitor plates. The movement of the plate is controlled by a stepper motor.
The three stepper motors of the three capacitors are manipulated from a Python program, through an Arduino program.
In Python, the user can enter the desired positions of capacitors as X x Y y Z z with X, Y, Z in [A, P, S] and x, y, z in [1, 100]. It is allowed to
specify not all capacitors, and to specify the capacitors in a different order. The positions of the capacitors are stored in a file, in 
order to retrieve the positions when closing the program.
The user can enter 'scan' to loop through all possible combinations of positions, or 'limit X (Y Z)' to find the limits of the capacitor(s) by moving the capacitor(s) until they touched the limit switches on both ends. To quit the program, the user can enter 'q'. This breaks the while loop and closes the opened files.

