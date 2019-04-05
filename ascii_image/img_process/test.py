from img_process import ImageTransform
import os
import sys

if __name__ == '__main__':
    input_str = " !\"#$%&'()*+'-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
    parent_dir = os.path.dirname(sys.path[0])
    example_dir = os.path.join(os.path.dirname(parent_dir), 'example')

    """
    JPG transformation
    """
    # img_path = os.path.join(example_dir, 'spring.jpg')
    # output_img_path = os.path.join(example_dir, 'spring_ascii.jpg')
    # it = ImageTransform.ImageTransform(img_path, char_list=input_str)
    # it.img_to_ascii_img(1 / 8, output_img_path)

    """
    GIF transformation
    """
    gif_path = os.path.join(example_dir, 'cat.gif')
    png_path = os.path.join(parent_dir, 'tmp')
    if not os.path.exists(png_path):
        os.mkdir(png_path)
    out_gif_path = os.path.join(example_dir, 'cat_ascii_color.gif')
    it_gif = ImageTransform.ImageTransform(gif_path)
    it_gif.gif_to_ascii_gif(1/4, out_gif_path, png_path, color=True)
