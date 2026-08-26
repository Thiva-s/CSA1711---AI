edge(a, b, 4).
edge(a, c, 2).
edge(b, d, 5).
edge(c, d, 1).
edge(d, e, 3).

best_first(Start, Goal) :-
    search([Start], Goal).

search([Goal|_], Goal) :-
    write('Goal reached: '), write(Goal), nl.

search([Current|Rest], Goal) :-
    findall(
        Node,
        (edge(Current, Node, _), \+ member(Node, Rest)),
        Nodes
    ),
    append(Nodes, Rest, NewList),
    search(NewList, Goal).