# LinguStruct
LinguStruct is an AI-supported system design framework optimized for AI understanding and usability. It provides a structured template for system design documents, facilitating easy and efficient system development for users worldwide.

## Installation
Ensure you have Python 3.6 or higher installed. Then, clone the repository and install the package using pip:
bash
git clone https://github.com/lilseedabe/lingustruct.git
cd lingustruct
pip install .

## Usage
### 1. Setting up API Keys:
Create a `.env` file in the root directory to store your API keys and other sensitive information.
Example `.env` file:
env
GROQ_API_KEY=your-groq-api-key

### 2. Running the Framework:
Here is an example of how to use the LinguStruct framework:
python
from lingustruct import TemplateManager, AISupport, Validator
# Initialize components
tm = TemplateManager()
ai = AISupport()
validator = Validator()
# Load project template field
project_id_field = tm.get_field("project_id")
print("Project ID Field:", project_id_field)
# AI-supported section completion
completion = ai.complete_design("meta", "The purpose of this project is...")
print("AI Completion:", completion)
# Validate project data
data = {
    "project_id": "12345",
    "v": "1.3",
    "p_order": ["meta", "arch", "tech", "svc", "sec", "perf"],
    "meta": {"t_v": "1.0", "p_n": "Project Name", "desc": "A sample project", "scale": "m"}
}
is_valid, message = validator.validate(data)
print("Validation Result:", message)

## Configuration
Make sure the `.env` file is properly configured with your API keys and other settings. Here is an example of the `.env` file:
env
GROQ_API_KEY=your-groq-api-key

## License
This package is provided for **personal and academic use only**.  
**Commercial use** requires a license agreement. Please contact us at `osusume-co@lilseed.jp` for licensing inquiries.

## Contributing
If you wish to contribute to LinguStruct, please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes and push them to your branch.
4. Submit a pull request for review.

## Disclaimer
The authors are not responsible for any misuse or unintended consequences of using this framework. Users must adhere to all applicable laws and regulations when using this software.

## Issues & Support
If you encounter any issues, please report them on the [GitHub Issues](https://github.com/lilseedabe/lingustruct/issues) page.

## Changelog
- **v0.1.0**: Initial release with basic framework and API integration.

## Authors
Developed by Yasunori Abe. For inquiries, contact `osusume-co@lilseed.jp`.
