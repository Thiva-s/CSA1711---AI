male(john).
male(bob).
male(david).

female(mary).
female(lisa).
female(anna).

parent(john, bob).
parent(mary, bob).

parent(john, lisa).
parent(mary, lisa).

parent(bob, david).
parent(lisa, anna).

father(X, Y) :-
    male(X),
    parent(X, Y).

mother(X, Y) :-
    female(X),
    parent(X, Y).

grandparent(X, Y) :-
    parent(X, Z),
    parent(Z, Y).