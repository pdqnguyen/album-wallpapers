import glob
import random
import os
from argparse import ArgumentParser
import numpy as np
from PIL import Image

NUM_ITER = 1
WALLPAPER_SIZE = (1920, 1080)    # Screen dimensions
ALBUM_SIZE = (300, 300)    # resize all to this
EXTENSIONS = ['.png', '.jpg']


def create_wallpaper(filename, albums, wallpaper_size=WALLPAPER_SIZE, album_size=ALBUM_SIZE):
    wallpaper_w, wallpaper_h = wallpaper_size
    album_w, album_h = album_size
    max_w, max_h = 0, 0    # Wallpaper dimensions
    albums_per_row = 0
    albums_per_col = 0
    while max_w < wallpaper_w:
        max_w += album_w
        albums_per_row += 1
    while max_h < wallpaper_h:
        max_h += album_h
        albums_per_col += 1
    image = Image.new('RGB', (max_w, max_h))  # blank wallpaper to fill
    # Add images
    x_offset = 0
    y_offset = 0
    i = 0
    a = None
    while y_offset < wallpaper_h:
        while x_offset < wallpaper_w:
            if i >= len(albums):
                break
            a = albums[i]
            a = a.resize((album_w, album_h), Image.BILINEAR)
            image.paste(a, (x_offset, y_offset))
            x_offset += a.size[0]
            i += 1
        if a is not None:
            x_offset = 0
            y_offset += a.size[1]
    # Save wallpaper
    image.save(filename)
    return


def main(source, output, num_iter=NUM_ITER, wallpaper_size=WALLPAPER_SIZE, album_size=ALBUM_SIZE):
    print('wallpaper size: {} x {}'.format(wallpaper_size[0], wallpaper_size[1]))
    print('album size: {} x {}'.format(album_size[0], album_size[0]))
    album_paths = glob.glob(os.path.join(source, '*'))
    albums = [Image.open(path) for path in album_paths if os.path.splitext(path)[1] in EXTENSIONS]
    num_albums = len(albums)
    albums_per_wallpaper = int(np.ceil(wallpaper_size[0] / album_size[0]) * np.ceil(wallpaper_size[1] / album_size[1]))
    num_wallpapers = int(np.ceil(float(num_albums) / albums_per_wallpaper))
    print(f"generating {num_wallpapers} wallpapers per batch ({albums_per_wallpaper} albums per wallpaper)")
    for i in range(num_iter):
        print("batch {} of {}".format(i + 1, num_iter))
        random.shuffle(albums)
        albums_oversampled = [a for a in albums]
        if num_albums < (num_wallpapers * albums_per_wallpaper):
            oversampling = random.sample(albums, albums_per_wallpaper - (num_albums % albums_per_wallpaper))
            albums_oversampled += oversampling
        for k in range(num_wallpapers):
            wallpaper_albums = albums_oversampled[k * albums_per_wallpaper: (k + 1) * albums_per_wallpaper]
            filename = str((i * num_wallpapers) + k).zfill(len(str(num_wallpapers))) + '.png'
            filename = os.path.join(output, filename)
            create_wallpaper(filename, wallpaper_albums, wallpaper_size=wallpaper_size, album_size=album_size)
            print(filename)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("source", help="source directory")
    parser.add_argument("output", help="output directory")
    parser.add_argument(
        "-i",
        "--num_iter",
        type=int,
        default=NUM_ITER,
        help="Number of iterations to produce wallpapers."
    )
    parser.add_argument(
        "-w",
        "--wallpaper",
        nargs=2,
        type=int,
        default=WALLPAPER_SIZE,
        help="Screen resolution (width and height in pixels)."
    )
    parser.add_argument(
        "-a",
        "--album",
        nargs=2,
        type=int,
        default=ALBUM_SIZE,
        help="Image tile size (width and height in pixels)."
    )
    args = parser.parse_args()
    if not os.path.exists(args.source):
        raise OSError(f"source directory {args.source} not found")
    if not os.path.exists(args.output):
        os.makedirs(args.output)
    main(args.source, args.output, num_iter=args.num_iter, wallpaper_size=args.wallpaper, album_size=args.album)
