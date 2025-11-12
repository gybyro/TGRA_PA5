from openal import oalInit, oalOpen, Listener

oalInit()

sounds = {
    # "step": oalOpen("assets/sfx/step.wav"),
    # "shoot": oalOpen("assets/sfx/shoot.wav")
    "bg_music": oalOpen("res/sound/Shrek_Remix.wav")
}

def update_listener(camera):
    Listener.set_position(tuple(camera.position))
    Listener.set_orientation(at=tuple(camera.forwards), up=tuple(camera.up))

# music.set_relative(True)  # sound moves *with* the listener
# music.set_position((0, 0, 0))  # same place as listener

music = oalOpen("res/sound/Shrek_Remix.wav")
# music.set_relative(True)
music.set_looping(True)
music.play()