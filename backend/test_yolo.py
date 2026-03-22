from ultralytics import YOLO

model = YOLO('yolov8x.pt')  # Make sure this model is in your directory
results = model('sample.png')  # Use your image

results[0].print()        # Show object summary in console
results[0].show()         # Display image with detections
results[0].save('output.png')  # Save output image
