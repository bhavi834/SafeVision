"""
detect.py
---------
CLI entry point for Module 3 (Image Detection) and Module 4 (Video
Detection).

Usage:
    python detect.py --image path/to/photo.jpg
    python detect.py --video path/to/clip.mp4

Prints a per-person compliance report to the console in the spec's
format, and saves an annotated copy (image or video) next to the
output folder.
"""

import argparse
import json
import os

from detection.detector import PPEDetector
from detection.compliance import ComplianceEngine
import config


def parse_args():
    parser = argparse.ArgumentParser(description="Run PPE detection on an image or video")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--image", help="Path to an image file")
    group.add_argument("--video", help="Path to a video file")
    parser.add_argument("--output", default=None, help="Where to save the annotated result")
    parser.add_argument("--json", action="store_true", help="Also print results as JSON")
    return parser.parse_args()


def run_image(image_path: str, output_path: str | None, as_json: bool):
    detector = PPEDetector()
    engine = ComplianceEngine()

    image, detections = detector.predict_path(image_path)
    results = engine.evaluate(detections)

    status_map = {i: p.is_compliant for i, p in enumerate(results)}
    annotated = detector.draw_detections(image, detections, status_map)

    output_path = output_path or os.path.join(
        config.OUTPUT_FOLDER, f"annotated_{os.path.basename(image_path)}"
    )
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    import cv2
    cv2.imwrite(output_path, annotated)

    print(ComplianceEngine.format_report_text(results))
    print(f"\nAnnotated image saved to: {output_path}")

    if as_json:
        print(json.dumps([p.to_dict() for p in results], indent=2))


def run_video(video_path: str, output_path: str | None):
    detector = PPEDetector()

    output_path = output_path or os.path.join(
        config.OUTPUT_FOLDER, f"annotated_{os.path.basename(video_path)}"
    )
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    print(f"Processing video '{video_path}'... this can take a while for long clips.")
    stats = detector.process_video(video_path, output_path)

    total_sightings = stats["compliant_sightings"] + stats["non_compliant_sightings"]
    compliance_pct = (
        100.0 * stats["compliant_sightings"] / total_sightings if total_sightings else 0.0
    )

    print(f"\nProcessed {stats['frames']} frames.")
    print(f"Compliant person-sightings:     {stats['compliant_sightings']}")
    print(f"Non-compliant person-sightings: {stats['non_compliant_sightings']}")
    print(f"Overall compliance rate:        {compliance_pct:.1f}%")
    print(f"Annotated video saved to: {output_path}")


def main():
    args = parse_args()
    if args.image:
        run_image(args.image, args.output, args.json)
    else:
        run_video(args.video, args.output)


if __name__ == "__main__":
    main()
