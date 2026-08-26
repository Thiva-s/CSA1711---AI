hanoi(1, A, B, C) :-
    write('Move disk from '), write(A),
    write(' to '), write(B), nl.

hanoi(N, A, B, C) :-
    N > 1,
    N1 is N - 1,
    hanoi(N1, A, C, B),
    hanoi(1, A, B, C),
    hanoi(N1, C, B, A).