
import cv2
import numpy as np
import matplotlib.pyplot as plt

COLORS = {
    "White": (245, 245, 245),
    "Yellow": (245, 215, 40),
    "Red": (220, 55, 60),
    "Orange": (245, 135, 35),
    "Blue": (55, 105, 215),
    "Green": (45, 170, 95)
}

SYMBOLS = {
    "White": "X",
    "Yellow": "*",
    "Red": "A",
    "Orange": "+",
    "Blue": "#",
    "Green": "O"
}


def classify_color(bgr):
    pixel = np.uint8([[bgr]])

    hsv = cv2.cvtColor(
        pixel,
        cv2.COLOR_BGR2HSV
    )[0, 0]

    h, s, v = map(int, hsv)

    if v < 55:
        return "Unknown"

    if s < 60:
        return "White" if v > 125 else "Unknown"

    if h < 10 or h >= 170:
        return "Red"

    if h < 22:
        return "Orange"

    if h < 39:
        return "Yellow"

    if h < 88:
        return "Green"

    if h < 138:
        return "Blue"

    return "Red"


def sample_face(frame):
    height, width = frame.shape[:2]

    size = int(min(height, width) * 0.60)

    x0 = (width - size) // 2
    y0 = (height - size) // 2

    step = size / 3

    detected = []
    rectangles = []

    for row in range(3):
        for col in range(3):
            x1 = int(x0 + col * step)
            y1 = int(y0 + row * step)

            x2 = int(x0 + (col + 1) * step)
            y2 = int(y0 + (row + 1) * step)

            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)

            radius = max(3, int(step * 0.15))

            patch = frame[
                max(0, cy-radius):min(height, cy+radius),
                max(0, cx-radius):min(width, cx+radius)
            ]

            if patch.size == 0:
                color = "Unknown"
            else:
                median = np.median(
                    patch.reshape(-1, 3),
                    axis=0
                ).astype(np.uint8)

                color = classify_color(median)

            detected.append(color)
            rectangles.append((x1, y1, x2, y2))

    return detected, rectangles


def annotate(frame, colors):
    display = frame.copy()

    _, rectangles = sample_face(frame)

    for color, rect in zip(colors, rectangles):
        x1, y1, x2, y2 = rect

        cv2.rectangle(
            display,
            (x1, y1),
            (x2, y2),
            (255, 255, 255),
            2
        )

        symbol = SYMBOLS.get(color, "?")

        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)

        cv2.putText(
            display,
            symbol,
            (cx - 10, cy + 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 0, 0),
            5
        )

        cv2.putText(
            display,
            symbol,
            (cx - 10, cy + 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (255, 255, 255),
            2
        )

    return display


def visualize_colors():
    fig, axes = plt.subplots(
        2, 3,
        figsize=(10, 6)
    )

    for ax, (name, rgb) in zip(
        axes.flat,
        COLORS.items()
    ):
        sample = np.full(
            (100, 100, 3),
            rgb,
            dtype=np.uint8
        )

        predicted = classify_color(rgb[::-1])

        ax.imshow(sample)

        ax.set_title(
            f"{name} → {predicted}\n"
            f"Symbol: {SYMBOLS[name]}"
        )

        ax.axis("off")

    plt.suptitle(
        "CubeVision X - HSV Color Recognition",
        fontsize=15
    )

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    visualize_colors()
