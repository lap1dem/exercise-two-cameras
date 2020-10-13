# exercise-two-cameras

Small room with a human actor inside. On one of the walls we have two cameras placed in parallel to each other:
- Distance between the cameras: 1 meter (100.0)
- Angle of view (AOV) for both cameras: 78° (degrees)
- Frame width: 2048 px; Frame height: 1080 px. 


Goals:
1) Calculate distance to the human actor using coordinates (x;y position of the human face in the frame) from two cameras placed in parallel. 
2) Provide single space x;y;z coordinates for the object. 

Delivery:
Python script which accepts X;Y coordinates for two cameras and returns the x;y;z single space coordinates (e.g. assuming the mid camera position). X - horizontal coordinate; Y - Vertical coordinate; Z - Depth / Distance to the object. 
