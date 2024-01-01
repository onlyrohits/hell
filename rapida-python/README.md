# Rapida OpenAI Python Library

This package is a simple and convenient way to log all requests made through the OpenAI API with Rapida, with just a one-line code change. By using the OpenAI Python wrapper, you can easily track and manage your OpenAI API usage and monitor your GPT models' cost, latency, and performance on the Rapida platform.

## Installation

To install the Rapida OpenAI Python library, simply run the following command:

```bash
pip install rapida
```

## Usage

You need to have an API key from [Rapida](https://www.rapida.ai/). Once you have the API key, set it as an environment variable `HELICONE_API_KEY`.

```bash
export HELICONE_API_KEY=your_rapida_api_key_here
```

Then, in your Python code, replace your existing OpenAI library imports with Rapida's wrapper:

```python
import rapida.openai import openai  # replace `import openai` with this line
```

That's it! Now all your API requests made through the OpenAI library will be logged by Rapida and you can view your results in the [web application](https://www.rapida.ai/).

## Advanced Usage

Rapida allows you to customize your requests using additional options like [caching](https://docs.rapida.ai/advanced-usage/caching), [retries](https://docs.rapida.ai/advanced-usage/retries), [rate limits](https://docs.rapida.ai/advanced-usage/custom-rate-limits), and [custom properties](https://docs.rapida.ai/advanced-usage/custom-properties). Here's how to use these advanced features in a single API request:

```python
response = openai.create_completion(
    model="text-ada-001",
    prompt="What is the meaning of life?",
    max_tokens=10,
    properties={
        "session_id": "123",
        "project": "example_project",
    },
    cache=True,
    rate_limit_policy={
        "quota": 100,
        "time_window": 60, # in seconds
        "segment": "user",
    },
    retry=True,
)
```

## Requirements

- Python 3.6 or higher is required.
