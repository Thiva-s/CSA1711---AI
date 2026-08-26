fact(sunny).
fact(warm).

rule :-
    fact(sunny),
    fact(warm),
    write('It is a good day.'), nl.

forward :-
    rule.