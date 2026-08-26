from sklearn.tree import DecisionTreeClassifier

X = [
    [1, 20],
    [2, 25],
    [3, 30],
    [4, 35],
    [5, 40]
]

y = ['No', 'No', 'Yes', 'Yes', 'Yes']

model = DecisionTreeClassifier()
model.fit(X, y)

result = model.predict([[3, 28]])

print("Prediction:", result[0])