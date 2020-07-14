Drone track green ball
Using the python programming I made the drone to track the green ball

If the ball move right the drone go right with the voice telling 'right'

If the ball move left the drone go left with the voice telling 'left'

If the ball move up the drone go up with the voice telling 'up'

If the ball move doen the drone go down with the voice telling 'down'

If the ball move near the drone go backward with the voice telling 'back'

If the ball move far the drone go forward with the voice telling '前進'

ドローンが緑色のボールを追跡します

ボールの左右、上下、前後の動きに追随します。

左右、上下、前後に動くと「right」,「left」,「up」,「down」, 「back」,「前進」と音声で知らせます。


How it works.
1. Divide tello camera screen into 9 segments.
2. Calculate the offset x, y from the camera screen center
3. if x offset > 100 move right
4. if x offset <-100 move left
5. if y offset > 100 move up
6. if y offset <-100 move down
7. if ball radius > 60 move back
8. if ball radius < 20 move forward
x, y offset and radius and lines are displayed as the program aid.
