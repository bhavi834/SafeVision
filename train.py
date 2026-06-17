"""
train.py
--------
CLI entry point for Module 2 (Model Training).

Usage:
    python train.py --data dataset/data.yaml --epochs 100 --imgsz 640 --batch 16

After training finishes, the best checkpoint is automatically copied
to models/best.pt so the Flask app and detect.py can use it right away.

For GPU training on Colab, see docs/colab_training.ipynb (generated
alongside this script) — it calls into the same training/trainer.py
module so behaviour is identical locally and in the cloud.
"""

import argparse

from training.trainer import Trainer


def parse_args():
    parser = argparse.ArgumentParser(description="Train the SafeVision PPE YOLOv8 model")
    parser.add_argument("--data", default="dataset/data.yaml", help="Path to data.yaml")
    parser.add_argument("--model", default="yolov8n.pt", help="Base checkpoint to fine-tune from")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--patience", type=int, default=20, help="Early-stopping patience")
    parser.add_argument("--device", default=None, help="e.g. 0 for GPU 0, or 'cpu'")
    parser.add_argument("--run-name", default="safevision_ppe")
    parser.add_argument(
        "--skip-validate", action="store_true", help="Skip running validation after training"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    trainer = Trainer(data_yaml=args.data, base_model=args.model, run_name=args.run_name)

    print(f"Starting training: {args.epochs} epochs, imgsz={args.imgsz}, batch={args.batch}")
    trainer.train(
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        patience=args.patience,
        device=args.device,
    )

    if not args.skip_validate:
        trainer.validate()

    trainer.export_best_to_models_dir()
    print("\nDone. Run `python detect.py --image path/to/photo.jpg` to try it out, "
          "or `python app.py` to use the dashboard.")


if __name__ == "__main__":
    main()
