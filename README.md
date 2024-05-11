[![Build and Publish Python Package](https://github.com/Cdaprod/hydrate/actions/workflows/push-to-pypi.yml/badge.svg)](https://github.com/Cdaprod/hydrate/actions/workflows/push-to-pypi.yml)

[![Build and Publish Python Package](https://github.com/Cdaprod/hydrate/actions/workflows/push-to-pypi.yml/badge.svg)](https://github.com/Cdaprod/hydrate/actions/workflows/push-to-pypi.yml)

![](photo.webp)

# Hydrate-Minio-Weaviate
Hydrate-Minio-Weaviate is a powerful Python package designed to automate the extraction, transformation, and loading of data from web resources directly into MinIO and Weaviate. This tool simplifies the process of hydrating your data lake and knowledge graph with fresh data, enhancing your AI and machine learning workflows with minimal effort.

## Features

- **Automated Data Extraction**: Fetch data seamlessly from specified URLs.
- **Data Transformation**: Process and clean the fetched data to ensure quality before storage.
- **Seamless Integration**: Store transformed data directly into MinIO buckets and index it within Weaviate for immediate usage in applications.
- **Configurable**: Flexible configuration options to cater to different environments and use cases.
- **Logging and Monitoring**: Comprehensive logging to track data processing and facilitate troubleshooting.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine or production environment for development and testing purposes.

### Prerequisites

What you need to install the software:

- Python 3.8 or later
- MinIO server (local or remote)
- Weaviate instance

### Installation

Install `hydrate-minio-weaviate` using pip:

```bash
pip install hydrate-minio-weaviate
```

## Configuration

To configure the system, edit the `config.py` file or pass parameters directly into the function calls. Detailed documentation on configuration parameters is available [here](#).

### Environment Variables

To run the `hydrate` package successfully, you need to configure several environment variables. These variables can be set in your local development environment or configured in CI/CD pipelines for automation.

### Setting up Environment Variables Locally

For local development, use a `.env` file to manage your environment settings securely. Here's how to set it up:

**Create a `.env` file** in your project root (the same directory as your `hydrate.py` script):
 
```plaintext
MINIO_ACCESS_KEY=your_minio_access_key
MINIO_SECRET_KEY=your_minio_secret_key
WEAVIATE_ENDPOINT=your_weaviate_endpoint
```
**Install `python-dotenv`** to easily load the variables from the `.env` file:

```bash
pip install python-dotenv
```

**Load the variables in your script**:

```python
from dotenv import load_dotenv
import os

load_dotenv()  # Load the variables from .env

# Your configuration class or setup
class ClientConfig(BaseModel):
    minio_endpoint: str = os.getenv('MINIO_ENDPOINT', 'default_endpoint')
    minio_access_key: str = os.getenv('MINIO_ACCESS_KEY', 'default_access_key')
    minio_secret_key: str = os.getenv('MINIO_SECRET_KEY', 'default_secret_key')
    weaviate_endpoint: str = os.getenv('WEAVIATE_ENDPOINT', 'default_endpoint')
```

### Usage

Here is a quick start to using `hydrate-minio-weaviate`:

```python
from hydrate_minio_weaviate import main

# Define the URLs and bucket name
urls = ["https://example.com", "https://another-example.com"]
bucket_name = "your-minio-bucket"

# Call the main function
main(urls, bucket_name)
```

For detailed usage and more examples, refer to the [Documentation](#).

### Configuring Environment Variables in GitHub Actions

For projects using GitHub Actions for CI/CD, configure your secrets in the GitHub repository to keep them secure:

1. **Navigate to your GitHub repository Settings**.
2. **Go to Secrets and create new repository secrets** for `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`, and `WEAVIATE_ENDPOINT`.
3. **Use these secrets in your GitHub Actions workflow**:
 
```yaml
jobs:
  build-and-publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    - name: Load environment variables
      run: |
        echo "MINIO_ACCESS_KEY=${{ secrets.MINIO_ACCESS_KEY }}" >> $GITHUB_ENV
        echo "MINIO_SECRET_KEY=${{ secrets.MINIO_SECRET_KEY }}" >> $GITHUB_ENV
        echo "WEAVIATE_ENDPOINT=${{ secrets.WEAVIATE_ENDPOINT }}" >> $GITHUB_ENV
    - name: Run script
      run: python hydrate/hydrate.py
```

### Best Practices

- **Security**: Avoid hardcoding your sensitive keys directly in the code. Always use environment variables or secure secrets management practices.
- **Documentation**: Ensure that any environment configurations are well-documented to facilitate easy setup for new users or contributors to your project.

By following these instructions, users can configure the `hydrate` package correctly in any environment.

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Support

If you need assistance or have any queries, please email us at support@example.com.

## Acknowledgments

- Thanks to the MinIO team for the robust storage solution.
- Appreciation to Weaviate for their innovative approach to knowledge graph management.
- All contributors who have been part of this project.

--- 

## Todo!

### Roadmap

- Future development plans and feature additions can be found on the [issues page](#).

### Notes:
- **Documentation Link**: Replace `#` with the actual link to your documentation, which might be on GitHub pages or another site.
- **Issues Page**: Link to the GitHub issues page for your project to show the roadmap and current issues.