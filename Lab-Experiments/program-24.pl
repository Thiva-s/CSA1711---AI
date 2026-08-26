diet(diabetes, 'Low sugar and high fiber diet').
diet(hypertension, 'Low salt and low fat diet').
diet(obesity, 'Low calorie and high protein diet').
diet(anemia, 'Iron rich food and green vegetables').
diet(fever, 'Light food and plenty of fluids').

suggest_diet(Disease, Diet) :-
    diet(Disease, Diet).