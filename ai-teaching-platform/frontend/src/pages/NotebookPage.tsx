import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { FiArrowLeft, FiBook, FiEdit, FiEye, FiSave, FiDownload, FiShare2 } from 'react-icons/fi'
import MarkdownRenderer from '../components/MarkdownRenderer'
import CodeEditor from '../components/CodeEditor'

// Mock notebook content
const mockNotebookContent = `# Linear Regression Implementation

This notebook demonstrates a simple linear regression implementation using PyTorch.

## Introduction

Linear regression is a fundamental machine learning algorithm for predicting continuous values. It models the relationship between input features and output targets using a linear equation.

The model is defined as:

\\[
y = wx + b
\\]

where:
- \\(y\\) is the predicted value
- \\(w\\) is the weight (slope)
- \\(x\\) is the input feature
- \\(b\\) is the bias (intercept)

## Implementation

Let's implement linear regression from scratch:

\`\`\`python
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt

class LinearRegressionModel(nn.Module):
    """Simple linear regression model."""
    
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(1, 1)  # One input, one output
        
    def forward(self, x):
        return self.linear(x)

def train_model(model, X, y, epochs=1000, learning_rate=0.01):
    """Train the linear regression model."""
    criterion = nn.MSELoss()
    optimizer = optim.SGD(model.parameters(), lr=learning_rate)
    
    losses = []
    
    for epoch in range(epochs):
        # Forward pass
        predictions = model(X)
        loss = criterion(predictions, y)
        
        # Backward pass and optimize
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        losses.append(loss.item())
        
        if (epoch + 1) % 100 == 0:
            print(f'Epoch [{epoch + 1}/{epochs}], Loss: {loss.item():.4f}')
    
    return losses

# Generate synthetic data
torch.manual_seed(42)
X = torch.randn(100, 1) * 10
true_weight = 2.5
true_bias = 1.0
y = true_weight * X + true_bias + torch.randn(100, 1) * 2

# Create and train model
model = LinearRegressionModel()
losses = train_model(model, X, y)

print(f"Trained weight: {model.linear.weight.item():.4f}")
print(f"Trained bias: {model.linear.bias.item():.4f}")
print(f"True weight: {true_weight}")
print(f"True bias: {true_bias}")
\`\`\`

## Results

After training, we can visualize the results:

\`\`\`python
# Make predictions
with torch.no_grad():
    predictions = model(X)

# Plot results
plt.figure(figsize=(10, 6))
plt.scatter(X.numpy(), y.numpy(), alpha=0.6, label='Original data')
plt.plot(X.numpy(), predictions.numpy(), color='red', linewidth=2, label='Regression line')
plt.xlabel('X')
plt.ylabel('y')
plt.title('Linear Regression Results')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
\`\`\`

## Mathematical Formulation

The loss function we minimize is the Mean Squared Error (MSE):

\\[
\\text{MSE} = \\frac{1}{n} \\sum_{i=1}^{n} (y_i - \\hat{y}_i)^2
\\]

Where:
- \\(n\\) is the number of samples
- \\(y_i\\) is the true value
- \\(\\hat{y}_i\\) is the predicted value

## Exercises

1. Try changing the learning rate and observe its effect on convergence.
2. Add L2 regularization to the model.
3. Extend the model to multiple features (multivariate linear regression).

## Conclusion

Linear regression is a simple yet powerful algorithm. This implementation shows how to build and train a model from scratch using PyTorch.
`

export default function NotebookPage() {
  const { courseId, chapterId, notebookId } = useParams<{
    courseId: string
    chapterId: string
    notebookId: string
  }>()
  
  const [mode, setMode] = useState<'view' | 'edit'>('view')
  const [content, setContent] = useState(mockNotebookContent)
  const [isSaved, setIsSaved] = useState(true)
  
  const handleContentChange = (newContent: string) => {
    setContent(newContent)
    setIsSaved(false)
  }
  
  const handleSave = () => {
    // In a real app, this would save to backend
    console.log('Saving notebook content:', content)
    setIsSaved(true)
  }
  
  const handleDownload = () => {
    const blob = new Blob([content], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'notebook.md'
    a.click()
    URL.revokeObjectURL(url)
  }
  
  return (
    <div className="space-y-6">
      <div>
        <Link 
          to={`/courses/${courseId}`}
          className="inline-flex items-center text-primary-600 hover:text-primary-700 mb-4"
        >
          <FiArrowLeft className="mr-2" />
          Back to Course
        </Link>
        
        <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Linear Regression Implementation</h1>
            <p className="mt-2 text-gray-600">
              Chapter 4 • Notebook 1 • Machine Learning Fundamentals
            </p>
          </div>
          
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setMode(mode === 'view' ? 'edit' : 'view')}
              className={`px-4 py-2 rounded-lg flex items-center space-x-2 ${
                mode === 'view'
                  ? 'bg-primary-600 text-white hover:bg-primary-700'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {mode === 'view' ? (
                <>
                  <FiEdit />
                  <span>Edit</span>
                </>
              ) : (
                <>
                  <FiEye />
                  <span>View</span>
                </>
              )}
            </button>
            
            <button
              onClick={handleSave}
              disabled={isSaved}
              className={`px-4 py-2 rounded-lg flex items-center space-x-2 ${
                isSaved
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-green-600 text-white hover:bg-green-700'
              }`}
            >
              <FiSave />
              <span>{isSaved ? 'Saved' : 'Save'}</span>
            </button>
            
            <button
              onClick={handleDownload}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 flex items-center space-x-2"
            >
              <FiDownload />
              <span>Download</span>
            </button>
            
            <button className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 flex items-center space-x-2">
              <FiShare2 />
              <span>Share</span>
            </button>
          </div>
        </div>
        
        <div className="mt-4 flex items-center space-x-4 text-sm text-gray-600">
          <div className="flex items-center space-x-2">
            <FiBook size={14} />
            <span>Last modified: 2 hours ago</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span>{isSaved ? 'All changes saved' : 'Unsaved changes'}</span>
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3">
          <div className="card min-h-[600px]">
            {mode === 'view' ? (
              <div className="prose prose-lg max-w-none">
                <MarkdownRenderer content={content} />
              </div>
            ) : (
              <div className="h-full">
                <CodeEditor
                  value={content}
                  onChange={handleContentChange}
                  language="markdown"
                  height="600px"
                />
              </div>
            )}
          </div>
          
          <div className="mt-6 card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Exercises & Questions</h3>
            <div className="space-y-4">
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h4 className="font-medium text-blue-900">Exercise 1: Learning Rate Analysis</h4>
                <p className="mt-1 text-blue-800">
                  Try changing the learning rate from 0.01 to 0.1 and 0.001. Observe how it affects:
                </p>
                <ul className="mt-2 ml-6 text-blue-800 list-disc">
                  <li>Convergence speed</li>
                  <li>Final loss value</li>
                  <li>Training stability</li>
                </ul>
              </div>
              
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <h4 className="font-medium text-green-900">Exercise 2: Regularization</h4>
                <p className="mt-1 text-green-800">
                  Add L2 regularization to the model. Modify the loss function to include:
                  \\[ \\text{Loss} = \\text{MSE} + \\lambda \\sum w^2 \\]
                  Experiment with different values of \\(\\lambda\\).
                </p>
              </div>
              
              <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
                <h4 className="font-medium text-purple-900">Question 1: Overfitting</h4>
                <p className="mt-1 text-purple-800">
                  What signs would indicate that your linear regression model is overfitting?
                  How could you detect and prevent it?
                </p>
              </div>
            </div>
          </div>
        </div>
        
        <div className="space-y-6">
          <div className="card">
            <h3 className="font-semibold text-gray-900 mb-4">Notebook Info</h3>
            <div className="space-y-3">
              <div>
                <div className="text-sm text-gray-500">Course</div>
                <div className="font-medium text-gray-900">Machine Learning Fundamentals</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">Chapter</div>
                <div className="font-medium text-gray-900">Linear Regression</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">Language</div>
                <div className="font-medium text-gray-900">Python</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">Estimated Time</div>
                <div className="font-medium text-gray-900">45 minutes</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">Difficulty</div>
                <div className="font-medium text-gray-900">
                  <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                    Beginner
                  </span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="card">
            <h3 className="font-semibold text-gray-900 mb-4">Code Execution</h3>
            <div className="space-y-3">
              <div className="p-3 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-700 font-mono">
                  $ python linear_regression.py
                </div>
                <div className="mt-2 text-xs text-gray-600">
                  Training model with 1000 epochs...
                </div>
              </div>
              <button className="w-full btn-primary">
                Run Code
              </button>
              <button className="w-full btn-secondary">
                Open in Colab
              </button>
            </div>
          </div>
          
          <div className="card">
            <h3 className="font-semibold text-gray-900 mb-4">Learning Objectives</h3>
            <ul className="space-y-2">
              {[
                'Understand linear regression theory',
                'Implement linear regression from scratch',
                'Train models with gradient descent',
                'Evaluate model performance',
                'Visualize results',
              ].map((objective, idx) => (
                <li key={idx} className="flex items-center text-gray-700">
                  <div className="w-2 h-2 bg-primary-500 rounded-full mr-2"></div>
                  {objective}
                </li>
              ))}
            </ul>
          </div>
          
          <div className="card">
            <h3 className="font-semibold text-gray-900 mb-4">Related Notebooks</h3>
            <div className="space-y-2">
              {[
                { title: 'Multiple Linear Regression', status: 'upcoming' },
                { title: 'Polynomial Regression', status: 'upcoming' },
                { title: 'Logistic Regression', status: 'completed' },
                { title: 'Regularization Techniques', status: 'available' },
              ].map((notebook, idx) => (
                <Link
                  key={idx}
                  to="#"
                  className="flex items-center justify-between p-2 hover:bg-gray-50 rounded-lg"
                >
                  <span className="text-sm text-gray-700">{notebook.title}</span>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    notebook.status === 'completed'
                      ? 'bg-green-100 text-green-800'
                      : notebook.status === 'available'
                      ? 'bg-blue-100 text-blue-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {notebook.status}
                  </span>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}