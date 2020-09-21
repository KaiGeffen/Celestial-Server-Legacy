from os.path import join, isdir
import os.path
import pyglet


def do_fp_setup():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(script_dir)
    if isdir('images'):
        image_base_path = join(script_dir, 'images')
    else:
        raise SystemError(f"Filepath {script_dir} does not contain required folder 'images'.")
    pyglet.resource.path = [image_base_path]
    pyglet.resource.reindex()
