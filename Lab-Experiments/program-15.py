from sklearn.tree import DecisionTreeClassifier

# Data
X = [
    [1, 1],
    [1, 0],
    [0, 1],
    [0, 0]
]

# Output
y = [1, 1, 0, 0]

# Create Decision Tree
model = DecisionTreeClassifier()

# Train
model.fit(X, y)

# Prediction
result = model.predict([[1, 1]])

print("Prediction:", result[0])