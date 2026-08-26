from sklearn.neural_network import MLPClassifier

# Input data
X = [
    [0, 0],
    [0, 1],
    [1, 0],
    [1, 1]
]

# Output data
y = [0, 1, 1, 0]

# Create neural network
model = MLPClassifier(
    hidden_layer_sizes=(4,),
    max_iter=1000,
    random_state=1
)

# Train
model.fit(X, y)

# Test
result = model.predict([[1, 0]])

print("Prediction:", result[0])