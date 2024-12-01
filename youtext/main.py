import argparse
import os
import logging
import tempfile
import time
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
import tiktoken
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

model = "gpt-4o"
max_tokens = 4096


def get_video_id(url):
    """Extract video ID from YouTube URL."""
    logger.info(f"Extracting video ID from URL: {url}")
    if "youtu.be" in url:
        return url.split("/")[-1]
    elif "youtube.com" in url:
        return url.split("v=")[1].split("&")[0]
    else:
        raise ValueError("Invalid YouTube URL")


def fetch_transcript(video_id):
    """Fetch transcript for a given YouTube video ID."""
    logger.info(f"Fetching transcript for video ID: {video_id}")
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry["text"] for entry in transcript])
    except Exception as e:
        logger.error(f"Error fetching transcript: {str(e)}")
        raise Exception(f"Error fetching transcript: {str(e)}")


def get_tokenizer():
    return tiktoken.encoding_for_model(model)


def chunk_text(text, max_tokens=max_tokens):
    logger.info(f"Chunking text into parts of max tokens: {max_tokens}")
    tokenizer = get_tokenizer()
    tokens = tokenizer.encode(text)
    chunks = []
    current_chunk = []
    current_count = 0
    for token in tokens:
        if current_count + 1 > max_tokens:
            chunks.append(tokenizer.decode(current_chunk))
            current_chunk = [token]
            current_count = 1
        else:
            current_chunk.append(token)
            current_count += 1
    if current_chunk:
        chunks.append(tokenizer.decode(current_chunk))
    return chunks


def generate_unique_filename(video_id, suffix):
    timestamp = int(time.time())
    return f"{video_id}_{timestamp}{suffix}"


def summarize_text(text):
    logger.info(f"Summarizing text of {len(get_tokenizer().encode(text))} tokens")
    try:
        chunks = chunk_text(text)
        summaries = []
        for i, chunk in enumerate(chunks):
            chunk_tokens = len(get_tokenizer().encode(chunk))
            logger.info(f"Processing chunk {i+1}/{len(chunks)} ({chunk_tokens} tokens)")
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that summarizes text.",
                    },
                    {
                        "role": "user",
                        "content": f"Please summarize the following text:\n\n{chunk}",
                    },
                ],
                max_tokens=max_tokens,
            )
            summaries.append(response.choices[0].message.content.strip())

        logger.info(f"Summarized {len(chunks)} chunks")
        if len(summaries) > 1:
            final_summary = summarize_text(" ".join(summaries))
            return final_summary
        else:
            return summaries[0]
    except Exception as e:
        logger.error(f"Error summarizing text: {str(e)}")
        raise Exception(f"Error summarizing text: {str(e)}")


def youtext(youtube_url):
    """Main function to fetch YouTube transcript and summarize it."""
    logger.info(f"Processing YouTube URL: {youtube_url}")
    try:
        video_id = get_video_id(youtube_url)
        transcript = fetch_transcript(video_id)
        transcript_tokens = len(get_tokenizer().encode(transcript))
        logger.info(f"Fetched transcript with {transcript_tokens} tokens")
        summary = summarize_text(transcript)

        # Save transcript to temporary file
        transcript_filename = generate_unique_filename(video_id, "_transcript.txt")
        transcript_path = os.path.join(tempfile.gettempdir(), transcript_filename)
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript)
        logger.info(f"Transcript saved to: {transcript_path}")

        # Save summary to temporary file
        summary_filename = generate_unique_filename(video_id, "_summary.txt")
        summary_path = os.path.join(tempfile.gettempdir(), summary_filename)
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary)
        logger.info(f"Summary saved to: {summary_path}")

        return {
            "video_id": video_id,
            "transcript": transcript,
            "transcript_tokens": transcript_tokens,
            "summary": summary,
            "transcript_file": transcript_path,
            "summary_file": summary_path,
        }
    except Exception as e:
        logger.error(f"Error in youtext function: {str(e)}")
        return {"error": str(e)}


def get_video_id(input_string):
    """Extract video ID from YouTube URL or return the input if it's already an ID."""
    logger.info(f"Extracting video ID from input: {input_string}")
    if "youtu.be" in input_string:
        return input_string.split("/")[-1]
    elif "youtube.com" in input_string:
        return input_string.split("v=")[1].split("&")[0]
    else:
        # Assume it's already a video ID
        return input_string


def create_outline(text):
    """Create a comprehensive outline from the transcript text."""
    logger.info("Generating detailed outline from transcript")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": """Create a comprehensive outline that can serve as a standalone reference. Include:
                    - Main topics with timestamps (if available)
                    - Key points and arguments
                    - Important examples and evidence
                    - Notable quotes or statements
                    - Definitions of technical terms
                    - Conclusions and takeaways
                    
                    The outline should be detailed enough that someone wouldn't need to watch the video or read the transcript to understand the content fully.""",
                },
                {
                    "role": "user",
                    "content": f"Please create a detailed outline for this transcript:\n\n{text}",
                },
            ],
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error creating outline: {str(e)}")
        raise Exception(f"Error creating outline: {str(e)}")


def cli():
    parser = argparse.ArgumentParser(
        description="YouTube video transcript and summary tool"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Summ command
    summ_parser = subparsers.add_parser("summ", help="Summarize YouTube video")
    summ_parser.add_argument("input", help="YouTube video URL or ID")

    # Script command
    script_parser = subparsers.add_parser(
        "script", help="Fetch transcript of YouTube video"
    )
    script_parser.add_argument("input", help="YouTube video URL or ID")

    # Outline command
    outline_parser = subparsers.add_parser(
        "outline", help="Generate outline of YouTube video content"
    )
    outline_parser.add_argument("input", help="YouTube video URL or ID")

    args = parser.parse_args()

    if args.command == "summ":
        result = youtext(args.input)
        if "error" not in result:
            print(f"Summary:\n{result['summary']}")
            print(f"Summary saved to: {result['summary_file']}")
        else:
            print(f"Error: {result['error']}")
    elif args.command == "script":
        video_id = get_video_id(args.input)
        transcript = fetch_transcript(video_id)
        print(f"Transcript:\n{transcript}")
        transcript_filename = generate_unique_filename(video_id, "_transcript.txt")
        transcript_path = os.path.join(tempfile.gettempdir(), transcript_filename)
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript)
        print(f"Transcript saved to: {transcript_path}")
    elif args.command == "outline":
        video_id = get_video_id(args.input)
        transcript = fetch_transcript(video_id)
        outline = create_outline(transcript)
        print(f"Outline:\n{outline}")

        outline_filename = generate_unique_filename(video_id, "_outline.txt")
        outline_path = os.path.join(tempfile.gettempdir(), outline_filename)
        with open(outline_path, "w", encoding="utf-8") as f:
            f.write(outline)
        print(f"Outline saved to: {outline_path}")
    else:
        parser.print_help()
        sys.exit(1)


# ... rest of the file remains unchanged


if __name__ == "__main__":
    cli()

# # Example usage
# if __name__ == "__main__":
#     youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
#     logger.info(f"Starting youtext process for URL: {youtube_url}")
#     result = youtext(youtube_url)
#     logger.info(f"youtext process completed. Result: {result}")
#     if "error" not in result:
#         logger.info(f"Transcript saved to: {result['transcript_file']}")
#         logger.info(f"Summary saved to: {result['summary_file']}")
