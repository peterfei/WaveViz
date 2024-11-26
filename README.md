# WaveViz

WaveViz is a powerful and flexible tool for creating stunning audio visualizations. It supports multiple waveform styles (bars, line, circle) and allows you to easily transform audio files into captivating videos with synchronized waveforms.

## Features

- **Multiple Waveform Types**: Choose from `bars`, `line`, or `circle`.
- **Customizable Visualizations**: Adjust bar count, bar width, colors, opacity, and more.
- **Audio Synchronization**: Automatically syncs waveform animations with audio playback.
- **High Performance**: Utilizes multiprocessing for fast audio processing.
- **Easy Output**: Exports MP4 videos with embedded audio.

------

## Installation

1. Ensure you have Python 3.8 or later installed.

2. Install required dependencies:

```bash
pip install numpy librosa matplotlib moviepy tqdm
```

------

## Usage

Run the script with the following command:

```bash
python waveviz.py <audio_file> [options]
```

### Positional Arguments:

- **`audio_file`**: Path to the input audio file (e.g., `.wav`, `.mp3`).

### Optional Arguments:

| Argument          | Description                                       | Default               |
| ----------------- | ------------------------------------------------- | --------------------- |
| `--waveform_type` | Type of waveform: `bars`, `line`, or `circle`.    | `bars`                |
| `--num_bars`      | Number of bars/points in the visualization.       | 50                    |
| `--bar_width`     | Width of the bars in the visualization.           | 0.8                   |
| `--facecolor`     | Background color of the visualization.            | `black`               |
| `--bar_color`     | Color of the bars/lines.                          | `cyan`                |
| `--edge_color`    | Edge color of the bars (for `bars` or `circle`).  | `cyan`                |
| `--bar_opacity`   | Opacity of the bars/lines (0.0 to 1.0).           | 1.0                   |
| `--speed`         | Playback speed factor (higher values are faster). | 1.0                   |
| `--fps`           | Frames per second for the animation.              | 30                    |
| `--ylim`          | Y-axis limit for bar heights.                     | 1.0                   |
| `--output`        | Output file name without extension.               | `audio_visualization` |

------

## Examples

### Default Visualization (Bars)

```bash
python waveviz.py your_audio_file.wav
```

### Line Waveform with Custom Colors

```bash
python waveviz.py your_audio_file.wav --waveform_type line --bar_color red --facecolor white
```

### Circular Waveform

```bash
python waveviz.py your_audio_file.wav --waveform_type circle --num_bars 100 --ylim 1.5
```

### Faster Playback with More Bars

```
python waveviz.py your_audio_file.wav --speed 2.0 --num_bars 80 --fps 60
```

------

## Example Output

Here’s an example of what WaveViz can produce:

![image-20241126172544016](http://image-peterfei-blog.test.upcdn.net/image-20241126172544016.png)

![image-20241126172634267](http://image-peterfei-blog.test.upcdn.net/image-20241126172634267.png)

![image-20241126184748156](http://image-peterfei-blog.test.upcdn.net/image-20241126184748156.png)

------

## How It Works

1. **Audio Processing**:
   - The tool uses `librosa` to analyze the audio file and divide it into frames.
   - RMS (Root Mean Square) values are calculated to represent audio intensity for each frame.
2. **Waveform Rendering**:
   - `matplotlib` is used to create dynamic animations of the waveform.
   - The tool supports multiple waveform styles: `bars`, `line`, and `circle`.
3. **Video Export**:
   - The silent waveform animation is exported as an MP4 video.
   - The original audio is synchronized with the video using `moviepy`.

------

## Troubleshooting

- Error: "ffmpeg not found":

  - Install 

    ```
    ffmpeg
    ```
  
     on your system:

    ```
    sudo apt install ffmpeg  # For Ubuntu
    brew install ffmpeg      # For macOS
    ```
  
- Slow Processing:

  - Ensure you are running the script on a multi-core CPU. WaveViz uses multiprocessing to speed up audio processing.

------

## Contributing

Contributions are welcome! If you encounter issues or have feature requests, feel free to submit a pull request or open an issue.

------

## License

WaveViz is licensed under the MIT License. See the `LICENSE` file for details.

------

Let me know if you'd like additional sections or modifications for this `README.md`! 🚀