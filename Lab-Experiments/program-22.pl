bird(parrot).
bird(eagle).
bird(penguin).
bird(ostrich).

can_fly(parrot).
can_fly(eagle).

cannot_fly(X) :-
    bird(X),
    \+ can_fly(X).
    