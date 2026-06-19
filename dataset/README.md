# Dataset folder

Drop your Roboflow PPE dataset export here in standard YOLOv8 format:

```
dataset/
├── data.yaml
├── train/
│   ├── images/
│   └── labels/
├── valid/
│   ├── images/
│   └── labels/
└── test/              (optional)
    ├── images/
    └── labels/
```

## How to get it from Roboflow

1. Open your dataset's "Generate" / "Versions" tab in Roboflow.
2. Choose export format **YOLOv8**.
3. Either:
   - Click **download zip**, then unzip its contents directly into this `dataset/` folder, or
   - Use the **"show download code"** snippet (needs the `roboflow` pip package and your API key), e.g.:

     ```python
     from roboflow import Roboflow
     rf = Roboflow(api_key="YOUR_API_KEY")
     project = rf.workspace("your-workspace").project("your-ppe-project")
     dataset = project.version(1).download("yolov8", location="dataset")
     ```

## Important: class order must match `data.yaml`

`data.yaml` in this folder defines the class list SafeVision expects
(`Person, Helmet, Safety Vest, Gloves, Face Mask, Goggles, Safety Boots`).
If your Roboflow project uses different class names or a different
order, either:

- Re-map/rename classes in Roboflow before exporting so they match, **or**
- Edit `data.yaml`'s `names:` list to match your export exactly, and
  update `SAFEVISION_CLASSES` in `.env` to the same list/order.

`config.py` and `detection/compliance.py` both read the class list
from one place, so once `data.yaml` and `.env` agree, everything else
(detector, compliance engine, dashboard) just works.
