# Multi LLM Code Explainer

A web application that explains code using both OpenAI's GPT-4 and Anthropic's Claude 3.5 Sonnet. Get multiple AI perspectives on your code!

## Features

- Paste any code snippet and get explanations from multiple AI models
- Clean, modern UI with dark mode
- Real-time explanations
- Side-by-side comparison of different AI explanations

## Prerequisites

- Python 3.8+
- OpenAI API Key
- Anthropic API Key
- AWS Account (for deployment)

## Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Gsebs/AI-Code-Explainer.git
   cd AI-Code-Explainer
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

5. Run the application:
   ```bash
   python app/app.py
   ```

6. Open your browser and navigate to `http://localhost:5000`

## AWS Deployment

1. Configure AWS credentials:
   ```bash
   aws configure
   ```

2. Add AWS credentials to `.env`:
   ```
   AWS_ACCESS_KEY_ID=your_aws_access_key_here
   AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
   AWS_REGION=your_preferred_region
   ```

## Usage

1. Visit the application in your web browser
2. Paste your code in the input box
3. Click "Submit"
4. View explanations from both GPT-4 and Claude

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/) 