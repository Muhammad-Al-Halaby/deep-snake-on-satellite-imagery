import os
from glob import glob
from posixpath import split


def main(data_dir, split, extension):
    images_path = glob(os.path.join(data_dir, f'*.{extension}'))    
    
    for image_path in images_path:
        os.rename(image_path, image_path.replace(f'.{extension}', f'_{split}.{extension}'))
    images_path = glob(os.path.join(data_dir, f'*.{extension}'))


    images_path = [image_path.split('/')[-1].split('.')[0] for image_path in images_path]
    # print(images_path)
    txt_path = os.path.realpath(os.path.join(data_dir, '..', '..', f'{split}.txt'))


    if 'images' in data_dir:
        with open(txt_path, 'w') as f:
            for image_path in images_path:
                f.write(image_path + '\n')


if __name__ == '__main__':
    splits = ['train', 'test']
    folders =  ['images', 'labels', 'labels_1D']
    extensions = ['jpg', 'png']
    for split in splits:
        for folder in folders:
            data_dir = f'./data/osd/{split}/{folder}'
            if folder == 'images':
                extension = extensions[0]    
            else:
                extension = extensions[1]    
            main(data_dir, split, extension)