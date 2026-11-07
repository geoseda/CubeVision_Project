
import os
import argparse
import csv
import cv2
import numpy as np
import matplotlib.pyplot as plt

from color_recognition import (
    classify_color,
    sample_face,
    annotate
)


def analyze_image(image_path, output_dir="results"):
    os.makedirs(output_dir, exist_ok=True)

    frame = cv2.imread(image_path)

    if frame is None:
        raise FileNotFoundError(
            f"Cannot open image: {image_path}"
        )

    detected, rectangles = sample_face(frame)

    annotated = annotate(frame, detected)

    hsv = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2HSV
    )

    filename = os.path.splitext(
        os.path.basename(image_path)
    )[0]

    annotated_path = os.path.join(
        output_dir,
        f"{filename}_annotated.png"
    )

    figure_path = os.path.join(
        output_dir,
        f"{filename}_analysis.png"
    )

    csv_path = os.path.join(
        output_dir,
        f"{filename}_colors.csv"
    )

    cv2.imwrite(
        annotated_path,
        annotated
    )

    with open(
        csv_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.writer(file)

        writer.writerow([
            "row",
            "column",
            "predicted_color",
            "hue",
            "saturation",
            "value"
        ])

        for index, (color, rect) in enumerate(
            zip(detected, rectangles)
        ):
            x1, y1, x2, y2 = rect

            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            h, s, v = hsv[cy, cx]

            writer.writerow([
                index // 3 + 1,
                index % 3 + 1,
                color,
                int(h),
                int(s),
                int(v)
            ])

    fig, axes = plt.subplots(
        2, 2,
        figsize=(12, 9)
    )

    axes[0, 0].imshow(
        cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )
    )

    axes[0, 0].set_title(
        "Original Rubik's Cube Image"
    )

    axes[0, 1].imshow(
        cv2.cvtColor(
            annotated,
            cv2.COLOR_BGR2RGB
        )
    )

    axes[0, 1].set_title(
        "Detected Stickers and Symbols"
    )

    axes[1, 0].imshow(
        hsv[:, :, 0],
        cmap="hsv",
        vmin=0,
        vmax=179
    )

    axes[1, 0].set_title(
        "HSV Hue Channel"
    )

    axes[1, 1].imshow(
        hsv[:, :, 1],
        cmap="gray",
        vmin=0,
        vmax=255
    )

    axes[1, 1].set_title(
        "HSV Saturation Channel"
    )

    for ax in axes.flat:
        ax.axis("off")

    plt.tight_layout()
    plt.savefig(
        figure_path,
        dpi=200,
        bbox_inches="tight"
    )
    plt.show()

    print("\nCUBEVISION X - FACE ANALYSIS")
    print("-----------------------------")

    grid = np.array(detected).reshape(3, 3)

    print("Detected colors:")
    print(grid)

    print("\nSaved outputs:")
    print(annotated_path)
    print(figure_path)
    print(csv_path)

    return detected


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--image",
        type=str,
        default=None
    )

    parser.add_argument(
        "--output",
        type=str,
        default="results"
    )

    args = parser.parse_args()

    image_path = args.image

    if not image_path:
        from tkinter import Tk, filedialog

        root = Tk()
        root.withdraw()

        image_path = filedialog.askopenfilename(
            title="Select Rubik's Cube Image",
            filetypes=[
                ("Images", "*.jpg *.jpeg *.png *.bmp")
            ]
        )

        root.destroy()

    if image_path:
        analyze_image(
            image_path,
            args.output
        )
    else:
        print("No image selected.")
