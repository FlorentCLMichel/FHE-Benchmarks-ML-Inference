import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, random_split
import os
from absl import app, flags

FLAGS = flags.FLAGS

# 1. Configuration
BATCH_SIZE = 64
LEARNING_RATE = 0.001
EPOCHS = 15 # Increased epochs for potentially better accuracy
MODEL_PATH = 'mnist_ffnn_model.pth'
RNG_SEED = 42 # for reproducibility

# Define command line flags
flags.DEFINE_string('model_path', MODEL_PATH, 'Path to save/load the model')
flags.DEFINE_integer('batch_size', BATCH_SIZE, 'Batch size for training and evaluation')
flags.DEFINE_float('learning_rate', LEARNING_RATE, 'Learning rate for optimizer')
flags.DEFINE_integer('epochs', EPOCHS, 'Number of training epochs')
flags.DEFINE_string('data_dir', './data', 'Directory to store/load MNIST dataset')
flags.DEFINE_boolean('no_cuda', False, 'Disable CUDA even if available')
flags.DEFINE_integer('seed', RNG_SEED, 'Random seed for reproducibility')

flags.DEFINE_boolean('export_test_data', False, 'Export test dataset to file and exit')
flags.DEFINE_string('test_data_output', 'mnist_test.txt', 'Output file for exported test data')
flags.DEFINE_integer('num_samples', -1, 'Number of samples to export (-1 for all samples)')

# Ensure reproducibility
torch.manual_seed(RNG_SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(RNG_SEED)

# 2. Data Loading and Preprocessing
def get_mnist_transform():
    """
    Get the standard MNIST transform for preprocessing.
    
    Returns:
        transforms.Compose: Transform pipeline for MNIST data
    """
    return transforms.Compose([
        transforms.ToTensor(), # Converts PIL Image or numpy.ndarray to FloatTensor and scales to [0.0, 1.0]
        transforms.Normalize((0.1307,), (0.3081,)) # Normalize with MNIST dataset's mean and std
    ])

def load_and_preprocess_data(batch_size=BATCH_SIZE, data_dir='./data'):
    """
    Load and preprocess MNIST dataset.
    
    Args:
        batch_size (int): Batch size for data loaders
        data_dir (str): Directory to store/load dataset
    
    Returns:
        tuple: (train_loader, val_loader, test_loader)
    """
    transform = get_mnist_transform()

    # Download MNIST dataset
    full_dataset = datasets.MNIST(data_dir, train=True, download=True, transform=transform)
    test_dataset = datasets.MNIST(data_dir, train=False, download=True, transform=transform)

    # Split training data into training and validation sets
    train_size = int(0.8 * len(full_dataset))
    val_size = len(full_dataset) - train_size
    train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    return train_loader, val_loader, test_loader
    

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
def train_model(model, train_loader, val_loader, criterion, optimizer, epochs, device, model_path):
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
            torch.save(model.state_dict(), model_path)
            print(f'Model saved to {model_path} with validation accuracy: {best_accuracy:.2f}%')

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

# Function to export test data to separate files.
def export_test_data(data_dir='./data', output_file='mnist_test.txt', num_samples=-1):
    """
    Export MNIST test dataset to separate label and pixel files.
    
    Args:
        data_dir (str): Directory to load dataset from
        output_file (str): Base output file path (will create .labels and .pixels files)
        num_samples (int): Number of samples to export (-1 for all)
    """
    transform = transforms.Compose([
        transforms.ToTensor(), # Converts PIL Image or numpy.ndarray to FloatTensor and scales to [0.0, 1.0]
    ])
    test_dataset = datasets.MNIST(data_dir, train=False, download=True, transform=transform)
    
    # Determine how many samples to export
    total_samples = len(test_dataset)
    samples_to_export = total_samples if num_samples == -1 else min(num_samples, total_samples)
    
    # Create separate file names for labels and pixels
    base_name = str(output_file).rsplit('.', 1)[0] if '.' in str(output_file) else str(output_file)
    labels_file = f"{base_name}_labels.txt"
    pixels_file = f"{base_name}_pixels.txt"
    
    with open(labels_file, 'w') as label_f, open(pixels_file, 'w') as pixel_f:
        for i, (image, label) in enumerate(test_dataset):
            if i >= samples_to_export:
                break
                
            # Flatten the image to 784 dimensions (28x28)
            flattened_image = image.view(-1).numpy()
            
            # Write label to labels file
            label_f.write(f"{label}\n")
            
            # Write pixel values to pixels file
            pixel_values = " ".join(f"{pixel:.6f}" for pixel in flattened_image)
            pixel_f.write(f"{pixel_values}\n")


def main(argv):
    # Check if we should just export test data and exit
    if FLAGS.export_test_data:
        print("Export mode: Loading and exporting test data...")
        export_test_data(data_dir=FLAGS.data_dir, output_file=FLAGS.test_data_output, num_samples=FLAGS.num_samples)
        print("Export completed. Exiting.")
        return
    
    # Use command line flags
    model_path = FLAGS.model_path
    batch_size = FLAGS.batch_size
    learning_rate = FLAGS.learning_rate
    epochs = FLAGS.epochs
    data_dir = FLAGS.data_dir
    use_cuda = not FLAGS.no_cuda and torch.cuda.is_available()
    random_seed = FLAGS.seed
    
    # Set random seed for reproducibility
    torch.manual_seed(random_seed)
    if use_cuda:
        torch.cuda.manual_seed_all(random_seed)
    
    # Load and preprocess data
    print("Loading and preprocessing data...")
    train_loader, val_loader, test_loader = load_and_preprocess_data(batch_size=batch_size, data_dir=data_dir)
    print("Data loading completed.")
    
    # Determine device (CPU or GPU)
    device = torch.device("cuda" if use_cuda else "cpu")
    print(f"Using device: {device}")
    print(f"Model path: {model_path}")
    print(f"Batch size: {batch_size}")
    print(f"Learning rate: {learning_rate}")
    print(f"Epochs: {epochs}")
    print(f"Random seed: {random_seed}")

    model = SimpleFFNN().to(device)
    criterion = nn.CrossEntropyLoss() # Suitable for classification tasks
    optimizer = optim.Adam(model.parameters(), lr=learning_rate) # Adam optimizer

    # Train the model if it does not exist
    if os.path.exists(model_path):
        print(f"\nModel '{model_path}' already exists. Skipping training and loading saved model.")
        model.load_state_dict(torch.load(model_path, map_location=device))
    else:
        print(f"\nModel '{model_path}' not found. Starting training...")
        train_model(model, train_loader, val_loader, criterion, optimizer, epochs, device, model_path)
        print("Training finished.")

    # Testing the model
    print(f"\nEvaluating model on test data...")
    test_accuracy = test_model(model, test_loader, device)


if __name__ == '__main__':
    app.run(main)
