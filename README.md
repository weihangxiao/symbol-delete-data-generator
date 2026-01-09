# Symbol Delete Task Generator 🗑️

A data generator for creating synthetic visual reasoning tasks where a symbol must be deleted from a specific position in a sequence. This task tests a model's ability to understand positional reasoning and sequence manipulation through visual animation.

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/weihangxiao/symbol-delete-data-generator.git
cd symbol-delete-data-generator

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# 4. Generate tasks
python examples/generate.py --num-samples 50
```

---

## 📋 Task Description

The **Symbol Delete Task** (Symbol Worlds_SymbolEditing_2) is a visual reasoning task where:

- **Initial State**: A sequence of symbols displayed horizontally
- **Goal**: Delete a specific symbol at a given position from the sequence
- **Animation**: The target symbol fades out, then remaining symbols shift left to close the gap
- **Solution**: Exactly **one unique solution** - delete symbol S at position P

### Key Features

- ✅ **Unique Solution**: Only one way to delete at a specific position
- ✅ **Clear Visual Reasoning**: Animation shows fade-out → shift-left sequence
- ✅ **Scalable**: 10K+ unique samples with 99% uniqueness
- ✅ **Fast Generation**: No complex solving algorithms required
- ✅ **Short Videos**: ~2.8 seconds per video (well under 10s limit)

---

## 📁 Project Structure

```
symbol-delete-data-generator/
├── core/                    # Core utilities (framework code)
│   ├── base_generator.py   # Abstract base class
│   ├── schemas.py          # Pydantic models
│   ├── image_utils.py      # Image rendering helpers
│   ├── video_utils.py      # Video generation utilities
│   └── output_writer.py    # File output management
├── src/                     # Task-specific implementation
│   ├── generator.py        # Symbol delete task generator
│   ├── prompts.py          # Task instruction prompts
│   └── config.py           # Task configuration
├── examples/
│   └── generate.py         # Entry point script
└── data/                    # Generated output
    └── questions/
        └── symbol_delete_task/
            └── symbol_delete_0000/
                ├── first_frame.png
                ├── final_frame.png
                ├── prompt.txt
                └── ground_truth.mp4
```

---

## 📦 Output Format

Each generated task produces:

```
data/questions/symbol_delete_task/{task_id}/
├── first_frame.png          # Initial state: sequence before deletion
├── final_frame.png          # Final state: sequence after deletion
├── prompt.txt               # Task instructions
└── ground_truth.mp4         # Solution animation video (~2.8 seconds)
```

### Output Details

- **first_frame.png**: Shows the initial sequence of symbols (e.g., [●, ▲, ■, ★, ◆])
- **final_frame.png**: Shows the final sequence with symbol deleted (e.g., [●, ▲, ★, ◆])
- **prompt.txt**: Contains instructions specifying which symbol to delete and at which position (e.g., "Delete symbol ■ at position 3")
- **ground_truth.mp4**: Animated video showing:
  - Initial sequence held for 0.5s
  - Target symbol fading out (0.8s)
  - Remaining symbols shifting left to close gap (1.0s)
  - Final sequence held for 0.5s
  - **Total duration: ~2.8 seconds**

---

## ⚙️ Configuration

All task parameters are configured in `src/config.py`:

```python
class TaskConfig(GenerationConfig):
    domain: str = "symbol_delete"
    image_size: tuple[int, int] = (800, 200)

    # Symbol set selection
    symbol_set: str = "shapes"  # Options: shapes, letters, numbers, mixed

    # Sequence configuration
    min_sequence_length: int = 5   # Minimum symbols in initial sequence
    max_sequence_length: int = 9   # Maximum symbols in initial sequence

    # Visual configuration
    symbol_size: int = 60          # Symbol size in pixels

    # Video settings
    generate_videos: bool = True
    video_fps: int = 10
```

### Available Symbol Sets

- **shapes**: ●, ▲, ■, ★, ◆, ♥, ◯, △, □, ☆, ◇, ♦, ▼, ▶, ◀ (15 symbols)
- **letters**: A-Z (26 symbols)
- **numbers**: 0-9 (10 symbols)
- **mixed**: Combination of shapes, letters, and numbers (13 symbols)

---

## 🎬 Generation Algorithm

The generator uses a simple but effective approach:

1. **Sequence Generation**: Randomly select N symbols (5-9) from chosen symbol set without replacement
2. **Delete Position Selection**: Randomly select deletion position (1 to N)
3. **Final Sequence Creation**: Remove symbol at target position
4. **Color Assignment**: Assign distinct colors to each unique symbol for visual clarity
5. **Animation Creation**: Generate smooth animation frames:
   - Phase 1: Fade-out (8 frames) - Target symbol disappears with decreasing opacity
   - Phase 2: Shift-left (10 frames) - Remaining symbols shift left to close gap
   - Hold frames at start and end (5 frames each)

### Key Features

- ✅ **Guaranteed Uniqueness**: Each task has exactly one solution path
- ✅ **Pure White Background**: RGB(255, 255, 255) for clean visual presentation
- ✅ **Colorful Symbols**: 10 distinct colors assigned consistently
- ✅ **Smooth Animation**: Linear interpolation for all movements
- ✅ **Fast Generation**: ~1 sample/second, no complex algorithms

---

## 📝 Usage Examples

### Generate 100 tasks with shapes (default)

```bash
python examples/generate.py --num-samples 100
```

### Generate 1000 tasks with letters

```bash
python examples/generate.py --num-samples 1000 --symbol-set letters
```

### Generate 500 tasks with custom sequence length

```bash
python examples/generate.py --num-samples 500 --min-length 6 --max-length 9
```

### Generate without videos (faster)

```bash
python examples/generate.py --num-samples 10000 --no-videos
```

### Generate with specific random seed

```bash
python examples/generate.py --num-samples 200 --seed 42
```

### Generate with custom output directory

```bash
python examples/generate.py --num-samples 50 --output data/my_custom_output
```

---

## 🔧 Command Line Options

```bash
python examples/generate.py --help
```

Options:
- `--num-samples`: Number of task samples to generate (required)
- `--symbol-set`: Symbol set to use: shapes, letters, numbers, mixed (default: shapes)
- `--min-length`: Minimum sequence length (default: 5)
- `--max-length`: Maximum sequence length (default: 9)
- `--output`: Output directory (default: `data/questions`)
- `--seed`: Random seed for reproducibility (optional)
- `--no-videos`: Disable video generation (faster)

---

## 📚 Dependencies

See `requirements.txt` for the complete list. Main dependencies:

- `numpy`: Numerical operations
- `Pillow`: Image processing and rendering
- `pydantic`: Configuration management
- `opencv-python`: Video generation

No specialized dependencies required (unlike chess, maze solvers, etc.)

---

## 🎯 Task Characteristics

### Scalability Analysis

- **3x3 Combinations**: ~15 symbols × 5 lengths × avg 7 positions = **500+ base variations**
- **With randomization**: Each sequence is randomly generated, creating **10K+ unique samples**
- **Measured uniqueness**: 99% unique in 100-sample test

### Video Specifications

- **Frame breakdown**:
  - Hold initial: 5 frames (0.5s)
  - Fade out: 8 frames (0.8s)
  - Shift left: 10 frames (1.0s)
  - Hold final: 5 frames (0.5s)
- **Total**: 28 frames at 10 FPS = **2.8 seconds**
- **Status**: ✅ Well under 10-second limit

### Prompt Specifications

- **Average length**: ~30 words
- **Format**: "Delete symbol {S} at position {P}. [Animation description]"
- **Status**: ✅ Well under 200-word limit

---

## 🎨 Visual Design

- **Background**: Pure white (255, 255, 255)
- **Symbol Colors**: 10 distinct colors from a diverse palette
- **Symbol Size**: 60 pixels (configurable)
- **Spacing**: 20 pixels between symbols
- **Centering**: Sequences are centered horizontally and vertically

---

## 📊 Quality Metrics

Based on 100-sample test:

| Metric | Result | Target | Status |
|--------|--------|--------|--------|
| Uniqueness | 99% | >95% | ✅ Pass |
| Video Length | 2.8s | <10s | ✅ Pass |
| Prompt Length | 30 words | <200 words | ✅ Pass |
| Generation Speed | ~1 sample/sec | N/A | ✅ Fast |
| Solution Uniqueness | 100% | 100% | ✅ Pass |

---

## 🏷️ Task Type

**Symbol Worlds → SymbolEditing → Symbol Worlds_SymbolEditing_2**

- **Task Name**: Delete Target Symbol
- **Description**: Delete a symbol at a specific position from a sequence
- **Reasoning Type**: Visual reasoning through symbol manipulation

---

## 📄 License

See `LICENSE` file for details.

---
