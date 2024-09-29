from pydub import AudioSegment
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

class AudioAnalyzer:
    def __init__(self):
        pass


    def detect_silence_based_on_volume_change(self,
                                              file_path: str, 
                                              nframes:int =32, 
                                              noise_floor_threshold=10000, 
                                              min_silence_duration=0.2, 
                                              drop_factor=0.05):
        
        """
        The function `detect_silence_based_on_volume_change` analyzes audio data to detect silence
        segments based on volume changes and visualizes the results.
        
        :param file_path: The `file_path` parameter is a required input for the function
        `detect_silence_based_on_volume_change`. It should be a string that represents the file path to
        the audio file that you want to analyze for silence detection based on volume change
        :type file_path: str
        :param nframes: The `nframes` parameter in the `detect_silence_based_on_volume_change` function
        represents the number of frames or samples to process at a time while analyzing the audio data.
        It determines the chunk size in which the audio data is processed for volume analysis. A smaller
        `nframes` value, defaults to 32
        :type nframes: int (optional)
        :param noise_floor_threshold: The `noise_floor_threshold` parameter in the
        `detect_silence_based_on_volume_change` function is used to set the minimum volume level that
        will be considered as noise. Any volume level below this threshold will be ignored when
        detecting silence segments based on volume drop. This helps in filtering out low-level, defaults
        to 10000 (optional)
        :param min_silence_duration: The `min_silence_duration` parameter in the
        `detect_silence_based_on_volume_change` function represents the minimum duration of silence that
        needs to be detected in the audio file. This parameter specifies the minimum length of time (in
        seconds) that a segment of silence must last in order to
        :param drop_factor: The `drop_factor` parameter in the `detect_silence_based_on_volume_change`
        function is used to determine the threshold for detecting a significant volume drop in the audio
        data. When the percentage change in volume falls below the negative value of `drop_factor`, it
        indicates a significant volume drop, potentially
        :return: The function `detect_silence_based_on_volume_change` returns two values:
        `silence_segments` and `df`.
        """

        # Load the audio file
        audio = AudioSegment.from_file(file_path)
        
        # Get the sample rate and duration of the audio
        sample_rate = audio.frame_rate
        duration = audio.duration_seconds
        print(f"Sample rate: {sample_rate} Hz | Duration: {duration:.2f}s")

        # Convert the audio to a numpy array of samples
        samples = np.array(audio.get_array_of_samples())

        # Prepare lists for data collection
        volume_data = []  # Collects volume normalization data
        time_data = []  # Collects time values
        silence_segments = []  # Collects silenceing segments

        # Calculate the total number of samples in the audio
        total_samples = len(samples)

        # State variables for tracking silence segments
        in_silence = False
        silence_start_time = None

        # Process the audio data in chunks of nframes
        for i in range(0, len(samples), nframes):
            indata = samples[i:i + nframes]  # Read a chunk of samples

            # Calculate the volume norm for this chunk
            volume_norm = np.linalg.norm(indata) * 10

            # Calculate the corresponding time in seconds
            time_in_seconds = (i / total_samples) * duration

            # Store the time and volume for this chunk
            time_data.append(time_in_seconds)
            volume_data.append(volume_norm)

        # Create a DataFrame for analysis
        df = pd.DataFrame({"Time (s)": time_data, "Volume Norm": volume_data})

        # Ignore segments below the noise floor threshold
        df = df[df["Volume Norm"] > noise_floor_threshold].reset_index(drop=True)

        # Calculate percentage change in volume
        df['Volume Change'] = df['Volume Norm'].pct_change()

        # Detect silence segments based on volume drop
        for idx, row in df.iterrows():
            current_time = row['Time (s)']
            volume_change = row['Volume Change']

            if volume_change < -drop_factor:  # Significant volume drop detected
                if not in_silence:
                    in_silence = True
                    silence_start_time = current_time
            else:
                if in_silence:
                    silence_end_time = current_time
                    silence_duration = silence_end_time - silence_start_time

                    # If the segment duration is above the minimum silence duration, mark as a silence
                    if silence_duration >= min_silence_duration:
                        silence_segments.append((silence_start_time, silence_end_time))

                    in_silence = False
                    silence_start_time = None

        # Check if a silence was ongoing at the end of the file
        if in_silence and silence_start_time is not None:
            silence_segments.append((silence_start_time, duration))

        # Plotting the results
        sns.set(style="whitegrid")
        plt.figure(figsize=(14, 6))
        sns.lineplot(x="Time (s)", y="Volume Norm", data=df, label='Volume Norm')
        # sns.histplot(bins=duration*10)

        # Highlight silenceing segments in red
        if silence_segments:
            for start, end in silence_segments:
                plt.axvspan(start, end, color='red', alpha=0.3, label='Silence Detected' if start == silence_segments[0][0] else "")

        plt.title("Znormalizowany poziom głośności oraz wystąpienia ciszy / przerwy w przemówieniu")
        plt.xlabel("Czas [s]")
        plt.ylabel("Znormalizowany poziom głośności (dB)")
        plt.legend()
        plt.show()

        return silence_segments, df

aa = AudioAnalyzer()

# File path to the MP3 file
mp3file = '/Users/pkiszczak/projects/deviniti/MF-video/app/utils/HY_2024_film_08.mp3'

# Run the function to detect silence and get the timestamps
silence_segments, df = aa.detect_silence_based_on_volume_change(mp3file)

# Print the start and end times of detected silence segments
for start, end in silence_segments:
    print(f"Silence detected from {start:.2f}s to {end:.2f}s")