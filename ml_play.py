"""
The template of the main script of the machine learning process
"""

import games.arkanoid.communication as comm
from games.arkanoid.communication import ( \
    SceneInfo, GameStatus, PlatformAction
)

def ml_loop():
    """
    The main loop of the machine learning process

    This loop is run in a separate process, and communicates with the game process.

    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.
    ball_served = False
    ball_speed = (0,0)
    ball_pos = (0,0)
    ml_loop.ball_prev=ball_pos
    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()

    
    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()
        ball_pos = list(scene_info.ball)
        if ball_pos[1]-ml_loop.ball_prev[1]!=0:
            ball_speed = [ball_pos[0]-ml_loop.ball_prev[0],ball_pos[1]-ml_loop.ball_prev[1]]
        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
            scene_info.status == GameStatus.GAME_PASS:
            # Do some stuff if needed
            ball_served = False

            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue

        # 3.3. Put the code here to handle the scene information

        # 3.4. Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_LEFT)
            ball_served = True
        else:  
            if ball_speed[1] > 0:    
                ball_pos_predict=ball_pos

                while ball_pos_predict[1] < 393 and ball_pos_predict[1] >= 0:
                    ball_pos_predict = [ball_pos_predict[0]+ball_speed[0],ball_pos_predict[1]+ball_speed[1]]
                    
                    if ball_pos_predict[0] <= 0 :
                        ball_pos_predict[0]=0
                        ball_speed[0] = abs(ball_speed[0])
                    if ball_pos_predict[0] >= 195 :
                        ball_pos_predict[0]=195
                        ball_speed[0] = -abs(ball_speed[0])
                print(ball_speed)
                print(ball_pos_predict)
                if scene_info.platform[0]+20>ball_pos_predict[0]:
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
                elif scene_info.platform[0]+20<ball_pos_predict[0]:
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
                else:
                    comm.send_instruction(scene_info.frame, PlatformAction.NONE)
            else:
                comm.send_instruction(scene_info.frame, PlatformAction.NONE)
        ml_loop.ball_prev=ball_pos
ml_loop.ball_prev=[0,0]
