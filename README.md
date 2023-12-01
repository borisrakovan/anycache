# anycache

## Overview

Anycache is a powerful Python library that provides an easy-to-use caching solution for your Python applications. It is
designed to cache the results of function calls, including support for synchronous functions, asynchronous functions,
synchronous generators, and asynchronous generators. The main feature of Anycache is its ability to persist cached data
across multiple interpreter invocations by storing them on disk.

## Features

- **Support for Various Function Types**: Anycache supports caching for synchronous and asynchronous functions, as well
  as synchronous and asynchronous generators.
- **Disk-Based Caching**: Cached data are stored on disk, allowing the cached values to survive across multiple
  interpreter invocations.
- **Custom Serialization**: Flexibility in choosing the serialization method for caching objects.
- **Namespace Support**: Organize cache files under specified namespaces for better management.
- **Automatic Cache Key Generation**: Unique cache keys are generated based on function names and arguments, ensuring
  the uniqueness and relevancy of cached data.

## Motivation

The primary motivation for using Anycache is to optimize performance and reduce the load on external resources. Typical
use cases include:

- **Web Scraping**: Web scraping is often time-consuming, involving many repeated calls. Anycache can significantly
  reduce the time and resources required by caching the results of these calls.
- **Communication with APIs**: During development, especially when interfacing with other APIs, it's common to rerun
  code with the same inputs multiple times. Anycache helps avoid redundant API calls and potential costs associated with
  them.

## Installation

```bash
pip install anycache
```

## Usage

### Basic Usage

To use Anycache, simply decorate your functions with `@cache`. Here's a basic example:

```python
from anycache import cache


@cache
def expensive_function(arg1, arg2):
    result = some_computation(arg1, arg2)
    return result
```

### Using with Async Functions

Anycache seamlessly works with asynchronous functions:

```python
from anycache import cache


@cache
async def expensive_async_function(arg1, arg2):
    result = await some_computation(arg1, arg2)
    return result
```

### Example: Caching OpenAI API Calls

Here's a practical example of using Anycache to cache calls to the OpenAI API:

```python
from anycache import cache
import openai


@cache(cache_dir="cache", namespace="openai.call_openai_api")
def call_openai_api(messages, max_tokens):
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        max_tokens=max_tokens
    )
    return completion.choices[0].message.content


# First invocation calls the API
result1 = call_openai_api("Translate 'Hello, world!' to French", max_tokens=5)
# Subsequent invocations with the same arguments use cached data
result2 = call_openai_api("Translate 'Hello, world!' to French", max_tokens=5)

assert result1 == result2  # True
```

## Configuration

- **cache_dir**: Specify the directory for storing cache files.
- **namespace**: Organize cache under a specific namespace.
- **is_method**: Set to `True` if decorating a method within a class.
- **serializer**: Choose a custom serializer for your cached data.

## Contributing

Contributions to Anycache are welcome! Please refer to the project's issue tracker to report bugs or suggest features.

## License

Anycache is released under the [MIT License](LICENSE).

---

By using Anycache, you can enhance the efficiency of your Python applications, especially in scenarios involving
repeated and expensive function calls. This library is particularly useful in development environments, where minimizing
redundant operations can save both time and resources.