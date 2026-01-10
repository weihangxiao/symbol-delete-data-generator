"""Symbol Delete Task generator - Delete symbol from sequence."""

import random
from typing import List, Optional
from PIL import Image, ImageDraw, ImageFont
from core import BaseGenerator, TaskPair, ImageRenderer
from core.video_utils import VideoGenerator
from .config import TaskConfig
from .prompts import get_prompt


# Symbol sets
SYMBOL_SETS = {
    "shapes": ["●", "▲", "■", "★", "◆", "♥", "◯", "△", "□", "☆", "◇", "♦", "▼", "▶", "◀"],
    "letters": list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
    "numbers": list("0123456789"),
    "mixed": ["●", "▲", "■", "★", "A", "B", "C", "1", "2", "3", "X", "Y", "Z"]
}

# Colors for symbols (diverse palette)
SYMBOL_COLORS = [
    (220, 60, 60),    # Red
    (60, 60, 220),    # Blue
    (60, 180, 60),    # Green
    (220, 160, 60),   # Orange
    (160, 60, 220),   # Purple
    (60, 180, 180),   # Cyan
    (220, 60, 160),   # Pink
    (100, 150, 60),   # Olive
    (220, 120, 60),   # Coral
    (80, 80, 200),    # Indigo
]


class SymbolDeleteGenerator(BaseGenerator):
    """Generates symbol deletion tasks."""

    def __init__(self, config: TaskConfig):
        super().__init__(config)
        self.renderer = ImageRenderer(image_size=config.image_size)
        self.video_generator = None
        if config.generate_videos and VideoGenerator.is_available():
            self.video_generator = VideoGenerator(fps=config.video_fps, output_format="mp4")

        # Select symbol set
        self.symbols = SYMBOL_SETS.get(config.symbol_set, SYMBOL_SETS["shapes"])

        # Colors
        self.bg_color = (255, 255, 255)  # Pure white background
        self.border_color = (60, 60, 60)
        self.text_color = (40, 40, 40)

    def generate_task_pair(self, task_id: str) -> TaskPair:
        """Generate one symbol deletion task."""
        # Generate initial sequence
        seq_length = random.randint(self.config.min_sequence_length, self.config.max_sequence_length)

        # Pick symbols without replacement for the sequence
        sequence = random.sample(self.symbols, seq_length)

        # Pick which symbol to delete (random position)
        delete_position = random.randint(0, len(sequence) - 1)
        delete_symbol = sequence[delete_position]

        # Create final sequence (without the deleted symbol)
        final_sequence = sequence[:delete_position] + sequence[delete_position + 1:]

        # Assign colors to symbols
        color_map = self._create_color_map(sequence)

        # Render images
        first_image = self._render_sequence(sequence, color_map)
        final_image = self._render_sequence(final_sequence, color_map)

        # Generate video if enabled
        video_path = None
        if self.config.generate_videos and self.video_generator:
            video_path = self._generate_video(
                sequence, final_sequence, delete_symbol, delete_position, color_map, task_id
            )

        # Get prompt (1-indexed position for human readability)
        prompt = get_prompt(delete_symbol, delete_position + 1, len(sequence))

        return TaskPair(
            task_id=task_id,
            domain=self.config.domain,
            prompt=prompt,
            first_image=first_image,
            final_image=final_image,
            ground_truth_video=video_path
        )

    def _create_color_map(self, all_symbols: List[str]) -> dict:
        """Assign consistent colors to symbols."""
        color_map = {}
        for i, symbol in enumerate(set(all_symbols)):
            color_map[symbol] = SYMBOL_COLORS[i % len(SYMBOL_COLORS)]
        return color_map

    def _render_sequence(self, sequence: List[str], color_map: dict) -> Image.Image:
        """Render a sequence of symbols."""
        width, height = self.config.image_size
        img = Image.new("RGB", (width, height), self.bg_color)
        draw = ImageDraw.Draw(img)

        if not sequence:
            return img

        # Calculate symbol spacing
        symbol_size = self.config.symbol_size
        spacing = symbol_size + 20
        total_width = len(sequence) * spacing - 20
        start_x = (width - total_width) // 2
        center_y = height // 2

        # Load font - try fonts with good Unicode symbol support
        font_size = symbol_size
        font = self._get_unicode_font(font_size)

        # Draw each symbol
        for i, symbol in enumerate(sequence):
            x = start_x + i * spacing
            self._draw_symbol(draw, symbol, x, center_y, symbol_size, color_map[symbol], font)

        return img

    def _draw_symbol(self, draw: ImageDraw.Draw, symbol: str, x: int, y: int,
                    size: int, color: tuple, font: ImageFont.FreeTypeFont):
        """Draw a single symbol at position (x, y)."""
        # Get text bounding box
        bbox = draw.textbbox((0, 0), symbol, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Center the text
        text_x = x - text_width // 2
        text_y = y - text_height // 2

        # Draw the symbol
        draw.text((text_x, text_y), symbol, fill=color, font=font)

    def _get_unicode_font(self, font_size: int) -> ImageFont.FreeTypeFont:
        """Get a font that supports Unicode symbols well."""
        # Try fonts in order of preference (best Unicode symbol support first)
        font_paths = [
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",  # macOS - excellent Unicode support
            "/Library/Fonts/Arial Unicode.ttf",  # macOS alternative location
            "/System/Library/Fonts/Apple Symbols.ttf",  # macOS - good for symbols
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",  # Linux
            "Arial Unicode MS",  # Cross-platform name
            "DejaVu Sans",  # Cross-platform name
            "Segoe UI Symbol",  # Windows
        ]

        for font_path in font_paths:
            try:
                return ImageFont.truetype(font_path, font_size)
            except (OSError, IOError):
                continue

        # Final fallback
        return ImageFont.load_default()

    def _generate_video(self, initial_seq: List[str], final_seq: List[str],
                       delete_symbol: str, delete_pos: int, color_map: dict,
                       task_id: str) -> Optional[str]:
        """Generate video showing the deletion animation."""
        import tempfile
        from pathlib import Path

        temp_dir = Path(tempfile.gettempdir()) / f"{self.config.domain}_videos"
        temp_dir.mkdir(parents=True, exist_ok=True)
        video_path = temp_dir / f"{task_id}_ground_truth.mp4"

        frames = self._create_animation_frames(
            initial_seq, final_seq, delete_symbol, delete_pos, color_map
        )
        result = self.video_generator.create_video_from_frames(frames, video_path)
        return str(result) if result else None

    def _create_animation_frames(self, initial_seq: List[str], final_seq: List[str],
                                 delete_symbol: str, delete_pos: int, color_map: dict,
                                 hold_frames: int = 5,
                                 fade_frames: int = 8,
                                 shift_frames: int = 10) -> List[Image.Image]:
        """Create animation frames for symbol deletion."""
        frames = []

        # Show initial sequence
        frames.extend([self._render_sequence(initial_seq, color_map)] * hold_frames)

        # Phase 1: Target symbol fades out
        for i in range(fade_frames):
            progress = (i + 1) / fade_frames
            frame = self._render_fade_out_frame(initial_seq, delete_symbol, delete_pos,
                                                color_map, progress)
            frames.append(frame)

        # Phase 2: Remaining symbols shift left to close the gap
        for i in range(shift_frames):
            progress = (i + 1) / shift_frames
            frame = self._render_shift_frame(initial_seq, delete_pos, color_map, progress)
            frames.append(frame)

        # Show final sequence
        frames.extend([self._render_sequence(final_seq, color_map)] * hold_frames)

        return frames

    def _render_fade_out_frame(self, sequence: List[str], target_symbol: str,
                               delete_pos: int, color_map: dict,
                               fade_progress: float) -> Image.Image:
        """Render frame with target symbol fading out."""
        width, height = self.config.image_size
        symbol_size = self.config.symbol_size
        spacing = symbol_size + 20

        # Create base image
        img = Image.new('RGB', (width, height), self.bg_color)
        draw = ImageDraw.Draw(img)

        # Calculate layout
        total_width = len(sequence) * spacing - 20
        start_x = (width - total_width) // 2
        center_y = height // 2

        # Load font - try fonts with good Unicode symbol support
        font_size = symbol_size
        font = self._get_unicode_font(font_size)

        # Draw all symbols
        for i, symbol in enumerate(sequence):
            x = start_x + i * spacing
            if i == delete_pos:
                # Draw fading symbol
                alpha = int(255 * (1 - fade_progress))
                overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
                overlay_draw = ImageDraw.Draw(overlay)

                color = color_map[symbol]
                rgba_color = (*color, alpha)

                bbox = overlay_draw.textbbox((0, 0), symbol, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                text_x = x - text_width // 2
                text_y = center_y - text_height // 2

                overlay_draw.text((text_x, text_y), symbol, fill=rgba_color, font=font)

                # Composite
                img = img.convert('RGBA')
                img = Image.alpha_composite(img, overlay)
                img = img.convert('RGB')
            else:
                # Draw normal symbol
                self._draw_symbol(draw, symbol, x, center_y, symbol_size, color_map[symbol], font)

        return img

    def _render_shift_frame(self, initial_seq: List[str], delete_pos: int,
                           color_map: dict, progress: float) -> Image.Image:
        """Render frame with symbols shifting left to close gap."""
        width, height = self.config.image_size
        symbol_size = self.config.symbol_size
        spacing = symbol_size + 20
        center_y = height // 2

        # Calculate initial layout (keep this consistent, don't re-center)
        initial_total_width = len(initial_seq) * spacing - 20
        start_x = (width - initial_total_width) // 2

        # Create image
        img = Image.new('RGB', (width, height), self.bg_color)
        draw = ImageDraw.Draw(img)

        # Load font - try fonts with good Unicode symbol support
        font_size = symbol_size
        font = self._get_unicode_font(font_size)

        # Draw symbols with interpolated positions (skip deleted symbol)
        for i, symbol in enumerate(initial_seq):
            if i == delete_pos:
                continue  # Skip the deleted symbol

            if i < delete_pos:
                # Symbols before deletion: stay in original position (no movement)
                current_x = start_x + i * spacing
            else:
                # Symbols after deletion: shift left by one spacing unit to close gap
                initial_x = start_x + i * spacing
                final_x = start_x + (i - 1) * spacing  # Shift left by one position
                current_x = initial_x + (final_x - initial_x) * progress

            self._draw_symbol(draw, symbol, int(current_x), center_y,
                            symbol_size, color_map[symbol], font)

        return img
