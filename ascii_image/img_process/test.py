from img_process import ImageTransform
import os
import sys

if __name__ == '__main__':
    input_str = " !\"#$%&'()*+'-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
    # input_str3 = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. "
    # img_path = 'naruto.jpg'
    # output_img = 'naruto_bw3.jpg'
    # it = ImageTransform.ImageTransform(img_path,char_list=input_str3)
    # it.img_to_ascii_img(1 / 8, output_img)

    gif_path = 'weisuoyuwei.gif'
    parent_dir = os.path.dirname(sys.path[0])
    png_path = os.path.join(parent_dir, 'tmp')
    if not os.path.exists(png_path):
        os.mkdir(png_path)
    it_gif = ImageTransform.ImageTransform(gif_path)
    it_gif.gif_to_ascii_gif(1/4, 'weisuoyuwei_ascii4.gif', png_path)

    # input = " !\"#$%&'()*+'-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
    # input2 = "A"
    # gif_path = 'weisuoyuwei.gif'
    # it_gif = ImageTransform.ImageTransform(gif_path)
    # string = it_gif.sort_char_list_by_darkness(input)
    # print(string)
