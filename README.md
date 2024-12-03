# Youtext

YouTubeTranscriptSummarizer is a Python tool that fetches transcripts from YouTube videos and generates summaries using OpenAI's GPT-4o model.

## Features

- Extract video ID from YouTube URLs
- Fetch transcripts from YouTube videos
- Summarize transcripts using OpenAI's GPT-4 model
- Save transcripts and summaries to temporary files
- CLI support for easy usage

## Installation

Choose one of the following installation methods:

### Method 1: Pip Installation (Recommended)

1. Clone this repository
2. Install the package:
   ```
   pip install -e .
   ```
   ```
   pip uninstall youtext

### Method 2: Manual Installation

1. Clone this repository
2. Install required packages:
   ```
   pip install youtube_transcript_api openai tiktoken
   ```
3. Make the script executable:
   ```
   chmod +x script.py
   ```
4. Create a symbolic link:
   ```
   ln -sf $(pwd)/youtext/main.py /usr/local/bin/youtext
   chmod +x /usr/local/bin/youtext
   ```

### For both methods:

Set up your OpenAI API key as an environment variable:

## Usage

After installation, you can use `youtext` from anywhere:

1. Summarize a video:
   ```
   youtext summ <YouTube_URL_or_ID>
   ```

2. Fetch a video transcript:
   ```
   youtext script <YouTube_URL_or_ID>
   ```

### CLI

The tool provides two main commands:

1. Summarize a video:
   ```
   python script.py summ <YouTube_URL_or_ID>
   ```

2. Fetch a video transcript:
   ```
   python script.py script <YouTube_URL_or_ID>
   ```

### As a Modulepython

```py
from script import youtext
result = youtext("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
print(result['summary'])
```


## Output

The tool saves transcripts and summaries to temporary files and returns their paths along with other information.

## Logging

The script uses Python's logging module to provide informative output during execution.

## Note

Ensure you have the necessary permissions and comply with YouTube's terms of service when using this tool.
