from sklearn.neighbors import KNeighborsClassifier

X = [[1], [2], [3], [4], [5]]
y = ['A', 'A', 'B', 'B', 'B']

model = KNeighborsClassifier(n_neighbors=3)
model.fit(X, y)

result = model.predict([[2.5]])

print("Predicted class:", result[0])