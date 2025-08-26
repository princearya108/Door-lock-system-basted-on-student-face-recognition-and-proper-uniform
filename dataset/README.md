# Dataset Directory

This directory contains training data for the door lock system.

## Structure

```
dataset/
├── faces/               # Student face images for training
│   ├── ST2024001.jpg   # Student ID as filename
│   ├── ST2024002.jpg
│   └── ...
└── uniforms/           # Uniform images for training
    ├── compliant/      # Images of proper uniforms
    │   ├── shirt_white_01.jpg
    │   ├── trouser_black_01.jpg
    │   └── ...
    └── non_compliant/  # Images of improper uniforms
        ├── shirt_red_01.jpg
        ├── no_tie_01.jpg
        └── ...
```

## Face Images Guidelines

1. **Image Quality**: High resolution (minimum 640x480)
2. **Lighting**: Good, even lighting on the face
3. **Angle**: Front-facing, minimal head tilt
4. **Expression**: Neutral expression preferred
5. **Background**: Clean, uncluttered background
6. **Format**: JPG, PNG supported
7. **Naming**: Use student ID as filename (e.g., ST2024001.jpg)

## Uniform Images Guidelines

1. **Categories**: Organize by compliant/non-compliant
2. **Items**: Include all uniform items (shirt, trousers, shoes, tie, etc.)
3. **Colors**: Capture different allowed/disallowed colors
4. **Angles**: Multiple angles and poses
5. **Lighting**: Various lighting conditions
6. **Background**: Different backgrounds for robustness

## Training Process

1. Place face images in `faces/` directory
2. Run face encoding batch process:
   ```python
   from cloud_functions.api.face_recognition_service import FaceRecognitionService
   
   service = FaceRecognitionService()
   result = service.batch_process_images('dataset/faces')
   print(result)
   ```

3. For uniform detection, use YOLO training process with labeled data

## Data Privacy

- Ensure proper consent for all face images
- Follow local privacy laws and school policies
- Secure storage and access controls
- Regular data audits and cleanup
