import trivial.graphics as gl
from OpenGL import GL
from quickwindow import quick_window

with quick_window(800, 600, "test") as wnd:
    for dt in wnd.loop():
        for event in wnd.events():
            pass
        GL.glClearColor(2, 0.2, 0.2, 1)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glViewport(0, 0, 800*2, 600*2)
        with gl.matrix_mode(gl.MatrixMode.PROJECTION):
            gl.load_ortho(-1, 1, -1, 1, -1, 1)
        with gl.matrix_mode(gl.MatrixMode.MODELVIEW):
            gl.load_identity()
        with gl.draw_mode(gl.DrawMode.TRIANGLES):
            gl.color4(1., 0., 0., 1.)
            gl.vertex2(-.5, -.5)
            gl.color4(0., 1., 0., 1.)
            gl.vertex2(.5, -.5)
            gl.color4(0., 0., 1., 1.)
            gl.vertex2(0., .5)
        gl.flush()
