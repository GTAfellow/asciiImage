from PIL import Image
import os


class GifProcess(object):

    @staticmethod
    def gif_frames_to_png(gif_path: str, png_path: str):
        """
        将gif每一帧转化为png
        :param gif_path: gif路径
        :param png_path: png存放路径
        :return:
        """
        i = 0
        im = Image.open(gif_path)
        my_palette = im.getpalette()
        try:
            while 1:
                im.putpalette(my_palette)
                new_im = Image.new("RGB", im.size)
                new_im.paste(im)
                path = os.path.join(png_path, 'foo' + str(i) + '.png')
                new_im.save(path)
                i += 1
                im.seek(im.tell() + 1)
        except EOFError:
            pass  # end of sequence

    @staticmethod
    def merge_png_to_gif(png_path, gif_path):
        """
        合并png到gif
        :param png_path: png路径
        :param gif_path: 输出gif路径
        :return:
        """
        file_list = os.listdir(png_path)
        GifProcess.sort_file_list(file_list)
        png_list = []
        im = Image.open(os.path.join(png_path, file_list[0]))
        for i in range(1, len(file_list)):
            path = os.path.join(png_path, file_list[i])
            if os.path.splitext(path)[1] == '.png':
                png_list.append(Image.open(path))
        im.save(gif_path, save_all=True, append_images=png_list, loop=0, duration=1)

    @staticmethod
    def sort_file_list(file_list: list):
        """
        排序名称为数字的文件列表
        :param file_list: 名称为数字的文件列表
        :return:
        """
        file_list.sort(key=lambda x: int(x[:-4]))
        return file_list
