# Implementation Status

This file distinguishes the current image/dashboard demonstration from the broader proposed smart-classroom design. Update it after each hardware integration and validation milestone.

## Demonstrated in the current project workflow

- Raspberry Pi 4 Model B used as the edge computer.
- Raspberry Pi Camera Module V2 (IMX219, 8 MP) used for image capture.
- Python image-processing workflow for face detection, anonymization and four-region occupancy estimation.
- InsightFace `buffalo_l` face detection with ONNX Runtime CPU execution in the described Approach B implementation.
- Image scaling, overlapping tiles and NMS to reduce duplicate face detections.
- Anonymized image and occupancy/region outputs.
- FastAPI backend serving dashboard data, images and occupancy report.
- React/Vite dashboard with overview and image-processing stages.
- Vercel frontend hosting and Cloudflare Tunnel for demo access to the Pi backend.

## Broader design / integration targets

The following components have been discussed as part of the full system, but this document does not claim they are fully integrated or validated:

- Teacher timetable-slot creation and scheduling.
- RFID-based student/slot validation and attendance.
- ESP32-S3 sensor/controller integration.
- PIR occupancy sensing and ultrasonic backup.
- LDR and temperature-based environment monitoring.
- Acoustic/noise monitoring.
- Relay-based automatic light/fan switching.
- Measured energy consumption and savings analytics.

Mark each item as complete only after the hardware is connected and the end-to-end behavior has been tested.

## Validation still required

Record measured results rather than estimated claims:

| Test | Evidence to record |
|---|---|
| Face detection | Labelled test images, true/false detections, precision and recall |
| Anonymization | Visual inspection of all detected faces, including missed detections |
| Region assignment | Ground-truth region labels and per-region confusion counts |
| Processing speed | Image dimensions, Pi model/RAM, Python version and average latency |
| Backend | API health, response time and error logs |
| Dashboard | Refresh behavior and successful image/report loading |
| Sensor integration | Sensor readings and test conditions |
| Relay control | Verified switching under safe isolated test conditions |
| Energy impact | Baseline and post-control power measurements over comparable periods |

## Known limitations

- Small, occluded or turned faces may be missed.
- Tile processing increases computation.
- Region estimation depends on camera placement and calibration.
- GrabCut may include background or adjacent people; geometric fallback is approximate.
- Anonymization is a visual privacy measure, not a guarantee of irreversible de-identification.
- A still-image pipeline is not equivalent to validated real-time video tracking.
- Occupancy counts alone do not establish student identity.
