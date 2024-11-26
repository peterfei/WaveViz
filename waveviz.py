import argparse
import librosa
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from moviepy.editor import VideoFileClip, AudioFileClip
from multiprocessing import Pool
from tqdm import tqdm

def compute_bar_height(task):
    """Compute the RMS amplitude for a given frame."""
    start_idx, end_idx, y = task
    frame_data = y[start_idx:end_idx]
    return np.sqrt(np.mean(frame_data ** 2))

def generate_waveform(wave_type, duration, sr, frequency=440, amplitude=1.0):
    """Generate different types of waveforms."""
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    
    if wave_type == 'sine':
        return amplitude * np.sin(2 * np.pi * frequency * t)
    elif wave_type == 'square':
        return amplitude * np.sign(np.sin(2 * np.pi * frequency * t))
    elif wave_type == 'triangle':
        return amplitude * 2 * (2 * (t * frequency - np.floor(t * frequency + 0.5))) - 1
    elif wave_type == 'sawtooth':
        return amplitude * 2 * (t * frequency - np.floor(t * frequency + 0.5))
    else:
        raise ValueError(f"Unsupported wave type: {wave_type}")

def create_audio_visualization(file, wave_type, num_bars, bar_width, facecolor, output, speed):
    # Load the audio file or generate a waveform
    sr_target = 22050  # Target sample rate
    if file:
        y, sr = librosa.load(file, sr=sr_target)
    else:
        duration = 5  # 5 seconds for example
        y = generate_waveform(wave_type, duration, sr_target)
        sr = sr_target  # Use the default sample rate
    
    # Parameters for bar visualization
    base_frame_duration = 0.05  # Base duration of each frame in seconds (50 ms)
    frame_duration = base_frame_duration / speed  # Adjust duration based on speed
    samples_per_frame = int(frame_duration * sr)  # Samples per frame
    num_frames = len(y) // samples_per_frame  # Total number of frames

    # Prepare tasks for multiprocessing
    tasks = [
        (i * samples_per_frame, (i + 1) * samples_per_frame, y)
        for i in range(num_frames)
    ]

    print("Starting audio processing with multiprocessing...")
    # Use multiprocessing to compute bar heights in parallel
    with Pool() as pool:
        bar_heights = pool.map(compute_bar_height, tasks)

    # Normalize bar heights for better visualization
    bar_heights = np.array(bar_heights)
    bar_heights /= bar_heights.max()  # Normalize to range [0, 1]

    # Visualization parameters
    bar_x = np.arange(num_bars)  # X positions of the bars

    # Create the figure
    fig, ax = plt.subplots(figsize=(10, 4), facecolor=facecolor)
    ax.set_facecolor(facecolor)  # Set background color
    bars = ax.bar(bar_x, np.zeros(num_bars), width=bar_width, color='cyan', edgecolor='cyan')

    # Customize the plot
    ax.set_xlim(-0.5, num_bars - 0.5)
    ax.set_ylim(0, 1)
    ax.axis('off')  # Turn off axis

    # Create a tqdm progress bar
    pbar = tqdm(total=num_frames, desc="Animating frames", ncols=80)

    # Update function for animation
    def update(frame):
        pbar.update(1)  # Update the progress bar for each frame
        # Update bar heights for the current frame
        start_idx = frame * samples_per_frame
        end_idx = start_idx + samples_per_frame
        frame_data = y[start_idx:end_idx]
        
        # Smoothly distribute data across bars
        segment_size = len(frame_data) // num_bars
        if segment_size > 0:
            bar_values = [
                np.sqrt(np.mean(frame_data[i * segment_size:(i + 1) * segment_size] ** 2))
                for i in range(num_bars)
            ]
        else:
            bar_values = [0] * num_bars  # If no data is available, show empty bars

        # Normalize bar values
        bar_values = np.array(bar_values) / max(bar_heights)
        
        # Update bar heights
        for bar, height in zip(bars, bar_values):
            bar.set_height(height)
        return bars

    # Create the animation
    ani = FuncAnimation(fig, update, frames=num_frames, blit=True, interval=frame_duration * 1000)

    # Save the animation as a silent MP4 file
    silent_video_file = "silent_audio_visualization.mp4"
    ani.save(silent_video_file, writer='ffmpeg', fps=int(1 / frame_duration))

    # Close the progress bar
    pbar.close()

    # Add audio to the video (if original audio is provided)
    final_video_file = f"{output}.mp4"
    if file:
        audio_clip = AudioFileClip(file)
        video_clip = VideoFileClip(silent_video_file)
        final_clip = video_clip.set_audio(audio_clip)
        final_clip.write_videofile(final_video_file, codec='libx264', audio_codec='aac')
    else:
        # If no file, just save the silent video
        final_video_file = "silent_" + final_video_file
        print(f"Video saved as: {final_video_file}")

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Generate an audio visualization from an audio file or waveform.")
    parser.add_argument(
        "file", type=str, nargs="?", default=None, help="Path to the audio file (e.g., .wav or .mp3)"
    )
    parser.add_argument(
        "--wave_type", type=str, choices=['sine', 'square', 'triangle', 'sawtooth'], default='sine',
        help="Waveform type for visualization (default: sine)"
    )
    parser.add_argument(
        "--num_bars", type=int, default=50, help="Number of bars in the visualization (default: 50)"
    )
    parser.add_argument(
        "--bar_width", type=float, default=0.8, help="Width of the bars in the visualization (default: 0.8)"
    )
    parser.add_argument(
        "--facecolor", type=str, default="black", help="Background color of the visualization (default: black)"
    )
    parser.add_argument(
        "--output", type=str, default="audio_visualization", help="Output file name without extension (default: audio_visualization)"
    )
    parser.add_argument(
        "--speed", type=float, default=1.0, help="Playback speed factor (default: 1.0, higher is faster)"
    )
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    create_audio_visualization(
        args.file, args.wave_type, args.num_bars, args.bar_width, args.facecolor, args.output, args.speed
    )
