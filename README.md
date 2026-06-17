# SafeVision — AI-Powered PPE Compliance Monitoring

This is the **core pipeline** phase of the SafeVision project: a working
YOLOv8-based PPE detector, a compliance engine that turns raw detections
into per-person COMPLIANT / NON-COMPLIANT verdicts, and a Flask dashboard
to run it on uploaded images. Database, alerts, and the wider dashboard
are wired up but disabled by default — flip them on whenever you're ready.

## What's working right now

| Module (per original spec) | Status |
|---|---|
| 1. Dataset handling | ✅ drop your Roboflow export into `dataset/` |
| 2. Model training | ✅ `train.py` + `training/trainer.py` |
| 3. Image detection | ✅ `detect.py --image ...` and the Flask `/upload` route |
| 4. Video detection | ✅ `detect.py --video ...` |
| 5. Webcam detection | 🔲 next phase |
| 6. Compliance engine | ✅ `detection/compliance.py` |
| 7. Database (MongoDB) | ⚙️ wired up, disabled until you set `MONGO_URI` + enable in `.env` |
| 8. Dashboard | ✅ upload/result flow live; live/violations/reports/analytics pages are placeholders |
| 9. Alerts (email/Telegram) | ⚙️ wired up, disabled until you set credentials + enable in `.env` |
| 10. Analytics | 🔲 next phase |
| 11. Advanced features (face recognition, attendance, restricted zones, fall detection, QR badges) | 🔲 next phase |
| 12. Documentation | 🔲 `docs/` reserved, this README covers setup for now |

## Folder structure

```
SafeVision/
├── dataset/            # drop your Roboflow YOLOv8 export + data.yaml here
├── models/             # trained weights (best.pt) land here after training
├── training/           # Trainer class used by train.py
├── detection/           # PPEDetector (YOLOv8 wrapper) + ComplianceEngine
├── alerts/              # email + Telegram senders (disabled by default)
├── database/            # MongoDB helpers (disabled by default)
├── dashboard/            # reserved for the Module 8 expansion
├── templates/            # Flask/Jinja HTML
├── static/               # CSS + uploaded/annotated images
├── reports/               # reserved for Module 10 output
├── docs/                   # reserved for Module 12 output
├── app.py                  # Flask app
├── detect.py                # CLI: run detection on an image or video
├── train.py                  # CLI: train the YOLOv8 model
├── config.py                  # all settings, read from .env
└── requirements.txt
```

## Setup

```bash
cd SafeVision
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env              # then edit .env as needed
```

### 1. Add your dataset

Drop your Roboflow YOLOv8 export into `dataset/` — see
`dataset/README.md` for exact steps. Make sure the class list in
`dataset/data.yaml` matches `SAFEVISION_CLASSES` in `.env` (both
already default to `Person, Helmet, Safety Vest, Gloves, Face Mask,
Goggles, Safety Boots`).

### 2. Train the model

```bash
python train.py --data dataset/data.yaml --epochs 100 --imgsz 640 --batch 16
```

This fine-tunes a YOLOv8n base checkpoint, prints Precision / Recall /
mAP50 / mAP50-95 after training, and copies the best weights to
`models/best.pt` automatically. For free GPU training, run the same
calls from a Colab notebook against `training/trainer.py` (just `pip
install ultralytics`, mount/clone the project, and call
`Trainer(...).train(...)` from a cell — the logic is identical).

### 3. Run detection from the CLI

```bash
python detect.py --image samples/site_photo.jpg
python detect.py --video samples/site_clip.mp4
```

Prints a per-person report:

```
Person 1
Helmet: Yes
Safety Vest: No
Gloves: No
Face Mask: Yes
Goggles: No
Safety Boots: Yes

Status: Violation
```

and saves an annotated image/video to `static/outputs/`.

### 4. Run the dashboard

```bash
python app.py
```

Visit `http://localhost:5000`, upload an image, and you'll get the
annotated result with a compliance "inspection tag" per person.
Live Monitoring / Violation History / Reports / Analytics are
placeholder pages for now — they're in the nav so the dashboard's
final shape is already visible.

## Turning on the database & alerts

Both are fully implemented, just **off by default** so the core
pipeline needs zero external services to run:

```bash
# .env
SAFEVISION_DB_ENABLED=true
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net
MONGO_DB_NAME=safevision

SAFEVISION_EMAIL_ALERTS_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_USER=you@gmail.com
SMTP_PASSWORD=your-app-password
ALERT_EMAIL_TO=safety-officer@example.com

SAFEVISION_TELEGRAM_ALERTS_ENABLED=true
TELEGRAM_BOT_TOKEN=123456:ABC-your-bot-token
TELEGRAM_CHAT_ID=987654321
```

Once enabled, every non-compliant detection from `/upload` or
`/api/detect` automatically writes a violation record to MongoDB and
fires both alert channels — no code changes needed, `app.py` already
calls `_notify_violations()` on every violation.

## API

`POST /api/detect` accepts a multipart image under the field name
`image` and returns JSON:

```json
{
  "person_count": 2,
  "violation_count": 1,
  "results": [
    {
      "person_index": 1,
      "bbox": [120, 45, 310, 480],
      "ppe_status": {"Helmet": true, "Safety Vest": false, "...": "..."},
      "missing_required_ppe": ["Safety Vest"],
      "status": "NON-COMPLIANT"
    }
  ]
}
```

## What's next

The next phases (in rough order, but happy to reorder based on what's
most useful): webcam/CCTV live detection, the violation history +
analytics dashboard pages backed by MongoDB, then the advanced
features (face recognition, attendance, restricted zones, fall
detection, QR badges) — each is closer to its own sub-project than a
quick add-on, so we'll tackle them one at a time.
