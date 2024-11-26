import argparse
import librosa
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from moviepy.editor import VideoFileClip, AudioFileClip
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import time


def compute_rms(task):
    """Compute RMS amplitude for a single frame."""
    start_idx, end_idx, y = task
    frame_data = y[start_idx:end_idx]
    if len(frame_data) > 0:
        return np.sqrt(np.mean(frame_data ** 2))
    return 0


def create_audio_visualization(file, waveform_type, num_bars, bar_width, facecolor, output, speed, bar_color, edge_color, bar_opacity, fps, ylim):
    # Load the audio file and resample
    sr_target = 22050  # Target sample rate
    y, sr = librosa.load(file, sr=sr_target)

    # Parameters for visualization
    base_frame_duration = 0.05  # Base duration of each frame in seconds (50 ms)
    frame_duration = base_frame_duration / speed  # Adjust duration based on speed
    samples_per_frame = int(frame_duration * sr)  # Samples per frame
    num_frames = len(y) // samples_per_frame  # Total number of frames

    # Prepare tasks for multiprocessing
    tasks = [
        (i * samples_per_frame, (i + 1) * samples_per_frame, y)
        for i in range(num_frames)
    ]

    print(f"Number of frames to process: {num_frames}")
    print(f"Number of processes: {cpu_count()}")

    start_time = time.time()
    print("Starting audio processing with multiprocessing...")

    # Use multiprocessing to compute RMS values
    with Pool() as pool:
        bar_heights = pool.map(compute_rms, tasks)

    end_time = time.time()
    print(f"Multiprocessing completed in {end_time - start_time:.2f} seconds.")

    # Normalize bar heights
    bar_heights = np.array(bar_heights)
    if bar_heights.max() > 0:
        bar_heights /= bar_heights.max()

    # Create the figure
    if waveform_type == "circle":
        fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(10, 10), facecolor=facecolor)
    else:
        fig, ax = plt.subplots(figsize=(10, 4), facecolor=facecolor)

    ax.set_facecolor(facecolor)
    ax.axis('off')  # Turn off axes for a cleaner look

    # Set up waveform visualizations
    if waveform_type == "bars":
        bars = ax.bar(
            np.arange(num_bars), np.zeros(num_bars), width=bar_width,
            color=bar_color, edgecolor=edge_color, alpha=bar_opacity
        )
        ax.set_xlim(-0.5, num_bars - 0.5)
        ax.set_ylim(0, ylim)

    elif waveform_type == "line":
        line, = ax.plot([], [], color=bar_color, linewidth=2)
        ax.set_xlim(0, num_bars)
        ax.set_ylim(0, ylim)

    elif waveform_type == "circle":
        bars = ax.bar(
            np.linspace(0, 2 * np.pi, num_bars, endpoint=False),  # Angles for the bars
            np.zeros(num_bars),  # Initial bar heights
            width=2 * np.pi / num_bars,  # Equal width for all bars
            color=bar_color,
            edgecolor=edge_color,
            alpha=bar_opacity,
        )
        ax.set_ylim(0, ylim)

    else:
        print(f"Error: Unsupported waveform type '{waveform_type}'. Choose from 'bars', 'line', or 'circle'.")
        return

    # Progress bar for animation
    pbar = tqdm(total=num_frames, desc="Animating frames", ncols=80)

    def update(frame):
        """Update the animation for the current frame."""
        pbar.update(1)

        # Map the bar heights to the current frame
        segment_size = len(bar_heights) // num_bars
        if segment_size > 0:
            bar_values = bar_heights[frame:frame + num_bars]
            bar_values = np.pad(bar_values, (0, num_bars - len(bar_values)), mode='constant')
        else:
            bar_values = [0] * num_bars

        # Update based on waveform type
        if waveform_type == "bars":
            for bar, height in zip(bars, bar_values):
                bar.set_height(height)
            return bars
        elif waveform_type == "line":
            line.set_data(np.arange(num_bars), bar_values)
            return line,
        elif waveform_type == "circle":
            for bar, height in zip(bars, bar_values):
                bar.set_height(height)
            return bars

    ani = FuncAnimation(fig, update, frames=num_frames, blit=True, interval=frame_duration * 1000)

    # Save the animation as a silent MP4 file
    silent_video_file = "silent_audio_visualization.mp4"
    ani.save(silent_video_file, writer='ffmpeg', fps=int(1 / frame_duration))

    # Close the progress bar
    pbar.close()

    # Add audio to the video
    final_video_file = f"{output}.mp4"
    audio_clip = AudioFileClip(file)
    video_clip = VideoFileClip(silent_video_file)

    # Combine audio and video
    final_clip = video_clip.set_audio(audio_clip)
    final_clip.write_videofile(final_video_file, codec='libx264', audio_codec='aac')

    print(f"Video saved as: {final_video_file}")


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Generate an audio visualization from an audio file.")
    parser.add_argument("file", type=str, help="Path to the audio file (e.g., .wav or .mp3)")
    parser.add_argument("--waveform_type", type=str, default="bars", help="Type of waveform: 'bars', 'line', or 'circle'")
    parser.add_argument("--num_bars", type=int, default=50, help="Number of bars/points in the visualization (default: 50)")
    parser.add_argument("--bar_width", type=float, default=0.8, help="Width of the bars in the visualization (default: 0.8)")
    parser.add_argument("--facecolor", type=str, default="black", help="Background color of the visualization (default: black)")
    parser.add_argument("--output", type=str, default="audio_visualization", help="Output file name without extension (default: audio_visualization)")
    parser.add_argument("--speed", type=float, default=1.0, help="Playback speed factor (default: 1.0, higher is faster)")
    parser.add_argument("--bar_color", type=str, default="cyan", help="Color of the bars/lines (default: cyan)")
    parser.add_argument("--edge_color", type=str, default="cyan", help="Color of the bar edges (default: cyan)")
    parser.add_argument("--bar_opacity", type=float, default=1.0, help="Opacity of the bars/lines (default: 1.0)")
    parser.add_argument("--fps", type=int, default=30, help="Frames per second for the animation (default: 30)")
    parser.add_argument("--ylim", type=float, default=1.0, help="Y-axis limit for bar heights (default: 1.0)")
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    create_audio_visualization(
        args.file, args.waveform_type, args.num_bars, args.bar_width, args.facecolor,
        args.output, args.speed, args.bar_color, args.edge_color, args.bar_opacity,
        args.fps, args.ylim
    )

