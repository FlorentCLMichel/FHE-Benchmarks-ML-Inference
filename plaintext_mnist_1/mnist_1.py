import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, random_split
import os

# 1. Configuration
BATCH_SIZE = 64
LEARNING_RATE = 0.001
EPOCHS = 15 # Increased epochs for potentially better accuracy
MODEL_PATH = 'mnist_ffnn_model.pth'
RANDOM_SEED = 42 # for reproducibility

# Ensure reproducibility
torch.manual_seed(RANDOM_SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(RANDOM_SEED)

# 2. Data Loading and Preprocessing
transform = transforms.Compose([
    transforms.ToTensor(), # Converts PIL Image or numpy.ndarray to FloatTensor and scales to [0.0, 1.0]
    transforms.Normalize((0.1307,), (0.3081,)) # Normalize with MNIST dataset's mean and std
])

# Download MNIST dataset
full_dataset = datasets.MNIST('./data', train=True, download=True, transform=transform)
test_dataset = datasets.MNIST('./data', train=False, download=True, transform=transform)

# Split training data into training and validation sets
train_size = int(0.8 * len(full_dataset))
val_size = len(full_dataset) - train_size
train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

# 3. Model Definition
class SimpleFFNN(nn.Module):
    def __init__(self):
        super(SimpleFFNN, self).__init__()
        # MNIST images are 28x28 = 784 pixels
        self.fc1 = nn.Linear(28 * 28, 128) # First hidden layer
        self.relu = nn.ReLU()             # Activation function
        self.fc2 = nn.Linear(128, 64)     # Second hidden layer
        self.fc3 = nn.Linear(64, 10)      # Output layer (10 classes for digits 0-9)

    def forward(self, x):
        x = x.view(-1, 28 * 28) # Flatten the 28x28 image into a 784-dimensional vector
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        x = self.relu(x)
        x = self.fc3(x)
        return x # No softmax here, as CrossEntropyLoss will apply it internally

# 4. Training Function
def train_model(model, train_loader, val_loader, criterion, optimizer, epochs, device):
    best_accuracy = 0.0
    for epoch in range(epochs):
        model.train() # Set model to training mode
        running_loss = 0.0
        correct_train = 0
        total_train = 0
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(device), target.to(device)

            optimizer.zero_grad() # Zero the gradients
            output = model(data)  # Forward pass
            loss = criterion(output, target) # Calculate loss
            loss.backward()       # Backward pass
            optimizer.step()      # Update weights

            running_loss += loss.item()
            _, predicted = torch.max(output.data, 1)
            total_train += target.size(0)
            correct_train += (predicted == target).sum().item()

        train_accuracy = 100 * correct_train / total_train
        print(f'Epoch {epoch+1}/{epochs}, Loss: {running_loss/len(train_loader):.4f}, Train Accuracy: {train_accuracy:.2f}%')

        # Validation phase
        model.eval() # Set model to evaluation mode
        correct_val = 0
        total_val = 0
        val_loss = 0.0
        with torch.no_grad(): # Disable gradient calculation during validation
            for data, target in val_loader:
                data, target = data.to(device), target.to(device)
                output = model(data)
                val_loss += criterion(output, target).item()
                _, predicted = torch.max(output.data, 1)
                total_val += target.size(0)
                correct_val += (predicted == target).sum().item()

        val_accuracy = 100 * correct_val / total_val
        val_loss /= len(val_loader)
        print(f'Validation Loss: {val_loss:.4f}, Validation Accuracy: {val_accuracy:.2f}%')

        # Save the model if it's the best so far
        if val_accuracy > best_accuracy:
            best_accuracy = val_accuracy
            torch.save(model.state_dict(), MODEL_PATH)
            print(f'Model saved to {MODEL_PATH} with validation accuracy: {best_accuracy:.2f}%')

# 5. Testing Function
def test_model(model, test_loader, device):
    model.eval() # Set model to evaluation mode
    correct = 0
    total = 0
    with torch.no_grad(): # Disable gradient calculation
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            _, predicted = torch.max(output.data, 1)
            total += target.size(0)
            correct += (predicted == target).sum().item()
    accuracy = 100 * correct / total
    print(f'Accuracy on test data: {accuracy:.2f}%')
    return accuracy

# 6. Main Execution
if __name__ == '__main__':
    # Determine device (CPU or GPU)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    model = SimpleFFNN().to(device)
    criterion = nn.CrossEntropyLoss() # Suitable for classification tasks
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE) # Adam optimizer

    # Train the model if it does not exist
    if os.path.exists(MODEL_PATH):
        print(f"\nModel '{MODEL_PATH}' already exists. Skipping training and loading saved model.")
        model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
    else:
        print(f"\nModel '{MODEL_PATH}' not found. Starting training...")
        train_model(model, train_loader, val_loader, criterion, optimizer, EPOCHS, device)
        print("Training finished.")

    # Testing the model
    print(f"\nEvaluating model on test data...")
    test_accuracy = test_model(model, test_loader, device)
