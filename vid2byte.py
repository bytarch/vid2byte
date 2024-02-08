import base64
import cv2
from io import BytesIO
import tempfile
import requests
import json

def encode_video_url_to_base64(video_url):
    try:
        # Fetch the video from the URL
        response = requests.get(video_url)
        response.raise_for_status()

        # Read the binary data of the video
        video_binary = response.content

        # Encode the binary data to base64
        base64_encoded = base64.b64encode(video_binary)

        # Convert bytes to string
        base64_string = base64_encoded.decode('utf-8')

        # Return the base64 string
        return base64_string
    except Exception as e:
        print(f"Error: {e}")
        return None

def decode_base64_to_video(base64_string, output_path, download_video):
    try:
        if download_video:
            # Decode the base64 string to binary data
            video_binary = base64.b64decode(base64_string)

            # Write the binary data to a video file
            with open(output_path, 'wb') as video_file:
                video_file.write(video_binary)
        else:
            # Use a virtual file (BytesIO) to simulate a file without downloading
            video_binary = base64.b64decode(base64_string)
            video_stream = BytesIO(video_binary)
    except Exception as e:
        print(f"Error: {e}")

def play_base64_video(base64_string):
    try:
        # Decode the base64 string to binary data
        video_binary = base64.b64decode(base64_string)

        # Create a temporary video file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
            temp_filename = temp_file.name

            # Write the binary data to the temporary file
            temp_file.write(video_binary)

        # Read the video file using OpenCV
        cap = cv2.VideoCapture(temp_filename)

        # Check if the video file is opened successfully
        if not cap.isOpened():
            print("Error: Could not open video file.")
            return

        # Play the video
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Display the frame
            cv2.imshow("Video", frame)

            # Break the loop if the 'q' key is pressed
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break

        # Release the video stream and close OpenCV windows
        cap.release()
        cv2.destroyAllWindows()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Remove the temporary video file
        if temp_filename:
            try:
                os.remove(temp_filename)
            except:
                pass

# Example usage with video URLs
video_urls = [
    'https://samplelib.com/lib/preview/mp4/sample-5s.mp4',
    # Add more video URLs as needed
]


# Boolen for download videos ( True to allow the raw data to be converted back to the mp4 file / False skips the conversion process. )
download_video=False


# Load existing saved data from .spp file if it exists
try:
    with open('decoded_videos_data.json', 'r') as spp_file:
        decoded_data = json.load(spp_file)
except FileNotFoundError:
    decoded_data = {}

for url in video_urls:
    encoded_string = encode_video_url_to_base64(url)
    output_path = f"{video_urls.index(url)}_decoded_video.mp4"
    decode_base64_to_video(encoded_string, output_path, download_video)

    # Save decoded string and video URL to the dictionary
    decoded_data[output_path] = {'base64_string': encoded_string, 'video_url': url}


# Save the updated dictionary to .spp file
with open('decoded_videos_data.json', 'w') as spp_file:
    json.dump(decoded_data, spp_file, indent=2)

# Choose a video index from the JSON data to play (e.g., the first video)
video_index_to_play = 0

# Get the base64 string from the chosen video index
video_path = list(decoded_data.keys())[video_index_to_play]
base64_string_to_play = decoded_data[video_path]['base64_string']

# Play the video from base64 string
play_base64_video(base64_string_to_play)