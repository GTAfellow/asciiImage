from PIL import Image, ImageFont, ImageDraw, ImageEnhance
from img_process import constants, GifProcess
import sys
import os
import shutil
import numpy as np
from tqdm import tqdm
import logging


class ImageTransform(object):
    """
    图像处理类
    """
    ascii_char = list("@M%WXmBU&ZQ$dpOLwh8kYCn#bqaxJoIuf0}(])[{tz|/jvc\?l+*ri<1>!^~_\";-,`:'. ")

    def __init__(self, img_path: str, char_list=None):
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s: %(message)s')
        self.img_path = img_path
        try:
            self.im = Image.open(self.img_path)
        except IOError:
            logging.error('Can not load. Please check your input path.')
            sys.exit(1)
        if char_list is not None:
            self.ascii_char = self.sort_char_list_by_darkness(char_list)

    def __resize(self, width: int, height: int):
        """
        图像长宽再设置
        :param width: 图像宽度
        :param height: 图像高度
        :return: PIL.Image Object
        """
        # im = Image.open(self.img_path)
        self.im.thumbnail((width, height), Image.ANTIALIAS)
        return self.im

    def __get_char(self, r: int, g: int, b: int, alpha=256):
        """
        将256灰度映射到70个字符上
        :param r:
        :param g:
        :param b:
        :param alpha:
        :return: 70个字符中一个
        """
        if alpha == 0:
            return ' '
        length = len(self.ascii_char)
        gray = int(0.2126 * r + 0.7152 * g + 0.0722 * b)
        unit = (256.0 + 1) / length
        return self.ascii_char[int(gray / unit)]

    def img_to_ascii(self, width: int, height: int, delimiter='\n'):
        """
        图像转换为字符画
        :param width: 图像宽度
        :param height: 图像高度
        :param delimiter: 分隔符
        :return: ascii字符串
        """
        im = self.__resize(width, height)  # 修改图像大小
        im = ImageTransform.enhance_contrast(im, constants.ImgConstants.CONTRAST_VALUE)  # 增大图像对比度
        string = ''
        for i in range(im.size[1]):
            for j in range(im.size[0]):
                string += self.__get_char(*im.getpixel((j, i)))
            string += delimiter
        return string

    def get_cell_size(self, font):
        """
        获取单元格大小
        :param font: 字体
        :return: cell边长
        """
        image = Image.new('RGB', (100, 100), color='white')
        draw = ImageDraw.Draw(image)
        w_list = []
        h_list = []
        for char in self.ascii_char:
            w, h = draw.textsize(char, font=font)
            w_list.append(w)
            h_list.append(h)
        max_w = max(w_list)
        max_h = max(h_list)
        return max(max_w, max_h)

    def ascii_to_img(self, string: str, img_path: str, delimiter='\n'):
        """
        ascii字符串转换为图片
        :param string: ascii字符串
        :param img_path: 图片输出地址
        :param delimiter: 分隔符
        :return:
        """
        font = ImageFont.truetype(constants.ImgConstants.FONT, constants.ImgConstants.FONT_SIZE)
        cell_size = self.get_cell_size(font)

        line_list = string.split(delimiter)
        image_width = len(line_list[0]) * cell_size
        image_height = len(line_list) * cell_size

        image = Image.new('RGB', (image_width, image_height), color='white')
        draw = ImageDraw.Draw(image)

        line_number = 0
        for line in line_list:
            char_number = 0
            for char in line:
                w, h = draw.textsize(char, font=font)
                img_w = char_number * cell_size + int((cell_size - w) / 2)
                img_h = line_number * cell_size + int((cell_size - h) / 2)
                draw.text((img_w, img_h), char, font=font, fill=(0, 0, 0))
                char_number += 1
            line_number += 1

        image.save(img_path)

    def ascii_to_colorful_img(self, string: str, img_path: str, array, delimiter='\n'):
        """
        ascii字符串转换为彩色图片
        :param string: ascii字符串
        :param img_path: 图片输出地址
        :param array: numpy图片数组
        :param delimiter: 分隔符
        :return:
        """
        font = ImageFont.truetype(constants.ImgConstants.FONT, constants.ImgConstants.FONT_SIZE)
        cell_size = self.get_cell_size(font)

        line_list = string.split(delimiter)
        image_width = len(line_list[0]) * cell_size
        image_height = len(line_list) * cell_size

        image = Image.new('RGB', (image_width, image_height), color='white')
        draw = ImageDraw.Draw(image)

        line_number = 0
        for line in line_list:
            char_number = 0
            for char in line:
                w, h = draw.textsize(char, font=font)
                img_w = char_number * cell_size + int((cell_size - w) / 2)
                img_h = line_number * cell_size + int((cell_size - h) / 2)
                color = ImageTransform.__get_pixel_color(array, line_number, char_number)
                draw.text((img_w, img_h), char, font=font, fill=color)
                char_number += 1
            line_number += 1

        image.save(img_path)

    def img_to_ascii_img(self, size_ratio: float, img_path: str, color=False):
        """
        将图片直接转化为ascii图片
        :param size_ratio: 大小比例
        :param img_path: 输出图片路径
        :param color: 是否是彩色
        :return:
        """
        if size_ratio <= 0:
            raise Exception("Must be positive.")
        width = int(self.im.size[0] * size_ratio)
        height = int(self.im.size[1] * size_ratio)
        if not color:
            string = self.img_to_ascii(width, height, delimiter='\n')
            self.ascii_to_img(string, img_path, delimiter='\n')
        else:
            string = self.img_to_ascii(width, height, delimiter='\n')
            array = self.__get_color_matrix()
            self.ascii_to_colorful_img(string, img_path, array)

    def gif_frames_to_png(self, png_path: str):
        """
        将gif每一帧转化为png
        :param png_path: png存放路径
        :return:
        """
        i = 0
        my_palette = self.im.getpalette()
        try:
            while 1:
                self.im.putpalette(my_palette)
                new_im = Image.new("RGB", self.im.size)
                new_im.paste(self.im)
                path = os.path.join(png_path, str(i) + '.png')
                new_im.save(path)
                i += 1
                self.im.seek(self.im.tell() + 1)
        except EOFError:
            pass  # end of sequence

    def __png_list_to_ascii_image(self, png_path: str, output_path: str, size_ratio: float, color=False):
        """
        批量将png转换为ascii图片
        :param png_path:
        :param output_path:
        :param size_ratio:
        :param color: 是否是彩色
        :return:
        """
        file_list = os.listdir(png_path)
        if not os.path.exists(png_path):
            logging.error('PNG files folder does not exist.')
            sys.exit(1)
        if not os.path.exists(output_path):
            os.mkdir(output_path)
        for i in tqdm(range(len(file_list))):
            path = os.path.join(png_path, file_list[i])
            if os.path.splitext(path)[1] == '.png':
                self.img_path = path
                try:
                    self.im = Image.open(self.img_path)
                except IOError:
                    logging.error('Can not load. Please check your input path.')
                    sys.exit(1)

                self.img_to_ascii_img(size_ratio, os.path.join(output_path, file_list[i]), color)

    def gif_to_ascii_gif(self, size_ratio: float, img_path: str, tmp_png_path: str, color=False):
        """
        gif图转ascii gif
        :param size_ratio: 大小比例
        :param img_path: 输出gif地址
        :param tmp_png_path: 临时png地址
        :param color: 是否是彩色
        :return:
        """
        split_png_dir = os.path.join(tmp_png_path, 'frames')
        processed_png_dir = os.path.join(tmp_png_path, 'processed')
        if not os.path.exists(split_png_dir):
            os.mkdir(split_png_dir)
        if not os.path.exists(processed_png_dir):
            os.mkdir(processed_png_dir)
        logging.info('Starting to split.')
        self.gif_frames_to_png(split_png_dir)
        logging.info('Splitting done.')
        logging.info('Starting to process.')
        self.__png_list_to_ascii_image(split_png_dir, processed_png_dir, size_ratio, color)
        logging.info('Processing done.')
        logging.info('Starting to generate the gif.')
        GifProcess.GifProcess.merge_png_to_gif(processed_png_dir, img_path)
        logging.info('Gif generation done.')
        ImageTransform.__clean_tmp_dir(tmp_png_path)
        logging.info('Cleaned the tmp directory.')

    @staticmethod
    def __clean_tmp_dir(tmp_png_path: str):
        """
        清空临时文件夹
        :param tmp_png_path:
        :return:
        """
        split_png_dir = os.path.join(tmp_png_path, 'frames')
        processed_png_dir = os.path.join(tmp_png_path, 'processed')
        if os.path.exists(split_png_dir):
            shutil.rmtree(split_png_dir)
        if os.path.exists(processed_png_dir):
            shutil.rmtree(processed_png_dir)

    @staticmethod
    def enhance_contrast(im, contrast_value: float):
        """
        修改对比度
        :param im: Image
        :param contrast_value: 对比度值
        :return:
        """
        enh_con = ImageEnhance.Contrast(im)
        image_contrasted = enh_con.enhance(contrast_value)
        return image_contrasted

    def __get_color_matrix(self):
        """
        Image转换为numpy数组
        :return: numpy数组
        """
        # im = self.__resize(width, height)
        array = np.array(self.im)
        return array

    @staticmethod
    def __get_pixel_color(array, i, j):
        """
        获取像素点RGB颜色
        :param array: numpy数组
        :param i: 横轴值
        :param j: 纵轴值
        :return:
        """
        if len(array) - 1 < i:
            i = len(array) - 1
        if len(array[0]) - 1 < j:
            j = len(array[0]) - 1
        return (array[i][j][0], array[i][j][1], array[i][j][2])

    @staticmethod
    def __get_char_darkness(char):
        """
        获取单个字符的暗度
        :param char: 字符
        :return: 暗度
        """
        image = Image.new('1', (50, 50), color=1)
        font = ImageFont.truetype(constants.ImgConstants.FONT, constants.ImgConstants.FONT_SIZE)
        draw = ImageDraw.Draw(image)
        darkness = 0
        w, h = draw.textsize(char, font=font)
        draw.text((0, 0), char, font=font, fill=0)
        for i in range(w):
            for j in range(h):
                if image.getpixel((i, j)) == 0:
                    darkness += 1
        return darkness

    @staticmethod
    def sort_char_list_by_darkness(string):
        """
        对字符进行暗度倒序排序
        :param string 字符串
        :return:
        """
        input_list = list(set(list(string)))
        tmp_list = []
        for char in input_list:
            darkness = ImageTransform.__get_char_darkness(char)
            tmp_list.append((char, darkness))
        tmp_list = sorted(tmp_list, key=lambda x: x[1])
        result_list = []
        for i in tmp_list:
            result_list.append(i[0])
        result_list.reverse()
        return result_list
