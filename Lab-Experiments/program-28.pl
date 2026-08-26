symptom(fever, flu).
symptom(cough, flu).
symptom(cold, flu).

symptom(headache, migraine).
symptom(nausea, migraine).

symptom(thirst, diabetes).
symptom(frequent_urination, diabetes).

diagnose(Disease, Symptoms) :-
    Symptoms = [S1, S2],
    symptom(S1, Disease),
    symptom(S2, Disease).