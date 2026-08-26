bird(parrot).
has_wings(parrot).

can_fly(X) :-
    bird(X),
    has_wings(X).
