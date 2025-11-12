"""Sigil generation for servitors"""

import math
from pathlib import Path
from typing import Tuple, Dict, Optional
from PIL import Image, ImageDraw


class SigilGenerator:
    """Generates sigils from text using witch wheel or random positioning"""
    
    def __init__(self, canvas_size: int = 500):
        """Initialize sigil generator"""
        self.canvas_size = canvas_size
        self.center = (canvas_size / 2, canvas_size / 2)
        self.outer_radius = (canvas_size / 2) - 10
        self.radius_steps = [
            self.outer_radius * 0.3,
            self.outer_radius * 0.6,
            self.outer_radius
        ]
        self.characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    
    def _create_witch_wheel_mapping(self) -> Dict[str, Tuple[float, float]]:
        """Create witch wheel character mapping"""
        mapping = {}
        circles = [
            "VWXYZ0123",
            "NOPQRSTU4567",
            "ABCDEFGHIJKLM89"
        ]
        
        for circle_idx, circle in enumerate(circles):
            angle_increment = (2 * math.pi) / len(circle)
            start_angle = -math.pi / 2
            
            for i, char in enumerate(circle):
                angle = start_angle + angle_increment * i
                radius = self.radius_steps[circle_idx]
                x = self.center[0] + radius * math.cos(angle)
                y = self.center[1] + radius * math.sin(angle)
                mapping[char] = (x, y)
        
        return mapping
    
    def _create_random_mapping(self) -> Dict[str, Tuple[float, float]]:
        """Create random character positioning within circles"""
        import random
        mapping = {}
        num_rings = len(self.radius_steps)
        
        for char in self.characters:
            ring_index = random.randint(0, num_rings - 1)
            radius = self.radius_steps[ring_index]
            angle = random.uniform(0, 2 * math.pi)
            
            x = self.center[0] + radius * math.cos(angle)
            y = self.center[1] + radius * math.sin(angle)
            mapping[char] = (x, y)
        
        return mapping
    
    def generate_sigil(
        self,
        text: str,
        position_type: str = "witch_wheel",
        unique_chars: bool = True,
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Generate a sigil from text
        
        Args:
            text: Input text to convert to sigil
            position_type: "witch_wheel" or "random"
            unique_chars: If True, only use unique characters
            output_path: Path to save the sigil image
        
        Returns:
            Path to the generated sigil image
        """
        # Clean and prepare text
        cleaned = text.upper().replace(" ", "")
        cleaned = "".join(c for c in cleaned if c in self.characters)
        
        if unique_chars:
            # Remove duplicates while preserving order
            seen = set()
            cleaned = "".join(c for c in cleaned if c not in seen and not seen.add(c))
        
        if len(cleaned) < 1:
            raise ValueError("No valid characters found in text")
        
        # Create mapping
        if position_type == "witch_wheel":
            mapping = self._create_witch_wheel_mapping()
        else:
            mapping = self._create_random_mapping()
        
        # Get points for characters
        points = [mapping[char] for char in cleaned if char in mapping]
        
        if len(points) < 1:
            raise ValueError("No valid points generated")
        
        # Create image
        img = Image.new("RGB", (self.canvas_size, self.canvas_size), "white")
        draw = ImageDraw.Draw(img)
        
        # Draw outer circle
        draw.ellipse(
            [
                self.center[0] - self.outer_radius,
                self.center[1] - self.outer_radius,
                self.center[0] + self.outer_radius,
                self.center[1] + self.outer_radius
            ],
            outline="black",
            width=2
        )
        
        # Draw lines connecting points
        for i in range(len(points) - 1):
            draw.line(
                [points[i][0], points[i][1], points[i + 1][0], points[i + 1][1]],
                fill="black",
                width=2
            )
        
        # Save image
        if output_path is None:
            # Generate filename from text
            safe_name = "".join(c for c in cleaned if c.isalnum())[:20]
            output_path = Path(f"{safe_name}_sigil.png")
        
        img.save(output_path)
        return Path(output_path)
    
    def generate_from_servitor(
        self,
        servitor_name: str,
        servitor_purpose: str,
        position_type: str = "witch_wheel",
        output_dir: Path = None
    ) -> Path:
        """
        Generate sigil from servitor name and purpose
        
        Args:
            servitor_name: Name of the servitor
            servitor_purpose: Purpose/intention of the servitor
            position_type: "witch_wheel" or "random"
            output_dir: Directory to save sigil
        
        Returns:
            Path to generated sigil
        """
        # Combine name and purpose for sigil generation
        combined_text = f"{servitor_name} {servitor_purpose}"
        
        if output_dir is None:
            output_dir = Path(".")
        
        safe_name = "".join(c for c in servitor_name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_name = safe_name.replace(' ', '_')
        output_path = output_dir / f"{safe_name}_sigil.png"
        
        return self.generate_sigil(
            combined_text,
            position_type=position_type,
            unique_chars=True,
            output_path=output_path
        )

