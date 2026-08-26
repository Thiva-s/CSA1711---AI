can_reach_banana(State) :-
    State = near_banana,
    write('Monkey gets the banana.').

can_reach_banana(State) :-
    State = far_from_banana,
    write('Monkey moves near the banana.'), nl,
    can_reach_banana(near_banana).