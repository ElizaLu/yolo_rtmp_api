from __future__ import annotations

import argparse
from pathlib import Path

from ultralytics import YOLO


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train a YOLOv8 detection model with stronger augmentation and localization-focused settings."
    )
    parser.add_argument("--data", type=str, default="data.yaml", help="Path to dataset YAML.")
    parser.add_argument("--model", type=str, default="yolov8x.pt", help="Pretrained YOLO weights or model YAML.")
    parser.add_argument("--epochs", type=int, default=100, help="Number of training epochs.")
    parser.add_argument("--imgsz", type=int, default=1280, help="Training image size.")
    parser.add_argument("--batch", type=int, default=4, help="Batch size.")
    parser.add_argument("--device", type=str, default="0", help="CUDA device id, e.g. 0, 0,1, cpu, mps.")
    parser.add_argument("--project", type=str, default="runs/train", help="Training output directory.")
    parser.add_argument("--name", type=str, default="yolov8x_aug_loc", help="Run name.")
    parser.add_argument("--workers", type=int, default=8, help="Dataloader workers.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    parser.add_argument("--patience", type=int, default=50, help="Early stopping patience.")
    parser.add_argument("--resume", action="store_true", help="Resume from last checkpoint if available.")

    # Augmentation knobs
    parser.add_argument("--hsv-h", type=float, default=0.03, help="Hue augmentation strength.")
    parser.add_argument("--hsv-s", type=float, default=0.7, help="Saturation augmentation strength.")
    parser.add_argument("--hsv-v", type=float, default=0.5, help="Value/brightness augmentation strength.")
    parser.add_argument("--degrees", type=float, default=10.0, help="Random rotation degrees.")
    parser.add_argument("--translate", type=float, default=0.10, help="Random translation fraction.")
    parser.add_argument("--scale", type=float, default=0.50, help="Random scale gain.")
    parser.add_argument("--shear", type=float, default=0.0, help="Random shear degrees.")
    parser.add_argument("--perspective", type=float, default=0.0, help="Random perspective factor.")
    parser.add_argument("--fliplr", type=float, default=0.5, help="Left-right flip probability.")
    parser.add_argument("--flipud", type=float, default=0.0, help="Up-down flip probability.")
    parser.add_argument("--mosaic", type=float, default=1.0, help="Mosaic probability.")
    parser.add_argument("--mixup", type=float, default=0.10, help="MixUp probability.")
    parser.add_argument("--cutmix", type=float, default=0.05, help="CutMix probability.")
    parser.add_argument(
        "--close-mosaic",
        type=int,
        default=15,
        help="Disable mosaic in the last N epochs to stabilize box regression.",
    )
    parser.add_argument(
        "--multi-scale",
        type=float,
        default=0.25,
        help="Randomly vary image size by +/- this fraction each batch.",
    )

    # Loss weighting knobs for box localization
    parser.add_argument("--box", type=float, default=8.0, help="Box loss weight.")
    parser.add_argument("--cls", type=float, default=0.5, help="Class loss weight.")
    parser.add_argument("--dfl", type=float, default=2.0, help="DFL loss weight.")

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset YAML not found: {data_path}")

    model = YOLO(args.model)

    train_kwargs = dict(
        data=str(data_path),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        project=args.project,
        name=args.name,
        workers=args.workers,
        seed=args.seed,
        patience=args.patience,
        resume=args.resume,
        amp=True,
        cos_lr=True,
        plots=True,

        # Augmentations: color + geometry + multi-scale
        hsv_h=args.hsv_h,
        hsv_s=args.hsv_s,
        hsv_v=args.hsv_v,
        degrees=args.degrees,
        translate=args.translate,
        scale=args.scale,
        shear=args.shear,
        perspective=args.perspective,
        fliplr=args.fliplr,
        flipud=args.flipud,
        mosaic=args.mosaic,
        mixup=args.mixup,
        cutmix=args.cutmix,
        close_mosaic=args.close_mosaic,
        multi_scale=args.multi_scale,

        # Localisation emphasis
        box=args.box,
        cls=args.cls,
        dfl=args.dfl,
    )

    print("Training with settings:")
    for k in [
        "data", "model", "epochs", "imgsz", "batch", "device", "project", "name",
        "hsv_h", "hsv_s", "hsv_v", "translate", "scale", "mosaic", "mixup", "cutmix",
        "close_mosaic", "multi_scale", "box", "cls", "dfl",
    ]:
        if k == "model":
            print(f"  {k}: {args.model}")
        else:
            print(f"  {k}: {train_kwargs.get(k, getattr(args, k.replace('-', '_'), None))}")

    _ = model.train(**train_kwargs)

    # Validate the best checkpoint if Ultralytics saved one.
    best_weights = Path(args.project) / args.name / "weights" / "best.pt"
    if best_weights.exists():
        best_model = YOLO(str(best_weights))
        val_metrics = best_model.val(data=str(data_path), imgsz=args.imgsz, batch=args.batch)
        print("Validation metrics:", val_metrics)
    else:
        print("No best.pt found; skipping post-training validation reload.")

    # Save location is handled by Ultralytics; print a friendly hint.
    print("Done. Check the run directory under:", Path(args.project) / args.name)


if __name__ == "__main__":
    main()
